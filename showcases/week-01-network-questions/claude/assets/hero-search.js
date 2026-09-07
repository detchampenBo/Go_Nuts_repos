/* Search against article names and snapshot IDs, independent of visible graph nodes. */
(function(root){
  const normalise=value=>String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[_\u2010-\u2015-]/g,' ').replace(/\s+/g,' ').trim();
  function matchHeroes(nodes,query){
    const q=normalise(query);if(!q)return {hits:[],exact:null};
    const rows=nodes.map(node=>({node,name:normalise(node.name),id:normalise(node.id),short:normalise(node.name.replace(/\s*\([^)]*\)/g,''))}));
    const hits=rows.filter(r=>r.name.includes(q)||r.id.includes(q)).sort((a,b)=>{
      const rank=r=>r.name===q||r.id===q?0:r.short===q?1:r.name.startsWith(q)?2:3;
      return rank(a)-rank(b)||a.node.name.localeCompare(b.node.name);
    });
    const exact=hits.find(r=>r.name===q||r.id===q);
    const aliases=hits.filter(r=>r.short===q);
    return {hits:hits.map(r=>r.node),exact:exact?.node||(aliases.length===1?aliases[0].node:null)};
  }
  root.matchHeroes=matchHeroes;
  if(typeof module!=='undefined')module.exports={matchHeroes};
})(globalThis);
