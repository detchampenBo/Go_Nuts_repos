import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { harmony, disparity, loudest, alone, seat, planKey } from './symposium-model.mjs';

const d = JSON.parse(readFileSync(new URL('symposium-data.json', import.meta.url)));

test('harmony: one table is 0, and every evening matches the Python modularity', () => {
  assert.ok(Math.abs(harmony(d.edges, d.guests.map(() => 0)).q) < 1e-12);
  for (const run of d.unweighted) assert.ok(Math.abs(harmony(d.edges, run.part).q - run.q) < 6e-5);
  for (const run of d.null) assert.ok(Math.abs(harmony(run.edges, run.part).q - run.q) < 6e-5);
});

test('disparity: a node with one dominant link keeps it; a flat star keeps nothing', () => {
  // node 0 talks to 1 (w=9) and 2, 3 (w=1): p = 0.82, (1-p)^2 = 0.03 < 0.05
  const star = [[0, 1, 9], [0, 2, 1], [0, 3, 1]];
  assert.deepEqual(disparity(star, 4, 0.05), [true, false, false]);
  assert.deepEqual(disparity([[0, 1, 1], [0, 2, 1], [0, 3, 1]], 4, 0.05), [false, false, false]);
  assert.deepEqual(loudest(star, 1), [true, false, false]);
  assert.deepEqual(alone(star, [true, false, false], 4), [2, 3]);
});

test('seat: every guest gets a finite position; plan keys ignore labels', () => {
  for (const part of [d.guests.map(() => 0), d.guests.map((g, i) => i), d.unweighted[0].part, d.eraPlan]) {
    const { pos } = seat(part);
    assert.ok(pos.every(p => Number.isFinite(p.x) && Number.isFinite(p.y)));
  }
  assert.equal(planKey([5, 5, 2, 7]), planKey([0, 0, 1, 2]));
  assert.notEqual(planKey([0, 1, 1]), planKey([0, 0, 1]));
});

test('newcomer: joins the table all their picks sit at; sits alone with no picks', async () => {
  const { seatNewcomer, harmony } = await import('./symposium-model.mjs');
  const tri = [[0, 1, 1], [1, 2, 1], [0, 2, 1], [3, 4, 1], [4, 5, 1], [3, 5, 1]];
  assert.equal(seatNewcomer(tri, [0, 0, 0, 1, 1, 1], [3, 4]).table, 1);
  assert.equal(seatNewcomer(tri, [0, 0, 0, 1, 1, 1], []).table, null);
  // the chosen table really is the best: Q with the newcomer there beats every alternative
  const part = d.unweighted[0].part, picks = [18, 17, 19];
  const edges = [...d.edges, ...picks.map(p => [24, p, 1])];
  const best = seatNewcomer(d.edges, part, picks).table;
  const q = t => harmony(edges, [...part, t]).q;
  for (const t of [...new Set(part), 99]) assert.ok(q(best) >= q(t) - 1e-12);
});
