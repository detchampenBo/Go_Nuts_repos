import { Retrieval, loadCorpus } from './retrieval.js';

const $ = selector => document.querySelector(selector);
const app = $('#app');
const escape = text => String(text).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
const words = text => text.trim().split(/\s+/).filter(Boolean);
const arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>';
const clock = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="13" r="8"/><path d="M12 8v5l3 2M9 2h6M12 2v3"/></svg>';
const doodle = `<svg viewBox="0 0 300 210" role="img" aria-label="An example doodle: a person underneath a raincloud"><path d="M64 49c-11-27 16-40 33-26 6-26 42-23 48-4 21-18 51-3 47 20 29-2 30 36 4 37H69c-23-2-24-25-5-27Z"/><path d="m94 89-5 15m43-17-7 16m46-13-6 16m-51 7-7 12m43-12-6 13"/><path d="m189 82-17 28 19-1-12 26" stroke="#e8a515" stroke-width="5"/><circle cx="132" cy="146" r="18"/><path d="m127 143 1 1m11-1 1 1m-12 10c4 3 7 3 11 0M131 165l-3 25m-1-17-27-12m29 12 28-14m-29 31-17 16m17-16 16 17M75 207c43-7 97-7 140-1"/><path d="m112 123 6-3m30 0 6 4"/></svg>`;
let corpus, engine, budget = 10, promptIndex = 1, state = 'home', timer, timerEnd = 0, roundGeneration = 0;
let strokes = [], currentStroke = null, color = '#3444df', width = 4, eraser = false, drawing = '', description = '', descriptionTimedOut = false;
let unit = '60', querySource = 'description', lastResult, activeQuery = '', busy = false, revealSequence = 0;
let canvas, ctx, paintFrame;

$('#about-open').addEventListener('click', () => $('#about').showModal());
$('.dialog-close').addEventListener('click', () => $('#about').close());
$('#about').addEventListener('click', event => { if (event.target === $('#about')) { const r = event.target.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) event.target.close(); } });

function mount(html, next) {
  clearInterval(timer); timer = null; state = next; app.innerHTML = html;
  window.scrollTo({ top: 0, behavior: 'instant' });
  app.focus({ preventScroll: true });
}
function progress(active) {
  return `<ol class="progress" aria-label="Game progress">${['Read', 'Draw', 'Pass', 'Describe', 'Reveal'].map((label, i) => `<li class="${i === active ? 'active' : i < active ? 'done' : ''}"${i === active ? ' aria-current="step"' : ''}><span class="num">${i < active ? '✓' : i + 1}</span>${label}</li>`).join('')}</ol>`;
}
function startTimer(seconds, done) {
  timerEnd = performance.now() + seconds * 1000;
  const tick = () => {
    const remaining = Math.max(0, Math.ceil((timerEnd - performance.now()) / 1000));
    const display = $('#timer');
    if (display) { display.innerHTML = `${clock}<span>${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, '0')}</span>`; display.classList.toggle('urgent', remaining <= 10); }
    if (!remaining) { clearInterval(timer); timer = null; done(); }
  };
  tick(); timer = setInterval(tick, 250);
}
function prompt() { return corpus.prompts[promptIndex]; }

