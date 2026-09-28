const $=id=>document.getElementById(id),A=Mystery.analyze(CASE),reduced=matchMedia('(prefers-reduced-motion: reduce)');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names=ids=>ids.map(i=>CASE.rooms[i].name).join(', '),suspectAt=room=>CASE.suspects.findIndex(s=>s.room===room),edgeKey=(a,b)=>[Math.min(a,b),Math.max(a,b)].join('-');
let clue=0,filed=[false,false,false],selections=[[],[],[]],probe=0,depth=0,measured=false,pairIndex=-1,playing=false,timer=0,accused=-1,closed=false,inspect=0,feedback='',feedbackGood=false,animFrame=0,animProgress=1;
let visibleSheets=[false,false,false];
const sheetInks=['#315a91','#987024','#8f4c43'];
const sheetNames=['Contacts','Distance','Traffic'];
const cluesHint=[
'Degree counts immediate neighbours, not every person you can eventually reach. Each line represents a mutual contact. Here raw degree is used; normalized degree would divide by 8.',
'BFS discovers everyone one distance layer at a time. Add the eight other people’s distances and divide by 8. Closeness is the inverse of that mean. This graph is connected and undirected, so everyone is reachable.',
'For each pair of people, find ALL shortest routes. If two routes tie and only one uses a hero, that hero earns ½ credit. Endpoints earn nothing. Add credits over the 28 pairs not involving that hero, then divide by 28. This is full normalized betweenness, not a single-route count.'
];
function emblem(i){
 const color=CASE.suspects[i].color;
 const art=[
 // Angular red hair, tactical suit, widow belt.
 `<path d="M29 20Q46 0 68 16L77 66 61 78 23 62Z" fill="#c73752"/><path d="M35 27L61 23 65 49 54 64 39 55Z" fill="#efb398"/><path d="M33 32L29 51 31 20 49 9 68 18 69 34 55 20Z" fill="#fa6273"/><path d="M38 39L46 40M55 38L62 36" stroke="#26142c" stroke-width="3"/><path d="M46 52L55 52" stroke="#9e3b51" stroke-width="2"/><path d="M38 59L49 69 60 60 77 70 90 112H10L23 72Z" fill="#263347"/><path d="M49 69V105M27 72L33 108M72 72L65 108" stroke="#7390a2" stroke-width="2"/><path d="M42 89H58L52 96 58 104H42L48 96Z" fill="#fa6273"/>`,
 // Web mask and red/blue suit.
 `<path d="M31 60L50 69 69 59 82 73 96 113H4L18 75Z" fill="#236e99"/><path d="M31 60L50 66 69 60 65 104H35Z" fill="#d94466"/><path d="M28 22Q49 -1 72 22L69 50 51 69 32 52Z" fill="#ed4b64"/><path d="M50 9V65M29 24L70 48M71 24L32 49M29 37H71M35 16Q50 27 65 16M32 50Q50 42 68 50" fill="none" stroke="#75263d" stroke-width="1.4"/><path d="M32 29L47 38 44 48Q32 46 32 29M68 29L53 38 56 48Q68 46 68 29" fill="#f6f3e5" stroke="#172a40" stroke-width="3"/><path d="M50 78V96M43 82L57 92M57 82L43 92" stroke="#172a40" stroke-width="3"/>`,
 // Horned cowl, exposed jaw, red body armour.
 `<path d="M29 62L49 70 69 62 86 76 95 113H5L15 78Z" fill="#a02a53"/><path d="M30 21L29 5 40 19Q52 12 62 20L72 5 71 43 63 60H37L29 43Z" fill="#cb3b67"/><path d="M34 43L49 48 66 42 62 57 51 66 38 57Z" fill="#d69b85"/><path d="M34 32L46 36 36 39M66 32L54 36 64 39" fill="#1c152c"/><path d="M44 55H57M50 19V43" stroke="#762747" stroke-width="2"/><path d="M29 79L48 86 72 77M50 71V111" fill="none" stroke="#f77e92" stroke-width="2"/><path d="M40 92V103Q53 104 53 98T40 92M49 92V103Q62 104 62 98T49 92" fill="none" stroke="#f77e92" stroke-width="2"/>`,
 // Tall black mask fins, yellow uniform and foreground claws.
 `<path d="M25 64L48 72 73 63 90 82 96 113H5L13 81Z" fill="#eabb43"/><path d="M27 26L13 3 39 20 61 20 87 3 73 47 63 64H37L26 47Z" fill="#e8be49"/><path d="M13 3L39 20 42 46 29 44ZM87 3L61 20 58 46 72 44Z" fill="#21334b"/><path d="M35 46L49 50 65 46 62 62 49 70 37 61Z" fill="#d5a182"/><path d="M28 33L39 36M61 36L72 33" stroke="#f5f3e6" stroke-width="3"/><path d="M42 59H57" stroke="#4b2630" stroke-width="2"/><path d="M27 67L36 108H18L10 85M72 66L65 108H84L91 84" fill="#244669"/><path d="M14 114L19 66 23 114M24 115L31 61 32 113M35 114L42 70 42 113" fill="#e8f0ee" stroke="#708fa2" stroke-width="1"/>`
 ][i];
 return `<svg viewBox="0 0 100 112" aria-hidden="true"><path d="M0 0H100V112H0Z" fill="#d9ded8"/><path d="M-10 90L96 2M-8 113L108 16M20 118L113 39" stroke="${color}" stroke-width="1" opacity=".2"/><circle cx="51" cy="42" r="34" fill="none" stroke="${color}" opacity=".4"/>${art}<path d="M0 105L100 88V112H0Z" fill="#1a1025" opacity=".18"/></svg>`;
}
function geometry(){const mobile=innerWidth<=760;return {mobile,w:mobile?460:1050,h:mobile?840:600,p:mobile?CASE.rooms.map(p=>({x:p.y*.67+38,y:p.x*.78+35})):CASE.rooms};}
function edgeD(a,b,g){const u=g.p[a],v=g.p[b],dx=v.x-u.x,dy=v.y-u.y,d=Math.hypot(dx,dy),r=suspectAt(a)>=0?36:23,t=suspectAt(b)>=0?36:23;const bend=edgeKey(a,b)==='2-7'?70:0;return `M${u.x+dx/d*r},${u.y+dy/d*r} Q${(u.x+v.x)/2-dy/d*bend},${(u.y+v.y)/2+dx/d*bend} ${v.x-dx/d*t},${v.y-dy/d*t}`;}
function trafficTotals(){const totals=A.a.map(()=>0);for(let i=0;i<=pairIndex;i++)A.pairs[i].credit.forEach((v,j)=>totals[j]+=v);return totals;}
function renderGraph(){
 const g=geometry(),node=CASE.suspects[probe].room,search=A.searches[node],lit=new Set(),nodes=new Set(),totals=trafficTotals(),pair=A.pairs[pairIndex];
 if(clue===0&&measured){nodes.add(node);A.a[node].forEach(n=>{nodes.add(n);lit.add(edgeKey(node,n));});}
 if(clue===1){search.distance.forEach((d,i)=>{if(d<=depth)nodes.add(i);});CASE.edges.forEach(([u,v])=>{if(Math.abs(search.distance[u]-search.distance[v])===1&&Math.max(search.distance[u],search.distance[v])<=depth)lit.add(edgeKey(u,v));});}
 if(clue===2&&pair)pair.routes.forEach(p=>p.forEach((v,i)=>{nodes.add(v);if(i)lit.add(edgeKey(p[i-1],v));}));
 let svg='<title>Nine people and fourteen mutual contacts</title>';
 CASE.edges.forEach(([a,b])=>{const active=lit.has(edgeKey(a,b));svg+=`<path d="${edgeD(a,b,g)}" fill="none" stroke="#f1f4ef" stroke-width="8"/><path d="${edgeD(a,b,g)}" fill="none" stroke="${active?sheetInks[Math.min(clue,2)]:'#9aa69d'}" stroke-width="${active?3:1.6}" opacity="${active?1:.6}"/>`;if(active&&animProgress<1)svg+=`<path d="${edgeD(a,b,g)}" fill="none" stroke="#263e32" stroke-width="5" pathLength="100" stroke-dasharray="${animProgress*100} 100"/>`;});
 CASE.rooms.forEach((person,id)=>{const p=g.p[id],s=suspectAt(id),r=s>=0?34:22,selected=id===node;
 if(clue===2&&totals[id]>0){const halo=Math.sqrt(42*42+totals[id]/A.denominator*9000);svg+=`<circle cx="${p.x}" cy="${p.y}" r="${halo}" fill="#8f4c43" fill-opacity=".12" stroke="#8f4c43" stroke-width="2"/>`;}
 if(clue===1&&search.distance[id]===depth)svg+=`<circle cx="${p.x}" cy="${p.y}" r="${r+10+(1-animProgress)*15}" fill="none" stroke="#987024" stroke-width="2"/>`;
 svg+=`<g class="room" role="button" tabindex="0" data-room="${id}" aria-label="Inspect ${esc(person.name)}"><circle class="room-circle" cx="${p.x}" cy="${p.y}" r="${r+3}" fill="#f5f6f1" stroke="${nodes.has(id)?sheetInks[Math.min(clue,2)]:selected?'#334f40':s>=0?'#708076':'#a5afa7'}" stroke-width="${selected?3:1.5}"/>`;
 if(s>=0)svg+=`<svg x="${p.x-28}" y="${p.y-32}" width="56" height="63" viewBox="0 0 100 112">${emblem(s).replace(/^<svg[^>]*>/,'').replace(/<\/svg>$/,'')}</svg>`;
 else svg+=`<text x="${p.x}" y="${p.y+5}" text-anchor="middle" fill="#42574a" style="font-size:13px;stroke:none">${person.name.split(' ').map(n=>n[0]).join('')}</text>`;
 svg+=`<text x="${p.x}" y="${p.y+r+22}" text-anchor="middle" fill="#243d30" style="font-size:${g.mobile?14:16}px;font-weight:700">${esc(person.name)}</text>`;
 if(clue===1&&nodes.has(id))svg+=`<circle cx="${p.x+r}" cy="${p.y-r}" r="12" fill="#e4c990"/><text x="${p.x+r}" y="${p.y-r+5}" text-anchor="middle" fill="#160e25" style="font-size:13px;stroke:none;font-weight:bold">${search.distance[id]}</text>`;
 if(clue===2&&pair)svg+=`<text x="${p.x}" y="${p.y+r+39}" text-anchor="middle" fill="#83473e" style="font-size:12px">${(totals[id]/A.denominator*100).toFixed(1)}%${pairIndex<35?' so far':''}</text>`;
 svg+='</g>';
 });
 const focus=document.activeElement?.dataset.room;$('network').setAttribute('viewBox',`0 0 ${g.w} ${g.h}`);$('network').innerHTML=svg;renderSheets();if(focus!==undefined)$('network').querySelector(`[data-room="${focus}"]`)?.focus({preventScroll:true});
}
function renderSheets(){
 const g=geometry(),shown=visibleSheets.filter(Boolean).length;
 const focused=document.activeElement?.dataset.sheet;
 $('sheet-controls').innerHTML=sheetNames.map((n,c)=>`<button data-sheet="${c}" style="--sheet-ink:${sheetInks[c]}" aria-pressed="${visibleSheets[c]}" ${filed[c]?'':'disabled'}>${c+1} / ${n}<small>${!filed[c]?'File clue to unlock':visibleSheets[c]?'On table':'Lifted'}</small></button>`).join('');
 $('toggle-sheets').textContent=shown?'Lift all sheets':'Stack filed sheets';$('toggle-sheets').disabled=!filed.some(Boolean);
 $('sheet-status').textContent=!filed.some(Boolean)?'Start with the base drawing. Each solved clue adds a transparent sheet.':`${shown} of ${filed.filter(Boolean).length} filed sheets on the table. A check means that suspect fits that sheet; a cross means they do not.`;
 $('light-table').dataset.layers=shown;
 $('sheet-overlays').innerHTML=visibleSheets.map((yes,c)=>{
  if(!yes)return '';const ink=sheetInks[c];let marks='';
  CASE.suspects.forEach((s,i)=>{const point=g.p[s.room],m=A.facts[i],fits=A.matches[c][i];const value=[`${m.degree} contacts`,`${m.mean.toFixed(3)} steps`,`${(m.between*100).toFixed(1)}% traffic`][c];
   const x=point.x+(g.mobile?-72:43),y=point.y+(g.mobile?62:-35)+c*22;
   marks+=`<g transform="translate(${x},${y})"><rect x="-5" y="-14" width="${g.mobile?148:125}" height="20" rx="1" fill="#f7f9f2" fill-opacity=".92"/><text fill="${ink}" font-size="${g.mobile?15:12}" font-family="Arial,sans-serif">${fits?'✓':'×'} ${value}</text></g>`;
   if(fits)marks+=`<circle cx="${point.x}" cy="${point.y}" r="${40+c*5}" fill="none" stroke="${ink}" stroke-width="1.5" stroke-dasharray="${c===1?'3 3':c===2?'9 3':'none'}"/>`;
  });
  return `<svg class="evidence-sheet" viewBox="0 0 ${g.w} ${g.h}" style="--sheet-ink:${ink}"><rect x="${7+c*3}" y="${7+c*3}" width="${g.w-24}" height="${g.h-24}" fill="${ink}" fill-opacity=".025" stroke="${ink}" stroke-opacity=".3"/>${marks}</svg>`;
 }).join('');
 if(focused!==undefined)$('sheet-controls').querySelector(`[data-sheet="${focused}"]`)?.focus({preventScroll:true});
}
function animate(){cancelAnimationFrame(animFrame);if(reduced.matches){animProgress=1;renderGraph();return;}animProgress=0;const start=performance.now();function step(now){animProgress=Math.min(1,(now-start)/600);renderGraph();if(animProgress<1)animFrame=requestAnimationFrame(step);}animFrame=requestAnimationFrame(step);}
function stopTraffic(){clearInterval(timer);playing=false;}
function tools(){
 const hero=CASE.suspects[probe],m=A.facts[probe],search=A.searches[hero.room],maxDepth=search.layers.length-1,complete=depth===maxDepth;
 $('tools').innerHTML=`<label for="probe">Investigate a hero</label><select id="probe">${CASE.suspects.map((s,i)=>`<option value="${i}">${esc(s.name)}</option>`).join('')}</select><p class="tool-readout" id="measurement"></p>`;$('probe').value=probe;
 $('probe').onchange=e=>{probe=+e.target.value;depth=0;measured=false;updateView();};
 let controls='';
 if(clue===0){$('map-heading').textContent='Who knows whom?';$('map-state').textContent=measured?`${hero.name}: ${m.degree} direct contacts.`:'Choose a hero, then inspect their contacts.';$('map-note').textContent='A line is a mutual contact. Only immediate neighbours count.';controls='<button id="measure" class="primary">Light up contacts</button>';$('measurement').textContent=measured?`${m.degree} contacts: ${names(A.a[hero.room])}.`:'Count connections, not everyone reachable along a chain.';}
 if(clue===1){$('map-heading').textContent='How close to everyone?';$('map-state').textContent=`${hero.name} · distance layer ${depth} · ${search.distance.filter(d=>d<=depth).length} of 9 people reached`;$('map-note').textContent='Badges show shortest distance. Each wave adds one step; positions stay fixed.';controls=`<button id="expand" class="primary" ${complete?'disabled':''}>${depth===0?'Send first wave':'Send next wave'}</button><button id="restart-wave">Restart waves</button>`;$('measurement').textContent=complete?`Distances to the other 8: ${search.distance.filter((_,i)=>i!==hero.room).join(' + ')} = ${m.sum}. Mean = ${m.sum}/8 = ${m.mean.toFixed(3)} steps. Closeness = ${m.closeness.toFixed(3)}.`:'Finish the waves to calculate the average distance to all eight other people.';}
 if(clue===2){const pair=A.pairs[pairIndex],total=trafficTotals()[hero.room];$('map-heading').textContent='Who carries the traffic?';$('map-state').textContent=pair?`Pair ${pairIndex+1}/36: ${CASE.rooms[pair.s].name} ↔ ${CASE.rooms[pair.t].name}. ${pair.routes.length} shortest route${pair.routes.length===1?'':'s'}.`:'Play back shortest routes between every pair of people.';$('map-note').textContent=pair?`${hero.name} earns ${pair.credit[hero.room].toFixed(2)} credit for this pair. The extra terracotta halo area grows with accumulated credit. Endpoints earn zero.`:'This is calculated shortest-path traffic, not observed messages. All tied shortest routes share one unit of credit.';controls=`<button id="play-traffic" class="primary" ${pairIndex===35?'disabled':''}>${playing?'Pause traffic':'Play traffic'}</button><button id="next-pair" ${pairIndex===35?'disabled':''}>Next pair</button><button id="finish-traffic">Show full count</button><button id="restart-traffic">Restart traffic</button>`;$('measurement').textContent=pairIndex<35?`${hero.name}: ${total.toFixed(2)} credits so far. Finish all 36 network pairs before comparing scores.`:`${hero.name}: ${total.toFixed(2)} / 28 eligible pairs = ${(m.between*100).toFixed(1)}% betweenness.`;}
 $('graph-controls').innerHTML=controls;
 if($('measure'))$('measure').onclick=()=>{measured=true;updateView();animate();};
 if($('expand'))$('expand').onclick=()=>{depth++;updateView();animate();};
 if($('restart-wave'))$('restart-wave').onclick=()=>{depth=0;updateView();};
 const advance=()=>{pairIndex=Math.min(35,pairIndex+1);if(pairIndex===35)stopTraffic();updateView();animate();};
 if($('next-pair'))$('next-pair').onclick=()=>{stopTraffic();advance();};
 if($('play-traffic'))$('play-traffic').onclick=()=>{if(playing){stopTraffic();updateView();}else{playing=true;advance();if(playing)timer=setInterval(advance,1100);}};
 if($('finish-traffic'))$('finish-traffic').onclick=()=>{stopTraffic();pairIndex=35;updateView();};
 if($('restart-traffic'))$('restart-traffic').onclick=()=>{stopTraffic();pairIndex=-1;updateView();};
}
function updateMapText(){}
function renderSuspects(){
  const remaining=Mystery.survivors(A.matches,filed),final=clue===3;
  $('suspects-heading').textContent=final?'Who is the mastermind?':'Who can you clear?' ;
  $('suspect-help').textContent=final?'Choose one suspect, then submit your accusation.':'Choose ONE suspect who cannot fit the clue. Cleared heroes stay out of the case.';
  $('remaining').textContent=`${remaining.length} ${remaining.length===1?'suspect remains':'suspects remain'}`;
  $('suspects').innerHTML=CASE.suspects.map((s,i)=>{
    const selected=final?accused===i:selections[clue].includes(i),eliminated=filed.some((yes,c)=>yes&&!A.matches[c][i]);
    return `<button class="suspect ${eliminated?'cleared':''}" data-suspect="${i}" aria-pressed="${selected}" aria-label="${esc(s.name)}, ${esc(s.note)}${selected?', selected':''}" style="--suspect-color:${s.color}" ${closed||eliminated||(!final&&filed[clue])?'disabled':''}><div class="suspect-portrait">${emblem(i)}<span class="select-badge" aria-hidden="true">${selected?'✓':'+'}</span></div><div class="suspect-copy"><span class="suspect-name">${esc(s.name)}</span><span class="suspect-room">${esc(s.note)}</span><span class="suspect-status">${eliminated?'✓ Cleared — innocent':filed.some(Boolean)?'Still possible':'Still a suspect'}</span></div></button>`;
  }).join('');
}
function renderNotebook(){
  $('evidence-grid').innerHTML=CASE.suspects.map((s,i)=>`<tr><td>${esc(s.name)}</td>${filed.map((yes,c)=>`<td class="${yes?A.matches[c][i]?'yes':'no':'unknown'}">${yes?A.matches[c][i]?'✓ Fits':'× Does not fit':'—'}</td>`).join('')}</tr>`).join('');
  const count=filed.filter(Boolean).length;$('notebook-heading').textContent=count===3?'Only one fits every log.':count===2?'Two suspects. One clue left.':"One clue isn’t enough.";
  $('notebook-note').textContent=count===0?'Filed evidence appears here. A suspect must fit every clue to remain possible.':`${count} of 3 logs filed. Keep the intersection: a suspect must have a check in every filed column.`;
}
function roomFacts(){$('room-facts').textContent=`Direct contacts: ${names(A.a[inspect])}.`;}
function updateView(){
  cancelAnimationFrame(animFrame);animProgress=1;const focus=document.activeElement?.id,focusedSuspect=document.activeElement?.dataset.suspect;
  document.querySelectorAll('[data-clue]').forEach(b=>{const c=+b.dataset.clue;b.disabled=c>0&&!filed[c-1];b.classList.toggle('filed',filed[c]);if(c===clue)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');b.querySelector('.file-status').textContent=filed[c]?'Filed':b.disabled?'Locked':'Open';b.querySelector('.step-number').textContent=filed[c]?'✓':c+1;});
  $('accuse-tab').disabled=!filed.every(Boolean);$('accuse-tab').querySelector('.file-status').textContent=filed.every(Boolean)?'Open':'Locked';if(clue===3)$('accuse-tab').setAttribute('aria-current','step');else $('accuse-tab').removeAttribute('aria-current');
  $('investigation').classList.remove('hidden');document.querySelector('.evidence-panel').classList.toggle('hidden',clue===3);$('investigation').classList.toggle('reviewing',clue===3);document.querySelector('.inspection').classList.toggle('hidden',clue===3);$('accusation').classList.toggle('hidden',clue!==3||closed);$('verdict').classList.toggle('hidden',!closed);
  if(clue<3){const c=CASE.clues[clue];$('file').textContent=selections[clue].length?'Clear '+CASE.suspects[selections[clue][0]].name:'Clear selected suspect';$('evidence-tag').textContent=`Evidence ${clue+1} / 3${filed[clue]?' · Filed':''}`;$('clue-title').textContent=c.name;$('statement').textContent=c.statement;$('topic').textContent=c.topic;$('math').textContent=c.math;$('instruction').textContent=c.instruction;$('hint').textContent=cluesHint[clue];$('question').textContent=c.question;tools();updateMapText();renderGraph();}
  $('file').classList.toggle('hidden',clue===3||filed[clue]);$('next-clue').classList.toggle('hidden',clue===3||!filed[clue]);$('next-clue').textContent=clue===2?'Make your accusation':'Next clue →';
  if(clue===3){$('map-heading').textContent='The evidence, aligned.';$('map-state').textContent='Only one suspect fits every filed sheet.';$('map-note').textContent='Lift individual sheets to see what each one contributes. Your deductions stay recorded.';$('graph-controls').innerHTML='';renderGraph();}
  $('feedback').textContent=feedback;$('feedback').classList.toggle('success',feedbackGood);renderSuspects();renderNotebook();roomFacts();
  if(focusedSuspect!==undefined)$('suspects').querySelector(`[data-suspect="${focusedSuspect}"]`)?.focus({preventScroll:true});else if(focus)$(focus)?.focus({preventScroll:true});
}
function switchClue(c){if(c===3&&!filed.every(Boolean)||c>0&&c<3&&!filed[c-1])return;stopTraffic();clue=c;if(c===3)visibleSheets=[...filed];depth=0;measured=false;feedback='';feedbackGood=false;updateView();$('investigation').querySelector('.hint').open=false;if(innerWidth<=760)document.querySelector(c===3?'.suspect-section':'.case-progress').scrollIntoView({block:'start',behavior:reduced.matches?'auto':'smooth'});}
function fileEvidence(){
  if(clue>=3||filed[clue])return;
  const chosen=selections[clue][0];
  if(chosen===undefined){feedback='Choose one suspect to clear using the cards below.';feedbackGood=false;updateView();return;}
  if(A.matches[clue][chosen]){feedback=`${CASE.suspects[chosen].name} still fits this clue. Look for someone whose measurement contradicts the clue.`;feedbackGood=false;updateView();return;}
  filed[clue]=true;visibleSheets[clue]=true;feedbackGood=true;const survivors=Mystery.survivors(A.matches,filed);const facts=A.facts[chosen];const explanation=[`${facts.degree} contacts, not 3`,`${facts.mean.toFixed(3)} steps on average, above 1.75`,`${(facts.between*100).toFixed(1)}% betweenness, below 10%`][clue];feedback=`${CASE.suspects[chosen].name} is cleared: ${explanation}. ${survivors.length} ${survivors.length===1?'suspect remains':'suspects remain'}.`;updateView();$('next-clue').focus({preventScroll:true});
}
function accuse(){
  if(!filed.every(Boolean)||clue!==3||closed)return;
  if(accused<0){$('accusation-feedback').textContent='Choose one suspect card first.';return;}
  const survivors=Mystery.survivors(A.matches,filed);
  if(!survivors.includes(accused)){const failed=CASE.clues.filter((_,c)=>!A.matches[c][accused]).map(c=>c.name);$('accusation-feedback').textContent=`That accusation contradicts ${failed.join(' and ')}. Check the notebook before submitting again.`;return;}
  closed=true;const s=CASE.suspects[accused],f=A.facts[accused];$('verdict-art').innerHTML=emblem(accused);$('verdict-title').textContent=`${s.name}. The hidden mastermind.`;$('verdict-copy').textContent='Only this suspect fits all three intercepted clues. Network position solves this fictional case; it is not evidence of wrongdoing in a real network.';
  $('proof').innerHTML=`<li><strong>Degree:</strong> ${f.degree} direct contacts.</li><li><strong>Closeness:</strong> ${f.sum}/8 = ${f.mean.toFixed(3)} steps on average, within the 1.75 limit. Closeness = ${f.closeness.toFixed(3)}.</li><li><strong>Betweenness:</strong> ${(f.between*A.denominator).toFixed(2)} / 28 = ${(f.between*100).toFixed(1)}%, above 10%.</li><li><strong>Why popularity misled you:</strong> Spider-Man has ${A.facts[1].degree} contacts, but Black Widow has higher betweenness (${(A.facts[0].between*100).toFixed(1)}% versus ${(A.facts[1].between*100).toFixed(1)}%). More contacts does not always mean more shortest-path traffic.</li>`;
  updateView();$('verdict').scrollIntoView({block:'center',behavior:reduced.matches?'auto':'smooth'});
}
function reset(){stopTraffic();cancelAnimationFrame(animFrame);clue=0;filed=[false,false,false];visibleSheets=[false,false,false];selections=[[],[],[]];depth=0;probe=0;measured=false;pairIndex=-1;accused=-1;closed=false;inspect=0;feedback='';feedbackGood=false;$('accusation-feedback').textContent='';$('inspect-room').value='0';updateView();document.querySelector('.hint').open=false;}
$('inspect-room').innerHTML=CASE.rooms.map((r,i)=>`<option value="${i}">${esc(r.name)}</option>`).join('');$('inspect-room').onchange=e=>{inspect=+e.target.value;roomFacts();};
function inspectNode(id){inspect=id;$('inspect-room').value=id;roomFacts();const suspect=suspectAt(id);if(suspect>=0){probe=suspect;depth=0;measured=false;updateView();}}
$('toggle-sheets').onclick=()=>{const lift=visibleSheets.some(Boolean);visibleSheets=filed.map(f=>lift?false:f);renderSheets();};
$('sheet-controls').onclick=e=>{const b=e.target.closest('[data-sheet]');if(!b||b.disabled)return;const c=+b.dataset.sheet;visibleSheets[c]=!visibleSheets[c];renderSheets();};
$('network').addEventListener('click',e=>{const n=e.target.closest('[data-room]');if(n)inspectNode(+n.dataset.room);});
$('network').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const n=e.target.closest('[data-room]');if(n){e.preventDefault();inspectNode(+n.dataset.room);}}});
$('suspects').onclick=e=>{const b=e.target.closest('[data-suspect]');if(!b||b.disabled||closed)return;const i=+b.dataset.suspect;if(clue===3){accused=i;$('accusation-feedback').textContent='';}else{selections[clue]=selections[clue][0]===i?[]:[i];feedback='';}updateView();};
document.querySelectorAll('[data-clue]').forEach(b=>b.onclick=()=>switchClue(+b.dataset.clue));$('accuse-tab').onclick=()=>switchClue(3);$('file').onclick=fileEvidence;$('next-clue').onclick=()=>switchClue(clue+1);$('submit-accusation').onclick=accuse;$('reset').onclick=reset;$('replay-case').onclick=()=>{reset();document.querySelector('.case-progress').scrollIntoView({block:'start',behavior:reduced.matches?'auto':'smooth'});};
window.addEventListener('resize',renderGraph);reduced.addEventListener('change',()=>{cancelAnimationFrame(animFrame);animProgress=1;renderGraph();});
reset();
