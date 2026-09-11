// Pure helpers for the friendship-paradox explorable. No DOM, no fetch.

/** How many neighbour dots the ego diagram draws before it starts summarising. */
export const NEIGHBOUR_CAP = 44;

/**
 * Split a hero's neighbours into the ones the diagram will draw and a count of
 * the rest. Neighbours arrive already sorted by descending degree.
 */
export function neighbourSample(hero, cap = NEIGHBOUR_CAP) {
  const shown = hero.neighbors.slice(0, cap);
  return { shown, hidden: hero.neighbors.length - shown.length };
}

/**
 * "isolated" - no connections at all
 * "top"      - NOT ONE friend is more connected. This is strictly stronger than
 *              having a low neighbour mean, so it reads the precomputed
 *              `topOfCircle` flag rather than comparing averages: a hero can
 *              average below their own degree while still having a hub friend.
 * "paradox"  - the friends' mean degree beats this hero's own degree
 * "below"    - the friends' mean is lower, but at least one friend still outranks them
 * "even"     - the friends' mean exactly equals this hero's degree
 */
export function verdict(hero) {
  if (hero.degree === 0) return "isolated";
  if (hero.topOfCircle) return "top";
  if (hero.neighborMean > hero.degree) return "paradox";
  if (hero.neighborMean < hero.degree) return "below";
  return "even";
}

/** Gap between a hero's degree and their friends' mean degree, signed. */
export function friendGap(hero) {
  return hero.neighborMean - hero.degree;
}

/**
 * The friendship-paradox identity: the degree of a node found by following a
 * random edge is <k> + variance / <k>. Returns the three pieces plus the
 * residual, which should be ~0 for consistent data.
 */
export function excessDecomposition(network) {
  const predicted = network.meanDegree + network.variance / network.meanDegree;
  return {
    mean: network.meanDegree,
    excess: network.variance / network.meanDegree,
    friend: network.friendMeanDegree,
    residual: network.friendMeanDegree - predicted,
  };
}

/** Hero id whose friends beat them by the widest margin (the sharpest demo). */
export function sharpestParadox(heroes) {
  let best = null;
  let bestGap = -Infinity;
  for (const [id, hero] of Object.entries(heroes)) {
    if (hero.degree === 0) continue;
    const gap = friendGap(hero);
    if (gap > bestGap) {
      bestGap = gap;
      best = id;
    }
  }
  return best;
}

/**
 * Case-insensitive search over hero display names, then ids. Prefix name
 * matches rank first, then name substrings, then id substrings (so "47"
 * finds "Node 47" in the model networks).
 */
export function matchHeroes(heroes, query, limit = 8) {
  const needle = query.trim().toLowerCase();
  if (!needle) return [];
  const scored = [];
  for (const [id, hero] of Object.entries(heroes)) {
    const name = hero.name.toLowerCase();
    const at = name.indexOf(needle);
    let rank = at === 0 ? 0 : at > 0 ? 1 : id.toLowerCase().includes(needle) ? 2 : -1;
    if (rank === -1) continue;
    scored.push({ id, hero, rank, name });
  }
  scored.sort((a, b) => a.rank - b.rank || a.name.localeCompare(b.name, undefined, { numeric: true }));
  return scored.slice(0, limit).map(({ id, hero }) => ({ id, hero }));
}

/** Round up to a friendly axis bound (multiple of step, at least step). */
export function niceCeil(value, step = 20) {
  return Math.max(step, Math.ceil(value / step) * step);
}

/** Fixed positions for the ego diagram: focal node centred, neighbours on a ring. */
export function egoLayout(count, size = 320) {
  const centre = size / 2;
  const radius = count > 26 ? centre - 30 : centre - 54;
  return Array.from({ length: count }, (_, i) => {
    const angle = (i * Math.PI * 2) / Math.max(count, 1) - Math.PI / 2;
    return [centre + Math.cos(angle) * radius, centre + Math.sin(angle) * radius];
  });
}

/** Radius for a neighbour dot, scaled by that neighbour's degree. */
export function dotRadius(degree, maxDegree) {
  const t = maxDegree > 0 ? degree / maxDegree : 0;
  return 3 + Math.sqrt(t) * 9;
}

/** Actual higher-degree neighbors, closest degree first; peaks fall back to their top neighbor. */
export function comparisonNeighbors(focal, heroes) {
  const higher = focal.neighbors.filter(id => heroes[id].degree > focal.degree);
  const byDegree = (a, b) => heroes[a].degree - heroes[b].degree || a.localeCompare(b);
  if (higher.length) return higher.sort(byDegree);
  return [...focal.neighbors].sort((a, b) => -byDegree(a, b)).slice(0, 1);
}
