import {
  NEIGHBOUR_CAP,
  comparisonNeighbors,
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

const $ = (selector) => document.querySelector(selector);
const esc = (value) =>
  String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const one = (value) => value.toFixed(1);
const pct = (value) => `${Math.round(value * 100)}%`;
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

let data;
let netKey = "marvel";
let selectedId = null;
let neighborIndex = 0;
let searchActive = -1;
let matches = [];
let axisMax = 120;
let networkOpen = false;

const network = () => data.networks[netKey];
const hero = (id) => network().heroes[id];

/* ---------------------------------------------------------------- scatter */

// One fixed scale across all three networks, so switching makes the cloud
// visibly collapse toward the line rather than silently rescaling. Both axes
// are square-root scaled: most heroes have a small degree, and a linear axis
// would crush them into the left edge. The same transform on both axes keeps
// the y = x diagonal a straight line.
const PLOT = { x0: 62, x1: 878, y0: 26, y1: 496 };
const TICKS = [0, 5, 10, 20, 40, 60, 80, 100, 120];
const unit = (v) => Math.sqrt(Math.max(0, v) / axisMax);
const sx = (v) => PLOT.x0 + unit(v) * (PLOT.x1 - PLOT.x0);
const sy = (v) => PLOT.y1 - unit(v) * (PLOT.y1 - PLOT.y0);

const NET_NOTE = {
  marvel: "The real network. A handful of hubs dominate, and almost every hero sits far above the line.",
  scalefree: "Growth plus preferential attachment builds the same hub structure — and reproduces the same lift.",
  random:
    "Same nodes, same number of connections, no hubs. A clear majority still sit above the line, but the " +
    "surplus collapses from +12.6 connections to +0.9. The paradox weakens; it does not vanish.",
};

/* ------------------------------------------------------------ whole graph */

const GRAPH_SIZE = 560;
const gx = (p) => 18 + p[0] * (GRAPH_SIZE - 36);
const gy = (p) => 18 + p[1] * (GRAPH_SIZE - 36);

function graphSvg() {
  const net = network();
  const entries = Object.entries(net.heroes);
  const focal = hero(selectedId);
  const focalFriends = new Set(focal ? focal.neighbors : []);

  // Deduplicate undirected edges, and draw the selected hero's own links last
  // so they sit on top of the hairball.
  const plain = [];
  const highlighted = [];
  for (const [id, h] of entries) {
    for (const other of h.neighbors) {
      if (id >= other) continue;
      const line = [h.pos, net.heroes[other].pos];
      if (id === selectedId || other === selectedId) highlighted.push(line);
      else plain.push(line);
    }
  }
  const drawEdges = (list, cls) =>
    list
      .map(([a, b]) => `<line class="${cls}" x1="${gx(a).toFixed(1)}" y1="${gy(a).toFixed(1)}" x2="${gx(b).toFixed(1)}" y2="${gy(b).toFixed(1)}"/>`)
      .join("");

  const maxDegree = Math.max(net.maxDegree, 1);
  const nodes = entries
    .sort((a, b) => (a[0] === selectedId ? 1 : 0) - (b[0] === selectedId ? 1 : 0))
    .map(([id, h]) => {
      const selected = id === selectedId;
      const r = selected ? 9 : 2.4 + Math.sqrt(h.degree / maxDegree) * 10;
      const cls = selected
        ? "gnode sel"
        : h.degree === 0
        ? "gnode iso"
        : focalFriends.has(id)
        ? "gnode friend"
        : "gnode";
      return `<circle class="${cls}" data-id="${esc(id)}" cx="${gx(h.pos).toFixed(1)}" cy="${gy(h.pos).toFixed(1)}" r="${r.toFixed(1)}"><title>${esc(h.name)} · ${h.degree} connections</title></circle>`;
    })
    .join("");

  return `<svg class="graph" viewBox="0 0 ${GRAPH_SIZE} ${GRAPH_SIZE}" role="img"
    aria-label="Force-directed drawing of the whole ${net.label} network: ${net.nodes} nodes and ${net.edges.toLocaleString()} connections. Each circle is sized by its number of connections, so hubs appear as the largest circles. ${esc(focal.name)} is highlighted in red together with its ${focal.degree} direct connections.">
    <g class="edges">${drawEdges(plain, "gedge")}</g>
    <g class="edges-hi">${drawEdges(highlighted, "gedge-hi")}</g>
    <g class="gnodes">${nodes}</g>
  </svg>`;
}

function scatterSvg() {
  const net = network();
  const focal = hero(selectedId);
  const ticks = TICKS.filter((t) => t <= axisMax);

  const grid = ticks
    .map(
      (t) => `<line class="grid" x1="${sx(t)}" y1="${sy(0)}" x2="${sx(t)}" y2="${sy(axisMax)}"/>
        <line class="grid" x1="${sx(0)}" y1="${sy(t)}" x2="${sx(axisMax)}" y2="${sy(t)}"/>
        <text class="tick" x="${sx(t)}" y="${sy(0) + 21}" text-anchor="middle">${t}</text>
        <text class="tick" x="${sx(0) - 11}" y="${sy(t) + 4}" text-anchor="end">${t}</text>`
    )
    .join("");

  const guides = focal && focal.degree
    ? `<line class="guide" x1="${sx(focal.degree)}" y1="${sy(focal.neighborMean)}" x2="${sx(focal.degree)}" y2="${sy(0)}"/>
       <line class="guide" x1="${sx(0)}" y1="${sy(focal.neighborMean)}" x2="${sx(focal.degree)}" y2="${sy(focal.neighborMean)}"/>`
    : "";

  const dots = Object.entries(net.heroes)
    .filter(([, h]) => h.degree > 0)
    .sort((a, b) => (a[0] === selectedId ? 1 : 0) - (b[0] === selectedId ? 1 : 0))
    .map(([id, h]) => {
      const cx = sx(h.degree);
      const cy = sy(h.neighborMean);
      const selected = id === selectedId;
      const lift = (sy(h.degree) - cy).toFixed(1); // start life on the diagonal
      return `<circle class="dot ${h.neighborMean > h.degree ? "up" : "down"}${selected ? " sel" : ""}"
        data-id="${esc(id)}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${selected ? 8 : 3.6}"
        style="transform:translateY(${lift}px)"
        ><title>${esc(h.name)} · ${h.degree} connections · friends average ${one(h.neighborMean)}</title></circle>`;
    })
    .join("");

  return `<svg class="scatter" viewBox="0 0 900 542" role="img"
    aria-label="Each of the ${net.connectedCount} connected heroes is one dot: horizontal position is their own number of connections, vertical position is the mean connections of their friends. ${pct(net.paradoxFraction)} of them sit above the diagonal line, meaning their friends are on average better connected than they are.">
    <polygon class="paradox-zone" points="${sx(0)},${sy(0)} ${sx(axisMax)},${sy(axisMax)} ${sx(0)},${sy(axisMax)}"/>
    ${grid}
    <line class="diagonal" x1="${sx(0)}" y1="${sy(0)}" x2="${sx(axisMax)}" y2="${sy(axisMax)}"/>
    <text class="zone-label" x="${sx(axisMax * 0.13)}" y="${sy(axisMax * 0.74)}">friends are more connected</text>
    <line class="mean-line" x1="${sx(net.meanDegree)}" y1="${sy(0)}" x2="${sx(net.meanDegree)}" y2="${sy(axisMax)}"/>
    <line class="friend-line" x1="${sx(0)}" y1="${sy(net.neighborMeanAverage)}" x2="${sx(axisMax)}" y2="${sy(net.neighborMeanAverage)}"/>
    <text class="friend-label" x="${sx(axisMax) - 6}" y="${sy(net.neighborMeanAverage) - 7}" text-anchor="end">average of these dots: ${one(net.neighborMeanAverage)}</text>
    <text class="mean-label" x="${sx(net.meanDegree) + 7}" y="${sy(axisMax) + 15}">all-node mean: ${one(net.meanDegree)}</text>
    ${guides}
    <g class="dots">${dots}</g>
    <text class="axis-title" x="${(PLOT.x0 + PLOT.x1) / 2}" y="538" text-anchor="middle">Your own connections →</text>
    <text class="axis-title" x="16" y="${(PLOT.y0 + PLOT.y1) / 2}" text-anchor="middle"
      transform="rotate(-90 16 ${(PLOT.y0 + PLOT.y1) / 2})">Your friends' average →</text>
  </svg>`;
}

function vizPanel() {
  const net = network();
  const focal = hero(selectedId);
  return `
    <section class="viz">
      <div class="viz-head">
        <div>
          <p class="eyebrow">EVERY CONNECTED HERO, ONE DOT</p>
          <h2>${pct(net.paradoxFraction)} of them land above the line.</h2>
          <p class="viz-sub">Above the line means: your friends have more connections than you do.
            Tap any dot to inspect that hero.</p>
        </div>
        <p class="net-note">${NET_NOTE[netKey]}</p>
      </div>
      <div class="viz-row">
        <figure class="viz-cell">
          <figcaption><strong>Every hero, one dot.</strong> Across: your own connections. Up: your friends' average.
            The diagonal is "exactly equal".</figcaption>
          <div class="scatter-wrap">${scatterSvg()}</div>
          <p class="cell-note">Square-root axes, identical on both, so the diagonal stays straight and the
            many low-degree heroes stay readable. The vertical reference line averages all ${net.nodes} nodes${net.isolates ? `, including ${net.isolates} isolates` : ""}; the dots and their horizontal average exclude isolates.</p>
        </figure>
        <details class="network-detail" ${networkOpen ? "open" : ""}>
          <summary>Explore the full network · ${net.nodes} nodes, ${net.edges.toLocaleString()} connections</summary>
        <figure class="viz-cell">
          <figcaption><strong>The network itself.</strong> Every node, every connection, sized by degree.
            ${netKey === "random" ? "Evenly textured — no node dominates." : "The big circles are the hubs."}</figcaption>
          <div class="graph-wrap">${graphSvg()}</div>
          <p class="cell-note">${esc(focal.name)} is red; its ${focal.degree} direct connection${focal.degree === 1 ? "" : "s"}
            ${focal.degree === 1 ? "is" : "are"} highlighted.${net.isolates ? ` The row along the bottom is the ${net.isolates} heroes with no connections at all.` : ""}</p>
        </figure>
        </details>
      </div>
      <p class="scatter-legend">
        <span class="key key--up">above the line (${net.paradoxCount})</span>
        <span class="key key--down">on or below (${net.connectedCount - net.paradoxCount})</span>
        <span class="key key--sel">selected: ${esc(focal.name)}</span>

      </p>
    </section>`;
}

/* --------------------------------------------------------------- ego view */

function egoSvg(id) {
  const focal = hero(id);
  const size = 300;
  const centre = size / 2;
  const { shown, hidden } = neighbourSample(focal, NEIGHBOUR_CAP);
  const maxDegree = Math.max(focal.degree, ...shown.map((n) => hero(n).degree), 1);
  const points = egoLayout(shown.length, size);
  const links = points
    .map(([x, y]) => `<line x1="${centre}" y1="${centre}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="ego-link"/>`)
    .join("");
  const dots = shown
    .map((nid, i) => {
      const nb = hero(nid);
      const [x, y] = points[i];
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${dotRadius(nb.degree, maxDegree).toFixed(1)}"
        class="ego-dot ${nb.degree > focal.degree ? "is-bigger" : "is-smaller"}"><title>${esc(nb.name)} · ${nb.degree} connections</title></circle>`;
    })
    .join("");
  const biggerCount = shown.filter((n) => hero(n).degree > focal.degree).length;
  return `
    <svg class="ego-graph" viewBox="0 0 ${size} ${size}" role="img"
      aria-label="${esc(focal.name)} at the centre with ${focal.degree} connections. Of the ${shown.length} friends drawn, ${biggerCount} have more connections.">
      <circle cx="${centre}" cy="${centre}" r="${centre - 6}" class="ego-field"/>
      ${links}${dots}
      <circle cx="${centre}" cy="${centre}" r="${Math.max(8, dotRadius(focal.degree, maxDegree)).toFixed(1)}" class="ego-focal"/>
    </svg>
    ${hidden > 0 ? `<p class="ego-more">Showing the ${shown.length} highest-degree neighbors; ${hidden} lower-ranked neighbors are not drawn. The average uses all ${focal.degree} neighbors.</p>` : ""}`;
}

const VERDICT_COPY = {
  paradox: (h) =>
    `Paradox holds — ${esc(h.name)}'s friends average ${one(h.neighborMean)} connections, ${one(friendGap(h))} more than ${esc(h.name)}.`,
  top: (h) =>
    `Top of the circle — not one of ${esc(h.name)}'s ${h.degree} friends is more connected. Only a handful of heroes can say that.`,
  below: (h) =>
    `Friends average ${one(h.neighborMean)} connections, ${one(-friendGap(h))} fewer than ${esc(h.name)}. But the average hides the tail: ` +
    `${h.biggerFriends} of ${esc(h.name)}'s friends still outrank them.`,
  even: (h) => `A rare tie — ${esc(h.name)}'s friends average exactly ${one(h.neighborMean)} connections.`,
  isolated: (h) => `${esc(h.name)} has no connections in this snapshot, so there are no friends to compare against.`,
};

function neighborCard(id) {
  const focal = hero(id);
  const candidates = comparisonNeighbors(focal, network().heroes);
  const neighborId = candidates[neighborIndex % candidates.length] ?? null;
  if (neighborId === null) return `<div class="neighbor-card"><p>No neighbors in this snapshot.</p></div>`;
  const neighbor = hero(neighborId);
  const higher = neighbor.degree > focal.degree;
  return `<div class="neighbor-card">
    <p class="eyebrow">${higher ? "MEET A MORE-CONNECTED NEIGHBOR" : "THEIR MOST-CONNECTED NEIGHBOR"}</p>
    <p aria-live="polite"><strong>${esc(focal.name)}</strong> has ${focal.degree} connections.
      Their neighbor <strong>${esc(neighbor.name)}</strong> has ${neighbor.degree}.</p>
    ${higher ? "" : '<p class="muted">None of their neighbors has more connections than they do.</p>'}
    <button class="neighbor-button" data-neighbor="${esc(neighborId)}">Explore ${esc(neighbor.name)} <span aria-hidden="true">→</span></button>
    ${higher ? `<p class="neighbor-note">Example ${neighborIndex % candidates.length + 1} of ${candidates.length} more-connected neighbors · ordered by degree, closest first.</p>` : ""}
    ${candidates.length > 1 ? '<button class="chip" data-another-neighbor>Show another neighbor ↻</button>' : ""}
    <p class="neighbor-note">One neighbor is an example. The friends’ average above determines whether the paradox holds for this hero.</p>
  </div>`;
}

function egoPanel(id) {
  const focal = hero(id);
  const v = verdict(focal);
  return `
    <section class="ego-panel">
      <div class="picker">
        <label for="hero-search">Find a hero</label>
        <div class="picker-field">
          <input id="hero-search" type="text" autocomplete="off" spellcheck="false"
            role="combobox" aria-expanded="false" aria-controls="hero-results" aria-autocomplete="list"
            placeholder="${netKey === "marvel" ? "Search by name…" : "Search by number, e.g. 47…"}" value=""/>
          <ul id="hero-results" role="listbox" aria-label="Matching heroes" hidden></ul>
        </div>
        <div class="example-chips">
          <button class="chip" data-pick="sharp">Sharpest paradox</button>
          <button class="chip" data-pick="hub">Biggest hub</button>
          <button class="chip" data-pick="top">Top of their circle</button>
        </div>
      </div>
      <h3 class="ego-name">${esc(focal.name)}</h3>
      <figure class="ego">${egoSvg(id)}</figure>
      <div class="you-vs-friends">
        <div class="stat"><strong>${focal.degree}</strong><span>own connections</span></div>
        <div class="versus" aria-hidden="true">vs</div>
        <div class="stat stat--accent"><strong>${focal.degree ? one(focal.neighborMean) : "—"}</strong><span>friends' average</span></div>
      </div>
      <p class="verdict verdict--${v}" role="status">${VERDICT_COPY[v](focal)}</p>
      ${neighborCard(id)}
    </section>`;
}

/* -------------------------------------------------------- aggregate panel */

function aggregatePanel() {
  const net = network();
  const parts = excessDecomposition(net);
  const top = net.topOfCircle.slice(0, 5).map((t) => esc(t.name)).join(", ");
  const extra = net.topOfCircle.length > 5 ? `, and ${net.topOfCircle.length - 5} more` : "";
  return `
    <aside class="aggregate-panel">
      <p class="eyebrow">WHY IT HAPPENS</p>
      <h3>The counting identity</h3>
      <div class="identity">
        <div class="identity-row"><span>Pick a <em>hero</em> at random</span><strong>${one(parts.mean)}</strong></div>
        <div class="identity-row identity-row--accent"><span>Pick a <em>connection</em> at random, look at one end</span><strong>${one(parts.friend)}</strong></div>
      </div>
      <p class="formula">⟨k⟩ + σ²/⟨k⟩ &nbsp;=&nbsp; ${one(parts.mean)} + ${one(parts.excess)} &nbsp;=&nbsp; ${one(parts.friend)}</p>
      <p class="muted">The surplus is the degree variance divided by the mean. Sampling a connection rather than
        a hero is what biases you toward hubs: a hero with ${net.maxDegree} links has ${net.maxDegree} chances to be
        picked, a hero with one link has one.</p>
      <p class="muted">Averaging the scatter's dots instead — one value per hero — gives
        <strong>${one(net.neighborMeanAverage)}</strong>. Close, but a different question: that samples heroes
        uniformly, then averages within each circle.</p>

      <h3>Top of their circle</h3>
      <p>${net.topOfCircle.length
        ? `${net.topOfCircle.length} hero${net.topOfCircle.length === 1 ? "" : "es"} here ${net.topOfCircle.length === 1 ? "has" : "have"} no friend more connected than themselves: ${top}${extra}.`
        : "Nobody here escapes it — every connected hero has at least one friend who outranks them."}</p>
      <p class="muted">This is the strict test: not one friend outranks them. A hero can still have a
        below-average circle while a single hub friend towers over them.</p>

      <dl class="net-facts">
        <div><dt>Nodes</dt><dd>${net.nodes}</dd></div>
        <div><dt>Connections</dt><dd>${net.edges.toLocaleString()}</dd></div>
        <div><dt>Largest degree</dt><dd>${net.maxDegree}</dd></div>
        <div><dt>Degree variance</dt><dd>${one(net.variance)}</dd></div>
      </dl>
    </aside>`;
}

/* ---------------------------------------------------------------- plumbing */

function pickId(kind) {
  const heroes = network().heroes;
  if (kind === "hub") {
    return Object.entries(heroes).reduce(
      (best, [id, h]) => (h.degree > heroes[best].degree ? id : best),
      Object.keys(heroes)[0]
    );
  }
  if (kind === "top") return network().topOfCircle[0]?.id ?? network().suggested;
  return sharpestParadox(heroes) ?? network().suggested;
}

function playRise() {
  const group = $(".scatter .dots");
  if (!group) return;
  const clear = () => group.querySelectorAll("circle").forEach((c) => (c.style.transform = ""));
  if (reducedMotion()) {
    clear();
    return;
  }
  requestAnimationFrame(() => requestAnimationFrame(clear));
}

// `animate` is only for entering a network, not for every hero click — replaying
// the drop on each selection turns a nice reveal into a twitch.
function render(animate = false) {
  document.querySelectorAll(".net-option").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.net === netKey));
  });
  $("#explorer").innerHTML = `${vizPanel()}<div class="explorer-grid">${egoPanel(selectedId)}${aggregatePanel()}</div>`;
  if (animate) playRise();
  else $(".scatter .dots")?.querySelectorAll("circle").forEach((c) => (c.style.transform = ""));
}

