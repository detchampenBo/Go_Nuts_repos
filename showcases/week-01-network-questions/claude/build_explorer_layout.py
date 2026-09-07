"""Presentation-only district layout. Preserves every article and source link."""
from pathlib import Path
import json,math
import networkx as nx
ROOT=Path(__file__).resolve().parent
raw=json.loads((ROOT.parents[2]/'data/graph.json').read_text())
g=nx.Graph();g.add_nodes_from(range(len(raw['nodes'])));g.add_edges_from((e['s'],e['t']) for e in raw['links'])
positions={}
for group in range(8):
 members=[i for i,n in enumerate(raw['nodes']) if n['comm']==group]
 local=nx.spring_layout(g.subgraph(members),seed=42,iterations=220,k=.65)
 angle=-math.pi/2+group*math.pi/4;cx=660+500*math.cos(angle);cy=460+330*math.sin(angle)
 # Spread close nodes without adding forces or edges to the underlying graph.
 xy={i:[float(local[i][0])*120,float(local[i][1])*100] for i in members}
 for _ in range(100):
  for j,a in enumerate(members):
   for b in members[j+1:]:
    dx=xy[b][0]-xy[a][0];dy=xy[b][1]-xy[a][1];dist=math.hypot(dx,dy)
    if dist<22:
     if dist<.001:dx,dy,dist=1,0,1
     push=(22-dist)*.26
     xy[a][0]-=dx/dist*push;xy[a][1]-=dy/dist*push;xy[b][0]+=dx/dist*push;xy[b][1]+=dy/dist*push
 for i in members:positions[raw['nodes'][i]['id']]=[round(cx+xy[i][0],3),round(cy+xy[i][1],3)]
island=[i for i,n in enumerate(raw['nodes']) if n['grp']=='island'];isolates=[i for i,n in enumerate(raw['nodes']) if n['grp']=='isolate']
for j,i in enumerate(island):
 angle=j*2*math.pi/len(island);positions[raw['nodes'][i]['id']]=[round(280+95*math.cos(angle),3),round(1040+60*math.sin(angle),3)]
for j,i in enumerate(isolates):positions[raw['nodes'][i]['id']]=[600+(j%9)*40,1015+(j//9)*55]
assert len(positions)==len(raw['nodes'])==303
(ROOT/'assets/explorer-layout.js').write_text('window.explorerDistrictLayout = '+json.dumps(positions,separators=(',',':'))+';\n')
print('303 article positions generated; source graph unchanged.')
