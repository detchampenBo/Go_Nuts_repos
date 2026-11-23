# Restricted H1 execution log

## User confirmation and closure — 21 November 2026

The user confirmed that they verified and accepted the current computations and new results and asked to close all 12 rerun issues. The primary feeder figure uses a 7-transfer minimum and the alternate uses 6. This closure records acceptance of the saved work. Raw R agreement remains 29/30 and live browser interaction remains unverified. The next paper task is [Issue 02 — Reconcile transfer and text samples](../../../paper_simple/scratch/2026-11-19_15-30-34_02-reconcile-samples-and-data-provenance.scratch).

## Resume and saved input/H1 verification — 21 November 2026

The user resumed the restricted reruns. Dispatched `/root/h1_resume` with `fork_turns="none"` to review the backbone discrepancy first. The planning agent used a read-only standard-library audit via `python -B -` from the repository root to compare SHA-256 against the reduction, H1 and baseline manifests. All three original input/lookup hashes, four reduction artifacts, 14 H1 artifacts and 124 frozen original output/figure hashes matched. Prior independent reduction/H1 verification remains current; no producer or H1 permutations were rerun in this step.

### Stage 10 boundary diagnosis

The fresh agent independently matched the saved restricted data against the ordered 16,636-row subset of the original. The agent used a PowerShell here-string piped to `conda run -n machine-learning --no-capture-output python -B -` to load `load_inputs`, `score_scope` and `reference_check` via `runpy.run_path`, then replayed the single saved scope/cutoff and the two-edge fixture. The agent ran `conda run -n network_analysis --no-capture-output Rscript --vanilla pnas_report/reruns/h1_2012_13-2024_25/provenance/inspect_disparity.R` and a fixture through `conda run -n network_analysis --no-capture-output Rscript --vanilla -`. The strict R comparison was confirmed. Its normalized arithmetic yields 0.19999999999999996; exact 1/5 equals the specified cutoff and the Python comparison excludes it. Raw R parity remains 29/30. No scoring or cutoff changed. [Diagnosis](backbone_boundary_diagnosis.json)

### Stage 08 ownership decision

The user requested screening the 28 new routes before the handoff. These routes account for 68 of the 626 selected transfer records. The screen uses the existing common-equity definition and interval criteria. The original ownership sources and prior manual group decisions are preserved.

The two research agents screened all 28 route keys against dated primary sources and matched all 68 events to the saved route/event tables. The existing scope includes 189 routes from the reused audit. Some additional keys appeared in that audit's earlier 334-route narrative and were reviewed again. The additional review found no verified common-equity interval. The coverage ledger preserves the original reuse flag and records the new screen status. The 16 confirmed intervals and two authorized manual inclusions were retained. [Source review](ownership_screen_28_routes.md) · [Coverage ledger](ownership_coverage_ledger.csv)

The fresh execution agent ran `conda run -n machine-learning --no-capture-output python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/premier_league_feeder_ownership_audit.py` and repeated it once after syncing the final source citations. All eight stamped input hashes match. The 626-row event CSV is byte-identical to the pre-screen output (SHA-256 `c965bc15fd2a13ab65bb65b5863c6b0f86cc549f9ae99129f589942a7f212281`). The destination table and screening-note paths were checked. Counts are 217 screened, 16 documented pairs, 15 pairs with concurrent events, 62 concurrent events, and 17 routes in the plotted group (85 pooled records). The original broad-sample snapshot warning was expected. No feeder permutations ran. [Ownership results](../output/premier_league_feeder_ownership_results.json)

### Stages 02 and 03 saved-output verification

The fresh agent used read-only `python -B -` checks to reconcile every route, weight and club degree with the restricted input, and compare the shared files with their saved hashes. The 1,157-club graph has 11,016 directed routes and weight 16,636. Degree maxima are 128, 136 and 104 for incoming, outgoing and reciprocal connections. The notebook's seven populated cells have saved execution results, including the final totals check. The network and combined degree PNGs were inspected and both compatibility PNGs match their corresponding publication exports byte for byte. Added the run-local recap and figure README using checked values.

The saved null has no loops or duplicate routes, preserves every in/out degree and the global weight multiset, and retains 1,988 observed routes after the recorded 110,160 successful swaps. Shared layout coverage, finite coordinates, hashes and seeds were checked. No notebook or shared-null producer was rerun.

### Stages 04–06 saved-output verification

