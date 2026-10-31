# Week 6 make-up practice test — From counts to meaning

**Time: 60 minutes · 40 points · Pen and paper · Closed book · No calculator or code**

This test uses the Week 6 **Essentials**, **On Test 2** skills and corresponding **Learn** exercises. All numerical examples are self-contained. Use the definitions printed here, rather than software defaults.

Suggested timing: **24 minutes** for Questions 1–16, **32 minutes** for Tasks 17–20 (about eight minutes each), and **4 minutes** to check. Choose **one** answer per multiple-choice question. Each is worth **1 point**, with no penalty for an incorrect answer. Each written task is worth **6 points**. Show short working, labeled drawings and brief explanations on separate paper.

## Formula and convention sheet

- N = number of documents; |d| = number of tokens in document d.
- DF(t) = number of documents containing t at least once.
- TF(t,d) = count(t,d)/|d|.
- IDF(t) = ln[N/DF(t)], with no smoothing or added constant.
- TF-IDF(t,d) = TF(t,d) × IDF(t).
- Use **ln(1) = 0, ln(2) ≈ 0.7, ln(4) ≈ 1.4** for this paper. Exact multiples of ln(2), or fractions using the supplied approximations, are acceptable. No other logarithm needs numerical evaluation for TF-IDF.
- Dot product A·B = sum of coordinate-by-coordinate products.
- Length ||A|| = square root of the sum of squared coordinates.
- Cosine(A,B) = (A·B)/(||A|| ||B||), for nonzero vectors. Useful roots: √16 = 4, √25 = 5, √100 = 10.
- For a word-context count table with grand total M: P(w,c) = cell/M; P(w) = row total/M; P(c) = column total/M.
- PMI(w,c) = log₂[P(w,c)/(P(w)P(c))]. PPMI(w,c) = max(PMI(w,c), 0).
- Use **log₂(1) = 0, log₂(2) = 1, log₂(1/2) = −1, log₂(3/2) ≈ 0.585**. The last value may be left as log₂(3/2).
- A symmetric context window of k includes up to k tokens on each side, excludes the center, and does not cross sentence boundaries. Keep repeated context occurrences.

## Part A — Multiple choice

### 1. Document frequency is not a token count

Across four documents, `shield` occurs respectively 3, 0, 1 and 0 times. What is its DF?

A. 1
B. 3
C. 4
D. 2

### 2. A corpus-specific common word

`galaxy` occurs in every document of a collection. Under this paper's TF-IDF definition, what happens to it?

A. Its IDF is zero even if it is not on an English stopword list.
B. Its IDF is largest because every document uses it.
C. Its TF must be zero in every document.
D. Its IDF increases with repeated occurrences inside one document, even when DF is unchanged.

### 3. Separating TF from IDF

Within the same collection, a term occurs twice in a four-token document A and twice in an eight-token document B. Its IDF is positive. Which statement holds?

A. Its weight in B is twice its weight in A.
B. Its weight in A is twice its weight in B.
C. The weights are equal because both raw counts are two.
D. A and B must use different IDF values for this term.

### 4. Predicting a rescaling

The cosine of nonzero vectors x and y is 0.6. Replace x by 5x. The new cosine is:

A. 3.0
B. 0.12
C. 0.6
D. 1.0

### 5. Reading an angle

Two nonzero TF-IDF vectors have no nonzero vocabulary coordinate in common. What does their cosine indicate?

A. Cosine 0: they are perpendicular in this representation, which does not prove unrelated meanings.
B. Cosine 1: no overlap is the strongest possible match.
C. Cosine −1: nonnegative TF-IDF weights make opposite directions inevitable.
D. Cosine 0: the documents cannot discuss the same subject in different words.

### 6. What object does a row represent?

In matrix X, the cell at row `article 3`, column `river` is a count. In matrix Y, the cell at row `bank`, column `river` counts occurrences within a chosen context window. Which description is correct?

