// Read-only Wikipedia adapter. A race pins each page's links to its first fetch.
const WikiAPI=(()=>{
  const endpoint='https://en.wikipedia.org/w/api.php';
  const normalize=s=>s.replaceAll('_',' ').normalize('NFC');
  async function json(url,signal){
    const controller=new AbortController(),abort=()=>controller.abort();
    if(signal?.aborted)throw new DOMException('Race cancelled','AbortError');
    signal?.addEventListener('abort',abort,{once:true});
    const timer=setTimeout(abort,18000);
    try{const r=await fetch(url,{signal:controller.signal,credentials:'omit'});if(!r.ok)throw Error(`Wikipedia returned HTTP ${r.status}`);const data=await r.json();if(data.error)throw Error(data.error.info||data.error.code);return data;}
    finally{clearTimeout(timer);signal?.removeEventListener('abort',abort);}
  }
  const query=(params,signal)=>json(endpoint+'?'+new URLSearchParams({format:'json',formatversion:'2',origin:'*',...params}),signal);
  function create(nodes,signal){
    const aliases=new Map(nodes.map((n,i)=>[normalize(n.title),i])),canonical=nodes.map(n=>n.title),cache=new Map(),pages=new Map();
    async function init(onProgress=()=>{}){
      // Resolve current names and incoming redirects for the fixed course roster.
      for(let offset=0;offset<nodes.length;offset+=40){
        const group=nodes.slice(offset,offset+40);let continuation={};
        do{
          const data=await query({action:'query',titles:group.map(n=>n.title).join('|'),redirects:'1',prop:'redirects',rdprop:'title',rdlimit:'max',...continuation},signal);
          const redirects=new Map([...(data.query?.normalized||[]),...(data.query?.redirects||[])].map(x=>[normalize(x.from),normalize(x.to)]));
          for(let k=0;k<group.length;k++){
            let title=normalize(group[k].title),guard=new Set();while(redirects.has(title)&&!guard.has(title)){guard.add(title);title=redirects.get(title);}
            canonical[offset+k]=title;aliases.set(title,offset+k);
          }
          for(const page of data.query?.pages||[]){const id=aliases.get(normalize(page.title));if(id===undefined)continue;for(const r of page.redirects||[])aliases.set(normalize(r.title),id);}
          continuation=data.continue;
        }while(continuation);
        onProgress(Math.min(offset+40,nodes.length),nodes.length);
      }
    }
    async function load(id){
      const data=await query({action:'parse',page:canonical[id],prop:'text|revid',redirects:'1',disableeditsection:'1'},signal);
      const doc=new DOMParser().parseFromString(data.parse.text,'text/html');
      // Keep prose and infobox links. Navigation lists are shortcuts unrelated to the article's story.
      doc.querySelectorAll('.navbox,.vertical-navbox,.sidebar,.metadata,.hatnote,.reflist,.references,.mw-editsection,.toc,#toc,.catlinks,script,style,sup.reference').forEach(e=>e.remove());
      const links=new Set();
      for(const a of doc.querySelectorAll('a[href]')){
        if(a.classList.contains('new'))continue;
        let title;try{const url=new URL(a.getAttribute('href'),'https://en.wikipedia.org');if(url.hostname!=='en.wikipedia.org'||!url.pathname.startsWith('/wiki/'))continue;title=decodeURIComponent(url.pathname.slice(6));}catch{continue;}
        const target=aliases.get(normalize(title));if(target!==undefined&&target!==id)links.add(target);
      }
      const paragraphs=[...doc.querySelectorAll('.mw-parser-output > p')].map(p=>p.textContent.trim()).filter(p=>p.length>55);
      const fallback=[...doc.querySelectorAll('p')].map(p=>p.textContent.trim()).find(p=>p.length>55);
      const summary=(paragraphs[0]||fallback||nodes[id].summary).replace(/\[\d+\]/g,'');
      const image=doc.querySelector('.infobox img')?.getAttribute('src');
      const page={links:[...links].sort((a,b)=>a-b),summary,revision:data.parse.revid,title:data.parse.title,thumbnail:image?new URL(image,'https://en.wikipedia.org').href:null};
      pages.set(id,page);return page;
    }
    async function page(id){if(!cache.has(id))cache.set(id,load(id).catch(e=>{cache.delete(id);throw e;}));return cache.get(id);}
    return {init,page,pages,canonical,links:async id=>(await page(id)).links};
  }
  function lastMonth(now=new Date()){
    const first=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth()-1,1)),last=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),0));
    const stamp=d=>d.toISOString().slice(0,10).replaceAll('-','')+'00';
    return {start:stamp(first),end:stamp(last),label:first.toLocaleDateString('en',{month:'long',year:'numeric',timeZone:'UTC'})};
  }
  async function pageviews(title,signal){const month=lastMonth();const url=`https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/${encodeURIComponent(title.replaceAll(' ','_'))}/monthly/${month.start}/${month.end}`;const data=await json(url,signal);if(!data.items?.length)throw Error('No pageview data');return{value:data.items.reduce((s,d)=>s+d.views,0),month:month.label};}
  return {create,pageviews,lastMonth};
})();
