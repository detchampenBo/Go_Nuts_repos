# Tokenlingo · Week 5

A Duolingo-style lesson path for Week 5 of 02805, *From language to numbers*.
Open `index.html` (no build step, no server logic).

## Cast

Seven heroes from the Marvel network the course has used since week 1, drawn in a flat,
round, big-eyed lesson-app style. Each one embodies one idea from the week, so the hero on
screen tells you which concept the question is about.

| Hero | Role | Concept |
| --- | --- | --- |
| Wolverine | The Tokenizer | tokens, types, token IDs, subword pieces (claws cut the text) |
| Ant-Man | The Shrinker | preprocessing: lowercasing, stopwords, lemmatization shrink words |
| Hulk | The Counter | counting and Zipf's law ("HULK COUNT FIRST") |
| Nick Fury | The Hapax | words seen exactly once; one eye, one appearance |
| Spider-Man | The N-gram | n-grams and context; "New York" is one place |
| Loki | The Bag of Words | keeps the counts, scrambles the order |
| Iron Man | The Cosine | cosine similarity; direction, not length |

The heroes are fan-art drawings made for a non-commercial course exercise. Marvel
characters belong to Marvel.

## Files

- `lessons.js`: all units, lessons, exercises and the guidebook glossary. Edit content here.
- `characters.js`: the SVG heroes and their expressions (idle, happy, sad, think).
- `app.js`: path, lesson runner, exercise types, XP, streak and daily quests.
- `styles.css`: light and dark themes.

Exercise types: `choice`, `multi`, `build` (word tiles), `match` (pairs), `number`,
`cut` (snip a word into subword pieces) and `vector` (build a Bag-of-Words row).
Wrong answers cost a heart and come back at the end of the lesson. Progress is kept in
the browser's localStorage only.