function home() {
  roundGeneration++; revealSequence++; busy = false; strokes = []; drawing = ''; description = ''; currentStroke = null;
  mount(`<div class="landing"><section class="hero" aria-labelledby="title"><div class="hero-copy"><span class="handwritten title-doodle">meaning gets<br>a little messy ↴</span><h1 id="title">Pass<br>it on.</h1><p>A passage becomes a picture.<br>A picture becomes a few words.<br>Can a machine find its way back?</p></div><div class="hero-stage" aria-label="An illustrated example of the game"><div class="demo-source"><div class="paper-label"><span class="round">1</span>Read a passage</div><p>“She is able to control the weather and atmosphere…”</p></div><div class="demo-drawing"><div class="paper-label"><span class="round">2</span>Draw what you mean</div>${doodle}</div><span class="stage-arrow">no words,<br>just scribbles ↗</span><div class="hero-note">Somewhere along<br>the way…</div><div class="demo-description"><small>3 &nbsp; Someone else describes it</small>“someone having a very bad hair day”</div></div></section><section class="setup" aria-label="Set up a game"><div class="setup-intro"><h2>Two humans. One screen.</h2><p>One draws. One describes. Two search engines guess.<br>About three minutes. Absolutely no artistic talent needed.</p></div><fieldset class="budget-group"><legend>Your partner’s word budget</legend><div class="budget-options">${[30, 10, 3].map(n => `<button type="button" data-budget="${n}" aria-label="${n} words" aria-pressed="${budget === n}"><strong>${n}</strong><span>${n === 30 ? 'roomy' : n === 10 ? 'tricky' : 'brutal'}</span></button>`).join('')}</div></fieldset><div><button id="start" class="primary" ${corpus ? '' : 'disabled'}>Let’s play ${arrow}</button><p id="load-state" class="load-label" role="status">${corpus ? '<span class="status-dot"></span>303 real articles. Your drawing stays here.' : 'Opening the box of passages…'}</p></div></section><div class="landing-bottom"><span>Read → draw → pass → describe → the big reveal</span><button id="demo" class="demo-button" ${corpus ? '' : 'disabled'}>Just me? Open a worked example ↗</button></div></div>`, 'home');
  document.querySelectorAll('[data-budget]').forEach(button => button.addEventListener('click', () => {
    budget = Number(button.dataset.budget);
    document.querySelectorAll('[data-budget]').forEach(b => b.setAttribute('aria-pressed', b === button));
  }));
  $('#start').addEventListener('click', begin);
  $('#demo').addEventListener('click', demo);
}

function begin() {
  if (!corpus) return;
  promptIndex = Math.floor(Math.random() * corpus.prompts.length);
  engine.warmup();
  read();
}
function read() {
  mount(`<div class="game-shell">${progress(0)}<div class="round-header"><div><h1>Keep the picture in your head.</h1><p>Player one: read this passage. You’ll draw it next. Keep it secret from your partner.</p></div></div><section class="game-panel read-panel"><div class="source-number">Your secret passage</div><p class="source-passage">${escape(prompt().prompt)}</p><div class="source-tip"><span aria-hidden="true">✳</span><span>From one of 303 real Wikipedia articles. Some names may be hidden. Draw the idea, not the words. Your partner gets just <strong>${budget} words</strong> to describe your picture.</span></div></section><div class="panel-actions"><p>You can still peek at this passage while drawing.</p><button id="to-draw" class="primary">I’ve got a picture ${arrow}</button></div></div>`, 'read');
  $('#to-draw').addEventListener('click', draw);
}

