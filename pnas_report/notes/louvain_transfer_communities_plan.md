# Handoff plan: directed, weighted Louvain communities and modularity progress

## Objective and scope

Implement a new Python analysis using the same eligible-transfer input as the Premier League joining-rate analysis. Detect Louvain communities on the directed, transfer-count-weighted graph, record how modularity changes during optimization, and compare the final observed modularity with Louvain optimized on one degree-preserving shuffled graph.

Produce three plot designs: the community network, the modularity progress plot, and a combined view. Use NetworkX for graph analysis and PyVis for the interactive community network. Provide publication exports for Overleaf as well.

This is the Louvain implementation plan. Implement it alongside the companion [Leiden plan](leiden_transfer_communities_plan.md) and follow the shared comparison protocol below. The analysis has not been run and no community assignments or Q-values have been established.

## Evidence that Louvain supports directed, weighted graphs

Use the **NetworkX implementation of directed Louvain**. Support differs between libraries; a restriction in another library does not establish a restriction for every Louvain implementation.

- The [NetworkX 3.3 Louvain API](https://networkx.org/documentation/networkx-3.3/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html) explicitly gives a directed modularity-gain equation using weighted in/out degrees. Its `weight` parameter accepts an edge-attribute name. For this network, that argument is `weight='transfer_count'`.
- The [NetworkX 3.3 implementation](https://networkx.org/documentation/networkx-3.3/_modules/networkx/algorithms/community/louvain.html) tests `G.is_directed()`, preserves the input graph class with `G.__class__()` for simple graphs, and computes in/out degrees with `weight='weight'` inside `_one_level`. The public input attribute is copied to that internal `weight` attribute. Direction and weights therefore enter the optimization itself.
- The API cites Dugué and Perez (2015), *Directed Louvain: maximizing modularity in directed networks*, [HAL report hal-01231784](https://hal.science/hal-01231784), as the directed-method reference. The bibliographic details below follow that API reference; the HAL page could not be inspected because access was denied.

These are direct documentation and implementation evidence, including the previously inspected NetworkX version. Recheck the installed release when implementing. The small directed weighted parity tests below verify the chosen implementation on this project's inputs.

Minimal public API example, for a directed graph already built with the stated weights:

```python
communities = nx.community.louvain_communities(
    G, weight="transfer_count", resolution=1.0, threshold=1e-7, seed=2026
)
q = nx.community.modularity(
    G, communities, weight="transfer_count", resolution=1.0
)
```

The instrumented implementation below must match this public routine; this example alone does not produce a move trace.

## Decisions and defaults

The user has requested a comparison of Louvain and Leiden on the directed, weighted transfer graph. This supersedes the earlier unweighted default. Use these settings:

| Decision | Default and reason |
| --- | --- |
| Louvain edge weighting | **Transfer-count-weighted directed routes.** Each distinct origin-to-destination route has weight `transfer_count`, the number of eligible transfer records on that route. Use these weights in optimization and Q scoring, matching Leiden. |
| Meaning of a move | **One accepted relocation of a node into a different community.** At an aggregated level, relocating a supernode counts as one move; record how many original clubs it represents. |
| Candidate computations | Log every candidate modularity evaluation separately, including rejected candidates. Candidate evaluations, accepted moves, sweeps and hierarchy levels are separate counters. |
| Progress curve | One connected observed-Q trajectory, with an observation for move zero and every accepted move. A separate horizontal blue line shows the shuffled graph's final optimized Q. |
| Null comparison | One shuffled graph, as requested. This is an exploratory comparison against one random realization, with no significance claim or permutation p-value. |

Use `weight='transfer_count'` consistently for observed and shuffled optimization and scoring. After topology rewiring, assign a seeded permutation of the observed edge-weight multiset to shuffled edges in deterministic order. This preserves exact topological degrees, total transfer weight and the global weight distribution, **not each club's in/out strength**. State that null explicitly. A strength-preserving null would require a different specification; do not silently describe degree preservation as strength preservation.

## Files and inputs

Paths are relative to `pnas_report/` unless stated otherwise:

- Input: `data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz`.
- Existing sample definition and saved results: `notebooks/age_shuffle_outsideprem_toprem.py` and `output/age_shuffle_outsideprem_toprem_results.json`.
- Existing graph construction and degree definitions: `notebooks/exploration_v3.ipynb`.
- Presentation requirements: `PLOTTING_STYLE.md`, plus the session preferences below.
- New implementation: `notebooks/louvain_transfer_communities.py`.
- Focused algorithm tests: `notebooks/test_louvain_transfer_communities.py`.
- Deliverables: `output/louvain_transfer_communities_findings/`.

Expose an importable `run_louvain_analysis(transfers_path, output_dir, *, seed=2026, shared_dir=None)` and a CLI including `--shared-dir`, with defaults resolved from `__file__`. Resolve `shared_dir=None` to `output/transfer_community_comparison/` under `pnas_report/`. Reproduction from the repository root should be:

```powershell
python -B pnas_report/notebooks/louvain_transfer_communities.py
```

Keep the existing age analysis, saved results and notebooks unchanged. The earlier environment inspection reported NetworkX 3.3 and no PyVis. Recheck the implementation environment, install PyVis if needed using its normal dependency/approval workflow, and record package versions. Do not assume the online documentation matches the installed release.

## 1. Reconstruct and verify the graph

1. Read the existing eligible-transfer file directly. Preserve all its selected records, including non-Premier-League destinations. **Do not filter to the 2,882 Premier League arrivals.**
2. Group by integer `(from_club_id, to_club_id)` and save the record count as `transfer_count`. Build an `nx.DiGraph` with one edge per directed pair and positive integer transfer-count weights. Club IDs identify nodes; club names are display labels.
3. Use the notebook's label mapping and deterministic node/edge insertion order. Name conflicts, if present, should be reported and resolved deterministically.
4. Verify the current snapshot against the saved analysis: **19,712 records, 5,213 distinct players, 1,254 nodes, 12,794 directed edges, no input self-loops**, and summed `transfer_count` equal to 19,712. Investigate discrepancies rather than forcing counts.
5. Define naming degree as unweighted total directed degree: `in_degree + out_degree`, calculated on the full original graph. Reciprocal partners contribute once in each direction. This is distinct from transfer strength and within-community degree.

**Completion check:** graph totals and degree definitions agree with the existing analysis, and the input checksum is recorded.

## 2. Instrument the complete directed Louvain algorithm

Use `weight='transfer_count'`, resolution `gamma=1.0`, the installed NetworkX default level stopping threshold (`1e-7` in the inspected version), no level cap, and fixed seed 2026. Preserve direction and weights throughout. The Leiden plan uses the same normalized directed modularity objective at gamma 1, with its own documented iteration stopping rule.

NetworkX's public `louvain_partitions` reports hierarchy levels; that output alone cannot supply a node-move trace. Implement an instrumented adaptation of the installed NetworkX Louvain logic in the new module. Keep the move-selection, aggregation, ordering and stopping behavior consistent with that version. Retain source attribution and the required license notice for copied implementation code. Avoid patching the installed package or globally monkey-patching NetworkX.

Instrumentation requirements:

- Start with every original club in its own community; save its actual modularity at **move 0**. Initial Q can be negative.
- For each node visit, record all candidate community evaluations, the current partition Q and the proposed delta Q. Save `q_candidate = q_before + delta_q` even when the proposal is rejected. Choose the best positive-gain candidate using the algorithm's existing rules.
- After an accepted relocation, increment the global move counter and save the actual partition Q. Recompute that Q on the original graph with `nx.community.modularity` to verify the incremental update. Full precision belongs in data files; round only display labels.
- Keep the accepted-move counter continuous across sweeps and aggregation levels. Save a mapping from every current supernode to its original club IDs, so every reported partition and Q can be interpreted on the original graph.
- At aggregation boundaries, preserve accumulated internal/inter-community edge weights and self-loops created by aggregation. The transfer-count-weighted graph also needs correctly weighted coarse graphs; treating coarse edges as unit weight changes the optimization problem.
- Record level-boundary and final Q computations separately from accepted moves. An aggregation step does not itself create an accepted move or an artificial jump in Q.
- A no-improvement sweep must be recorded as convergence evidence. Save total candidate evaluations, accepted moves, sweeps, levels, the stopping reason, final community count and final Q.

For reference, score the original directed graph using:

```text
Q = sum over communities C of:
    internal_edge_mass(C) / m
    - gamma * out_degree_mass(C) * in_degree_mass(C) / m^2
```

Use transfer-count weights throughout: `m` is their sum, and out/in degree masses are summed out/in strengths on the full graph. Apply the same normalized definition to the null graph and the Leiden results. Each directed edge contributes once; there is no undirected factor of two.

**Completion check:** every accepted state is a valid partition of all original nodes; canonical and incremental Q agree within numerical tolerance; accepted-state Q is nondecreasing within tolerance; aggregation preserves Q. On small seeded fixtures, the final partition and Q match the unmodified NetworkX algorithm under the same input order and parameters.

## 3. Create the shuffled comparison

1. Reuse the shared shuffled graph if available, verifying its metadata and checksum. Otherwise generate it once for both methods: copy the observed route topology, keep the same node IDs, and randomize endpoints using directed degree-preserving swaps with the shared seeds below.
2. Preserve **each individual club's in-degree and out-degree exactly**, the number of nodes and edges, and a simple loop-free directed graph. Preserve the observed graph itself unchanged.
3. Inspect the installed `nx.directed_edge_swap` implementation before using it. The inspected 3.3 implementation can propose self-loops and drops edge attributes on rewired edges. Use an attributed, loop-free adaptation of its three-edge swap if necessary. Reject proposals with self-loops or existing target edges **before applying them**. Keep valid directed triangle reversals possible; rejecting all repeated endpoints unnecessarily excludes them.
4. Target **10 times the edge count in successful three-edge swaps**, with at most 100 times that target in attempted proposals. Record actual successes and attempts. If it cannot complete, report the failure and investigate; never remove loops or duplicate edges afterward, since that changes degrees.
5. Assign the seeded weight permutation after topology swaps. Verify exact degree dictionaries before/after, absence of self-loops and parallel routes, equality of weight multisets and total weight, and meaningful topology change. Save the shared shuffled weighted edge list, seeds, checksums and fraction of original directed edges retained. The swap count is a practical randomization budget, not proof of uniform sampling or adequate mixing.
6. Run the **same complete instrumented Louvain procedure** on the exact shared shuffled graph with the same optimizer parameters and stopping rule as the observed Louvain run. The required horizontal baseline is its final optimized `Q_shuffled`, not Q for the observed partition evaluated on shuffled edges.

**Completion check:** all preserved invariants hold, both runs have complete traces, and `Q_observed`, `Q_shuffled` and `delta_Q = Q_observed - Q_shuffled` are independently reproducible.

This pooled topology null does not preserve seasons, season-specific league eligibility, geography, ownership, reciprocal ties or player trajectories. It preserves total transfer volume and the global weight distribution, but not club-specific in/out strengths or the association between route topology and transfer volumes. Explain these limits when relating it to the selected joining-rate dataset.

## 4. Name communities and draw the network

For each final observed community, choose the member with the highest full-graph total directed degree. Break ties by the smallest numeric club ID. Its club name is the community's display name, following the Week 4 curriculum convention. Save representative IDs and degrees; disambiguate identical display names with IDs.

Assign one distinct, deterministic colour to every community, identically across PyVis, the static network, legends and tables. Begin with the guide's default palette; extend it with distinct categorical colours if there are more than five communities, without recycling swatches. Reserve blue `#0072B2` for the null-model baseline. Labels and community names must support interpretation beyond colour alone.

- Compute and save one shared observed-graph layout for both methods, or reuse that saved layout if Leiden ran first. Use identical positions in PyVis and publication exports; account for the browser's downward-positive y coordinates.
- Use PyVis `Network(directed=True)` and NetworkX graph data to produce the interactive community view. Keep all original nodes and edges. Show club name, ID, community, in-degree, out-degree and transfer count information in tooltips.
- Default to fixed saved coordinates with physics disabled so opening the page does not change the layout. Embed assets locally or inline so the delivered HTML is usable offline and does not depend on a CDN.
- Size nodes by the declared total-degree measure; draw edges faintly enough to see community colours. Label representative clubs, and show a readable legend containing every community name and its node count. Do not silently discard small communities or hide observations to improve Q.
- Draw the static counterpart using NetworkX and Matplotlib from the same positions, assignments, sizes and colours. This supplies vector publication output; a screenshot of the PyVis canvas is not the PDF source.

**Completion check:** every original club is shown and assigned once, each community has a unique colour, representatives satisfy the ranking rule, and all legends and representative labels are readable. Community names are convenient labels, not claims about the cause or meaning of the grouping.

## 5. Plot Q against accepted moves

- X-axis: **Accepted Louvain moves**, beginning at 0. Y-axis: **Directed weighted modularity, Q**. Use linear axes, integer move ticks and a range that includes the initial Q, final observed Q and shuffled baseline.
- Draw one continuous orange observed trajectory (`#DC831B`) through every recorded accepted-state Q, with small markers indicating the computed states. Do not smooth, interpolate extra observations or substitute hierarchy-level numbers for moves.
- Draw the final shuffled Q as a **solid blue horizontal line (`#0072B2`)** over the full observed move range. Label it **Degree-preserving shuffle (one graph)** with its Q value. This is a single optimized null result, not a null mean.
- Include final observed Q, shuffled Q and total accepted moves in the legend or compact annotations. Keep full counters, delta Q, settings and interpretation in the recap.
- Record level boundaries in the saved trace; if shown on the plot, use restrained annotations that do not compete with the two required lines.

**Completion check:** every curve point is traceable to the progress CSV, the final point matches the detected partition's modularity, and the horizontal baseline matches the separately optimized shuffled graph.

## 6. Three views and deliverables

Use these descriptive stems, with PDF, 600 dpi PNG and editable-text SVG for each static view:

| Plot | Stem | Additional interactive format |
| --- | --- | --- |
| Community network | `louvain_transfer_communities` | Same-stem PyVis HTML |
| Modularity progress and null baseline | `louvain_transfer_modularity_progress` | None required |
| Combined network and Q plot | `louvain_transfer_communities_and_modularity` | HTML containing the same PyVis network and progress SVG |

The combined HTML can embed the existing PyVis HTML and progress SVG; reuse the saved analysis and layout. The static combined view contains the two matching axes, with `(a)` and `(b)` panel titles. These are three plot designs in multiple formats, not additional analyses.

Also save in the deliverable folder:

| File | Required contents |
| --- | --- |
| `communities.csv` | Club ID/name, community ID/name, representative flag, original in/out/total degree, transfer strengths, colour and saved x/y coordinates. |
| `community_summary.csv` | Community size, representative ID/name and degree, and final Q contribution. Contributions must sum to final observed Q. |
| `louvain_progress.csv` | Run (`observed`/`shuffled`), accepted-move index, level, sweep, moved node/supernode ID, represented original-node count, delta Q, actual Q and community count. Include move 0 for both runs. |
| `louvain_q_evaluations.csv` | Run, sequential evaluation ID, evaluation type, level, sweep, node visit, current move count, source/target community, Q before, candidate delta Q, candidate Q and accepted flag. Record initial, candidate, accepted, boundary and final computations with their types; Q verification calls should be tagged separately. |
| `shuffled_routes.csv` | Exact shuffled directed endpoints and `transfer_count` weights, sufficient to reconstruct the null graph. |
| `louvain_results.json` | Input checksum, graph counts, weighting convention, directed flag, resolution, thresholds, seeds, versions, shared graph checksums, shuffle diagnostics, all counters, final Q values, delta Q, community count, convergence reason and verification results. |
| `README.md` | Links to all outputs and reproduction command. |
| `louvain_transfer_communities_caption.md` | Short standalone captions for all three views. |
| `louvain_transfer_communities_summary.md` | Research question, sample, graph/degree definitions, algorithm, counters, null construction, comparison and limitations. |

Use `PLOTTING_STYLE.md` for publication exports. Session preferences superseding its defaults are **9 pt legends**, descriptive filenames, compact combined height around **3.4 inches** where legible, and solid blue null references. Combined width is 7.16 inches; standalone default width is 3.58 inches. A dense network or long community legend may justify more height; verify actual print readability rather than shrinking fonts. Standalone plots have captions outside the plotting area and no internal titles. Embed Arial in PDFs and preserve vector content and intended page dimensions.

## 7. Verification and completion

Implement meaningful tests for the new algorithm instrumentation and shuffle, rather than tests that merely repeat formatting constants:

1. A small asymmetric directed graph with unequal positive weights where candidate delta Q can be checked against explicit NetworkX modularity for each candidate partition, including a rejected proposal. Ensure the fixture detects accidental symmetrization or binarization.
2. A multilevel example verifying original-node membership, Q invariance under aggregation and continuous accepted-move indexing across levels.
3. Seeded parity with the installed unmodified Louvain routine, plus repeat-run equality of partitions, traces and counters.
4. A directed shuffle test verifying every node's in/out degree, edge count, loop-free simplicity, weight-multiset and total-weight preservation, and deterministic output. Include a proposed self-loop rejection and a valid directed triangle reversal.
5. Full-data checks for the input snapshot, exact saved/final Q agreement, complete node coverage and representative naming, preserved degree dictionaries for the shuffled graph, and identical shared-input checksums across Louvain and Leiden.

Render and inspect all publication PDFs in colour and grayscale. Check fonts, page rotation, complete legends, clipped labels, distinct community swatches, and alignment between standalone and combined views. Open the PyVis and combined HTML views and verify offline loading, tooltips, legend completeness and agreement with the saved partition. Ensure a plotting rerun can consume saved analysis outputs without rerunning Louvain or changing assignments.

Completion means the new module runs, the focused checks pass, both optimization runs and their complete traces are saved, all three plot designs exist in their required formats, and the recap and shared comparison report the actual results of both methods under the protocol below. An observed Q above the shuffled Q supports only “higher than this degree-preserving randomized realization.” One shuffle provides neither a null distribution nor evidence of statistical significance. Louvain is heuristic and seed-sensitive; its partition is not a unique or proven optimum. Do not promise the comparison will be positive.

## Shared Louvain-Leiden comparison protocol

This section is the common contract for both plans. The analysis has not been run; no method is presumed to win. The two implementations optimize normalized directed, transfer-count-weighted modularity at `gamma=1.0`, starting from the same singleton partition.

1. **Prepare and save common inputs once.** Use `output/transfer_community_comparison/` for `observed_routes.csv`, `shuffled_routes.csv`, `layout.csv` and `shared_inputs.json`. Save directed endpoint-weight tuples in deterministic order, all original node IDs, input checksum, graph counts, insertion order, seeds, shuffle diagnostics and file checksums. Both modules must accept a `shared_dir` keyword/CLI argument defaulting to this folder. If common inputs exist, verify them against the source data and settings before reuse; do not silently overwrite a different realization. Per-method copies of the null edge list must match the shared checksum.
2. **Use explicit seed streams.** With base seed 2026, use optimizer seed 2026 for each fresh method/graph run, swap seed 2027, weight-permutation seed 2028 and observed-layout seed 2029. For another base seed, use the corresponding offsets. Equal optimizer seeds make runs reproducible within each implementation; they do not create identical random searches across libraries. Compute layout from the same observed weighted graph and reuse the exact positions and node sizes for both community views.
3. **Complete four optimization runs.** Run Louvain and Leiden on the observed graph and on the exact same saved weighted null graph. Each uses its documented convergence rule: Louvain's level threshold, and Leiden's first iteration without positive improvement. Record both rules and package versions. Keep the original single-seed, single-shuffle scope; these runs do not characterize robustness across seeds or a null distribution.
4. **Compare final results on a common scale.** Independently recompute every final Q in NetworkX. Save `method_comparison.csv` with one row per method: observed Q, null Q, observed-minus-null Q, community counts for both graphs, observed community-size distribution, settings and convergence status. Report `Q_Leiden - Q_Louvain` separately for the observed graph and the shared null. The horizontal null baseline in each method's progress plot is that method's own optimized null Q; the graph is shared, the optimized partition need not be.
5. **Compare memberships and connectivity.** Save `community_overlap.csv` with Louvain ID, Leiden ID, intersection size and Jaccard overlap for each nonempty intersection on the observed graph. Include both community sizes so splits and merges are visible; arbitrary numeric labels or representative names must not be treated as matches. Save `community_connectivity.csv` with each observed community's weakly and strongly connected component counts in its induced directed subgraph. Report these as diagnostics; do not turn the Leiden paper's connectivity statements into a promise of strong connectivity for directed routes.
6. **Make the comparison reviewable.** Save `method_comparison.md` linking the two methods' outputs, input checksums, comparison table, overlap table and connectivity diagnostics. Add a static paired community-network view, `louvain_leiden_community_comparison`, in PDF, 600 dpi PNG and editable-text SVG using the shared layout, node sizes, plotting style and readable legends. Colours identify communities within each method; the same swatch across panels does not imply identical membership. Keep the method-specific progress plots separate: Louvain accepted moves and Leiden completed iterations are different units. Instrumentation also differs, so logged runtimes do not establish an algorithm speed ranking.

**Completion check:** all four runs use identical endpoint-weight inputs for each graph, identical initial membership and the same Q definition; comparison tables reproduce the method results; overlap counts cover every observed club once and have correct row/column totals; connectivity diagnostics cover every community; the paired network uses identical coordinates. Q differences are descriptive results for these runs, not significance tests or proof of a globally optimal partition.

## References for the implementing agent

- [Week 4 curriculum: Louvain, naming communities, progress and null comparisons](../../data/week4/).
- [NetworkX Louvain API](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html) and [implementation](https://networkx.org/documentation/stable/_modules/networkx/algorithms/community/louvain.html). Inspect the installed version before adapting it.
- [NetworkX directed modularity](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html).
- [NetworkX directed edge swaps](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.swap.directed_edge_swap.html). Verify loop and attribute behavior in the installed source.
- [PyVis API and NetworkX integration](https://pyvis.readthedocs.io/en/latest/documentation.html).

## Overleaf references

The companion [Leiden plan's citation section](leiden_transfer_communities_plan.md#overleaf-citation-and-section-reference) contains the original Leiden paper's full BibTeX entry, including the user-supplied arXiv URL. Cite it as `\cite{traag2019leiden}` when describing Leiden and comparing the methods. Use `\label{sec:louvain-transfer-communities}` for the Louvain section and `\ref{sec:louvain-transfer-communities}` for internal section cross-references. Literature citations use `\cite`, not `\ref`.

For the directed Louvain adaptation cited by NetworkX, add:

```bibtex
@techreport{dugue2015directedlouvain,
  author      = {Dugué, Nicolas and Perez, Anthony},
  title       = {Directed {Louvain}: maximizing modularity in directed networks},
  institution = {Université d'Orléans},
  year        = {2015},
  number      = {hal-01231784},
  url         = {https://hal.science/hal-01231784}
}
```

Retain the original Louvain method reference linked in the NetworkX documentation, Blondel et al. (2008), *Fast unfolding of communities in large networks*, [DOI 10.1088/1742-5468/2008/10/P10008](https://doi.org/10.1088/1742-5468/2008/10/P10008), when writing the methods section. Record the algorithm sources in the generated summary and README as well.