The fresh agent used `conda run -n machine-learning --no-capture-output python -B -` to independently score directed weighted modularity of the four saved partitions and check membership, summary statistics, progress and input/layout hashes. Louvain Q is 0.4456384395 observed and 0.2125154743 shuffled. Leiden Q is 0.4481771911 observed and 0.2154084036 shuffled. All seven required comparison exports are present. The 15 overlap cells account for all 1,157 clubs. Each method has five weakly connected observed subgraphs and none are strongly connected. The combined Louvain, combined Leiden and side-by-side comparison PNGs were inspected. No optimizer or comparison producer was rerun.

Corrected reproduction commands in the three saved community documents and their run-local generators. The commands now target the restricted producers. The adaptation manifest records the two source changes.

### Stage 10 saved-export verification

The fresh agent used `conda run -n machine-learning --no-capture-output python -B -` to verify 17,695 scoped endpoint scores, 606 retention/fragmentation rows, 2,314 layout rows and the complete embedded HTML dataset. The HTML uses a strict comparison and no external script source. The publication view was inspected. Of 34 files hashed in the backbone run record, 32 remain exact. The two differences are the Louvain README and community comparison Markdown, where the reproduction commands were corrected after execution. The pre-edit hashes remain in the results JSON. Live browser QA was unavailable because the browser tool stopped when it could not verify the current Windows URL.

### Stage 07 saved-output verification

The fresh agent independently rebuilt the season-specific arrivals and calculated observed and expected counts for all 11,448 tested pairs using read-only `python -B -` checks. All saved p-values agree with the reported upper-tail counts and plus-one correction. Selection gives 296 unadjusted p < 0.05 pairs, including 217 recurring routes and 626 records. The saved run documents repeatability with the same seed. No permutations ran in this resume check. The saved Markdown was corrected to reflect the restricted seasons and to link the original proposal accurately.

### Stage 09 feeder publication exports

The fresh agent ran `conda run -n machine-learning --no-capture-output python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_premier_league_feeder_findings.py`. The three displayed routes and 17/200 group sizes agree with the saved results. The capsule caption now explains the two manual inclusions and the bounded screen. With `python -B -` and PyMuPDF 1.28.2, rendered the three source PDFs using `page.get_pixmap(matrix=fitz.Matrix(2, 2))`. The 1032×663 combined and both 516×663 standalone previews were visually inspected. Verified PDF fonts, editable SVG text, PNG dimensions and compatibility figure content.

### Stage 11 artifact inventory and paper evidence

Ran the final audit via `python -B -` from the repository root. Checked all 124 expected paths, 124 original hashes, ordered CSV schemas and top-level JSON keys. Verified 20 single-page PDFs, 29 PNGs, 20 SVGs and generated Markdown links. The audit rechecked four reduction hashes, 14 H1 hashes and eight ownership input hashes. The final manifest lists the seven supplemental exports and both documentation-only hash changes in the historic backbone input inventory. [Verification report](output_parity_report.md) · [Final SHA-256 manifest](final_outputs_manifest.json)

### Stage 09 display cutoff update, 21 November 2026

The user selected 7 transfers as the primary panel (a) minimum and asked for a separate 6-transfer PDF. The fresh agent ran `conda run -n machine-learning --no-capture-output python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_premier_league_feeder_findings.py` using Python 3.11.16 and Matplotlib 3.11.1. A second plotting run added room for the alternate legend. The final exports show six primary bars and 13 alternate bars. The primary remains 7.16 × 4.6 inches. The alternate is 7.16 × 7.4 inches. Both retain the same panel (b) curves and 17/200 group counts. The standalone panel (b) PNG exactly matches its prior hash.

Both PDFs and the refreshed primary compatibility and standalone figures were checked. With PyMuPDF 1.28.2 and `Matrix(2, 2)`, the agent regenerated the three saved primary QA PNGs. Feeder inputs and all 124 frozen original artifact hashes match. The final manifest now includes the alternate as an eighth supplemental output. [Primary PDF](../output/premier_league_feeder_findings/combined.pdf) · [Alternate PDF](../output/premier_league_feeder_findings/combined_min_6.pdf)

## PAUSED for shutdown — 20 November 2026

User explicitly requested pause and shutdown handoff. Planning agent interrupted the execution subagent and confirmed no active Python/conda/R computation. Do not resume until instructed. Saved results/partial outputs are preserved; all 124 frozen original artifacts were rechecked unchanged. [PAUSE_CHECKPOINT.md](../PAUSE_CHECKPOINT.md) is the authoritative current handoff; older “running” entries below are historical.

