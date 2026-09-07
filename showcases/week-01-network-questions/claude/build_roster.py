"""Build comic roster layouts and directed community link counts from the saved graph."""
from pathlib import Path
import json
import networkx as nx
ROOT=Path(__file__).resolve().parent
raw=json.loads((ROOT.parents[2]/'data/graph.json').read_text())
colors=['#82b4ed','#ffb04f','#99d775','#ff818e','#d6a0dc','#70d4cf','#f2d66e','#b7a1f4']
ids={i for i,n in enumerate(raw['nodes']) if n['grp']=='giant'}
edges=[(e['s'],e['t']) for e in raw['links'] if e['s'] in ids and e['t'] in ids]
groups=[]
for c in raw['communities']:
 i=c['id'];members=sorted(n for n in ids if raw['nodes'][n]['comm']==i);mapping={n:j for j,n in enumerate(members)}
 internal=[(a,b) for a,b in edges if a in mapping and b in mapping]
 g=nx.Graph();g.add_nodes_from(members);g.add_edges_from(internal)
 pos=nx.spring_layout(g,seed=42,iterations=150)
 outgoing=[0]*8;incoming=[0]*8
 for a,b in edges:
  ca,cb=raw['nodes'][a]['comm'],raw['nodes'][b]['comm']
  if ca==i and cb!=i:outgoing[cb]+=1
  if cb==i and ca!=i:incoming[ca]+=1
 groups.append({'id':i,'name':c['label'],'color':colors[i],'nodes':[{'name':raw['nodes'][n]['name'],'degree':raw['nodes'][n]['deg'],'x':round(200+pos[n][0]*163,2),'y':round(120+pos[n][1]*88,2)} for n in members], 'edges':[[mapping[a],mapping[b]] for a,b in internal], 'incoming':incoming,'outgoing':outgoing})
(ROOT/'assets/roster-data.js').write_text('window.communityRoster = '+json.dumps(groups,separators=(',',':'))+';\n')
print('8 communities,',sum(len(g['nodes']) for g in groups),'articles;',sum(sum(g['outgoing']) for g in groups),'cross-community directed links')
