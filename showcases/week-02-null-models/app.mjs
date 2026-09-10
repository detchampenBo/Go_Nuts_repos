import { MAX_SCORE, newGame, currentCard, submit, advance, readLeaderboard, saveScore } from "./game.mjs";

const $ = selector => document.querySelector(selector);
const esc = value => String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const percent = value => `${Math.round(value * 100)}%`;
let data, game, selection = null, runId, saved = false;
let animationTimer;
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

function sketch(hero, metric, shuffled = false) {
  const view = shuffled ? hero.shuffled : hero;
  const k = view.degree;
  const points = Array.from({ length: k }, (_, i) => {
    const angle = i * Math.PI * 2 / Math.max(k, 1) - Math.PI / 2;
    const radius = k > 35 ? 39 + (i % 3) * 11 : 57;
    return [80 + Math.cos(angle) * radius, 80 + Math.sin(angle) * radius];
  });
  const link = (a, b, color, width) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${color}" stroke-width="${width}"/>`;
  const between = metric === "clustering" ? view.links.map(([a, b]) => `<g class="triangle" tabindex="0" role="img" aria-label="Linked neighbor pair: one closed triangle"><path class="triangle-fill" d="M80 80 L${points[a].join(" ")} L${points[b].join(" ")} Z"/>${link(points[a], points[b], "#b64025", 1.8)}</g>`).join("") : "";
  const label = metric === "degree"
    ? `Connection sketch for ${hero.name}. ${k < 6 ? "A small circle of fewer than six neighbors." : k < 15 ? "A medium circle of six to fourteen neighbors." : k < 40 ? "A large circle of fifteen to thirty-nine neighbors." : "A very large circle of at least forty neighbors."}`
    : `Neighborhood of ${hero.name}: ${k} neighbors, ${view.links.length} links among them. Compare the share of possible neighbor pairs that are linked.`;
  return `<svg class="network" viewBox="0 0 160 160" role="img" aria-label="${esc(label)}">
    <circle cx="80" cy="80" r="67" fill="${metric === "degree" ? "#f1f5f6" : "#faf1e9"}"/>
    ${points.map(p => link([80, 80], p, "#b7c5cc", 1)).join("")}${between}
    ${points.map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="${k > 35 ? 2.4 : 3.5}" fill="#456c78"/>`).join("")}
    <circle cx="80" cy="80" r="9" fill="#fff"/><circle cx="80" cy="80" r="6" fill="#b64025"/>
  </svg>`;
}

function heroCard(id, metric, reveal = true, fresh = false, shuffled = false) {
  const hero = data.heroes[id];
  const view = shuffled ? hero.shuffled : hero;
  const measure = metric === "degree" ? `${view.degree} links` : `Clustering: ${percent(view.clustering)}`;
  return `<article class="hero-card${fresh ? " new-card" : ""}"><div class="card-heading"><span class="hero-emblem" aria-hidden="true">${esc(hero.name.split(/[ -]/).map(w => w[0]).slice(0, 2).join(""))}</span><span>FIELD NOTES / ${metric === "degree" ? "01" : "02"}</span></div>${sketch(hero, metric, shuffled)}
    <h3>${esc(hero.name)}</h3><div class="hero-value${reveal ? "" : " hidden"}">${reveal ? measure : "?"}</div></article>`;
}

function challenge(title, description) {
  return `<div class="challenge"><div><h2 id="challenge-title" tabindex="-1">${title}</h2><p>${description}</p></div><span class="round-badge">${game.round - game.startRound + 1} / ${8 - game.startRound}</span></div>`;
}

function feedback() {
  const result = game.answers.at(-1);
  let explanation;
  if (result.card) {
    const hero = data.heroes[result.card.id];
    explanation = result.card.metric === "degree"
      ? `${esc(hero.name)} has <strong style="display:inline;color:inherit">${hero.degree} connections</strong> in this snapshot. ${hero.degree > data.edges * 2 / data.nodes ? "That is above" : "That is below"} the network average of ${(data.edges * 2 / data.nodes).toFixed(1)}. The lineup now shows the correct position.`
      : `${esc(hero.name)} has ${hero.degree} neighbors and ${hero.links.length} links among their ${hero.degree * (hero.degree - 1) / 2} possible pairs: <strong style="display:inline;color:inherit">${percent(hero.clustering)} clustering</strong>. Each linked pair completes a triangle with the hero.`;
  } else if (game.round === 6) {
    explanation = "Every hero keeps exactly the same number of links. Their degree ranking stays fixed, even though their neighbors can change.";
  } else {
    explanation = `Average clustering falls from ${data.clustering.toFixed(3)} to ${data.shuffleMean.toFixed(3)} across 100 shuffles. The hubs remain. The extra clustering in the real network therefore goes beyond the degree sequence alone.`;
  }
  return `<div class="feedback${result.correct ? "" : " incorrect"}" role="status"><strong>${result.correct ? "Right on. +100 points" : "A useful surprise. +0 points"}</strong><p>${explanation}</p></div>`;
}

function actionBar() {
  if (game.phase === "revealed") return `<div class="action-bar">${feedback()}<button class="primary-button" id="next-button">${game.round === 7 ? "See my score" : game.round === 2 ? "Try tight circles" : game.round === 5 ? "Time to shuffle" : "Next prediction"} <span aria-hidden="true">→</span></button></div>`;
  return `<div class="action-bar"><p class="action-copy" id="selection-status" role="status">${selection === null ? "Make a prediction. Each correct answer earns 100 points." : "Prediction selected. Ready for the reveal?"}</p><button class="primary-button" id="check-button" ${selection === null ? "disabled" : ""}>Reveal answer <span aria-hidden="true">→</span></button></div>`;
}

function renderPlacement() {
  const card = currentCard(game);
  const isDegree = card.metric === "degree";
  const revealed = game.phase === "revealed";
  const slot = index => `<button class="slot${selection === index ? " selected" : ""}" data-slot="${index}" aria-pressed="${selection === index}" aria-label="Place ${esc(data.heroes[card.id].name)} ${index === 0 ? "before " + esc(data.heroes[game.row[0]].name) : index === game.row.length ? "after " + esc(data.heroes[game.row.at(-1)].name) : "between " + esc(data.heroes[game.row[index - 1]].name) + " and " + esc(data.heroes[game.row[index]].name)}">${selection === index ? "✓" : "+"}</button>`;
  const row = game.row.map((id, i) => `${revealed ? "" : slot(i)}${heroCard(id, card.metric, true, revealed && id === card.id)}`).join("") + (revealed ? "" : slot(game.row.length));
  return `${challenge(isDegree ? "Where does this hero belong?" : "How tight is this hero’s circle?", isDegree
    ? "Estimate the number of connections from the sketch. Place the new hero from fewest to most."
    : "Compare the share of neighbor pairs joined by orange links. Place the new hero from least to most tightly connected.")}
    <div class="play-area"><aside class="candidate"><p class="eyebrow">${revealed ? "JUST REVEALED" : "YOUR NEXT HERO"}</p>${heroCard(card.id, card.metric, revealed)}
      <p class="candidate-note">${isDegree ? "The orange dot is your hero. Each blue dot is one of their neighbors. All their neighbors are shown." : "Blue dots are neighbors. Orange lines link neighbors to each other. Hover or tap an orange link to illuminate a triangle. Compare linked pairs with all possible pairs."}</p></aside>
    <div class="lineup-area"><div class="axis"><span>${isDegree ? "Fewer connections" : "Looser circle"}</span><span class="axis-line" aria-hidden="true"></span><span>${isDegree ? "More connections" : "Tighter circle"}</span></div>
      <div class="lineup-scroll"><div class="lineup">${row}</div></div><p class="slot-hint">${revealed ? "The outlined card is the hero you just placed." : 'Choose a <strong>+</strong> to place your card. Swipe the row if needed.'}</p></div></div>${actionBar()}`;
}

function swapDiagram() {
  return `<div class="swap-lab"><svg class="swap-diagram" viewBox="0 0 440 200" role="img" aria-label="Illustrative edge swap: A–B and C–E become A–E and C–B. Every degree is preserved; a triangle opens.">
    <g stroke="#a4bab8" stroke-width="3"><path d="M65 45L220 25L375 45"/></g>
    <path id="swap-edges" d="M65 45L375 45 M65 155L375 155" fill="none" stroke="#c34426" stroke-width="4"/>
    ${[[65,45,"A"],[375,45,"B"],[65,155,"C"],[220,25,"D"],[375,155,"E"]].map(([x,y,label]) => `<circle cx="${x}" cy="${y}" r="19" fill="#193c40"/><text x="${x}" y="${y+5}" text-anchor="middle" fill="white" font-size="14">${label}</text>`).join("")}
    </svg><button class="primary-button accent" id="scramble-button">Scramble this universe ↗</button><p id="swap-status" role="status">Illustrative swap · A: 2 · B: 2 · C: 1 · D: 2 · E: 1<br>One closed triangle</p></div>`;
}

function histogram(count = 100) {
  const max = Math.max(data.clustering, ...data.shuffleSamples, ...data.randomSamples) * 1.15;
  const sets = [data.randomSamples, data.shuffleSamples].map(samples => {
    const bins = Array(45).fill(0);
    for (const v of samples.slice(0, count)) bins[Math.min(44, Math.floor(v / max * 45))]++;
    return bins;
  });
  const tallest = Math.max(1, ...sets.flat());
  const x = value => 65 + value / max * 760;
  return `<svg class="histogram" viewBox="0 0 900 310" role="img" aria-label="${count} of 100 precomputed samples per baseline. Random mean ${data.randomMean.toFixed(3)}, degree-preserving shuffle mean ${data.shuffleMean.toFixed(3)}, real clustering ${data.clustering.toFixed(3)}.">
    ${[0, .5, 1].map(f => `<line x1="65" x2="825" y1="${235-f*155}" y2="${235-f*155}" stroke="#e3e0d8"/><text x="50" y="${240-f*155}" text-anchor="end" class="chart-label">${Math.round(f*tallest)}</text>`).join("")}
    <text x="65" y="25" class="chart-label">Samples per bin · ${count}/100 per baseline</text>
    ${sets.map((bins, j) => bins.map((n,i) => `<rect x="${65+i*760/45}" y="${235-n/tallest*155}" width="15" height="${n/tallest*155}" fill="${j ? '#237b76' : '#8575b3'}" opacity=".85" rx="2"/>`).join("")).join("")}
    <line x1="${x(data.clustering)}" x2="${x(data.clustering)}" y1="55" y2="235" stroke="#c34426" stroke-width="4"/>
    <text x="${x(data.clustering)}" y="45" text-anchor="middle" fill="#c34426" font-size="16">Real: ${data.clustering.toFixed(3)}</text>
    ${[0,.05,.1,.15,.2,.25,.3,.35].filter(v => v <= max).map(v => `<text x="${x(v)}" y="260" text-anchor="middle" class="chart-label">${v.toFixed(2)}</text>`).join("")}
    <text x="445" y="295" text-anchor="middle" class="chart-label">Average clustering · all ${data.nodes} nodes</text></svg>`;
}

function animateSamples() {
  clearInterval(animationTimer);
  let count = reducedMotion() ? 100 : 0;
  const draw = () => { const chart = $("#null-chart"); if (chart) chart.innerHTML = histogram(count); };
  draw();
  if (count === 100) return;
  animationTimer = setInterval(() => { count = Math.min(100, count + 2); draw(); if (count === 100) clearInterval(animationTimer); }, 45);
}

function renderShuffle() {
  const first = game.round === 6;
  const revealed = game.phase === "revealed";
  const choices = first
    ? [["stay", "The ranking stays", "Same heroes, same connection counts."], ["change", "The ranking changes", "New neighbors, a new order."]]
    : [["lower", "Less clustering", "Fewer closed circles, on average."], ["same", "About the same", "The hubs explain the tight circles."], ["higher", "More clustering", "The shuffle makes circles tighter."]];
  let content;
  if (!revealed) {
    content = `<div class="shuffle-intro">${swapDiagram()}<p class="shuffle-explanation">Swap who links to whom, thousands of times. <strong>Every hero keeps exactly the same number of connections.</strong> We shuffle the whole network, including its hubs.</p></div>
      <div class="choices" role="group" aria-label="Your prediction">${choices.map(([key, title, note]) => `<button class="choice${selection === key ? " selected" : ""}" data-choice="${key}" aria-pressed="${selection === key}"><strong>${title}</strong><span>${note}</span></button>`).join("")}</div>`;
  } else if (first) {
    const id = game.puzzle.clustering[2];
    const hero = data.heroes[id];
    content = `<div class="shuffle-result"><div class="mini-comparison"><div><p class="eyebrow">BEFORE</p>${heroCard(id, "clustering")}</div><div><p class="eyebrow">AFTER A SHUFFLE</p>${heroCard(id, "clustering", true, false, true)}</div></div>
      <div class="result-note"><h3>The links move. The counts stay.</h3><p>${esc(hero.name)} has ${hero.degree} neighbors before and after. The orange links show how their neighborhood can change. The complete ranking by connection count stays exactly the same.</p><div class="stats-pair"><div><strong>${hero.degree}</strong><span>Neighbors before</span></div><div><strong>${hero.shuffled.degree}</strong><span>Neighbors after</span></div></div></div></div>`;
  } else {
    const extreme = data.shuffleSamples.filter(v => v >= data.clustering).length;
    content = `<div class="null-reveal"><p class="eyebrow">THE EVIDENCE</p><h3>Same connection counts.<br><em>${Math.round((1-data.shuffleMean/data.clustering)*100)}% less clustering.</em></h3><div class="chart-legend"><span class="random-key">Random links · same n and m</span><span class="shuffle-key">Shuffled · every degree preserved</span><span class="real-key">Real Marvel network</span></div><div id="null-chart">${histogram()}</div><button class="secondary-button" id="replay-samples">Replay sample reveal</button><p class="storage-note">100 precomputed networks per baseline, revealed in sequence.</p><div class="result-note"><h3>Can hubs alone explain these tight circles?</h3><p>${extreme} out of 100 shuffles reached the real network’s clustering. Keeping the hubs was not enough to reproduce its tightly linked circles. This supports structure beyond the degree sequence; it does not identify its cause. Empirical p = ${data.empiricalP.toFixed(4)}.</p><div class="stats-pair"><div><strong>${data.randomMean.toFixed(3)}</strong><span>Random-link average</span></div><div><strong>${data.clustering.toFixed(3)}</strong><span>Real network</span></div><div><strong>${data.shuffleMean.toFixed(3)}</strong><span>Shuffle average</span></div></div></div></div>`;
  }
  return `${challenge(first ? "Would a degree ranking survive?" : "What happens to the tight circles?", first
    ? "Imagine heroes ranked by their number of connections. Predict what happens when we shuffle the links."
    : "Predict how the network’s average clustering compares after 100 degree-preserving shuffles.")}
    <div class="shuffle-area">${content}</div>${actionBar()}`;
}

function leaderboardMarkup() {
  let entries;
  try { entries = readLeaderboard(localStorage).filter(e => e.puzzle === game.puzzle.id).sort((a, b) => b.score - a.score || a.date - b.date).slice(0, 10); }
  catch { return '<p class="empty-board">Your browser is blocking saved scores. You can still play every puzzle.</p>'; }
  if (!entries.length) return '<div class="empty-board">An open spot at the top.<br>Save a score to start this puzzle’s leaderboard.</div>';
  return `<table><caption class="storage-note">Top 10 · Puzzle ${game.puzzle.id} · This browser</caption><thead><tr><th scope="col">Rank</th><th scope="col">Name</th><th scope="col">Score</th></tr></thead><tbody>${entries.map((e, i) => `<tr${e.id === runId ? ' class="current-entry"' : ""}><td>${i + 1}</td><td>${esc(e.name)}</td><td>${e.score}</td></tr>`).join("")}</tbody></table>`;
}

function renderFinish() {
  return `<div class="finish-takeaway"><p class="eyebrow">TAKE THIS WITH YOU</p><h2>Hubs survive. Tight circles unravel.</h2><p>Keeping every degree still lowers average clustering from ${data.clustering.toFixed(3)} to ${data.shuffleMean.toFixed(3)}. The real network has structure beyond its connection counts.</p></div><div class="finish"><div><p class="eyebrow">PUZZLE ${game.puzzle.id} COMPLETE</p><h2 id="challenge-title" tabindex="-1">${game.score >= 600 ? "A feel for the network." : "A few new connections."}</h2>
    <div class="final-score">${game.score}<span> / ${(8-game.startRound)*100}</span></div><div class="result-squares" aria-label="${game.score / 100} correct out of ${8-game.startRound} predictions">${game.answers.map((a, i) => `<span class="result-square${a.correct ? " correct" : ""}" title="Prediction ${i + 1}: ${a.correct ? "correct" : "incorrect"}" aria-hidden="true">${a.correct ? "✓" : "−"}</span>`).join("")}</div>
    <p class="finish-copy">${game.score / 100} of ${8-game.startRound} predictions correct. You explored connections, clustering, and the structure that a shuffle leaves behind.</p>
    ${game.startRound ? '<p class="storage-note">Practice complete. Start Connections for an eight-prediction leaderboard run.</p>' : `<form class="save-form" id="save-form"><label for="player-name">Add your name to the leaderboard <span class="storage-note">(optional)</span></label><div class="input-row"><input id="player-name" name="name" maxlength="24" placeholder="Your name" autocomplete="nickname" required ${saved ? "disabled" : ""}/><button class="primary-button" type="submit" ${saved ? "disabled" : ""}>${saved ? "Score saved ✓" : "Save score"}</button></div><p class="storage-note">Saved on this browser only. Other visitors won’t see your name.</p><p class="form-message" id="save-message" role="status"></p></form>`}
    <div class="finish-actions"><button class="primary-button accent" id="another-button">Next puzzle →</button><button class="secondary-button" id="replay-button">Replay this puzzle</button></div></div>
    <aside class="leaderboard-panel"><p class="eyebrow">THE LOCAL LEADERBOARD</p><h3>${esc(game.puzzle.name)}</h3><p class="storage-note">Same puzzle. Same eight predictions. Ties keep the earlier score first.</p><div id="leaderboard-entries">${leaderboardMarkup()}</div></aside></div>`;
}

function render(focus = false) {
  clearInterval(animationTimer);
  $("#run-description").textContent = game.startRound ? `Practice · ${8-game.startRound} predictions · no leaderboard` : "Full run · 8 predictions";
  $(".score-box > div > span").textContent = ` / ${(8-game.startRound)*100}`;
  $("#score").textContent = String(game.score).padStart(3, "0");
  $("#puzzle-label").textContent = `Puzzle ${game.puzzle.id} · ${game.puzzle.name}`;
  const stage = Math.min(2, Math.floor(game.round / 3));
  for (let i = 0; i < 3; i++) {
    const item = $(`#stage-${i}`);
    item.classList.toggle("done", (i >= game.startRound / 3 && i < stage) || (game.phase === "complete" && i >= game.startRound / 3));
    if (i === stage && game.phase !== "complete") item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  }
  $("#game").innerHTML = game.phase === "complete" ? renderFinish() : game.round < 6 ? renderPlacement() : renderShuffle();
  if (game.round === 7 && game.phase === "revealed") animateSamples();
  if (focus) {
    const target = game.phase === "revealed" ? $("#next-button") : $("#challenge-title");
    target?.focus({ preventScroll: true });
  }
}

