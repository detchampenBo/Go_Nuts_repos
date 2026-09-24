// Throwaway demo of the selected Aristotle-first direction. All state is in memory.
import { xFraction } from './school.mjs';
const d = await (await fetch('school-data.json')).json();
const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const colors = ['#2a78d6','#c55b26','#17876a','#b17b00','#bd4d81','#3a8542','#7860bb','#c94f57','#88929e'];
const name = i => d.lanes[i].splinter ? 'Small groups' : `${d.lanes[i].top[0]} group`;
const shortName = i => d.lanes[i].splinter ? 'Small groups' : `${d.lanes[i].top[0].split(' ').at(-1)} group`;
const P = d.philosophers;
const home = p => p.votes.indexOf(Math.max(...p.votes));
let run = 0, selected = P.findIndex(p => p.name === 'Aristotle'), previous = 0;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const x = p => 214 + xFraction(p.year) * 900;
const y = (p, i, r) => 58 + p.runs[r] * 57 + Math.sin(i * 12.9898) * 15;
const radius = p => 1.5 + Math.sqrt(p.degree) * .37;
const ari = P[selected];
$('split').innerHTML = ari.votes.map((v,i)=>({v,i})).filter(a=>a.v).sort((a,b)=>b.v-a.v).map(({v,i}) => `<div class="vote"><span>${esc(shortName(i))}</span><div class="track"><div class="bar" style="width:${v / d.runs.length * 100}%;background:${colors[i]}"></div></div><b>${v}<small>/50</small></b></div>`).join('');
$('people').innerHTML = P.map(p=>`<option value="${esc(p.name)}"></option>`).join('');
function detail() {
  const p = P[selected], lane = p.runs[run];
  $('detail').innerHTML = `<h2>${esc(p.name)}</h2><p>Run ${run+1}: <strong>${esc(name(lane))}</strong> · ${p.votes[lane]} of 50 runs assign this group.</p><p>${p.degree} links · ${p.yearKnown ? `Born ${p.year < 0 ? `${-p.year} BC` : p.year}` : 'Birth year estimated from era'} · <a href="${esc(p.url)}" target="_blank" rel="noopener">Wikipedia</a></p>`;
  $('metrics').textContent = `This run: modularity Q = ${d.runs[run].q.toFixed(3)}; similarity to the reference (NMI, 0–1) = ${d.runs[run].nmi.toFixed(2)}. Degree-preserving shuffled networks score Q = ${d.nullQ.mean.toFixed(3)} on average. These are optimised partitions of the shuffled networks, using the same measure.`;
}
function draw(t = 1) {
  const moving = previous !== run;
  const changed = P.filter(p=>p.runs[run]!==p.runs[previous]).length;
  $('status').innerHTML = `<strong>Run ${run+1} / 50 · seed ${d.meta.seeds[run]}</strong>${moving ? `${changed} philosophers changed lanes since run ${previous+1}` : 'Select a dot or run the algorithm again'}`;
  let s = d.lanes.map((l,i)=>`<rect x="0" y="${30+i*57}" width="1200" height="57" fill="${i%2 ? '#f3f6fa':'#fff'}"/><rect x="0" y="${34+i*57}" width="4" height="49" fill="${colors[i]}"/><text x="18" y="${56+i*57}" font-size="12" font-weight="600" fill="#182333">${esc(shortName(i))}</text><text x="18" y="${74+i*57}" font-size="10" fill="#526578">${P.filter(p=>p.runs[run]===i).length} philosophers</text>`).join('');
  for (const year of [-800,-400,0,1000,1500,1700,1800,1900]) { const xx=214+xFraction(year)*900; s+=`<path d="M${xx} 30V543" stroke="#e3eaf2"/><text x="${xx}" y="20" text-anchor="middle" font-size="10" fill="#526578">${year<0 ? `${-year} BC` : year===0 ? '1 AD' : year}</text>`; }
  if (moving) P.forEach((p,i)=>{ if(p.runs[run]===p.runs[previous]) return; const xx=x(p), a=y(p,i,previous), b=y(p,i,run); s+=`<path d="M${xx} ${a} Q${xx+26} ${(a+b)/2} ${xx} ${b}" fill="none" stroke="${colors[home(p)]}" stroke-width="${i===selected?2.5:1}" opacity="${i===selected?.8:.13}"/>`; });
  P.forEach((p,i)=>{ if(i===selected)return; const moved = moving && p.runs[run]!==p.runs[previous]; const yy=y(p,i,previous)+(y(p,i,run)-y(p,i,previous))*t; s+=`<circle class="node" data-i="${i}" cx="${x(p)}" cy="${yy}" r="${radius(p)}" fill="${colors[home(p)]}" opacity="${moving ? moved?.88:.22 : .6}" stroke="${moved?'#182333':'white'}" stroke-width="${moved?1.2:.6}"><title>${esc(p.name)} · ${esc(name(p.runs[run]))}</title></circle>`; });
  const p=P[selected], xx=x(p), yy=y(p,selected,previous)+(y(p,selected,run)-y(p,selected,previous))*t;
  s+=`<circle cx="${xx}" cy="${yy}" r="${radius(p)+5}" fill="white" stroke="#182333" stroke-width="2"/><circle cx="${xx}" cy="${yy}" r="${radius(p)}" fill="${colors[home(p)]}"/><text x="${xx>850?xx-18:xx+18}" y="${yy-15}" text-anchor="${xx>850?'end':'start'}" font-size="13" font-weight="700" fill="#182333" stroke="white" stroke-width="4" paint-order="stroke">${esc(p.name)} → ${esc(shortName(p.runs[run]))}</text>`;
  $('map').innerHTML=s;
}
let animation;
function change(next) {
  cancelAnimationFrame(animation); previous=run; run=next; detail();
  if(reduced){draw();return;}
  $('again').disabled=true; $('reset').disabled=true;
  const start=performance.now();
  function frame(now){const t=Math.min(1,(now-start)/1100);draw(t*t*(3-2*t));if(t<1)animation=requestAnimationFrame(frame);else{$('again').disabled=false;$('reset').disabled=false;}}
  animation=requestAnimationFrame(frame);
}
$('again').onclick=()=>change((run+1)%d.runs.length);
$('reset').onclick=()=>change(0);
$('map').onclick=e=>{const target=e.target.closest('[data-i]');if(target){selected=+target.dataset.i;$('person').value=P[selected].name;detail();draw();}};
$('person').addEventListener('change',e=>{const i=P.findIndex(p=>p.name.toLowerCase()===e.target.value.trim().toLowerCase());if(i<0){$('search-message').textContent='Choose a philosopher from the suggestions.';return;}selected=i;$('search-message').textContent='';detail();draw();});
detail();draw();
