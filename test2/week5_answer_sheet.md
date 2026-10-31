# Week 5 — Answer sheet and marking guide

Use after completing the test. **40 points:** 16 multiple-choice points plus 24 written-task points. These are practice marks, not an official course grading scale. Accept equivalent wording and correct alternative examples. Award partial credit for valid working; do not repeatedly penalize one carried-forward arithmetic error.

## Multiple-choice answers

| Question | Answer | Reason |
|---|:---:|---|
| 1 | C | The tokenizer creates the initial boundaries. Lowercasing and filtering act afterward. IDs index pieces; they do not rank meanings. |
| 2 | B | The four occurrences remain; the vocabulary becomes `{apple, .}`. |
| 3 | D | Longest matching pieces give `un | mask | ing`. A whole-word entry is unnecessary. |
| 4 | A | `was` and `is` collapse to the same lemma, removing the tense distinction being studied. |
| 5 | B | A: 8/80 = 1/10. B: 6/30 = 1/5, twice A's rate. Neither rate identifies meaning. |
| 6 | A | Before: 4/20 = 20%. After: 4/10 = 40%. Only the denominator changes. |
| 7 | D | Counts sum to 10; there are four distinct forms. `gate` and `metal` each occur once. |
| 8 | C | Each doubling of rank halves frequency: 64/16 = 4. |
| 9 | B | The axes change the display, not the observations. Visual resemblance does not establish an exact model. |
| 10 | D | A concordance shows actual occurrences with context; `similar()` finds other words sharing contexts. |
| 11 | A | Antonyms can occur in the same grammatical slots. Context similarity does not entail synonymy. |
| 12 | C | 5 − 3 + 1 = 3 trigrams. Longer exact sequences keep more order but generally have less repeated evidence. |
| 13 | D | `of the`: 30/30 = 1. `silver shield`: 8/2 = 4. Raw frequency ignores the baseline. |
| 14 | B | A column follows one vocabulary term across documents; it cannot establish meaning or order. |
| 15 | C | One new type adds a column, with one occurrence in D2 and none in the other documents. |
| 16 | A | Count vectors retain term frequencies but discard the order needed to identify who chased whom. |

## Task 17 — Make the preprocessing visible

### a. Pipeline — 2 points

```text
"Heroes help heroes."
        |
     tokenize
        v
[Heroes, help, heroes, .]   4 tokens, 4 types
        |
     lowercase
        v
[heroes, help, heroes, .]   4 tokens, 3 types
        |
 remove punctuation
        v
[heroes, help, heroes]      3 tokens, 2 types
        |
 heroes -> hero
        v
[hero, help, hero]          3 tokens, 2 types
```

Award 1 point for the correct sequence of lists and operations; 1 for the counts. Lemmatization changes the form but does not further reduce the type count in this particular example.

### b. Frequency table — 2 points

| Type | Count | Relative frequency |
|---|---:|---:|
| hero | 2 | 2/3 |
| help | 1 | 1/3 |

`help` is the only hapax type. Award 1 point for the table; 1 for the requested relative frequency and hapax identification.

### c. Representation choices — 2 points

`unmasked` becomes **`un | mask | ed`**, three tokens. A word absent as a whole can still be spelled using available pieces; the letter fallback covers words composed of those letters. This does not by itself give the model knowledge of the word's meaning.

Merging `hero` and `heroes` would obstruct a question about how often texts discuss one hero versus multiple heroes, because the singular/plural distinction has been removed.

Award 1 point for the segmentation and fallback explanation; 1 for a concrete question whose signal is lost.

## Task 18 — Build and change a document-term matrix

### a. Matrix and interpretation — 2 points

| Document | birds | help | robots |
|---|---:|---:|---:|
| D1 | 1 | 1 | 1 |
| D2 | 1 | 1 | 1 |
| D3 | 0 | 1 | 2 |

D3 has no `birds`, one `help` and two `robots`. The `birds` column is `[1, 1, 0]`: one occurrence in each of D1 and D2, none in D3.

Award 1 point for the matrix; 1 for both interpretations.

### b. Sparsity and edit — 2 points

There is **1 zero in 9 cells: 1/9**. Appending `quietly` makes the matrix **3 × 4**. Its new column is:

| Document | quietly |
|---|---:|
| D1 | 0 |
| D2 | 1 |
| D3 | 0 |

With alphabetical order it sits between `help` and `robots`; the existing counts stay unchanged. Large corpora have many vocabulary terms, but each document uses only a subset, leaving many zeros. This tiny matrix itself is not especially sparse.

Award 1 point for the zero fraction and edited dimensions/column; 1 for explaining real-corpus sparsity.

### c. Information kept and lost — 2 points

D1 and D2 contain the same words with the same counts. Bag of Words ignores their order, including the reversal of helper and recipient. It can answer “Which document contains the most occurrences of `robots`?” It cannot answer “Do birds help robots or do robots help birds in D1?”

