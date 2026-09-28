// Pure graph operations. All race edges are directed.
const RaceGraph=(()=>{
  const adjacency=(n,edges,directed=true)=>{const a=Array.from({length:n},()=>new Set());for(const [u,v]of edges)if(u!==v){a[u].add(v);if(!directed)a[v].add(u);}return a.map(s=>[...s].sort((a,b)=>a-b));};
  function bfs(a,start,target=-1){
    const distance=Array(a.length).fill(-1),parent=Array(a.length).fill(-1),layers=[[start]],q=[start];distance[start]=0;
    for(let h=0;h<q.length;h++)for(const v of a[q[h]])if(distance[v]<0){distance[v]=distance[q[h]]+1;parent[v]=q[h];(layers[distance[v]]??=[]).push(v);q.push(v);}
    return {distance,parent,layers,path:route(parent,start,target),visited:q.length};
  }
  function route(parent,start,target){if(target<0)return [];if(start===target)return[start];if(parent[target]<0)return[];const path=[target];while(path.at(-1)!==start)path.push(parent[path.at(-1)]);return path.reverse();}
  async function search(n,start,target,getLinks,onLayer=async()=>{},signal){
    const distance=Array(n).fill(-1),parent=Array(n).fill(-1),layers=[[start]];let frontier=[start];distance[start]=0;
    await onLayer({depth:0,nodes:frontier.slice(),distance:distance.slice(),parent:parent.slice()});
    while(frontier.length&&distance[target]<0){
      if(signal?.aborted)throw new DOMException('Race cancelled','AbortError');
      const next=[];
      // Bounded concurrency, complete a ring before expanding the next one.
      for(let offset=0;offset<frontier.length;offset+=3){
        const batch=frontier.slice(offset,offset+3),lists=await Promise.all(batch.map(getLinks));
        if(signal?.aborted)throw new DOMException('Race cancelled','AbortError');
        lists.forEach((links,i)=>{const u=batch[i];for(const v of links)if(distance[v]<0){distance[v]=distance[u]+1;parent[v]=u;next.push(v);}});
        if(distance[target]>=0)break;
      }
      if(!next.length)break;
      layers.push(next);await onLayer({depth:layers.length-1,nodes:next.slice(),distance:distance.slice(),parent:parent.slice()});frontier=next;
    }
    return {distance,parent,layers,path:route(parent,start,target),visited:distance.filter(x=>x>=0).length};
  }
  function metrics(a){
    const n=a.length,b=Array(n).fill(0),closeness=[],harmonic=[],all=[];
    for(let s=0;s<n;s++){
      const d=Array(n).fill(-1),sigma=Array(n).fill(0),dep=Array(n).fill(0),q=[s];d[s]=0;sigma[s]=1;
      for(let h=0;h<q.length;h++){const u=q[h];for(const v of a[u]){if(d[v]<0){d[v]=d[u]+1;q.push(v);}if(d[v]===d[u]+1)sigma[v]+=sigma[u];}}
      const reachable=q.length-1,sum=d.reduce((t,x)=>t+Math.max(0,x),0);
      closeness[s]=sum?reachable/sum*reachable/(n-1):0;harmonic[s]=d.reduce((t,x)=>t+(x>0?1/x:0),0)/(n-1);
      for(let k=q.length-1;k>=0;k--){const w=q[k];for(const v of a[w])if(d[v]===d[w]-1)dep[v]+=sigma[v]/sigma[w]*(1+dep[w]);if(w!==s)b[w]+=dep[w];}
      all.push(d);
    }
    for(let i=0;i<n;i++)b[i]/=(n-1)*(n-2);
    let eig=Array(n).fill(1/Math.sqrt(n));
    for(let k=0;k<1000;k++){const next=a.map((links,i)=>eig[i]+links.reduce((s,j)=>s+eig[j],0));const norm=Math.hypot(...next);for(let i=0;i<n;i++)next[i]/=norm;const error=next.reduce((s,v,i)=>s+Math.abs(v-eig[i]),0);eig=next;if(error<1e-12)break;}
    return {degree:a.map(x=>x.length),closeness,harmonic,betweenness:b,eigenvector:eig,distances:all};
  }
  function pagerank(a,alpha=.85){const n=a.length;let rank=Array(n).fill(1/n);for(let k=0;k<1000;k++){const dangling=rank.reduce((s,v,i)=>s+(a[i].length?0:v),0),next=Array(n).fill((1-alpha+alpha*dangling)/n);for(let i=0;i<n;i++)for(const j of a[i])next[j]+=alpha*rank[i]/a[i].length;const error=next.reduce((s,v,i)=>s+Math.abs(v-rank[i]),0);rank=next;if(error<1e-12)break;}return rank;}
  return {adjacency,bfs,route,search,metrics,pagerank};
})();
if(typeof module!=='undefined')module.exports=RaceGraph;