function selectHero(id, focusInput = false) {
  if (!hero(id)) return;
  selectedId = id;
  neighborIndex = 0;
  searchActive = -1;
  matches = [];
  render();
  if (focusInput) $("#hero-search")?.focus();
}

function switchNetwork(key) {
  if (!data.networks[key] || key === netKey) return;
  netKey = key;
  neighborIndex = 0;
  if (!hero(selectedId)) selectedId = network().suggested;
  searchActive = -1;
  matches = [];
  render(true);
}

function hideResults() {
  const list = $("#hero-results");
  const input = $("#hero-search");
  if (list) list.hidden = true;
  if (input) {
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  }
}

function renderResults() {
  const list = $("#hero-results");
  const input = $("#hero-search");
  if (!list || !input) return;
  if (!matches.length) {
    hideResults();
    return;
  }
  list.innerHTML = matches
    .map(
      ({ id, hero: h }, i) =>
        `<li id="hero-opt-${i}" role="option" data-id="${esc(id)}" aria-selected="${i === searchActive}" class="${i === searchActive ? "active" : ""}"><span>${esc(h.name)}</span><span class="opt-degree">${h.degree}</span></li>`
    )
    .join("");
  list.hidden = false;
  input.setAttribute("aria-expanded", "true");
  if (searchActive >= 0) input.setAttribute("aria-activedescendant", `hero-opt-${searchActive}`);
  else input.removeAttribute("aria-activedescendant");
}

