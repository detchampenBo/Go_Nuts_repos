# Handoff plan: directed, weighted Leiden communities and modularity progress

## Objective and scope

Implement a new Python analysis using the same eligible-transfer input as the Premier League joining-rate analysis. Detect Leiden communities on the directed, transfer-count-weighted graph, record how modularity changes during optimization, and compare the final observed modularity with Leiden optimized on one degree-preserving shuffled graph.

Produce three plot designs: the community network, the modularity progress plot, and a combined view. Use `leidenalg` with `igraph` for community detection, NetworkX for graph construction and independent modularity checks, and PyVis for the interactive community network. Provide publication exports for Overleaf as well.

Leiden is the selected method. Direction and weights do not inherently rule out Louvain: NetworkX also implements directed, weighted Louvain. Describe the change as a methodological choice, motivated by Leiden's refinement phase and the original paper, rather than claiming Louvain cannot process this graph. The paper's connectivity guarantees must not be presented as a guarantee of **strong connectivity** in this directed transfer network. See the linked documentation and citation below.

This document is the implementation plan. The analysis has not been run and no community assignments or Q-values have been established.

## Decisions and defaults

The directed, weighted graph specification supersedes the earlier unweighted default. Use these settings:

| Decision | Default and reason |
| --- | --- |
| Leiden edge weighting | **Transfer-count-weighted directed routes.** Each distinct origin-to-destination route has weight `transfer_count`, the number of eligible transfer records on that route. Use these weights in both optimization and Q scoring. |
| Progress unit | **One complete Leiden iteration**, using the public optimizer API. Iterations, node moves and aggregation levels are different units. |
| Internal instrumentation | No internal candidate/move trace is required. Save membership and independently verified Q at iteration boundaries. |
| Progress curve | One connected observed-Q trajectory, with an observation for iteration zero and every completed iteration. A separate horizontal blue line shows the shuffled graph's final optimized Q. |
| Null comparison | One shuffled graph, as requested. This is an exploratory comparison against one random realization, with no significance claim or permutation p-value. |

Use `weight='transfer_count'` in NetworkX scoring and `weights='transfer_count'` in `leidenalg`. After topology rewiring, assign a seeded permutation of the observed edge-weight multiset to shuffled edges in deterministic order. This preserves exact topological degrees, total transfer weight and the global weight distribution, **not each club's in/out strength**. State that null explicitly. A strength-preserving null would require a different specification; do not silently describe degree preservation as strength preservation.

## Files and inputs

Paths are relative to `pnas_report/` unless stated otherwise:

- Input: `data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz`.
- Existing sample definition and saved results: `notebooks/age_shuffle_outsideprem_toprem.py` and `output/age_shuffle_outsideprem_toprem_results.json`.
- Existing graph construction and degree definitions: `notebooks/exploration_v3.ipynb`.
- Presentation requirements: `PLOTTING_STYLE.md`, plus the session preferences below.
- New implementation: `notebooks/leiden_transfer_communities.py`.
- Focused algorithm tests: `notebooks/test_leiden_transfer_communities.py`.
- Deliverables: `output/leiden_transfer_communities_findings/`.

Expose an importable `run_leiden_analysis(transfers_path, output_dir, *, seed=2026, shared_dir=None)` and a CLI including `--shared-dir`, with defaults resolved from `__file__`. Resolve `shared_dir=None` to `output/transfer_community_comparison/` under `pnas_report/`. Reproduction from the repository root should be:

```powershell
python -B pnas_report/notebooks/leiden_transfer_communities.py
```

Keep the existing age analysis, saved results and notebooks unchanged. This plan is `notes/leiden_transfer_communities_plan.md`. The companion [Louvain plan](louvain_transfer_communities_plan.md) defines the shared comparison protocol; implement both plans for the requested comparison. The earlier environment inspection reported NetworkX 3.3 and no PyVis. Recheck the implementation environment; install compatible `leidenalg`, `igraph` and PyVis packages if needed using the normal dependency/approval workflow, and record their exact versions alongside NetworkX and plotting dependencies. Do not assume the online `latest` documentation matches the installed versions.

## 1. Reconstruct and verify the graph

