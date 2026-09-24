// Which School? — Week 4 explorable. Data comes from prepare_data.py (school-data.json).
import { laneOffset, modularity, nmi, verdict, xFraction } from './school.mjs';

const $ = (id) => document.getElementById(id);
const d = await (await fetch('school-data.json')).json();
const P = d.philosophers;
const L = d.lanes;
const RUNS = d.runs.length;
const REF = d.meta.referenceRun;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ------------------------------------------------------------------ derived per-node facts
const neighbours = P.map(() => []);
for (const [a, b, w] of d.edges) { neighbours[a].push([b, w]); neighbours[b].push([a, w]); }
neighbours.forEach((list) => list.sort((x, y) => y[1] - x[1]));

P.forEach((p, i) => {
  const order = p.votes.map((v, lane) => [v, lane]).sort((a, b) => b[0] - a[0] || (a[1] === p.runs[REF] ? -1 : 1));
  p.home = order[0][1];
  p.loyalty = order[0][0] / RUNS;
  p.rival = order[1][0] > 0 ? order[1][1] : p.home;
  p.j = Math.sin(i * 12.9898 + 78.233) * 43758.5453 % 1; // stable jitter in (-1, 1)
  p.jx = Math.sin(i * 39.3468 + 11.135) * 24634.6345 % 1;
  p.r = 1.6 + Math.sqrt(p.degree) * 0.45;
  p.idx = i;
});
const byDegree = [...P].sort((a, b) => b.degree - a.degree);
const homeOf = P.map((p) => p.home);
const leaveRate = L.map((_, lane) => {
  const members = P.filter((p) => p.home === lane);
  const left = members.reduce((s, p) => s + p.runs.filter((r) => r !== lane).length, 0);
  return members.length ? left / (members.length * RUNS) : 0;
});
const consensusQ = modularity(d.edges, homeOf);
const consensusNmi = nmi(homeOf, P.map((p) => p.runs[REF]));
const eraNmi = nmi(homeOf, P.map((p) => p.era));

// ------------------------------------------------------------------ state
const state = { run: null, sel: -1, hover: -1, touched: new Set() };
let names = [];
try { names = JSON.parse(localStorage.getItem('which-school-names') || '[]'); } catch { /* private mode */ }
const laneName = (i) => names[i]?.trim() || (L[i].splinter ? 'Splinter groups' : `${L[i].top[0]}’s school`);

let colors = [];
const readColors = () => {
  const cs = getComputedStyle(document.documentElement);
  colors = L.map((lane, i) => cs.getPropertyValue(lane.splinter ? '--s9' : `--s${i + 1}`).trim());
  colors.ink = cs.getPropertyValue('--ink').trim();
  colors.muted = cs.getPropertyValue('--muted').trim();
  colors.surface = cs.getPropertyValue('--surface').trim();
  colors.alt = cs.getPropertyValue('--lane-alt').trim();
  colors.grid = cs.getPropertyValue('--grid').trim();
};
readColors();

// ------------------------------------------------------------------ geometry
const canvas = $('canvas');
const ctx = canvas.getContext('2d');
const geo = { W: 0, H: 0, gutter: 200, top: 28, lanes: [] };
const TICKS = [-800, -400, 0, 500, 1000, 1300, 1500, 1600, 1700, 1800, 1900];