Award 1 point for explaining the collision; 1 for the answerable/unanswerable question pair.

## Task 19 — Local order and collocations

### a. Windows and counts — 2 points

```text
Bigrams:
[small robots] [robots help] [help small] [small birds]

Trigrams:
[small robots help] [robots help small] [help small birds]
```

Unigram counts: `small: 2`, `robots: 1`, `help: 1`, `birds: 1`.

Award 1 point for both window lists; 1 for the unigram table. The two occurrences of `small` are one type.

### b. Association — 2 points

- `small robots`: 6/2 = **3**.
- `of the`: 20/20 = **1**.

The first pair occurs three times as often as independence predicts. The second is frequent but occurs exactly as often as its component frequencies predict. Award 1 point for the ratios; 1 for the baseline-based explanation.

### c. Method and trade-off — 2 points

Trigrams preserve an additional token of local order, but the longer exact combinations tend to recur less often, giving sparser evidence. A **concordance** is appropriate for inspecting the uses of `small`: its surrounding passages can distinguish physical size from organizational importance. `similar()` instead returns other words in comparable contexts.

Award 1 point for the trade-off; 1 for the method and justification.

## Task 20 — A figure and a claim

### a. Sketch and axes — 2 points

Plot **(1, 8), (2, 4), (3, 2), (4, 1), (5, 1)** with rank horizontal and frequency vertical. A valid schematic is:

```text
frequency
8 | *
7 |
6 |
5 |
4 |     *
3 |
2 |         *
1 |             *   *
0 +--------------------- rank
    1   2   3   4   5
```

On log-log axes, both coordinates are displayed logarithmically: equal ratios receive equal spacing, making multiplicative patterns easier to inspect. The counts, ranks and underlying observations remain the same.

Award 1 point for the correctly labeled sketch; 1 for the axes explanation. An exact straight line is neither required nor justified by these data.

### b. Counts — 2 points

Total tokens = 8 + 4 + 2 + 1 + 1 = **16**. Relative frequency of `power` = 4/16 = **1/4 = 25%**. Hapax types are `shield` and `river`: **2/5 of the types**. The hapax denominator is five types, not sixteen tokens.

Award 1 point for total and relative frequency; 1 for the hapax fraction.

### c. Critique — 2 points

Example: “A frequent function word is not evidence that grammar is the corpus's subject, and four uses of `power` establish neither its political sense nor thematic centrality. Inspect the `power` concordance and compare its relative frequency with a relevant reference corpus under stated preprocessing. A roughly straight log-log pattern is descriptive evidence, not proof of an exact Zipf model.”

Award 1 point for rejecting both frequency-to-meaning inferences; 1 for rejecting the claimed proof and proposing a concrete inspection or comparison. No formal statistical fitting procedure is required.

## Coverage against the supplied curriculum

The rows follow the Week 5 **On Test 2** skills in their original order. Q denotes a multiple-choice question; T denotes a written task.

| Assessed skill | Practice coverage |
|---|---|
| Raw text, tokenization and later preprocessing | Q1–2; T17a |
| Subword segmentation and unfamiliar words | Q3; T17c |
| Tokens, types, vocabulary and document units | Q2, Q7, Q14; T17–18 |
| Effects of lowercasing, punctuation, stopwords and lemmatization | Q2, Q4, Q6; T17 |
| Frequency tables, relative frequency and hapax types | Q5–7; T17b, T20b |
| Rank-frequency plots, linear/log-log axes and limits of Zipf claims | Q8–9; T20a,c |
| Concordances versus similar-context words; similarity is not synonymy | Q10–11; T19c |
| Unigrams, bigrams, trigrams and context/sparsity trade-off | Q12; T19a,c |
| Frequent pairs versus collocations | Q13; T19b |
| Construct and read matrix rows and columns | Q14; T18a |
| Sparsity, preprocessing and loss of word order | Q15–16; T17, T18 |
| Match representations to research questions | Q4, Q10, Q16; T17c, T18c, T19c |
| Critique unsupported corpus claims and unstated processing choices | Q5, Q9, Q11; T17, T20c |

Closest Learn exercises: **5.1, 5.2, the Learn portions of 5.4–5.5, and 5.6**. These questions adapt their reasoning style using new small examples. Optional Goodies, coding tasks and corpus-specific trivia are not assessed.

Source: Sune Lehmann, DTU 02805, [Week 5 — From language to numbers](<../data/week5/Week 5 · From language to numbers · 02805.html>), including **Essentials** and **On Test 2**. All 11 HTML files in `data/week5` were inspected, including saved figures and the video wrapper. The page credits its content under **CC BY-SA 4.0**; this adapted practice material is shared under the same license. Question design and marking allocations here are original practice additions.