1. Read the existing eligible-transfer file directly. Preserve all its selected records, including non-Premier-League destinations. **Do not filter to the 2,882 Premier League arrivals.**
2. Group by integer `(from_club_id, to_club_id)` and save the record count as `transfer_count`. Build an `nx.DiGraph` with one edge per directed pair and positive integer transfer-count weights. Club IDs identify nodes; club names are display labels.
3. Use the notebook's label mapping and deterministic node/edge insertion order. Name conflicts, if present, should be reported and resolved deterministically.
4. Verify the current snapshot against the saved analysis: **19,712 records, 5,213 distinct players, 1,254 nodes, 12,794 directed edges, no input self-loops**, and summed `transfer_count` equal to 19,712. Investigate discrepancies rather than forcing counts.
5. Define naming degree as unweighted total directed degree: `in_degree + out_degree`, calculated on the full original graph. Reciprocal partners contribute once in each direction. This is distinct from transfer strength and within-community degree.
6. Convert to `igraph.Graph(directed=True)` using an explicit, saved bijection between club IDs and contiguous vertex indices. Transfer each directed edge and its `transfer_count` without symmetrizing, binarizing or losing reciprocal edges. Verify node/edge counts, directed endpoint-weight tuples and each club's in/out strength against the NetworkX graph.

**Completion check:** graph totals and degree definitions agree with the existing analysis, and the input checksum is recorded.

## 2. Run Leiden and record iteration-level progress

Use the public `leidenalg` API with `ModularityVertexPartition`, `weights='transfer_count'`, singleton initial membership and optimizer seed 2026. This partition type directly returns normalized directed modularity at fixed `gamma=1.0`; it does not accept a `resolution_parameter` argument. Keep Leiden's refinement enabled. Do not substitute CPM, whose quality values would not be comparable with the Louvain modularity objective. See the [partition API](https://leidenalg.readthedocs.io/en/latest/reference.html#modularityvertexpartition).

