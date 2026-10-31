# Week 7 — Answer sheet and marking guide

Use after completing the test. **40 points:** 16 multiple-choice points plus 24 written-task points. These are practice marks, not an official course grading scale. Accept equivalent explanations, clearly labeled alternative drawings and sensible validation designs. Credit valid intermediate work; do not repeatedly penalize one carried-forward arithmetic mistake.

## Multiple-choice answers

| Question | Answer | Reason |
|---|:---:|---|
| 1 | B | Static lookup reuses the type's vector. Contextual representations can respond to the surrounding loan/river clues. |
| 2 | D | Each page supplies one row of 384 features. The parameters were learned earlier; applying the encoder computes new document vectors. |
| 3 | A | Unread tokens cannot influence this representation. Truncation or chunking is a substantive modeling choice to document and check. |
| 4 | C | C has the highest original cosine. The nearest plotted dot need not be the original-space nearest neighbor. |
| 5 | D | t-SNE emphasizes local relationships and does not justify exact semantic ratios from global gaps or cluster shapes. |
| 6 | B | These methods operate on different evidence and output different kinds of groupings. Disagreement can motivate inspection. |
| 7 | C | Only `wonderful` has a nonzero score, +2. The lookup does not represent the stated sarcastic intent. |
| 8 | A | Increasing the feature by one changes z by its coefficient, −2. The probability decreases, but not by a fixed percentage-point amount. |
| 9 | B | Supervised learning fits weights from labeled examples. A lookup lexicon provides its scores in advance. |
| 10 | D | Confidence is a model output, not proof of target-domain accuracy, validity, author happiness or a character's morality. |
| 11 | A | Each B starts a span and the corresponding I continues it. `visited` is outside the spans. |
| 12 | C | Detecting names and determining their real-world referents are different tasks. Aliases require context-sensitive resolution. |
| 13 | D | Paragraph co-occurrence creates all three pairwise edges. The added links record co-mention within a larger unit, not demonstrated interaction. |
| 14 | A | Exact distinctive terms can favor sparse matching; paraphrases can favor dense matching. Neither guarantees relevance. |
| 15 | C | Unit norms make the cosine denominator one. Dot products are 3/5 and 0. |
| 16 | B | Both rise by one and fall by one. Their levels differ; neither track alone establishes human emotional states. |

## Task 17 — The representation and its drawing

### a. Two rankings — 2 points

Map distances from Q are **A: 1, C: 3, B: 4**, so map order is **A, C, B**. Original cosine order is **B (0.9), C (0.7), A (0.4)**.

The map compresses a high-dimensional representation into two coordinates and can distort distances and neighborhoods. In addition, the comparison here is between visual Euclidean distance and original cosine similarity. Their rankings need not agree.

Award 1 point for both rankings; 1 for explaining the different geometry or projection distortion.

### b. Keep the original vectors separate — 2 points

```text
Raw pages
    |
stated truncation/chunking rule + pretrained encoder
    v
Original document vectors (384 features per page)
    |                                  |
    |                                  +--> cosine neighbors here
    v
Dimensionality reduction
    v
2D map (two plotting coordinates per page)
```

If only the projection changes and the original vectors are fixed, the original cosine values **do not change**. A new drawing does not alter the vectors used for that calculation.

Award 1 point for the diagram with cosine placed at the original-vector stage; 1 for the invariance explanation. The diagram need not name a particular encoder or projection algorithm.

### c. Three kinds of grouping — 2 points

| Output | Evidence used |
|---|---|
| LDA topic mixture | Word-count patterns; topics are distributions over words and documents have mixtures over topics. |
| Embedding-based cluster assignment | Closeness of dense document representations under a clustering method. |
| Hyperlink-network community | Structural patterns of links between pages. |

A mixture can allocate weight to several topics for one document. A single cluster assignment selects one group under the chosen clustering rule; it is not that full mixture. Agreement can be interesting without proving a unique true grouping.

