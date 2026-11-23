# Louvain transfer backbone

The observed directed network contains 1,157 clubs, 11,016 ordered routes and 16,636 recorded transfers. The saved 5-community Louvain partition has modularity Q = 0.445638.

## Whole network

| α | Routes | Transfers | Active clubs | Largest weak component | Between-community routes | Between-community transfers |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.10 | 566/11,016 | 2,986/16,636 | 229/1,157 | 225/1,157 | 90/4,337 | 395/5,507 |
| 0.20 | 1,396/11,016 | 5,271/16,636 | 383/1,157 | 378/1,157 | 309/4,337 | 958/5,507 |
| 0.30 | 2,833/11,016 | 8,191/16,636 | 514/1,157 | 511/1,157 | 772/4,337 | 1,888/5,507 |

At α = 0.20, 16.3% of within-community routes survive, compared with 7.1% of between-community routes. The three highest-weight surviving cross-community routes (with ties ordered by club IDs) are Grasshoppers (Wolfsburg) → Wolves (Chelsea, 10 transfers), Granada CF (Atlético) → Udinese Calcio (Inter, 10 transfers), Marseille (Monaco) → Genoa (Inter, 8 transfers).

## Within the saved communities

Each community uses its internal routes to compute endpoint degrees and strengths.

| Community | Active clubs at 0.10 | Largest weak component at 0.10 | Active clubs at 0.20 | Largest weak component at 0.20 | Weak components at 0.20 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Inter | 46/344 | 46/344 | 76/344 | 76/344 | 1 |
| Monaco | 39/229 | 36/229 | 66/229 | 64/229 | 2 |
| Atlético | 41/214 | 37/214 | 61/214 | 61/214 | 1 |
| Wolfsburg | 28/193 | 26/193 | 55/193 | 55/193 | 1 |
| Chelsea | 36/177 | 7/177 | 62/177 | 62/177 | 1 |

As the slider moves down from 1.00, Atlético loses club coverage first at α = 0.72 (213/214 active). Monaco is the first to have multiple active weak components, at α = 0.43 (2 components, largest 112/229 clubs).

At α = 0.10, Inter has the lowest incident-club coverage (46/344) and Chelsea has the smallest largest weak component relative to its membership (7/177). The per-community retention table records the full slider grid without historical community assumptions.

## Report cutoff

Use α = 0.20 as the course-derived starting point and a readable report snapshot. The whole-network view shows 12.7% of routes and 31.7% of transfer volume, with 383 active clubs in 3 weak components; the largest covers 32.7% of observed clubs. At 0.10, the sparser drawing retains 17.9% of volume and has 3 active weak components. At 0.30, coverage rises to 49.2% of volume and the additional routes add visual overlap.

The directed disparity rule tests each source's outgoing and destination's incoming shares. A score strictly below α at either eligible endpoint retains the route. The directed connectivity exception is tested separately. Eligible exception routes by scope are Whole network (0), Inter (0), Monaco (0), Atlético (0), Wolfsburg (0), Chelsea (0).

Coverage uses original scope totals. Active clubs touch at least one retained route. Weak and strong component counts use only active clubs, with isolates counted separately. Weak connectivity ignores arrow direction. All colours and group labels come from the saved pre-filter partition.

Alpha is an exploratory local cutoff. A network-wide false-positive rate would require a separate inferential procedure. The transfer weights count records in the observed sample, and retention describes locally concentrated volume under the null. Explaining why a route exists requires evidence beyond these transfer counts.

The original LaTeX subsection reports the broad-period analysis. Its bibliography entry for Serrano, Boguñá and Vespignani is reusable in the restricted paper. [Historical LaTeX subsection](../../../../paper/transfer_backbone.tex) · [BibTeX file](../../../../paper/transfer_backbone_references.bib)


The R reference agrees in 29 of 30 scope/cutoff comparisons. In scope 1 at α = 0.20, the exact score for Grêmio → Sassuolo equals the cutoff. Python excludes the route under the strict comparison. R's normalized arithmetic rounds the score below the cutoff and retains it. [Saved parity results](backbone_results.json) · [Boundary diagnosis](../../provenance/backbone_boundary_diagnosis.json)
