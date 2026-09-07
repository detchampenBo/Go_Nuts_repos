"""Draw a compact vector community map from the saved graph, without changing data."""
import json,math,html
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parent
raw=json.loads((ROOT.parents[2]/'data/graph.json').read_text())
nodes={i:n for i,n in enumerate(raw['nodes']) if n['grp']=='giant'}
edges=[(e['s'],e['t']) for e in raw['links'] if e['s'] in nodes and e['t'] in nodes]
g=nx.Graph();g.add_nodes_from(nodes);g.add_edges_from(edges)
colors=['#82b4ed','#ffb04f','#99d775','#ff818e','#d6a0dc','#70d4cf','#f2d66e','#b7a1f4']
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 600" role="img" aria-labelledby="title desc">', '<title id="title">Eight communities in the 277-article giant component</title>','<desc id="desc">Real article links connect eight numbered groups, corresponding to the legend. The ring layout is a drawing choice; node area reflects total degree in the frozen roster.</desc>']
pos={};centres={}
for i in range(8):
 angle=-math.pi/2+i*math.pi/4;cx=410+270*math.cos(angle);cy=300+200*math.sin(angle);centres[i]=(cx,cy)
 group=[n for n in nodes if nodes[n]['comm']==i]
 local=nx.spring_layout(g.subgraph(group),seed=42,iterations=180)
 parts.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="94" ry="80" fill="{colors[i]}" fill-opacity=".045" stroke="{colors[i]}" stroke-opacity=".18" stroke-dasharray="3 6"/>')
 for n in group:pos[n]=(cx+local[n][0]*75,cy+local[n][1]*59)
for a,b in edges:
 x,y=pos[a];xx,yy=pos[b];same=nodes[a]['comm']==nodes[b]['comm'];color=colors[nodes[a]['comm']] if same else '#95a8c3'
 parts.append(f'<path d="M{x:.2f},{y:.2f}L{xx:.2f},{yy:.2f}" fill="none" stroke="{color}" stroke-opacity="{.23 if same else .065}" stroke-width=".8"/>')
for n in sorted(nodes,key=lambda n:nodes[n]['deg'],reverse=True):
 x,y=pos[n];r=math.sqrt(7+nodes[n]['deg']*.8)
 parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{colors[nodes[n]["comm"]]}" stroke="#101923" stroke-width="1.2"><title>{html.escape(nodes[n]["name"])} · {nodes[n]["deg"]} total links</title></circle>')
for i,(cx,cy) in centres.items():
 angle=-math.pi/2+i*math.pi/4;x=cx+76*math.cos(angle);y=cy+68*math.sin(angle)
 parts.append(f'<rect x="{x-15:.2f}" y="{y-13:.2f}" width="30" height="26" rx="3" fill="{colors[i]}" stroke="#0b1119" stroke-width="2"/><text x="{x:.2f}" y="{y+4:.2f}" text-anchor="middle" fill="#101923" font-family="system-ui,sans-serif" font-size="12" font-weight="900">0{i+1}</text>')
parts.append('</svg>');(ROOT/'assets/community-map.svg').write_text('\n'.join(parts)+'\n')
print(f'Rendered {len(nodes)} nodes and {len(edges)} directed edges')
