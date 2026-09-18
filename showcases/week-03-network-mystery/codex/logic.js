// Pure graph and evidence operations; no DOM or hidden answer key.
const Mystery=(()=>{
  const adjacency=data=>{const a=data.rooms.map(()=>[]);for(const [u,v]of data.edges){a[u].push(v);a[v].push(u);}return a;};
  function bfs(a,start){
    const distance=a.map(()=>-1),predecessors=a.map(()=>[]),layers=[[start]],queue=[start];distance[start]=0;
    for(let i=0;i<queue.length;i++){
      const u=queue[i];for(const v of a[u]){
        if(distance[v]<0){distance[v]=distance[u]+1;(layers[distance[v]]??=[]).push(v);queue.push(v);}
        if(distance[v]===distance[u]+1)predecessors[v].push(u);
      }
    }
    return {distance,predecessors,layers};
  }
  function shortestPaths(a,start,end){
    const {distance,predecessors}=bfs(a,start);if(distance[end]<0)return[];
    const routes=[];
    function visit(v,tail){if(v===start){routes.push([start,...tail]);return;}for(const p of predecessors[v])visit(p,[v,...tail]);}
    visit(end,[]);return routes;
  }
  function analyze(data){
    const a=adjacency(data),searches=a.map((_,i)=>bfs(a,i)),pairs=[],raw=a.map(()=>0);
    for(let s=0;s<a.length;s++)for(let t=s+1;t<a.length;t++){
      const routes=shortestPaths(a,s,t),credit=a.map(()=>0);
      for(const path of routes)for(const v of path.slice(1,-1))credit[v]+=1/routes.length;
      credit.forEach((x,i)=>raw[i]+=x);pairs.push({s,t,routes,credit});
    }
    const denominator=(a.length-1)*(a.length-2)/2;
    const metrics=a.map((neighbors,i)=>{const sum=searches[i].distance.reduce((x,y)=>x+y,0);return {degree:neighbors.length,sum,mean:sum/(a.length-1),closeness:(a.length-1)/sum,between:raw[i]/denominator};});
    const facts=data.suspects.map(s=>metrics[s.room]);
    const matches=[facts.map(f=>f.degree===3),facts.map(f=>f.mean<=1.75),facts.map(f=>f.between>=.1)];
    return {a,searches,pairs,metrics,facts,matches,denominator};
  }
  function survivors(matches,filed){return matches[0].map((_,i)=>i).filter(i=>filed.every((yes,c)=>!yes||matches[c][i]));}
  function checkSelection(matches,clue,selected){return matches[clue].every((yes,i)=>yes===selected.includes(i));}
  return {adjacency,bfs,shortestPaths,analyze,survivors,checkSelection};
})();
if(typeof module!=='undefined')module.exports=Mystery;