function draw() {
  strokes = []; currentStroke = null; descriptionTimedOut = false;
  mount(`<div class="game-shell">${progress(1)}<div class="round-header"><div><h1>Make a beautiful mess.</h1><p>Player one: draw the passage. No letters, names, or numbers. You have 90 seconds.</p></div><div class="timer" id="timer" aria-label="Drawing time remaining"></div></div><section class="game-panel draw-layout"><div class="canvas-wrap"><canvas id="drawing" class="drawing-canvas" width="1000" height="750" tabindex="0" aria-label="Drawing area. Use your mouse, pen, or finger to draw. Press Control or Command Z to undo."></canvas><span class="canvas-hint">Your masterpiece goes here.</span></div><aside class="draw-sidebar"><div class="prompt-note"><span class="handwritten">Psst. The passage.</span><p>${escape(prompt().prompt)}</p></div><div class="tool-settings"><div><span class="tool-label">Ink</span><div class="colors">${['#3444df', '#202142', '#ed6d88', '#e6ab23', '#2a9a69'].map(c => `<button class="color" data-color="${c}" style="--color:${c}" aria-label="${({ '#3444df': 'Blue', '#202142': 'Black', '#ed6d88': 'Pink', '#e6ab23': 'Yellow', '#2a9a69': 'Green' })[c]} ink" aria-pressed="${c === color}"></button>`).join('')}</div></div><div class="brush-control"><label class="tool-label" for="brush">Stroke width</label><input id="brush" class="brush-range" type="range" min="2" max="16" value="${width}" aria-label="Brush width"></div></div><div class="toolrow"><button class="tool" id="eraser" aria-label="Eraser" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 13 10-10 7 7-10 10H7l-3-3zM10 7l7 7M11 20h10"/></svg></button><button class="tool" id="undo" aria-label="Undo last stroke"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 4-6 6 6 6M3 10h10a7 7 0 0 1 7 7v3"/></svg></button><button class="tool" id="clear">Clear</button></div><p class="small">Mouse, finger, or stylus.<br>A stick figure is a valid artistic choice.</p></aside></section><div class="panel-actions"><p id="draw-status" role="status">A drawing is needed before you can pass it on.</p><button class="primary" id="finish-draw" disabled>Fold it & pass it ${arrow}</button></div></div>`, 'draw');
  canvas = $('#drawing'); ctx = canvas.getContext('2d'); eraser = false;
  const bounds = canvas.getBoundingClientRect(); canvas.height = Math.round(1000 * bounds.height / bounds.width);
  function point(event) { const rect = canvas.getBoundingClientRect(); return [(event.clientX - rect.left) * canvas.width / rect.width, (event.clientY - rect.top) * canvas.height / rect.height]; }
  canvas.addEventListener('pointerdown', event => {
    if (event.button && event.pointerType === 'mouse') return;
    event.preventDefault(); canvas.setPointerCapture(event.pointerId);
    currentStroke = { color: eraser ? '#ffffff' : color, width: width * (eraser ? 4 : 1) * 1.7, points: [point(event)], erase: eraser };
    strokes.push(currentStroke); redraw(); updateDrawingState();
  });
  canvas.addEventListener('pointermove', event => {
    if (!currentStroke) return;
    currentStroke.points.push(point(event));
    if (!paintFrame) paintFrame = requestAnimationFrame(() => { paintFrame = null; redraw(); });
  });
  const end = () => { currentStroke = null; updateDrawingState(); };
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end); canvas.addEventListener('lostpointercapture', end);
  canvas.addEventListener('keydown', event => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') { event.preventDefault(); strokes.pop(); redraw(); updateDrawingState(); } });
  $('#brush').addEventListener('input', event => width = Number(event.target.value));
  document.querySelectorAll('[data-color]').forEach(button => button.addEventListener('click', () => {
    color = button.dataset.color; eraser = false; $('#eraser').setAttribute('aria-pressed', false);
    document.querySelectorAll('[data-color]').forEach(b => b.setAttribute('aria-pressed', b === button));
  }));
  $('#eraser').addEventListener('click', event => { eraser = !eraser; event.currentTarget.setAttribute('aria-pressed', eraser); });
  $('#undo').addEventListener('click', () => { strokes.pop(); redraw(); updateDrawingState(); });
  $('#clear').addEventListener('click', () => { strokes = []; currentStroke = null; redraw(); updateDrawingState(); });
  $('#finish-draw').addEventListener('click', finishDrawing);
  redraw();
  startTimer(90, () => {
    if (strokes.some(stroke => !stroke.erase)) finishDrawing();
    else { $('#draw-status').textContent = 'Time’s up. Add a quick sketch, then pass it on.'; $('#timer').setAttribute('aria-label', 'Drawing time ended'); }
  });
}
function redraw() {
  if (!ctx) return;
  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (const stroke of strokes) {
    ctx.strokeStyle = stroke.color; ctx.fillStyle = stroke.color; ctx.lineWidth = stroke.width; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const [first, ...rest] = stroke.points;
    if (!rest.length) { ctx.beginPath(); ctx.arc(first[0], first[1], stroke.width / 2, 0, Math.PI * 2); ctx.fill(); }
    else { ctx.beginPath(); ctx.moveTo(...first); for (const p of rest) ctx.lineTo(...p); ctx.stroke(); }
  }
}
function updateDrawingState() {
  const hasDrawing = strokes.some(stroke => !stroke.erase);
  if ($('.canvas-hint')) $('.canvas-hint').hidden = hasDrawing;
  if ($('#finish-draw')) $('#finish-draw').disabled = !hasDrawing;
  if ($('#draw-status')) $('#draw-status').textContent = hasDrawing ? 'Happy accidents count. Ready when you are.' : 'A drawing is needed before you can pass it on.';
}
function finishDrawing() {
  if (!strokes.some(stroke => !stroke.erase)) return;
  currentStroke = null; redraw(); drawing = canvas.toDataURL('image/png'); handoff();
}
function handoff() {
  // The original passage and drawing tools leave the DOM before the next player sees the screen.
  mount(`<div class="game-shell">${progress(2)}<section class="handoff"><div class="game-panel"><svg class="envelope" viewBox="0 0 160 120" aria-hidden="true"><path d="M10 28h140v82H10z"/><path d="m10 28 70 48 70-48M10 110l49-48m91 48-49-48"/><path d="M25 28 34 6l103 5 3 17" fill="var(--paper)"/></svg><span class="handwritten">No peeking. No explaining.</span><h1>Pass the screen.</h1><p>Player two, it’s your turn. You’ll only see the drawing. Describe what you see in <strong>${budget} words or fewer</strong>. You have 60 seconds.</p><button id="to-describe" class="primary blue">I’m the next player ${arrow}</button></div></section></div>`, 'pass');
  $('#to-describe').addEventListener('click', describe);
}
function describe() {
  mount(`<div class="game-shell">${progress(3)}<div class="round-header"><div><h1>What on earth is this?</h1><p>Player two: describe the drawing. Your words are all the search engines will get.</p></div><div class="timer" id="timer" aria-label="Description time remaining"></div></div><section class="game-panel describe-layout"><img class="drawing-preview" src="${drawing}" alt="Player one’s drawing. Describe what you see."><div class="description-box"><label for="description">Put it into words.<br>Very few words.</label><p>No help from the artist. Try describing the idea rather than guessing a character’s name.</p><textarea id="description" maxlength="600" placeholder="I think it’s…" autocomplete="off" spellcheck="true"></textarea><div class="word-meter" id="word-meter"><span id="word-help">You’ve got ${budget} words. Make them count.</span><strong id="word-count">0 / ${budget}</strong></div><div class="word-track" id="word-track"><span></span></div><button class="primary blue" id="reveal" disabled>Let the machines guess ${arrow}</button><p id="description-status" class="small muted" role="status"></p></div></section></div>`, 'describe');
  $('#description').addEventListener('input', updateWords);
  $('#reveal').addEventListener('click', () => { description = $('#description').value.trim(); if (words(description).length && words(description).length <= budget) reveal(); });
  $('#description').focus({ preventScroll: true });
  startTimer(60, () => {
    descriptionTimedOut = true;
    const count = words($('#description').value).length;
    if (count > 0 && count <= budget) { description = $('#description').value.trim(); reveal(); }
    else { $('#description-status').textContent = count > budget ? 'Time’s up. Trim your description to the word budget, then reveal.' : 'Time’s up. Add a few words, then reveal.'; }
  });
}
function updateWords() {
  const count = words($('#description').value).length;
  $('#word-count').textContent = `${count} / ${budget}`;
  $('#word-meter').classList.toggle('over', count > budget);
  $('#word-track').classList.toggle('over', count > budget);
  $('#word-track span').style.width = `${Math.min(100, count / budget * 100)}%`;
  $('#word-help').textContent = count > budget ? `${count - budget} too many. What can you leave out?` : count === budget ? 'Every word is doing a job.' : `${budget - count} words left.`;
  $('#reveal').disabled = !count || count > budget;
  if (descriptionTimedOut && count > 0 && count <= budget) $('#description-status').textContent = 'Ready to reveal.';
}

