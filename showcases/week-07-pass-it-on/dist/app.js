import { Retrieval, loadCorpus, queryVector } from './retrieval.js?v=essay1';
import { Mechanics } from './mechanics.js?v=essay1';

const $ = selector => document.querySelector(selector);
const app = $('#app');
const escape = text => String(text).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
const words = text => text.trim().split(/\s+/).filter(Boolean);
const tokens = text => text.toLowerCase().match(/\b[a-z0-9_]{2,}\b/g) || [];  // same rule as queryVector()
const arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>';
const STAGES = [30, 10, 3];
const BANNED = 5;
// An explicitly authored example round; its rankings are computed live.
// Paraphrased on purpose: keyword search slips (#2 → #8 → #13) while meaning search holds (#1 → #1 → #7).
const EXAMPLE = { prompt: 0, squeezes: ['he makes a tight full-body costume with a web pattern and builds gadgets on his wrists that shoot webs for fighting and swinging around town', 'homemade web costume and wrist gadgets for swinging', 'web swinging costume'] };
let corpus, engine, evidence, promptIndex = 1, state = 'home', roundGeneration = 0, taboo = false;
let stage = 0, squeezes = [], stageRanks = [], banned = [], liveSequence = 0, liveTimer;
let unit = '60', querySource = '3', lastResult, activeQuery = '', busy = false, revealSequence = 0, evidenceRule = 'rarest';
let mechanics;

$('#about-open').addEventListener('click', () => $('#about').showModal());
$('.dialog-close').addEventListener('click', () => $('#about').close());
$('#about').addEventListener('click', event => { if (event.target === $('#about')) { const r = event.target.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) event.target.close(); } });

function mount(html, next) {
  mechanics?.destroy(); mechanics = null;
  clearTimeout(liveTimer); liveSequence++; state = next; app.innerHTML = html;
  document.body.classList.toggle('essay-mode', next === 'findings');
  window.scrollTo({ top: 0, behavior: 'instant' });
  app.focus({ preventScroll: true });
}
function progress(active) {
  return `<ol class="progress" aria-label="Game progress">${['Read', '30 words', '10 words', '3 words', 'Reveal'].map((label, i) => `<li class="${i === active ? 'active' : i < active ? 'done' : ''}"${i === active ? ' aria-current="step"' : ''}><span class="num">${i < active ? '✓' : i + 1}</span>${label}</li>`).join('')}</ol>`;
}
function prompt() { return corpus.prompts[promptIndex]; }
const target = () => prompt().doc;
const rankOf = (list, doc) => list.findIndex(item => item.doc === doc) + 1;
// A keyword query that shares no indexed word with the target cannot rank it; report that instead of a tie position.
const keywordRank = result => result.keyword.find(item => item.doc === target()).score > 0 ? rankOf(result.keyword, target()) : null;
const semanticRank = result => result.semantic ? rankOf(result.semantic, target()) : null;

// The passage's highest-weight TF-IDF words: what taboo mode forbids.
async function bannedWords() {
  const lex = await engine.lexical();
  return [...queryVector(prompt().prompt, lex)].sort((a, b) => b[1] - a[1]).slice(0, BANNED).map(([i]) => lex.vocab[i]);
}
function markBanned(text) {
  if (!banned.length) return escape(text);
  const set = new Set(banned);
  return text.split(/(\b[a-zA-Z0-9_]{2,}\b)/g).map(t => set.has(t.toLowerCase()) ? `<mark class="banned">${escape(t)}</mark>` : escape(t)).join('');
}

