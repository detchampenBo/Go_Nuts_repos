import { queryVector, sparseScores, ranked } from './retrieval.js?v=squeeze7';

const html = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const tokens = text => text.toLowerCase().match(/\b[a-z0-9_]{2,}\b/g) || [];
const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
const normalized = vector => {
  const norm = Math.hypot(...vector);
  return Array.from(vector, value => norm ? value / norm : 0);
};
const cosine = (a, b) => Math.max(-1, Math.min(1, dot(normalized(a), normalized(b))));
const sparseCosine = (a, b) => [...a].reduce((sum, [i, value]) => sum + value * (b.get(i) || 0), 0);
const signed = value => `${value >= 0 ? '+' : '−'}${Math.abs(value).toFixed(5)}`;
const rankOf = (list, doc) => list.findIndex(item => item.doc === doc) + 1;

export class Mechanics {
  constructor(root, { engine, corpus, target, context }) {
    this.root = root; this.engine = engine; this.corpus = corpus; this.target = target; this.readContext = context;
    this.stage = 'words'; this.doc = target; this.removed = new Set(); this.sequence = 0;
    this.dimension = 0; this.chunkUnit = '60'; this.selectedPassage = null;
    this.root.innerHTML = `<div class="mechanics-heading"><div><span class="handwritten">Okay, but how did it do that?</span><h2 id="mechanics-title">Open the machine.</h2><p>Take apart the actual calculations behind this round. Change one thing and watch what happens.</p></div><span class="mechanics-sticker" aria-hidden="true">Poke around.<br>It won’t break.</span></div><div class="mechanics-tabs" role="tablist" aria-label="Explore the retrieval mechanics">${[['words', 'Words → weights'], ['context', 'Text → vector'], ['angle', 'Vectors → score'], ['chunks', 'Passages → rank']].map(([key, label], i) => `<button type="button" id="tab-${key}" role="tab" data-stage="${key}" aria-selected="${key === this.stage}" aria-controls="mechanics-body" tabindex="${i ? -1 : 0}"><span>${i + 1}</span>${label}</button>`).join('')}</div><div class="mechanics-controls"><div class="mechanics-query"><span>Message being inspected</span><p id="mechanics-query"></p></div><label id="mechanics-doc-label">Compare with article<select id="mechanics-doc">${corpus.documents.map((doc, i) => `<option value="${i}" ${i === this.doc ? 'selected' : ''}>${html(doc.title)}${i === target ? ' · original' : ''}</option>`).join('')}</select></label></div><div id="mechanics-body" role="tabpanel" aria-labelledby="tab-words" tabindex="0"></div>`;
    root.querySelectorAll('[data-stage]').forEach(button => button.addEventListener('click', () => this.selectStage(button.dataset.stage)));
    root.querySelector('[role="tablist"]').addEventListener('keydown', event => {
      const buttons = [...root.querySelectorAll('[data-stage]')];
      const index = buttons.indexOf(document.activeElement);
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % buttons.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + buttons.length) % buttons.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (next !== undefined) { event.preventDefault(); buttons[next].focus(); this.selectStage(buttons[next].dataset.stage); }
    });
    this.el('#mechanics-doc').addEventListener('change', event => { this.doc = Number(event.target.value); this.selectedPassage = null; this.render(); });
    this.update();
  }
  el(selector) { return this.root.querySelector(selector); }
  destroy() { this.sequence++; this.destroyed = true; }
  inspect(doc, stage) {
    this.doc = doc; this.el('#mechanics-doc').value = String(doc); this.selectedPassage = null;
    this.selectStage(stage);
    this.root.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }
  update() {
    const { text } = this.readContext();
    if (text !== this.lastText) { this.removed.clear(); this.contextPair = null; this.contextResult = null; this.lastText = text; }
    this.el('#mechanics-query').textContent = `“${text}”`;
    this.render();
  }
  selectStage(stage) {
    this.stage = stage;
    this.root.querySelectorAll('[data-stage]').forEach(button => {
      const selected = button.dataset.stage === stage;
      button.setAttribute('aria-selected', selected); button.tabIndex = selected ? 0 : -1;
    });
    this.el('#mechanics-body').setAttribute('aria-labelledby', `tab-${stage}`);
    this.el('#mechanics-doc-label').hidden = stage === 'context';
    this.render();
  }
  async render() {
    const sequence = ++this.sequence;
    const body = this.el('#mechanics-body');
    body.setAttribute('aria-busy', true);
    body.innerHTML = '<p class="mechanics-loading" role="status">Opening the calculation…</p>';
    try {
      const content = await this[this.stage](sequence);
      if (this.destroyed || sequence !== this.sequence) return;
      if (content !== undefined) body.innerHTML = content;
      body.removeAttribute('aria-busy');
      this.bind?.();
    } catch (error) {
      if (this.destroyed || sequence !== this.sequence) return;
      body.removeAttribute('aria-busy');
      body.innerHTML = `<p class="mechanics-error">This calculation couldn’t open: ${html(error.message)}</p><button class="secondary" id="mechanics-retry">Try again</button>`;
      this.el('#mechanics-retry').addEventListener('click', () => this.render());
    }
  }
  vectorGrid(vector, label, key = '') {
    const max = Math.max(...vector.map(Math.abs), .00001);
    return `<div class="vector-row"><span class="vector-row-label">${html(label)}</span><div class="vector-grid" role="img" aria-label="${html(label)}: all 384 coordinates; blue is positive, pink is negative. Inspect an individual coordinate with the slider below.">${vector.map((value, i) => `<i aria-hidden="true" data-coordinate="${key}${i}" class="${i === this.dimension ? 'selected-coordinate' : ''}" style="--cell-color:${value >= 0 ? '#3444df' : '#c64c76'};--cell-opacity:${.12 + Math.abs(value) / max * .88}" title="Coordinate ${i + 1}: ${value.toFixed(6)}"></i>`).join('')}</div></div>`;
  }
  async context(sequence) {
    const { text, result } = this.readContext();
    if (!this.contextPair) this.contextPair = [text, text.trim().split(/\s+/).reverse().join(' ')];
    const pair = [...this.contextPair];
    let analysis = this.contextResult;
    if (!analysis || analysis.pair[0] !== pair[0] || analysis.pair[1] !== pair[1]) {
      const [a, b, ta, tb] = await Promise.all([this.engine.vector(pair[0]), this.engine.vector(pair[1]), this.engine.tokens(pair[0]), this.engine.tokens(pair[1])]);
      if (this.destroyed || sequence !== this.sequence) return;
      analysis = { pair, a: normalized(a), b: normalized(b), ta, tb,
        lexical: sparseCosine(queryVector(pair[0], result.lex), queryVector(pair[1], result.lex)),
        aHasWords: queryVector(pair[0], result.lex).size > 0, bHasWords: queryVector(pair[1], result.lex).size > 0,
        semantic: cosine(a, b) };
      this.contextResult = analysis;
    }
    const pieces = tokenData => tokenData.pieces.map(piece => `<span class="wordpiece ${piece.startsWith('[') ? 'special-piece' : ''}">${html(piece)}</span>`).join('');
    this.bind = () => {
      this.el('#compare-texts').addEventListener('submit', event => {
        event.preventDefault();
        const a = this.el('#sentence-a').value.trim(), b = this.el('#sentence-b').value.trim();
        if (!a || !b) return;
        this.contextPair = [a, b]; this.contextResult = null; this.render();
      });
      this.el('#reverse-example').addEventListener('click', () => { this.contextPair = [text, text.trim().split(/\s+/).reverse().join(' ')]; this.contextResult = null; this.render(); });
      this.el('#role-example').addEventListener('click', () => { this.contextPair = ['A person saves a monster.', 'A monster saves a person.']; this.contextResult = null; this.render(); });
      this.el('#bank-example').addEventListener('click', () => { this.contextPair = ['I went to the bank to deposit money.', 'I sat on the river bank near the water.']; this.contextResult = null; this.render(); });
      this.el('#context-dimension').addEventListener('input', event => {
        this.dimension = Number(event.target.value) - 1;
        this.paintContextCoordinate(analysis);
      });
      this.paintContextCoordinate(analysis);
    };
    const fullLexical = analysis.aHasWords && analysis.bHasWords;
    return `<div class="lesson-intro"><h3>Same words. Same meaning?</h3><p>A bag of words forgets order. A pretrained encoder processes words in context before producing a sentence vector. Reorder or rewrite a message and compare what each representation notices.</p></div><form id="compare-texts" class="context-form"><label>Message A<textarea id="sentence-a" maxlength="1200" required rows="2">${html(pair[0])}</textarea></label><label>Message B<textarea id="sentence-b" maxlength="1200" required rows="2">${html(pair[1])}</textarea></label><button class="primary blue" type="submit">Encode both messages</button></form><div class="example-buttons"><span>Try a controlled example:</span><button class="secondary" id="reverse-example">Reverse your words</button><button class="secondary" id="role-example">Swap who saves whom</button><button class="secondary" id="bank-example">Two kinds of bank</button></div><div class="context-comparison"><div><span class="method-tag">TF-IDF · same corpus vocabulary</span><strong id="context-lexical">${fullLexical ? analysis.lexical.toFixed(4) : 'No direction'}</strong><p>${fullLexical && analysis.lexical > .99999 ? 'Identical weighted bags of words. Word order cannot change this representation.' : fullLexical ? 'Shared weighted vocabulary determines this score; the order is discarded.' : 'At least one message has no indexed words. Its zero vector has no cosine direction.'}</p></div><div><span class="method-tag">MiniLM · contextual sentence vectors</span><strong id="context-semantic">${analysis.semantic.toFixed(4)}</strong><p>The actual cosine between these sentence embeddings. A high value can still miss an important difference in meaning.</p></div></div><div class="encoder-flow"><span>WordPieces</span><b aria-hidden="true">→</b><span>Pretrained contextual encoder</span><b aria-hidden="true">→</b><span>Mean pooling</span><b aria-hidden="true">→</b><span>Normalize</span></div><details class="math-detail"><summary>See the exact input tokens</summary><p>The tokenizer splits text into WordPieces. <code>[CLS]</code> and <code>[SEP]</code> are special model tokens. Context enters in the encoder; the token IDs alone are vocabulary lookups.</p><div class="piece-row"><b>A · ${analysis.ta.used} input tokens</b>${pieces(analysis.ta)}</div><div class="piece-row"><b>B · ${analysis.tb.used} input tokens</b>${pieces(analysis.tb)}</div><p class="fineprint">Input limit: 256 tokens, including special tokens. ${analysis.ta.total > analysis.ta.used || analysis.tb.total > analysis.tb.used ? `Truncation occurred: full token counts are A=${analysis.ta.total}, B=${analysis.tb.total}; only the displayed inputs were encoded.` : 'Both complete messages fit inside the input limit.'}</p></details><div class="vector-workbench"><div class="vector-legend"><strong>384 numbers per message</strong><span><i class="positive-key"></i>Positive <i class="negative-key"></i>Negative</span></div>${this.vectorGrid(analysis.a, 'Message A', 'a')}${this.vectorGrid(analysis.b, 'Message B', 'b')}<label class="dimension-label" for="context-dimension">Inspect a coordinate <output id="context-coordinate-label"></output></label><input id="context-dimension" class="dimension-slider" type="range" min="1" max="384" value="${this.dimension + 1}"><div id="context-coordinate" class="coordinate-equation" aria-live="polite"></div><p class="fineprint">Cell order is coordinate order, not a semantic map. Color intensity is scaled separately within each row for readability. The slider shows the actual values. Individual coordinates do not have labels like “heroic” or “angry.”</p></div><div class="lesson-takeaway"><strong>The catch:</strong> context-sensitive does not mean meaning-perfect. The encoder was pretrained elsewhere; this round computes new representations using learned weights. This sandbox leaves your game messages and rankings unchanged.</div>`;
  }
  paintContextCoordinate(analysis) {
    const i = this.dimension;
    this.el('#context-coordinate-label').textContent = `${i + 1} / 384`;
    this.el('#context-coordinate').innerHTML = `<span>A[${i + 1}] <b>${signed(analysis.a[i])}</b></span><span>B[${i + 1}] <b>${signed(analysis.b[i])}</b></span>`;
    this.root.querySelectorAll('[data-coordinate]').forEach(cell => cell.classList.toggle('selected-coordinate', Number(cell.dataset.coordinate.slice(1)) === i));
  }
  async angle() {
    const { text, result, unit } = this.readContext();
    if (!result.semantic) throw new Error('The semantic model is unavailable. Retry semantic search above first.');
    const [query, data] = await Promise.all([this.engine.vector(text), this.engine.data(unit)]);
    const index = unit === 'page' ? this.doc : result.winners[this.doc];
    const q = normalized(query), d = normalized(data.vectors.subarray(index * 384, (index + 1) * 384));
    const products = q.map((value, i) => value * d[i]);
    const score = Math.max(-1, Math.min(1, products.reduce((sum, value) => sum + value, 0)));
    const theta = Math.acos(score), degrees = theta * 180 / Math.PI;
    const x = 180 + 145 * Math.cos(theta), y = 205 - 145 * Math.sin(theta);
    const arcX = 180 + 48 * Math.cos(theta), arcY = 205 - 48 * Math.sin(theta);
    const doc = this.corpus.documents[this.doc];
    this.bind = () => {
      this.el('#angle-dimension').addEventListener('input', event => {
        this.dimension = Number(event.target.value) - 1; this.paintAngleCoordinate(q, d, products);
      });
      this.paintAngleCoordinate(q, d, products);
    };
    return `<div class="lesson-intro"><h3>A similarity score is an angle.</h3><p>Both vectors are normalized to length 1. Multiply matching coordinates, then add all 384 products. That dot product is their cosine similarity.</p></div><div class="angle-workbench"><figure class="angle-figure"><svg viewBox="0 0 390 380" role="img" aria-label="The actual angle between the query and selected article vector is ${degrees.toFixed(2)} degrees."><defs><marker id="query-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 6 3 0 6" fill="#3444df"/></marker><marker id="article-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 6 3 0 6" fill="#c64c76"/></marker></defs><circle cx="180" cy="205" r="145" fill="none" stroke="#d6d7e6" stroke-dasharray="4 5"/><path d="M180 205H325" stroke="#3444df" stroke-width="4" marker-end="url(#query-arrow)"/><path d="M180 205L${x} ${y}" stroke="#c64c76" stroke-width="4" marker-end="url(#article-arrow)"/><path d="M228 205A48 48 0 ${theta > Math.PI ? 1 : 0} 0 ${arcX} ${arcY}" fill="none" stroke="#77798e" stroke-width="1.5"/><circle cx="180" cy="205" r="4" fill="#202142"/><text x="240" y="231" fill="#3444df">query · length 1</text><text x="${Math.min(255, Math.max(8, x - 35))}" y="${Math.max(20, y - 17)}" fill="#c64c76">article · length 1</text><text x="211" y="183" fill="#202142">${degrees.toFixed(1)}°</text></svg><figcaption>This shows their true pairwise angle in the plane spanned by the two vectors. It does not treat two embedding coordinates as the whole space.</figcaption></figure><div class="angle-answer"><span class="handwritten">Same calculation. All the dimensions.</span><strong id="angle-cosine">${score.toFixed(4)}</strong><span>cos(${degrees.toFixed(2)}°)</span><p>${html(doc.title)} · ${unit === 'page' ? 'normalized whole-page mean' : `best matching ${unit}-word passage`}</p><p class="fineprint">0° → cosine 1<br>90° → cosine 0<br>180° → cosine −1<br>Opposite directions do not necessarily mean opposite meanings.</p></div></div><div class="vector-workbench"><div class="vector-legend"><strong>The actual vectors being multiplied</strong><span><i class="positive-key"></i>Positive <i class="negative-key"></i>Negative</span></div>${this.vectorGrid(q, 'Query', 'q')}${this.vectorGrid(d, 'Article / passage', 'd')}<label class="dimension-label" for="angle-dimension">Pick one of the 384 multiplications <output id="angle-coordinate-label"></output></label><input class="dimension-slider" id="angle-dimension" type="range" min="1" max="384" value="${this.dimension + 1}"><div id="angle-coordinate" class="coordinate-equation" aria-live="polite"></div><p class="fineprint">Every coordinate contributes. Positive and negative products can cancel; the final score sums them all. The displayed article vector has been renormalized after storage quantization.</p></div><details class="math-detail"><summary>Show all 384 products and their sum</summary><div class="math-table-wrap all-products"><table><thead><tr><th>Coordinate</th><th>Query</th><th>Article / passage</th><th>Product</th></tr></thead><tbody>${products.map((value, i) => `<tr><th>${i + 1}</th><td>${signed(q[i])}</td><td>${signed(d[i])}</td><td>${signed(value)}</td></tr>`).join('')}</tbody><tfoot><tr><th colspan="3">Sum of unrounded products</th><td>${score.toFixed(6)}</td></tr></tfoot></table></div></details><div class="lesson-takeaway"><strong>Why normalize?</strong> It removes vector length from the comparison, so the angle determines similarity. Select another article above to see its actual angle. This is geometry within one representation, not a probability that the article is right.</div>`;
  }
  paintAngleCoordinate(q, d, products) {
    const i = this.dimension;
    this.el('#angle-coordinate-label').textContent = `${i + 1} / 384`;
    this.el('#angle-coordinate').innerHTML = `<span>${signed(q[i])}</span><b>×</b><span>${signed(d[i])}</span><b>=</b><strong>${signed(products[i])}</strong>`;
    this.root.querySelectorAll('[data-coordinate]').forEach(cell => cell.classList.toggle('selected-coordinate', Number(cell.dataset.coordinate.slice(1)) === i));
  }
  async chunks(sequence) {
    const { text } = this.readContext();
    const [query, sixty, oneEighty, whole, data] = await Promise.all([
      this.engine.vector(text), this.engine.search(text, '60'), this.engine.search(text, '180'),
      this.engine.search(text, 'page'), this.engine.data(this.chunkUnit),
    ]);
    if (this.destroyed || sequence !== this.sequence) return;
    if (![sixty, oneEighty, whole].every(result => result.semantic)) throw new Error('Semantic retrieval must be available to compare passage units.');
    const q = normalized(query);
    const passages = [];
    for (let i = 0; i < data.passages.length; i++) {
      if (data.passages[i].doc !== this.doc) continue;
      const vector = normalized(data.vectors.subarray(i * 384, (i + 1) * 384));
      passages.push({ index: i, text: data.passages[i].text, score: dot(q, vector) });
    }
    const winner = passages.reduce((best, passage) => passage.score > best.score ? passage : best, passages[0]);
    if (!passages.some(passage => passage.index === this.selectedPassage)) this.selectedPassage = winner.index;
    const selected = passages.find(passage => passage.index === this.selectedPassage);
    const comparison = [['60', '60-word passages', sixty], ['180', '180-word passages', oneEighty], ['page', 'Whole-page average', whole]];
    this.bind = () => {
      this.root.querySelectorAll('[data-chunk-unit]').forEach(button => button.addEventListener('click', () => {
        this.chunkUnit = button.dataset.chunkUnit; this.selectedPassage = null; this.render();
      }));
      this.root.querySelectorAll('[data-passage]').forEach(button => button.addEventListener('click', () => {
        this.selectedPassage = Number(button.dataset.passage);
        const passage = passages.find(p => p.index === this.selectedPassage);
        this.root.querySelectorAll('[data-passage]').forEach(b => b.setAttribute('aria-pressed', b === button));
        this.el('#selected-passage-text').textContent = passage.text;
        this.el('#selected-passage-label').textContent = `Passage ${passages.indexOf(passage) + 1} · ${passage.text.split(/\s+/).length} words · cosine ${passage.score.toFixed(4)}${passage.index === winner.index ? ' · best match' : ''}`;
      }));
    };
    return `<div class="lesson-intro"><h3>Find a detail. Or average it away.</h3><p>The query and encoder stay fixed. Only the article representation changes. Passage retrieval takes the highest passage score; whole-page retrieval compares the query with a normalized average of the 180-word passage vectors.</p></div><div class="chunk-ranks">${comparison.map(([key, label, result]) => {
      const rank = rankOf(result.semantic, this.doc), match = result.semantic.find(item => item.doc === this.doc);
      return `<div class="chunk-rank ${key === this.chunkUnit ? 'chosen-chunk' : ''}"><span>${label}</span><strong>#${rank}</strong><small>of 303 · cosine ${match.score.toFixed(4)}</small>${key === 'page' ? '<p>Mean of vectors, then normalize.<br>Not the mean of passage scores.</p>' : `<button class="secondary" data-chunk-unit="${key}" aria-pressed="${key === this.chunkUnit}">Inspect these passages</button>`}</div>`;
    }).join('')}</div><div class="chunk-explanation"><span class="handwritten">Open the article’s memory.</span><p>Each numbered piece is a real passage of <strong>${html(this.corpus.documents[this.doc].title)}</strong>, in source order. Blue intensity shows query similarity on a fixed 0–1 scale; the starred piece wins. Click any piece to read it.</p></div><div class="passage-strip" aria-label="Article passages in source order">${passages.map((passage, i) => `<button class="passage-tile ${passage.index === winner.index ? 'winning-passage' : ''}" data-passage="${passage.index}" aria-pressed="${passage.index === this.selectedPassage}" style="--match:${Math.max(0, passage.score)}" aria-label="Passage ${i + 1}, ${passage.text.split(/\s+/).length} words, cosine ${passage.score.toFixed(4)}${passage.index === winner.index ? ', best match' : ''}"><span>${passage.index === winner.index ? "★ " : ""}${i + 1}</span><small>${passage.text.split(/\s+/).length}w</small></button>`).join('')}</div><div class="passage-reading"><strong id="selected-passage-label">Passage ${passages.indexOf(selected) + 1} · ${selected.text.split(/\s+/).length} words · cosine ${selected.score.toFixed(4)}${selected.index === winner.index ? ' · best match' : ''}</strong><p id="selected-passage-text">${html(selected.text)}</p></div><details class="math-detail"><summary>What exactly gets averaged?</summary><p>For a page with passage vectors u₁ … uₙ, first calculate <code>m = (u₁ + … + uₙ) / n</code>. Then calculate <code>page = m / ||m||</code>. Finally score <code>query · page</code>. Passage search instead uses <code>max(query · uᵢ)</code>. These are different operations and can produce different ranks.</p><p class="fineprint">Passage vectors are unit-normalized before averaging. A 60- or 180-word budget is a maximum, not an exact length. Splits respect sentence boundaries when possible and also enforce the encoder’s 256-token limit. Comparisons use the same corpus and query; storage and model quantization add small numerical approximations.</p></details><div class="lesson-takeaway"><strong>Look for a local clue:</strong> does the winning passage contain the detail your words tried to keep? Shorter passages may help, but do not always win. Maximum-passage scoring also gives articles with many passages more chances to match.</div>`;
  }
  async words() {
    const { text, result } = this.readContext();
    const lex = result.lex;
    const raw = tokens(text);
    const usable = raw.filter(word => !this.removed.has(word));
    const query = queryVector(usable.join(' '), lex);
    const scores = ranked(sparseScores(query, lex.rows));
    const [indices, weights] = lex.rows[this.doc];
    const documentWeights = new Map(indices.map((index, j) => [index, weights[j]]));
    const count = new Map(); usable.forEach(word => count.set(word, (count.get(word) || 0) + 1));
    const allWords = [...new Set(raw)];
    const rows = allWords.filter(word => lex.index.has(word) && !lex.stopSet.has(word)).map(word => {
      const index = lex.index.get(word), frequency = count.get(word) || 0;
      const idf = lex.idf[index], tf = frequency ? 1 + Math.log(frequency) : 0;
      const q = query.get(index) || 0, d = documentWeights.get(index) || 0;
      const df = Math.round((this.corpus.documents.length + 1) / Math.exp(idf - 1) - 1);
      return { word, frequency, idf, tf, q, d, df, product: q * d };
    }).sort((a, b) => b.product - a.product || b.idf - a.idf);
    const sum = rows.reduce((total, row) => total + row.product, 0);
    const totalCount = this.corpus.documents.length;
    const rank = query.size && scores.find(item => item.doc === this.doc).score > 0 ? `#${rankOf(scores, this.doc)}` : 'No match';
    const originalRank = result.keyword.find(item => item.doc === this.doc).score > 0 ? `#${rankOf(result.keyword, this.doc)}` : 'No match';
    const tokenMarkup = raw.map(word => {
      const ignored = lex.stopSet.has(word) || !lex.index.has(word);
      const reason = lex.stopSet.has(word) ? 'English stop word' : !lex.index.has(word) ? 'Not in the corpus vocabulary' : 'Click to remove or restore this word';
      return `<button type="button" class="word-token ${ignored ? 'ignored' : ''} ${this.removed.has(word) ? 'removed' : ''}" data-word="${html(word)}" ${ignored ? 'disabled' : ''} aria-pressed="${!this.removed.has(word)}" title="${reason}">${html(word)}</button>`;
    }).join('');
    this.bind = () => {
      this.root.querySelectorAll('[data-word]').forEach(button => button.addEventListener('click', () => {
        const word = button.dataset.word;
        if (this.removed.has(word)) this.removed.delete(word); else this.removed.add(word);
        this.render();
      }));
      this.el('#reset-words').addEventListener('click', () => { this.removed.clear(); this.render(); });
    };
    return `<div class="lesson-intro"><h3>Which words do the pulling?</h3><p>TF-IDF turns the message into a weighted bag of words. Click a word to remove all its occurrences from this query. Watch the selected article’s score and rank change.</p></div><div class="token-workbench">${tokenMarkup || '<span>No two-character word tokens.</span>'}</div><div class="lesson-toolbar"><span>Faded = stop word or outside the vocabulary. Crossed out = removed by you.</span><button class="secondary" id="reset-words" ${this.removed.size ? '' : 'disabled'}>Restore words</button></div><div class="word-calculation"><div class="term-pulls">${rows.length ? rows.map(row => `<div class="term-pull ${row.frequency ? '' : 'muted-term'}"><span>${html(row.word)}</span><div class="pull-track"><i style="width:${Math.max(0, Math.min(100, (sum ? row.product / sum : 0) * 100))}%"></i></div><span>${row.product.toFixed(4)}</span><small>in ${row.df} / ${totalCount} articles</small></div>`).join('') : '<p class="empty-message">None of these words enters the TF-IDF vocabulary.</p>'}<p class="fineprint">Bar length shows each word’s share of the score. The numbers are the actual cosine contributions; they add to the score.</p></div><div class="calculation-answer"><span class="handwritten">Add the shared-word products</span><strong id="word-cosine">${sum.toFixed(4)}</strong><span>TF-IDF cosine similarity</span><div class="rank-change"><span>${originalRank}<small>with the full message</small></span><b aria-hidden="true">→</b><span id="word-rank">${rank}<small>with your words removed</small></span></div><p>${query.size ? `${query.size} vocabulary terms survive. Their query vector is normalized again after each removal.` : 'Nothing remains to compare. A zero vector has no cosine direction; retrieval assigns zero overlap.'}</p></div></div><details class="math-detail"><summary>Follow the numbers: counts → weights → cosine</summary><p>Keep lowercase word tokens of at least two characters, remove English stop words, and count each remaining word. Apply <code>tf = 1 + ln(count)</code>, then <code>idf = 1 + ln((1 + 303) / (1 + document frequency))</code>. Multiply tf × idf and normalize the whole vector to length 1. The query and article are both normalized, so cosine is the sum of their matching coordinate products.</p><div class="math-table-wrap"><table><thead><tr><th>Word</th><th>Count</th><th>IDF</th><th>TF × IDF</th><th>Query weight</th><th>Article weight</th><th>Product</th></tr></thead><tbody>${rows.map(row => `<tr><th>${html(row.word)}</th><td>${row.frequency}</td><td>${row.idf.toFixed(3)}</td><td>${(row.tf * row.idf).toFixed(3)}</td><td>${row.q.toFixed(4)}</td><td>${row.d.toFixed(4)}</td><td>${row.product.toFixed(5)}</td></tr>`).join('')}</tbody></table></div><p class="fineprint">Article weights use the complete article. The table includes every indexed term in this message; missing article terms contribute zero. Removing words changes only the query, leaving corpus IDF and article vectors fixed.</p></details><div class="lesson-takeaway"><strong>Try it:</strong> remove the rarest word, then a common one. Rarity changes IDF, but the effect on a particular match also depends on which words the article contains.</div>`;
  }
}
