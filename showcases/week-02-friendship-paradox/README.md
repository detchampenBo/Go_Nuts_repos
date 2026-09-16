# The Friendship Paradox

A self-contained Week 2 explorable. Pick a hero in the Marvel Wikipedia-link
network and see, node by node, that its friends are on average more connected
than it is — then read why from the degree-variance identity, and compare the
same counts on a scale-free model and a random model of the same size.

No build, backend, account, or package install. Open the folder through the
GitHub Pages site or a local HTTP server:

```sh
python -m http.server 8000
# then visit http://localhost:8000/showcases/week-02-friendship-paradox/
```

## What it shows

- **The whole network** — a force-directed drawing of every node and every
  connection, sized by degree. This is where the structural difference is
  obvious: the scale-free model grows visible hubs, the random model is an even
  mesh. Positions are precomputed (see below), not simulated in the browser.
- **The scatter** — every connected hero as one dot: across is its own degree, up
  is the mean degree of its friends, with the `y = x` diagonal drawn. Dots above
  the line are heroes whose friends are on average better connected. Both axes
  are square-root scaled with the same transform, so the diagonal stays straight
  while the many low-degree heroes remain readable.
- **Ego view** — the selected hero at the centre, up to 44 highest-degree friends as dots sized by
  that friend's own degree.
- **The identity** — `⟨k⟩ + σ²/⟨k⟩`.

Clicking a node in the network or a dot in the scatter selects that hero.

## Two averages that are easy to confuse

The page reports both, deliberately, because they answer different questions:

- `friendMeanDegree` = `⟨k²⟩/⟨k⟩` = `⟨k⟩ + σ²/⟨k⟩` is the expected degree at the
  end of a **uniformly chosen connection**. Sampling an edge endpoint is what
  biases you toward hubs, and it is the quantity the identity describes.
- `neighborMeanAverage` averages **one value per hero** — each hero's own
  friends' mean degree. This is what the scatter's vertical axis averages, so it
  is the value the chart's horizontal reference line is drawn at.

For Marvel these are 22.08 and 24.22. Labelling either one "the average friend"
without saying which sampling procedure produced it is wrong.

## Top of their circle

`topOfCircle` is the strict test: **not one** friend outranks the hero. That is
stronger than the hero's friends' mean being below their own degree — Betsy
Braddock has 28 connections and a friends' mean of 25.07, yet six of her friends
outrank her, Spider-Man among them at 106. Heroes in that situation are reported
as "below", never as "top".

## Data and models

`prepare_data.py` reads `../../data/week1/week1_nodes.tsv` and `week1_edges.tsv`
(303 articles, 1,784 directed hyperlinks). A link in either direction is one
undirected connection; reciprocal links count once. This yields 1,434 edges and
17 isolates. A hyperlink is not a canonical Marvel alliance.

Two comparison networks are generated with the Python standard library only,
using the same node count:

- **Scale-free** — a Barabási–Albert graph (growth + preferential attachment),
  `m` chosen so `⟨k⟩ ≈ 2m` matches Marvel's density. Seed `20802`.
- **Random** — a uniform `G(n, m)` graph with the same edge count as Marvel.
  Seed `20803`.

For each network the generator records every node's degree, its friends' mean
degree, its neighbour list (sorted by descending degree), and whether the
paradox holds. Aggregates: `⟨k⟩`, `⟨k²⟩/⟨k⟩`, the degree variance, `σ²/⟨k⟩`, and
the fraction of connected nodes for which the paradox holds (isolates excluded).

Node positions come from a deterministic Fruchterman-Reingold layout
(`force_layout`, 520 iterations, seeds 20811/20812/20813) run over the connected
nodes only — pure repulsion would fling isolates off the canvas, so Marvel's 17
isolates are parked in a row along the bottom instead. The layout takes about 12
seconds for all three networks.

The friendship paradox is a property of degree variance, so a degree-preserving
shuffle cannot remove it — that is why there is no shuffle control here. For the
same reason it never disappears entirely: the random model still has σ² ≈ 8.6
(Poisson, so σ² ≈ ⟨k⟩), leaving 62.7% of nodes above the diagonal. What collapses
is the *size* of the effect — the surplus drops from +12.6 connections to +0.9.
Only a perfectly regular graph, where every node has identical degree, removes it.

## Rebuild and verify

```sh
python prepare_data.py
node --test        # runs paradox.test.mjs
```

Commit `paradox-data.json` alongside any generator change. It includes the input
SHA-256, both model seeds, and all per-node measurements.

The scatterplot is the primary view. The full network is an optional disclosure;
its open state persists while selecting heroes or switching networks. The chart
labels its all-node reference mean separately from the connected-node scatter.
For large neighborhoods, the ego view explicitly identifies the top-degree subset;
all numerical neighborhood averages still use every neighbor.
