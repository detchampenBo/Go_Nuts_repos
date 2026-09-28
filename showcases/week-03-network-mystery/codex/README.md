# The hidden mastermind

A throwaway Week 3 prototype: can three centrality clues become an understandable detective game? Visual direction: a light table with removable evidence sheets. This is a fictional nine-person, fourteen-edge, connected undirected network, not Marvel canon or Wikipedia data.

Open `prototype.html` directly, or serve the repository with `python3 -m http.server 8033` and visit `/showcases/week-03-network-mystery/codex/prototype.html`. Rebuild after source edits with `node showcases/week-03-network-mystery/codex/build.mjs`. No dependencies or persistence are needed at runtime.

## Interaction

Investigate a hero, use the graph tool, and clear one incompatible suspect per clue. Degree lights up direct contacts. Closeness uses BFS layers and the mean distance to all eight other people. Betweenness plays back all 36 unordered network pairs, splits tied shortest-path credit, excludes endpoints, and normalizes each person's score by their 28 eligible pairs.

Filing a deduction unlocks a transparent sheet with the four suspects' measured values and match marks. Sheet visibility is independent of filed evidence. Lift any sheet, lift all, or restack them; none of these actions changes the case result. The final accusation retains the map so all three sheets can be compared together. Distinct inks and circle dash patterns supplement explicit check/cross marks and the accessible evidence register.

## Visual direction

The user selected transparent evidence sheets after rejecting generic comic styling. Keep the mathematical game and original character portraits. Replace neon outlines, tilted labels, halftones and oversized repeated cards with an aligned light-table surface, tabbed files, a compact portrait strip and registered overlays.

Palette: cool paper #f5f7f1, table #e1e7df, forest ink #263c30, contact blue #315a91, distance ochre #987024, traffic terracotta #8f4c43. Palatino gives the case title a printed-document voice; Avenir/Segoe UI carries controls and measurements. Character portraits are original SVG drawings with restrained colour. Existing gameplay uses fixed node positions within each viewport.

Reference research (pages and image-search previews inspected; no source artwork incorporated):
- [The Met: Josef Albers, Interaction of Color](https://www.metmuseum.org/art/collection/search/737721): mounted paper studies and cutouts; transfer the idea of independent evidence leaves occupying a shared composition.
- [David Rumsey Georeferencer](https://www.davidrumsey.com/view/georeferencer): registered map overlays and comparison modes; transfer fixed landmarks and reversible layer visibility.
- [DIC Kawamura, Albers exhibition](https://kawamura-museum.dic.co.jp/art/exhibition-past/2023/albers/): image-search preview of overlapping paper circles informed translucent rings. The full page could not be retrieved; this is a limited reference.

The user already chose the direction, so three alternative directions were not reopened. Composition sketch: case introduction → evidence tabs → clue at left and registered contact map at right → compact suspect strip → evidence register. Mobile puts the clue above the map.

## Verification and limits

Independent Floyd–Warshall distances matched all 81 BFS distances. Independent path enumeration matched all nine betweenness scores and closeness calculations. Each clue excludes a different suspect: one clue leaves three, any pair leaves two, all three leave one.

Browser verification covered the full case, empty deduction feedback, degree and distance measurements, traffic totals, sheet creation, individual and collective lifting, unchanged deductions while sheets are hidden, final accusation, reset, and a 390px viewport without horizontal overflow. No JavaScript errors occurred in that playthrough. Desktop and mobile screenshots were reviewed; faint annotations during repeated fade animation were corrected, and mobile labels enlarged. Files are in `output/playwright/evidence-*.png`.

This does not establish that users find the game intuitive or its style distinctive; those remain user-evaluation questions. Archive branch: `prototype/week-03-network-mystery`. Git capture remains deferred after the earlier declined staging request. No external issue was supplied.

## Designer's solution (spoilers)

| Suspect | Degree | Mean distance | Closeness | Betweenness |
| --- | ---: | ---: | ---: | ---: |
| Black Widow | 3 | 1.625 | 0.6154 | 14.2857% |
| Spider-Man | 5 | 1.500 | 0.6667 | 11.9048% |
| Daredevil | 3 | 1.875 | 0.5333 | 26.1905% |
| Wolverine | 3 | 1.750 | 0.5714 | 0% |

The clues require degree 3, mean distance at most 1.75, and betweenness at least 10%. Their intersection is Black Widow. The lesson is that the measures answer different questions, not that the culprit has the largest value of every measure.

Course: [Week 3 — Who matters, and why](https://sunelehmann.com/socialgraphs2026-web/weeks/week3.html). This prototype focuses on three centralities and BFS rather than the full week's topics.

## Character-art revision

The ink-headshot experiment was reverted at the user's request. The previous coloured SVG portraits and their restrained dossier treatment are restored; the transparent evidence sheets and game mechanics remain unchanged.
