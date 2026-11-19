# Handoff plan for disparity-filtered Louvain transfer backbones

## Research question and reference

Which directed transfer routes carry unusually large shares of a club's local transfer volume, and how do the five saved Louvain communities fragment as the cutoff becomes stricter? Build an explorable that makes the answer visible at several cutoffs. Use the existing observed, directed, transfer-count-weighted Louvain partition as the starting point.

The design reference is Section 8, “Seeing structure in the hairball: backbones,” in [the local Week 4 HTML](../../data/week4/Week%204%20%C2%B7%20Communities%20%E2%80%94%2002805.html#backbones). The local iframe is an empty browser-save stub. The live explorable pairs an alpha slider and network with retention curves, route and node counts, the largest component, and details on hovered objects. It starts at alpha 0.20. Follow its workflow of filtering, laying out the backbone, and colouring by the pre-filter community assignments. Preserve the source-to-destination directions of the football data. [Week 4, Section 8](https://sunelehmann.com/socialgraphs2026-web/weeks/week4.html#backbones) · [Live reference explorable](https://sunelehmann.com/socialgraphs2026-web/explorables/backbone.html)

## 1. Freeze and validate the inputs

Paths below are relative to `pnas_report/`.

- Read [observed_routes.csv](../output/transfer_community_comparison/observed_routes.csv) for ordered `from_club_id,to_club_id,transfer_count` tuples. Read [communities.csv](../output/louvain_transfer_communities_findings/communities.csv) for the display IDs, names, representatives and colours. The saved `final_partitions.csv` groups can verify membership up to relabelling. Use the IDs in `communities.csv` for display and joins.
- Check the route file against its SHA-256 in [shared_inputs.json](../output/transfer_community_comparison/shared_inputs.json) and match that metadata and route checksum to [louvain_results.json](../output/louvain_transfer_communities_findings/louvain_results.json). Save the SHA-256 of the membership input as well. Verify complete club coverage, unique club IDs, unique ordered pairs, positive integer weights, zero loops and preservation of reciprocal routes. Reuse these assignments throughout the work. The saved observed Louvain Q is 0.43817694309007504.
- For each community, induce a directed subgraph containing all its clubs and every observed route whose two endpoints belong to it. Compute its own endpoint degrees and strengths on that graph. Also offer a **Whole network** view scored against the full observed graph so the user can examine surviving links between groups. An internal route can have different scores in these two views because their degrees and strengths use different denominators.

| Community | Clubs | Internal directed routes | Internal transfers |
| --- | ---: | ---: | ---: |
| 1 Inter | 365 | 2,385 | 4,699 |
| 2 Lille | 293 | 1,557 | 2,397 |
| 3 Atlético Madrid | 210 | 1,420 | 2,578 |
| 4 Hoffenheim | 206 | 1,419 | 2,185 |
| 5 Wolves | 180 | 802 | 1,144 |
| All communities | 1,254 | 7,583 | 13,003 |

The full graph has 12,794 directed routes and 19,712 transfers, including 5,211 between-community routes with total weight 6,709. These are pre-filter checkpoints. Investigate mismatches before proceeding.

## 2. Implement and validate the directed disparity filter

The paper's null splits a node's directional strength uniformly among its incident routes in that direction. For route \(u\to v\) with weight \(w\), test the route independently against the source's outgoing distribution and the destination's incoming distribution. The endpoint score is the upper-tail probability \((1-w/s)^{k-1}\), where \(s\) is the directional strength and \(k\) the corresponding directional degree. Save \(k\), \(s\) and the score for each endpoint. Compute on the complete input graph for that view once, with full precision. [Serrano, Boguñá and Vespignani, directed supplement §§5.1–5.2](https://arxiv.org/html/0904.2389v1#S5)

- For \(k>1\), keep the route if either applicable endpoint score is strictly below \(\alpha\). Equality fails that endpoint's test. A directional degree of one has a missing score. With one such endpoint, the other determines statistical retention.
- Include the paper's directed connectivity exception as a separate retention reason. Keep \(u\to v\) for all displayed cutoffs when \(k^{out}_u=1,\ k^{in}_v=1,\ k^{in}_u>1,\ k^{out}_v>1\). Record this as a structural exception, with both scores missing. A degree-one dyad that satisfies neither the statistical rule nor the exception falls out at every filtered cutoff and appears in the unfiltered view. The exception preserves the specified route. Connectivity of the resulting graph is measured directly. [Directed supplement §5.2](https://arxiv.org/html/0904.2389v1#S5.SS2)
- Use R `disparityfilter::backbone(graph, weights = weights, directed = TRUE, alpha = alpha)` version 2.2.3 to validate the statistical component. Construct an unnamed directed igraph with a saved, contiguous one-based index to club-ID mapping. The package compares edge-list endpoints against numerical vertex indices. Align weights with `igraph::E(graph)` order and verify the round-trip tuples before scoring. Rejoin the package output on the ordered club pair. It can return two rows for one route if both endpoint scores pass and differ. Collapse their membership to one retained route and keep its original weight once. For a scope with zero routes, return a typed empty result from the wrapper. [Versioned function docs](https://www.rdocumentation.org/packages/disparityfilter/versions/2.2.3/topics/backbone) · [CRAN package](https://cran.r-project.org/package=disparityfilter) · [Released package source](https://rdrr.io/cran/disparityfilter/src/R/disparity_filter.R)
- The package skips both directional degree-one endpoints and omits the paper's connectivity exception. Compare the package's ordered retained route set with the closed-form statistical rule on all six views at \(\alpha\in\{0.05,0.10,0.20,0.30,0.50\}\). Verify the displayed paper-rule set against the union of the package set and the flagged exceptions. The current inputs have zero eligible exception routes across the six scopes. Report the count for each scope so the rule remains auditable on later data. Compute the per-route endpoint scores in Python for tooltips and slider thresholds, and keep R parity as a reproducible test.
- Treat alpha as an exploratory local cutoff. The two endpoint tests, structural exception, many routes and repeated views preclude interpreting alpha as a network-wide false-positive rate. These weights count transfers in the selected sample. Retention captures locally concentrated volume under this null and cannot establish the reason a route exists.

## 3. Build the explorable and the publication view

1. **Controls.** Open on the whole network with alpha 0.20. Offer a community selector with the five saved names, a keyboard-accessible slider from 0.01 to 1.00 in 0.01 steps, and an explicit unfiltered view. Smaller alpha is stricter. Offer faint or hidden dropped routes. The unfiltered view shows every original route in the selected scope, including untestable degree-one routes.
2. **Layout and marks.** Compute one weighted force layout per scope using seed 2029 and the backbone at alpha 0.50 as the reference. Save reference alpha, seed, package version and coordinates. Place clubs disconnected at the reference cutoff in a designated margin, in deterministic ID order, so they can still be found when shown. Fix coordinates and disable physics before changing alpha. Keep node sizes fixed by pre-filter strength within each scope. Use the original Louvain colours and names. Label the saved representative and give it an explicit isolated state when relevant. Use faint directed edges with arrowheads and width increasing with transfer count. Hover should show club name, ID, community and original versus retained in/out counts and strengths. Route hover should show direction, transfer count, both endpoint scores and the retention reason. Embed all assets for offline use.
3. **Retention and fragmentation.** Update retained routes and transfer weights, clubs incident to a retained route, and largest weak component size against the scope's unfiltered baseline. Count empty backbones as zero active clubs and zero clubs in the largest active weak component. Report weak and strong component counts on the active subgraph in the saved table, with isolates reported separately. Plot route and weight retention, incident-club coverage and largest-weak-component coverage over alpha. In the whole-network view show retained within- and between-community routes and weights. A smaller largest component indicates loss of weak connectivity among visible routes. It establishes neither reachability along route directions nor a change in Louvain membership.
4. **Publication figure.** Export side-by-side snapshots at 0.10, 0.20 and 0.30 for the whole-network view with fixed positions and sizes. Use [PLOTTING_STYLE.md](../PLOTTING_STYLE.md) for Arial, vector PDF, 600 dpi PNG, editable-text SVG and print inspection. Keep the same legend and include the retained counts in the caption. Start at alpha 0.20 as a course-derived reference. Discuss visibility, weight coverage and fragmentation when choosing a final report cutoff.

## 4. Save the analysis and verify the handoff

Implement `notebooks/disparityfilter_reference.R`, `notebooks/louvain_transfer_backbone.py` and `notebooks/test_louvain_transfer_backbone.py`. Resolve default paths from the source file. Save deliverables under `output/louvain_transfer_backbone_findings/`.

| Output | Required contents |
| --- | --- |
| `louvain_transfer_backbone.html` | Offline network, selector, alpha control, retention curves, counts and tooltips |
| `louvain_backbone_alpha_comparison.pdf`, `.png`, `.svg` | Three fixed-layout whole-network snapshots |
| `backbone_route_scores.csv` | Scope, ordered endpoint IDs, original weight, each endpoint's degree, strength and score, minimum available score, exception flag |
| `backbone_retention.csv` | Per-scope per-alpha counts, denominators, active coverage, isolates, components, and internal/between-community route and weight totals |
| `backbone_layout.csv` | Scoped coordinates and node sizes |
| `backbone_results.json` | Input checksums, versions, rules, seeds, layout and parity diagnostics |
| `README.md` and `backbone_summary.md` | Commands, file links, plot caption and interpretation of actual findings |

Acceptance checks

- Test \(A\to B=15,\ A\to C=1,\ D\to B=3\). For \(A\to B\), the outgoing score is 0.0625 and the incoming score is \(1/6\). It falls out at 0.0625, passes only from the source at 0.10, and passes both endpoints at 0.20 while contributing one route and 15 transfers. A standalone \(E\to F=9\) exercises the missing scores. Use a separate \(G\to H,\ I\to H,\ H\to J,\ J\to K,\ J\to L\) fixture where \(H\to J\) passes only by the paper exception. Test reciprocal edges with unequal weights, a zero-route scope and an empty retained graph. Include a fixture where the same route has different scores in the induced and whole-network views.
- Verify the checkpoints from step 1, exact package parity for the statistical rule on all selected cutoffs, nested retained edge sets as alpha increases, and original weights for all retained routes. Independently recompute the incident clubs and largest weak component at 0.10, 0.20 and 0.30. Check directedness in every scope and distinguish original membership size from the active club count in the interface.
- Open the HTML with networking disabled. Exercise all six scopes, slider boundaries and the unfiltered view. Check tooltips, displayed counts, coordinate stability and empty-state behaviour. Inspect the exported PDFs in colour and grayscale and verify embedded Arial, editable SVG text and 600 dpi PNG.
- Confirm the saved Louvain files and shared inputs match their original checksums after the analysis. Report surviving cross-community routes and describe which communities lose coverage or fragment earliest, with values and denominators traceable to the tables.

## Environment and bibliography

Use `conda activate network_analysis`. The environment has R 4.5.3, R igraph 2.3.4 and disparityfilter 2.2.3, installed from the exact archived CRAN release. The directed smoke test passed the strict cutoff, dual-endpoint output, degree-one dyad and package exception checks. Python 3.12.14, NetworkX 3.7, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.5, Matplotlib 3.11.2 and PyVis 0.3.2 were verified in the same environment. The Python smoke test exercised a seeded force layout, a PDF export and PyVis HTML generation. [CRAN package requirements](https://cran.r-project.org/package=disparityfilter) · [Exact CRAN source archive](https://cran.r-project.org/src/contrib/Archive/disparityfilter/disparityfilter_2.2.3.tar.gz)

Add [transfer_backbone_references.bib](../paper/transfer_backbone_references.bib) to the Overleaf bibliography and cite the paper as `\cite{serrano2009multiscale}`. Give the report subsection `\label{sec:louvain-transfer-backbone}` and refer to that section with `\ref{sec:louvain-transfer-backbone}`. [Published paper](https://doi.org/10.1073/pnas.0808904106) · [arXiv record](https://arxiv.org/abs/0904.2389)
