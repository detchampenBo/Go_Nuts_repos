// Lesson content for Tokenlingo, following the sections of Week 5
// ("From language to numbers") of DTU 02805 Social Graphs and Interactions.
//
// Exercise types:
//   choice  one correct option          multi   select every correct option
//   build   arrange word tiles          match   tap matching pairs
//   number  type a number               cut     snip a word into subword pieces
//   vector  build a Bag-of-Words count vector
(function () {
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

  // ---------- small visuals shown above an exercise ----------
  const CORPUS = [
    ["iron", "man", "fights", "the", "villain", "."],
    ["the", "villain", "escapes", "to", "new", "york", "."],
    ["iron", "man", "follows", "the", "villain", "to", "new", "york", "."],
    ["the", "city", "thanks", "iron", "man", "."],
  ];
  const corpus = () =>
    `<figure class="v v-corpus"><figcaption>Toy corpus · 4 sentences · already tokenized and lowercased</figcaption>${CORPUS.map(
      (s) => `<div class="v-tokrow">${s.map((t) => `<span class="v-tok">${esc(t)}</span>`).join("")}</div>`
    ).join("")}</figure>`;

  const code = (text, out) =>
    `<figure class="v v-code"><pre><code>${esc(text)}</code></pre>${out ? `<pre class="v-out"><code>${esc(out)}</code></pre>` : ""}</figure>`;

  const gen = () => {
    const rows = [["New", 0.55], ["Wakanda", 0.3], ["the", 0.15]];
    return `<figure class="v v-gen"><figcaption>Toki's toy table · hand-written teaching values, not a real model</figcaption>
      <p class="v-prompt">Iron Man flew to <span class="v-caret">▍</span></p>
      ${rows.map(([w, p]) => `<div class="v-bar"><span class="v-bar-label">${w}</span><span class="v-bar-track"><span style="width:${p * 100}%"></span></span><span class="v-bar-num">${p.toFixed(2)}</span></div>`).join("")}
    </figure>`;
  };

  function zipf(mode) {
    const W = 170, H = 120, pad = 22;
    const pts = Array.from({ length: 40 }, (_, i) => [i + 1, 1000 / (i + 1)]);
    const lin = pts.map(([r, f], i) => `${i ? "L" : "M"}${(pad + ((r - 1) / 39) * (W - pad - 8)).toFixed(1)} ${(H - pad - (f / 1000) * (H - pad - 10)).toFixed(1)}`).join(" ");
    const log = pts.map(([r, f], i) => `${i ? "L" : "M"}${(pad + (Math.log10(r) / Math.log10(40)) * (W - pad - 8)).toFixed(1)} ${(H - pad - ((Math.log10(f) - 1.3) / 1.7) * (H - pad - 10)).toFixed(1)}`).join(" ");
    const panel = (title, d, xl, yl) => `
      <svg viewBox="0 0 ${W} ${H + 8}" class="v-plot" role="img" aria-label="${title}">
        <text x="${W / 2}" y="9" class="v-plot-title">${title}</text>
        <line x1="${pad}" y1="${H - pad}" x2="${W - 6}" y2="${H - pad}" class="v-axis"/>
        <line x1="${pad}" y1="12" x2="${pad}" y2="${H - pad}" class="v-axis"/>
        <path d="${d}" class="v-curve"/>
        <text x="${W / 2 + 8}" y="${H - 5}" class="v-plot-label">${xl}</text>
        <text x="8" y="${H / 2}" class="v-plot-label" transform="rotate(-90 8 ${H / 2})">${yl}</text>
      </svg>`;
    return `<figure class="v v-zipf"><figcaption>Ideal Zipf curve, s = 1, ranks 1–40</figcaption><div class="v-plots">
      ${panel("linear axes", lin, "rank", "frequency")}
      ${mode === "both" ? panel("log-log axes", log, "log rank", "log freq") : ""}
    </div></figure>`;
  }

  const report = () => `<figure class="v v-report"><figcaption>From an AI-drafted report</figcaption>
    <blockquote>The Marvel corpus is dominated by the language of publishing rather than heroism: <mark data-k="A">the most frequent words are the, of, Marvel, Comics and published.</mark> <mark data-k="B">Frequency against rank is a straight line on log-log axes, which proves the corpus follows Zipf's law.</mark> And <mark data-k="C">power occurs 1,204 times, making it the central theme of the Marvel universe.</mark></blockquote></figure>`;

  const kwic = () => {
    const lines = [
      ["seized political", "power", "after the coup in Latveria"],
      ["absorbs electrical", "power", "from the city grid and"],
      ["her mutant", "power", "lets her control the weather"],
      ["a cosmic source of", "power", "known as the Phoenix Force"],
    ];
    return `<figure class="v v-kwic"><figcaption>Concordance for <b>power</b> · illustrative lines</figcaption>
      ${lines.map(([l, k, r]) => `<div class="v-kwic-row"><span class="l">…${l}</span><span class="k">${k}</span><span class="r">${r}…</span></div>`).join("")}</figure>`;
  };

  const MATRIX = {
    vocab: ["brains", "build", "future", "models", "predict", "the"],
    docs: [["brains predict the future", [1, 0, 1, 0, 1, 1]], ["models predict the future", [0, 0, 1, 1, 1, 1]], ["brains build models", [1, 1, 0, 1, 0, 0]]],
  };
  const matrix = (hiCol) => `<figure class="v v-matrix"><figcaption>Document-term matrix</figcaption><div class="v-scroll"><table>
    <thead><tr><th></th>${MATRIX.vocab.map((v, i) => `<th class="${i === hiCol ? "hi" : ""}">${v}</th>`).join("")}</tr></thead>
    <tbody>${MATRIX.docs.map(([d, row], j) => `<tr><th title="${d}">Doc ${j + 1}<small>${d}</small></th>${row.map((n, i) => `<td class="${i === hiCol ? "hi" : ""}">${n}</td>`).join("")}</tr>`).join("")}</tbody>
  </table></div></figure>`;

  const onehot = () => `<figure class="v v-matrix"><figcaption>One coordinate per vocabulary word</figcaption><div class="v-scroll"><table>
    <thead><tr><th>word</th><th>vector</th></tr></thead>
    <tbody><tr><th>dog</th><td class="mono">[1, 0, 0]</td></tr><tr><th>puppy</th><td class="mono">[0, 1, 0]</td></tr><tr><th>democracy</th><td class="mono">[0, 0, 1]</td></tr></tbody>
  </table></div></figure>`;

  const cosine = () => `<figure class="v v-formula"><figcaption>Cosine similarity</figcaption>
    <p class="mono">cos(x, y) = x · y / (‖x‖ ‖y‖)</p>
    <p class="mono small">x = [1, 0, 1, 0, 1, 1]  brains predict the future<br>y = [0, 0, 1, 1, 1, 1]  models predict the future</p></figure>`;

  // ---------- units and lessons ----------
  const UNITS = [
    {
      id: "u1", title: "From raw text to tokens", section: "Sections 1–2", char: "toki", color: "#58cc02", dark: "#58a700",
      lessons: [
        {
          id: "why", title: "Why language?", desc: "Language as data about people, and the next-token loop.",
          ex: [
            { type: "choice", say: "In Kuuk Thaayorre you don't ask for the beer on your right. You use the compass.", q: "How would a Kuuk Thaayorre speaker point you to the beer?", options: ["The beer southwest of you", "The beer on your left", "The beer in front of you", "The beer next to the chips"], answer: 0, why: "Kuuk Thaayorre uses absolute directions (north, south, east, west) where English uses left and right, so speakers always keep track of which way they face." },
            { type: "choice", say: "Gaby (2012) asked people to lay out pictures of a person growing older.", q: "How did Kuuk Thaayorre speakers order the pictures?", options: ["East to west, whichever way they were seated", "Always left to right", "Always right to left", "Oldest picture in the middle"], answer: 0, why: "The order followed the compass, not the table. Seat them facing another way and the sequence turns too. Language is data about how people think." },
            { type: "build", say: "Chatbots write one token at a time. Put the loop in order.", q: "Build the next-token loop", tiles: ["text so far", "probabilities for the next token", "pick one token", "append it", "look it up in a dictionary"], answer: ["text so far", "probabilities for the next token", "pick one token", "append it"], why: "A causal language model repeats: text so far → probabilities over possible next tokens → pick one → add it → do it again." },
            { type: "choice", say: "Here's my toy probability table.", visual: gen(), q: "Toki samples the next token 100 times. About how often is it 'Wakanda'?", options: ["About 30 times", "Never, the top token always wins", "About 55 times", "Exactly once"], answer: 0, why: "Sampling follows the probabilities, so roughly 30 out of 100. Only greedy decoding would always pick 'New'." },
            { type: "choice", say: "I asked the same prompt twice and got two different sentences!", q: "Why?", options: ["The model samples from probabilities, so it is stochastic", "The tokenizer changed between runs", "The vocabulary was shuffled", "Wikipedia was edited in between"], answer: 0, why: "A lower-probability pick can send the sentence somewhere new. A deterministic model would give the same output every time." },
          ],
        },
        {
          id: "tokens", title: "Tokens & types", desc: "Where does one piece of text end and the next begin?",
          ex: [
            { type: "build", say: "Python's split() cuts on spaces and nothing else.", visual: code(`raw = "Iron Man wasn't in New York."\nraw.split()`), q: "What does raw.split() return?", tiles: ["Iron", "Man", "wasn't", "in", "New", "York.", "was", "n't", "York", "."], answer: ["Iron", "Man", "wasn't", "in", "New", "York."], why: "Splitting on spaces keeps wasn't together and leaves the full stop glued to York." },
            { type: "build", say: "A language-aware tokenizer like spaCy makes other choices.", visual: code(`raw = "Iron Man wasn't in New York."`), q: "Build the spaCy-style tokens", tiles: ["Iron", "Man", "was", "n't", "in", "New", "York", ".", "wasn't", "York."], answer: ["Iron", "Man", "was", "n't", "in", "New", "York", "."], why: "Neither split is 'natural' or objectively right. Somebody wrote rules, or trained a model, that decided where the boundaries go." },
            { type: "number", say: "Count with me: the cat saw the other cat", q: "How many tokens?", answer: 6, why: "A token is one occurrence: the · cat · saw · the · other · cat = 6." },
            { type: "number", say: "Same sentence: the cat saw the other cat", q: "How many types?", answer: 4, why: "A type is a distinct form: the, cat, saw, other = 4. 'the' and 'cat' are two tokens each but one type each." },
            { type: "choice", say: "Apple apple APPLE", q: "Keep capitals: how many types? Lowercase first: how many?", options: ["3, then 1", "1, then 1", "3, then 3", "1, then 3"], answer: 0, why: "Type counts are partly a property of the corpus and partly of your preprocessing. Lowercasing collapses all three into one type." },
            { type: "match", q: "Tap the matching pairs", pairs: [["token", "one occurrence"], ["type", "one distinct form"], ["vocabulary", "the set of types"], ["token ID", "an integer index"], ["tokenization", "choosing boundaries"]] },
          ],
        },
        {
          id: "preprocess", title: "Preprocessing choices", char: "stoppy", desc: "Every cleaning step throws something away.",
          ex: [
            { type: "match", q: "Match each step to what it does", pairs: [["lowercasing", "Apple → apple"], ["stopword removal", "drops the, of, in"], ["lemmatization", "fighting → fight"], ["punctuation filter", "drops . , !"]] },
            { type: "multi", say: "I'm Stoppy. My friends and I get filtered out a lot.", q: "Select every stopword", options: ["the", "Thor", "of", "hammer", "in", "were"], answer: [0, 2, 4, 5], why: "Stopwords are very frequent function words. Thor and hammer are content words, the ones left behind after filtering." },
            { type: "build", say: "Lemmatize me: heroes were fighting", q: "Map each word to its lemma", tiles: ["hero", "be", "fight", "heroes", "was", "fought"], answer: ["hero", "be", "fight"], why: "Lemmatization maps word forms to dictionary forms: heroes → hero, were → be, fighting → fight. Number and tense are gone." },
            { type: "choice", say: "'The Big Apple' is New York. 'a big apple' is lunch.", q: "Which step erases the difference?", options: ["Lowercasing", "Tokenization", "Counting", "Stopword removal"], answer: 0, why: "Sometimes the capital letter is exactly the useful information. Lowercasing deletes it." },
            { type: "choice", say: "Here's my trick question. You measure 'power' as a share of all tokens.", q: "You remove stopwords. No 'power' token is removed. What happens to power's relative frequency?", options: ["It goes up, because the total shrinks", "It stays exactly the same", "It goes down", "It becomes zero"], answer: 0, why: "Relative frequency is count ÷ total tokens. Dropping the, of and in shrinks the total, so every remaining word looks more frequent." },
            { type: "choice", char: "toki", say: "A speech transcript is full of 'um' and 'uh'.", q: "When should you keep them as tokens?", options: ["When hesitation is part of what you study", "Never, they are noise", "Only after lemmatization", "Only when capitalized"], answer: 0, why: "The useful choice depends on what you measure. In speech, hesitations carry information." },
          ],
        },
        {
          id: "subwords", title: "Subword pieces", desc: "How a model reads a word it has never seen.",
          ex: [
            { type: "build", say: "From what you type to what the model sees.", q: "Put the pipeline in order", tiles: ["raw characters", "tokenizer", "token pieces", "token IDs", "model"], answer: ["raw characters", "tokenizer", "token pieces", "token IDs", "model"], why: "The model never sees 'apple' as a word. It sees token IDs: integers pointing into its vocabulary." },
            { type: "cut", say: "My vocabulary is these pieces plus every single letter. Go left to right and always take the longest piece that fits.", q: "Snip 'unbreakable' into pieces", vocab: ["un", "break", "able", "iron", "man", "hat", "tan", "wak", "anda"], word: "unbreakable", answer: ["un", "break", "able"], why: "un + break + able: three pieces, all in the vocabulary." },
            { type: "cut", say: "Same vocabulary. Longest piece first, left to right.", q: "Snip 'manhattan'", vocab: ["un", "break", "able", "iron", "man", "hat", "tan", "wak", "anda"], word: "manhattan", answer: ["man", "hat", "tan"], why: "man + hat + tan. The model can read Manhattan without ever storing the whole word." },
            { type: "cut", say: "One more from Marvel geography.", q: "Snip 'wakanda'", vocab: ["un", "break", "able", "iron", "man", "hat", "tan", "wak", "anda"], word: "wakanda", answer: ["wak", "anda"], why: "wak + anda: two pieces." },
            { type: "choice", say: "Now the villain.", q: "With the same vocabulary, how many tokens does 'thanos' cost?", options: ["6, one per letter", "2: than + os", "1", "It can't be represented"], answer: 0, why: "No multi-letter piece fits, so it falls back to letters: t·h·a·n·o·s. Expensive, but never unknown." },
            { type: "choice", say: "Byte-pair encoding builds vocabularies like mine.", q: "What does BPE start from, and what does it repeat?", options: ["Single characters; merge the most frequent neighbouring pair", "Whole words; split the rarest one", "A dictionary; delete stopwords", "Sentences; shuffle them"], answer: 0, why: "BPE keeps merging the most frequent adjacent pair until it reaches the target vocabulary size. Starting from characters means no word is ever completely unknown." },
            { type: "choice", q: "Heaps' law: as a corpus grows, the number of distinct types…", options: ["keeps growing, more and more slowly", "stops after 1,000 words", "shrinks", "grows exactly as fast as the tokens"], answer: 0, why: "New word forms keep turning up. A fixed subword vocabulary covers them with reusable pieces." },
          ],
        },
      ],
    },
    {
      id: "u2", title: "Counting language", section: "Section 3", char: "zipfy", color: "#ce82ff", dark: "#a568cc",
      lessons: [
        {
          id: "count", title: "Count first", desc: "Tokens, types, hapaxes and relative frequency.",
          ex: [
            { type: "number", say: "Before any model, count! This corpus has 28 tokens.", visual: corpus(), q: "How many times does 'the' occur?", answer: 4, why: "Once in each sentence. Count it yourself before you believe Counter." },
            { type: "choice", visual: corpus(), q: "counts.most_common(2) puts which two at the top?", options: ["'the' and '.'", "'iron' and 'man'", "'villain' and 'york'", "'fights' and 'city'"], answer: 0, why: "The definite article and a full stop win, 4 times each. That is a fact about English, not about superheroes." },
            { type: "multi", char: "hapax", say: "I'm Hapax. I show up exactly once.", visual: corpus(), q: "Select every hapax", options: ["fights", "villain", "escapes", "to", "follows", "city", "york", "thanks"], answer: [0, 2, 4, 5, 7], why: "fights, escapes, follows, city and thanks occur once each: 5 of the 13 types, almost 40%." },
            { type: "choice", char: "hapax", say: "Big corpora must get rid of me, right?", q: "Across 727,000 tokens of full Marvel pages, what share of the ~27,000 types occur only once?", options: ["About 36%", "About 1%", "About 90%", "None"], answer: 0, why: "The hapax share shrinks surprisingly slowly. More text keeps bringing in new rare words." },
            { type: "choice", q: "'the' occurs 4 times in 28 tokens. Its relative frequency is…", options: ["4 / 28 ≈ 0.14", "4", "28 / 4 = 7", "4 / 13 ≈ 0.31"], answer: 0, why: "Divide by the total number of tokens, not by the number of types." },
            { type: "choice", q: "Why use relative frequencies to compare documents?", options: ["Longer documents contain more of almost everything", "Raw counts can't be sorted", "They remove stopwords", "They fix the tokenizer"], answer: 0, why: "Dividing by length puts a short page and a long page on the same scale." },
          ],
        },
        {
          id: "zipf", title: "Zipf's law", desc: "A few words everywhere, and a very long tail.",
          ex: [
            { type: "choice", say: "My tail is long, like the vocabulary.", visual: zipf("linear"), q: "With s = 1, the word at rank 2 occurs about…", options: ["half as often as rank 1", "as often as rank 1", "twice as often", "100 times less often"], answer: 0, why: "f(r) ∝ 1 / r^s. With s = 1, rank 2 gets 1/2 of rank 1, and rank 10 gets 1/10." },
            { type: "number", q: "Rank 1 occurs 1,000 times. With s = 1, about how often does rank 10 occur?", answer: 100, why: "1,000 × 1/10 = 100." },
            { type: "choice", visual: zipf("both"), q: "Draw the same ideal curve on log-log axes. What does it become?", options: ["A straight line", "A circle", "The same steep curve", "A flat line"], answer: 0, why: "log f = −s · log r + c is a straight line with slope −s. Same numbers, different coordinate system." },
            { type: "choice", say: "Throwback to week 2!", q: "The rank-frequency plot is the CCDF with its axes swapped. Why?", options: ["A word's rank is the number of words at least that frequent", "Both always use linear axes", "Both need careful binning", "Words are nodes"], answer: 0, why: "The rank of a word with frequency f counts the words occurring at least f times, which is what a CCDF counts. That is also why neither plot needs binning." },
            { type: "choice", q: "The Marvel short-description curve is bumpier than Moby Dick's. A good reason?", options: ["303 short descriptions are a small corpus full of repeated Wikipedia phrasing", "Marvel fans write differently", "Zipf's law only holds for novels", "The log-log axes are broken"], answer: 0, why: "Corpus size, templated phrases like 'published by Marvel Comics', and the kind of text all bend the curve." },
          ],
        },
        {
          id: "flaw", title: "Spot the flaw", desc: "Catch an AI-drafted report overclaiming.",
          ex: [
            { type: "choice", say: "Three claims, three flaws. Let's go.", visual: report(), q: "Claim A lists 'the' and 'of' at the top. What is wrong with calling that a finding?", options: ["Function words top almost every English corpus", "The counts must be wrong", "'the' is not a word", "Nothing, it is a finding about Marvel"], answer: 0, why: "A frequency list is not a finding. You need a comparison before it says anything about Marvel." },
            { type: "choice", visual: report(), q: "Claim B says a straight log-log line 'proves' Zipf's law. What is honest?", options: ["The plot is suggestive, not proof", "It proves Heaps' law instead", "It proves the corpus is random", "It is proof, but only on linear axes"], answer: 0, why: "A straight-ish log-log line is consistent with Zipf. To say more you would fit it, compare alternatives and check the tails." },
            { type: "choice", char: "gramps", visual: report(), q: "Claim C: 'power' occurs 1,204 times, so it is the central theme. What do you check first?", options: ["A concordance: how is 'power' used?", "The number of hapaxes", "The tokenizer's speed", "Whether 'power' is a stopword"], answer: 0, why: "A raw count is not meaning. 'power' can be political, electrical or a superpower. Read it in context." },
            { type: "multi", q: "Which habits make a claim about a corpus honest?", options: ["State the preprocessing you used", "Say what you compared against", "Check examples in the raw text", "Trust the plot if the line looks straight", "Report the top counts as themes"], answer: [0, 1, 2], why: "What was counted, what it was compared against, and what you verified in the text." },
            { type: "choice", say: "Last one!", q: "Your code says 'power' occurs 1,204 times. Your own reading of the text disagrees. Who wins?", options: ["The text. Then find out what the code did", "The code, computers don't miscount", "Whichever number is bigger", "Average the two"], answer: 0, why: "If the code and the text disagree, the text wins. Work out what happened." },
          ],
        },
      ],
    },
    {
      id: "u3", title: "Words in context", section: "Section 3", char: "gramps", color: "#ff9600", dark: "#cd7900",
      lessons: [
        {
          id: "ngrams", title: "N-grams", desc: "Slide a window and keep a little order.",
          ex: [
            { type: "multi", say: "Each of my segments is a token. Slide a window over me!", q: "Select every bigram in 'New York City'", options: ["New York", "York City", "New City", "New York City", "City New"], answer: [0, 1], why: "Bigrams are neighbouring pairs: New York and York City. 'New York City' is the single trigram." },
            { type: "number", q: "A sentence has 6 tokens. How many trigrams does it contain?", answer: 4, why: "A window of 3 fits 6 − 3 + 1 = 4 times." },
            { type: "choice", q: "As n grows from 1 to 5, each n-gram keeps…", options: ["more local order, but exact repeats get rarer", "less order and more repeats", "the same information", "only stopwords"], answer: 0, why: "That is the context-versus-sparsity trade-off. A particular five-word sequence may occur once in the whole corpus." },
            { type: "choice", say: "This is next-token prediction too, just tiny.", q: "'New' is followed by 'York' 900 times and by 'car' 100 times. What is P(York | New)?", options: ["0.9", "0.1", "900", "0.5"], answer: 0, why: "P(York | New) = count(New York) ÷ count(New followed by anything) = 900 ÷ 1,000." },
            { type: "choice", q: "'dog bites man' and 'man bites dog' have identical unigram counts. Which bigram tells them apart?", options: ["dog bites", "bites", "man", "the"], answer: 0, why: "Only the first sentence contains 'dog bites'. Bigrams keep some order that unigrams throw away." },
            { type: "choice", q: "A trigram model predicts the next word from…", options: ["the two previous words", "the previous word only", "the whole document", "nothing, word frequency alone"], answer: 0, why: "Bigram: P(wₜ | wₜ₋₁). Trigram: P(wₜ | wₜ₋₂, wₜ₋₁)." },
          ],
        },
        {
          id: "context", title: "Concordance & collocations", desc: "What a count cannot tell you.",
          ex: [
            { type: "choice", say: "Every 'power' with its neighbours. Old-school, still great.", visual: kwic(), q: "What does this view show that a count of 'power' cannot?", options: ["Which senses of the word are in use", "How many types the corpus has", "The rank of 'power'", "Whether the corpus follows Zipf"], answer: 0, why: "A concordance (key word in context) puts the word in the middle so you can read how it is actually used." },
            { type: "match", q: "Match each NLTK tool to its question", pairs: [["concordance()", "each occurrence in context"], ["similar()", "words in comparable contexts"], ["collocation", "together more than expected"], ["common_contexts()", "contexts two words share"]] },
            { type: "choice", q: "similar('blue') returns 'red'. What does that tell you?", options: ["They occupy similar contexts, not that they're synonyms", "They are synonyms", "They form a bigram", "They have the same frequency"], answer: 0, why: "similar() only knows positions in this corpus. Similar context is not the same as similar meaning." },
            { type: "choice", q: "'of the' is the most frequent bigram. Is it a strong collocation?", options: ["No, 'of' and 'the' are so common they meet by chance", "Yes, frequency is association", "Yes, every bigram is a collocation", "No, collocations must be nouns"], answer: 0, why: "Association scores such as likelihood ratio or PMI compare a pair's count with what the separate word frequencies predict." },
            { type: "multi", q: "Which pairs behave like collocations?", options: ["machine learning", "climate change", "of the", "in a", "New York"], answer: [0, 1, 4], why: "These pairs act like units. 'of the' and 'in a' are frequent only because their words are." },
          ],
        },
      ],
    },
    {
      id: "u4", title: "From words to documents", section: "Sections 4–5", char: "baggy", color: "#1cb0f6", dark: "#1899d6",
      lessons: [
        {
          id: "bow", title: "Bag of Words", desc: "Turn a document into a row of counts.",
          ex: [
            { type: "vector", say: "Toss a document in. I count every vocabulary word.", q: "Build the vector for 'models predict the future'", vocab: ["brains", "build", "future", "models", "predict", "the"], doc: "models predict the future", answer: [0, 0, 1, 1, 1, 1], why: "One position per vocabulary term, in the same order for every document: [0, 0, 1, 1, 1, 1]." },
            { type: "vector", say: "Zeros count too.", q: "Build the vector for 'Loki tricks Thor and Thor tricks Loki'", vocab: ["and", "hulk", "loki", "smashes", "thor", "tricks"], doc: "loki tricks thor and thor tricks loki", answer: [1, 0, 2, 0, 2, 2], why: "hulk and smashes are in the vocabulary but not in this document, so their cells stay 0." },
            { type: "choice", visual: matrix(4), q: "Read down the 'predict' column. What does it say?", options: ["[1, 1, 0]: predict is in documents 1 and 2", "[0, 0, 1, 1, 1, 1]", "predict is the most common word", "[0, 0, 1]"], answer: 0, why: "Row view: one document across all terms. Column view: one term across all documents." },
            { type: "choice", visual: matrix(-1), q: "3 documents and 6 vocabulary terms. What shape is the document-term matrix?", options: ["3 × 6", "6 × 3", "6 × 6", "3 × 3"], answer: 0, why: "Rows are documents, columns are vocabulary terms. Some books use the transpose, the term-document matrix." },
            { type: "choice", q: "'fight' and 'fights' get separate columns. Which step would merge them?", options: ["Lemmatization", "Lowercasing", "Stopword removal", "Splitting on spaces"], answer: 0, why: "Lemmatization maps both forms to 'fight'. Every preprocessing choice changes the matrix." },
            { type: "choice", q: "The full Marvel pages have about 27,000 vocabulary terms. Most cells of their matrix are…", options: ["zero, so the matrix is sparse", "one", "negative", "the word's rank"], answer: 0, why: "Each page uses a small slice of the vocabulary, so the matrix is almost all zeros." },
          ],
        },
        {
          id: "collide", title: "The collision machine", desc: "Different meanings, same vector.",
          ex: [
            { type: "choice", say: "Shake shake shake. I forget the order!", q: "Which sentence gets the SAME vector as 'the dog chased the ball'?", options: ["the ball chased the dog", "a dog chased a ball", "the dog chased the balls", "the dog chased"], answer: 0, why: "Same words, same counts, same vector. Opposite story." },
            { type: "build", say: "Flip the meaning. Keep my vector.", q: "Rearrange 'brains predict models'", tiles: ["models", "predict", "brains"], answer: ["models", "predict", "brains"], why: "Both sentences give [1, 0, 0, 1, 1, 0] over brains, build, future, models, predict, the. Bag of Words can't tell them apart." },
            { type: "choice", q: "Where is losing word order probably fine?", options: ["Comparing what two political speeches talk about", "Working out who did what to whom", "Translating a sentence", "Spotting negation like 'not good'"], answer: 0, why: "Topic-level questions survive the bag. Questions about relations between words do not." },
            { type: "choice", q: "Bag of Words can't tell 'bank' (money) from 'bank' (river). Why?", options: ["Each type gets one column, whatever its context", "The tokenizer drops it", "It's a stopword", "Banks are rare"], answer: 0, why: "One column per type, so every sense of a word lands in the same cell." },
          ],
        },
        {
          id: "cosine", title: "Where counting stops", char: "cosi", desc: "Cosine similarity, and what counts can't see.",
          ex: [
            { type: "choice", say: "I'm Cosi. I only care about the angle between two vectors.", q: "A cosine of 1 means the two vectors…", options: ["point in the same direction", "share no terms", "have the same length", "are at right angles"], answer: 0, why: "1 means same direction. 0 means right angles, which for word counts means no shared terms." },
            { type: "choice", visual: cosine(), q: "What is cos(x, y)?", options: ["0.75", "3", "0.5", "1"], answer: 0, why: "x · y = 3 (future, predict, the). ‖x‖ = ‖y‖ = √4 = 2. So 3 ÷ (2 × 2) = 0.75." },
            { type: "choice", q: "A short page and a long page use words in exactly the same proportions. Their cosine is…", options: ["1", "0", "the ratio of their lengths", "undefined"], answer: 0, why: "Cosine divides by the lengths, so only direction counts." },
            { type: "choice", say: "Wolverine's page looks a lot like Quicksilver's. They aren't even linked.", q: "Why, with raw counts?", options: ["the, and and of dominate every vector", "They are secretly the same character", "Cosine favours short pages", "The link data is wrong"], answer: 0, why: "Remove the stopwords and language starts to rediscover the network: linked characters tend to be described in similar words." },
            { type: "choice", visual: onehot(), q: "cosine(dog, puppy) = ?", options: ["0, same as dog vs democracy", "1", "0.5", "Higher than dog vs democracy"], answer: 0, why: "Basis vectors are at right angles. Counted independently, words carry no information about how they relate." },
            { type: "choice", say: "Next week, words get vectors from the company they keep.", q: "Which idea takes us there?", options: ["Words in similar contexts often have related meanings", "Longer words carry more meaning", "Rare words matter most", "Alphabetical order encodes meaning"], answer: 0, why: "dog and puppy share neighbours like walk, leash and bark. Record those contexts and meaning starts to show up as geometry." },
          ],
        },
      ],
    },
    {
      id: "u5", title: "Week 5 Legendary", section: "Review", char: "hapax", color: "#ffc800", dark: "#e0a800",
      lessons: [
        { id: "legend", title: "Legendary challenge", legend: true, desc: "Ten questions drawn from the whole week. Every character shows up." },
      ],
    },
  ];

  const GLOSSARY = {
    u1: [
      ["NLP", "Methods for turning language into representations a computer can work with, then using them to perform a task."],
      ["Token", "One occurrence produced by a tokenizer. The same type can appear as many tokens."],
      ["Type · vocabulary", "A type is one distinct token form. The vocabulary is the set of types kept by the representation."],
      ["Tokenization", "Deciding where one text unit ends and the next begins. Different tokenizers can reasonably split the same string differently."],
      ["Subword tokenization", "Representing text with reusable pieces smaller than words, so unfamiliar words can still be represented."],
      ["Token ID", "The integer index used to look up a token or subword piece in a model's vocabulary."],
      ["Preprocessing", "Choices made before measurement, such as lowercasing, lemmatization, punctuation filtering and stopword removal. Each can remove useful information."],
      ["Stopword", "A very frequent function word, such as the, of or in, that many analyses drop."],
      ["Lemmatization", "Mapping each word form to its dictionary form: heroes → hero, were → be."],
    ],
    u2: [
      ["Frequency · relative frequency", "A raw count, or the count divided by the total number of tokens so corpora of different sizes compare more sensibly."],
      ["Hapax", "A type observed exactly once in the corpus."],
      ["Zipf's law", "Word frequency falls roughly as an inverse power of rank. A straight-ish log-log plot is suggestive, not proof."],
    ],
    u3: [
      ["Concordance / KWIC", "Every occurrence of a target word with a small window of surrounding text. It answers: how is this word used here?"],
      ["similar()", "NLTK's search for words in comparable immediate contexts. Similar context does not guarantee synonymy."],
      ["N-gram", "A sequence of neighbouring tokens. Longer n-grams keep more local order and become sparser."],
      ["Collocation", "A pair that occurs together more strongly than its words' separate frequencies predict."],
    ],
    u4: [
      ["Document", "The unit of text you choose to represent: a Wikipedia page, an article, a speech, a user's posts."],
      ["Bag of Words", "A document representation that counts vocabulary terms and discards word order."],
      ["Document-term matrix", "Rows are documents, columns are vocabulary terms, each cell is that term's count in that document."],
      ["Sparse matrix", "A matrix where most entries are zero, as when each document uses a small part of a large vocabulary."],
      ["Cosine similarity", "x · y ÷ (‖x‖ ‖y‖). 1 means same direction, 0 means no shared terms. Length does not matter."],
    ],
  };

  window.TL_UNITS = UNITS;
  window.TL_GLOSSARY = GLOSSARY;
})();
