# The Friendship Paradox

Language for the Week 2 friendship-paradox explorable, derived from the Week 1
Wikipedia snapshot.

## Language

**Hero**:
A Wikipedia article for one Marvel character, shown as the centre of the ego view.
_Avoid_: Character profile, canonical hero

**Connection**:
An undirected link between two heroes when either article links to the other in
the frozen snapshot. It does not assert a friendship or alliance in the stories.
_Avoid_: Friendship, alliance, relationship

**Friend**:
A hero directly connected to the selected hero. Used only in the paradox phrasing
("your friends have more friends than you"), never as a claim about the stories.
_Avoid_: Ally, teammate

**Friends' average**:
The mean number of connections across all of a hero's friends.
_Avoid_: Neighbour degree, expected degree

**Paradox holds**:
The state where a hero's friends' average is greater than the hero's own
connection count.
_Avoid_: The paradox is true, the hero is unpopular

**Top of their circle**:
A hero with no friend more connected than themselves.
_Avoid_: Most popular, the winner

**Scale-free model**:
A generated Barabási–Albert network (growth plus preferential attachment) with
the same node count as the Marvel network.
_Avoid_: Power-law graph, real scale-free network

**Random model**:
A generated uniform `G(n, m)` network with the same node and edge count as the
Marvel network.
_Avoid_: Null model, shuffled network

**The identity**:
`⟨k⟩ + σ²/⟨k⟩` — the expected degree of a node reached by following a random
connection. The surplus over `⟨k⟩` is the degree variance divided by the mean.
_Avoid_: The formula, the equation
