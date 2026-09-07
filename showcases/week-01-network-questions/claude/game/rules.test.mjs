import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {outcome,bestDefence} from './rules.mjs';
const missions=JSON.parse(fs.readFileSync(new URL('./missions.json',import.meta.url)));
const raw=JSON.parse(fs.readFileSync(new URL('../../../../data/graph.json',import.meta.url)));
const realEdges=new Set(raw.links.flatMap(e=>{const a=raw.nodes[e.s].name,b=raw.nodes[e.t].name;return[JSON.stringify([a,b]),JSON.stringify([b,a])];}));
// An independent union-find oracle checks every legal shield placement.
function oracle(m,shields){
 const dead=new Set(m.targets.filter(n=>!shields.includes(n))), parent=m.nodes.map((_,i)=>i);
 function find(n){while(parent[n]!==n)n=parent[n];return n;}
 for(const[a,b]of m.edges)if(!dead.has(a)&&!dead.has(b))parent[find(a)]=find(b);
 const counts=new Map();m.nodes.forEach((_,i)=>{if(!dead.has(i))counts.set(find(i),(counts.get(find(i))||0)+1);});
 return Math.max(0,...counts.values());
}
test('direction is ignored, erased articles do not bridge survivors, isolates count',()=>{
 const m={nodes:[{},{},{},{}],edges:[[1,0],[1,2]],targets:[1]};
 assert.equal(outcome(m,[]).score,1);assert.equal(outcome(m,[1]).score,3);
 assert.deepEqual(outcome(m,[]).removed,[1]);
});
for(const m of missions)test(`${m.title}: real graph, 120 outcomes, exact optimum`,()=>{
 assert.equal(m.nodes.length,24);assert.equal(new Set(m.targets).size,10);
 for(const [a,b]of m.edges)assert.ok(realEdges.has(JSON.stringify([m.nodes[a].name,m.nodes[b].name])));
 assert.equal(outcome({...m,targets:[]},[]).score,24);
 let high=0,low=24,count=0;
 for(let a=0;a<8;a++)for(let b=a+1;b<9;b++)for(let c=b+1;c<10;c++){
  const shields=[m.targets[a],m.targets[b],m.targets[c]], result=outcome(m,shields);
  assert.equal(result.score,oracle(m,shields));assert.equal(result.removed.length,7);
  assert.equal(result.components.flat().length,17);
  assert.ok(shields.every(n=>!result.removed.includes(n)));
  high=Math.max(high,result.score);low=Math.min(low,result.score);count++;
 }
 assert.equal(count,120);assert.equal(high,m.bestScore);assert.equal(low,m.worstScore);
 assert.ok(high-low>=5);const best=bestDefence(m);assert.equal(best.score,high);assert.equal(outcome(m,best.shields).score,high);
});