function select(choice) {
  if (game.phase !== "answering") return;
  selection = choice;
  document.querySelectorAll("[data-slot], [data-choice]").forEach(button => {
    const chosen = button.dataset.slot !== undefined ? Number(button.dataset.slot) === choice : button.dataset.choice === choice;
    button.classList.toggle("selected", chosen);
    button.setAttribute("aria-pressed", String(chosen));
    if (button.dataset.slot !== undefined) button.textContent = chosen ? "✓" : "+";
  });
  $("#check-button").disabled = false;
  $("#selection-status").textContent = "Prediction selected. Ready for the reveal?";
}

function start(puzzleId, stage = 0) {
  clearInterval(animationTimer);
  game = newGame(data, puzzleId, stage);
  $("#puzzle-select").value = puzzleId;
  selection = null;
  saved = false;
  runId = crypto.randomUUID();
  render();
}

function openDialog(title, content) {
  $("#dialog-title").textContent = title;
  $("#dialog-content").innerHTML = content;
  $("#info-dialog").showModal();
}

$("#game").addEventListener("click", event => {
  const triangle = event.target.closest(".triangle");
  if (triangle) { triangle.classList.toggle("active"); return; }
  const button = event.target.closest("button");
  if (!button) return;
  if (button.id === "replay-samples") { animateSamples(); return; }
  if (button.id === "scramble-button") {
    const swapped = button.dataset.swapped !== "true";
    button.dataset.swapped = String(swapped);
    $("#swap-edges").setAttribute("d", swapped ? "M65 45L375 155 M65 155L375 45" : "M65 45L375 45 M65 155L375 155");
    $("#swap-status").innerHTML = `Illustrative swap · A: 2 · B: 2 · C: 1 · D: 2 · E: 1<br>${swapped ? "Triangle opened. Every degree stays fixed." : "One closed triangle"}`;
    button.textContent = swapped ? "Restore the links ↶" : "Scramble this universe ↗";
    return;
  }
  if (button.id === "retry-load") { load(); return; }
  if (!game) return;
  if (button.dataset.slot !== undefined) select(Number(button.dataset.slot));
  else if (button.dataset.choice) select(button.dataset.choice);
  else if (button.id === "check-button" && selection !== null) {
    if (submit(game, data, selection)) render(true);
  } else if (button.id === "next-button") {
    advance(game, data); selection = null; render(true);
  } else if (button.id === "another-button" || button.id === "replay-button") {
    const next = button.id === "replay-button" ? game.puzzle.id : data.puzzles[(data.puzzles.findIndex(p => p.id === game.puzzle.id) + 1) % data.puzzles.length].id;
    start(next, game.startRound / 3); $("#challenge-title").focus();
  }
});

