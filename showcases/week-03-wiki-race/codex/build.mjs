import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../..'),require=createRequire(import.meta.url),G=require('./engine.js');
const source=JSON.parse(fs.readFileSync(path.join(root,'showcases/week-01-network-questions/codex/heroes.json')));
const rows=fs.readFileSync(path.join(root,'data/week1/week1_nodes.tsv'),'utf8').split('\n').filter(l=>l&&!l.startsWith('#')).slice(1).map(l=>l.split('\t'));
const descriptions=new Map(rows.map(r=>[r[0],r[4]||'']));
const nodes=source.heroes.map(n=>({...n,summary:descriptions.get(n.id)||'',title:n.id.replaceAll('_',' ')})),index=new Map(nodes.map((n,i)=>[n.id,i]));
const edges=source.edges.map(e=>[index.get(e.source),index.get(e.target)]),directed=G.adjacency(nodes.length,edges),undirected=G.adjacency(nodes.length,edges,false);
const m=G.metrics(undirected),pr=G.pagerank(directed);
nodes.forEach((n,i)=>n.stats={degree:m.degree[i],closeness:m.closeness[i],harmonic:m.harmonic[i],betweenness:m.betweenness[i],eigenvector:m.eigenvector[i],pagerank:pr[i]});
let sum=0,count=0;for(let i=0;i<nodes.length;i++)for(const d of G.bfs(directed,i).distance)if(d>0){sum+=d;count++;}
const ids=['Rockman_(character)','Storm_(Marvel_Comics)','Spider-Man','Wolverine_(character)','Black_Cat_(Marvel_Comics)','Hulk','Adam_Warlock'];
const missions=[['The long way home',ids[0],ids[1]],['Across the universe',ids[2],ids[3]],['A cosmic detour',ids[4],ids[6]]].map(([label,s,t])=>({label,start:index.get(s),target:index.get(t)}));
for(const mission of missions)if(!G.bfs(directed,mission.start,mission.target).path.length)throw Error('Unreachable practice mission');
// Find a one-way challenge with a path of 2–4 links and no return route.
outer:for(let i=0;i<nodes.length;i++){const r=G.bfs(directed,i);for(let j=0;j<nodes.length;j++)if(r.distance[j]>=2&&r.distance[j]<=4&&!G.bfs(directed,j,i).path.length){missions.push({label:'The one-way door',start:i,target:j});break outer;}}
const data={nodes,edges,missions,snapshot:'2026-08-26',directedMean:sum/count,reachablePairs:count};
let html=fs.readFileSync(path.join(here,'template.html'),'utf8');
for(const [key,file]of [['STYLE','style.css'],['ENGINE','engine.js'],['API','api.js'],['APP','app.js']])html=html.replace(`/* ${key} */`,fs.readFileSync(path.join(here,file),'utf8'));
html=html.replace('/* DATA */','const DATA = '+JSON.stringify(data).replaceAll('<','\\u003c')+';');
fs.writeFileSync(path.join(here,'prototype.html'),html);
fs.writeFileSync(path.join(here,'data.json'),JSON.stringify(data));
console.log(`Built self-contained prototype: ${nodes.length} heroes, ${edges.length} directed edges; mean reachable directed distance ${(sum/count).toFixed(4)}.`);
