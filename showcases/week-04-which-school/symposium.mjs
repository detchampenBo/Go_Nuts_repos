import { harmony, degreeAndStrength, disparity, loudest, alone, seat, planKey } from './symposium-model.mjs';
import { nmi } from './school.mjs';

const $ = id => document.getElementById(id);
const esc = v => String(v).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const PALETTE = ['#d86b78', '#a9bb5c', '#7fa0e0', '#e3a24f', '#bb8bd0', '#5fbcb2', '#a3a7ab'];
const GOLD = '#e3b664', FG = '#efe6d6', BRASS = '#c9a36a';
const MOOD_NOTE = 'In colour: most of their conversation partners share the table. Grey with “…”: nobody to talk to.';
const ALPHAS = [0.05, 0.1, 0.2, 0.3, 0.5];
const COURSE = { cover:'Welcome', guests:'Aperitif', plan:'First course', louvain:'Second course', null:'Intermezzo', volume:'Main course', backbone:'Cheese', cliques:'Dessert', hall:'Digestif' };
const f3 = x => x.toFixed(3);
const pct = x => `${Math.round(x * 100)}%`;
const list = names => names.length ? names.join(', ') : 'nobody';

async function start() {
  const res = await fetch('symposium-data.json');
  if (!res.ok) throw new Error('Could not load symposium-data.json');
  const d = await res.json();
  const G = d.guests, E = d.edges, n = G.length;
  const card = i => G[i].card;
  const { degree, strength } = degreeAndStrength(E, n);
  const neighbours = G.map(() => new Set());
  E.forEach(([a, b]) => { neighbours[a].add(b); neighbours[b].add(a); });
  const S = { course:'cover', plan:Array(n).fill(0), selected:null, evening:0, step:null, weighted:false, alpha:2, filter:'disparity', k:5, shuffle:null };
  const nullQ = d.null.map(r => r.q), realQ = d.unweighted.map(r => r.q);
  const mean = xs => xs.reduce((s, x) => s + x, 0) / xs.length;
  const nullMean = mean(nullQ), nullSd = Math.sqrt(nullQ.reduce((s, q) => s + (q - nullMean) ** 2, 0) / (nullQ.length - 1));
  const bestQ = Math.max(...realQ);

  // Colour tables in order of their earliest guest, so colours read as eras.
  const colours = part => { const key = planKey(part).split('.').map(Number); return part.map((_, i) => PALETTE[key[i] % PALETTE.length]); };
  const tablesOf = part => new Set(part).size;
  const together = (runs, a, b) => runs.filter(r => r.part[a] === r.part[b]).length;
  const PLATO = G.findIndex(g => g.card === 'Plato'), ARISTOTLE = G.findIndex(g => g.card === 'Aristotle');

  const photo = i => `portraits/guests/${G[i].card.toLowerCase()}.jpg`;

  // ---------------------------------------------------------------- the room
  const svg = $('room'), NS = 'http://www.w3.org/2000/svg';
  svg.insertAdjacentHTML('afterbegin', `<defs><clipPath id="face" clipPathUnits="objectBoundingBox"><circle cx=".5" cy=".5" r=".5"/></clipPath><radialGradient id="pool"><stop offset="0" stop-color="${GOLD}" stop-opacity=".24"/><stop offset=".55" stop-color="${GOLD}" stop-opacity=".08"/><stop offset="1" stop-color="${GOLD}" stop-opacity="0"/></radialGradient></defs>`);
  const nodes = G.map((g, i) => {
    const el = document.createElementNS(NS, 'g');
    el.setAttribute('class', 'guest arrive'); el.setAttribute('tabindex', '0'); el.setAttribute('role', 'button');
    el.style.animationDelay = `${200 + i * 60}ms`;
    el.addEventListener('animationend', () => el.classList.remove('arrive'), { once:true });
    el.innerHTML = `<g class="rings"></g><image href="${photo(i)}" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/><circle class="frame"/><text class="name"></text><g class="say" hidden><rect class="bubble-bg" width="22" height="14" rx="6"/><text class="bubble" x="11" y="10" text-anchor="middle">…</text></g>`;
    el.querySelector('.name').textContent = g.card;
    el.addEventListener('click', () => select(i));
    el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(i); } });
    $('guests').append(el);
    return el;
  });
  $('tables').addEventListener('click', e => {
    const t = e.target.closest('[data-table]');
    if (t && S.course === 'plan' && S.selected !== null) movePlan(S.selected, +t.dataset.table);
  });

  // The seating plan lives in a 640×520 world, scaled into the part of the screen the room owns:
  // all of it for the cover, the space left of the course cards otherwise.
  const phone = matchMedia('(max-width: 860px)');
  function region(W, H) {
    if (phone.matches) return S.course === 'cover' ? { x:0, y:50, w:W, h:H - 56 } : { x:0, y:56, w:W, h:H - 56 - 70 };
    return S.course === 'cover' ? { x:0, y:48, w:W, h:H - 110 } : { x:8, y:90, w:W - 490, h:H - 90 - 140 };
  }
  function frame() {
    const W = svg.clientWidth, H = svg.clientHeight;
    if (!W || !H) return;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const r = region(W, H), u = Math.min(r.w / 640, r.h / 520);
    $('world').style.transform = `translate(${(r.x + (r.w - 640 * u) / 2).toFixed(1)}px, ${(r.y + (r.h - 520 * u) / 2).toFixed(1)}px) scale(${u.toFixed(4)})`;
    // the cover title sits on the long table, so it is sized by that table
    $('story').style.setProperty('--table', `${Math.round(2 * (18 + 5.2 * n - 22) * u)}px`);
  }
  new ResizeObserver(frame).observe(svg);

  let scene, cur = null, anim = 0;
  const lerp = (a, b, t) => ({ ...b, x:a.x + (b.x - a.x) * t, y:a.y + (b.y - a.y) * t, cx:a.cx + (b.cx - a.cx) * t, cy:a.cy + (b.cy - a.cy) * t, r:a.r + (b.r - a.r) * t });
  function place(part) {
    const { pos, tables } = seat(part);
    const byId = new Map(tables.map(t => [t.id, t]));
    const target = pos.map(p => { const t = byId.get(p.table); return { ...p, cx:t.x, cy:t.y, r:t.r }; });
    cancelAnimationFrame(anim);
    if (!cur || reduced) { cur = target; draw(); return; }
    const from = cur, t0 = performance.now();
    const frame = now => {
      const t = Math.min(1, (now - t0) / 650), e = t < .5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
      cur = target.map((p, i) => lerp(from[i], p, e));
      draw();
      if (t < 1) anim = requestAnimationFrame(frame);
    };
    anim = requestAnimationFrame(frame);
  }

  function draw() {
    const seen = new Map();
    cur.forEach(p => { if (!seen.has(p.table)) seen.set(p.table, p); });
    $('tables').innerHTML = [...seen.entries()].map(([id, p]) => `<g data-table="${id}"><circle class="pool" cx="${p.cx.toFixed(1)}" cy="${p.cy.toFixed(1)}" r="${(p.r + 56).toFixed(1)}" fill="url(#pool)"/><circle class="table-top" cx="${p.cx.toFixed(1)}" cy="${p.cy.toFixed(1)}" r="${Math.max(7, p.r - 22).toFixed(1)}"/>${scene.letters ? `<text class="table-label" x="${p.cx.toFixed(1)}" y="${p.cy.toFixed(1)}">${'ABCD'[id]}</text>` : ''}</g>`).join('');
    const sel = S.selected;
    $('links').innerHTML = scene.edges.map(e => {
      const hot = sel !== null && (e.a === sel || e.b === sel);
      const cls = `link${hot ? ' hot' : sel !== null || e.faint ? ' faint' : ''}`;
      const style = `${e.color ? `stroke:${e.color};` : ''}${e.opacity && !hot && sel === null ? `stroke-opacity:${e.opacity};` : ''}`;
      return `<line class="${cls}" x1="${cur[e.a].x.toFixed(1)}" y1="${cur[e.a].y.toFixed(1)}" x2="${cur[e.b].x.toFixed(1)}" y2="${cur[e.b].y.toFixed(1)}" stroke-width="${(e.width || 1.2).toFixed(2)}"${e.dash ? ' stroke-dasharray="4 4"' : ''}${style ? ` style="${style}"` : ''}/>`;
    }).join('');
    nodes.forEach((el, i) => {
      const p = cur[i], c = Math.cos(p.angle), s = Math.sin(p.angle);
      el.setAttribute('transform', `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
      const t = el.querySelector('.name'), r = scene.size[i];
      t.setAttribute('x', (c * (r + 5)).toFixed(1));
      t.setAttribute('y', (s * (r + 5) + (Math.abs(c) < .15 ? (s > 0 ? 11 : -3) : 4.5)).toFixed(1));
      t.setAttribute('text-anchor', c > .15 ? 'start' : c < -.15 ? 'end' : 'middle');
      // the "…" bubble faces the table, away from the name
      el.querySelector('.say').setAttribute('transform', `translate(${(-c * (r + 9) - 11).toFixed(1)} ${(-s * (r + 9) - 7).toFixed(1)})`);
    });
  }

  // A guest's mood: the share of their conversation partners (volume, when weighted) at their table.
  function moods() {
    const total = Array(n).fill(0), here = Array(n).fill(0);
    for (const e of scene.edges) {
      if (e.faint) continue;
      const w = scene.weighted ? e.w : 1;
      total[e.a] += w; total[e.b] += w;
      if (scene.part[e.a] === scene.part[e.b]) { here[e.a] += w; here[e.b] += w; }
    }
    return total.map((t, i) => ({ share:t ? here[i] / t : 0, here:here[i], total:t, mood:!t || !here[i] ? 'bored' : here[i] / t >= .5 ? 'content' : 'neutral' }));
  }

  function paint() {
    const sel = S.selected, near = sel === null ? null : neighbours[sel];
    scene.moods = scene.mood === undefined ? moods() : null;
    nodes.forEach((el, i) => {
      const r = scene.size[i], img = el.querySelector('image'), frame = el.querySelector('.frame');
      img.setAttribute('x', (-r).toFixed(1)); img.setAttribute('y', (-r).toFixed(1));
      img.setAttribute('width', (2 * r).toFixed(1)); img.setAttribute('height', (2 * r).toFixed(1));
      frame.setAttribute('r', r.toFixed(1));
      frame.setAttribute('stroke', scene.fill[i]);
      const mood = scene.moods ? scene.moods[i].mood : scene.mood || 'neutral';
      el.classList.remove('content', 'neutral', 'bored');
      el.classList.add(mood);
      const say = el.querySelector('.say');
      say.toggleAttribute('hidden', mood !== 'bored'); // SVG elements ignore the .hidden property
      el.classList.toggle('selected', sel === i);
      el.classList.toggle('dim', scene.dim.has(i) || (near !== null && i !== sel && !near.has(i) && S.course !== 'plan'));
      el.querySelector('.rings').innerHTML = (scene.rings[i] || []).map((c, j) => `<circle class="ring" r="${(r + 3.5 + j * 3.6).toFixed(1)}" stroke="${c}"/>`).join('');
      el.setAttribute('aria-label', `${G[i].card}${mood === 'bored' ? ', nobody to talk to' : ''}`);
      el.setAttribute('aria-pressed', String(sel === i));
    });
  }

  // ---------------------------------------------------------------- scenes, one per course
  const plainEdges = (list = E) => list.map(([a, b, w]) => ({ a, b, w }));
  const face = k => 10 + .6 * k, faceByVolume = s => 8 + 1.6 * Math.sqrt(s);
  function build() {
    const ev = S.evening, base = { dim:new Set(), rings:[], letters:false, size:degree.map(face) };
    const tableEdges = (edges, part, fill) => edges.map(e => part[e.a] === part[e.b] ? { ...e, color:GOLD, opacity:.6 } : { ...e, dash:true, opacity:.14 });
    switch (S.course) {
      case 'cover': return { ...base, part:G.map(() => 0), fill:G.map(() => BRASS), mood:'content', edges:plainEdges().map(e => ({ ...e, faint:true })), title:'The Symposium', note:'' };
      case 'guests': return { ...base, part:G.map(() => 0), fill:G.map(() => BRASS), edges:plainEdges(), title:'One long table',
        note:'Every line is a conversation: one article links to the other. Portrait size = degree.' };
      case 'plan': {
        const fill = S.plan.map(t => PALETTE[t]);
        return { ...base, part:S.plan, fill, letters:true, edges:tableEdges(plainEdges(), S.plan, fill), title:`Your plan · harmony ${f3(harmony(E, S.plan).q)}`,
          note:`Gold threads stay at a table. Tap a guest, then a table. ${MOOD_NOTE}` };
      }
      case 'louvain': {
        const run = d.unweighted[ev], part = S.step === null ? run.part : replay(ev)[S.step];
        const fill = colours(run.part);
        return { ...base, part, fill, edges:tableEdges(plainEdges(), part, fill), title:`Evening ${ev + 1} · ${tablesOf(part)} table${tablesOf(part) > 1 ? 's' : ''}`,
          note:`Frame colour: where each guest ends up tonight. ${MOOD_NOTE}` };
      }
      case 'null': {
        if (S.shuffle === null) {
          const run = d.unweighted[ev], fill = colours(run.part);
          return { ...base, part:run.part, fill, edges:tableEdges(plainEdges(), run.part, fill), title:`The real party · harmony ${f3(run.q)}`, note:'Press shuffle to rewire the conversations.' };
        }
        const run = d.null[S.shuffle], fill = colours(run.part), deg = Array(n).fill(0);
        run.edges.forEach(([a, b]) => { deg[a]++; deg[b]++; });
        return { ...base, part:run.part, fill, size:deg.map(face), edges:tableEdges(run.edges.map(([a, b]) => ({ a, b, w:1 })), run.part, fill),
          title:`Shuffled party ${S.shuffle + 1} · harmony ${f3(run.q)}`, note:'Same degrees as the real party. Random partners.' };
      }
      case 'volume': {
        const run = (S.weighted ? d.weighted : d.unweighted)[ev], fill = colours(run.part);
        const edges = tableEdges(plainEdges(), run.part, fill).map(e => ({ ...e, width:S.weighted ? .6 + .75 * e.w : 1.2 }));
        return { ...base, part:run.part, fill, edges, size:S.weighted ? strength.map(faceByVolume) : base.size, weighted:S.weighted,
          title:S.weighted ? `By volume · ${tablesOf(run.part)} tables` : `By count · ${tablesOf(run.part)} tables`,
          note:S.weighted ? 'Thread width = volume. Portrait size = strength (total volume). Moods now weigh volume.' : 'Every conversation counts once. Portrait size = degree.' };
      }
      case 'backbone': {
        const run = d.weighted[ev], fill = colours(run.part), keep = currentKeep();
        return { ...base, part:run.part, fill, size:strength.map(faceByVolume), weighted:true,
          edges:plainEdges().map((e, i) => ({ ...e, width:.6 + .75 * e.w, faint:!keep[i], color:keep[i] ? fill[e.a] === fill[e.b] ? GOLD : FG : null, opacity:keep[i] ? .8 : null })),
          title:`${S.filter === 'disparity' ? 'Disparity filter' : 'Loudest links'} · ${keep.filter(Boolean).length} of ${E.length} kept`,
          note:'Seated by volume. Only kept conversations count toward a mood, so a guest with none left goes grey.' };
      }
      case 'cliques': {
        const run = d.weighted[ev], circles = d.cliques[S.k].communities, rings = G.map(() => []);
        circles.forEach((c, j) => c.forEach(i => rings[i].push(PALETTE[j])));
        const inside = (a, b) => circles.some(c => c.includes(a) && c.includes(b));
        return { ...base, part:run.part, fill:G.map(() => BRASS), mood:false, rings, dim:new Set(G.map((_, i) => i).filter(i => !rings[i].length)),
          edges:plainEdges().map(e => ({ ...e, faint:!inside(e.a, e.b) })), title:`k = ${S.k} · ${circles.length} circle${circles.length === 1 ? '' : 's'}`,
          note:'Seated by volume. Rings = circles of friends; a guest can wear several.' };
      }
      case 'hall': {
        const fill = colours(G.map(g => g.hall));
        return { ...base, part:G.map(g => g.hall), fill, edges:plainEdges().map(e => ({ ...e, faint:true })), title:'Seated with all 1,374 philosophers',
          note:'Each table is a school from the full network’s reference run.' };
      }
    }
  }

  const replays = new Map();
  function replay(ev) {
    if (!replays.has(ev)) {
      const steps = [G.map((_, i) => i)];
      for (const diff of d.unweighted[ev].trace) { const next = [...steps.at(-1)]; diff.forEach(([g, c]) => { next[g] = c; }); steps.push(next); }
      replays.set(ev, steps);
    }
    return replays.get(ev);
  }
  const currentKeep = () => S.filter === 'disparity' ? disparity(E, n, ALPHAS[S.alpha]) : loudest(E, disparity(E, n, ALPHAS[S.alpha]).filter(Boolean).length);

  function render(move = true) {
    scene = build();
    $('story').classList.toggle('is-cover', S.course === 'cover');
    frame();
    $('stage-course').textContent = COURSE[S.course];
    $('stage-title').textContent = scene.title;
    $('stage-note').textContent = scene.note;
    paint();
    if (move) place(scene.part); else draw();
    tray();
    panels();
  }

  // ---------------------------------------------------------------- the tray under the room
  function tray() {
    const i = S.selected;
    if (S.course === 'hall') {
      const lanes = [...new Set(G.map(g => g.hall))], fill = colours(G.map(g => g.hall));
      $('tray').innerHTML = lanes.map(l => { const h = d.hall[l], who = G.map((g, j) => j).filter(j => G[j].hall === l); return `<div><span style="color:${fill[who[0]]}">●</span> <span class="data">${h.size} in the hall, led by</span> ${esc(h.top.join(', '))}</div>`; }).join('');
      return;
    }
    if (i === null) { $('tray').innerHTML = S.course === 'plan' ? '<span class="data">Choose a guest to move them.</span>' : ''; return; }
    const g = G[i], talks = [...neighbours[i]].map(card).join(', ');
    const m = scene.moods && scene.moods[i];
    const feeling = m ? `<br><span class="data">${m.total ? `${m.mood === 'content' ? 'Happy' : m.mood === 'bored' ? 'Nobody to talk to' : 'Half listening'}: ${scene.weighted ? `${m.here} of ${m.total} volume` : `${m.here} of ${m.total} partners`} at this table` : 'No conversations here'}</span>` : '';
    if (S.course === 'plan') {
      $('tray').innerHTML = `Seat <span class="who">${esc(g.card)}</span> at <span class="seat-buttons">${[0, 1, 2, 3].map(t => `<button data-seat="${t}" aria-pressed="${S.plan[i] === t}" style="border-color:${PALETTE[t]};color:${S.plan[i] === t ? '#14100d' : PALETTE[t]}${S.plan[i] === t ? `;background:${PALETTE[t]}` : ''}">${'ABCD'[t]}</button>`).join('')}</span>${feeling}`;
      $('tray').querySelectorAll('[data-seat]').forEach(b => b.addEventListener('click', () => movePlan(i, +b.dataset.seat)));
      return;
    }
    const circles = d.cliques[S.k].communities.filter(c => c.includes(i)).length;
    const extra = S.course === 'cliques' ? ` · in ${circles} circle${circles === 1 ? '' : 's'}` : S.course === 'volume' || S.course === 'backbone' ? ` · volume ${strength[i]}` : '';
    $('tray').innerHTML = `<a class="who" href="${esc(g.url)}" target="_blank" rel="noopener">${esc(g.name)} ↗</a> <span class="data">${esc(g.year < 0 ? `${-g.year} BC` : g.year ?? g.era)} · ${degree[i]} conversations${extra}</span><br><span class="data">Talks with ${esc(talks)}</span>${feeling}`;
  }

  function select(i) {
    S.selected = S.selected === i ? null : i;
    paint(); draw(); tray();
  }

  function movePlan(i, t) {
    S.plan[i] = t;
    render();
  }

  // ---------------------------------------------------------------- the text column
  const rank = (values, fmt) => G.map((_, i) => i).sort((a, b) => values[b] - values[a] || a - b).slice(0, 5).map(i => `<li>${esc(card(i))} <span>${fmt(values[i])}</span></li>`).join('');
  $('sociable').innerHTML = rank(degree, k => `· ${k}`);
  $('rank-degree').innerHTML = rank(degree, k => `· ${k}`);
  $('rank-strength').innerHTML = rank(strength, s => `· ${s}`);

  const keys = d.unweighted.map(r => planKey(r.part));
  const freq = keys.reduce((m, k) => m.set(k, (m.get(k) || 0) + 1), new Map());
  const classes = [...freq.keys()].sort((a, b) => freq.get(b) - freq.get(a));
  $('evenings').innerHTML = keys.map((k, i) => `<button data-evening="${i}" class="${classes.indexOf(k) === 0 ? 'common' : ''}" aria-label="Evening ${i + 1}, plan ${'abcdefgh'[classes.indexOf(k)]}">${'abcdefgh'[classes.indexOf(k)]}</button>`).join('');

  function meter(svgEl, lo, hi, marks, band) {
    const x = v => 10 + (v - lo) / (hi - lo) * 380;
    let out = band ? `<rect class="band" x="${x(band[0])}" y="14" width="${x(band[1]) - x(band[0])}" height="16"/><text x="${(x(band[0]) + x(band[1])) / 2}" y="60" text-anchor="middle">random parties</text>` : '';
    out += `<line class="axis" x1="10" x2="390" y1="30" y2="30"/>`;
    for (let v = Math.ceil(lo * 10) / 10; v <= hi + 1e-9; v += .1) out += `<line class="axis" x1="${x(v)}" x2="${x(v)}" y1="30" y2="34"/><text x="${x(v)}" y="46" text-anchor="middle">${v.toFixed(1)}</text>`;
    out += marks.map(m => `<path d="M${x(m.v)} 30 l-5 -9 h10 z" fill="${m.color}"/><text x="${x(m.v) + (m.anchor === 'end' ? -7 : 7)}" y="22" text-anchor="${m.anchor}" style="fill:${m.color}">${esc(m.label)}</text>`).join('');
    svgEl.innerHTML = out;
  }

  function panels() {
    const h = harmony(E, S.plan);
    $('plan-q').textContent = f3(h.q);
    $('plan-together').textContent = pct(h.together);
    $('plan-expected').textContent = pct(h.expected);
    meter($('plan-meter'), -.1, .4, [{ v:h.q, label:'you', color:'#d86b78', anchor:h.q <= bestQ ? 'end' : 'start' }, { v:bestQ, label:'maître d’', color:'#efe6d6', anchor:h.q <= bestQ ? 'start' : 'end' }], [nullMean - 2 * nullSd, nullMean + 2 * nullSd]);

    const ev = S.evening, run = d.unweighted[ev], steps = replay(ev);
    const part = S.step === null ? run.part : steps[S.step];
    const moving = S.step !== null && S.step > 0 && run.trace[S.step - 1].length > 1;
    $('louvain-status').innerHTML = S.step !== null && S.step < steps.length - 1
      ? `Move ${S.step} of ${steps.length - 1}: ${S.step === 0 ? 'every guest at a table for one' : moving ? 'a whole table moves' : `${esc(card(run.trace[S.step - 1][0][0]))} changes table`}<br>${tablesOf(part)} tables · harmony ${f3(harmony(E, part).q)}`
      : `Evening ${ev + 1}: ${tablesOf(run.part)} tables · harmony ${f3(run.q)} · plan ${'abcdefgh'[classes.indexOf(keys[ev])]}, seen on ${freq.get(keys[ev])} of 50 evenings<br>Agreement (NMI) with evening 1: ${f3(nmi(run.part, d.unweighted[0].part))} · with seating by era: ${f3(nmi(run.part, d.eraPlan))} · with your plan: ${f3(nmi(run.part, S.plan))}`;
    document.querySelectorAll('[data-evening]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.evening === ev)));

    const plot = $('null-plot'), lo = .1, hi = .3, x = v => 10 + (v - lo) / (hi - lo) * 380;
    const stack = new Map();
    plot.innerHTML = `<line class="axis" x1="10" x2="390" y1="84" y2="84"/>` + [.1, .15, .2, .25, .3].map(v => `<text x="${x(v)}" y="100" text-anchor="middle">${v.toFixed(2)}</text>`).join('')
      + nullQ.map((q, i) => { const bin = Math.round(q / .005); const h = stack.get(bin) || 0; stack.set(bin, h + 1); return `<circle cx="${x(bin * .005).toFixed(1)}" cy="${78 - h * 7}" r="3.2" fill="${i === S.shuffle ? '#d86b78' : '#c9a36a'}"/>`; }).join('')
      + `<line x1="${x(mean(realQ))}" x2="${x(mean(realQ))}" y1="14" y2="84" stroke="#efe6d6" stroke-width="2"/><text x="${x(mean(realQ)) - 4}" y="22" text-anchor="end">our party ${f3(mean(realQ))}</text><text x="${x(nullMean)}" y="10" text-anchor="middle">shuffled</text>`;
    $('null-status').innerHTML = `${S.shuffle === null ? 'Fifty shuffled parties, already seated.' : `Shuffled party ${S.shuffle + 1}: harmony ${f3(nullQ[S.shuffle])}.`}<br>Shuffled: ${f3(nullMean)} ± ${f3(nullSd)}. Ours: ${f3(mean(realQ))}, ${((mean(realQ) - nullMean) / nullSd).toFixed(1)} standard deviations higher.`;

    const wRun = d.weighted[ev];
    $('volume-status').innerHTML = S.weighted
      ? `By volume: ${tablesOf(wRun.part)} tables, weighted harmony ${f3(wRun.q)}.<br>Plato and Aristotle share a table on ${together(d.weighted, PLATO, ARISTOTLE)} of 50 evenings.`
      : `By count: ${tablesOf(run.part)} tables, harmony ${f3(run.q)}.<br>Plato and Aristotle share a table on ${together(d.unweighted, PLATO, ARISTOTLE)} of 50 evenings.`;

    const keepD = disparity(E, n, ALPHAS[S.alpha]), budget = keepD.filter(Boolean).length, keepG = loudest(E, budget);
    const lostD = alone(E, keepD, n).map(card), lostG = alone(E, keepG, n).map(card);
    $('alpha-out').textContent = ALPHAS[S.alpha].toFixed(2);
    $('alpha').setAttribute('aria-valuetext', ALPHAS[S.alpha].toFixed(2));
    $('backbone-status').innerHTML = `α = ${ALPHAS[S.alpha]}: the filter keeps ${budget} of ${E.length} conversations.<br>Disparity filter leaves alone: ${esc(list(lostD))}.<br>The ${budget} loudest links leave alone: ${esc(list(lostG))}.`;

    const c = d.cliques[S.k], counts = G.map((_, i) => c.communities.filter(m => m.includes(i)).length);
    const several = G.map((_, i) => i).filter(i => counts[i] > 1).map(i => `${card(i)} (${counts[i]})`);
    $('k-out').textContent = S.k;
    $('clique-status').innerHTML = c.communities.length
      ? `${c.cliques} ${S.k}-cliques join into ${c.communities.length} circle${c.communities.length === 1 ? '' : 's'}.<br>In several: ${esc(list(several))}. In none: ${esc(list(counts.map((k, i) => k ? null : card(i)).filter(Boolean)))}.`
      : `No ${S.k} guests all talk to one another. Nobody stands in a circle.`;
    $('circles').innerHTML = c.communities.map((m, j) => `<li><i style="border-color:${PALETTE[j]}"></i><span>${esc(m.map(card).join(', '))}</span></li>`).join('');
  }

  // ---------------------------------------------------------------- controls
  let timer = 0;
  const stop = () => { clearInterval(timer); timer = 0; $('play').textContent = '▶ Watch the maître d’ seat the room'; };
  $('play').addEventListener('click', () => {
    if (timer) { stop(); return; }
    S.course = 'louvain'; S.selected = null;
    const steps = replay(S.evening);
    if (reduced) { S.step = null; render(); return; }
    S.step = 0; render();
    $('play').textContent = '❚❚ Pause';
    timer = setInterval(() => {
      if (S.step >= steps.length - 1) { stop(); S.step = null; render(); return; }
      S.step++; render();
    }, 700);
  });
  $('another').addEventListener('click', () => { stop(); S.evening = (S.evening + 1) % d.unweighted.length; S.step = null; render(); });
  $('evenings').addEventListener('click', e => { const b = e.target.closest('[data-evening]'); if (!b) return; stop(); S.evening = +b.dataset.evening; S.step = null; render(); });
  document.querySelectorAll('[data-plan]').forEach(b => b.addEventListener('click', () => {
    const kind = b.dataset.plan;
    S.plan = kind === 'one' ? G.map(() => 0) : kind === 'era' ? [...d.eraPlan] : G.map(() => Math.floor(Math.random() * 4));
    render();
  }));
  $('shuffle').addEventListener('click', () => { S.shuffle = S.shuffle === null ? 0 : (S.shuffle + 1) % d.null.length; render(); });
  document.querySelectorAll('[data-weight]').forEach(b => b.addEventListener('click', () => {
    S.weighted = b.dataset.weight === 'volume';
    document.querySelectorAll('[data-weight]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render();
  }));
  document.querySelectorAll('[data-filter]').forEach(b => b.addEventListener('click', () => {
    S.filter = b.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render(false);
  }));
  $('alpha').addEventListener('input', e => { S.alpha = +e.target.value; render(false); });
  $('k').addEventListener('input', e => { S.k = +e.target.value; render(false); });

  // The course crossing the reading line sets the scene.
  const observer = new IntersectionObserver(entries => {
    const hit = entries.find(e => e.isIntersecting);
    if (!hit || hit.target.dataset.course === S.course) return;
    stop(); S.step = null;
    S.course = hit.target.dataset.course;
    render();
  }, { rootMargin:phone.matches ? '-74% 0px -22% 0px' : '-55% 0px -40% 0px' });
  document.querySelectorAll('.course, .cover').forEach(s => observer.observe(s));
  render();
}

start().catch(err => { $('load-error').hidden = false; $('load-error').textContent = `${err.message}. Serve this folder over HTTP (python3 -m http.server) and reload.`; });