$("#game").addEventListener("submit", event => {
  if (event.target.id !== "save-form") return;
  event.preventDefault();
  if (saved) return;
  const name = $("#player-name").value;
  if (!name.trim()) { $("#save-message").textContent = "Enter a name, or continue without saving."; return; }
  try {
    saveScore(localStorage, game, name, runId);
    saved = true;
    $("#player-name").disabled = true;
    const button = $("#save-form button");
    button.disabled = true;
    button.textContent = "Score saved ✓";
    $("#save-message").textContent = "Your score is saved in this browser.";
    $("#leaderboard-entries").innerHTML = leaderboardMarkup();
  } catch {
    $("#save-message").textContent = "This browser couldn’t save your score. Allow site storage and try again; your result is still here.";
  }
});

$("#help-button").addEventListener("click", () => openDialog("A little intuition is all you need.", `
  <ol><li><strong>Place the hero.</strong> Look at the next card’s network sketch, then choose a + between the revealed cards. The row runs from lowest to highest.</li>
  <li><strong>Reveal the answer.</strong> A correct prediction earns 100 points. After a miss, the card moves to its correct position so you can learn from it.</li>
  <li><strong>Change your perspective.</strong> First rank connection counts, then the share of neighbor pairs that are linked. Finish with two predictions about shuffling.</li></ol>
  <p>Eight predictions, up to 800 points. No timer or lives. Use Tab and Enter to play with a keyboard. On a narrow screen, swipe the lineup to see all its cards.</p>
  <p>You can save a name after finishing. Each of the three puzzles has its own leaderboard in this browser. Replays are allowed.</p>`));