function home() {
  roundGeneration++; revealSequence++; busy = false; squeezes = []; stageRanks = []; banned = []; stage = 0;
  mount(`<div class="landing"><section class="hero" aria-labelledby="title"><div class="hero-copy"><span class="handwritten title-doodle">meaning gets<br>a little squeezed ↴</span><h1 id="title">Pass<br>it on.</h1><p>A real passage. Squeeze it into 30 words.<br>Then 10. Then 3.<br>Can the machines still find where it came from?</p></div><div class="hero-stage squeeze-stage" aria-label="An illustrated example of the game"><div class="demo-source"><div class="paper-label"><span class="round">1</span>Read a passage</div><p>“She is able to control the weather and atmosphere…”</p></div><div class="demo-slip slip-10"><div class="paper-label"><span class="round">2</span>Ten words</div><p>weather-controlling woman, one of the strongest mutants alive</p></div><div class="demo-slip slip-3"><div class="paper-label"><span class="round">3</span>Three</div><p>weather controlling mutant</p></div><span class="stage-arrow">every cut<br>costs something ↗</span><div class="hero-note">Keyword search: #?<br>Meaning search: #?</div></div></section><section class="setup" aria-label="Set up a game"><div class="setup-intro"><h2>You squeeze. The machines search.</h2><p>Two real search engines rank all 303 articles<br>live, every time you cut a word.</p></div><fieldset class="budget-group"><legend>Taboo mode</legend><div class="budget-options">${[[false, 'Off', 'any words'], [true, 'On', `ban its ${BANNED} rarest`]].map(([v, a, b]) => `<button type="button" data-taboo="${v}" aria-pressed="${taboo === v}"><strong>${a}</strong><span>${b}</span></button>`).join('')}</div></fieldset><div><button id="start" class="primary" ${corpus ? '' : 'disabled'}>Let’s play ${arrow}</button><p id="load-state" class="load-label" role="status">${corpus ? '<span class="status-dot"></span>303 real articles. Everything stays in this tab.' : 'Opening the box of passages…'}</p></div></section><section class="teaser" aria-labelledby="teaser-h"><div class="teaser-head"><span class="handwritten">What we found</span><h2 id="teaser-h">We squeezed all 303 pages first.</h2><button id="teaser-open" class="primary">Read the finding ${arrow}</button></div><div class="teaser-cards" id="teaser-cards"><p class="small">Loading the evidence…</p></div></section><div class="landing-bottom"><span>Read → 30 → 10 → 3 → open the machine</span><button id="text-demo" class="demo-button" ${corpus ? '' : 'disabled'}>Open an example round ↗</button><button id="findings" class="demo-button" ${corpus ? '' : 'disabled'}>What we found ↗</button></div></div>`, 'home');
  document.querySelectorAll('[data-taboo]').forEach(button => button.addEventListener('click', () => {
    taboo = button.dataset.taboo === 'true';
    document.querySelectorAll('[data-taboo]').forEach(b => b.setAttribute('aria-pressed', b === button));
  }));
  $('#start').addEventListener('click', begin);
  $('#text-demo').addEventListener('click', demo);
  $('#findings').addEventListener('click', () => findings());
  $('#teaser-open').addEventListener('click', () => findings());
  loadEvidence().then(ev => {
    if (state !== 'home') return;
    const s = ev.merge.sets[1];
    $('#teaser-cards').innerHTML = `<button class="teaser-card" data-jump="merge"><b>−${s.vsKeyword['0.5'].losses} <small>heroes</small></b><span>Merge keyword and meaning search the standard 50/50 way, and you lose heroes keyword search had already found.</span></button>`;
    document.querySelectorAll('[data-jump]').forEach(b => b.addEventListener('click', () => findings()));
  }).catch(() => { $('#teaser-cards').innerHTML = ''; });
}

async function begin() {
  if (!corpus) return;
  promptIndex = Math.floor(Math.random() * corpus.prompts.length);
  engine.warmup();
  banned = taboo ? await bannedWords() : [];
  read();
}
function read() {
  mount(`<div class="game-shell">${progress(0)}<div class="round-header"><div><h1>Read it once. Really read it.</h1><p>Next you’ll squeeze this into 30 words, then 10, then 3. Two search engines will try to find the article it came from.</p></div></div><section class="game-panel read-panel"><div class="source-number">Your passage</div><p class="source-passage">${markBanned(prompt().prompt)}</p><div class="source-tip"><span aria-hidden="true">✳</span><span>From one of 303 real Wikipedia articles. Some names may be hidden. ${banned.length ? `<strong>Taboo mode:</strong> the ${BANNED} words marked in red are the passage’s rarest words in the corpus. You can’t use them.` : 'Use your own words or the passage’s. Watch what each search engine rewards.'}</span></div></section><div class="panel-actions"><p>The passage stays on screen while you squeeze.</p><button id="to-squeeze" class="primary">Start squeezing ${arrow}</button></div></div>`, 'read');
  $('#to-squeeze').addEventListener('click', () => squeeze(0));
}

