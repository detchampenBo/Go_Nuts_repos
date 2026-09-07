export function outcome(mission, shields) {
  const protectedNodes = new Set(shields);
  const removed = new Set(mission.targets.filter(n => !protectedNodes.has(n)));
  const neighbours = mission.nodes.map(() => []);
  for (const [a,b] of mission.edges) if (!removed.has(a) && !removed.has(b)) {
    neighbours[a].push(b); neighbours[b].push(a);
  }
  const seen = new Set(removed), components = [];
  for (let i=0; i<mission.nodes.length; i++) if (!seen.has(i)) {
    const group=[i]; seen.add(i);
    for (let k=0;k<group.length;k++) for (const n of neighbours[group[k]]) if (!seen.has(n)) {seen.add(n);group.push(n);}
    components.push(group);
  }
  components.sort((a,b)=>b.length-a.length);
  return {removed:[...removed], components, score:components[0]?.length || 0};
}
export function bestDefence(mission) {
  let best={score:-1,shields:[]}; const t=mission.targets;
  for(let a=0;a<t.length-2;a++) for(let b=a+1;b<t.length-1;b++) for(let c=b+1;c<t.length;c++) {
    const shields=[t[a],t[b],t[c]], score=outcome(mission,shields).score;
    if(score>best.score) best={score,shields};
  }
  return best;
}
