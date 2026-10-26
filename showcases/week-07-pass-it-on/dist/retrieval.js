const ROOT = new URL('./', import.meta.url);
async function resource(name, binary = false) {
  const response = await fetch(new URL(name, ROOT));
  if (!response.ok) throw new Error(`Could not load ${name} (${response.status}).`);
  return binary ? response.arrayBuffer() : response.json();
}

export function queryVector(text, lexical) {
  const index = lexical.index || new Map(lexical.vocab.map((word, i) => [word, i]));
  const stop = lexical.stopSet || new Set(lexical.stop);
  const frequencies = new Map();
  for (const word of text.toLowerCase().match(/\b[a-z0-9_]{2,}\b/g) || []) {
    if (!stop.has(word) && index.has(word)) {
      const i = index.get(word);
      frequencies.set(i, (frequencies.get(i) || 0) + 1);
    }
  }
  let norm = 0;
  for (const [i, count] of frequencies) {
    const value = (1 + Math.log(count)) * lexical.idf[i];
    frequencies.set(i, value); norm += value * value;
  }
  norm = Math.sqrt(norm);
  if (norm) for (const [i, value] of frequencies) frequencies.set(i, value / norm);
  return frequencies;
}

export function sparseScores(query, rows) {
  return rows.map(([indices, weights]) => {
    let score = 0;
    for (let j = 0; j < indices.length; j++) score += (query.get(indices[j]) || 0) * weights[j];
    return score;
  });
}

export function denseScores(query, vectors, owners, documentCount) {
  const dimension = query.length;
  const count = vectors.length / dimension;
  const scores = new Float32Array(documentCount).fill(-Infinity);
  const winners = new Int32Array(documentCount).fill(-1);
  for (let i = 0; i < count; i++) {
    let dot = 0, norm = 0;
    const offset = i * dimension;
    for (let j = 0; j < dimension; j++) {
      const value = vectors[offset + j];
      dot += query[j] * value; norm += value * value;
    }
    const score = norm ? dot / Math.sqrt(norm) : 0;
    const doc = owners ? owners[i].doc : i;
    if (score > scores[doc]) { scores[doc] = score; winners[doc] = i; }
  }
  return { scores: Array.from(scores), winners };
}

export function ranked(scores) {
  return scores.map((score, doc) => ({ doc, score })).sort((a, b) => b.score - a.score || a.doc - b.doc);
}

export class Retrieval {
  constructor(corpus) {
    this.corpus = corpus;
    this.vectors = new Map();
    this.queries = new Map();
    this.results = new Map();
  }
  async lexical() {
    if (!this.lexicalPromise) this.lexicalPromise = resource('data/lexical.json').then(data => {
      data.index = new Map(data.vocab.map((word, i) => [word, i]));
      data.stopSet = new Set(data.stop);
      return data;
    }).catch(error => { this.lexicalPromise = null; throw error; });
    return this.lexicalPromise;
  }
  async model() {
    if (!this.modelPromise) this.modelPromise = (async () => {
      const { pipeline, env } = await import('./vendor/transformers.min.js');
      env.allowRemoteModels = false;
      env.allowLocalModels = true;
      env.localModelPath = new URL('models/', ROOT).href;
      env.backends.onnx.wasm.wasmPaths = new URL('vendor/', ROOT).href;
      env.backends.onnx.wasm.numThreads = 1;
      env.backends.onnx.wasm.proxy = false;
      return pipeline('feature-extraction', 'all-MiniLM-L6-v2', { quantized: true, local_files_only: true });
    })().catch(error => { this.modelPromise = null; throw error; });
    return this.modelPromise;
  }
  warmup() { this.model().catch(() => {}); this.lexical().catch(() => {}); }
  async vector(text) {
    if (!this.queries.has(text)) {
      const pending = this.model().then(model => model(text, { pooling: 'mean', normalize: true })).then(tensor => tensor.data);
      this.queries.set(text, pending);
      pending.catch(() => this.queries.delete(text));
    }
    return this.queries.get(text);
  }
  async tokens(text) {
    const model = await this.model();
    const full = await model.tokenizer(text, { truncation: false, padding: false });
    const input = await model.tokenizer(text, { truncation: true, padding: false, max_length: 256 });
    const ids = Array.from(input.input_ids.data, Number);
    return { total: full.input_ids.data.length, used: ids.length,
      pieces: ids.map(id => model.tokenizer.decode([id], { skip_special_tokens: false })) };
  }
  async data(unit) {
    if (!this.vectors.has(unit)) {
      const pending = Promise.all([
        resource(`data/vectors-${unit}.bin`, true).then(buffer => new Int8Array(buffer)),
        unit === 'page' ? null : resource(`data/passages-${unit}.json`),
      ]).then(([vectors, passages]) => ({ vectors, passages }));
      this.vectors.set(unit, pending);
      pending.catch(() => this.vectors.delete(unit));
    }
    return this.vectors.get(unit);
  }
  async search(text, unit = '60') {
    const key = `${unit}\u0000${text}`;
    if (!this.results.has(key)) {
      const pending = (async () => {
        const lex = await this.lexical();
        const sparse = queryVector(text, lex);
        const keyword = ranked(sparseScores(sparse, lex.rows));
        try {
          const [query, data] = await Promise.all([this.vector(text), this.data(unit)]);
          const dense = denseScores(query, data.vectors, data.passages, this.corpus.documents.length);
          return { keyword, semantic: ranked(dense.scores), winners: dense.winners, passages: data.passages, sparse, lex };
        } catch (error) {
          this.results.delete(key);
          return { keyword, semantic: null, error: error.message, sparse, lex };
        }
      })();
      this.results.set(key, pending);
      pending.catch(() => this.results.delete(key));
    }
    return this.results.get(key);
  }
  contributions(doc, result) {
    const [indices, weights] = result.lex.rows[doc];
    return indices.map((i, j) => ({ word: result.lex.vocab[i], value: (result.sparse.get(i) || 0) * weights[j] }))
      .filter(term => term.value > 0).sort((a, b) => b.value - a.value);
  }
  excerpt(doc, result) {
    const terms = this.contributions(doc, result);
    const words = this.corpus.documents[doc].text.split(/\s+/);
    let best = 0, bestScore = -1;
    const weights = new Map(terms.map(term => [term.word, term.value]));
    for (let i = 0; i < words.length; i += 40) {
      let score = 0;
      for (const word of words.slice(i, i + 90)) {
        for (const token of word.toLowerCase().match(/\b[a-z0-9_]{2,}\b/g) || []) score += weights.get(token) || 0;
      }
      if (score > bestScore) { bestScore = score; best = i; }
    }
    return (best ? '… ' : '') + words.slice(best, best + 90).join(' ') + (best + 90 < words.length ? ' …' : '');
  }
}

export async function loadCorpus() { return resource('data/corpus.json'); }