function squeeze(index) {
  stage = index;
  const limit = STAGES[index], previous = squeezes[index - 1] || '';
  mount(`<div class="game-shell">${progress(index + 1)}<div class="round-header"><div><h1>${index === 0 ? 'Squeeze it into 30 words.' : index === 1 ? 'Now 10. What stays?' : 'Three words. Choose carefully.'}</h1><p>${index === 0 ? 'Summarise the yellow passage in the box: your own words, or cut it down. Both search engines rank all 303 articles as you type; #1 means they found it.' : `Your ${STAGES[index - 1]} words are below. Cut them down to ${limit}, keeping the words you think matter.`}</p></div></div><section class="game-panel squeeze-layout"><aside class="squeeze-source"><span class="handwritten">The passage</span><p>${markBanned(prompt().prompt)}</p></aside><div class="description-box"><label for="squeeze">${limit} words or fewer.</label>${index === 0 ? '<button type="button" class="secondary paste" id="paste">Or paste the passage and cut it down</button>' : ''}<textarea id="squeeze" maxlength="400" autocomplete="off" spellcheck="true">${escape(previous)}</textarea><div class="word-meter" id="word-meter"><span id="word-help"></span><strong id="word-count"></strong></div><div class="word-track" id="word-track"><span></span></div><div class="live" aria-live="polite"><div class="live-rank keyword"><span class="method-tag">Keyword search · TF-IDF</span><span class="rank-number" id="live-k">–</span><span class="live-hint">rank of the source article</span><span class="live-was" id="was-k"></span></div><div class="live-rank semantic"><span class="method-tag">Meaning search · MiniLM</span><span class="rank-number" id="live-s">–</span><span class="live-hint">rank of the source article</span><span class="live-was" id="was-s"></span></div></div><div class="weights"><span class="method-tag">What each word is worth to keyword search</span><div class="chips" id="chips"></div><p class="fineprint">Share of the original article’s TF-IDF score. Grey words are ignored (stop words or unseen in the corpus); “0” words are indexed but never appear in this article.</p></div><button class="primary blue" id="next" disabled>${index < 2 ? `Lock it in. Squeeze to ${STAGES[index + 1]}` : 'Lock it in. Reveal'} ${arrow}</button><p id="squeeze-status" class="small muted" role="status"></p></div></section></div>`, 'squeeze');
  const box = $('#squeeze');
  box.addEventListener('input', () => { updateMeter(); scheduleLive(); });
  $('#next').addEventListener('click', lockIn);
  $('#paste')?.addEventListener('click', () => { box.value = prompt().prompt; box.focus(); updateMeter(); scheduleLive(0); });
  box.focus({ preventScroll: true }); box.setSelectionRange(box.value.length, box.value.length);
  const was = stageRanks[index - 1];
  if (was) { $('#was-k').textContent = `was ${was.k ? '#' + was.k : 'unmatched'} at ${STAGES[index - 1]}`; $('#was-s').textContent = `was ${was.s ? '#' + was.s : '–'} at ${STAGES[index - 1]}`; }
  updateMeter(); scheduleLive(0);
}
function usedBanned(text) { const set = new Set(tokens(text)); return banned.filter(b => set.has(b)); }
function updateMeter() {
  const text = $('#squeeze').value, count = words(text).length, limit = STAGES[stage], hit = usedBanned(text);
  $('#word-count').textContent = `${count} / ${limit}`;
  $('#word-meter').classList.toggle('over', count > limit || hit.length > 0);
  $('#word-track').classList.toggle('over', count > limit);
  $('#word-track span').style.width = `${Math.min(100, count / limit * 100)}%`;
  $('#word-help').textContent = hit.length ? `Taboo: “${hit.join('”, “')}” is banned.` : count > limit ? `${count - limit} too many. What can go?` : count === limit ? 'Every word is doing a job.' : count ? `${limit - count} words left.` : 'Start typing.';
  $('#next').disabled = !count || count > limit || hit.length > 0;
}
function scheduleLive(delay = 350) { clearTimeout(liveTimer); liveTimer = setTimeout(live, delay); }
async function live() {
  const text = $('#squeeze')?.value.trim(), sequence = ++liveSequence;
  if (!text) { $('#live-k').textContent = '–'; $('#live-s').textContent = '–'; $('#chips').innerHTML = ''; return; }
  $('#squeeze-status').textContent = 'Searching 303 articles… (the first search opens the meaning model)';
  const result = await engine.search(text, unit);
  if (sequence !== liveSequence || state !== 'squeeze') return;
  const k = keywordRank(result), s = semanticRank(result);
  $('#live-k').textContent = k ? `#${k}` : '—'; $('#live-k').title = k ? '' : 'No shared indexed words with the original article';
  $('#live-s').textContent = s ? `#${s}` : '…';
  $('#squeeze-status').textContent = result.semantic ? '' : 'Meaning search could not open; keyword ranks are still real.';
  paintChips(text, result);
}
function paintChips(text, result) {
  const lex = result.lex, contributions = new Map(engine.contributions(target(), result).map(c => [c.word, c.value]));
  const total = [...contributions.values()].reduce((a, b) => a + b, 0), seen = new Set();
  $('#chips').innerHTML = tokens(text).filter(t => !seen.has(t) && seen.add(t)).map(t => {
    if (banned.includes(t)) return `<span class="chip taboo" title="Banned in taboo mode">${escape(t)}</span>`;
    if (lex.stopSet.has(t) || !lex.index.has(t)) return `<span class="chip ignored" title="Ignored by TF-IDF">${escape(t)}</span>`;
    const share = total ? (contributions.get(t) || 0) / total : 0, idf = lex.idf[lex.index.get(t)];
    return `<span class="chip" style="--share:${share.toFixed(3)}" title="IDF ${idf.toFixed(2)}: ${idf > 4.5 ? 'rare in the corpus' : idf > 2.5 ? 'fairly common' : 'very common'}">${escape(t)} <b>${Math.round(share * 100)}%</b></span>`;
  }).join('');
}
async function lockIn() {
  const text = $('#squeeze').value.trim();
  if (!text || words(text).length > STAGES[stage] || usedBanned(text).length) return;
  $('#next').disabled = true;
  const result = await engine.search(text, unit);
  squeezes[stage] = text; stageRanks[stage] = { k: keywordRank(result), s: semanticRank(result) };
  if (stage < 2) squeeze(stage + 1); else reveal();
}

async function demo() {
  if (!corpus) return;
  promptIndex = EXAMPLE.prompt; taboo = false; banned = []; squeezes = [...EXAMPLE.squeezes];
  engine.warmup();
  mount(`<div class="game-shell">${progress(4)}<section class="game-panel loading-panel"><span class="handwritten">An authored example round.</span><h1>Ranking each squeeze…</h1><div class="loading-line" aria-hidden="true"><span></span></div><p role="status">Searching 303 articles three times. The first run opens the local meaning model.</p></section></div>`, 'loading');
  stageRanks = [];
  for (const text of squeezes) { const r = await engine.search(text, unit); stageRanks.push({ k: keywordRank(r), s: semanticRank(r) }); }
  reveal(true);
}

