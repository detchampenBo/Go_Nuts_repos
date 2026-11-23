"""Create isolated producer copies, changing only input/output and snapshot plumbing."""
import difflib
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]


def main():
    target = RUN / "notebooks"
    target.mkdir(exist_ok=True)
    changes = {}
    for name in ["transfer_community_inputs.py", "transfer_community_outputs.py",
                 "louvain_transfer_communities.py", "leiden_transfer_communities.py",
                 "compare_transfer_communities.py"]:
        source = REPORT / "notebooks" / name
        original = source.read_text(encoding="utf-8")
        text = original
        if name in {"transfer_community_outputs.py", "compare_transfer_communities.py"}:
            text = text.replace("python -B pnas_report/notebooks/",
                                "python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/")
        if name == "transfer_community_inputs.py":
            text = text.replace('REPORT / "data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz"',
                                'REPORT / "data/outsideprem_toprem_eligible_transfers.csv.gz"')
            text = text.replace('== sample["eligible_transfer_records"] == 19712',
                                '== sample["eligible_transfer_records"] == restricted["rows"]')
            text = text.replace('== sample["distinct_players"] == 5213',
                                '== sample["distinct_players"] == restricted["players"]')
            text = text.replace('== (1254, 12794)', '== (restricted["clubs"], restricted["directed_routes"])')
            text = text.replace('        sample = saved["all_eligible_transfers"]["sample_counts"]',
                                '        restricted = json.loads((REPORT / "provenance/reduction_manifest.json").read_text())["restricted"]\n'
                                '        require(checksum(transfers_path) == restricted["sha256"], "Restricted input hash differs")\n'
                                '        sample = saved["all_eligible_transfers"]["sample_counts"]')
        (target / name).write_text(text, encoding="utf-8")
        changes[name] = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "copy_sha256": hashlib.sha256((target / name).read_bytes()).hexdigest(),
                         "diff": list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                                         fromfile="original/" + name, tofile="rerun/" + name))}
    notebook = json.loads((REPORT / "notebooks/exploration_v3.ipynb").read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        text = "".join(cell["source"])
        text = text.replace("pnas_report/data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz",
                            "pnas_report/reruns/h1_2012_13-2024_25/data/outsideprem_toprem_eligible_transfers.csv.gz")
        text = text.replace("pnas_report/output/", "pnas_report/reruns/h1_2012_13-2024_25/output/")
        text = text.replace("pnas_report/figures/", "pnas_report/reruns/h1_2012_13-2024_25/figures/")
        cell["source"] = text.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
    (RUN / "figures").mkdir(exist_ok=True)
    (target / "exploration_v3.ipynb").write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    (RUN / "provenance/source_adaptations.json").write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