A. Both rows represent documents, because both matrices contain words.
B. X's columns are documents and Y's columns are topic labels.
C. Y's cell counts every occurrence of `river` anywhere in the corpus, independently of `bank`.
D. X represents documents by vocabulary counts; Y represents target words by nearby context-word counts.

### 7. Reading a two-corpus term plot

This plot uses **linear** axes: horizontal = uses per 100 tokens in corpus A; vertical = uses per 100 tokens in corpus B. Each letter is one term. S is at (0,8), M at (8,8), and N at (8,0).

```text
B rate
8 | S               M
  |
4 |
  |
0 +-----------------N---- A rate
    0       4       8
```

Which interpretation is correct?

A. M is distinctive of A; S is distinctive of neither group.
B. M is common in both; S is comparatively distinctive of B; N of A.
C. N is used more in B; S more in A.
D. All three terms have identical rates because there are three points.

### 8. What a term plot cannot show

`charge` lies on the diagonal of a two-corpus rate plot. One analyst claims this proves it has the same meaning in both groups. What should you conclude?

A. Equal rates guarantee identical contexts.
B. The plot must be wrong because ambiguous words cannot be plotted.
C. The plot establishes comparable usage rates; inspecting occurrences is needed to assess meaning.
D. A term on the diagonal must have zero occurrences.

### 9. Avoiding an inverted probability

In an LDA topic T, the word `gene` has probability 0.2. Which interpretation is valid?

A. Every document containing `gene` has exactly 20% topic T.
B. A document has a 20% chance of containing `gene` at least once, regardless of length.
C. Twenty percent of all documents must belong exclusively to T.
D. Conditional on drawing a word from T's word distribution, `gene` has probability 0.2.

### 10. Reading topic mixtures

Two documents have LDA mixtures A = [0.9, 0.1] and B = [0.5, 0.5] over the same two topics. Which is best supported?

A. B contains twice as many words as A.
B. A is easier to summarize with one dominant topic; B gives equal mixture weight to both.
C. A belongs to only one topic because 0.9 is large.
D. The mixture values are probabilities over individual vocabulary words.

### 11. A fitted solution is not a discovery of fixed labels

After fitting four LDA topics once, an analyst labels a word list `Technology` and declares that the model discovered exactly four true themes. What is the best correction?

A. The label is an interpretation; topic count, preprocessing and initialization can affect the fitted solution, which needs inspection and comparison.
B. The chosen number of topics is guaranteed to equal the true number of themes.
C. The model generated the English label directly, so it cannot be disputed.
D. Changing preprocessing can only change plotting colors.

### 12. Changing the context window

For `blue robot repairs red ship`, take `repairs` as the center. What changes when the symmetric window expands from 1 to 2?

A. The center itself becomes a context word.
B. `robot` and `red` are removed.
C. `blue` and `ship` are added, supplying broader context beyond the immediate neighbors.
D. The context becomes only the words to the right of the center.

### 13. From PMI to PPMI

A word-context pair occurs half as often as independence predicts. Its PMI is log₂(1/2) = −1. What does PPMI do?

A. Keeps −1, to emphasize a negative association.
B. Replaces it with 0; the pair is below its independence baseline.
C. Changes it to +1 by taking its absolute value.
D. Changes its observed raw count to zero in the original corpus.

### 14. A cheaper training task

A vocabulary has 50,000 words. A learner contrasts an observed center-context pair with five sampled noise pairs instead of scoring the whole vocabulary. Which interpretation fits?

A. It has proved the sampled words are unrelated in every possible context.
B. It has deleted the five words permanently from the vocabulary.
C. It has replaced training with a manually written synonym dictionary.
D. It is using negative sampling to make each training step cheaper; the noise labels are not universal semantic judgments.

### 15. Comparing static methods

One team uses PPMI rows, another Word2Vec, and a third GloVe learned from global co-occurrence statistics. Each stores one vector per word type. What common limitation matters for `bank`?

