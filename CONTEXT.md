# Hero Link Network

This context describes the directed Wikipedia-link snapshot used in the week 01 hero-network showcase and notebook.

## Language

**Hero article**:
A node representing one Wikipedia article for a Marvel Comics superhero in the frozen dataset.
_Avoid_: Character node, hero page

**Hero link**:
A directed edge from the article containing a link to the hero article being linked.
_Avoid_: Connection, relationship

**Inbound degree**:
The number of hero links directed to a hero article.
_Avoid_: Popularity, importance

**Outbound degree**:
The number of hero links directed from a hero article to other hero articles.
_Avoid_: Reach, influence

**Reference constellation**:
The thresholded global graph view, in which visible hero articles are selected by inbound degree.
_Avoid_: Full graph, network map

**Selected hero**:
The hero article chosen by search or direct interaction, whose direct inbound and outbound hero links are highlighted.
_Avoid_: Focus node, active character

**Spider-Man graph frame**:
The visual entry state placed directly after the page introduction, where a Spider-Man widget launches the data-morphing web before the reference constellation becomes interactive.
_Avoid_: Hero banner, page illustration

**Data morph**:
The transition in which Spider-Man's direct hero links form the opening web and expand into the reference constellation.
_Avoid_: Decorative animation, fake network

**Ego lens**:
An optional detail view of a selected hero article and its direct inbound and outbound neighbours.
_Avoid_: Filtered graph, subnetwork

**Outbound opening web**:
The initial nine visible hero links directed from Spider-Man to Black Cat, Hulk, Mayday Parker, Scarlet Spider, Silk, Spider-Man Noir, Spider-UK, Spider-Woman (Gwen Stacy), and Venom.
_Avoid_: Spider-Man web, representative links

**Spider-Man widget**:
The persistent compact character control that shows Spider-Man's degree summary and opens his ego lens after the data morph.
_Avoid_: Corner decoration, mascot

**Visible constellation**:
The default 42-hero reference constellation, containing hero articles with inbound degree of at least 12 and only hero links whose endpoints are both visible.
_Avoid_: Complete network, all-links graph

**Spider-Man endpoint**:
One of the nine named outbound hero articles at the end of a strand in the outbound opening web.
_Avoid_: Web decoration, illustrative connection

**Hero selector**:
The typeahead control that selects a hero article for highlighting in the visible constellation.
_Avoid_: Live filter, hero search

**Direction highlight**:
The selected hero's direct links, coloured blue for incoming links and coral for outgoing links, with arrows shown only for those links.
_Avoid_: Edge colour, selected relationship
