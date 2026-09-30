# Bag-of-Words Collision Explorable

This context describes the Week 5 widget that makes representation loss visible by letting one shared word set become three differently ordered sentences.

## Language

**Shared word bank**:
The fixed set of five word tiles that can be reused in every sentence lane.
_Avoid_: Word pool, vocabulary list

**Batch placement**:
The interaction in which dragging one word from the shared word bank into any sentence lane places that word at the same position in all three sentence lanes.
_Avoid_: Bulk fill, auto-complete

**Sentence lane**:
One of the three drop targets where a student arranges the shared word bank into an ordered sentence.
_Avoid_: Row, column, track

**Vector collision**:
The result in which different ordered sentences produce identical Bag-of-Words count vectors.
_Avoid_: Duplicate sentence, same meaning

**Comparison reveal**:
The deliberate step after prediction that shows the three colored sentences and their identical numerical rows together.
_Avoid_: Animation, answer screen

**Insertion marker**:
The visible position indicator that shows where a dragged word will be inserted when it is dropped onto a sentence lane.
_Avoid_: Drop line, cursor
