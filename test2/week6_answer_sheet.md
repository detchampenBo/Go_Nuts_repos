# Week 6 — Answer sheet and marking guide

Use after completing the test. **40 points:** 16 multiple-choice points plus 24 written-task points. These are practice marks, not an official course grading scale. Accept equivalent wording and valid alternative checks. Award partial credit for sound working and carry forward isolated arithmetic errors without repeatedly penalizing them.

## Multiple-choice answers

| Question | Answer | Reason |
|---|:---:|---|
| 1 | D | Two documents contain `shield`; four is its total occurrence count, not its DF. |
| 2 | A | IDF = ln(N/N) = 0. Corpus-wide commonness is learned from DF, not from a manually supplied stopword list. |
| 3 | B | TF is 2/4 in A and 2/8 in B. The term has the same collection-wide IDF in both. |
| 4 | C | Positive scaling changes length, not direction; the scale cancels in the cosine ratio. |
| 5 | A | Their dot product is zero. Different words can still convey related meanings that the representation misses. |
| 6 | D | X has document rows and vocabulary columns; Y has target-word rows and context-word columns. |
| 7 | B | M has equal high rates; S is used only in B in these observations; N only in A. |
| 8 | C | Rates describe how often a word occurs, not which senses or contexts produced those occurrences. |
| 9 | D | It is P(word = gene given topic T), not the inverse probability or a document mixture. |
| 10 | B | Both mixtures sum to one. A is dominated by T1; B distributes its weight equally. |
| 11 | A | The word distributions come from the fit; the label is a human interpretation and the solution depends on choices. |
| 12 | C | Window 1: `robot, red`. Window 2 adds `blue, ship`. Wider windows often add topical associations. |
| 13 | B | PPMI = max(−1,0) = 0. This clips the weight, not the observed corpus count. |
| 14 | D | A small set of noise comparisons reduces computation. A sampled pair is not a claim that two words can never be related. |
| 15 | C | All three are static here: one vector per type. PPMI uses reweighted counts, Word2Vec learns from context prediction, and GloVe learns from global co-occurrence statistics. |
| 16 | A | High cosine indicates similar direction under the learned representation. Antonyms can share contexts. |

## Task 17 — TF-IDF from a tiny corpus

### a. Document frequency and IDF — 2 points

| Term | DF | IDF |
|---|---:|---:|
| common | 4 | ln(4/4) = 0 |
| alloy | 2 | ln(4/2) = ln(2) ≈ 0.7 |
| magic | 1 | ln(4/1) = ln(4) ≈ 1.4 |

Award 1 point for all DF values and 1 for all IDF values. Multiple occurrences inside a document do not add to DF.

### b. D1's weights — 2 points

| Term | Count in D1 | TF in D1 | TF-IDF using supplied logs |
|---|---:|---:|---:|
| common | 1 | 1/4 | 0 |
| alloy | 1 | 1/4 | (1/4)(0.7) = 7/40 = 0.175 |
| magic | 2 | 1/2 | (1/2)(1.4) = 7/10 = 0.7 |

Exact forms **ln(2)/4** and **ln(4)/2 = ln(2)** are equally valid. Rounded numbers here use the test's convenient logarithm values, not full-precision natural logarithms.

`magic` has the largest weight. TF accounts for its frequency within D1, while IDF rewards its relative rarity across documents. Raw counts alone cannot distinguish `common` from `alloy` in D1 even though their collection-wide prevalence differs.

Award 1 point for TF and TF-IDF values; 1 for the largest term and explanation.

### c. A collection change — 2 points

`alloy`'s TF **in D1 stays 1/4**, because D1 is unchanged. Its DF rises from 2 to 3, so its IDF **decreases** from ln(4/2) to ln(4/3). Its D1 TF-IDF therefore **decreases**. The weights of an unchanged document can change when the collection changes, because IDF is a collection statistic.

Award 1 point for the three directions; 1 for the explanation using the new DF and unchanged D1.

## Task 18 — Geometry you can draw

### a. Arrows and lengths — 2 points

Draw arrows from (0,0) to A(3,4), B(6,8) and C(4,0). A lies halfway along B's arrow; C is on the positive horizontal axis.

- ||A|| = √(9 + 16) = **5**.
- ||B|| = √(36 + 64) = **10**.
- ||C|| = √16 = **4**.

A and B share the same direction. Award 1 point for the sketch and alignment; 1 for the lengths.

### b. Cosines — 2 points

- A·B = 3×6 + 4×8 = 18 + 32 = **50**. Cosine(A,B) = 50/(5×10) = **1**.
- A·C = 3×4 + 4×0 = **12**. Cosine(A,C) = 12/(5×4) = **3/5 = 0.6**.

A and B overlap in direction; C is separated by a nonzero acute angle. Award 1 point for each correct calculation with working consistent with the drawing.

### c. Scaling and interpretation — 2 points

Cosine(2A,B) = **1** and cosine(2A,C) = **3/5**. Doubling A doubles both its dot product with the other vector and its length, so the factors cancel.

For count vectors, equal direction means proportional vocabulary counts; more generally it means proportional feature weights in the chosen representation. It does not establish identical meaning, word order, narrative roles or document length.

Award 1 point for the unchanged values and cancellation explanation; 1 for distinguishing representation-level agreement from a meaning claim.

## Task 19 — A common context versus an informative context

### a. Totals and probabilities — 2 points

