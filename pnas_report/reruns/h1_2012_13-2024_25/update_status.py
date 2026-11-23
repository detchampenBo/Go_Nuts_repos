"""Update the run index at execution boundaries; never resolve a review issue."""
from pathlib import Path
import sys

run = Path(__file__).resolve().parent
number, state, message = sys.argv[1:]
path = run / "README.md"
lines = path.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if line.startswith(f"| {number} |"):
        cells = line.split("|")
        cells[-2] = " " + state + " "
        lines[index] = "|".join(cells)
        break
start = next(index for index, line in enumerate(lines) if line == "## Current checkpoint") + 2
end = next(index for index in range(start, len(lines)) if lines[index].startswith("## "))
lines[start:end] = [message, "", "Status is updated here at stage boundaries; actual commands and checks are in [the execution log](provenance/run_log.md). Execution verification is separate from user satisfaction confirmation. Original Issue 02 remains Open.", ""]
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
with (run / "provenance/run_log.md").open("a", encoding="utf-8") as handle:
    handle.write(f"\n\n20 November 2026 — Stage {number}: {state}. {message}\n")
