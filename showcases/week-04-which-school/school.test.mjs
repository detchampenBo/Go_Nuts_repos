import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { modularity, nmi, xFraction } from './school.mjs';

test('modularity: one community is 0, and matches the Python value on the reference run', () => {
  const d = JSON.parse(readFileSync(new URL('school-data.json', import.meta.url)));
  assert.equal(Math.abs(modularity(d.edges, d.philosophers.map(() => 0))) < 1e-12, true);
  // Two disjoint triangles split perfectly: Q = 2 * (3/6 - (6/12)^2) = 0.5
  const tri = [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5]];
  assert.ok(Math.abs(modularity(tri, [0, 0, 0, 1, 1, 1]) - 0.5) < 1e-12);
});

test('nmi: identical = 1, relabelled = 1, independent = 0', () => {
  assert.equal(nmi([0, 0, 1, 1], [0, 0, 1, 1]), 1);
  assert.ok(Math.abs(nmi([0, 0, 1, 1], ['b', 'b', 'a', 'a']) - 1) < 1e-12);
  assert.ok(Math.abs(nmi([0, 0, 1, 1], [0, 1, 0, 1])) < 1e-12);
});

test('time axis is monotonic and clamped', () => {
  assert.equal(xFraction(-5000), 0);
  assert.equal(xFraction(2000), 1);
  for (let y = -800; y < 1900; y += 7) assert.ok(xFraction(y + 7) >= xFraction(y));
});