Award 1 point for the three matches; 1 for the mixture-versus-assignment distinction.

## Task 18 — A sentiment score is a measurement choice

### a. Two lookup failures — 2 points

- `good but terrible`: +1 + 0 − 2 = **−1**. A single total compresses mixed sentiment and does not represent which aspect was good or terrible, or how `but` structures the contrast.
- `not good`: 0 + 1 = **+1**. The lookup ignores negation and therefore assigns a positive score to an ordinarily negative expression.

Award 1 point for both sums; 1 for distinguishing mixed-sentiment compression from a negation error. The rule is a sum over occurrences, not a mean over matched words.

### b. Weighted features — 2 points

z = 0 + 2(1/2) − 1(1/2) = 1 − 1/2 = **1/2**, so the predicted class is **POSITIVE**.

Raising x_good by 1/2 adds 2(1/2) = 1 to z. New z = **3/2**, still POSITIVE with a higher model-predicted positive probability.

```text
Text -> TF-IDF features -> learned weighted score z -> class decision
          (1/2, 1/2)              1/2                    POSITIVE
```

Award 1 point for the initial score and class; 1 for the changed score and diagram. No sigmoid calculation is required. Positive or negative feature weights describe effects on this classifier's prediction, not universal meanings of words.

### c. Validation and the measurement target — 2 points

The reported 96% accuracy comes from another domain; a confident prediction here does not validate transfer to encyclopedic prose. Moreover, movie-review polarity is not automatically a measure of whether a fictional character is happy. The report has not established that its score measures the intended property.

A concrete check: define the intended target, such as positive versus negative language in the passage; independently label a random sample of encyclopedia passages without seeing model predictions; compare predictions with those labels and inspect errors in negation, mixed sentiment and domain-specific language. Controlled pairs such as `good`/`not good` can supplement this sample. If character happiness is the target, the reference labels must assess evidence of that property rather than merely reuse review polarity labels.

Award 1 point for the domain/measurement mismatch; 1 for a concrete target-domain check with a reference or behavior to compare. “Use a larger model” or “check confidence” alone does not earn the validation point.

## Task 19 — From named spans to a graph

### a. BIO tags — 2 points

| Token | Tag |
|---|---|
| Iron | B-PER |
| Man | I-PER |
| met | O |
| Ada | B-PER |
| in | O |
| New | B-LOC |
| York | I-LOC |
| . | O |

Award 1 point for the two person spans and their boundaries; 1 for the location span and outside tags. These are the exercise's intended annotations, not a prediction of a specific real tagger.

### b. Extraction versus resolution — 2 points

There are **four person-name strings**: Iron Man, Ada, Tony Stark and Bo. There are **three resolved character nodes**: Tony Stark, Ada and Bo.

Alias mapping: **Iron Man → Tony Stark**; Tony Stark remains Tony Stark. Ada and Bo each remain separate. New York is a location, excluded by the graph's definition. NER detects and types spans; entity resolution decides whether differently worded mentions share a referent.

Award 1 point for both counts and alias mapping; 1 for distinguishing extraction from resolution.

### c. Two graph constructions — 2 points

Sentence-level graph, **2 edges**:

```text
Ada --- Tony Stark --- Bo
```

Paragraph-level graph, **3 edges**:

```text
       Tony Stark
       /        \
     Ada ------- Bo
```

The added edge is **Ada–Bo**. They appear in the same paragraph but no sentence states that they interact. Changing the text unit changes the measured relation and graph structure, not just the layout.

Award 1 point for both graphs and edge counts; 1 for the added edge and interpretation. Node placement is arbitrary, but connectivity must match.

## Task 20 — Retrieve evidence, then generate

### a. Dense ranking — 2 points

- q·A = 0×1 + 1×0 = **0**.
- q·B = 0×(3/5) + 1×(4/5) = **4/5**.
- q·C = 0×0 + 1×1 = **1**.