**Approved trace change:** replace the earlier accepted-move and candidate-evaluation requirements with Q after each complete Leiden iteration. The Python optimizer delegates internal moves to compiled code; the public API does not expose a complete candidate/move event stream. Full internal logging would require separate source instrumentation and is outside this plan. An iteration includes local moving, refinement and aggregation; it is not one node move or one aggregation level. See the [official optimizer source](https://github.com/vtraag/leidenalg/blob/main/src/leidenalg/Optimiser.py).

1. Save the singleton membership and Q at **iteration 0**. Initial Q can be negative.
2. Create one `la.Optimiser()` per run and call `set_rng_seed(seed)` once. Reuse that optimizer and partition for successive `optimise_partition(partition, n_iterations=1)` calls, preserving RNG state. Retain the installed release's default Leiden routines and record their settings.
3. After each call, save iteration index, returned quality improvement, actual `partition.quality()`, community count and original-club membership. Independently recompute Q using `nx.community.modularity(G, communities, weight='transfer_count', resolution=1.0)`. Keep full precision in data files.
4. Continue until the first iteration with no positive returned improvement, including that terminal iteration in the trace. This follows the documented stopping rule for `n_iterations=-1`; do not inherit Louvain's level threshold or stop at the default two iterations. A materially negative gain is a verification failure to investigate. Use numerical tolerance for Q checks, not an undocumented early-stopping rule.
5. Record completed iterations, quality verification calls, final Q, final community count and stopping reason. Internal move, candidate, sweep and hierarchy-level counts are unavailable and must not be inferred from changes in membership.

The [advanced optimizer guide](https://leidenalg.readthedocs.io/en/latest/advanced.html#optimiser) describes direct optimizer access; the [official Python implementation](https://github.com/vtraag/leidenalg/blob/main/src/leidenalg/Optimiser.py) shows the stopping loop and compiled backend calls.

For both methods and both graphs, independently score directed weighted modularity as:

```text
Q = sum over communities C of:
    internal_transfer_weight(C) / m
    - out_strength(C) * in_strength(C) / m^2
m = sum of all directed transfer_count weights
```

Each directed edge contributes once; there is no undirected factor of two. Community strengths are summed over the full graph, not only internal routes. The formula follows the directed definition in the [partition implementation](https://github.com/vtraag/leidenalg/blob/main/src/leidenalg/VertexPartition.py).

**Completion check:** every saved state partitions all original clubs exactly once; Leiden and independent NetworkX Q agree within a declared tolerance (e.g. absolute `1e-10`); iteration Q is nondecreasing within that tolerance; returned improvements agree with Q differences. On small seeded directed weighted fixtures, the final partition and Q match `la.find_partition(..., la.ModularityVertexPartition, weights='transfer_count', n_iterations=-1, seed=2026)` with identical vertex/edge order, up to community-label permutation.

## 3. Create the shuffled comparison

1. Reuse the shared shuffled graph from the companion Louvain plan if available, verifying its metadata and checksum. Otherwise generate it once under that protocol: copy the observed route topology, keep the same node IDs, and randomize endpoints using directed degree-preserving swaps. Save it for both methods; do not independently regenerate a different null for Leiden.
2. Preserve **each individual club's in-degree and out-degree exactly**, the number of nodes and edges, and a simple loop-free directed graph. Preserve the observed graph itself unchanged.
3. Inspect the installed `nx.directed_edge_swap` implementation before using it. The inspected 3.3 implementation can propose self-loops and drops edge attributes on rewired edges. Use an attributed, loop-free adaptation of its three-edge swap if necessary. Reject proposals with self-loops or existing target edges **before applying them**. Keep valid directed triangle reversals possible; rejecting all repeated endpoints unnecessarily excludes them.
4. Target **10 times the edge count in successful three-edge swaps**, with at most 100 times that target in attempted proposals. Record actual successes and attempts. If it cannot complete, report the failure and investigate; never remove loops or duplicate edges afterward, since that changes degrees.
5. Assign the seeded weight permutation after topology swaps, as specified above. Verify exact degree dictionaries before/after, absence of self-loops and parallel routes, equality of weight multisets and total weight, and meaningful topology change. Save the shuffled weighted edge list, seeds, checksums and fraction of original directed edges retained. The swap count is a practical randomization budget, not proof of uniform sampling or adequate mixing.
6. Run the **same complete Leiden procedure with iteration logging** on the shared shuffled graph, using the same optimizer settings, singleton initialization and stopping rule as for the observed graph. The required horizontal baseline is its final optimized `Q_shuffled`, not Q for the observed partition evaluated on shuffled edges.

**Completion check:** all preserved invariants hold, both runs have complete traces, and `Q_observed`, `Q_shuffled` and `delta_Q = Q_observed - Q_shuffled` are independently reproducible.

This pooled topology null does not preserve seasons, season-specific league eligibility, geography, ownership, reciprocal ties or player trajectories. It preserves total transfer volume and the global weight distribution, but not club-specific in/out strengths or the association between route topology and transfer volumes. Explain these limits when relating it to the selected joining-rate dataset.

## 4. Name communities and draw the network

For each final observed community, choose the member with the highest full-graph total directed degree. Break ties by the smallest numeric club ID. Its club name is the community's display name, following the Week 4 curriculum convention. Save representative IDs and degrees; disambiguate identical display names with IDs.

Assign one distinct, deterministic colour to every community, identically across PyVis, the static network, legends and tables. Begin with the guide's default palette; extend it with distinct categorical colours if there are more than five communities, without recycling swatches. Reserve blue `#0072B2` for the null-model baseline. Labels and community names must support interpretation beyond colour alone.

- Reuse the shared observed-graph layout from the Louvain comparison protocol, or compute and save it once for both methods. Use identical positions in PyVis and publication exports; account for the browser's downward-positive y coordinates.
- Use PyVis `Network(directed=True)` and NetworkX graph data to produce the interactive community view. Keep all original nodes and edges. Show club name, ID, community, in-degree, out-degree and transfer count information in tooltips.
- Default to fixed saved coordinates with physics disabled so opening the page does not change the layout. Embed assets locally or inline so the delivered HTML is usable offline and does not depend on a CDN.
- Size nodes by the declared total-degree measure; draw edges faintly enough to see community colours. Label representative clubs, and show a readable legend containing every community name and its node count. Do not silently discard small communities or hide observations to improve Q.
- Draw the static counterpart using NetworkX and Matplotlib from the same positions, assignments, sizes and colours. This supplies vector publication output; a screenshot of the PyVis canvas is not the PDF source.

**Completion check:** every original club is shown and assigned once, each community has a unique colour, representatives satisfy the ranking rule, and all legends and representative labels are readable. Community names are convenient labels, not claims about the cause or meaning of the grouping.

## 5. Plot Q against completed Leiden iterations

- X-axis: **Completed Leiden iterations**, beginning at 0. Y-axis: **Directed weighted modularity, Q**. Use linear axes, integer iteration ticks and a range including initial Q, final observed Q and the shuffled baseline.
- Draw one connected orange observed trajectory (`#DC831B`) through every saved iteration Q, including the terminal no-improvement iteration. Mark computed states; do not smooth or add extra observations.
- Draw final shuffled Q as a **solid blue horizontal line (`#0072B2`)** over the full observed iteration range. Label it **Degree-preserving shuffle (one graph)** with its Q value. It is the separately optimized Leiden null result.
- Include final observed Q, shuffled Q and completed iterations in the legend or compact annotations. Keep settings and interpretation in the recap.
- Louvain's accepted moves and Leiden's iterations are different units. Use separate progress panels; never overlay them on a shared step axis or interpret their counts as comparable computational effort.

**Completion check:** every point is traceable to the progress CSV, final Q matches the saved partition, and the baseline matches Leiden optimized on the exact shared shuffled graph.

## 6. Three views and deliverables

Use these descriptive stems, with PDF, 600 dpi PNG and editable-text SVG for each static view:

| Plot | Stem | Additional interactive format |
| --- | --- | --- |
| Community network | `leiden_transfer_communities` | Same-stem PyVis HTML |
| Modularity progress and null baseline | `leiden_transfer_modularity_progress` | None required |
| Combined network and Q plot | `leiden_transfer_communities_and_modularity` | HTML containing the same PyVis network and progress SVG |

The combined HTML can embed the existing PyVis HTML and progress SVG; reuse the saved analysis and layout. The static combined view contains the two matching axes, with `(a)` and `(b)` panel titles. These are three plot designs in multiple formats, not additional analyses.

Also save in the deliverable folder:

| File | Required contents |
| --- | --- |
| `communities.csv` | Club ID/name, community ID/name, representative flag, original in/out/total degree, transfer strengths, colour and saved x/y coordinates. |
| `community_summary.csv` | Community size, representative ID/name and degree, and final Q contribution. Contributions must sum to final observed Q. |
| `leiden_progress.csv` | Run (`observed`/`shuffled`), completed-iteration index, returned quality improvement, independently computed delta Q, Leiden Q, NetworkX Q, verification error and community count. Include iteration 0 and the terminal no-improvement iteration for both runs. |
| `leiden_membership_trace.csv` | Run, iteration, club ID and community ID for each saved state, sufficient to reconstruct every recorded partition. |
| `club_vertex_mapping.csv` | Explicit club ID to igraph vertex-index mapping. |
| `shuffled_routes.csv` | Exact shuffled directed endpoints and `transfer_count` weights, sufficient to reconstruct the null graph. |
| `leiden_results.json` | Input checksum, graph counts, weighting convention, directed flag, partition type, fixed resolution, stopping rule, verification tolerance, optimizer settings, seeds, versions, shared graph checksums, shuffle diagnostics, available counters, final Q values, delta Q, community count, convergence reason and verification results. |
| `README.md` | Links to all outputs and reproduction command. |
| `leiden_transfer_communities_caption.md` | Short standalone captions for all three views. |
| `leiden_transfer_communities_summary.md` | Research question, sample, graph/degree definitions, algorithm, counters, null construction, comparison and limitations. |

Use `PLOTTING_STYLE.md` for publication exports. Session preferences superseding its defaults are **9 pt legends**, descriptive filenames, compact combined height around **3.4 inches** where legible, and solid blue null references. Combined width is 7.16 inches; standalone default width is 3.58 inches. A dense network or long community legend may justify more height; verify actual print readability rather than shrinking fonts. Standalone plots have captions outside the plotting area and no internal titles. Embed Arial in PDFs and preserve vector content and intended page dimensions.

## 7. Verification and completion

Implement meaningful tests for the new algorithm instrumentation and shuffle, rather than tests that merely repeat formatting constants:

1. A small asymmetric directed graph with unequal positive weights: verify Leiden Q against the explicit directed weighted formula and NetworkX Q for fixed partitions, including singleton membership. Ensure the fixture detects accidental symmetrization or binarization.
2. Conversion round-trip checks for club IDs, reciprocal edges, weights and in/out strengths; verify every iteration membership covers the original clubs exactly once.
3. Seeded parity with the public converged Leiden call, plus repeat-run equality of canonical partitions, iteration traces and counters. Verify the final no-improvement iteration is retained.
4. Shared shuffle checks for every node's in/out degree, edge count, loop-free simplicity, weight multiset, total weight and deterministic output. Include self-loop rejection and a valid directed triangle reversal when implementing the shared shuffler.
5. Full-data checks for the input snapshot, saved/final Q agreement, complete node coverage, representative naming and identical shared-input checksums across Leiden and Louvain.

Render and inspect all publication PDFs in colour and grayscale. Check fonts, page rotation, complete legends, clipped labels, distinct community swatches, and alignment between standalone and combined views. Open the PyVis and combined HTML views and verify offline loading, tooltips, legend completeness and agreement with the saved partition. Ensure a plotting rerun can consume saved analysis outputs without rerunning Leiden or changing assignments.

Completion means the new module runs, the focused checks pass, both optimization runs and their complete traces are saved, all three plot designs exist in their required formats, and the recap and shared comparison report the actual results of both methods under the companion plan's protocol. An observed Q above the shuffled Q supports only “higher than this degree-preserving randomized realization.” One shuffle provides neither a null distribution nor evidence of statistical significance. Leiden is heuristic and seed-sensitive; its partition is not a unique or proven optimum. Do not promise the comparison will be positive.

## Paired comparison with Louvain

Follow the **Shared Louvain-Leiden comparison protocol** in the [Louvain plan](louvain_transfer_communities_plan.md#shared-louvain-leiden-comparison-protocol). Both plans must use the same weighted observed graph, exact saved null realization, resolution, input ordering and network layout. The shared comparison includes final Q, method-specific null differences, community sizes, overlap and connectivity diagnostics. Do not treat an equal seed as identical random search or assert that Leiden must obtain higher Q.

## References for the implementing agent

- [Leiden package documentation](https://leidenalg.readthedocs.io/en/latest/), [introduction and directed/weighted support](https://leidenalg.readthedocs.io/en/latest/intro.html), [partition and optimiser API](https://leidenalg.readthedocs.io/en/latest/reference.html), and [advanced optimisation](https://leidenalg.readthedocs.io/en/latest/advanced.html). Inspect the installed version before implementation.
- Official Python sources: [`Optimiser.py`](https://github.com/vtraag/leidenalg/blob/main/src/leidenalg/Optimiser.py) and [`VertexPartition.py`](https://github.com/vtraag/leidenalg/blob/main/src/leidenalg/VertexPartition.py). Use the installed release's matching source when checking behaviour.
- **Original Leiden paper:** Traag, V. A., Waltman, L., and van Eck, N. J. (2019). *From Louvain to Leiden: guaranteeing well-connected communities*. Scientific Reports **9**, 5233. [User-supplied arXiv record, 1810.08473](https://arxiv.org/abs/1810.08473); [published article DOI](https://doi.org/10.1038/s41598-019-41695-z). The preprint was first submitted in 2018; the journal publication is from 2019. Use the citation key `traag2019leiden` below.
- [Week 4 curriculum: Louvain, naming communities, progress and null comparisons](../../data/week4/). Retain the naming and comparison conventions; implement Leiden as specified here.
- [NetworkX Louvain API](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html), documenting directed/weighted support; background for the methodological clarification, not the implementation target.
- [NetworkX directed modularity](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html).
- [NetworkX directed edge swaps](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.swap.directed_edge_swap.html). Verify loop and attribute behavior in the installed source.
- [PyVis API and NetworkX integration](https://pyvis.readthedocs.io/en/latest/documentation.html).

## Overleaf citation and section reference

When writing the report section, add this entry to the report's bibliography and cite the algorithm with `\cite{traag2019leiden}`. Use `\label{sec:leiden-transfer-communities}` on the methods section and `\ref{sec:leiden-transfer-communities}` for internal cross-references. In LaTeX, `\cite` references a paper; `\ref` references a labelled section, figure or table.

```bibtex
@article{traag2019leiden,
  author        = {Traag, Vincent A. and Waltman, Ludo and van Eck, Nees Jan},
  title         = {From {Louvain} to {Leiden}: guaranteeing well-connected communities},
  journal       = {Scientific Reports},
  volume        = {9},
  pages         = {5233},
  year          = {2019},
  doi           = {10.1038/s41598-019-41695-z},
  eprint        = {1810.08473},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SI},
  url           = {https://arxiv.org/abs/1810.08473}
}
```

Suggested LaTeX scaffold (describe the actual settings and findings when the analysis is complete):

```latex
\subsection{Communities in the directed transfer network}
\label{sec:leiden-transfer-communities}
We detect communities using the Leiden algorithm~\cite{traag2019leiden},
optimising directed modularity with transfer counts as edge weights.
```

Record the paper and package-documentation links in the generated analysis summary and README as well, so the implementation outputs retain their methodological provenance.