function computeMatches(value) {
  matches = matchHeroes(network().heroes, value, 8);
  renderResults();
}

// #explorer's contents are rebuilt on every render, so every listener that
// touches them is delegated from the container, which persists.
const explorer = $("#explorer");
explorer.addEventListener("toggle", event => {
  if (event.target.matches(".network-detail")) {
    networkOpen = event.target.open;
  }
}, true);

explorer.addEventListener("click", (event) => {
  if (event.target.closest("[data-another-neighbor]")) {
    neighborIndex++;
    $(".neighbor-card").outerHTML = neighborCard(selectedId);
    $("[data-another-neighbor]")?.focus({ preventScroll: true });
    return;
  }
  const neighbor = event.target.closest("[data-neighbor]");
  if (neighbor) {
    selectHero(neighbor.dataset.neighbor);
    const heading = $(".ego-name");
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
    return;
  }
  const chip = event.target.closest("[data-pick]");
  if (chip) {
    selectHero(pickId(chip.dataset.pick));
    return;
  }
  const dot = event.target.closest(".scatter circle[data-id], .graph circle[data-id]");
  if (dot) selectHero(dot.dataset.id);
});

explorer.addEventListener("input", (event) => {
  if (event.target.id !== "hero-search") return;
  searchActive = -1;
  computeMatches(event.target.value);
});

