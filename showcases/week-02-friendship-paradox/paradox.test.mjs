import { test } from "node:test";
import assert from "node:assert/strict";
import {
  neighbourSample,
  verdict,
  friendGap,
  excessDecomposition,
  sharpestParadox,
  matchHeroes,
  egoLayout,
  dotRadius,
  niceCeil,
} from "./paradox.mjs";

const heroes = {
  a: { name: "Ant-Man", degree: 2, neighborMean: 40, neighbors: ["b", "c"], paradox: true, biggerFriends: 2, topOfCircle: false },
  b: { name: "Big Hub", degree: 60, neighborMean: 8, neighbors: ["a", "c"], paradox: false, biggerFriends: 0, topOfCircle: true },
  c: { name: "Cat", degree: 3, neighborMean: 3, neighbors: ["a", "b", "d"], paradox: false, biggerFriends: 1, topOfCircle: false },
  d: { name: "Drifter", degree: 0, neighborMean: 0, neighbors: [], paradox: false, biggerFriends: 0, topOfCircle: false },
};

test("neighbourSample splits shown from hidden at the cap", () => {
  const hero = { neighbors: Array.from({ length: 50 }, (_, i) => `n${i}`) };
  const { shown, hidden } = neighbourSample(hero, 44);
  assert.equal(shown.length, 44);
  assert.equal(hidden, 6);
});

test("neighbourSample reports no hidden neighbours below the cap", () => {
  assert.deepEqual(neighbourSample({ neighbors: ["x", "y"] }, 44), { shown: ["x", "y"], hidden: 0 });
});

test("verdict classifies the five cases", () => {
  assert.equal(verdict(heroes.a), "paradox");
  assert.equal(verdict(heroes.b), "top");
  assert.equal(verdict(heroes.c), "even");
  assert.equal(verdict(heroes.d), "isolated");
});

test("verdict never claims 'top' when a single friend still outranks the hero", () => {
  // The real Betsy Braddock: 28 connections, friends average 25.07 (lower than
  // her own), yet six friends outrank her — Spider-Man among them at 106.
  const betsy = {
    name: "Betsy Braddock",
    degree: 28,
    neighborMean: 25.07,
    neighbors: [],
    paradox: false,
    biggerFriends: 6,
    topOfCircle: false,
  };
  assert.equal(verdict(betsy), "below");
  assert.notEqual(verdict(betsy), "top");
});

test("verdict reserves 'top' for heroes with zero bigger friends", () => {
  const peak = { degree: 40, neighborMean: 12, neighbors: [], biggerFriends: 0, topOfCircle: true };
  assert.equal(verdict(peak), "top");
});

test("friendGap is signed", () => {
  assert.equal(friendGap(heroes.a), 38);
  assert.equal(friendGap(heroes.b), -52);
});

test("excessDecomposition reproduces the friend mean from <k> and variance", () => {
  const network = { meanDegree: 10, variance: 120, friendMeanDegree: 22 };
  const parts = excessDecomposition(network);
  assert.equal(parts.mean, 10);
  assert.equal(parts.excess, 12);
  assert.equal(parts.friend, 22);
  assert.ok(Math.abs(parts.residual) < 1e-9);
});

test("sharpestParadox picks the widest positive gap and ignores isolates", () => {
  assert.equal(sharpestParadox(heroes), "a");
});

test("matchHeroes ranks prefix matches ahead of substring matches", () => {
  const hits = matchHeroes(heroes, "a");
  // "Ant-Man" starts with the query (rank 0); "Cat" contains it (rank 1).
  assert.deepEqual(hits.map((h) => h.id), ["a", "c"]);
});

test("matchHeroes returns nothing for an empty query", () => {
  assert.deepEqual(matchHeroes(heroes, "   "), []);
});

test("matchHeroes falls back to ids, so a bare number finds a model node", () => {
  const nodes = { 47: { name: "Node 48", degree: 3 }, 3: { name: "Node 4", degree: 1 } };
  assert.deepEqual(matchHeroes(nodes, "47").map((h) => h.id), ["47"]);
});

test("matchHeroes orders numbered names naturally", () => {
  const nodes = {
    1: { name: "Node 2", degree: 1 },
    9: { name: "Node 10", degree: 1 },
    2: { name: "Node 3", degree: 1 },
  };
  assert.deepEqual(matchHeroes(nodes, "node").map((h) => h.hero.name), ["Node 2", "Node 3", "Node 10"]);
});

test("niceCeil rounds up to the step and never returns zero", () => {
  assert.equal(niceCeil(106, 20), 120);
  assert.equal(niceCeil(120, 20), 120);
  assert.equal(niceCeil(0, 20), 20);
});

test("egoLayout centres the ring and returns one point per neighbour", () => {
  const points = egoLayout(4, 320);
  assert.equal(points.length, 4);
  const [x, y] = points[0];
  assert.ok(Math.abs(x - 160) < 1e-6);
  assert.ok(y < 160);
});

test("dotRadius grows with degree and never collapses to zero", () => {
  assert.ok(dotRadius(0, 100) >= 3);
  assert.ok(dotRadius(100, 100) > dotRadius(25, 100));
});


test("comparison examples explore smaller qualifying neighbors before the biggest hub", async () => {
  const { comparisonNeighbors } = await import("./paradox.mjs");
  const nodes = { hub: {degree: 106}, near: {degree: 12}, low: {degree: 3}, middle: {degree: 25} };
  assert.deepEqual(comparisonNeighbors({degree: 10, neighbors: ['hub','low','middle','near']}, nodes), ['near','middle','hub']);
  assert.deepEqual(comparisonNeighbors({degree: 110, neighbors: ['hub','near']}, nodes), ['hub']);
  assert.deepEqual(comparisonNeighbors({degree: 0, neighbors: []}, nodes), []);
});