async function loadEvidence() {
  if (!evidence) evidence = await fetch('data/squeeze-evidence.json?v=essay1').then(r => { if (!r.ok) throw new Error(`Could not load the evidence (${r.status}).`); return r.json(); });
  return evidence;
}
async function reveal(isDemo = false) {
  querySource = '3'; unit = '60';
  const generation = roundGeneration;
  mount(`<div class="game-shell">${progress(4)}<section class="game-panel loading-panel"><span class="handwritten">Let’s open the whole squeeze.</span><h1>Did the meaning<br>make it through?</h1><div class="loading-line" aria-hidden="true"><span></span></div><p role="status">Searching 303 articles and loading the corpus-wide evidence.</p></section></div>`, 'loading');
  try {
    const [result, ev] = await Promise.all([engine.search(squeezes[2], unit), loadEvidence()]);
    if (generation !== roundGeneration) return;
    evidence = ev; lastResult = result; activeQuery = squeezes[2];
    evidenceRule = taboo ? 'taboo' : 'rarest';
    renderReveal(isDemo);
  } catch (error) {
    if (generation !== roundGeneration) return;
    $('.loading-panel').innerHTML = `<h1>That message got stuck.</h1><p>${escape(error.message)}</p><button id="retry" class="primary blue">Try again ${arrow}</button>`;
    $('#retry').addEventListener('click', () => reveal(isDemo));
  }
}
const rankText = r => r ? `#${r}` : '—';
function renderReveal(isDemo = false) {
  const source = prompt(), doc = corpus.documents[source.doc];
  const slip = (i) => `<article class="chain-item"><div class="paper-label"><span class="round">${i + 2}</span>${STAGES[i]} words${isDemo ? ' · example' : ''}</div><p class="description-quote">“${escape(squeezes[i])}”</p><p class="chain-ranks"><span class="k">Keyword ${rankText(stageRanks[i].k)}</span><span class="s">Meaning ${rankText(stageRanks[i].s)}</span></p></article>`;
  mount(`<div class="reveal-shell">${progress(4)}<div class="reveal-heading"><span class="handwritten">${isDemo ? 'A worked example · real search results' : taboo ? 'Taboo round · everybody can look now' : 'Everybody can look now.'}</span><h1>Well, that got squeezed.</h1><p>The original was <strong>${escape(doc.title)}</strong>. Here’s what each cut cost.</p></div><section class="chain chain-4" aria-label="The squeeze, step by step"><article class="chain-item"><div class="paper-label"><span class="round">1</span>The passage</div><p>${markBanned(source.prompt)}</p><details><summary>See the unedited source</summary><p>${escape(source.original)}</p></details><a href="${escape(doc.url)}" target="_blank" rel="noopener">${escape(doc.title)} · Wikipedia ↗</a></article>${STAGES.map((_, i) => slip(i)).join('')}</section><section class="retrieval-panel evidence-panel" aria-labelledby="evidence-heading"><div class="retrieval-header"><div><h2 id="evidence-heading">You vs. 303 articles.</h2><p class="small muted" style="margin-top:7px">Your round, drawn over the same squeeze run automatically on every article.</p></div><div class="query-switch" aria-label="How the automatic squeeze picks words">${[['first', 'Keep the first N'], ['rarest', 'Keep the rarest N'], ['taboo', `Taboo: rarest N, top ${evidence.banned} banned`]].map(([r, l]) => `<button data-rule="${r}" aria-pressed="${r === evidenceRule}">${l}</button>`).join('')}</div></div><figure class="decay"><svg id="decay" viewBox="0 0 900 380" role="img" aria-labelledby="decay-cap"></svg><figcaption id="decay-cap"></figcaption></figure></section><section class="retrieval-panel" aria-labelledby="search-heading"><div class="retrieval-header"><div><h2 id="search-heading">Two ways to find it.</h2><p class="small muted" style="margin-top:7px">Click a result. Read what the machine retrieved.</p></div><div class="query-switch" aria-label="Text to search">${[['3', '3 words'], ['10', '10 words'], ['30', '30 words'], ['original', 'Original passage']].map(([q, l]) => `<button data-query="${q}" aria-pressed="${q === querySource}">${l}</button>`).join('')}</div></div><div class="rank-columns"><section class="keyword" aria-label="Keyword retrieval"><div class="rank-heading"><h3>Remembers words.</h3><span class="method-tag">TF-IDF</span></div><div id="keyword-results"></div></section><section class="semantic" aria-label="Semantic retrieval"><div class="rank-heading"><h3>Looks for context.</h3><label class="sr-only" for="unit">Semantic retrieval unit</label><select id="unit"><option value="60">60-word passages</option><option value="180">180-word passages</option><option value="page">Whole-page averages</option></select></div><div id="semantic-results"></div></section></div><p class="retrieval-note">The numbers are cosine similarities, not confidence or “meaning retained.” Compare ranks within a method. Passage search scores each article by its best matching passage. Both systems can return irrelevant results.</p><p id="search-status" class="small muted" role="status" style="margin-top:12px"></p></section><section id="mechanics" class="mechanics" aria-labelledby="mechanics-title"></section><aside class="insight" aria-live="polite"><span class="handwritten">What got lost?</span><div id="insight"></div></aside><div class="reveal-actions"><button id="again" class="primary">Another round ${arrow}</button><div class="toolrow"><button id="to-findings" class="secondary">What we found</button><button id="save" class="secondary">Save the squeeze</button><button id="methods" class="secondary">What’s being measured?</button></div></div></div>`, 'reveal');
  document.querySelectorAll('[data-query]').forEach(button => button.addEventListener('click', () => {
    querySource = button.dataset.query;
    document.querySelectorAll('[data-query]').forEach(b => b.setAttribute('aria-pressed', b === button));
    updateSearch();
  }));
  document.querySelectorAll('[data-rule]').forEach(button => button.addEventListener('click', () => {
    evidenceRule = button.dataset.rule;
    document.querySelectorAll('[data-rule]').forEach(b => b.setAttribute('aria-pressed', b === button));
    paintDecay();
  }));
  $('#unit').addEventListener('change', event => { unit = event.target.value; updateSearch(); });
  $('#again').addEventListener('click', home);
  $('#methods').addEventListener('click', () => $('#about').showModal());
  $('#save').addEventListener('click', downloadSqueeze);
  $('#to-findings').addEventListener('click', () => findings());

  app.addEventListener('click', handleEvidence);
  paintDecay();
  paintRankings();
  mechanics = new Mechanics($('#mechanics'), { engine, corpus, target: source.doc,
    context: () => ({ text: activeQuery, result: lastResult, unit }) });
}

