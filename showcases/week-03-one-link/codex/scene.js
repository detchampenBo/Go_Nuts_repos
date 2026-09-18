// PROTOTYPE scene: comic-print composition around actual sampled shortest routes.
let scenePositions=[],sampled=[],sceneOld=new Map(),sceneNew=new Map(),sceneNodes=new Set(),mobileScene=false;
function addTracks(map,path){for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i],k=key(a,b);if(!map.has(k))map.set(k,{a,b,count:0});map.get(k).count++;}}
function viaBroker(a,b){
  if(Graph.share(before,a,b,broker)>0)return [...Graph.path(baseAdj,a,broker).slice(0,-1),...Graph.path(baseAdj,broker,b)];
  return Graph.path(baseAdj,a,b);
}
function viaBypass(a,b){
  for(const [x,y] of [[u,v],[v,u]])if(after.distances[a][x]+1+after.distances[y][b]===after.distances[a][b])return [...Graph.path(afterAdj,a,x),...Graph.path(afterAdj,y,b)];
  return Graph.path(afterAdj,a,b);
}
function buildScene(){
  mobileScene=innerWidth<=650;
  const candidates=comparison.journeys,limit=Math.min(32,candidates.length),chosen=new Set();
  sampled=[];sceneOld=new Map();sceneNew=new Map();sceneNodes=new Set([broker,u,v]);
  // Evenly spaced through the sorted affected-pair list: illustrative, not random.
  for(let i=0;i<limit;i++){const j=candidates[Math.floor(i*candidates.length/limit)];const k=key(j.s,j.t);if(chosen.has(k))continue;chosen.add(k);const old=viaBroker(j.s,j.t),next=viaBypass(j.s,j.t);sampled.push({old,next});addTracks(sceneOld,old);addTracks(sceneNew,next);old.forEach(x=>sceneNodes.add(x));next.forEach(x=>sceneNodes.add(x));}
  // Keep every article visible; separate the featured broker and endpoints spatially.
  scenePositions=globalPositions.map(p=>mobileScene?{x:35+(p.x-50)/760*340,y:125+(p.y-40)/350*220}:{x:60+(p.x-50)/760*520,y:115+(p.y-40)/350*390});
  const anchor=mobileScene?[{x:100,y:420},{x:305,y:535},{x:315,y:375}]:[{x:740,y:180},{x:1050,y:320},{x:710,y:460}];
  [broker,u,v].forEach((id,i)=>scenePositions[id]=anchor[i]);
}
function curve(a,b,p){
  const x=p[a],y=p[b];
  if(mobileScene&&!full){const mid=(x.y+y.y)/2;return `M${x.x},${x.y} C${x.x},${mid} ${y.x},${mid} ${y.x},${y.y}`;}
  const mid=(x.x+y.x)/2;return `M${x.x},${x.y} C${mid},${x.y} ${mid},${y.y} ${y.x},${y.y}`;
}
function longCurve(path,p){return path.slice(1).map((b,i)=>curve(path[i],b,p)).join(' ');}
function glyph(id,x,y,r,color){
  const label=name(id).toLowerCase();
  if(label.includes('spider-man'))return `<g transform="translate(${x},${y}) scale(${r/40})"><path d="M-22,-17 Q-24,4 -6,12 L-2,-1 Z M22,-17 Q24,4 6,12 L2,-1 Z" fill="#f9f6ea" stroke="#111024" stroke-width="3"/><path d="M0,-34 V-8 M0,14 V34 M-30,-4 L-9,-1 M30,-4 L9,-1 M-23,24 L-8,10 M23,24 L8,10" fill="none" stroke="${color}" stroke-width="1" opacity=".5"/></g>`;
  if(label.includes('black widow'))return `<path d="M${x-13},${y-19} L${x+13},${y-19} L${x+5},${y} L${x+13},${y+19} L${x-13},${y+19} L${x-5},${y} Z" fill="${color}"/>`;
  return `<text x="${x}" y="${y+8}" text-anchor="middle" style="font:bold 25px Impact,sans-serif;stroke:none;fill:${color}">${escape(name(id).split(' ').map(w=>w[0]).slice(0,2).join(''))}</text>`;
}
function render(){
  const f=phase/100,p=full?globalPositions:scenePositions,W=full?860:mobileScene?420:1200,H=full?460:mobileScene?730:610;
  $('phase').textContent=phase===0?'Before':phase===100?'After':`Transition · ${phase}%`;
  $('map-title').textContent=phase<50?'Every broker needs a bottleneck.':'The web finds another way.';
  $('map-caption').textContent=full?`${N} articles · ${DATA.edges.length} original links · selected journey highlighted`:`${sampled.length} affected pairs in motion · all ${N} articles visible · schematic positions`;
  const pct=100*(before.b[broker]-after.b[broker])/before.b[broker];
  $('scene-note').classList.toggle('after-note',phase>=50);
  $('scene-note').innerHTML=phase<50?`<strong>One new link.</strong>Drag the slider. Watch the routes find a way around ${escape(name(broker))}.`:`<strong>−${pct.toFixed(1)}% brokerage.</strong>Same heroes. A different balance of importance.`;
  $('scene-note').classList.toggle('hidden',full);
  const selected=new Set([...oldPath,...newPath]),scale=full?.58:1;
  let svg=`<title>Shortest routes rerouting around ${escape(name(broker))}</title><defs><pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#080615"/></pattern><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter></defs>`;
  if(!full){
    // Printed shadow disks and offset contour rings distinguish the featured stations.
    for(const [id,c] of [[broker,'#ffdf6c'],[v,'#50eced']]){
      const {x,y}=p[id],rr=id===broker?91-20*f:78+18*f;
      svg+=`<circle cx="${x+5}" cy="${y+4}" r="${rr}" fill="${c}" opacity=".035"/><circle cx="${x+5}" cy="${y+4}" r="${rr}" fill="url(#dots)" opacity=".6"/><circle cx="${x-3}" cy="${y+3}" r="${rr}" fill="none" stroke="#fa468e" stroke-width="1" opacity=".3"/><circle cx="${x+3}" cy="${y-2}" r="${rr-4}" fill="none" stroke="${c}" stroke-width="1" opacity=".2"/>`;
    }
  }
  svg+='<g aria-hidden="true">';
  for(const [a,b]of DATA.edges)svg+=`<path d="${full?line(a,b,p):curve(a,b,p)}" fill="none" stroke="#786088" stroke-width="${full?.65:.7}" opacity="${full?.22:.12}"/>`;
  svg+='</g>';
  if(!full){
    for(const [tracks,color,opacity]of [[sceneOld,'#ffdd6a',1-f*.93],[sceneNew,'#54edef',f]]){
      for(const {a,b,count}of tracks.values()){
        const width=.6+Math.sqrt(count)*1.2,d=curve(a,b,p);
        svg+=`<path d="${d}" class="route" stroke="${color}" stroke-width="${width}" opacity="${opacity*.48}"/>`;
        if(count>=4)svg+=`<path d="${d}" class="route" stroke="${color}" stroke-width="${width+5}" opacity="${opacity*.07}"/>`;
      }
    }
    // Marks advance along actual edges during a user-driven transition.
    for(let j=0;j<sampled.length;j++){
      const old=sampled[j].old,next=sampled[j].next;
      for(const [path,color,opacity]of [[old,'#ffe77e',1-f],[next,'#81ffff',f]]){
        svg+=`<path d="${longCurve(path,p)}" class="route" stroke="${color}" stroke-width="1.8" stroke-dasharray="2 65" style="stroke-dashoffset:${-phase*5-j*9}" opacity="${opacity*.8}"/>`;
      }
    }
  }
  const edge=full?line(u,v,p):curve(u,v,p),start=newPath[0],end=newPath[newPath.length-1];
  svg+=`<path d="${edge}" fill="none" stroke="#f34c9a" stroke-width="${full?5:10}" opacity="${f*.4}" transform="translate(2,2)"/>`;
  svg+=`<path d="${edge}" class="route" stroke="#54edef" stroke-width="${full?2:4}" stroke-dasharray="${phase===100?'none':'9 9'}" opacity="${.13+.87*f}"/>`;
  const oldD=full?routeD(oldPath,p):longCurve(oldPath,p),newD=full?routeD(newPath,p):longCurve(newPath,p);
  svg+=`<path d="${oldD}" class="route" stroke="#ffe16b" stroke-width="${full?2:2.8}" opacity="${1-f*.85}"/><path d="${newD}" class="route" stroke="#bdffff" stroke-width="${full?2:3}" opacity="${f}"/>`;
  for(let id=0;id<N;id++){
    if([broker,u,v].includes(id))continue;
    const active=sceneNodes.has(id),sel=selected.has(id),{x,y}=p[id],r=(full?1.7:2.1)+Math.sqrt(before.b[id])*18;
    svg+=`<g class="station" data-id="${id}" role="button" tabindex="-1" aria-label="${escape(name(id))}; choose as bypass endpoint"><title>${escape(name(id))}</title><circle cx="${x}" cy="${y}" r="${Math.max(r,7)}" fill="transparent"/><circle class="node-disc" cx="${x}" cy="${y}" r="${r}" fill="${sel?'#ffdf79':active?'#b998b9':'#665176'}" opacity="${active||full?'.85':'.45'}" stroke="${sel?'#ffdf79':'#160d28'}" stroke-width="1"/>`;
    if(sel&&!full)svg+=`<text x="${x+9}" y="${y-7}" style="font-size:${mobileScene?10:12}px;fill:#ebd9e8">${escape(name(id))}</text>`;
    svg+='</g>';
  }
  for(const [id,color,role]of [[broker,'#ffe16b','The broker'],[u,'#d9a5d8','Bypass endpoint'],[v,'#54edef','Bypass endpoint']]){
    const {x,y}=p[id],base=before.b[id],score=base*(1-f)+after.b[id]*f;
    const r=full?7+Math.sqrt(score)*22:(id===broker?39:34)*Math.sqrt(base>0?Math.max(.35,score/base):1);
    svg+=`<g class="station" data-id="${id}" role="button" tabindex="0" aria-label="${escape(name(id))}; choose as bypass endpoint"><title>${escape(name(id))}: ${(base*100).toFixed(3)}% before, ${(after.b[id]*100).toFixed(3)}% after</title><circle cx="${x+3}" cy="${y+3}" r="${r+4}" fill="none" stroke="#f74691" stroke-width="2"/><circle class="node-disc" cx="${x}" cy="${y}" r="${r}" fill="#140e2a" stroke="${color}" stroke-width="3"/>`;
    if(!full)svg+=glyph(id,x,y,r,color);
    const labelY=y+r+(full?18:27);
    svg+=`<text x="${x}" y="${labelY}" text-anchor="middle" style="font-family:Impact,'Arial Narrow',sans-serif;font-style:italic;font-size:${full?14:mobileScene?21:28}px;fill:${color};stroke-width:6">${escape(name(id).toUpperCase())}</text>`;
    if(!full)svg+=`<text x="${x}" y="${labelY+19}" text-anchor="middle" style="font-size:${mobileScene?10:12}px;fill:#b7a2c4">${role}${id===broker?' · '+(score*100).toFixed(2)+'% betweenness':''}</text>`;
    svg+='</g>';
  }
  $('map').setAttribute('viewBox',`0 0 ${W} ${H}`);$('map').innerHTML=svg;
}
