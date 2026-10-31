# Week 7 make-up practice test — From meaning to measurement

**Time: 60 minutes · 40 points · Pen and paper · Closed book · No calculator or code**

This test uses the Week 7 **Essentials**, **On Test 2** skills and corresponding **Learn** exercises. The page's optional bias section and Goodies are outside this test. All model outputs below are illustrative, supplied values; you do not need to predict the exact behavior of a real software package.

Suggested timing: **24 minutes** for Questions 1–16, **32 minutes** for Tasks 17–20 (about eight minutes each), and **4 minutes** to check. Choose **one** answer per multiple-choice question. Each is worth **1 point**, with no penalty for an incorrect answer. Each written task is worth **6 points**. Use separate paper for short calculations, labeled diagrams and concise explanations.

## Formula and convention sheet

- **Toy sentiment lexicon:** wonderful = +2; good = +1; bad = −1; terrible = −2. All other words score zero. Lowercase and ignore punctuation. Score a text by **summing the scores of all token occurrences**, including repetitions. There is no negation rule.
- A toy binary logistic classifier uses score **z = b + Σᵢ wᵢxᵢ**, where x contains TF-IDF feature values. Larger z means higher predicted probability of the class labeled **POSITIVE**. For this paper, predict POSITIVE if z > 0 and NEGATIVE if z < 0. No probability or exponential calculation is needed, and no example has z = 0.
- Dot product q·d = sum of coordinate-by-coordinate products. Cosine(q,d) = (q·d)/(||q|| ||d||). For two unit-length vectors, cosine = dot product. All retrieval vectors requiring calculation here are already unit length.
- **BIO:** B-TYPE begins an entity span; I-TYPE continues the same span; O is outside an entity. Use PER for a person/character and LOC for a place.
- Network tasks use simple, undirected graphs: resolved characters are nodes; two different nodes receive one edge if they occur in the same stated text unit. Exclude locations, self-loops and duplicate edges. Aliases are supplied where needed.

## Part A — Multiple choice

### 1. Same word, different context

Compare “The bank approved a loan” with “We rested on the river bank.” Which prediction fits the representations?

A. A static embedding necessarily creates a new bank vector whenever the sentence changes.
B. A static embedding reuses one bank vector; a contextual model can use `loan` and `river` to produce different occurrence-level vectors.
C. A contextual representation must ignore all surrounding words.
D. Different token IDs for every sentence are required before context can affect a vector.

### 2. What has been pretrained?

A pretrained encoder maps each of four pages to 384 numbers, without further training. Which interpretation is correct?

A. Each of the 384 columns is guaranteed to be one named human theme.
B. The resulting matrix contains 384 documents and four word types.
C. Passing the pages through the encoder necessarily retrains all its parameters on those pages.
D. The matrix has four document rows; their vectors are computed using parameters learned before this application.

### 3. Missing part of the document

An encoder reads at most 100 tokens, but a page has 300. A system silently keeps only the first 100 and calls the result “a representation of the full page.” What is the best response?

A. State the truncation or use a documented chunking and aggregation rule that covers the relevant text; then check its effect.
B. Increasing the size of the plotted dots restores the omitted text.
C. A dense vector automatically contains text the encoder never read.
D. Removing the page title guarantees that all 300 tokens fit.

### 4. A map and a neighbor list disagree

A 2D map places A nearest to Q. The original-space cosine values to Q are A: 0.8, B: 0.5, C: 0.9. Which document is the nearest under the original cosine measure?

A. A, because visible distance overrides the original vectors.
B. B, because its cosine is the smallest.
C. C, because 0.9 is highest; the projection can distort relationships.
D. All three, because reducing dimensions makes every cosine equal.

### 5. Interpreting a t-SNE gap

Two clusters are drawn far apart in a t-SNE map. An analyst says their separation is exactly twice the semantic difference between two other clusters. Which correction is appropriate?

A. A map's global distances are exact semantic measurements as long as it uses colors.
B. The statement becomes valid if the circles are larger.
C. Every t-SNE coordinate is a named topic probability.
D. t-SNE emphasizes local neighborhoods; global map distances and cluster shapes do not support that quantitative claim by themselves.

### 6. Same pages, different groups

LDA, embedding clustering and hyperlink community detection disagree about a page. Which explanation is most appropriate?