| Target word | the | bark | money | Row total |
|---|---:|---:|---:|---:|
| dog | 4 | 3 | 1 | 8 |
| bank | 4 | 1 | 3 | 8 |
| Column total | 8 | 4 | 4 | **16** |

For `(dog, bark)`:

- P(dog,bark) = **3/16**.
- P(dog) = 8/16 = **1/2**.
- P(bark) = 4/16 = **1/4**.
- Independence predicts P(dog)P(bark) = (1/2)(1/4) = **1/8 = 2/16**.

Award 1 point for the totals; 1 for the probabilities and independence product.

### b. PMI and clipping — 2 points

For `(dog, bark)`, observed/expected = (3/16)/(2/16) = **3/2**. PMI = **log₂(3/2) ≈ 0.585**; PPMI is the same positive value. The observed association exceeds independence.

For `(dog, money)`, P(dog,money) = 1/16 and the independence product is again 1/8. Ratio = (1/16)/(2/16) = **1/2**. PMI = **−1** and PPMI = **0**. This pair occurs less often than independence predicts.

Award 1 point for each pair's calculation, including clipping.

### c. Commonness and geometry — 2 points

For `(dog, the)`, P(dog,the) = 4/16 = 1/4. The independence product is (8/16)(8/16) = 1/4. Ratio = 1, so **PMI = 0** and **PPMI = 0**.

`the` is frequent, but its frequency near `dog` is exactly what its marginals predict. Reweighting removes this shared dimension here and emphasizes unexpectedly strong associations such as `dog`–`bark`. Changing the relative coordinate weights changes vector directions, so cosine neighbors can change. It is not merely a uniform rescaling of every row, and PPMI does not automatically eliminate every common word in every dataset.

Award 1 point for the calculation; 1 for the explanation of commonness and changed geometry.

## Task 20 — Two ways to model the same corpus

### a. Training examples — 2 points

Window-2 contexts are `young, robots, small, ships`.

```text
Skip-gram:
repair -> young
repair -> robots
repair -> small
repair -> ships

CBOW:
[young, robots, small, ships] -> repair
```

Skip-gram predicts nearby words from the center; CBOW predicts the center from the surrounding words. Award 1 point for all four Skip-gram pairs; 1 for the CBOW example and direction explanation.

### b. Two distinct distributions — 2 points

```text
D's topic mixture: [ T1 | T1 | T1 | T2 ]
                    <--- 3/4 --->  1/4
```

The bar distributes D's mixture weight over topics, totaling one. T1's word distribution instead assigns probabilities to vocabulary terms such as `ship`, `orbit` and `planet`, also totaling one over its entire vocabulary. The three listed top words need not exhaust that vocabulary or sum to one on their own.

This two-distribution structure describes **LDA specifically**, not every topic-modeling method. Topic modeling is the broader aim of recovering recurring word-use patterns; other methods can define their latent structure differently.

Award 1 point for the correctly proportioned bar and document interpretation; 1 for distinguishing the topic's word distribution and identifying LDA as the particular model.

### c. Critique — 2 points

Example: “Space is our interpretation of T1's word probabilities, so we should inspect high-weight documents before adopting the label. The fitted topics depend on topic count, preprocessing and initialization; rerunning with another seed or reasonable topic count would test stability. A high cosine for `hero` and `villain` may reflect shared contexts, so concordance inspection is needed before interpreting it as synonymy.”

Award 1 point for identifying human labeling and solution dependence with a concrete check; 1 for rejecting the synonymy inference and explaining what high cosine can reflect.

## Coverage against the supplied curriculum

The rows follow the Week 6 **On Test 2** skills in their original order. Q denotes a multiple-choice question; T denotes a written task.

| Assessed skill | Practice coverage |
|---|---|
| TF, DF, IDF, TF-IDF and ubiquitous terms | Q1–3; T17 |
| Cosine, angle interpretation and positive scaling | Q4–5; T18 |
| Document-term versus word-context rows, columns and cells | Q6; T17, T19 |
| Two-corpus term plots: shared and distinctive rates | Q7–8 |
| Topic modeling versus LDA; topic-word and document-topic distributions | Q9–11; T20b,c |
| Human topic labels and dependence on topic count, processing and initialization | Q11; T20c |
| Distributional hypothesis and narrow/wide context windows | Q12, Q16; T20a,c |
| PMI ingredients, PPMI clipping and common contexts | Q13; T19 |
| Skip-gram, CBOW and negative sampling | Q14; T20a |
| PPMI, Word2Vec, GloVe and static polysemy limitation | Q15–16; T19, T20a,c |
| Critique topic and embedding claims | Q11, Q16; T20c |

Closest Learn exercises: **6.1, 6.4, 6.6 and 6.8**. Scattertext interpretation is also included because it is explicitly assessed in **On Test 2**. Optional derivations, library-default trivia and programming are not required.

Source: Sune Lehmann, DTU 02805, [Week 6 — From counts to meaning](<../data/week6/Week 6 · From counts to meaning · 02805.html>), including **Essentials** and **On Test 2**. All 13 HTML files in `data/week6` were inspected: the main page contains the curriculum, while the 12 companion HTML files in this saved copy have blank bodies. All figures and numerical examples needed here are therefore supplied directly in the test. The source page credits its content under **CC BY-SA 4.0**; this adapted practice material is shared under the same license. Question design and marking allocations here are original practice additions.