async function demo() {
  if (!corpus) return;
  promptIndex = 1; budget = 10; description = 'someone having a very bad hair day';
  // This drawing is an explicitly authored example; rankings are computed live.
  const image = new Image();
  const blob = new Blob([doodle.replace('role="img"', 'xmlns="http://www.w3.org/2000/svg"').replace('stroke="#e8a515"', 'stroke="#e8a515"').replace('<svg ', '<svg fill="none" stroke="#3444df" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" ')], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  try {
    await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = reject; image.src = url; });
    const c = document.createElement('canvas'); c.width = 800; c.height = 600;
    const context = c.getContext('2d'); context.fillStyle = 'white'; context.fillRect(0, 0, 800, 600); context.drawImage(image, 0, 20, 800, 560); drawing = c.toDataURL();
  } finally { URL.revokeObjectURL(url); }
  engine.warmup(); reveal(true);
}

async function reveal(isDemo = false) {
  querySource = 'description'; unit = '60';
  const generation = roundGeneration;
  mount(`<div class="game-shell">${progress(4)}<section class="game-panel loading-panel"><span class="handwritten">Let’s open the whole chain.</span><h1>Can the machines<br>find their way back?</h1><div class="loading-line" aria-hidden="true"><span></span></div><p role="status">Searching 303 articles. The first reveal also opens the local semantic model; this can take a few seconds.</p><p class="fineprint">Your description is processed in this browser.</p></section></div>`, 'loading');
  try {
    const result = await engine.search(description, unit);
    if (generation !== roundGeneration) return;
    lastResult = result; activeQuery = description;
    renderReveal(isDemo);
  } catch (error) {
    if (generation !== roundGeneration) return;
    $('.loading-panel').innerHTML = `<h1>That message got stuck.</h1><p>${escape(error.message)}</p><button id="retry" class="primary blue">Try again ${arrow}</button>`;
    $('#retry').addEventListener('click', () => reveal(isDemo));
  }
}
function renderReveal(isDemo = false) {
  const source = prompt(), doc = corpus.documents[source.doc];
  mount(`<div class="reveal-shell">${progress(4)}<div class="reveal-heading"><span class="handwritten">${isDemo ? 'A worked example · real search results' : 'Everybody can look now.'}</span><h1>Well, that took a turn.</h1><p>The original was <strong>${escape(doc.title)}</strong>. Here’s what made it through.</p></div><section class="chain" aria-label="The complete message chain"><article class="chain-item"><div class="paper-label"><span class="round">1</span>The passage</div><p>${escape(source.prompt)}</p><details><summary>See the unedited source</summary><p>${escape(source.original)}</p></details><a href="${escape(doc.url)}" target="_blank" rel="noopener">${escape(doc.title)} · Wikipedia ↗</a></article><article class="chain-item"><div class="paper-label"><span class="round">2</span>${isDemo ? 'The example drawing' : 'The drawing'}</div><img src="${drawing}" alt="${isDemo ? 'Authored example drawing of a person beneath a raincloud' : 'Player one’s drawing'}"></article><article class="chain-item"><div class="paper-label"><span class="round">3</span>${isDemo ? 'The example description' : 'The description'}</div><p class="description-quote">“${escape(description)}”</p><p class="small" style="margin-top:15px">${words(description).length} of ${budget} words used</p></article></section><section class="retrieval-panel" aria-labelledby="search-heading"><div class="retrieval-header"><div><h2 id="search-heading">Two ways to find it.</h2><p class="small muted" style="margin-top:7px">Click a result. Read what the machine retrieved.</p></div><div class="query-switch" aria-label="Text to search"><button data-query="description" aria-pressed="true">The description</button><button data-query="original" aria-pressed="false">Original passage</button></div></div><div class="rank-columns"><section class="keyword" aria-label="Keyword retrieval"><div class="rank-heading"><h3>Remembers words.</h3><span class="method-tag">TF-IDF</span></div><div id="keyword-results"></div></section><section class="semantic" aria-label="Semantic retrieval"><div class="rank-heading"><h3>Looks for context.</h3><label class="sr-only" for="unit">Semantic retrieval unit</label><select id="unit"><option value="60">60-word passages</option><option value="180">180-word passages</option><option value="page">Whole-page averages</option></select></div><div id="semantic-results"></div></section></div><p class="retrieval-note">The numbers are cosine similarities, not confidence or “meaning retained.” Compare ranks within a method. Passage search scores each article by its best matching passage. Both systems can return irrelevant results.</p><p id="search-status" class="small muted" role="status" style="margin-top:12px"></p></section><aside class="insight" aria-live="polite"><span class="handwritten">What got lost?</span><div id="insight"></div></aside><div class="reveal-actions"><button id="again" class="primary">Another round ${arrow}</button><div class="toolrow"><button id="save" class="secondary">Save the chain</button><button id="methods" class="secondary">What’s being measured?</button></div></div></div>`, 'reveal');
  document.querySelectorAll('[data-query]').forEach(button => button.addEventListener('click', () => {
    querySource = button.dataset.query;
    document.querySelectorAll('[data-query]').forEach(b => b.setAttribute('aria-pressed', b === button));
    updateSearch();
  }));
  $('#unit').addEventListener('change', event => { unit = event.target.value; updateSearch(); });
  $('#again').addEventListener('click', home);
  $('#methods').addEventListener('click', () => $('#about').showModal());
  $('#save').addEventListener('click', downloadChain);
  app.addEventListener('click', handleEvidence);
  paintRankings();
}

