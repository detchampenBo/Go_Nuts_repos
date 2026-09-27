// Pure helpers for The Symposium, kept separate so symposium.test.mjs can check them.

// Modularity split into its two terms: Q = Σ l_c/m − Σ (d_c/2m)². Unweighted.
export function harmony(edges, part) {
  const m = edges.length, inside = new Map(), degree = new Map();
  const add = (map, k) => map.set(k, (map.get(k) || 0) + 1);
  for (const [a, b] of edges) {
    add(degree, part[a]); add(degree, part[b]);
    if (part[a] === part[b]) add(inside, part[a]);
  }
  let together = 0, expected = 0;
  for (const [c, d] of degree) { together += (inside.get(c) || 0) / m; expected += (d / (2 * m)) ** 2; }
  return { together, expected, q: together - expected };
}

export function degreeAndStrength(edges, n) {
  const degree = Array(n).fill(0), strength = Array(n).fill(0);
  for (const [a, b, w] of edges) { degree[a]++; degree[b]++; strength[a] += w; strength[b] += w; }
  return { degree, strength };
}

// Serrano, Boguñá & Vespignani 2009: keep a link if it is significant for either endpoint.
export function disparity(edges, n, alpha) {
  const { degree, strength } = degreeAndStrength(edges, n);
  const significant = (x, w) => degree[x] > 1 && (1 - w / strength[x]) ** (degree[x] - 1) < alpha;
  return edges.map(([a, b, w]) => significant(a, w) || significant(b, w));
}

// Global threshold with the same budget: the `count` loudest links (ties go to the earlier link).
export function loudest(edges, count) {
  const order = edges.map((e, i) => i).sort((i, j) => edges[j][2] - edges[i][2] || i - j);
  const keep = Array(edges.length).fill(false);
  order.slice(0, count).forEach(i => { keep[i] = true; });
  return keep;
}

export function alone(edges, keep, n) {
  const talks = Array(n).fill(false);
  edges.forEach(([a, b], i) => { if (keep[i]) talks[a] = talks[b] = true; });
  return talks.map((t, i) => t ? -1 : i).filter(i => i >= 0);
}

// Guest i's home is hour i on a clock of history (Socrates at noon, clockwise). A table sits at
// the mean home of its guests, so tables drift toward their era. Overlapping tables are pushed apart.
export function seat(part, box = { w: 640, h: 520 }) {
  const n = part.length, cx = box.w / 2, cy = box.h / 2;
  const home = i => { const a = -Math.PI / 2 + 2 * Math.PI * i / n; return [cx + Math.cos(a) * (box.w / 2 - 125), cy + Math.sin(a) * (box.h / 2 - 85)]; };
  const groups = new Map();
  part.forEach((c, i) => groups.set(c, [...(groups.get(c) || []), i]));
  const tables = [...groups.entries()].map(([id, members]) => ({
    id, members,
    x: members.reduce((s, i) => s + home(i)[0], 0) / members.length,
    y: members.reduce((s, i) => s + home(i)[1], 0) / members.length,
    r: 18 + 5.2 * members.length, // room for a portrait at every seat
  }));
  // Names sit beside a shared table, but radially outward from a table for one.
  const room = t => t.members.length > 1 ? 70 : 4;
  for (let pass = 0; pass < 120; pass++) {
    for (const a of tables) for (const b of tables) {
      if (a === b) continue;
      let dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy);
      const need = a.r + b.r + room(a) + room(b);
      if (d >= need) continue;
      if (d < 1e-6) { dx = Math.cos(a.id * 2.4 + b.id); dy = Math.sin(a.id * 2.4 + b.id); d = 1; }
      const push = (need - d) / 2;
      a.x -= dx / d * push; a.y -= dy / d * push; b.x += dx / d * push; b.y += dy / d * push;
    }
    for (const t of tables) {
      const side = t.members.length > 1 ? 104 : 40; // long names beside the outermost seats
      t.x = Math.max(t.r + side, Math.min(box.w - t.r - side, t.x));
      t.y = Math.max(t.r + 24, Math.min(box.h - t.r - 24, t.y));
    }
  }
  const pos = Array(n);
  for (const t of tables) t.members.forEach((g, k) => {
    const angle = t.members.length === 1 ? Math.atan2(t.y - cy, t.x - cx) : -Math.PI / 2 + (2 * Math.PI * k) / t.members.length;
    pos[g] = { x: t.x + Math.cos(angle) * t.r, y: t.y + Math.sin(angle) * t.r, angle, table: t.id };
  });
  return { pos, tables: tables.sort((a, b) => Math.min(...a.members) - Math.min(...b.members)) };
}

// Same seating, any labels: a canonical key for "is this the same plan?".
export const planKey = part => {
  const first = new Map();
  return part.map(c => first.has(c) ? first.get(c) : (first.set(c, first.size), first.size - 1)).join('.');
};

// A newcomer linked to `picks` joins the table with the largest modularity gain, or sits alone
// if no table gains (one move of Louvain's first phase): ΔQ_C = k_in/m − Σtot_C·k/(2m²), m and Σtot
// counting the newcomer's own links.
export function seatNewcomer(edges, part, picks) {
  const k = picks.length, m = edges.length + k;
  const tot = new Map(), inC = new Map();
  const add = (map, c, v) => map.set(c, (map.get(c) || 0) + v);
  for (const [a, b] of edges) { add(tot, part[a], 1); add(tot, part[b], 1); }
  for (const p of picks) { add(tot, part[p], 1); add(inC, part[p], 1); }
  const gains = [...tot.keys()].map(c => ({ table:c, gain:(inC.get(c) || 0) / m - tot.get(c) * k / (2 * m * m) }))
    .sort((x, y) => y.gain - x.gain);
  return { table:k && gains[0].gain > 1e-12 ? gains[0].table : null, gains };
}
