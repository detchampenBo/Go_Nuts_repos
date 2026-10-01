# Tokenlingo · Week 5

A Duolingo-style lesson path for Week 5 of 02805, *From language to numbers*.
Open `index.html` (no build step, no server logic).

## Cast

Each character embodies one idea from the week, so the character on screen tells you
which concept the question is about.

| Character | Role | Concept |
| --- | --- | --- |
| Toki | The Tokenizer | tokens, types, token IDs, subword pieces (scissors on its head) |
| Stoppy | The Stopword | preprocessing; wears a "the" label and holds a stop sign |
| Zipfy | The Long Tail | counting and Zipf's law; its spots shrink as 1/rank along the tail |
| Hapax | Seen Only Once | hapax types; a one-eyed unicorn |
| Gramps | The N-gram | n-grams and context; a caterpillar of tokens with a bigram window |
| Baggy | The Bag of Words | document vectors; words tumble out of order |
| Cosi | The Cosine | cosine similarity; antennae measure an angle θ |

## Files

- `lessons.js`: all units, lessons, exercises and the guidebook glossary. Edit content here.
- `characters.js`: the SVG cast and their expressions (idle, happy, sad, think).
- `app.js`: path, lesson runner, exercise types, XP, streak and daily quests.
- `styles.css`: light and dark themes.

Exercise types: `choice`, `multi`, `build` (word tiles), `match` (pairs), `number`,
`cut` (snip a word into subword pieces) and `vector` (build a Bag-of-Words row).
Wrong answers cost a heart and come back at the end of the lesson. Progress is kept in
the browser's localStorage only.
