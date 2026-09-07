"""Build reproducible missions using only real edges from the frozen graph."""
import itertools,json,random
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parent
raw=json.loads((ROOT.parents[3]/'data/graph.json').read_text())
g=nx.Graph();g.add_nodes_from(range(len(raw['nodes'])));g.add_edges_from((e['s'],e['t']) for e in raw['links'])
rng=random.Random(42); missions=[]
for trial in range(600):
 seed=rng.choice([n for n in g if g.degree(n)>2]); chosen={seed}
 while len(chosen)<24:
  frontier=list(set().union(*(set(g[n]) for n in chosen))-chosen)
  if not frontier:break
  chosen.add(rng.choice(sorted(frontier)))
 if len(chosen)!=24:continue
 h=g.subgraph(chosen).copy(); targets=rng.sample(sorted(chosen),10)
 def score(shields):
  live=h.subgraph(chosen-(set(targets)-set(shields)))
  return max(map(len,nx.connected_components(live)),default=0)
 scores=[(score(s),s) for s in itertools.combinations(targets,3)]
 low=min(s for s,_ in scores);high=max(s for s,_ in scores)
 if high-low<5 or high<15:continue
 ordered=sorted(chosen);mapping={old:i for i,old in enumerate(ordered)}
 pos=nx.spring_layout(h,seed=42,iterations=150)
 missions.append({'title':['The fractured front','A universe divided','The last connection'][len(missions)],'nodes':[{'name':raw['nodes'][n]['name'],'x':round(450+pos[n][0]*345,2),'y':round(310+pos[n][1]*230,2)} for n in ordered], 'edges':[[mapping[a],mapping[b]] for a,b in h.edges()], 'targets':[mapping[n] for n in targets], 'bestScore':high,'worstScore':low})
 if len(missions)==3:break
assert len(missions)==3
(ROOT/'missions.json').write_text(json.dumps(missions,indent=2)+'\n')
print([(m['title'],m['worstScore'],m['bestScore']) for m in missions])
