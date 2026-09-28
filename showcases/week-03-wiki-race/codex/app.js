const $=id=>document.getElementById(id),nodes=DATA.nodes,N=nodes.length;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const name=i=>nodes[i].name.replace(/ \([^)]*\)$/,'');
const frozen=RaceGraph.adjacency(N,DATA.edges),undirected=RaceGraph.adjacency(N,DATA.edges,false),reduceMotion=matchMedia('(prefers-reduced-motion: reduce)');
const sessionVisits=new Map(),viewCache=new Map(),viewPending=new Set();
let epoch=0,controller=new AbortController(),api=null,mode='live',mission=DATA.missions[0],state='idle',path=[],current=mission.start,currentLinks=[],known=new Map(),frames=[],solution=null,ring=0,autoTimer=0,won=false,motion=true,tick=0,cardIds=[],cardsVersion=0;
const chosen=()=>DATA.missions[+$('mission').value];
const still=e=>e===epoch&&!controller.signal.aborted;
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const heroOptions=nodes.map((n,i)=>({i,n:name(i)})).sort((a,b)=>a.n.localeCompare(b.n)).map(x=>`<option value="${x.i}">${esc(x.n)}</option>`).join('');
$('mission').innerHTML=DATA.missions.map((m,i)=>`<option value="${i}">${esc(name(m.start))} → ${esc(name(m.target))} · ${esc(m.label)}</option>`).join('');
function initials(i){return name(i).split(/[ -]/).map(w=>w[0]).slice(0,2).join('');}
function emblem(i,color='#fb4d93'){
  const spider=/Spider-Man|Spider-Woman|Silk/.test(name(i)),widow=/Black Widow/.test(name(i));
  return `<svg viewBox="0 0 100 100" aria-hidden="true"><defs><pattern id="dots-${i}" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#100821"/></pattern></defs><path d="M50 4 89 23 95 68 53 97 8 74 5 30Z" fill="${color}"/><path d="M50 10 84 27 87 64 51 89 15 70 13 34Z" fill="url(#dots-${i})"/><path d="M45 3 85 23 92 70 48 96 4 72 1 28Z" fill="none" stroke="#63eeee" stroke-width="2"/>${spider?'<path d="M20 31Q18 64 44 66L45 48Z M80 31Q82 64 56 66L55 48Z" fill="#fff5df" stroke="#150a23" stroke-width="4"/>':widow?'<path d="M33 23H67L56 50 67 77H33L44 50Z" fill="#150a23"/>':`<text x="50" y="64" text-anchor="middle" fill="#160d24" style="font:italic 40px Impact,sans-serif">${initials(i)}</text>`}</svg>`;
}
function layout(){
  const p=nodes.map((_,i)=>({x:450+Math.cos(i*2.39996)*Math.sqrt(i/N)*330,y:310+Math.sin(i*2.39996)*Math.sqrt(i/N)*215}));
  for(let k=0;k<180;k++){
    const dx=new Float64Array(N),dy=new Float64Array(N);
    for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){const x=p[i].x-p[j].x,y=p[i].y-p[j].y,d=x*x+y*y+30,f=170/d;dx[i]+=x*f;dy[i]+=y*f;dx[j]-=x*f;dy[j]-=y*f;}
    for(const [i,j]of DATA.edges){const x=p[j].x-p[i].x,y=p[j].y-p[i].y,d=Math.hypot(x,y)||1,f=(d-35)*.018;dx[i]+=x/d*f;dy[i]+=y/d*f;dx[j]-=x/d*f;dy[j]-=y/d*f;}
    for(let i=0;i<N;i++){p[i].x+=Math.max(-7,Math.min(7,dx[i]+(450-p[i].x)*.014))*(1-k/240);p[i].y+=Math.max(-7,Math.min(7,dy[i]+(300-p[i].y)*.02))*(1-k/240);}
  }
  const xs=p.map(x=>x.x),ys=p.map(x=>x.y),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
  return p.map(x=>({x:80+(x.x-xmin)/(xmax-xmin)*740,y:135+(x.y-ymin)/(ymax-ymin)*365}));
}
const positions=layout();let racePositions=positions.map(p=>({...p}));
function positionMission(){racePositions=positions.map(p=>({...p}));racePositions[mission.start]={x:170,y:265};racePositions[mission.target]={x:735,y:385};}
function bezier(a,b,p){const x=p[a],y=p[b],mx=(x.x+y.x)/2;return`M${x.x},${x.y} Q${mx},${(x.y+y.y)/2-25} ${y.x},${y.y}`;}
function strokePath(route,p){return route.slice(1).map((v,i)=>`<path d="${bezier(route[i],v,p)}"/>`).join('');}
function draw(){
  if(solution&&['replay','done'].includes(state)){drawBFS();return;}
  const replaying=frames.length>0&&['replay','done','searching','search-error'].includes(state),dist=replaying?frames[Math.min(ring,frames.length-1)].distance:null;
  let p=racePositions;
  if(replaying){
    p=positions.map(q=>({...q}));const maxDepth=Math.max(1,...(solution?.distance||frames.at(-1).distance).filter(d=>d>=0));
    const all=solution?.distance||frames.at(-1).distance;
    const groups=Array.from({length:maxDepth+1},()=>[]);all.forEach((d,i)=>{if(d>=0)groups[d].push(i);});
    p[mission.start]={x:450,y:310};
    groups.forEach((g,d)=>{if(!d)return;const r=65+(d-1)*Math.min(62,175/Math.max(1,maxDepth-1));g.forEach((id,k)=>{const a=k/g.length*Math.PI*2-.8+d*.31;p[id]={x:450+Math.cos(a)*r*1.55,y:310+Math.sin(a)*r*.86};});});
    all.forEach((d,i)=>{if(d<0){const a=i/N*Math.PI*2;p[i]={x:450+Math.cos(a)*400,y:310+Math.sin(a)*220};}});
  }
  const modeEdges=state==='idle'?DATA.edges:mode==='practice'?DATA.edges:[...known].flatMap(([i,links])=>links.map(j=>[i,j]));
  const routeNodes=new Set(path),algorithmShown=state==='done'&&solution?.path.length,algorithmNodes=new Set(algorithmShown?solution.path:[]);
  let svg='<title>Your directed route and the algorithm’s breadth-first search</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="#bf86b9"/></marker><marker id="pink-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="#fb4d93"/></marker><marker id="cyan-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="#62eeee"/></marker></defs>';
  if(replaying){
    for(let d=1;d<=ring;d++){const max=Math.max(1,frames.length-1),r=65+(d-1)*Math.min(62,175/Math.max(1,max-1));svg+=`<ellipse cx="450" cy="310" rx="${r*1.55}" ry="${r*.86}" fill="${d===ring?'#62eeee07':'none'}" stroke="#62eeee" stroke-width="${d===ring?2:1}" opacity="${d===ring?.5:.18}" stroke-dasharray="${d===ring?'none':'3 8'}"/><text x="${450+r*1.55-18}" y="310" fill="#62eeee" font-size="12">${d}</text>`;}
  }
  svg+='<g fill="none" stroke="#ae6caa" stroke-width=".65" opacity=".14">';
  for(const [a,b]of modeEdges)svg+=`<path d="${bezier(a,b,p)}" ${a===current&&!replaying?'marker-end="url(#arrow)"':''}/>`;
  svg+='</g>';
  if(replaying){const frame=frames[Math.min(ring,frames.length-1)];svg+='<g fill="none" stroke="#62eeee" stroke-width="1.2" opacity=".45" marker-end="url(#cyan-arrow)">';for(let i=0;i<N;i++)if(frame.parent[i]>=0)svg+=`<path d="${bezier(frame.parent[i],i,p)}"/>`;svg+='</g>';}
  else if(['playing','loading-page'].includes(state)){svg+='<g fill="none" stroke="#db8ace" stroke-width="1.6" opacity=".6" marker-end="url(#arrow)">';for(const v of currentLinks)svg+=`<path d="${bezier(current,v,p)}"/>`;svg+='</g>';}
  svg+=`<g fill="none" stroke="#fb4d93" stroke-width="4" marker-end="url(#pink-arrow)">${strokePath(path,p)}</g>`;
  if(algorithmShown)svg+=`<g fill="none" stroke="#62eeee" stroke-width="3" marker-end="url(#cyan-arrow)">${strokePath(solution.path,p)}</g>`;
  if(motion&&!reduceMotion.matches&&path.length>1)svg+=`<g fill="none" stroke="#fff4dd" stroke-width="2" stroke-dasharray="3 29" stroke-dashoffset="${-tick*3}">${strokePath(algorithmShown?solution.path:path,p)}</g>`;
  for(let i=0;i<N;i++){
    const reached=dist&&dist[i]>=0,active=reached||routeNodes.has(i),goal=i===mission.target,start=i===mission.start,focus=i===current&&!replaying,big=goal||start||focus;
    const color=goal?'#ffe579':algorithmNodes.has(i)||reached?'#62eeee':routeNodes.has(i)||start?'#fb4d93':'#84618f';
    const r=big?16:active?5:2+Math.sqrt(nodes[i].inDegree)*.4;
    if(big)svg+=`<circle cx="${p[i].x+3}" cy="${p[i].y+3}" r="${r+6}" fill="none" stroke="#fb4d93" stroke-width="1" opacity=".55"/><circle cx="${p[i].x-2}" cy="${p[i].y-2}" r="${r+6}" fill="none" stroke="#62eeee" stroke-width="1" opacity=".35"/>`;
    svg+=`<circle cx="${p[i].x}" cy="${p[i].y}" r="${r}" fill="${big?'#170f2a':color}" stroke="${big?color:'none'}" stroke-width="3" opacity="${active||big?1:.4}"><title>${esc(name(i))}${reached?' · '+dist[i]+' steps from start':''}</title></circle>`;
    if(big)svg+=`<text x="${p[i].x}" y="${p[i].y+5}" text-anchor="middle" fill="${color}" style="font-size:12px;font-weight:bold;stroke:none">${goal?'★':start?'S':'●'}</text>`;
    if(big||routeNodes.has(i)||algorithmNodes.has(i)){const short=name(i);svg+=`<text x="${p[i].x}" y="${p[i].y+r+22}" text-anchor="middle" fill="${color}" font-size="${big?17:12}" font-weight="${big?800:500}">${esc(short)}</text>`;}
  }
  $('network').innerHTML=svg;
}
function stopAuto(){clearInterval(autoTimer);autoTimer=0;$('auto').textContent='Auto-play';}
function clearRace(){epoch++;controller.abort();controller=new AbortController();stopAuto();api=null;path=[];cardIds=[];currentLinks=[];known=new Map();frames=[];solution=null;ring=0;won=false;cardsVersion++;viewPending.clear();for(const id of ['replay','results','link-section','retry','practice','article-link','show-results'])$(id).classList.add('hidden');$('links').innerHTML='';$('filter').value='';$('step').classList.remove('hidden');}
function idle(){clearRace();setStage('setup');state='idle';mission=chosen();mode=$('mode').value;current=mission.start;positionMission();$('destination-reminder').textContent=name(mission.target);$('start-name').textContent=name(mission.start);$('target-name').textContent=name(mission.target);$('destination-reminder').textContent=name(mission.target);$('current-name').textContent=name(mission.start);$('summary').textContent='Reach '+name(mission.target)+' using only outgoing links between Marvel hero articles. Your goal is fewer clicks, not a faster clock.';$('article-art').innerHTML=emblem(mission.start);$('status').textContent='';$('clicks').textContent='0';$('trail').innerHTML='<li>No clicks yet.</li>';$('graph-title').textContent='The universe is waiting.';$('graph-kicker').textContent='Your route. Your instincts.';$('mode-badge').textContent='Choose a mission to begin';$('start').disabled=false;$('restart').disabled=true;$('give-up').disabled=true;$('splash-caption').classList.remove('hidden');draw();}
async function begin(){
  clearRace();setStage('race');mission=chosen();mode=$('mode').value;current=mission.start;positionMission();state='loading';const e=epoch;
  $('start-name').textContent=name(mission.start);$('target-name').textContent=name(mission.target);$('destination-reminder').textContent=name(mission.target);$('current-name').textContent=name(current);$('article-art').innerHTML=emblem(current);$('start').disabled=true;$('restart').disabled=false;$('give-up').disabled=true;$('splash-caption').classList.add('hidden');$('clicks').textContent='0';$('trail').innerHTML='<li>Getting ready…</li>';
  $('mode-badge').textContent=mode==='live'?'Live Wikipedia · shared race cache':'Frozen practice · 26 Aug 2026';
  try{
    if(mode==='live'){api=WikiAPI.create(nodes,controller.signal);$('status').textContent='Opening Wikipedia and resolving the hero roster…';await api.init((n,total)=>{if(still(e))$('status').textContent=`Preparing live Wikipedia: ${n} / ${total} heroes resolved.`;});}
    if(!still(e))return;path=[mission.start];await showPage(e);
  }catch(err){if(!still(e))return;state='start-error';$('status').textContent='Live Wikipedia could not be loaded. Retry, or start a separate frozen-practice race.';$('retry').classList.remove('hidden');$('practice').classList.remove('hidden');$('summary').textContent=err.message;$('start').disabled=false;}
}
async function getLinks(id){
  const e=epoch,provider=api;const links=mode==='practice'?frozen[id]:(await provider.page(id)).links;if(still(e))known.set(id,links);return links;
}
function drawTrail(){ $('clicks').textContent=Math.max(0,path.length-1);$('trail').innerHTML=path.map(i=>`<li>${esc(name(i))}</li>`).join(''); }
async function showPage(e=epoch){
  state='loading-page';currentLinks=[];$('link-section').classList.add('hidden');$('retry').classList.add('hidden');$('practice').classList.add('hidden');$('give-up').disabled=true;$('filter').value='';$('current-name').textContent=name(current);$('article-art').innerHTML=emblem(current);$('status').textContent=mode==='live'?'Reading this article’s outgoing links…':'Opening the frozen article links…';$('summary').textContent='';drawTrail();draw();
  try{
    const info=mode==='practice'?{links:frozen[current],summary:nodes[current].summary}:await api.page(current);
    if(!still(e))return;known.set(current,info.links);currentLinks=info.links;
    $('summary').textContent=info.summary.length>520?info.summary.slice(0,517)+'…':info.summary;
    $('article-source').textContent=mode==='live'?'Live article':'Course snapshot';$('article-link').href=info.revision?`https://en.wikipedia.org/w/index.php?oldid=${info.revision}`:nodes[current].url;$('article-link').textContent=info.revision?'Read this Wikipedia revision ↗':'Read the current Wikipedia article ↗';$('article-link').classList.remove('hidden');
    state='playing';$('status').textContent=currentLinks.length?'Follow an article link below. Every click counts.':'Dead end: this article has no outgoing links to playable heroes. Restart, or let BFS find a route from the start.';
    $('start').disabled=false;$('give-up').disabled=false;$('link-section').classList.remove('hidden');$('graph-title').textContent='Where would you go next?';$('graph-note').textContent=mode==='live'?`${known.size} live articles read · bright arrows are this page’s outgoing links. Positions use the course layout.`:'Frozen directed graph · bright arrows are this page’s outgoing links.';renderLinks();draw();
  }catch(err){if(!still(e))return;state='page-error';$('status').textContent='This page could not be loaded. Your last move is kept; retry loading without adding another click.';$('retry').classList.remove('hidden');if(mode==='live')$('practice').classList.remove('hidden');$('start').disabled=false;}
}
function renderLinks(){
  const filter=$('filter').value.trim().toLowerCase(),links=currentLinks.filter(i=>name(i).toLowerCase().includes(filter)).sort((a,b)=>name(a).localeCompare(name(b)));
  $('link-count').textContent=currentLinks.length+' hero links';$('links').innerHTML=links.length?links.map(i=>`<button class="hero-link ${i===mission.target?'goal':''}" data-hero="${i}">${esc(name(i))}<span>${i===mission.target?'Finish!':'↗'}</span></button>`).join(''):'<p class="small">'+(currentLinks.length?'No matching hero links.':'No playable links on this page.')+'</p>';
}
async function move(id){if(state!=='playing'||!currentLinks.includes(id))return;path.push(id);current=id;sessionVisits.set(id,(sessionVisits.get(id)||0)+1);drawTrail();if(id===mission.target){won=true;$('current-name').textContent=name(id);$('article-art').innerHTML=emblem(id,'#ffe579');$('summary').textContent='Destination reached. Your route is locked in. Now BFS checks the same directed links.';$('link-section').classList.add('hidden');$('article-link').classList.add('hidden');await solve();}else await showPage();}
async function solve(){
  const e=epoch;setStage('bfs');state='searching';frames=[];solution=null;ring=0;stopAuto();$('replay').classList.remove('hidden');$('results').classList.add('hidden');$('link-section').classList.add('hidden');$('give-up').disabled=true;$('step').disabled=true;$('auto').disabled=true;$('replay-reset').disabled=true;$('retry-bfs').classList.add('hidden');$('status').textContent=won?'You made it. Let’s see what BFS finds.':'Your attempt is saved. BFS is taking over.';$('graph-kicker').textContent='Same links. A different strategy.';$('graph-title').textContent='Searching one ring at a time…';
  try{
    solution=await RaceGraph.search(N,mission.start,mission.target,getLinks,async frame=>{
      if(!still(e))return;frames.push(frame);$('bfs-status').textContent=`${mode==='live'?'Reading live pages. ':''}Discovered ${frame.distance.filter(x=>x>=0).length} heroes through distance ${frame.depth}.`;
    },controller.signal);
    if(!still(e))return;state='replay';ring=0;$('step').disabled=false;$('auto').disabled=false;$('replay-reset').disabled=false;renderReplay();$('replay').scrollIntoView({block:'start',behavior:reduceMotion.matches?'auto':'smooth'});
  }catch(err){if(!still(e))return;state='search-error';$('bfs-status').textContent='The live search is incomplete because a page request failed. This is not proof that the target is unreachable. Retry reuses pages already fetched.';$('retry-bfs').classList.remove('hidden');$('status').textContent='No shortest-path score until the search completes.';draw();}
}
function renderReplay(){
  $('step').classList.remove('hidden');$('show-results').classList.add('hidden');$('step').textContent=ring===0?'Explore the first ring':`Explore ring ${ring+1}`;
  $('ring-list').innerHTML=frames.map((f,i)=>`<button data-ring="${i}" class="${i===ring?'active':''} ${i>ring?'future':''}" aria-pressed="${i===ring}" ${i>ring?'disabled':''}><strong>${i===0?'Start':i+' '+(i===1?'click':'clicks')}</strong>${i<=ring?f.nodes.length+' discovered':'Not explored yet'}</button>`).join('');
  const frame=frames[ring],hit=frame.distance[mission.target]>=0;
  $('bfs-status').textContent=hit?`Target found at distance ${frame.distance[mission.target]}. Every earlier ring was searched first.`:`Ring ${ring}: ${frame.nodes.length} ${frame.nodes.length===1?'article':'articles'} discovered ${ring} ${ring===1?'click':'clicks'} from ${name(mission.start)}.`;
  $('replay-title').textContent=hit?`${name(mission.target)} found in ${frame.distance[mission.target]} clicks.`:ring===0?`Start at ${name(mission.start)}.`:`Every hero here is ${ring} clicks away.`;
  $('bfs-status').textContent=hit?'BFS checked every shorter distance first. That is why this route is guaranteed to use the fewest clicks.':ring===0?'Only the starting hero has been discovered. Next, follow all of its outgoing links together.':`BFS found ${frame.nodes.length} new heroes at this distance. Next, follow their outgoing links and ignore heroes already seen.`;
  $('graph-title').textContent=hit?'Shortest route found.':`BFS ring ${ring}`;$('graph-note').textContent='Rings encode shortest directed distance. The final ring stops once the target is found; some peers may remain undiscovered.';draw();
}
function nextRing(){if(!solution)return;if(ring<frames.length-1){ring++;renderReplay();}if(ring===frames.length-1){stopAuto();finish();}}
function autoplay(){if(autoTimer){stopAuto();return;}if(state==='done'){state='replay';ring=0;renderReplay();}if(reduceMotion.matches||!motion){ring=frames.length-1;renderReplay();finish();return;}$('auto').textContent='Pause BFS';autoTimer=setInterval(nextRing,1800);}
function finish(){
  state='done';stopAuto();$('show-results').classList.remove('hidden');$('step').classList.add('hidden');$('results').classList.remove('hidden');const shortest=solution.path.length?solution.path.length-1:null,clicks=path.length-1;
  $('result-title').textContent=shortest===null?'A one-way dead end.':won?(clicks===shortest?'You matched the machine.':'You got there. It found a shortcut.'):'The algorithm found a way.';
  $('result-copy').textContent=shortest===null?'BFS exhausted every reachable article in this race graph. The target cannot be reached by following its arrows.':won?`You took ${clicks} clicks. The shortest route takes ${shortest}.`:`Your unfinished attempt took ${clicks} clicks. BFS found a route of ${shortest}.`;
  $('score-stamp').innerHTML=shortest===null?'NO<br>ROUTE':won&&clicks===shortest?'PERFECT<br>ROUTE':won?`+${clicks-shortest}<br>CLICKS`:`${shortest}<br>CLICKS`;
  const chain=p=>p.map(i=>esc(name(i))).join(' <span aria-hidden="true">→</span> ');
  $('your-route').innerHTML=chain(path)+(won?'':' <em>(unfinished)</em>');$('algorithm-route').innerHTML=shortest===null?'Unreachable in the selected directed graph.':chain(solution.path);
  $('average-note').textContent=`Context: 2.67 links is the course’s undirected giant-component average, not a directed race benchmark. The frozen graph averages ${DATA.directedMean.toFixed(2)} links over reachable directed pairs${mode==='live'?'; this is not the live graph’s average':''}.`;
  const visits=[...sessionVisits].sort((a,b)=>b[1]-a[1]).slice(0,3);$('visit-note').textContent=visits.length?'Your most-visited heroes this tab: '+visits.map(([i,c])=>name(i)+' ('+c+')').join(', ')+'. This describes your play, not mathematical betweenness.':'No hero visits recorded yet. Human traffic and shortest-path betweenness are different measurements.';
  $('reverse-note').textContent='A route there does not promise a route back.';$('reverse').disabled=false;draw();
  const other=solution.path.slice(1,-1).sort((a,b)=>nodes[b].stats.betweenness-nodes[a].stats.betweenness)[0]??mission.target;
  if(!cardIds.length||cardIds[0]!==mission.start){cardIds=[mission.start,other];renderCards();}
}
async function reverseCheck(){
  const e=epoch;$('reverse').disabled=true;$('reverse-note').textContent='Checking the reverse direction on the same race graph…';
  try{const result=await RaceGraph.search(N,mission.target,mission.start,getLinks,()=>{},controller.signal);if(!still(e))return;$('reverse-note').textContent=result.path.length?`${name(mission.target)} → ${name(mission.start)} takes ${result.path.length-1} clicks. ${result.path.map(name).join(' → ')}`:`${name(mission.target)} cannot reach ${name(mission.start)}. Every reachable article was checked; the arrows make this journey one-way.`;}
  catch{if(still(e)){$('reverse-note').textContent='The reverse search could not finish. Reachability is unknown; retry the check.';$('reverse').disabled=false;}}
}
const statLabels={degree:'Degree',closeness:'Closeness',harmonic:'Harmonic',betweenness:'Betweenness',eigenvector:'Eigenvector',pagerank:'PageRank',pageviews:'Monthly pageviews'};
const fmt=(stat,v)=>v===null?'Unavailable':stat==='degree'||stat==='pageviews'?v.toLocaleString('en'):v.toFixed(4);
function value(id,stat){return stat==='pageviews'?viewCache.get(id)?.value??null:nodes[id].stats[stat];}
function cardMarkup(id,side){
  const liveSummary=api?.pages.get(id)?.summary,summary=(liveSummary||nodes[id].summary).split(/(?<=[.!?])\s/)[0];
  const views=viewCache.get(id),pageSource=api?.pages.get(id);
  return `<article class="hero-card"><div class="card-head"><label class="sr-only" for="card-${side}">Hero on card ${side+1}</label><select id="card-${side}" data-card="${side}">${heroOptions}</select>${emblem(id,side?'#62eeee':'#fb4d93')}<h3>${esc(name(id))}</h3></div><p class="card-summary">${esc(summary||'A Marvel hero article in the course roster.')}</p>${Object.entries(statLabels).map(([key,label])=>`<button class="stat" data-stat="${key}" data-side="${side}" ${key==='pageviews'&&value(id,key)===null?'disabled':''}><span>${label}</span><strong>${key==='pageviews'&&!views?'Loading…':fmt(key,value(id,key))}</strong></button>`).join('')}<div class="card-foot">Network stats: 26 Aug 2026. Pageviews: ${esc(views?.month||WikiAPI.lastMonth().label)} · ${views?.value===null?'API unavailable':views?'Wikimedia, live fetched':'fetching…'}.<br><a href="${esc(pageSource?.revision?'https://en.wikipedia.org/w/index.php?oldid='+pageSource.revision:nodes[id].url)}" target="_blank" rel="noopener">Wikipedia summary source ↗</a></div></article>`;
}
function renderCards(){
  cardsVersion++;const version=cardsVersion,e=epoch;
  $('cards').innerHTML=cardIds.map(cardMarkup).join('');cardIds.forEach((id,i)=>$('card-'+i).value=id);$('battle-result').textContent='Pick a stat on either card to play.';
  for(const id of new Set(cardIds))if(!viewCache.has(id)&&!viewPending.has(id)){
    viewPending.add(id);
    WikiAPI.pageviews(api?.canonical[id]||nodes[id].title,controller.signal).then(v=>{if(still(e))viewCache.set(id,v);}).catch(()=>{if(still(e))viewCache.set(id,{value:null,month:WikiAPI.lastMonth().label});}).finally(()=>{if(still(e)){viewPending.delete(id);if(cardIds.includes(id))renderCards();}});
  }
}
function battle(stat){
  const [a,b]=cardIds,va=value(a,stat),vb=value(b,stat);if(va===null||vb===null){$('battle-result').textContent='Both cards need available values for this comparison.';return;}
  document.querySelectorAll('.stat').forEach(e=>e.classList.remove('winner','loser'));
  const winner=va>vb?0:vb>va?1:-1;
  document.querySelectorAll(`[data-stat="${stat}"]`).forEach(e=>e.classList.add(winner<0||+e.dataset.side===winner?'winner':'loser'));
  $('battle-result').textContent=winner<0?`${statLabels[stat]}: a tie. Try another definition of importance.`:`${name(cardIds[winner])} wins on ${statLabels[stat].toLowerCase()}: ${fmt(stat,Math.max(va,vb))} vs ${fmt(stat,Math.min(va,vb))}. Now pick another stat.`;
}
$('start').onclick=begin;$('restart').onclick=begin;$('again').onclick=()=>{begin();$('mission').scrollIntoView({behavior:reduceMotion.matches?'auto':'smooth',block:'start'});};
$('mission').onchange=idle;$('mode').onchange=idle;$('filter').oninput=renderLinks;
$('links').onclick=e=>{const b=e.target.closest('[data-hero]');if(b)move(+b.dataset.hero);};
$('retry').onclick=()=>state==='start-error'?begin():showPage();$('practice').onclick=()=>{$('mode').value='practice';begin();};
$('give-up').onclick=()=>{won=false;solve();};$('retry-bfs').onclick=solve;$('step').onclick=nextRing;$('auto').onclick=autoplay;
$('replay-reset').onclick=()=>{stopAuto();state='replay';ring=0;renderReplay();};
$('ring-list').onclick=e=>{const b=e.target.closest('[data-ring]');if(!b)return;stopAuto();ring=+b.dataset.ring;state='replay';renderReplay();if(ring===frames.length-1)finish();};
$('reverse').onclick=reverseCheck;$('change-mission').onclick=idle;$('show-results').onclick=()=>{setStage('results');$('results').scrollIntoView({block:'start',behavior:reduceMotion.matches?'auto':'smooth'});};$('back-bfs').onclick=()=>{setStage('bfs');ring=0;state='replay';renderReplay();};$('cards').onchange=e=>{if(e.target.matches('[data-card]')){cardIds[+e.target.dataset.card]=+e.target.value;renderCards();}};
$('cards').onclick=e=>{const b=e.target.closest('[data-stat]');if(b)battle(b.dataset.stat);};
$('soundless-motion').onclick=()=>{motion=!motion;$('soundless-motion').setAttribute('aria-pressed',!motion);$('soundless-motion').textContent=motion?'Pause motion':'Resume motion';if(!motion)stopAuto();draw();};
reduceMotion.addEventListener('change',()=>{if(reduceMotion.matches)stopAuto();draw();});
let lastTick=0;function animate(now){if(now-lastTick>100){lastTick=now;if(motion&&!reduceMotion.matches&&path.length>1){tick++;draw();}}requestAnimationFrame(animate);}requestAnimationFrame(animate);
idle();

function setStage(stage){document.body.dataset.stage=stage;const active=stage==='bfs'?'stage-bfs':stage==='results'?'stage-cards':'stage-race';for(const id of ['stage-race','stage-bfs','stage-cards']){if(id===active)$(id).setAttribute('aria-current','step');else $(id).removeAttribute('aria-current');}$('change-mission').classList.toggle('hidden',stage==='setup');}
