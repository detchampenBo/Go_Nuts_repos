"""PROTOTYPE: prepare the frozen graph; build a portable HTML after search finishes.

python3 prepare.py          # writes graph.json and /tmp/one-link-graph.txt
python3 prepare.py --build  # embeds graph, search result, logic and UI in prototype.html
"""
import csv, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if '--build' in sys.argv:
    graph = json.loads((HERE/'graph.json').read_text())
    graph['discovery'] = json.loads((HERE/'discovery.json').read_text())
    page = (HERE/'template.html').read_text().replace('/* GRAPH_DATA */', 'const DATA = '+json.dumps(graph)+';')
    page = page.replace('/* GRAPH_LOGIC */', (HERE/'logic.js').read_text())
    page = page.replace('/* VISUAL_STYLE */', (HERE/'visual.css').read_text())
    page = page.replace('/* SCENE_RENDERER */', (HERE/'scene.js').read_text())
    (HERE/'prototype.html').write_text(page)
    print('Built portable prototype.html')
    sys.exit()
with (ROOT/'data/week1/week1_nodes.tsv').open() as f:
    nodes = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
edges=[]
for line in (ROOT/'data/week1/week1_edges.tsv').read_text().splitlines():
    if line and not line.startswith('#'):
        a,b=line.split('\t')[:2]
        edges.append((a,b))
adj={n['node_id']:set() for n in nodes}
for a,b in edges:
    if a!=b: adj[a].add(b);adj[b].add(a)
seen=set();components=[]
for a in adj:
    if a in seen:continue
    comp={a};stack=[a];seen.add(a)
    while stack:
        for b in adj[stack.pop()]:
            if b not in seen:seen.add(b);comp.add(b);stack.append(b)
    components.append(comp)
giant=max(components,key=len)
selected=[n for n in nodes if n['node_id'] in giant]
idx={n['node_id']:i for i,n in enumerate(selected)}
links=sorted({tuple(sorted((idx[a],idx[b]))) for a,b in edges if a in giant and b in giant and a!=b})
graph={'nodes':[{'id':n['node_id'],'name':n['name'],'url':n['url']} for n in selected], 'edges':links,
       'sourceNodes':len(nodes),'sourceEdges':len(edges),'snapshot':'2026-08-26'}
(HERE/'graph.json').write_text(json.dumps(graph))
pathlib.Path('/tmp/one-link-graph.txt').write_text(f'{len(selected)} {len(links)}\n'+'\n'.join(f'{a} {b}' for a,b in links))
print(len(selected),'nodes;',len(links),'undirected links')
