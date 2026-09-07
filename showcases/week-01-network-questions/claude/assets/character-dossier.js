/* Persistent, keyboard-accessible article dossier. Remote text is never HTML. */
(() => {
  const cache=new Map();let request=0,returnFocus=null;
  const panel=document.createElement('aside');panel.className='character-dossier';panel.hidden=true;
  panel.setAttribute('aria-labelledby','dossier-name');
  panel.innerHTML='<div class="dossier-top"><span>CHARACTER DOSSIER / WIKIPEDIA</span><button type="button" aria-label="Close character dossier">×</button></div><div class="dossier-art"><img alt="" hidden><span class="dossier-monogram" aria-hidden="true"></span><span class="dossier-stamp">ARTICLE IDENTIFIED</span></div><div class="dossier-body"><h2 id="dossier-name"></h2><p class="dossier-group"></p><div class="dossier-stats"></div><p class="dossier-bio" aria-live="polite"></p><a class="dossier-wiki" target="_blank" rel="noopener noreferrer">Read the full Wikipedia article ↗</a><p class="dossier-credit">Summary and image: Wikipedia. Link counts: frozen course snapshot.</p></div>';
  document.body.append(panel);const q=s=>panel.querySelector(s),image=q('img');
  function hide(){request++;panel.hidden=true;document.body.classList.remove('dossier-open');if(returnFocus?.isConnected)returnFocus.focus({preventScroll:true});}
  q('button').addEventListener('click',hide);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!panel.hidden)hide();});
  function safeImage(url){try{const u=new URL(url,location.href);return (u.protocol==='https:'&&u.hostname==='upload.wikimedia.org') || u.origin===location.origin;}catch{return false;}}
  function setImage(url,name){image.hidden=true;q('.dossier-monogram').hidden=false;if(!url||!safeImage(url))return;image.alt=name;image.onload=()=>{image.hidden=false;q('.dossier-monogram').hidden=true;};image.onerror=()=>{image.hidden=true;q('.dossier-monogram').hidden=false;};image.src=url;}
  window.characterSummary = id => {
    if(!cache.has(id))cache.set(id,fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(id),{signal:AbortSignal.timeout(8000)}).then(r=>r.ok?r.json():null).catch(()=>null));
    return cache.get(id);
  };
  window.showCharacterDossier = async (d, source) => {
    const explorer=document.body.classList.contains('explorer-page');
    const anchor=explorer?document.querySelector('.hud .field'):source?.closest('.rec-controls, .balance-controls');
    if(anchor)anchor.insertAdjacentElement('afterend',panel);
    if(explorer && matchMedia('(max-width: 700px)').matches){
      document.body.classList.add('controls-open');
      const toggle=document.getElementById('ui-toggle');
      if(toggle){toggle.textContent='Close controls';toggle.setAttribute('aria-expanded','true');}
    }
    const token=++request;returnFocus=document.activeElement;panel.hidden=false;document.body.classList.add('dossier-open');
    const name=d.name||d.id.replaceAll('_',' '),id=d.id||name.replaceAll(' ','_');
    q('#dossier-name').textContent=name;q('.dossier-group').textContent=d.commLabel||d.group||'Marvel Wikipedia article';
    q('.dossier-monogram').textContent=name.split(/[\s-]+/).slice(0,2).map(w=>w[0]).join('').toUpperCase();
    const local=window.rosterPortraits?.find(p=>name===p.name||name.startsWith(p.name+' ('));
    setImage(local?.src,name);q('.dossier-bio').textContent='Opening the Wikipedia dossier…';
    const stats=q('.dossier-stats');stats.replaceChildren();
    for(const [label,value] of [['Incoming',d.in??d.incoming],['Outgoing',d.out??d.outgoing]])if(Number.isFinite(value)){
      const box=document.createElement('div'),number=document.createElement('strong'),caption=document.createElement('span');number.textContent=value;caption.textContent=label;box.append(number,caption);stats.append(box);
    }
    q('.dossier-wiki').href='https://en.wikipedia.org/wiki/'+encodeURIComponent(id);
    const summary=await window.characterSummary(id);if(token!==request||panel.hidden)return;
    if(summary?.thumbnail?.source)setImage(summary.thumbnail.source,name);
    const text=summary?.extract||summary?.description;
    q('.dossier-bio').textContent=text?(text.length>450?text.slice(0,447).replace(/\s+\S*$/,'')+'…':text):'The live introduction is unavailable. You can still explore the saved link statistics or open the Wikipedia article.';
  };
  document.addEventListener('change',e=>{
    const select=e.target;if(select.id==='rec-article'&&typeof reciprocityData!=='undefined'){
      const d=reciprocityData.nodes[Number(select.value)];if(d)window.showCharacterDossier(d,select);
    }else if(select.id==='balance-hero'&&typeof balanceArticles!=='undefined'){
      const d=balanceArticles.find(n=>n.id===select.value||n.name===select.selectedOptions[0]?.textContent);if(d)window.showCharacterDossier(d,select);
    }
  });
})();