async function updateSearch() {
  const sequence = ++revealSequence;
  busy = true;
  activeQuery = querySource === 'original' ? prompt().prompt : description;
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
  const target = prompt().doc;
  const column = (list, method) => {
    if (!list) return `<p class="empty-message">Semantic search couldn’t open in this browser. Keyword results are still real.</p><button class="secondary" id="retry-semantic">Retry semantic model</button>`;
    const rank = list.findIndex(item => item.doc === target) + 1;
    const noMatch = method === 'keyword' && list[0].score <= 0;
    if (noMatch) return '<p class="empty-message">No indexed words in common. TF-IDF cannot distinguish the articles for this query; an arbitrary tied ranking would be misleading.</p>';
    const topScore = list[0].score;
    const rankText = method === 'keyword' && list[rank - 1].score === 0 ? 'unmatched' : `#${rank}`;
    return `<div class="target-rank"><span class="rank-number">${rankText === 'unmatched' ? '—' : rankText}</span><p><strong>${escape(corpus.documents[target].title)}</strong>${rankText === 'unmatched' ? 'No shared indexed words with the original' : `Original article’s rank out of ${corpus.documents.length}`}</p></div><ol class="rank-list">${list.slice(0, 5).map((item, i) => `<li class="rank-result${item.doc === target ? ' target' : ''}"><button data-evidence="${method}" data-doc="${item.doc}" aria-expanded="false"><span class="place">${i + 1}</span><span class="result-name">${escape(corpus.documents[item.doc].title)}</span><span class="score">${item.score.toFixed(3)}</span><span class="score-line" aria-hidden="true"><i style="width:${topScore > 0 ? Math.max(0, item.score / topScore * 100) : 0}%"></i></span></button></li>`).join('')}</ol>`;
  };
  $('#keyword-results').innerHTML = column(lastResult.keyword, 'keyword');
  $('#semantic-results').innerHTML = column(lastResult.semantic, 'semantic');
  if ($('#retry-semantic')) $('#retry-semantic').addEventListener('click', updateSearch);
  $('#search-status').textContent = `Searching ${querySource === 'original' ? 'the original drawing prompt' : 'the final description'}: “${activeQuery}”`;
  const kr = lastResult.keyword.findIndex(item => item.doc === target) + 1;
  const dr = lastResult.semantic?.findIndex(item => item.doc === target) + 1;
  const hasLexical = lastResult.keyword.find(item => item.doc === target).score > 0;
  let title, text;
  if (querySource === 'original') {
    title = 'Same source. A different representation.';
    text = 'The original prompt removes the drawing and description handoffs from this comparison. Now change only the semantic retrieval unit: the query stays fixed while the representation of each article changes.';
  } else if (!lastResult.semantic) {
    title = 'One instrument is unavailable.';
    text = 'Keyword retrieval is shown. The semantic model failed to load; retry it to compare methods. No simulated semantic results are substituted.';
  } else if (hasLexical && kr <= 5 && dr <= 5) {
    title = 'The message made it through.';
    text = `Both methods found the source in their top five: keyword rank ${kr}, semantic rank ${dr}. That shows recovery in this round, not perfect preservation of the passage’s meaning. Open the evidence and see which details survived.`;
  } else {
    title = 'A few words can send you somewhere else.';
    text = `The original ${hasLexical ? `ranks ${kr} in keyword search` : 'has no indexed words in common with your description'} and ranks ${dr} in semantic search. Look at what replaced it. Then switch to the original passage to separate the human handoffs from retrieval behavior.`;
  }
  $('#insight').innerHTML = `<h3>${title}</h3><p>${text}</p>`;
}
function highlight(text, terms) {
  const set = new Set(terms);
  return text.split(/(\b[a-zA-Z0-9_]{2,}\b)/g).map(token => set.has(token.toLowerCase()) ? `<mark>${escape(token)}</mark>` : escape(token)).join('');
}
function handleEvidence(event) {
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
  const evidence = document.createElement('div'); evidence.className = 'evidence';
  evidence.innerHTML = `<div class="evidence-label">${label}</div>${contributions}<p>${text}</p><a href="${escape(article.url)}" target="_blank" rel="noopener">Read the source article ↗</a>`;
  button.after(evidence); button.setAttribute('aria-expanded', true);
}
function downloadChain() {
  const source = prompt();
  const payload = { title: 'Pass it on', source: corpus.documents[source.doc].title,
    sourceUrl: corpus.documents[source.doc].url, sourceLicense: 'CC BY-SA 4.0', sourceSnapshot: corpus.source,
    original: source.original, drawingPrompt: source.prompt, description, wordBudget: budget, drawing,
    retrievalUnit: unit, querySource, query: activeQuery,
    keyword: lastResult.keyword.slice(0, 5).map(item => ({ title: corpus.documents[item.doc].title, cosine: item.score })),
    semantic: lastResult.semantic?.slice(0, 5).map(item => ({ title: corpus.documents[item.doc].title, cosine: item.score })) || null,
    model: corpus.model, note: 'Cosine similarities are not confidence or percentages of meaning retained.' };
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = 'pass-it-on-chain.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
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
