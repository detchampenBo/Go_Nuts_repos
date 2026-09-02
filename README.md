# Go_Nuts_repos

A repository for a master's course where we have to go nuts.


ACCESS THE WEBSITE HERE:
https://detchampenbo.github.io/Go_Nuts_repos/index.html

## Visual course library

The root `index.html` is a static GitHub Pages gallery. Visual experiments are linked
from that page; the Marvel project lives in
`showcases/week-01-network-questions/claude/`. Read
[`docs/HOW_THE_SITE_WORKS.md`](docs/HOW_THE_SITE_WORKS.md) for a plain-language map of
how the files fit together and how to add the next week's work.

### Publish with GitHub Pages

In the repository's **Settings → Pages**, choose **Deploy from a branch**, then select
the branch and the `/ (root)` folder. GitHub Pages will serve `index.html` directly.

### Edit the current graph

The first visual is in `showcases/week-01-network-questions`. For normal updates, edit
`showcases/week-01-network-questions/data/source-network.json` and run:

```bash
python showcases/week-01-network-questions/prepare_graph.py
```

Commit both JSON files. The Python step is intentionally small: it provides a place to
add data ingestion and transformations later while keeping the deployed site static.
