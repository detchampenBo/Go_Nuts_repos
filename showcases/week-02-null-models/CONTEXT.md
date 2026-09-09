# Marvel Lineup

Language for the individual Week 2 network puzzles, derived from the Week 1 Wikipedia snapshot.

## Language

**Puzzle**:
A fixed sequence of eight predictions with one score. Each puzzle has its own leaderboard.
_Avoid_: Match, alliance race

**Hero card**:
A Wikipedia hero article presented with a sketch of its network neighborhood.
_Avoid_: Canonical character profile

**Connection**:
An undirected link between two hero articles when either article links to the other in the frozen snapshot. It does not assert a friendship or alliance in the stories.
_Avoid_: Friendship, alliance

**Lineup**:
Hero cards arranged from lowest to highest by the current network measure.
_Avoid_: Team

**Tight circle**:
A hero neighborhood with a high share of linked neighbor pairs, measured by local clustering.
_Avoid_: Lots of connections

**Shuffle**:
A random rewiring of the network that preserves every hero's exact connection count.
_Avoid_: Random network with no constraints

**Local leaderboard**:
Names and completed puzzle scores saved in the current browser, separately for each puzzle.
_Avoid_: Global leaderboard, shared leaderboard
