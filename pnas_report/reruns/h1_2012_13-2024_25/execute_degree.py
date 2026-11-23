"""Execute the redirected original notebook and save its derived tables."""
import json
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

RUN = Path(__file__).resolve().parent
path = RUN / "notebooks/exploration_v3.ipynb"
notebook = nbformat.read(path, as_version=4)
notebook.cells.append(nbformat.v4.new_code_cell('''
assert graph.number_of_nodes() == 1157
assert graph.number_of_edges() == 11016
assert graph.size(weight='weight') == len(data_full) == 16636
degree_df.to_csv(OUTPUT_DIR / 'club_degrees.csv', index=False)
network_summary.to_csv(OUTPUT_DIR / 'network_summary.csv')
pd.DataFrame([(node, *pos[node]) for node in graph], columns=['club_id', 'x', 'y']).to_csv(OUTPUT_DIR / 'network_layout.csv', index=False)
'''))
manager = KernelManager(kernel_name="python3")
manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
client = NotebookClient(notebook, km=manager, timeout=600,
                        resources={"metadata": {"path": str(RUN.parents[2])}})
try:
    client.execute()
finally:
    nbformat.write(notebook, path)
print("Executed redirected notebook:", path)