A. At least two methods must have a coding error because they use the same documents.
B. They use word-count patterns, dense-text geometry and link structure respectively, so differing groupings can be informative.
C. All three use only word counts, so their outputs should match exactly.
D. Hyperlink communities are a document's probability distribution over vocabulary words.

### 7. Reading a score in context

The writer intends “Wonderful, another cancelled train!” sarcastically. Under the printed lexicon and summation rule, which result and interpretation are correct?

A. 0, because punctuation automatically removes sentiment.
B. −2, because the lookup rule detects the writer's intended sarcasm.
C. +2, because `wonderful` contributes +2; the fixed lookup misses the sarcastic context.
D. +2, proving that the writer is pleased about the cancellation.

### 8. Interpreting a feature weight

In a binary TF-IDF logistic classifier, the coefficient of `terrible` is −2 for the POSITIVE class. Holding every other feature and the intercept fixed, increasing that feature by 1 does what?

A. Decreases z by 2 and lowers the model's predicted probability of POSITIVE.
B. Raises the probability of POSITIVE by exactly two percentage points.
C. Proves the word has negative meaning in every possible sentence.
D. Changes the document's tokenization boundaries.

### 9. Where do the classification weights come from?

A researcher fits a logistic classifier to TF-IDF vectors of reviews with human sentiment labels. How does this differ from the printed lookup lexicon?

A. TF-IDF itself supplies the correct sentiment label without training.
B. The classifier learns feature weights from labeled examples; the lexicon uses preset word scores.
C. Logistic regression requires every coordinate to be a contextual token representation.
D. Training ensures valid measurements in every new domain.

### 10. Confidence is not validation

A model trained on movie reviews calls an encyclopedia sentence POSITIVE with confidence 0.99. What is justified?

A. The author's actual happiness is 99%.
B. The encyclopedia measurement has 99% accuracy.
C. The character described is morally good with probability 0.99.
D. This is the model's confident classification; its behavior and the intended measurement still need checking on the new domain.

### 11. Reading BIO tags

```text
Ada/B-PER Lovelace/I-PER visited/O New/B-LOC York/I-LOC
```

Which extraction follows from these tags?

A. Two spans: `Ada Lovelace` as PER and `New York` as LOC.
B. Five one-token entities.
C. One person span covering the entire sentence.
D. Two people named Ada and Lovelace, with no place entity.

### 12. Names are not necessarily people

A tagger finds the person-name strings `Iron Man`, `Tony Stark` and `Stark`. A report calls them “three distinct characters” without inspecting their references. What is missing?

A. A larger font for the entity list.
B. Lowercasing alone, which always resolves every alias correctly.
C. Entity resolution: determining whether different mentions refer to the same underlying character.
D. A proof that every entity name consists of one token.

### 13. Changing the co-occurrence unit

One paragraph contains “Ada met Bo. Cy waited alone.” All three names refer to different people. What changes when edges use paragraphs instead of sentences?

A. Only the node positions change; edges cannot change.
B. The edge Ada–Bo disappears.
C. Cy must be removed because the second sentence has only one person.
D. Ada–Cy and Bo–Cy are added, although this does not establish that Cy interacted with either person.

### 14. Choosing a retrieval method

Query A contains a rare exact code, `ZX-17`, which occurs in the relevant document. Query B says `automobile repair`, while a relevant passage says `fixing cars` and shares no retained terms with the query. Which prediction is most reasonable?

A. Sparse TF-IDF can be strong for A's exact match; dense retrieval may help with B's vocabulary mismatch, but both require relevance checks.
B. Dense retrieval is guaranteed to beat sparse retrieval for every query.
C. Sparse TF-IDF always assigns a high similarity to documents with no retained vocabulary overlap.
D. A code match proves the entire returned document answers any question containing the code.

### 15. Ranking normalized vectors

The query is q = (1,0). Document vectors x = (3/5,4/5) and y = (0,1) are unit length. Which statement is correct?

A. y ranks first because it has a larger second coordinate.
B. Their cosine similarities cannot be found without a calculator.
C. x ranks first: q·x = 3/5 and q·y = 0, and these dot products equal their cosines.
D. Both have cosine 1 because both document vectors are normalized.

### 16. Shape versus level in an emotional arc

Two three-position sentiment tracks are A = [0,1,0] and B = [2,3,2]. An analyst studies narrative rise and fall rather than the overall score level. What is supported?