explorer.addEventListener("focusin", (event) => {
  if (event.target.id !== "hero-search") return;
  searchActive = -1;
  computeMatches(event.target.value);
});

explorer.addEventListener("focusout", (event) => {
  if (event.target.id !== "hero-search") return;
  setTimeout(hideResults, 120);
});

explorer.addEventListener("keydown", (event) => {
  if (event.target.id !== "hero-search") return;
  const list = $("#hero-results");
  if (event.key === "ArrowDown") {
    event.preventDefault();
    if (list.hidden) {
      computeMatches(event.target.value);
      return;
    }
    searchActive = Math.min(matches.length - 1, searchActive + 1);
    renderResults();
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    searchActive = Math.max(0, searchActive - 1);
    renderResults();
  } else if (event.key === "Enter") {
    if (searchActive >= 0 && matches[searchActive]) {
      event.preventDefault();
      selectHero(matches[searchActive].id, true);
    }
  } else if (event.key === "Escape") {
    hideResults();
  }
});

explorer.addEventListener("mousedown", (event) => {
  const item = event.target.closest("#hero-results [data-id]");
  if (!item) return;
  event.preventDefault();
  selectHero(item.dataset.id, true);
});

document.querySelector(".network-switch").addEventListener("click", (event) => {
  const button = event.target.closest("[data-net]");
  if (button) switchNetwork(button.dataset.net);
});