A. None of the methods can use context statistics during construction.
B. All methods require each vector coordinate to have the same named meaning.
C. Each uses one fixed representation for both river and financial occurrences, even though the construction methods differ.
D. All three compute a fresh sentence-dependent vector at each occurrence.

### 16. High cosine is evidence of what?

`hero` and `villain` have high cosine in a trained word embedding. Which statement is justified?

A. Their learned representations are aligned, potentially reflecting shared contexts; inspect usage before making a meaning claim.
B. They must be interchangeable in every sentence.
C. The embedding has established that they have the same moral role.
D. High cosine shows that neither word appeared near common context words.

## Part B — Draw, calculate and explain

### 17. TF-IDF from a tiny corpus — 6 points

The four documents are already tokenized. Each contains four tokens.

```text
D1: common alloy magic magic
D2: common common alloy alloy
D3: common common common common
D4: common common common common
```

**a. (2 points)** Draw a table with one row each for `common`, `alloy` and `magic`, and columns for DF and IDF. Fill it using the supplied logarithm values.

**b. (2 points)** Add columns for TF in D1 and TF-IDF in D1. Which term has the largest weight in D1? Explain why comparing raw counts alone would miss part of the weighting decision.

**c. (2 points)** Replace one `common` in D4 with `alloy`. Without evaluating a new logarithm, predict whether `alloy`'s TF, IDF and TF-IDF **in D1** increase, decrease or stay the same. Explain the role of the collection in this change.

### 18. Geometry you can draw — 6 points

Let A = (3,4), B = (6,8), C = (4,0).

**a. (2 points)** Draw the three arrows from the origin on labeled axes. Calculate their lengths and identify which pair has the same direction.

**b. (2 points)** Calculate cosine(A,B) and cosine(A,C), showing dot products and lengths. Give exact fractions where appropriate and compare the answers with your sketch.

**c. (2 points)** Replace A with 2A. State both new cosine values without repeating all the arithmetic, and explain why they remain unchanged. If these were document vectors, what would equal direction establish about the representation, and what would it not establish about meaning?

### 19. A common context versus an informative context — 6 points

The following is the complete table of counted target-context pairs for this exercise. Use these table totals, not a separate token total.

| Target word | the | bark | money |
|---|---:|---:|---:|
| dog | 4 | 3 | 1 |
| bank | 4 | 1 | 3 |

**a. (2 points)** Copy the table, adding row totals, column totals and the grand total. For `(dog, bark)`, calculate P(dog,bark), P(dog), P(bark) and the probability expected under independence, P(dog)P(bark).

**b. (2 points)** Calculate PMI and PPMI for `(dog, bark)` and `(dog, money)`. Use the supplied logarithm values; no approximation by hand is necessary.

**c. (2 points)** Calculate PMI for `(dog, the)`. Explain why a frequent context can receive zero PPMI and why reweighting entire rows this way can change their nearest neighbors under cosine similarity. Do not calculate a full cosine here.

### 20. Two ways to model the same corpus — 6 points

One researcher trains word vectors; another fits LDA to the same documents.

**a. (2 points)** For the sentence `young robots repair small ships`, use center `repair` and symmetric window 2. Write every Skip-gram input → target pair and the corresponding single CBOW input → target example. Explain which direction of prediction changes.

**b. (2 points)** LDA gives document D topic mixture `[3/4 T1, 1/4 T2]`. Draw a four-part bar showing it. T1's highest-probability words are `ship, orbit, planet`. State what the bar represents and how that differs from T1's distribution over words. Is this two-distribution structure a definition of all topic modeling, or the particular model used by LDA?

**c. (2 points)** Critique this report in three short sentences: “The model itself named T1 Space. This single fit has revealed the corpus's definitive topics. The word vectors put `hero` close to `villain`, proving that they are synonyms.” Include one concrete inspection or rerun that would strengthen the analysis.

**End of test.** Check all 16 choices and four written tasks before opening the answer sheet.