function layout() {
  const W = $('stage').clientWidth;
  geo.W = W;
  geo.gutter = W < 600 ? 104 : 200;
  $('stage').style.setProperty('--gutter', `${geo.gutter}px`);
  const target = Math.max(430, Math.min(660, W * 0.56));
  const raw = L.map((l) => 8 + Math.sqrt(l.size));
  const sum = raw.reduce((a, b) => a + b, 0);
  let y = geo.top;
  geo.lanes = raw.map((r) => {
    const h = Math.max(42, (r / sum) * target);
    const lane = { top: y, h, mid: y + h / 2, half: h / 2 - 4 };
    y += h;
    return lane;
  });
  geo.H = y + 4;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = W * dpr;
  canvas.height = geo.H * dpr;
  canvas.style.height = `${geo.H}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  renderGutter();
}
const xOf = (year) => geo.gutter + 14 + xFraction(year) * (geo.W - geo.gutter - 28);

function target(p) {
  const lane = state.run === null ? p.home : p.runs[state.run];
  const g = geo.lanes[lane];
  return { x: xOf(p.year) + p.jx * 2.5, y: g.mid + laneOffset(p, lane) * g.half, lane };
}

// ------------------------------------------------------------------ animation
const pos = P.map(() => null);
let anim = null;
function moveTo(instant = false) {
  const now = performance.now();
  P.forEach((p, i) => {
    const t = target(p);
    const from = pos[i] ? { x: pos[i].x, y: pos[i].y } : t;
    pos[i] = { ...from, from, to: t, delay: instant ? 0 : ((t.x - geo.gutter) / geo.W) * 280 };
  });
  anim = instant || reduced ? null : { start: now, dur: 700 };
  if (!anim) pos.forEach((q) => { q.x = q.to.x; q.y = q.to.y; });
  requestAnimationFrame(frame);
}
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);
function frame(now) {
  let busy = false;
  if (anim) {
    for (const q of pos) {
      const t = Math.min(1, Math.max(0, (now - anim.start - q.delay) / anim.dur));
      if (t < 1) busy = true;
      const e = ease(t);
      q.x = q.from.x + (q.to.x - q.from.x) * e;
      q.y = q.from.y + (q.to.y - q.from.y) * e;
    }
    if (!busy) anim = null;
  }
  draw();
  if (busy) requestAnimationFrame(frame);
}

// ------------------------------------------------------------------ drawing
function draw() {
  const { W, H } = geo;
  ctx.clearRect(0, 0, W, H);
  geo.lanes.forEach((g, i) => {
    ctx.fillStyle = i % 2 ? colors.alt : colors.surface;
    ctx.fillRect(0, g.top, W, g.h);
    ctx.fillStyle = colors[i];
    ctx.fillRect(0, g.top + 3, 3, g.h - 6);
  });
  ctx.font = '11px "DM Sans", system-ui';
  ctx.textAlign = 'center';
  let lastLabel = -Infinity;
  for (const y of TICKS) {
    const x = xOf(y);
    ctx.fillStyle = colors.grid;
    ctx.fillRect(x, geo.top, 1, H - geo.top);
    if (x - lastLabel < 44) continue; // narrow screens: skip labels that would collide
    lastLabel = x;
    ctx.fillStyle = colors.muted;
    ctx.fillText(y < 0 ? `${-y} BC` : y === 0 ? '1 AD' : `${y}`, x, 17);
  }

  const sel = state.sel;
  const focus = new Set(sel >= 0 ? [sel, ...neighbours[sel].map(([n]) => n)] : []);
  if (sel >= 0) {
    const a = pos[sel];
    for (const [n, w] of neighbours[sel]) {
      const b = pos[n];
      ctx.strokeStyle = colors.ink;
      ctx.globalAlpha = 0.14 + Math.min(0.5, w / 30);
      ctx.lineWidth = Math.min(3, 0.6 + w / 6);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.quadraticCurveTo((a.x + b.x) / 2, Math.min(a.y, b.y) - Math.abs(a.x - b.x) * 0.18 - 10, b.x, b.y);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  for (const p of byDegree) { // big dots first, so small ones stay visible on top
    const q = pos[p.idx];
    const moved = state.run !== null && q.to.lane !== p.home;
    let alpha = state.run === null ? 0.85 : moved ? 1 : 0.32;
    if (sel >= 0 && !focus.has(p.idx)) alpha *= 0.35;
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(q.x, q.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = colors[p.home];
    ctx.fill();
    ctx.lineWidth = moved ? 1.6 : 1;
    ctx.strokeStyle = moved ? colors.ink : colors.surface;
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // Direct labels: the two best-connected members of each school, plus selection and hover.
  const labelled = new Set();
  if (sel < 0 && state.run === null) {
    L.forEach((l, lane) => { if (!l.splinter) P.filter((p) => p.home === lane).sort((a, b) => b.degree - a.degree).slice(0, 2).forEach((p) => labelled.add(p.idx)); });
  }
  if (sel >= 0) labelled.add(sel);
  if (state.hover >= 0) labelled.add(state.hover);
  ctx.textAlign = 'left';
  const placed = [];
  // Selection and hover are drawn last and always; ambient labels are skipped if they would collide.
  const order = [...labelled].sort((a, b) => (a === sel || a === state.hover) - (b === sel || b === state.hover));
  for (const i of order) {
    const q = pos[i];
    const bold = i === sel || i === state.hover;
    ctx.font = `${bold ? 700 : 600} ${bold ? 13 : 11.5}px "DM Sans", system-ui`;
    const label = P[i].name;
    const w = ctx.measureText(label).width;
    const x = Math.min(q.x + P[i].r + 4, geo.W - w - 6);
    const box = [x - 2, q.y - 8, x + w + 2, q.y + 8];
    if (!bold && placed.some((o) => box[0] < o[2] && o[0] < box[2] && box[1] < o[3] && o[1] < box[3])) continue;
    placed.push(box);
    ctx.lineWidth = 3.5;
    ctx.strokeStyle = colors.surface;
    ctx.strokeText(label, x, q.y + 4);
    ctx.fillStyle = colors.ink;
    ctx.fillText(label, x, q.y + 4);
  }
  if (sel >= 0) {
    const q = pos[sel];
    ctx.lineWidth = 2;
    ctx.strokeStyle = colors.ink;
    ctx.beginPath();
    ctx.arc(q.x, q.y, P[sel].r + 3.5, 0, Math.PI * 2);
    ctx.stroke();
  }
}

// ------------------------------------------------------------------ gutter (lane names)
function renderGutter() {
  const gutter = $('gutter');
  if (!gutter.children.length) {
    L.forEach((l, i) => {
      const box = document.createElement('div');
      box.className = 'lane-label';
      box.innerHTML = `<input aria-label="Name for school ${i + 1}" maxlength="32" /><small></small>`;
      const input = box.querySelector('input');
      input.value = names[i] || '';
      input.placeholder = laneName(i);
      input.title = 'Click to name this school';
      input.classList.toggle('named', !!input.value);
      input.addEventListener('input', () => {
        names[i] = input.value;
        input.classList.toggle('named', !!input.value.trim());
        try { localStorage.setItem('which-school-names', JSON.stringify(names)); } catch { /* ignore */ }
        progress(1);
        renderTribunal(); renderTable(); renderLessons(); renderChips();
      });
      gutter.append(box);
    });
  }
  [...gutter.children].forEach((box, i) => {
    const g = geo.lanes[i];
    box.style.top = `${g.top}px`;
    box.style.height = `${g.h}px`;
    const pct = Math.round(leaveRate[i] * 100);
    box.querySelector('small').innerHTML = `<span class="swatch" style="background:${colors[i]}"></span>${L[i].size} · ~${pct}% leave per run`;
  });
}

// ------------------------------------------------------------------ interaction on canvas
function hit(ev) {
  const r = canvas.getBoundingClientRect();
  const x = ev.clientX - r.left, y = ev.clientY - r.top;
  let best = -1, bestD = Infinity;
  P.forEach((p, i) => {
    const q = pos[i];
    const dd = Math.hypot(q.x - x, q.y - y);
    if (dd < Math.max(7, p.r + 3) && dd < bestD) { best = i; bestD = dd; }
  });
  return { best, x, y };
}
canvas.addEventListener('pointermove', (ev) => {
  const { best, x, y } = hit(ev);
  if (best !== state.hover) { state.hover = best; draw(); }
  const tip = $('tooltip');
  if (best < 0) { tip.hidden = true; return; }
  const p = P[best];
  const lane = pos[best].to.lane;
  tip.innerHTML = `<b>${p.name}</b>${yearText(p)} · ${laneName(lane)}<br>Usual school in ${Math.round(p.loyalty * RUNS)}/50 runs`;
  tip.hidden = false;
  tip.style.left = `${Math.min(x + 14, geo.W - 250)}px`;
  tip.style.top = `${y + 14}px`;
});
canvas.addEventListener('pointerleave', () => { state.hover = -1; $('tooltip').hidden = true; draw(); });
canvas.addEventListener('click', (ev) => {
  const { best } = hit(ev);
  select(best);
});

function select(i, scroll = false) {
  state.sel = i;
  if (i >= 0) progress(3);
  renderTribunal();
  draw();
  if (scroll && i >= 0 && innerWidth < 980) $('tribunal').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
}

// ------------------------------------------------------------------ run controls
let playing = null;
function setRun(run) {
  state.run = run;
  if (run !== null) progress(2);
  $('consensus').setAttribute('aria-pressed', String(run === null));
  $('run-label').textContent = run === null ? 'Majority of 50 runs' : `Run ${run + 1} of 50 · seed ${d.meta.seeds[run]}`;
  moveTo();
  renderReadouts();
  renderTribunal();
}
$('consensus').onclick = () => { stop(); setRun(null); };
$('prev').onclick = () => { stop(); setRun(state.run === null ? RUNS - 1 : (state.run + RUNS - 1) % RUNS); };
$('next').onclick = () => { stop(); setRun(state.run === null ? 0 : (state.run + 1) % RUNS); };
$('reroll').onclick = () => {
  stop();
  let r;
  do r = Math.floor(Math.random() * RUNS); while (r === state.run);
  setRun(r);
};
function stop() {
  clearInterval(playing); playing = null;
  $('play').setAttribute('aria-pressed', 'false');
  $('play').textContent = '▶ Play all 50';
}
$('play').onclick = () => {
  if (playing) return stop();
  $('play').setAttribute('aria-pressed', 'true');
  $('play').textContent = '❚❚ Pause';
  const step = () => { if (state.run === RUNS - 1) return stop(); setRun(state.run === null ? 0 : state.run + 1); };
  step();
  playing = setInterval(step, 1300);
};
addEventListener('keydown', (ev) => {
  if (ev.target.matches('input, textarea')) return;
  if (ev.key === 'ArrowRight') $('next').click();
  else if (ev.key === 'ArrowLeft') $('prev').click();
  else if (ev.key === 'r') $('reroll').click();
  else if (ev.key === 'Escape') select(-1);
});

function renderReadouts() {
  const run = state.run;
  const moved = run === null ? P.filter((p) => p.loyalty < 1).length : P.filter((p) => p.runs[run] !== p.home).length;
  $('k-val').textContent = run === null ? new Set(homeOf).size : d.runs[run].k;
  $('moved-val').textContent = moved.toLocaleString();
  $('moved-val').nextElementSibling.textContent = run === null ? 'philosophers who switch school at least once' : 'philosophers not in their usual school';
  $('nmi-val').textContent = (run === null ? consensusNmi : d.runs[run].nmi).toFixed(2);
  renderGauge();
}

// ------------------------------------------------------------------ Q gauge
function renderGauge() {
  const svg = $('q-svg');
  const W = svg.clientWidth || 800;
  const x = (q) => 8 + (q / 0.7) * (W - 16);
  const nq = d.nullQ;
  const q = state.run === null ? consensusQ : d.runs[state.run].q;
  const ticks = d.runs.map((r) => `<line x1="${x(r.q)}" x2="${x(r.q)}" y1="26" y2="40" stroke="var(--faint)" stroke-width="1" opacity=".6"/>`).join('');
  svg.innerHTML = `
    <rect x="${x(0.3)}" y="30" width="${x(0.7) - x(0.3)}" height="6" rx="3" fill="var(--grid)"/>
    <text x="${x(0.3)}" y="60">typical real networks: 0.3–0.7</text>
    <line x1="${x(0)}" x2="${x(0.7)}" y1="33" y2="33" stroke="var(--line)" stroke-width="1"/>
    <rect x="${x(nq.mean - 3 * nq.sd)}" y="22" width="${Math.max(3, x(nq.mean + 3 * nq.sd) - x(nq.mean - 3 * nq.sd))}" height="22" rx="1.5" fill="var(--muted)" opacity=".7"/>
    <text x="${x(nq.mean)}" y="14" text-anchor="middle">shuffled null ${nq.mean.toFixed(3)}</text>
    ${ticks}
    <g class="q-now"><line x1="${x(q)}" x2="${x(q)}" y1="18" y2="48" stroke="var(--accent)" stroke-width="2.5"/>
    <text x="${x(q)}" y="14" text-anchor="middle">Q = ${q.toFixed(3)}</text></g>
    <text x="${x(0)}" y="60">0</text>`;
  $('q-caption').textContent = `Modularity of ${state.run === null ? 'the consensus partition' : `run ${state.run + 1}`}. The grey ticks are all 50 runs. The dark bar is ${nq.values.length} degree-preserving shuffles of the same network, which still score Q ≈ ${nq.mean.toFixed(2)}.`;
}

// ------------------------------------------------------------------ tribunal
const yearText = (p) => (p.yearKnown ? ` · b. ${p.year < 0 ? `${-p.year} BC` : p.year}` : '');
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function renderTribunal() {
  const box = $('tribunal');
  const i = state.sel;
  if (i < 0) {
    const pick = ['Aristotle', 'Galileo Galilei', 'Baruch Spinoza', 'Immanuel Kant'].map((n) => P.findIndex((p) => p.name === n)).filter((i) => i >= 0);
    box.innerHTML = `<p class="eyebrow">Inspect a philosopher</p><h3>Who belongs where?</h3><p class="meta">Click a dot to see its 50 assignments and strongest links. Or start with one of these:</p><div class="chips">${pick.map((i) => personChip(i)).join('')}</div>`;
    wireChips(box);
    return;
  }
  const p = P[i];
  const v = verdict(p.loyalty);
  const rows = p.votes.map((n, lane) => [n, lane]).filter(([n]) => n).sort((a, b) => b[0] - a[0]);
  box.innerHTML = `
    <p class="eyebrow"><span class="swatch" style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${colors[p.home]};margin-right:6px"></span>${esc(laneName(p.home))}</p>
    <h3>${esc(p.name)}</h3>
    <p class="meta">${p.era}${yearText(p)} · ${p.degree} links</p>
    ${p.subfields.length ? `<div class="tags">${p.subfields.map((s) => `<span class="tag">${s}</span>`).join('')}</div>` : ''}
    <p class="desc">${esc(p.desc)}</p>
    <a class="wiki" href="${p.url}" target="_blank" rel="noopener">Read on Wikipedia ↗</a>
    <div class="verdict">
      <p class="verdict-title">${v}</p>
      <p class="verdict-sub">${rows.length === 1 ? `All 50 runs put ${esc(p.name)} in the same school.` : `${rows[0][0]} of 50 runs put ${esc(p.name)} in ${esc(laneName(rows[0][1]))}. The rest disagree.`} Each square is one run. Click one to jump to it.</p>
      <div class="ballots">${p.runs.map((lane, k) => `<button class="ballot${k === state.run ? ' now' : ''}" data-run="${k}" style="background:${colors[lane]}" aria-label="Run ${k + 1}: ${esc(laneName(lane))}" title="Run ${k + 1}: ${esc(laneName(lane))}"></button>`).join('')}</div>
      <ul class="vote-rows">${rows.map(([n, lane]) => `<li><i class="dot" style="background:${colors[lane]}"></i><span>${esc(laneName(lane))}</span><span class="n">${n}</span></li>`).join('')}</ul>
    </div>
    <div class="ties"><p class="eyebrow">Strongest links (weight)</p><div class="chips">${neighbours[i].slice(0, 8).map(([n, w]) => personChip(n, w)).join('')}</div></div>`;
  box.querySelectorAll('.ballot').forEach((b) => b.addEventListener('click', () => { stop(); setRun(+b.dataset.run); }));
  wireChips(box);
}
const personChip = (i, extra) => `<button class="person" data-i="${i}" title="${esc(laneName(P[i].home))}"><i style="background:${colors[P[i].home]}"></i>${esc(P[i].name)}${extra !== undefined ? ` <em>${extra}</em>` : ''}</button>`;
const wireChips = (root) => root.querySelectorAll('.person').forEach((b) => b.addEventListener('click', () => select(+b.dataset.i, true)));

// ------------------------------------------------------------------ search + chips
$('names').innerHTML = byDegree.map((p) => `<option value="${esc(p.name)}"></option>`).join('');
$('search').addEventListener('change', (ev) => {
  const i = P.findIndex((p) => p.name.toLowerCase() === ev.target.value.trim().toLowerCase());
  if (i >= 0) { select(i, true); ev.target.value = ''; }
});
function renderChips() {
  const contested = P.filter((p) => p.degree >= 25).sort((a, b) => a.loyalty - b.loyalty || b.degree - a.degree).slice(0, 14);
  $('contested').innerHTML = contested.map((p) => personChip(p.idx, `${Math.round(p.loyalty * 100)}%`)).join('');
  const loyal = byDegree.filter((p) => p.loyalty === 1 && p.degree >= 60).slice(0, 14);
  $('loyal').innerHTML = loyal.map((p) => personChip(p.idx)).join('');
  wireChips($('contested')); wireChips($('loyal'));
}

// ------------------------------------------------------------------ lessons + table
function renderLessons() {
  const qs = d.runs.map((r) => r.q), ks = d.runs.map((r) => r.k), nm = d.runs.map((r) => r.nmi).filter((_, k) => k !== REF);
  const switchers = P.filter((p) => p.loyalty < 1).length;
  const ari = P.find((p) => p.name === 'Aristotle');
  const shakiest = L.map((_, i) => i).filter((i) => !L[i].splinter).sort((a, b) => leaveRate[b] - leaveRate[a])[0];
  const cards = [
    [`${Math.min(...qs).toFixed(2)}–${Math.max(...qs).toFixed(2)}`, 'Q only means something next to a null', `A shuffled network with the same degrees still scores Q ≈ ${d.nullQ.mean.toFixed(3)} ± ${d.nullQ.sd.toFixed(3)}. What matters is the gap to that null, not Q ≈ 0.5 on its own.`],
    [`${Math.min(...ks)}–${Math.max(...ks)}`, 'One run is not the answer', `Fifty seeds give between ${Math.min(...ks)} and ${Math.max(...ks)} communities, with NMI to the reference map from ${Math.min(...nm).toFixed(2)} to ${Math.max(...nm).toFixed(2)}. Louvain visits nodes in random order, and the modularity landscape is full of near-ties.`],
    [`${Math.round((switchers / P.length) * 100)}%`, 'Nodes can belong to more than one community', `${switchers.toLocaleString()} of ${P.length.toLocaleString()} philosophers switch school at least once. Aristotle's votes split ${ari.votes.filter((v) => v).sort((a, b) => b - a).join(' / ')}. That is the case for overlapping methods such as k-clique and link communities.`],
    [eraNmi.toFixed(2), 'The names are a story you tell afterwards', `NMI between the consensus schools and Wikipedia's century lists. Eras explain part of it, not all of it. The “${esc(laneName(shakiest))}” lane loses about ${Math.round(leaveRate[shakiest] * 100)}% of its members in a typical run. Check a name before you trust it.`],
  ];
  $('lesson-grid').innerHTML = cards.map(([big, h, p]) => `<article class="lesson"><p class="big">${big}</p><h3>${h}</h3><p>${p}</p></article>`).join('');
}
function renderTable() {
  $('school-table').innerHTML = `<thead><tr><th>School</th><th>Members</th><th>Best connected</th><th>Median birth</th><th>Never switch</th><th>Leave per run</th></tr></thead><tbody>${
    L.map((l, i) => {
      const members = P.filter((p) => p.home === i);
      const stay = members.filter((p) => p.loyalty === 1).length;
      return `<tr><td><strong>${esc(laneName(i))}</strong></td><td class="num">${members.length}</td><td>${l.top.map(esc).join(', ')}</td><td class="num">${l.medianYear < 0 ? `${-l.medianYear} BC` : l.medianYear}</td><td class="num">${Math.round((stay / members.length) * 100)}%</td><td class="num">${Math.round(leaveRate[i] * 100)}%</td></tr>`;
    }).join('')}</tbody>`;
}

// ------------------------------------------------------------------ progress chips
function progress(step) {
  if (state.touched.has(step)) return;
  state.touched.add(step);
  document.querySelectorAll('.steps li')[step - 1]?.classList.add('done');
}

// ------------------------------------------------------------------ boot
layout();
moveTo(true);
renderReadouts();
renderTribunal();
renderChips();
renderLessons();
renderTable();
new ResizeObserver(() => { layout(); moveTo(true); renderGauge(); }).observe($('stage'));
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { readColors(); renderGutter(); draw(); renderTribunal(); renderChips(); });
