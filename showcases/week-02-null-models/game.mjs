export const MAX_SCORE = 800;
export const STORAGE_KEY = "marvel-lineup-leaderboard-v1";

export function value(data, id, metric) {
  return data.heroes[id][metric];
}

export function newGame(data, puzzleId, stage = 0) {
  if (![0, 1, 2].includes(stage)) throw new Error("Unknown activity");
  const puzzle = data.puzzles.find(p => p.id === puzzleId);
  if (!puzzle) throw new Error("Unknown puzzle");
  return { puzzle, startRound: stage * 3, round: stage * 3, phase: "answering", score: 0, answers: [],
    row: puzzle[stage === 0 ? "degree" : "clustering"].slice(0, 2).sort((a, b) => value(data, a, stage === 0 ? "degree" : "clustering") - value(data, b, stage === 0 ? "degree" : "clustering")) };
}

export function currentCard(game) {
  if (game.round >= 6) return null;
  const metric = game.round < 3 ? "degree" : "clustering";
  return { id: game.puzzle[metric][2 + game.round % 3], metric };
}

export function submit(game, data, choice) {
  if (game.phase !== "answering") return null;
  const card = currentCard(game);
  let correct;
  if (card) {
    if (!Number.isInteger(choice) || choice < 0 || choice > game.row.length) return null;
    const target = value(data, card.id, card.metric);
    correct = (choice === 0 || value(data, game.row[choice - 1], card.metric) <= target)
      && (choice === game.row.length || target <= value(data, game.row[choice], card.metric));
    game.row.push(card.id);
    game.row.sort((a, b) => value(data, a, card.metric) - value(data, b, card.metric));
  } else {
    const allowed = game.round === 6 ? ["stay", "change"] : ["lower", "same", "higher"];
    if (!allowed.includes(choice)) return null;
    const expected = game.round === 6 ? "stay"
      : data.shuffleMean < data.clustering ? "lower" : data.shuffleMean > data.clustering ? "higher" : "same";
    correct = choice === expected;
  }
  const result = { correct, choice, card, round: game.round };
  game.answers.push(result);
  game.score += correct ? 100 : 0;
  game.phase = "revealed";
  return result;
}

export function advance(game, data) {
  if (game.phase !== "revealed") return false;
  if (game.round === 7) {
    game.phase = "complete";
    return true;
  }
  game.round++;
  game.phase = "answering";
  if (game.round === 3) {
    game.row = game.puzzle.clustering.slice(0, 2)
      .sort((a, b) => value(data, a, "clustering") - value(data, b, "clustering"));
  }
  return true;
}

export function cleanName(name) {
  return String(name).replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, 24);
}

export function readLeaderboard(storage) {
  const raw = storage.getItem(STORAGE_KEY);
  if (!raw) return [];
  let entries;
  try { entries = JSON.parse(raw); } catch { return []; }
  if (!Array.isArray(entries)) return [];
  return entries.filter(e => e && typeof e.id === "string" && typeof e.puzzle === "string"
    && typeof e.name === "string" && cleanName(e.name).length > 0
    && Number.isInteger(e.score) && e.score >= 0 && e.score <= MAX_SCORE && e.score % 100 === 0
    && Number.isFinite(e.date));
}

export function saveScore(storage, game, name, id, date = Date.now()) {
  const cleaned = cleanName(name);
  if (game.phase !== "complete" || game.startRound > 0 || game.answers.length !== 8 || !cleaned) throw new Error("Complete a puzzle and enter a name first.");
  const entries = readLeaderboard(storage);
  if (!entries.some(e => e.id === id)) {
    entries.push({ id, puzzle: game.puzzle.id, name: cleaned, score: game.score, date });
  }
  entries.sort((a, b) => b.score - a.score || a.date - b.date);
  const limited = entries.filter((entry, index) => entries.slice(0, index)
    .filter(previous => previous.puzzle === entry.puzzle).length < 50);
  storage.setItem(STORAGE_KEY, JSON.stringify(limited));
  return limited;
}