// Share of articles still found (top 5) as words are removed: one plain 0–100% axis, budgets evenly spaced.
// Lines are labelled at their ends; the gap between the two searches is shaded. On the reveal, the player's own
// ranks sit in a separate row under the axis instead of competing with the corpus lines.
function lineChart(svg, { series, ticks, format, height = 330, extra = 0, after = () => '' }) {
  const B = evidence.budgets, W = 900, m = { l: 56, r: 150, t: 22, b: 40 }, H = height;
  const x = i => m.l + i / (B.length - 1) * (W - m.l - m.r), max = ticks[ticks.length - 1];
  const y = v => H - m.b - v / max * (H - m.t - m.b);
  let g = '<g class="axis">';
  for (const v of ticks) g += `<line x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 10}" y="${y(v) + 4}" text-anchor="end">${format(v)}</text>`;
  B.forEach((b, i) => { g += `<text class="budget" x="${x(i)}" y="${H - m.b + 22}" text-anchor="middle">${b}</text>`; });
  g += `<text x="${m.l}" y="${H - m.b + 22}" text-anchor="end" dx="-10">words</text></g>`;
  const [a, c] = series;
  g += `<path class="gap" d="M${a.values.map((v, i) => `${x(i)},${y(v)}`).join('L')}L${c.values.map((v, i) => `${x(i)},${y(v)}`).reverse().join('L')}Z"/>`;
  for (const s of series) {
    g += `<path d="M${s.values.map((v, i) => `${x(i)},${y(v)}`).join('L')}" fill="none" stroke="${s.color}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>`;
    g += s.values.map((v, i) => `<circle cx="${x(i)}" cy="${y(v)}" r="6" fill="${s.color}" stroke="var(--paper)" stroke-width="2.5"><title>${s.title(i)}</title></circle>`).join('');
    const last = s.values.length - 1;
    g += `<text class="end-label" x="${x(last) + 14}" y="${y(s.values[last]) + 5}" fill="${s.color}">${s.label} ${format(s.values[last], true)}</text>`;
  }
  svg.setAttribute('viewBox', `0 0 ${W} ${H + extra}`);
  svg.innerHTML = g + after(x, H);
}
function paintDecay() {
  const rule = evidence.rules[evidenceRule], B = evidence.budgets, pct = v => Math.round(v * 100) + '%';
  const series = [['keyword', 'Keyword', 'var(--kw)'], ['semantic', 'Meaning', 'var(--blue)']].map(([key, label, color]) => ({
    label, color, values: rule[key].map(s => s.top5),
    title: i => `${label} search, ${B[i]} words: source in the top 5 for ${pct(rule[key][i].top5)} of ${evidence.articles} articles (median rank ${rule[key][i].median})` }));
  const mine = state === 'reveal';
  lineChart($('#decay'), { series, ticks: [0, 0.25, 0.5, 0.75, 1], format: v => pct(v), extra: mine ? 78 : 0,
    after: (x, H) => !mine ? '' : `<g class="you"><text class="you-label" x="56" y="${H + 30}" text-anchor="end" dx="-10">you</text>${STAGES.map((b, i) => {
      const cx = x(B.indexOf(b)), r = stageRanks[i];
      const badge = (dy, rank, color, name) => `<g><rect x="${cx - 34}" y="${H + dy}" width="68" height="24" rx="12" fill="${rank && rank <= 5 ? color : 'var(--paper)'}" stroke="${color}" stroke-width="2"/><text x="${cx}" y="${H + dy + 16}" text-anchor="middle" fill="${rank && rank <= 5 ? 'white' : color}">${name} ${rankText(rank)}</text><title>Your ${b} words: ${name === 'K' ? 'keyword' : 'meaning'} rank ${rankText(rank)}</title></g>`;
      return badge(14, r.k, 'var(--kw)', 'K') + badge(44, r.s, 'var(--blue)', 'M');
    }).join('')}</g>` });
  const at = b => B.indexOf(b), k3 = rule.keyword[at(3)], s3 = rule.semantic[at(3)], k1 = rule.keyword[at(1)], s1 = rule.semantic[at(1)];
  const how = { first: 'keeps the first N words of one sentence from each article', rarest: 'keeps the N rarest words of one sentence from each article', taboo: `bans each sentence’s ${evidence.banned} rarest words, then keeps the rarest N of the rest` }[evidenceRule];
  $('#decay-cap').innerHTML = `How often each search still puts the source article in its top 5, when a robot ${how}. At 3 words: <b class="kw-t">keyword ${pct(k3.top5)}</b>, <b class="sm-t">meaning ${pct(s3.top5)}</b>. At 1 word: ${pct(k1.top5)} and ${pct(s1.top5)}.${mine ? ' Your ranks are in the row underneath; a filled badge means top 5.' : ''} The robot only deletes words; it never paraphrases.`;
}

