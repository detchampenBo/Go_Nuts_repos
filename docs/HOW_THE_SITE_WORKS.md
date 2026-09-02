# How this site works

This repository is a small library of visual course work. It is designed so that a new
visual can be added each week without changing or breaking earlier ones.

You do not need to be a programmer to understand the roles below. Think of the site as
a gallery: the front page is the gallery entrance, and each linked subfolder is an
individual exhibition.

## The folder map

```text
Go_Nuts_repos/
├── index.html                         The gallery entrance shown by GitHub Pages
├── site-index.css                     The appearance of that entrance page
├── showcases/                         Additional visual experiments
│   ├── README.md                      Short checklist for adding a new showcase
│   └── week-01-network-questions/     The first showcase
│       ├── codex/                     Codex's solution page and supporting files
│       ├── claude/                    Claude's solution page and supporting files
│       ├── data/
│       │   ├── source-network.json    The editable source information
│       │   └── graph-data.json        The prepared information used by the page
│       └── prepare_graph.py           Turns source information into display information
├── docs/                              Plain-language documentation
└── README.md                          Publishing instructions and a project overview
```

## What happens when someone visits the site

1. GitHub Pages opens the root `index.html` file. This is the course's gallery page.
2. A person finds a weekly showcase card, such as **Network questions**.
3. The card offers a button for each solution. Week 01 has **Codex solution** and
   **Claude solution**.
4. A solution page opens its own `index.html` file and any supporting files in the same
   solution folder.
5. The interactive graph reads `data/graph-data.json`. This is the file that the browser
   understands and displays.

In short: **source data → preparation → display data → interactive visual**.

## Updating the current network visual

For normal content changes, open
`showcases/week-01-network-questions/data/source-network.json`. It contains the names,
questions, and connections in the network. Change that file first.

Then run this one command from the repository folder:

```bash
python showcases/week-01-network-questions/prepare_graph.py
```

It refreshes `graph-data.json`, which is the version used by the website. Commit both
files together so the source and the displayed result stay in sync.

The Python file currently only adds stable positions and colours. Later, it is the right
place to load a spreadsheet, combine several data sources, calculate network measures,
or clean data before the site displays it. GitHub Pages still only needs to serve the
finished files, so no server is required.

## Adding next week's visual

1. Create a new folder in `showcases`, using a readable name such as
   `week-02-mobility-patterns`.
2. Create a separate subfolder for each solution inside it. Put the page and everything
   it needs inside the relevant solution folder. A simple visual can have just an
   `index.html` file; a richer one can also have its own `styles.css`, `script.js`, data,
   and Python preparation file.
3. Add one weekly showcase card to the root `index.html`, with one clear button for each
   solution, so visitors can compare the approaches.
4. Open the page locally and check that it looks right before pushing it.
5. Push the files to the GitHub branch used by Pages. The published gallery will update.

Keeping each showcase self-contained means one week's work can evolve freely without
accidentally changing another week's visual.

## What to edit—and what to leave alone

| If you want to… | Start with… |
| --- | --- |
| Change the gallery title or add a showcase card | Root `index.html` |
| Change the gallery colours or spacing | `site-index.css` |
| Change the words or connections in a graph | That showcase's `data/source-*.json` file |
| Change how a visual looks | That showcase's `styles.css` file |
| Change what happens when a visitor clicks | That showcase's `script.js` file |
| Bring in or calculate new data | That showcase's Python file |
| Understand this system later | This guide |

## A note on names

Use names that explain the idea rather than the tool. `week-03-community-bridges` is
better than `week-03-final` or `new-graph`. The folder name becomes part of the public
web address, so a clear name also makes the link easier to share.
