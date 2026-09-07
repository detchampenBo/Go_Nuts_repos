(() => {
  const groups=window.communityRoster, grid=document.getElementById('roster-grid');
  const status=document.getElementById('roster-status'), full=document.getElementById('roster-full'), toggle=document.getElementById('roster-toggle');
  if(!groups || !grid) return;
  let selected=null;
  const panels=[];
  function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;}
  function svgEl(tag,attrs,text){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
  function network(group){
    const s=svgEl('svg',{viewBox:'0 0 400 240','aria-hidden':'true',class:'roster-mini'});
    group.edges.forEach(([a,b])=>{const n=group.nodes[a],m=group.nodes[b];s.append(svgEl('line',{x1:n.x,y1:n.y,x2:m.x,y2:m.y,stroke:group.color,'stroke-opacity':.24,'stroke-width':.8}));});
    [...group.nodes].sort((a,b)=>b.degree-a.degree).forEach(n=>{const c=svgEl('circle',{cx:n.x,cy:n.y,r:Math.sqrt(4+n.degree*.45),fill:group.color,stroke:'#101721','stroke-width':1});c.append(svgEl('title',{},`${n.name} · ${n.degree} total links`));s.append(c);});return s;
  }
  function detail(group){
    const box=el('div','roster-detail');box.id=`roster-detail-${group.id}`;
    box.append(el('h3','', 'Across the panels'));
    box.append(el('p','roster-detail-intro','Directed links between this group and the other communities. Each count is an article-to-article link.'));
    const rows=groups.filter(g=>g.id!==group.id).map(g=>({g,incoming:group.incoming[g.id],outgoing:group.outgoing[g.id]})).sort((a,b)=>(b.incoming+b.outgoing)-(a.incoming+a.outgoing));
    const max=Math.max(1,...rows.map(r=>r.incoming+r.outgoing));
    const list=el('div','roster-connections');
    rows.forEach(r=>{
      const row=el('div','roster-connection');row.style.setProperty('--destination',r.g.color);
      row.append(el('span','roster-destination',r.g.name));
      const bar=el('span','roster-bar');bar.setAttribute('aria-hidden','true');const fill=el('span');fill.style.width=`${100*(r.incoming+r.outgoing)/max}%`;bar.append(fill);row.append(bar);
      row.append(el('span','roster-count',`${r.incoming} in · ${r.outgoing} out`));list.append(row);
    });box.append(list);
    const top=[...group.nodes].sort((a,b)=>b.degree-a.degree).slice(0,3);
    box.append(el('p','roster-featured','Highest total degree: '+top.map(n=>`${n.name.replace(/ \([^)]*\)/g,'')} (${n.degree})`).join(' · ')));
    const portrait=window.rosterPortraits?.find(p=>p.id===group.id);
    if(portrait){const credit=el('p','roster-image-credit');const source=el('a','',`${portrait.name} image via Wikipedia`);source.href=portrait.article;const original=el('a','','Image source');original.href=portrait.imageSource;credit.append(source,document.createTextNode(' · '),original);box.append(credit);}
    const link=el('a','roster-explore','Explore all article links ↗');link.href='explorer.html';box.append(link);
    return box;
  }
  function select(id){
    selected=selected===id?null:id;
    panels.forEach(({article,button,body,group})=>{
      const active=selected===group.id;article.classList.toggle('expanded',active);button.setAttribute('aria-expanded',String(active));body.hidden=!active;
      button.querySelector('.roster-open').textContent=active?'Close dossier −':'Follow the links ↗';
    });
    status.textContent=selected===null?'Choose a panel to uncover its connections to the other groups.':`${groups.find(g=>g.id===selected).name} expanded. Connection counts appear below its network.`;
  }
  groups.forEach(group=>{
    const article=el('article','roster-panel');article.style.setProperty('--team',group.color);
    const button=el('button','roster-cover');button.type='button';button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls',`roster-detail-${group.id}`);
    button.setAttribute('aria-label',`${group.name}, ${group.nodes.length} articles. Show connections.`);
    const captions=['Meanwhile, among the X-Men…','Somewhere in the cosmos…','Across the gamma divide…','Within the Spider-family…','Down at street level…','Beyond the ordinary…','Back with the Avengers…','On the streets, together…'];
    const head=el('span','roster-panel-top');head.append(el('span','roster-issue',`0${group.id+1}`),el('span','roster-size',`${group.nodes.length} ARTICLES`));button.append(head);
    button.append(el('span','roster-name',group.name));
    const portrait=window.rosterPortraits?.find(p=>p.id===group.id);
    if(portrait){
      const frame=el('span','roster-portrait');const image=el('img');image.src=portrait.src;image.alt=portrait.name;image.loading='lazy';image.decoding='async';
      frame.append(image,el('span','roster-narration',captions[group.id]),el('span','roster-character-name',portrait.name));button.append(frame);
    }
    const map=el('span','roster-network-inset');map.append(el('span','roster-network-caption','INSIDE THEIR WORLD'),network(group));button.append(map);
    const bottom=el('span','roster-panel-bottom');bottom.append(el('span','roster-link-count',`${group.edges.length} links inside this community`),el('span','roster-open','Follow the links ↗'));button.append(bottom);
    const body=detail(group);body.hidden=true;button.addEventListener('click',()=>select(group.id));article.append(button,body);grid.append(article);panels.push({article,button,body,group});
    const li=el('li','',`0${group.id+1} / ${group.name}`);li.style.setProperty('--team',group.color);document.getElementById('roster-full-legend').append(li);
  });
  toggle.addEventListener('click',()=>{const show=full.hidden;full.hidden=!show;grid.hidden=show;toggle.setAttribute('aria-pressed',String(show));toggle.textContent=show?'Back to comic panels ↙':'Show full network ↗';status.textContent=show?'All eight communities together. Numbers match the legend below.':'Choose a panel to uncover its connections to the other groups.';if(!show&&selected!==null)status.textContent=`${groups.find(g=>g.id===selected).name} is still expanded.`;});
})();