// The 7.13 write-up as an essay. Draft for layout review: the opening, Act II and its figure.
let mergeWeight = '0.5';
async function findings() {
  if (!corpus) return;
  roundGeneration++;
  mount(`<div class="game-shell"><section class="game-panel loading-panel"><h1>Opening the evidence…</h1><div class="loading-line" aria-hidden="true"><span></span></div></section></div>`, 'loading');
  let ev;
  try { ev = await loadEvidence(); } catch (error) { $('.loading-panel').innerHTML = `<h1>The evidence didn’t load.</h1><p>${escape(error.message)}</p>`; return; }
  const G = ev.merge, nameless = G.sets[1], pct = v => Math.round(v * 100) + '%';
  mount(`<article class="essay">
    <header class="essay-head"><p class="kicker">Pass it on · What we found · Week 7 · 7.13</p><h1>Merge them,<br>and lose them.</h1>
      <p class="dek">Real search systems merge keyword search and meaning search. On Marvel’s ${ev.documents} hero pages, the standard 50/50 merge loses <b>${nameless.vsKeyword['0.5'].losses} heroes</b> that keyword search had already found on its own.</p>
      <p class="draft">Draft · layout preview: the opening, Act II and its figure</p></header>
    <section class="essay-row"><div class="essay-text">
      <p>In the game you squeeze a passage until the search engines can’t find the hero any more. Two engines try. <b class="kw-t">Keyword search</b> (TF-IDF) matches the exact words; <b class="sm-t">meaning search</b> (MiniLM sentence embeddings) matches the gist. They fail on different heroes, so the obvious fix is to use both at once. That is what most real search systems do, and it has a name: hybrid search.</p>
      <p>We tried it on every hero, three ways: ten words from the hero’s story, five words with every name removed, and ${G.sets[2].n} descriptions we wrote ourselves before looking at any results.</p></div>
      <aside class="note"><span class="pill">On Test 2</span><p>Sparse retrieval matches shared words; dense retrieval ranks by embedding similarity (section 6). A hybrid ranks by both.</p></aside></section>
    <section class="essay-row"><div class="essay-text"><p class="act">Act II</p><h2>Merge them, or trust one?</h2>
      <p>The usual recipe, reciprocal rank fusion, gives each engine an equal say. With the five nameless words it puts the right hero in the top 5 for <b>${pct(nameless.top5['0.5'])}</b> of heroes. Keyword search alone managed <b>${pct(nameless.top5.keyword)}</b>. The merge rescues ${nameless.vsKeyword['0.5'].gains} heroes that keyword search missed and drops ${nameless.vsKeyword['0.5'].losses} that it had found. Tip the merge toward keywords and it recovers; at 90/10 it edges past both engines.</p></div>
      <aside class="note"><span class="pill">On Test 2</span><p>Reciprocal rank fusion: score = w / (60 + keyword rank) + (1 − w) / (60 + meaning rank). Only ranks are used, so the two engines’ scores never need to share a scale.</p></aside></section>
    <figure class="card" aria-labelledby="merge-h"><div class="card-head"><h3 id="merge-h">Three tests, one merge</h3><div class="pills" role="group" aria-label="How much say keyword search gets in the merge">${G.weights.map(w => `<button type="button" data-w="${w}" aria-pressed="${String(w) === mergeWeight}">${Math.round(w * 100)} / ${Math.round((1 - w) * 100)}</button>`).join('')}</div></div>
      <div id="merge-bars"></div>
      <figcaption><b>How to read it</b> Each block is one test. The three bars show how often the right hero lands in the top 5 of ${ev.documents} pages: keyword search alone, meaning search alone, and the merge. The buttons set how much say keyword search gets in the merge, from an equal 50/50 to 90/10. The line under each block counts heroes the merge wins and loses compared with keyword search on its own.</figcaption></figure>
    <footer class="essay-foot"><button id="f-play" class="pill-button">Play a round →</button><button id="f-example" class="pill-button ghost">Open the example round</button></footer>
  </article>`, 'findings');
  document.querySelectorAll('[data-w]').forEach(button => button.addEventListener('click', () => {
    mergeWeight = button.dataset.w;
    document.querySelectorAll('[data-w]').forEach(b => b.setAttribute('aria-pressed', b === button));
    paintMerge();
  }));
  $('#f-play').addEventListener('click', home); $('#f-example').addEventListener('click', demo);
  paintMerge();
}
function paintMerge() {
  const pct = v => Math.round(v * 100) + '%', w = mergeWeight, label = `merge ${Math.round(w * 100)}/${Math.round((1 - w) * 100)}`;
  const bar = (name, v, cls) => `<div class="mbar-row ${cls}"><span class="mlab">${name}</span><span class="mtrack"><i style="width:${v * 100}%"></i></span><span class="mval">${pct(v)}</span></div>`;
  $('#merge-bars').innerHTML = evidence.merge.sets.map(s => {
    const d = s.vsKeyword[w], verdict = d.gains > d.losses ? 'better than keyword search alone' : d.gains < d.losses ? 'worse than keyword search alone' : 'no better than keyword search alone';
    return `<div class="mblock"><p class="mtitle">${escape(s.label)} <span>· ${s.n} heroes</span></p>${bar('keyword', s.top5.keyword, 'kw')}${bar('meaning', s.top5.meaning, 'sm')}${bar(label, s.top5[w], 'mg')}<p class="mdelta">vs keyword alone: <b>+${d.gains}</b> rescued, <b>−${d.losses}</b> lost · ${verdict}</p></div>`;
  }).join('');
}