Actual saved backbone_results.json contains 30 R comparisons, one failed, `r_parity_passed=false`: scope 1, alpha .20, R-only route 210→6574 weight4, R329/Python328 routes. Floating-point boundary explanation is a hypothesis, not completed diagnosis. Python exports are saved but not parity-verified. Ownership ledger/scoping saves 217 selected/189 previously screened/28 new unscreened routes; no new research performed. Resume in a NEW fresh-context agent, review boundary evidence first, and discuss ownership evidence coverage. No analysis rerun was performed by the planning agent while preparing this checkpoint.

2026-11-20 16:38:41 Europe/Copenhagen: Created issues and froze 124 original artifact hashes/schemas. No statistical/structural rerun yet.

Data reduction, executed by the planning agent before the fresh-agent requirement:

```powershell
python pnas_report/reruns/h1_2012_13-2024_25/reduce_h1_data.py
```

Environment: existing Python 3.12; only standard library used. Exact version/script hash in reduction_manifest.json. Verified exact saved roundtrip, field/order preservation, unique keys, explicit source-season membership, real-club/non-PL origins and original source checksum preservation. A fresh agent must independently verify this artifact before downstream runs. Append ACTUAL commands, environments, outcomes and blockers; issue instructions are not execution evidence.


## Fresh-context execution, 20 November 2026

Dispatched as /root/restricted_h1_reruns with fork_turns=none. Read saved paper/index/issues/provenance; independently reproduced data reduction before statistics.

Actual commands from repository root:

```powershell
python pnas_report/reruns/h1_2012_13-2024_25/reduce_h1_data.py
conda run -n machine-learning --no-capture-output python -X faulthandler pnas_report/notebooks/age_shuffle_outsideprem_toprem.py --transfers-path pnas_report/reruns/h1_2012_13-2024_25/data/outsideprem_toprem_eligible_transfers.csv.gz --output-dir pnas_report/reruns/h1_2012_13-2024_25/output
conda run -n machine-learning --no-capture-output python pnas_report/reruns/h1_2012_13-2024_25/verify_h1.py
python pnas_report/reruns/h1_2012_13-2024_25/record_progress.py
```

Environment: machine-learning Python 3.11.16; NumPy 2.4.6, Matplotlib 3.11.1, pandas 3.0.5, NetworkX 3.6.1, igraph 0.11.8, nbformat 5.11.1, nbclient 0.11.0. Reduction uses base Python 3.12. Direct unactivated executables in machine-learning and network_analysis initially terminated during plotting; faulthandler identified native Windows DLL exception 0xc06d007f in Matplotlib's bar geometry. Activated conda run resolved the failure; no statistical/plotting changes. Historical _verify_snapshot warnings expected, separately checked against restricted manifest. Original H1 producer unchanged; verify_h1.py generates data-derived recaps and independently verifies every result. Extra artifact: sensitivity membership CSV. Main p=.098, sensitivity p=.074; all 14 H1 exports present, combined plot inspected, 124 original hashes unchanged. Issues remain pending user satisfaction confirmation.



20 November 2026 — Stage 02: Computed; recap/QA pending. Reduction and H1 independently verified (main p=0.098, player sensitivity p=0.074). Redirected degree notebook and shared null completed. Louvain/Leiden completed with Q=0.445638440/0.448177191; export verification pending. Comparison running. Feeder statistics computed: 217 selected routes/626 records; ownership coverage assessment next. R parity dependency under investigation.


20 November 2026 — Stage 03: Computed; cross-stage verification pending. Reduction/H1 verified. Degree notebook and shared null computed; original inputs/results preserved. Louvain/Leiden computed and comparison running. Feeder statistics computed; ownership coverage assessment next.


20 November 2026 — Stage 04: Computed; export verification pending. Reduction/H1 verified. Degree/shared null and both community methods computed; comparison running. Feeder statistics computed; ownership coverage assessment next.


20 November 2026 — Stage 05: Computed; export verification pending. Reduction/H1 verified. Degree/shared null and both community methods computed; comparison running. Feeder statistics computed; ownership coverage assessment next.


20 November 2026 — Stage 06: Running. Reduction/H1 verified. Degree/shared null and both community methods computed; comparison running. Feeder statistics computed; ownership coverage assessment next.


20 November 2026 — Stage 07: Computed; artifact verification pending. Reduction/H1 verified. Degree/shared null and both community methods computed; comparison running. Feeder: 217 selected recurring routes, 626 events, 2,396 PL arrivals. Ownership evidence joins/coverage next; R parity dependency under investigation.
