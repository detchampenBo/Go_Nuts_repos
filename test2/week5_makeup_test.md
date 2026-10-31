# Week 5 make-up practice test — From language to numbers

**Time: 60 minutes · 40 points · Pen and paper · Closed book · No calculator or code**

This test uses the Week 5 **Essentials**, **On Test 2** skills and corresponding **Learn** exercises. All texts and numerical datasets below are small teaching examples; no knowledge of Marvel characters is needed.

Suggested timing: **24 minutes** for Questions 1–16, **32 minutes** for Tasks 17–20 (about eight minutes each), and **4 minutes** to check. Choose **one** answer per multiple-choice question. Each is worth **1 point**, with no penalty for an incorrect answer. Each written task is worth **6 points**. Show short working and labeled sketches; brief explanations are sufficient. Use separate paper for your answers.

## Formula and convention sheet

- Relative frequency = type count / total token count after the stated preprocessing.
- Percentage = relative frequency × 100.
- Number of contiguous n-gram occurrences in a sequence of L tokens = L − n + 1, for L ≥ n. Do not add boundary tokens.
- Observed/expected association ratio = observed pair count / expected pair count under independence. Expected counts are supplied whenever needed.
- For the ideal comparison curve in this paper, frequency at rank r is f(r) = K/r. On a log-log plot, both axes are logarithmic: equal spacing represents equal multiplicative changes, not equal additions.
- A count document-term matrix uses documents as rows and vocabulary terms as columns. Zero fraction = number of zero cells / total number of cells.
- Follow each question's explicit tokenization rules. Do not assume the behavior of a particular software library.

## Part A — Multiple choice

### 1. Where did the change happen?

A pipeline produces `["New", "York", "."]`, changes it to `["new", "york"]`, and then looks up integer IDs. Which account correctly identifies the decisions?

A. The model's next-token probabilities determined the original word boundaries.
B. The integer IDs made New York become two pieces.
C. Tokenization made the initial pieces; subsequent lowercasing and punctuation filtering changed them.
D. The IDs measure how meaningful each retained word is.

### 2. Lowercasing without filtering

The token list is `["Apple", "apple", "APPLE", "."]`. Lowercase every token and do nothing else. What remains?

A. 2 tokens and 2 types.
B. 4 tokens and 2 types.
C. 4 tokens and 4 types.
D. 3 tokens and 1 type.

### 3. An unfamiliar word

A toy vocabulary contains `un`, `mask`, `ing`, and every lowercase letter. After lowercasing, use the longest matching piece at each position, moving left to right. How is `Unmasking` represented?

A. One unknown token, because the whole word is absent.
B. `u | n | mask | i | n | g`, because single letters must always be chosen first.
C. One token whose ID is the number of letters in the word.
D. `un | mask | ing`; a whole word can be unfamiliar while its pieces are available.

### 4. Preprocessing removes the outcome

A researcher asks whether articles describe events in the past or present. They replace `was` and `is` by `be` before keeping only word counts. What is the main problem?

A. This lemmatization removes a distinction relevant to the research question.
B. It necessarily increases the number of tokens.
C. It preserves tense while removing only punctuation.
D. It makes a frequency table impossible to construct.

### 5. Comparing different-sized corpora

`power` occurs 8 times in 80 tokens in corpus A and 6 times in 30 tokens in corpus B. Which conclusion follows from relative frequency?

A. A uses it more often proportionally, because 8 exceeds 6.
B. B uses it twice as often proportionally: 20% versus 10%.
C. The rates are equal because both corpora contain the word.
D. These counts establish that power has the same meaning in both corpora.

### 6. A changing denominator

A corpus has 20 tokens, including 4 occurrences of `power`. Removing 10 stopword tokens removes no `power` tokens. Its relative frequency now is:

A. 40%, up from 20%, even though its raw count is unchanged.
B. 20%, because the numerator is unchanged.
C. 10%, because half the corpus was removed.
D. 80%, because every retained word doubles its raw count.

### 7. Reading a frequency table

| Type | Count |
|---|---:|
| iron | 3 |
| gate | 1 |
| metal | 1 |
| the | 5 |

Which statement is correct?

A. There are 4 tokens and 10 types.
B. `the` is a hapax because it has one table row.
C. There is one hapax: `iron`.
D. There are 10 tokens, 4 types and 2 hapax types.

### 8. Reading a log-log figure

Both axes below use equal spacing for a doubling. The four plotted points lie on an ideal f(r) = K/r curve.

```text
frequency
64 | *
32 |     *
16 |         *
 8 |             *
 4 |
   +-------------------- rank
     1   2   4   8   16
```

What frequency would extend that ideal curve to rank 16?

A. 0
B. 2
C. 4
D. 8

### 9. What does the figure establish?

A researcher finds an approximately straight decreasing rank-frequency pattern on log-log axes for a real corpus. Which statement is defensible?

A. Switching to logarithmic axes changed the actual word counts.
B. The pattern is consistent with a power-law-like relationship, but the picture alone does not prove an exact Zipf model.
C. The plot proves all preprocessing choices give identical frequencies.
D. Equal distances on the horizontal axis represent equal additions to rank.

### 10. Choosing the right inspection

You want to know whether `charge` refers to money or an attack in a set of documents. You also want a separate list of words found in comparable immediate contexts. Which pairing fits these two aims?

A. Frequency ranking for meanings; token IDs for comparable contexts.
B. A vocabulary list for meanings; document lengths for comparable contexts.
C. `similar()` for the original occurrences; a concordance for a list of replacement words.
D. A concordance for the original occurrences; `similar()` for words in comparable contexts.

### 11. A misleading similarity claim