Ranking: **C, B, A**. Both query and passages have unit length, so the denominator in cosine is one.

Award 1 point for the three scores and ranking; 1 for the normalization explanation. A top-ranked passage is still a candidate for relevance inspection, not guaranteed correct evidence.

### b. Vocabulary mismatch — 2 points

The sparse vectors have no shared retained coordinates, so their dot product is zero; lexical matching cannot connect `automobile repair` to `fixing cars` under the stated representation. A useful dense encoder would need to have learned relationships between those paraphrases so that their vectors align despite the missing exact overlap.

Sparse retrieval can be especially helpful for an exact rare name, part number or technical term retained in both query and relevant passage, such as `ZX-17`. Neither prediction guarantees that the full result answers the user's question.

Award 1 point for explaining the mismatch and dense representation's needed information; 1 for a contrasting exact-match case with a reason.

### c. Diagnose the stages — 2 points

```text
Question -> RETRIEVAL -> visible retrieved passages
                               |
                      question + passages
                               v
                          GENERATION -> answer
```

- **Run 1 demonstrates a retrieval failure:** the needed Mira evidence is absent from what was returned, despite existing in the corpus. The answer also makes an unsupported transfer from Nilo to Mira; a responsible generator could have declined to infer Mira's birthplace from that passage. It is not necessary to claim that generation was faultless in order to diagnose the retrieval failure.
- **Run 2 demonstrates a generation failure:** the correct Mira evidence was retrieved, but the generated answer contradicts it.

Inspect the query, available relevant source, retrieved passages and final answer to separate these problems. Looking only at the answer cannot reliably locate the failure.

Award 1 point for the two-stage diagram with visible evidence; 1 for the diagnoses, including the distinction between Run 1's missing evidence and its unsupported answer.

## Coverage against the supplied curriculum

The first 13 rows follow the Week 7 **On Test 2** skills in their original order. The final row covers additional explicit **Essentials**. Q denotes a multiple-choice question; T denotes a written task.

| Assessed skill | Practice coverage |
|---|---|
| Static versus contextual representations | Q1 |
| Document embeddings versus 2D projections | Q2–4; T17b |
| Original cosine neighbors versus nearby plotted dots | Q4–5; T17a,b |
| LDA topics, embedding clusters and structural communities | Q6; T17c |
| Lexicon sentiment; negation, mixed sentiment and context failures | Q7; T18a,c |
| TF-IDF in a logistic classifier; signs of feature weights | Q8–9; T18b |
| Confidence versus validity in a new domain | Q10; T18c |
| Read/write BIO tags; NER versus entity resolution | Q11–12; T19a,b |
| Co-occurrence units and their graph consequences | Q13; T19c |
| Sparse/dense retrieval and vocabulary mismatch | Q14–15; T20a,b |
| RAG stages and retrieval/generation failures | T20c |
| Concrete validation of pretrained measurement models | Q10; T18c |
| Critique borrowed accuracy, undefined scores and unresolved entity counts | Q10, Q12; T18c, T19b |
| Pretraining, chunking, dimensionality reduction, t-SNE and emotional-arc shape | Q2–5, Q16; T17 |

Closest Learn exercises: **7.1, 7.3, 7.5, 7.7 and 7.9**. Core explanatory material also supplies projection, chunking and emotional-arc interpretation. No model-name trivia, training architecture, coding or optional bias-framework knowledge is required.

Source: Sune Lehmann, DTU 02805, [Week 7 — From meaning to measurement](<../data/week7/Week 7 · From meaning to measurement · 02805.html>), including **Essentials** and **On Test 2**. All 11 HTML files in `data/week7` were inspected: nine companion files have blank bodies in the saved copy; the nonblank files are the main page and one video wrapper. The test supplies its own complete figures and data. The source page credits its content under **CC BY-SA 4.0**; this adapted practice material is shared under the same license. Question design and marking allocations here are original practice additions.
