# Straightforward graph datasets for the course project

27 October 2026. Selection criterion: a downloadable edge list with a clear edge meaning, manageable size, useful node labels, and a question that can be tested against a network null model. These are historical snapshots; they should not be described as current social behavior.

## Recommended: SNAP email-Eu-core

[Stanford SNAP's dataset page](https://snap.stanford.edu/data/email-Eu-core.html) provides two small files: directed email links and a department label for each person. A node is an anonymized member of a European research institution. An edge `u → v` means `u` sent `v` **at least one** email within the institution; it is not an email count or a measure of tie strength. SNAP reports 1,005 nodes, 25,571 edges, and 42 departments. External correspondents are excluded.

**Focused question:** Are within-department email links more common than expected after preserving each person's number of distinct outgoing and incoming contacts? Compute the observed within-department edge share or categorical assortativity, compare it with directed degree-preserving rewires, and inspect which departments contribute most to the difference. A secondary check could compare detected communities with department labels, but departments are organizational labels, not proof of actual social communities. Verify node IDs, duplicate/self edges, labels for isolates, and whether the rewiring leaves the directed degree sequence intact. Avoid claiming anything about email volume, work quality, or present-day institutions.

This is the best first choice: the edge has a direct behavioral meaning, both files are ready to join on node ID, and the null model gives the project a real mathematical comparison without elaborate data collection.

## Alternative: SocioPatterns high-school contacts

[SocioPatterns' original download page](https://sociopatterns.org/datasets/high-school-dynamic-contact-networks/) provides contact lists and student metadata for a French high school. The 2012 sample covers five classes over seven days. Each row records an observed face-to-face proximity contact between two anonymized students during a 20-second interval; metadata supply class and gender. The authors' [study](https://sociopatterns.org/assets/papers/fournet2014.pdf) notes that only participating students are represented.

**Focused question:** Do within-class contacts remain overrepresented relative to a null model preserving each student's number of contacts, and does that pattern change by day? Make an undirected edge when two students have any recorded contact in a chosen day; optionally weight it by the number of 20-second intervals. Keep daily snapshots separate before aggregating. Verify timestamps, symmetric pair handling, student metadata, and observation windows. This is more intuitive than email, but temporal aggregation is a modeling choice and prior work already establishes strong class mixing, so the paper should emphasize a clear comparison rather than rediscover that fact.

## Third option: 2005 political-blog hyperlinks

[Mark Newman's network-data archive](https://public.websites.umich.edu/~mejn/netdata/) hosts the Adamic–Glance directed political-blog network in GML. A node is a US political blog and a directed edge is a hyperlink to another blog. The [original authors' paper](https://www.ambuehler.ethz.ch/CDstore/www2005-ws/workshop/wf10/AdamicGlanceBlogWWW.pdf) studies liberal/conservative linking, so a basic polarization result is established prior art. An extension could compare reciprocity within and across political labels with a directed-degree-preserving baseline. Inspect the GML node labels and parallel links before calculating. This is easy to load but old and heavily studied; use it if the topic is more engaging than organizational email.

## Recommendation

Start with **email-Eu-core**. The smallest viable project is one edge list, one department-label file, a directed mixing matrix, and a directed-degree-preserving null comparison. Add community detection only if it answers a second, explicit question. A force-directed drawing or a centrality ranking alone would be a weak result.
