# One link changes everything — throwaway prototype

Open `prototype.html` directly, or run `python3 -m http.server 8033` from the repository root and visit `/showcases/week-03-one-link/codex/prototype.html`. The generated HTML is self-contained; it requires no network, framework, or installation.

**Question:** Does watching shortest paths reroute make the loss of brokerage understandable?

The first scene compares an actual Marvel article network with one hypothetical added link. The strongest link is determined by exhaustive search, not editorial selection. “Strongest” means the largest absolute decrease in any node's normalized betweenness. The UI supports any missing link, arbitrary journey endpoints, an impact view, the full network, drawing links, and before/after playback. Three walkthroughs demonstrate shortening a route, redistributing tied routes, and rejecting an existing link.

## Finding

In the frozen 2026-08-26 snapshot, collapsing directions and keeping the largest component gives 277 nodes and 1,421 edges. All **36,805** missing undirected edges were searched. Adding **Rockman ↔ Spider-Man** causes the largest absolute loss: **Black Widow (Natasha Romanova)** falls from **0.0351202984466759** to **0.0232790051273909**, a relative decrease of about **33.7%** (1.184 percentage points). This shortens 296 of the 38,226 unordered pair distances. Another 234 pairs have unchanged distance but reduced shortest-path share for Black Widow.

The visualization distinguishes one representative route from the all-shortest-path calculation. Animated markers represent shortest paths, not measured traffic. Intermediate frames interpolate the two states visually. No fractional graph is analyzed. Node area above a visibility minimum follows betweenness. The impact subset is disclosed and the miniature map supplies full-network context.

## Rebuild

From this directory:

```sh
python3 prepare.py
clang++ -O3 -std=c++17 search.cpp -o /tmp/one-link-search
/tmp/one-link-search < /tmp/one-link-graph.txt > discovery.json
python3 prepare.py --build
```

`prepare.py` reads the repository's original TSV files, keeps the largest undirected component, and writes `graph.json`. `search.cpp` searches every missing edge using exact Brandes betweenness. `logic.js` recalculates browser results. `template.html` contains the interface; the build embeds both data and logic into `prototype.html`.

## Verification and verdict

The C++ search and browser calculations agree on the selected result. An independent, temporary definition-based calculation explicitly enumerated all 189,470 shortest paths before and 188,806 after. Every node's normalized betweenness agreed with the browser's Brandes implementation to within 4 × 10⁻¹⁵.

The numerical premise is supported: one added edge can cause a substantial loss of brokerage. Whether this presentation explains it well remains a user-evaluation question. No production design decision is claimed yet. The intended archival branch is `prototype/week-03-one-link`; no implementation issue exists in this session.

Visual plan: navy map ground (#111c2b), slate tracks (#46566b), off-white station labels (#eef0e9), amber original routes (#ffbd69), cyan bypass (#72e3e3). A large condensed headline introduces a fixed transit diagram; the measurement panel sits alongside it. The map, not decorative cards, carries the story. User-requested motion takes precedence over the generic logic-prototype preference for no animation; reduced-motion preferences are respected.
