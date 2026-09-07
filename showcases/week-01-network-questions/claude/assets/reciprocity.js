(() => {
  const data=reciprocityData;
  const svg=document.getElementById('rec-map');
  const toggle=document.getElementById('rec-toggle');
  const select=document.getElementById('rec-article');
  function el(tag,attrs={},text){
    const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));
    if(text!==undefined)e.textContent=text;
    return e;
  }
  svg.append(el('title',{id:'rec-map-title'},'Marvel references with and without one-way connections'));
  const desc=el('desc',{id:'rec-map-desc'});svg.append(desc);
  const edges=el('g');svg.append(edges);
  data.edges.forEach(e=>{
    const a=data.nodes[e.a],b=data.nodes[e.b];
    edges.append(el('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:e.mutual?'#74e5e3':'#f39b83','stroke-width':.8,class:e.mutual?'mutual':'one-way'}));
  });
  svg.append(el('text',{x:760,y:125,fill:'#b4ccd1','font-size':12},'The 9-node island'));
  svg.append(el('text',{x:760,y:315,fill:'#b4ccd1','font-size':12},'17 original isolates'));
  const circles=data.nodes.map((n,i)=>{
    const c=el('circle',{cx:n.x,cy:n.y,r:Math.sqrt(6+(n.incoming+n.outgoing)*.65),stroke:'#071e25','stroke-width':.8});
    c.append(el('title',{},`${n.name}: ${n.incoming} inbound, ${n.outgoing} outbound, ${n.mutual} mutual neighbours`));
    c.addEventListener('click',()=>{select.value=String(i);render();});
    svg.append(c);return c;
  });
  const ring=el('circle',{fill:'none',stroke:'#fff','stroke-width':1.8,'pointer-events':'none'});svg.append(ring);
  [...data.nodes.keys()].sort((a,b)=>data.nodes[a].name.localeCompare(data.nodes[b].name)).forEach(i=>{
    const o=document.createElement('option');o.value=String(i);o.textContent=data.nodes[i].name;select.append(o);
  });
  select.value=String(data.nodes.findIndex(n=>n.id==='Shamrock_(comics)'));
  function render(){
    const filtered=toggle.checked, m=filtered?data.reciprocal:data.full;
    svg.classList.toggle('mutual-only',filtered);
    document.getElementById('rec-largest').textContent=m.largest;
    document.getElementById('rec-isolates').textContent=m.isolates;
    document.getElementById('rec-connections').textContent=(filtered?data.retained:data.connections).toLocaleString('en-US');
    circles.forEach((c,i)=>{const n=data.nodes[i];c.setAttribute('fill',n.isolated?'#758b93':filtered&&n.mutual===0?'#d8ff70':'#74e5e3');});
    const n=data.nodes[Number(select.value)];
    ring.setAttribute('cx',n.x);ring.setAttribute('cy',n.y);ring.setAttribute('r',Math.sqrt(6+(n.incoming+n.outgoing)*.65)+4);
    document.getElementById('rec-detail').textContent=`${n.name} · ${n.incoming} inbound / ${n.outgoing} outbound · ${n.mutual} mutual neighbours. ${n.isolated?'Already isolated in the full snapshot.':n.mutual===0?'Becomes isolated when one-way connections are removed.':'Retains at least one connection under the mutual-only rule.'}`;
    desc.textContent=`${filtered?'Mutual-only':'Full'} graph: ${m.largest} articles in the largest component and ${m.isolates} isolates. All positions are unchanged.`;
  }
  function distribution(key){
    const chart=document.getElementById(`rec-dist-${key}`), values=data.trials.map(t=>t[key]);
    const observed=data.reciprocal[key];
    const lo=Math.min(observed,...values)-3,hi=Math.max(observed,...values)+3;
    const counts=new Map();values.forEach(v=>counts.set(v,(counts.get(v)||0)+1));
    const max=Math.max(...counts.values()),x=v=>35+(v-lo)/(hi-lo)*305;
    chart.setAttribute('viewBox','0 0 365 225');
    chart.append(el('title',{},`${key==='largest'?'Largest component':'Isolate count'}: mutual-only ${observed}; 500 random trials range from ${Math.min(...values)} to ${Math.max(...values)}.`));
    chart.append(el('text',{x:35,y:15,fill:'#b4ccd1','font-size':11},'Number of random trials'));
    for(const level of [0,max]){
      const y=175-level/max*130;
      chart.append(el('line',{x1:35,x2:340,y1:y,y2:y,stroke:'#36525a'}));
      chart.append(el('text',{x:29,y:y+4,fill:'#b4ccd1','text-anchor':'end','font-size':10},level));
    }
    for(const [v,count] of counts){
      const bar=el('rect',{x:x(v)-305/(hi-lo)*.42,y:175-count/max*130,width:305/(hi-lo)*.84,height:count/max*130,fill:'#568f9c'});
      bar.append(el('title',{},`${v} articles: ${count} trials`));chart.append(bar);
    }
    chart.append(el('line',{x1:x(observed),x2:x(observed),y1:30,y2:177,stroke:'#d8ff70','stroke-width':2}));
    chart.append(el('text',{x:x(observed),y:26,fill:'#d8ff70','text-anchor':'middle','font-size':11},`actual ${observed}`));
    for(let v=Math.ceil(lo/10)*10;v<=hi;v+=10)chart.append(el('text',{x:x(v),y:194,fill:'#b4ccd1','text-anchor':'middle','font-size':11},v));
    chart.append(el('text',{x:187,y:218,fill:'#b4ccd1','text-anchor':'middle','font-size':11},key==='largest'?'Articles in largest component':'Isolated articles'));
  }
  toggle.addEventListener('change',render);select.addEventListener('change',render);
  render();distribution('largest');distribution('isolates');
})();
