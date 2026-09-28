// Pure helpers for the Which School? page, kept separate so school.test.mjs can check them.

// Piecewise time axis: stretched where philosophers are dense (the 1700s–1800s).
const YEARS = [-800, -400, 0, 500, 1000, 1300, 1500, 1600, 1700, 1800, 1900];
const FRACS = [0, 0.09, 0.16, 0.24, 0.32, 0.4, 0.48, 0.57, 0.67, 0.82, 1];
export function xFraction(year) {
  const y = Math.max(YEARS[0], Math.min(YEARS.at(-1), year));
  let i = 1;
  while (i < YEARS.length - 1 && y > YEARS[i]) i++;
  return FRACS[i - 1] + ((y - YEARS[i - 1]) / (YEARS[i] - YEARS[i - 1])) * (FRACS[i] - FRACS[i - 1]);
}

// Vertical position inside a lane, in half-lane units (-1 top … 1 bottom).
// Loyal philosophers sit on the centre line; the less loyal, the further they lean
// toward their second school. A philosopher shown outside their usual school sits
// on the edge facing home.
export function laneOffset(p, lane) {
  const clamp = (v) => Math.max(-0.92, Math.min(0.92, v));
  if (lane !== p.home) return clamp(Math.sign(p.home - lane) * 0.62 + p.j * 0.25);
  return clamp(Math.sign(p.rival - p.home) * (1 - p.loyalty) * 1.4 + p.j * 0.28);
}

// Q = Σ_c [ l_c/m − (d_c/2m)² ] on an unweighted edge list [[a, b, w], …].
export function modularity(edges, part) {
  const m = edges.length;
  const inside = new Map(), degree = new Map();
  const add = (map, k, v) => map.set(k, (map.get(k) || 0) + v);
  for (const [a, b] of edges) {
    add(degree, part[a], 1);
    add(degree, part[b], 1);
    if (part[a] === part[b]) add(inside, part[a], 1);
  }
  let q = 0;
  for (const [c, dc] of degree) q += (inside.get(c) || 0) / m - (dc / (2 * m)) ** 2;
  return q;
}

// Normalized mutual information, arithmetic normalization (sklearn's default).
export function nmi(a, b) {
  const n = a.length;
  const count = (xs) => xs.reduce((m, x) => m.set(x, (m.get(x) || 0) + 1), new Map());
  const ca = count(a), cb = count(b), joint = new Map();
  a.forEach((x, i) => {
    const key = `${x}\u0000${b[i]}`;
    const cell = joint.get(key) || { x, y: b[i], v: 0 };
    cell.v++;
    joint.set(key, cell);
  });
  let mi = 0;
  for (const { x, y, v } of joint.values()) mi += (v / n) * Math.log((v * n) / (ca.get(x) * cb.get(y)));
  const h = (c) => -[...c.values()].reduce((s, v) => s + (v / n) * Math.log(v / n), 0);
  const denom = (h(ca) + h(cb)) / 2;
  return denom ? mi / denom : 1;
}

export function verdict(loyalty) {
  if (loyalty === 1) return 'Unanimous';
  if (loyalty >= 0.8) return 'Settled, mostly';
  if (loyalty >= 0.6) return 'Split decision';
  return 'Hung jury';
}