In a corpus, both `hot` and `cold` frequently occur between `the` and `water`. A context-based search returns one as similar to the other. What is the best interpretation?

A. They share usage contexts; this does not make them synonyms.
B. The corpus proves they have the same temperature meaning.
C. The search must have used a dictionary of synonyms.
D. Comparable contexts imply identical raw frequencies.

### 12. Increasing n

For `red robots help blue robots`, compare contiguous trigrams with unigrams. Which statement is correct?

A. There are five trigram occurrences, each preserving less order than a unigram.
B. There are three trigrams, and longer sequences must repeat more often across a corpus.
C. There are three trigram occurrences; they preserve more local order, but exact longer sequences tend to be rarer.
D. Trigrams recover the complete document order for every possible document.

### 13. Frequency versus association

Expected counts have already been calculated from the individual word frequencies under independence.

| Pair | Observed count | Expected count |
|---|---:|---:|
| of the | 30 | 30 |
| silver shield | 8 | 2 |

Which statement is supported?

A. `of the` has stronger association because it occurs more often.
B. Both pairs occur four times more often than expected.
C. The less frequent pair cannot be a collocation.
D. `silver shield` has the larger observed/expected ratio, despite its smaller raw count.

### 14. Reading a matrix in two directions

| Document | robot | river | saves |
|---|---:|---:|---:|
| D1 | 2 | 0 | 1 |
| D2 | 0 | 1 | 1 |

What does the `river` column `[0, 1]` say?

A. D1 and D2 contain zero and one tokens in total.
B. `river` occurs zero times in D1 and once in D2.
C. There are zero river-related meanings in D1 and one in D2.
D. D2 contains `river` before `saves`.

### 15. Predicting a matrix edit

A count matrix has 3 document rows and 5 vocabulary columns. Add one previously unseen word once to D2 and rebuild the vocabulary, keeping the documents unchanged otherwise. What happens?

A. A fourth document row is created.
B. Every existing count increases by one.
C. The matrix has 3 rows and 6 columns; the new word's column is `[0, 1, 0]`.
D. Every cell in the new column must be nonzero.

### 16. Matching representation to question

One team wants to compare vocabulary use across articles. Another wants to distinguish `robots chase birds` from `birds chase robots`. Which choice best fits?

A. Word counts can support the first aim; local order or original text is needed for the second distinction.
B. Unigram counts distinguish both sentences because their subjects differ.
C. Removing all word order improves the second task without losing relevant information.
D. A vocabulary set alone records how often each word occurs.

## Part B — Draw, calculate and explain

### 17. Make the preprocessing visible — 6 points

Raw document: **`Heroes help heroes.`**

Rules: split at spaces, separate the final full stop as its own token, and preserve case initially. Later operations, in order, are lowercasing, removing punctuation, and mapping `heroes` to `hero`. Apply no other changes.

**a. (2 points)** Draw a short arrow pipeline from the raw document through the initial tokens and each later operation. Write the token count and type count under each token list.

**b. (2 points)** For the final token list, make a frequency table. Give the relative frequency of `hero` and identify every hapax type. A fraction is sufficient.

**c. (2 points)** Using pieces `un`, `mask`, `ed`, plus every lowercase letter, split `unmasked` by longest match from left to right. Explain why character pieces help with unfamiliar words, and give one question for which merging `heroes` and `hero` would remove useful information.

### 18. Build and change a document-term matrix — 6 points

Each line is one document. Lowercase, remove the full stops, split on spaces and make no other changes.

- D1: `Robots help birds.`
- D2: `Birds help robots.`
- D3: `Robots help robots.`

**a. (2 points)** Draw the count document-term matrix with alphabetically ordered columns. State what the D3 row and the `birds` column mean.

**b. (2 points)** Give the fraction of zero cells. Then append `quietly` once to D2: state the new matrix dimensions and draw only the new column. Explain briefly why large real document-term matrices often have many zeros.

**c. (2 points)** Explain why D1 and D2 receive identical count vectors despite saying different things. Give one question this matrix can answer and one it cannot answer.

### 19. Local order and collocations — 6 points

Token sequence: **`small robots help small birds`**. Do not add start/end tokens.

**a. (2 points)** Draw the sliding windows, or an equivalent bracketed list, for all bigrams and trigrams. Give the unigram frequency table.

**b. (2 points)** In a larger corpus, `small robots` occurs 6 times against an expected count of 2; `of the` occurs 20 times against an expected count of 20. Calculate both observed/expected ratios. Explain why the most frequent pair is not the strongest association here.

**c. (2 points)** Explain the context-versus-sparsity trade-off when moving from bigrams to trigrams. Then choose between a concordance and `similar()` to investigate whether `small` describes physical size or organizational importance, and justify your choice.

### 20. A figure and a claim — 6 points

These are all the types in a tiny corpus, already sorted by decreasing frequency.

| Rank | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| Type | the | power | city | shield | river |
| Count | 8 | 4 | 2 | 1 | 1 |

**a. (2 points)** Sketch frequency against rank on ordinary linear axes. Mark the five points and label both axes. Explain what changes, and what stays unchanged, if the same data are redrawn on log-log axes.

**b. (2 points)** Calculate the total number of tokens, the relative frequency of `power`, and the fraction of types that are hapax types.

**c. (2 points)** Critique this report in two or three sentences: “The most frequent word is `the`, so the corpus is mainly about grammar. `power` occurs four times, proving political power is its central theme. The roughly straight log-log plot proves exact Zipf's law.” Identify the unsupported interpretations and name a concrete check of the underlying text or comparison data.

**End of test.** Check that you have answered 16 multiple-choice questions and all four written tasks before opening the answer sheet.
