"""Render presentation charts from the existing graph; never modify analysis data."""
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT.parents[2] / 'data/graph.json').read_text())
plt.rcParams.update({'figure.facecolor':'#151e22', 'axes.facecolor':'#151e22',
    'text.color':'#f3efdf', 'axes.labelcolor':'#b9c8cd', 'xtick.color':'#b9c8cd',
    'ytick.color':'#b9c8cd', 'axes.edgecolor':'#607078', 'font.size':11,
    'axes.titleweight':'bold', 'axes.titlepad':20, 'svg.fonttype':'none'})
nodes = DATA['nodes']
fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
total = np.array([n['deg'] for n in nodes])
axes[0].hist(total, bins=range(0, int(total.max())+3), color='#d3f66b', edgecolor='#0c1013', linewidth=.5)
axes[0].set(title='01 / TOTAL DEGREE', xlabel='Total links', ylabel='Articles')
axes[0].annotate('Spider-Man', xy=(115,1), xytext=(66,15), color='#ff9565', arrowprops={'arrowstyle':'->','color':'#ff9565'})
for key,label,color in [('in','Inbound','#ff8c73'),('out','Outbound','#a69af4')]:
    values=np.array([n[key] for n in nodes]); counts=Counter(values)
    positive=sorted(k for k in counts if k>0)
    axes[1].loglog(positive,[counts[k] for k in positive],'o',color=color,label=label,ms=5)
    values=np.sort(values); ccdf=1-np.arange(len(values))/len(values)
    axes[2].loglog(values[values>0],ccdf[values>0],drawstyle='steps-post',color=color,label=label,lw=2)
axes[1].set(title='02 / DEGREE COUNTS',xlabel='Links (log scale)',ylabel='Articles (log scale)')
axes[2].set(title='03 / THE LONG TAIL',xlabel='Links (log scale)',ylabel='Fraction at or above (log scale)')
for ax in axes:
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.12)
for ax in axes[1:]:ax.legend(frameon=False,labelcolor='#f3efdf')
fig.tight_layout(pad=2.5)
fig.savefig(ROOT/'assets/degree-comic.svg',bbox_inches='tight')
plt.close(fig)
# Match the notebook: internal directed edges / all touching directed edges,
# restricted to the giant component, using its existing community assignments.
giant={n['id']:n for n in nodes if n['grp']=='giant'}
edges=DATA.get('links',DATA.get('edges'))
def endpoint(e,key):
    v=e[key] if key in e else nodes[e['s' if key=='source' else 't']]['id']
    return v['id'] if isinstance(v,dict) else v
rows=[]
for community in sorted({n['comm'] for n in giant.values()}):
    members={k for k,n in giant.items() if n['comm']==community}
    internal=touching=0
    for e in edges:
        a,b=endpoint(e,'source'),endpoint(e,'target')
        if a not in giant or b not in giant:continue
        internal+=a in members and b in members
        touching+=a in members or b in members
    label=next(n['commLabel'] for n in giant.values() if n['comm']==community)
    rows.append({'label':label,'value':100*internal/touching})
(ROOT/'assets/community-shares.json').write_text(json.dumps(sorted(rows,key=lambda r:-r['value']),indent=2)+'\n')
print('Rendered degree-comic.svg and community-shares.json')