$("#leaderboard-button").addEventListener("click", () => {
  if (game) openDialog(`Leaderboard · Puzzle ${game.puzzle.id}`, `<p>Names and scores are saved in this browser only. Complete the puzzle to add yours.</p>${leaderboardMarkup()}`);
});
$("#data-button").addEventListener("click", () => {
  if (!data) return;
  openDialog("Behind the puzzle", `<p><strong>${data.nodes} hero articles. ${data.edges.toLocaleString()} connections.</strong> These are Wikipedia article links from the frozen Week 1 dataset, not evidence of friendships or alliances in Marvel stories.</p>
    <p>The original ${data.directedEdges.toLocaleString()} hyperlinks have a direction. For this puzzle, a link in either direction counts as one undirected connection. Reciprocal links count once.</p>
    <p><strong>Clustering</strong> is the number of links among a hero’s neighbors divided by the number of possible neighbor pairs. It measures the share of closed triangles, not the raw number of links.</p>
    <p><strong>The shuffle test:</strong> 100 independently restarted shuffles, each with ${ (data.edges * 10).toLocaleString()} accepted edge swaps and a fixed random seed. No self-links or duplicate edges. Each hero keeps their exact degree. We average local clustering over all ${data.nodes} heroes, counting degree below 2 as zero, including the ${data.isolates} isolates.</p>
    <p><strong>Random-link baseline:</strong> 100 uniform simple G(n,m) graphs keep the same ${data.nodes} nodes and ${data.edges.toLocaleString()} edges, but allow individual degrees to change. Their mean clustering is ${data.randomMean.toFixed(3)}. Both baselines use the same all-node average.</p>
    <p>These are precomputed results from the full snapshot. The small diagrams show complete neighborhoods; the connection-count stage omits neighbor-to-neighbor lines for clarity.</p>
    <p>The final histogram compares the network statistic, not your game score, with the null distribution. Its one-sided empirical p-value uses (1 + shuffles at least as high) / 101. A finite simulation never establishes a probability of zero.</p>
    <p><a href="../../data/week2/Week%202_Models%20%26%20null%20models_02805_curriculum.html">Read the Week 2 curriculum ↗</a> · <a href="README.md">Data and methods ↗</a></p>`);
});
$("#close-dialog").addEventListener("click", () => $("#info-dialog").close());
$("#info-dialog").addEventListener("click", event => { if (event.target === $("#info-dialog")) { const r = event.target.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) event.target.close(); } });

document.querySelector(".stages").addEventListener("click", event => {
  const button = event.target.closest("[data-stage]");
  if (!button || !data) return;
  start(game.puzzle.id, Number(button.dataset.stage));
  $("#challenge-title").focus({preventScroll:true});
});

$("#puzzle-select").addEventListener("change", event => { start(event.target.value, game.startRound / 3); $("#challenge-title").focus({preventScroll:true}); });

async function load() {
  try {
    const response = await fetch("./puzzle-data.json");
    if (!response.ok) throw new Error("Data could not load");
    data = await response.json();
    $("#puzzle-select").innerHTML = data.puzzles.map(p => `<option value="${p.id}">Deck ${p.id} · ${esc(p.name)}</option>`).join("");
    $("#puzzle-select").disabled = false;
    start(data.puzzles[0].id);
  } catch {
    $("#game").innerHTML = '<div class="error"><h2>The cards couldn’t load.</h2><p>Check your connection and try again. If you opened the HTML file directly, open the site through a local web server instead.</p><button id="retry-load" class="primary-button">Try again</button></div>';
    $("#puzzle-label").textContent = "Puzzle unavailable";
  }
}
load();
