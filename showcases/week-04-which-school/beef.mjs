import { cases } from './beef-cases.mjs';
import { neighbourhood, pairSummary } from './beef-model.mjs';

const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const colors = ['#3b78a2','#a36524','#338269','#b28917','#b94c77','#438144','#7963b7','#b85a42','#78838c'];
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const controls = document.querySelectorAll('button');
controls.forEach(b => b.disabled = true);

async function start() {
  const [d, exact] = await Promise.all(['school-data.json','beef-data.json'].map(async url => {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Could not load ${url}`);
    return response.json();
  }));
  if (d.meta.inputSha256 !== exact.inputSha256) throw new Error('The network and pair results use different source data.');
  const P = d.philosophers;
  let current = cases.find(c => c.id === new URLSearchParams(location.search).get('dispute')) || cases[0];
  let n, run = 0, view = 'all', inspected = null;
  const guesses = new Map();
  const lane = i => P[i].runs[d.meta.referenceRun];
  const laneName = i => d.lanes[i].splinter ? 'Small reference groups' : `Group with ${d.lanes[i].top[0]}`;
  const glyph = same => same
    ? '<svg viewBox="0 0 28 18" aria-hidden="true"><path d="M7 9H21" stroke="currentColor" stroke-width="2"/><circle cx="6" cy="9" r="4" fill="currentColor"/><circle cx="22" cy="9" r="4" fill="currentColor"/></svg>'
    : '<svg viewBox="0 0 28 18" aria-hidden="true"><circle cx="5" cy="6" r="3" fill="none" stroke="currentColor"/><circle cx="23" cy="12" r="3" fill="none" stroke="currentColor"/><path d="M17 2L11 16" stroke="currentColor"/></svg>';

  function renderCase() {
    n = neighbourhood(d, current.people);
    run = 0; view = 'all'; inspected = null;
    document.querySelectorAll('[data-case]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.case === current.id)));
    $('case-kind').textContent = current.kind;
    $('case-heading').textContent = current.topic;
    $('case-count').textContent = `Dispute ${cases.indexOf(current)+1} of ${cases.length}`;
    $('arena').innerHTML = current.people.map((person, i) => `<article class="contender"><img class="portrait" src="portraits/${current.images[i]}" alt="Portrait of ${esc(person)}" width="300" height="400"><div><h3>${esc(current.short[i])}</h3><span class="lifespan">${esc(current.dates[i])}</span><p class="position">${esc(current.positions[i])}</p><p class="position-detail">${esc(current.explanations[i])}</p></div></article>`).join('') + '<span class="vs" aria-hidden="true">vs.</span><span class="paraphrase">Positions paraphrased from the sources below</span>';
    $('dispute-context').textContent = current.context;
    $('source-list').innerHTML = current.sources.map(([title,note,url]) => `<div class="source"><a href="${esc(url)}" target="_blank" rel="noopener">${esc(title)} ↗</a><p>${esc(note)}</p></div>`).join('');
    $('evidence').hidden = $('connections').hidden = !guesses.has(current.id);
    document.querySelectorAll('[data-guess]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.guess === guesses.get(current.id))));
    $('skip-guess').textContent = guesses.has(current.id) ? 'View the evidence again' : 'Just show me the evidence';
    if (guesses.has(current.id)) renderEvidence();
    const url = new URL(location.href); url.searchParams.set('dispute',current.id); history.replaceState(null,'',url);
  }

  function reveal(guess) {
    guesses.set(current.id, guess);
    $('evidence').hidden = $('connections').hidden = false;
    document.querySelectorAll('[data-guess]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.guess === guess)));
    $('skip-guess').textContent = 'View the evidence again';
    renderEvidence();
    $('result-title').focus({preventScroll:true});
    $('evidence').scrollIntoView({behavior: reduced ? 'auto' : 'smooth', block:'start'});
  }

  function renderEvidence() {
    const pair = exact.pairs[current.id];
    const stats = pairSummary(pair.together);
    const guess = guesses.get(current.id);
    $('guess-feedback').textContent = guess === 'skip' ? 'What the network says' : stats.majority === 'tie' ? 'An even split across runs' : guess === stats.majority ? 'Your prediction matches the majority of runs' : 'The majority of runs says otherwise';
    $('result-title').textContent = stats.same === stats.total ? 'At odds in print. Together in every run.' : stats.majority === 'together' ? 'Opposing positions. Usually one community.' : 'A real dispute. An uncertain boundary.';
    $('result-copy').textContent = current.interpretation;
    $('together-count').textContent = stats.same;
    $('runs').innerHTML = pair.together.map((same,i) => `<button class="run ${same ? 'same' : 'different'}" data-run="${i}" aria-pressed="${i===run}" aria-label="Seed ${d.meta.seeds[i]}: ${same?'same':'different'} community${same?'':' groups'}">${glyph(same)}<small>${d.meta.seeds[i]}</small></button>`).join('');
    renderRun();
    $('network-intro').textContent = `${current.short[0]} has ${P[n.pair[0]].degree} neighbours; ${current.short[1]} has ${P[n.pair[1]].degree}. They share ${n.shared.length}. Shared neighbours are connections in Wikipedia, not a list of supporters.`;
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.view===view)));
    renderGraph();
    const list = (ids, label) => `<section><h3>${esc(label)} (${ids.length})</h3><ul>${ids.map(i=>`<li><a href="${esc(P[i].url)}" target="_blank" rel="noopener">${esc(P[i].name)}</a> · ${P[i].degree} links</li>`).join('')}</ul></section>`;
    $('neighbour-list').innerHTML = list(n.shared,'Connected to both') + list(n.exclusive[0],`Only ${current.short[0]} (of this pair)`) + list(n.exclusive[1],`Only ${current.short[1]} (of this pair)`);
  }

  function renderRun() {
    const same = exact.pairs[current.id].together[run];
    $('run-detail').textContent = `Seed ${d.meta.seeds[run]}: ${same?'together':'apart'} · ${d.runs[run].k} communities · Q ${d.runs[run].q.toFixed(3)}`;
    document.querySelectorAll('[data-run]').forEach(b => b.setAttribute('aria-pressed',String(+b.dataset.run===run)));
  }

  function renderGraph() {
    const shared = n.shared.slice(0,12), left=n.exclusive[0].slice(0,6), right=n.exclusive[1].slice(0,6);
    const nodes = [
      ...n.pair.map((i,k)=>({i,x:k?810:310,y:280,kind:'pair',side:k})),
      ...shared.map((i,k)=>({i,x:560,y:78+k*(408/Math.max(1,shared.length-1)),kind:'shared'})),
      ...left.map((i,k)=>({i,x:95+Math.sin(k)*15,y:100+k*72,kind:'exclusive',side:0})),
      ...right.map((i,k)=>({i,x:1025-Math.sin(k)*15,y:100+k*72,kind:'exclusive',side:1})),
    ];
    let svg = `<text x="95" y="38" text-anchor="middle" font-size="12" fill="#695c76">${esc(current.short[0])} only</text><text x="560" y="38" text-anchor="middle" font-size="12" fill="#695c76">Connected to both</text><text x="1025" y="38" text-anchor="middle" font-size="12" fill="#695c76">${esc(current.short[1])} only</text>`;
    for (const q of nodes.filter(q=>q.kind!=='pair')) {
      for (const [side, ni] of n.neighbours.entries()) if (ni.has(q.i)) {
        const center=nodes[side];
        svg+=`<path d="M${center.x} ${center.y} Q${(center.x+q.x)/2} ${center.y} ${q.x} ${q.y}" fill="none" stroke="${q.kind==='shared'?'#907ab2':'#bcb0cc'}" stroke-width="${q.kind==='shared'?1.5:1}" opacity="${view==='shared'&&q.kind==='exclusive'?.1:.65}"/>`;
      }
    }
    if(n.direct) svg+='<path d="M330 280 Q560 600 790 280" stroke="#907ab2" fill="none" stroke-width="1.5"/><text x="560" y="463" text-anchor="middle" font-size="10" fill="#695c76" stroke="#faf7fd" stroke-width="4" paint-order="stroke">Direct Wikipedia link between the pair</text>';
    for(const q of nodes) {
      const p=P[q.i], r=2+.8*Math.sqrt(p.degree), focal=q.kind==='pair';
      const label=focal?current.short[q.side]:p.name;
      const anchor=q.kind==='exclusive'?(q.side?'end':'start'):'middle';
      const tx=q.kind==='exclusive'?q.x+(q.side?-r-7:r+7):q.x;
      const ty=q.kind==='exclusive'?q.y+4:q.y+r+(focal?25:13);
      svg+=`<g class="graph-node" role="button" tabindex="0" data-node="${q.i}" aria-label="Inspect ${esc(p.name)}, ${p.degree} links, ${esc(laneName(lane(q.i)))}" opacity="${view==='shared'&&q.kind==='exclusive'?.2:1}"><circle cx="${q.x}" cy="${q.y}" r="${Math.max(16,r+6)}" fill="transparent" stroke="${inspected===q.i?'#2d203e':'none'}" stroke-width="2"/><circle cx="${q.x}" cy="${q.y}" r="${r}" fill="${colors[lane(q.i)]}" stroke="${focal?'#2d203e':'#faf7fd'}" stroke-width="${focal?2:1}"/><text x="${tx}" y="${ty}" text-anchor="${anchor}" font-size="${focal?19:10}" font-weight="${focal?700:500}" fill="#2d203e" stroke="#faf7fd" stroke-width="4" paint-order="stroke">${esc(label)}</text>${focal?`<text x="${q.x}" y="${ty+19}" text-anchor="middle" font-size="10" fill="#695c76">${p.degree} links · reference group ${lane(q.i)+1}</text>`:''}</g>`;
    }
    $('network').innerHTML=svg;
    const lanes=[...new Set(nodes.map(q=>lane(q.i)))].sort((a,b)=>a-b);
    $('graph-legend').innerHTML=lanes.map(i=>`<span><i style="background:${colors[i]}"></i>${i+1}: ${esc(laneName(i))}</span>`).join('');
    const total=n.shared.length+n.exclusive[0].length+n.exclusive[1].length;
    $('network-note').textContent=`Showing ${nodes.length-2} of ${total} neighbours (${total-(nodes.length-2)} omitted): up to 12 shared and 6 exclusive per side, chosen by highest degree. This favours hubs. Only links to the featured pair are drawn. On a phone, swipe the drawing to explore.`;
    if (inspected === null) $('node-detail').textContent='Select a philosopher in the drawing to inspect their connections. The complete list below includes everyone omitted from the drawing.';
  }

  function inspect(i) {
    inspected=i;
    const p=P[i];
    const connected=n.neighbours.map((set,k)=>set.has(i)?current.short[k]:null).filter(Boolean);
    $('node-detail').innerHTML=`<strong>${esc(p.name)}</strong><br>${p.degree} links in the full network. ${connected.length?`Linked to ${esc(connected.join(' and '))}.`:''}<br>${esc(laneName(lane(i)))} in reference run ${d.meta.referenceRun+1}. <a href="${esc(p.url)}" target="_blank" rel="noopener">Read on Wikipedia ↗</a>`;
    // Preserve the focused SVG element while changing selection styling.
    document.querySelectorAll('[data-node]').forEach(g=>g.querySelector('circle').setAttribute('stroke',+g.dataset.node===i?'#2d203e':'none'));
  }

  document.querySelectorAll('[data-case]').forEach(b=>b.addEventListener('click',()=>{current=cases.find(c=>c.id===b.dataset.case);renderCase();}));
  document.querySelectorAll('[data-guess]').forEach(b=>b.addEventListener('click',()=>reveal(b.dataset.guess)));
  $('skip-guess').addEventListener('click',()=>reveal('skip'));
  $('runs').addEventListener('click',e=>{const b=e.target.closest('[data-run]');if(b){run=+b.dataset.run;renderRun();}});
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;document.querySelectorAll('[data-view]').forEach(btn=>btn.setAttribute('aria-pressed',String(btn===b)));renderGraph();}));
  $('network').addEventListener('click',e=>{const g=e.target.closest('[data-node]');if(g)inspect(+g.dataset.node);});
  $('network').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const g=e.target.closest('[data-node]');if(g){e.preventDefault();inspect(+g.dataset.node);}}});
  const qs=d.runs.map(r=>r.q);
  $('null-note').textContent=`The 50 partitions score modularity Q = ${Math.min(...qs).toFixed(3)}–${Math.max(...qs).toFixed(3)}. The mean after optimising ${d.nullQ.values.length} degree-preserving shuffles is ${d.nullQ.mean.toFixed(3)} (SD ${d.nullQ.sd.toFixed(3)}). This supports structure relative to that baseline, not the truth of a school label.`;
  controls.forEach(b=>b.disabled=false);
  renderCase();
}

start().catch(error=>{
  console.error(error);
  $('load-error').hidden=false;
  $('load-error').textContent='The network evidence could not be loaded. Serve this folder through the local web server and reload the page.';
});