/* ----------------------------------------------------------------- dialogs */

function openDialog(title, content) {
  $("#dialog-title").textContent = title;
  $("#dialog-content").innerHTML = content;
  $("#info-dialog").showModal();
}
$("#close-dialog").addEventListener("click", () => $("#info-dialog").close());
$("#info-dialog").addEventListener("click", (event) => {
  if (event.target !== $("#info-dialog")) return;
  const r = event.target.getBoundingClientRect();
  if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)
    event.target.close();
});

$("#help-button").addEventListener("click", () =>
  openDialog("How to read this", `
    <ol>
      <li><strong>Left: the whole network.</strong> Every node and every connection, placed by a force-directed
        layout and sized by number of connections. Compare the shapes — the scale-free model grows obvious
        hubs, the random model is an even mesh.</li>
      <li><strong>Right: every hero as one dot.</strong> Across is their own number of connections; up is the
        average across all their friends. The diagonal is "exactly equal".</li>
      <li><strong>Above the line = the paradox.</strong> A dot above the diagonal is a hero whose friends are,
        on average, better connected than they are.</li>
      <li><strong>Click anything</strong> — a node in the network or a dot in the scatter — to inspect that
        hero below, with its own circle of friends drawn out.</li>
      <li><strong>Switch networks</strong> at the top. The scatter keeps the same axes every time, so you can
        watch the cloud lift off the line for Marvel and flatten onto it for the random model.</li>
    </ol>
    <p>Keyboard: Tab to the search box, type a name or number, then ↑ ↓ and Enter. Every node and dot has a
      tooltip on hover.</p>`)
);

