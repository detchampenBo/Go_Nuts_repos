/* PROTOTYPE: pure, unweighted, undirected graph calculations. No DOM dependencies. */
const Graph = (() => {
  function adjacency(n, edges) {
    const a=Array.from({length:n},()=>[]);
    for(const [u,v] of edges){a[u].push(v);a[v].push(u);}
    return a;
  }
  function analyze(adj) {
    const n=adj.length, b=new Float64Array(n), distances=[], counts=[];
    for(let s=0;s<n;s++) {
      const d=new Int16Array(n).fill(-1),sigma=new Float64Array(n),dep=new Float64Array(n),q=[];
      d[s]=0;sigma[s]=1;q.push(s);
      for(let h=0;h<q.length;h++) {
        const v=q[h];
        for(const w of adj[v]) {
          if(d[w]<0){d[w]=d[v]+1;q.push(w);}
          if(d[w]===d[v]+1)sigma[w]+=sigma[v];
        }
      }
      for(let k=q.length-1;k>=0;k--) {
        const w=q[k];
        for(const v of adj[w])if(d[v]===d[w]-1)dep[v]+=sigma[v]/sigma[w]*(1+dep[w]);
        if(w!==s)b[w]+=dep[w];
      }
      distances.push(d);counts.push(sigma);
    }
    for(let i=0;i<n;i++)b[i]/=(n-1)*(n-2);
    return {b,distances,counts};
  }
  function path(adj,s,t) {
    const prev=new Int16Array(adj.length).fill(-1),q=[s];prev[s]=s;
    for(let h=0;h<q.length && prev[t]<0;h++)for(const v of adj[q[h]])if(prev[v]<0){prev[v]=q[h];q.push(v);}
    if(prev[t]<0)return [];
    const p=[t];while(p[p.length-1]!==s)p.push(prev[p[p.length-1]]);return p.reverse();
  }
  function share(result,s,t,v) {
    if(s===v||t===v)return 0;
    return result.distances[s][v]+result.distances[v][t]===result.distances[s][t]
      ? result.counts[s][v]*result.counts[v][t]/result.counts[s][t] : 0;
  }
  function compare(before,after,broker) {
    const n=before.b.length;let shortened=0,winner=0;
    const journeys=[];
    for(let s=0;s<n;s++)for(let t=s+1;t<n;t++) {
      const saved=before.distances[s][t]-after.distances[s][t];
      if(saved>0)shortened++;
      const loss=share(before,s,t,broker)-share(after,s,t,broker);
      if(loss>1e-8)journeys.push({s,t,saved,loss});
    }
    journeys.sort((a,b)=>b.loss-a.loss||b.saved-a.saved||a.s-b.s||a.t-b.t);
    for(let i=1;i<n;i++)if(after.b[i]-before.b[i]>after.b[winner]-before.b[winner])winner=i;
    return {shortened,winner,journeys};
  }
  return {adjacency,analyze,path,share,compare};
})();
if(typeof module!=='undefined')module.exports=Graph;