async function updateSearch() {
  const sequence = ++revealSequence;
  busy = true;
  activeQuery = querySource === 'original' ? prompt().prompt : squeezes[STAGES.indexOf(Number(querySource))];
  $('#search-status').textContent = 'Recomputing from the same text with your selected representation…';
  $('#keyword-results').setAttribute('aria-busy', 'true'); $('#semantic-results').setAttribute('aria-busy', 'true');
  document.querySelector('.rank-columns').style.opacity = '.45';
  try {
    const result = await engine.search(activeQuery, unit);
    if (sequence !== revealSequence || state !== 'reveal') return;
    lastResult = result; busy = false; paintRankings();
  } catch (error) {
    if (sequence !== revealSequence || state !== 'reveal') return;
    busy = false; $('#search-status').textContent = error.message;
  } finally {
    if (sequence === revealSequence && state === 'reveal') {
      document.querySelector('.rank-columns').style.opacity = '1';
      $('#keyword-results').removeAttribute('aria-busy'); $('#semantic-results').removeAttribute('aria-busy');
    }
  }
}

function paintRankings() {
  const doc = target();
  const column = (list, method) => {
    if (!list) return `<p class="empty-message">Semantic search couldn’t open in this browser. Keyword results are still real.</p><button class="secondary" id="retry-semantic">Retry semantic model</button>`;
    const rank = rankOf(list, doc);
    if (method === 'keyword' && list[0].score <= 0) return '<p class="empty-message">No indexed words in common. TF-IDF cannot distinguish the articles for this query; an arbitrary tied ranking would be misleading.</p>';
    const topScore = list[0].score;
    const unmatched = method === 'keyword' && list[rank - 1].score === 0;
    return `<div class="target-rank"><span class="rank-number">${unmatched ? '—' : '#' + rank}</span><p><strong>${escape(corpus.documents[doc].title)}</strong>${unmatched ? 'No shared indexed words with the original' : `Original article’s rank out of ${corpus.documents.length}`}</p></div><ol class="rank-list">${list.slice(0, 5).map((item, i) => `<li class="rank-result${item.doc === doc ? ' target' : ''}"><button data-evidence="${method}" data-doc="${item.doc}" aria-expanded="false"><span class="place">${i + 1}</span><span class="result-name">${escape(corpus.documents[item.doc].title)}</span><span class="score">${item.score.toFixed(3)}</span><span class="score-line" aria-hidden="true"><i style="width:${topScore > 0 ? Math.max(0, item.score / topScore * 100) : 0}%"></i></span></button></li>`).join('')}</ol>`;
  };
  $('#keyword-results').innerHTML = column(lastResult.keyword, 'keyword');
  $('#semantic-results').innerHTML = column(lastResult.semantic, 'semantic');
  if ($('#retry-semantic')) $('#retry-semantic').addEventListener('click', updateSearch);
  $('#search-status').textContent = `Searching ${querySource === 'original' ? 'the original passage' : `your ${querySource} words`}: “${activeQuery}”`;
  let title, text;
  const lost = method => STAGES.findIndex((_, i) => !stageRanks[i][method] || stageRanks[i][method] > 5);
  const lk = lost('k'), ls = lost('s');
  if (querySource === 'original') {
    title = 'Same source. A different representation.';
    text = 'The full passage removes your squeezing from the comparison. Change only the semantic retrieval unit: the query stays fixed while the representation of each article changes.';
  } else if (!lastResult.semantic) {
    title = 'One instrument is unavailable.';
    text = 'Keyword retrieval is shown. The semantic model failed to load; retry it to compare methods. No simulated semantic results are substituted.';
  } else if (lk === -1 && ls === -1) {
    title = 'It made it through all three cuts.';
    text = 'Both searches kept the source in their top five from 30 words down to 3. That shows recovery in this round, not that the passage’s meaning survived. Open the evidence and see which words carried it.';
  } else {
    const at = i => i === -1 ? 'never dropped out of the top five' : `dropped out of the top five at ${STAGES[i]} words`;
    title = lk !== -1 && (ls === -1 || ls > lk) ? 'The rare words were holding it up.' : ls !== -1 && (lk === -1 || lk > ls) ? 'Meaning search lost the thread first.' : 'Both lost it at the same cut.';
    text = `Keyword search ${at(lk)}; meaning search ${at(ls)}. Look at which words you cut at that step, then switch between 30, 10 and 3 words to watch the results change.`;
  }
  $('#insight').innerHTML = `<h3>${title}</h3><p>${text}</p>`;
  mechanics?.update();
}
function highlight(text, terms) {
  const set = new Set(terms);
  return text.split(/(\b[a-zA-Z0-9_]{2,}\b)/g).map(token => set.has(token.toLowerCase()) ? `<mark>${escape(token)}</mark>` : escape(token)).join('');
}
function handleEvidence(event) {
  const inspect = event.target.closest('[data-inspect-doc]');
  if (inspect && mechanics && !busy) {
    mechanics.inspect(Number(inspect.dataset.inspectDoc), inspect.dataset.inspectStage); return;
  }
  const button = event.target.closest('[data-evidence]');
  if (!button || busy || state !== 'reveal') return;
  const existing = button.parentElement.querySelector('.evidence');
  if (existing) { existing.remove(); button.setAttribute('aria-expanded', false); return; }
  const doc = Number(button.dataset.doc), method = button.dataset.evidence;
  const article = corpus.documents[doc];
  let text, label, contributions = '';
  if (method === 'keyword') {
    const terms = engine.contributions(doc, lastResult);
    text = highlight(engine.excerpt(doc, lastResult), terms.map(term => term.word));
    label = 'Shared-word evidence · excerpt selected for term coverage';
    contributions = `<div class="contributions">${terms.slice(0, 8).map(term => `<span>${escape(term.word)} ${term.value.toFixed(3)}</span>`).join('')}</div><p class="fineprint">Term contributions to full-page cosine similarity; the excerpt is a reading aid.</p>`;
  } else if (unit === 'page') {
    text = escape(article.text.split(/\s+/).slice(0, 100).join(' ') + ' …');
    label = 'Article opening · score averages passages across the whole page';
  } else {
    text = escape(lastResult.passages[lastResult.winners[doc]].text);
    label = `Best matching passage · at most ${unit} words`;
  }
  const evidenceBox = document.createElement('div'); evidenceBox.className = 'evidence';
  evidenceBox.innerHTML = `<div class="evidence-label">${label}</div>${contributions}<p>${text}</p><a href="${escape(article.url)}" target="_blank" rel="noopener">Read the source article ↗</a><button class="inspect-score" data-inspect-doc="${doc}" data-inspect-stage="${method === 'keyword' ? 'words' : 'angle'}">Take apart this score</button>`;
  button.after(evidenceBox); button.setAttribute('aria-expanded', true);
}
function downloadSqueeze() {
  const source = prompt();
  const payload = { title: 'Pass it on · Squeeze', source: corpus.documents[source.doc].title,
    sourceUrl: corpus.documents[source.doc].url, sourceLicense: 'CC BY-SA 4.0', sourceSnapshot: corpus.source,
    original: source.original, prompt: source.prompt, taboo, banned,
    squeezes: STAGES.map((budget, i) => ({ budget, text: squeezes[i], keywordRank: stageRanks[i].k, semanticRank: stageRanks[i].s })),
    retrievalUnit: unit, querySource, query: activeQuery,
    keyword: lastResult.keyword.slice(0, 5).map(item => ({ title: corpus.documents[item.doc].title, cosine: item.score })),
    semantic: lastResult.semantic?.slice(0, 5).map(item => ({ title: corpus.documents[item.doc].title, cosine: item.score })) || null,
    model: corpus.model, note: 'Cosine similarities are not confidence or percentages of meaning retained.' };
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = 'pass-it-on-squeeze.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}

home();
loadCorpus().then(data => {
  corpus = data; engine = new Retrieval(data);
  if (state === 'home') home();
}).catch(error => {
  if ($('#load-state')) $('#load-state').innerHTML = `Couldn’t load the articles. <button class="demo-button" id="reload">Reload</button>`;
  if ($('#reload')) $('#reload').addEventListener('click', () => location.reload());
  console.error(error);
});