$("#data-button").addEventListener("click", () => {
  if (!data) return;
  const net = network();
  openDialog("Behind the data", `
    <p><strong>${data.networks.marvel.nodes} hero articles, ${data.networks.marvel.edges.toLocaleString()} undirected connections.</strong>
      Wikipedia article links from the frozen Week 1 snapshot — not friendships or alliances in the stories.
      A link in either direction counts once.</p>
    <p><strong>The two models</strong> use the same ${data.networks.marvel.nodes} nodes. The scale-free network is a
      Barabási–Albert graph (growth plus preferential attachment), m = ${data.baParameter}, seed ${data.seeds.barabasiAlbert}.
      The random network is a uniform G(n, m) graph with the same edge count as Marvel, seed ${data.seeds.randomGnm}.
      Both are generated by <code>prepare_data.py</code> using the Python standard library only.</p>
    <p><strong>The identity.</strong> A node reached along a random edge has expected degree ⟨k⟩ + σ²/⟨k⟩,
      where σ² is the degree variance. Here: ${one(net.meanDegree)} + ${one(net.variance / net.meanDegree)} = ${one(net.friendMeanDegree)}.</p>
    <p><strong>"Above the line"</strong> means the mean degree of a hero's friends exceeds their own degree.
      Isolated nodes (degree 0) are excluded from the chart and from the ${pct(net.paradoxFraction)} figure.</p>
    <p>All values are precomputed from the full snapshot. Source SHA-256: <code>${esc(data.sourceSha256.slice(0, 16))}…</code></p>
    <p><a href="../../data/week2/Week%202_Models%20%26%20null%20models_02805_curriculum.html">Read the Week 2 curriculum ↗</a>
      · <a href="README.md">Data and methods ↗</a></p>`);
});

/* -------------------------------------------------------------------- boot */

async function load() {
  try {
    const response = await fetch("./paradox-data.json");
    if (!response.ok) throw new Error("data");
    data = await response.json();
    let peak = 0;
    for (const net of Object.values(data.networks)) {
      for (const h of Object.values(net.heroes)) {
        if (h.degree > peak) peak = h.degree;
        if (h.neighborMean > peak) peak = h.neighborMean;
      }
    }
    axisMax = niceCeil(peak, 20);
    selectedId = network().suggested;
    render(true);
  } catch {
    $("#explorer").innerHTML = `
      <div class="error">
        <h2>The network couldn't load.</h2>
        <p>If you opened the HTML file directly, serve the folder over HTTP instead:
          <code>python -m http.server</code> from the repository root, then open this page through
          <code>localhost</code>.</p>
      </div>`;
  }
}

load();
