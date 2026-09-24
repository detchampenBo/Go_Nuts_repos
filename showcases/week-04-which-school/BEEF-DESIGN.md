# Philosophical Beef

Build a useful counterexample to “community = agreement”. Three sourced critiques
lead to a prediction, exact pair co-membership across 50 Louvain partitions, and
an inspectable shared-neighbour drawing. The argument is sourced independently
of the Wikipedia-link graph. No inferred sentiment or invented historical feud.

## Direction

The user selected the philosophical-beef concept after rejecting a reroll-only
demo. This implements that direction, rather than three alternative prototypes.
The older explorer and demo remain available.

Poster → two opposing positions → prediction → 50-run evidence → neighbourhood.

Theatre-scale Barlow Condensed type contrasts with quiet DM Sans data labels.
Lilac paper #eee9f5, aubergine ink #2d203e, violet #7060bd, yellow #eeed8e,
and pink #eab8cf. Portrait colours identify two sides of an argument only;
network colours identify communities and have an explicit independent legend.
The run glyph distinguishes together/apart by shape as well as colour.

Avoid the rejected crowded timeline, movement without an investigative task,
and invented school labels. Use sourced positions, a falsifiable prediction,
and directly labelled evidence. No generated portraits or decorative graphs.

## References inspected

- Pentagram, The Public Theater: https://www.pentagram.com/work/the-public-theater
  Project description and browser composition inspected. Large condensed type
  carries identity; transfer theatrical hierarchy, not the original artwork.
- Giorgia Lupi / Stefanie Posavec, Dear Data: https://www.dear-data.com/theproject
  Project page inspected in browser. Personal comparisons precede measurement;
  transfer a small repeated glyph vocabulary and explicit reading instructions.
- Commons portrait collection for the six named philosophers: source metadata
  inspected and public-domain portraits downloaded locally. Original imagery
  supplies recognisable people, with a consistent grayscale CSS treatment.

## Scientific decisions

Use original partitions, never the aligned display lanes, for pair membership.
`prepare_beef.py` reproduces every seeded partition and checks its modularity
and community count against the existing data. Exact results: Hegel/Schopenhauer
50/50; Hobbes/Rousseau 44/50; Plato/Aristotle 24/50.

Neighbour counts use all undirected links. The drawing is a disclosed ego sample:
top 12 common neighbours and top 6 exclusive neighbours per side, by full degree.
The full neighbour list is accessible underneath. Node area is approximately
proportional to degree, with radius 2 + 0.8√degree for minimum legibility.
The layout encodes neighbour category, not ideology, geography, or force distance.

Run locally: `python3 -m http.server 8000` at repository root, then open
`/showcases/week-04-which-school/beef.html`.