A. B has a different rise-and-fall shape because every value is positive.
B. Both have the same rise-then-fall shape, while B is shifted upward by two units.
C. Both tracks prove that all readers experienced the same emotions.
D. A sentence-level sentiment curve is automatically a direct measure of the author's happiness.

## Part B — Draw, calculate and explain

### 17. The representation and its drawing — 6 points

The map uses ordinary linear coordinates: Q = (0,0), A = (1,0), B = (4,0), C = (0,3). It is a projection of fixed 384-dimensional document vectors.

```text
map y
3 | C
2 |
1 |
0 | Q   A           B
  +-------------------- map x
    0   1   2   3   4
```

Original-space cosine similarities to Q are:

| Document | A | B | C |
|---|---:|---:|---:|
| Cosine to Q | 0.4 | 0.9 | 0.7 |

**a. (2 points)** Rank A, B and C from nearest to farthest on the map and separately from highest to lowest original cosine. Explain why disagreement does not by itself indicate a coding error. No square-root calculation is needed.

**b. (2 points)** Draw a diagram from raw pages to original document embeddings to a 2D projection. Mark where you would calculate cosine neighbors. If only the projection changes, state whether the original cosine values should change, and why.

**c. (2 points)** Match each output to the information used: an LDA topic mixture, an embedding-based cluster assignment, and a hyperlink-network community. Explain why a topic mixture differs from assigning a page to one cluster.

### 18. A sentiment score is a measurement choice — 6 points

**a. (2 points)** Calculate the printed lexicon's sum for `good but terrible` and for `not good`. Explain the problem exposed by each phrase. A mixed score and a negation error are different issues.

**b. (2 points)** A toy logistic classifier receives only two already-computed TF-IDF values: x_good = 1/2 and x_terrible = 1/2. Its intercept is 0, w_good = +2 and w_terrible = −1. Calculate z and the predicted class. If x_good rises by 1/2 while all other values stay fixed, calculate the new z. Sketch a short input → weighted score → predicted class diagram to show where TF-IDF enters.

**c. (2 points)** A report says: “This movie-review model had 96% accuracy elsewhere and is 99% confident here, so its scores prove which encyclopedia characters are happy.” Identify the measurement problem and propose one concrete validation procedure on the intended domain, including what you would inspect or compare.

### 19. From named spans to a graph — 6 points

One paragraph contains two sentences:

1. `Iron Man met Ada in New York.`
2. `Tony Stark thanked Bo.`

For this exercise, Iron Man and Tony Stark are two names for **one** character. Ada and Bo are separate characters. New York is a place. Use the network conventions on the formula sheet.

**a. (2 points)** Write one BIO tag for each token of sentence 1, using exactly this tokenization:

```text
Iron | Man | met | Ada | in | New | York | .
```

**b. (2 points)** Across both sentences, how many distinct **person-name strings** were extracted, and how many **resolved character nodes** should there be? Give the alias mapping and explain why NER alone does not complete this step.

**c. (2 points)** Draw the sentence-level and paragraph-level character co-occurrence graphs. State the number of edges in each and identify the edge added by using the larger unit. Explain why that added edge does not prove an interaction.

### 20. Retrieve evidence, then generate — 6 points

**a. (2 points)** A normalized dense query has q = (0,1). Three normalized passage vectors are A = (1,0), B = (3/5,4/5), C = (0,1). Calculate all three cosine scores and rank the passages. Explain why dot products are sufficient.

**b. (2 points)** A relevant passage says `fixing cars`, but the query says `automobile repair`. Assume these are the only retained terms and they do not overlap. Explain the limitation of sparse TF-IDF here and what a dense representation would need to capture to help. Give one contrasting query situation in which sparse retrieval could work especially well.

**c. (2 points)** Draw the two stages of RAG, keeping retrieved evidence visible. Then diagnose these two runs for the question “Where was Mira born?” The corpus contains the correct passage “Mira was born in Harbor Town.”

- Run 1 retrieves only “Nilo was born in Hill Town” and answers “Hill Town.”
- Run 2 retrieves “Mira was born in Harbor Town” and answers “Hill Town.”

For each run, identify the demonstrated failure stage. In Run 1, distinguish the observable retrieval problem from any additional unsupported step in generation.

**End of test.** Check all 16 choices and four written tasks before opening the answer sheet.
