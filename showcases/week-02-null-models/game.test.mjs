import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { newGame, currentCard, submit, advance, saveScore, readLeaderboard, STORAGE_KEY } from "./game.mjs";

const data = JSON.parse(readFileSync(new URL("./puzzle-data.json", import.meta.url)));
const storage = () => {
  const items = new Map();
  return { getItem: key => items.get(key) ?? null, setItem: (key, value) => items.set(key, value) };
};

function correctChoice(game) {
  const card = currentCard(game);
  if (!card) return game.round === 6 ? "stay" : "lower";
  return game.row.filter(id => data.heroes[id][card.metric] < data.heroes[card.id][card.metric]).length;
}

function complete(id = "01", correct = true) {
  const game = newGame(data, id);
  for (let i = 0; i < 8; i++) {
    const choice = correctChoice(game);
    const wrong = currentCard(game) ? (choice + 1) % (game.row.length + 1) : i === 6 ? "change" : "higher";
    submit(game, data, correct ? choice : wrong);
    advance(game, data);
  }
  return game;
}

for (const puzzle of data.puzzles) {
  test(`puzzle ${puzzle.id}: all eight predictions complete with a score of 800`, () => {
    const game = complete(puzzle.id);
    assert.equal(game.phase, "complete");
    assert.equal(game.score, 800);
    assert.equal(game.answers.length, 8);
    assert.equal(currentCard(game), null);
  });
  test(`puzzle ${puzzle.id}: wrong placements correct the row and play can continue`, () => {
    const game = complete(puzzle.id, false);
    assert.equal(game.score, 0);
    assert.equal(game.phase, "complete");
    assert.equal(game.row.length, 5);
    const values = game.row.map(id => data.heroes[id].clustering);
    assert.deepEqual(values, values.toSorted((a, b) => a - b));
  });
}

test("each answer is scored once; invalid input and skipping cannot change the game", () => {
  const game = newGame(data, "01");
  assert.equal(advance(game, data), false);
  for (const invalid of [null, -1, 3, 0.5, "0", "stay"]) assert.equal(submit(game, data, invalid), null);
  assert.equal(game.answers.length, 0);
  submit(game, data, correctChoice(game));
  assert.equal(game.score, 100);
  assert.equal(submit(game, data, 0), null);
  assert.equal(game.score, 100);
  assert.equal(game.row.length, 3);
});

test("stage transition starts a fresh clustering lineup", () => {
  const game = newGame(data, "01");
  for (let i = 0; i < 3; i++) { submit(game, data, correctChoice(game)); advance(game, data); }
  assert.equal(game.round, 3);
  assert.equal(currentCard(game).metric, "clustering");
  assert.equal(game.row.length, 2);
  assert.deepEqual(new Set(game.row), new Set(game.puzzle.clustering.slice(0, 2)));
});

test("equal-valued cards allow either adjacent insertion position", () => {
  const fixture = { heroes: { a: { degree: 3 }, b: { degree: 3 }, c: { degree: 3 } }, puzzles: [{ id: "t", degree: ["a", "b", "c"] }] };
  for (const position of [0, 1, 2]) assert.equal(submit(newGame(fixture, "t"), fixture, position).correct, true);
});

test("only completed games with a nonblank name can be saved", () => {
  const store = storage();
  assert.throws(() => saveScore(store, newGame(data, "01"), "Test", "x"));
  assert.throws(() => saveScore(store, complete(), " \n ", "x"));
  assert.deepEqual(readLeaderboard(store), []);
});

test("scores persist, duplicate submissions are ignored, ties use earlier submission", () => {
  const store = storage();
  saveScore(store, complete("01", false), "First", "a", 1);
  saveScore(store, complete(), "  Ada  ", "b", 2);
  saveScore(store, complete(), "Later", "c", 3);
  saveScore(store, complete(), "Duplicate", "b", 4);
  saveScore(store, complete("02"), "Another puzzle", "d", 5);
  const entries = readLeaderboard(store);
  assert.equal(entries.length, 4);
  assert.deepEqual(entries.filter(e => e.puzzle === "01").map(e => e.name), ["Ada", "Later", "First"]);
  assert.equal(entries[0].score, 800);
});

test("malformed storage and invalid entries do not break the leaderboard", () => {
  const store = storage();
  for (const raw of ["broken", "null", "{}", "123", "[null,7,{}]"]) {
    store.setItem(STORAGE_KEY, raw);
    assert.deepEqual(readLeaderboard(store), []);
  }
  store.setItem(STORAGE_KEY, JSON.stringify([{ id: "x", puzzle: "01", name: "X", score: 900, date: 1 }]));
  assert.deepEqual(readLeaderboard(store), []);
  saveScore(store, complete(), "Recovered", "y");
  assert.equal(readLeaderboard(store)[0].name, "Recovered");
});

test("storage write errors propagate so the interface can offer a retry", () => {
  const store = { getItem: () => null, setItem: () => { throw new Error("Storage blocked"); } };
  assert.throws(() => saveScore(store, complete(), "Ada", "x"), /Storage blocked/);
});

test("each puzzle keeps its best 50 scores without crowding out other puzzles", () => {
  const store = storage();
  const game = complete();
  for (let i = 0; i < 55; i++) saveScore(store, game, "Player", String(i), i);
  saveScore(store, complete("02", false), "Second puzzle", "other", 100);
  assert.equal(readLeaderboard(store).filter(e => e.puzzle === "01").length, 50);
  assert.equal(readLeaderboard(store).filter(e => e.puzzle === "02").length, 1);
});

test('activity selection starts the matching content and excludes partial runs from leaderboard', () => {
  for (const stage of [1, 2]) {
    const game = newGame(data, '01', stage);
    assert.equal(game.round, stage * 3);
    assert.equal(currentCard(game)?.metric ?? 'shuffle', stage === 1 ? 'clustering' : 'shuffle');
    while (game.phase !== 'complete') {
      submit(game, data, correctChoice(game));
      advance(game, data);
    }
    assert.equal(game.answers.length, 8 - stage * 3);
    assert.equal(game.score, (8 - stage * 3) * 100);
    assert.throws(() => saveScore(storage(), game, 'Practice', 'practice'));
  }
});
