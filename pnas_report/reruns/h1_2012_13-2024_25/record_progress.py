"""Record verified execution milestones without resolving user-review issues."""
from pathlib import Path

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1] / "paper_simple"


def append(path, text):
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n\n" + text + "\n")


def milestone(number, text):
    issue = next((RUN / "scratch").glob(f"*_{number}-*.scratch"))
    content = issue.read_text(encoding="utf-8")
    content = content.replace("## Status\n\nOpen", "## Status\n\nExecution verified; user satisfaction confirmation pending", 1)
    content = content.replace("## Status\n\nIn progress", "## Status\n\nExecution verified; user satisfaction confirmation pending", 1)
    issue.write_text(content + "\n\n20 November 2026 — " + text + "\n", encoding="utf-8")


if __name__ == "__main__":
    milestone("00", "Fresh-context agent /root/restricted_h1_reruns independently executed reduce_h1_data.py. Exact deterministic compressed SHA-256 reproduced (48247e435eb0256405f778cafcfdba4eea39651a009fa61f88c41c907d36055a), including retained/excluded rows, fields and order. Counts match the manifest; no July 2025 records removed.")
    milestone("01", "Unchanged original H1 producer completed via activated machine-learning environment. Independent verify_h1.py exactly recomputed both 999-permutation distributions, tail/tie counts, stratum counts and fresh restricted-player draw; selection membership saved in provenance/h1_sensitivity_selected_rows.csv. Main: 2,267/15,573 under30 vs 129/1,063 older; gap −2.421780853 pp, null −1.314527914 pp, tail 97 (15 ties), p=0.098. Sensitivity: 925/4,310 vs 57/292; gap −1.941168992 pp, null +0.458181539 pp, tail 73 (27 ties), p=0.074. All 14 artifacts exist; combined PNG visually inspected without clipping. All 124 frozen original hashes remain unchanged. Historical snapshot warnings remain labelled as historical. No method/plot changes; recaps generated from new results. See provenance/h1_verification.json.")
    index = RUN / "README.md"
    content = index.read_text(encoding="utf-8")
    content = content.replace("No statistical/structural rerun is complete. Next: fresh agent verifies issue 00 artifacts and executes issue 01's H1 and fixed-player sensitivity, keeping original settings. Other stages follow dependencies below. Original Issue 02 stays Open; no new H1 p value or partition is available.", "Fresh-context reduction and H1 execution are verified. Main gap −2.42 pp (p=0.098); new fixed one-transfer-per-player gap −1.94 pp (p=0.074). All 14 H1 artifacts and exact independent permutation verification are saved; all 124 original hashes remain unchanged. Next: network/degree and shared community inputs, then dependent analyses. Original Issue 02 remains Open; user satisfaction confirmation is pending.")
    content = content.replace("Reduction verified; fresh review pending", "Execution verified; confirmation pending")
    content = content.replace("| 00 |", "| 00 |", 1)
    content = content.replace("| 00 | Approved", "| 00 | Approved")
    content = content.replace("| 00 | Open; not run |", "| 00 | Execution verified; confirmation pending |", 1)
    index.write_text(content, encoding="utf-8")
    evidence = """### Fresh-context restricted H1 execution: 20 November 2026

The new agent independently reproduced the restricted input hash and reran the original H1 implementation with unchanged settings. Main joining rates are 2,267/15,573 (14.56%) under 30 and 129/1,063 (12.14%) aged 30+, gap −2.42 percentage points; lower-tail permutation p=0.098 (97 of 999 shuffled gaps at or below observed, including 15 ties; plus-one correction). The new fixed uniform draw of one restricted eligible transfer for each of 4,602 players gives 925/4,310 (21.46%) and 57/292 (19.52%), gap −1.94 points and p=0.074 (73 tail draws including 27 ties). Neither p value falls below 0.05. These replace broad-period H1 findings for the approved scope; H2/H2b/coverage/validation remain unchanged and use separate samples.

Sources: [new results JSON](../reruns/h1_2012_13-2024_25/output/age_shuffle_outsideprem_toprem_results.json), [new summary](../reruns/h1_2012_13-2024_25/output/age_shuffle_outsideprem_toprem_summary.md), [figures and captions](../reruns/h1_2012_13-2024_25/output/age_shuffle_outsideprem_toprem_findings/README.md), [exact independent verification](../reruns/h1_2012_13-2024_25/provenance/h1_verification.json), [new sensitivity membership](../reruns/h1_2012_13-2024_25/provenance/h1_sensitivity_selected_rows.csv). All 124 frozen original artifact hashes passed preservation verification. No issue is resolved without satisfaction confirmation. Next: network/degree and shared community inputs, followed by dependent reruns.
"""
    append(PAPER / "evidence_and_sources.md", evidence)
    checkpoint = PAPER / "README.md"
    content = checkpoint.read_text(encoding="utf-8")
    content = content.replace("No new statistical/structural result is yet available.", "Fresh-context H1 execution is now verified: main gap −2.42 pp, p=0.098; fixed new one-transfer-per-player sensitivity −1.94 pp, p=0.074. [Verification](../reruns/h1_2012_13-2024_25/provenance/h1_verification.json) confirms exact independent recomputation, all 14 H1 exports and unchanged original hashes.")
    content = content.replace("Exact next execution: verify", "Initial required execution (now verified): verify")
    append(checkpoint, "20 November 2026 execution update: reduction and H1 are independently verified by the new fresh-context agent. Next execution is network/degree and shared community inputs, then their dependencies. Original Issue 02 stays Open; all resolutions await user confirmation.")
    checkpoint.write_text(content + "\n\n20 November 2026 execution update: reduction and H1 are independently verified by the new fresh-context agent. Next execution is network/degree and shared community inputs, then their dependencies. Original Issue 02 stays Open; all resolutions await user confirmation.\n", encoding="utf-8")
    append(RUN / "provenance/run_log.md", """## Fresh-context execution, 20 November 2026

Dispatched as /root/restricted_h1_reruns with fork_turns=none. Read saved paper/index/issues/provenance; independently reproduced data reduction before statistics.

Actual commands from repository root:

```powershell
python pnas_report/reruns/h1_2012_13-2024_25/reduce_h1_data.py
conda run -n machine-learning --no-capture-output python -X faulthandler pnas_report/notebooks/age_shuffle_outsideprem_toprem.py --transfers-path pnas_report/reruns/h1_2012_13-2024_25/data/outsideprem_toprem_eligible_transfers.csv.gz --output-dir pnas_report/reruns/h1_2012_13-2024_25/output
conda run -n machine-learning --no-capture-output python pnas_report/reruns/h1_2012_13-2024_25/verify_h1.py
python pnas_report/reruns/h1_2012_13-2024_25/record_progress.py
```

Environment: machine-learning Python 3.11.16; NumPy 2.4.6, Matplotlib 3.11.1, pandas 3.0.5, NetworkX 3.6.1, igraph 0.11.8, nbformat 5.11.1, nbclient 0.11.0. Reduction uses base Python 3.12. Direct unactivated executables in machine-learning and network_analysis initially terminated during plotting; faulthandler identified native Windows DLL exception 0xc06d007f in Matplotlib's bar geometry. Activated conda run resolved the failure; no statistical/plotting changes. Historical _verify_snapshot warnings expected, separately checked against restricted manifest. Original H1 producer unchanged; verify_h1.py generates data-derived recaps and independently verifies every result. Extra artifact: sensitivity membership CSV. Main p=.098, sensitivity p=.074; all 14 H1 exports present, combined plot inspected, 124 original hashes unchanged. Issues remain pending user satisfaction confirmation.
""")
