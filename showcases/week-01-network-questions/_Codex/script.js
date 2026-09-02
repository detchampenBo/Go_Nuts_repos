const svgNamespace = "http://www.w3.org/2000/svg";
const inboundChart = document.querySelector("#inbound-chart");
const minDegree = document.querySelector("#min-degree");
const degreeOutput = document.querySelector("#degree-output");
const heroSearch = document.querySelector("#hero-search");
const rowLimit = document.querySelector("#row-limit");
const filterSummary = document.querySelector("#filter-summary");

let heroes = [];
let selectedHero;
let networkEdges = [];
let selectedNetworkHero;
let egoMode = false;

const spiderFrame = document.querySelector("#network");
const spiderStage = document.querySelector("#spider-stage");
const spiderNetwork = document.querySelector("#spider-network");
const enterNetwork = document.querySelector("#enter-network");
const graphControls = document.querySelector("#graph-controls");
const networkThreshold = document.querySelector("#network-threshold");
const networkThresholdOutput = document.querySelector("#network-threshold-output");
const networkSearch = document.querySelector("#network-search");
const heroResults = document.querySelector("#hero-results");
const egoLens = document.querySelector("#ego-lens");

function svgElement(tag, attributes = {}) {
  const element = document.createElementNS(svgNamespace, tag);
  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
  return element;
}

function appendText(svg, text, x, y, className) {
  const element = svgElement("text", { x, y, class: className });
  element.textContent = text;
  svg.append(element);
  return element;
}

function format(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function sortedBy(key) {
  return [...heroes].sort((a, b) => b[key] - a[key] || a.name.localeCompare(b.name));
}

function updateDetails(hero) {
  selectedHero = hero;
  const rank = sortedBy("inDegree").findIndex((item) => item.id === hero.id) + 1;
  const gap = hero.inDegree - hero.outDegree;
  document.querySelector("#detail-rank").textContent = `INBOUND RANK ${String(rank).padStart(2, "0")} / ${heroes.length}`;
  document.querySelector("#detail-name").textContent = hero.name;
  document.querySelector("#detail-in").textContent = format(hero.inDegree);
  document.querySelector("#detail-out").textContent = format(hero.outDegree);
  document.querySelector("#detail-gap").textContent = `${gap >= 0 ? "+" : ""}${format(gap)}`;
  document.querySelector("#detail-reading").textContent = gap >= 0
    ? "This article is referenced more often by other hero pages than it references heroes itself."
    : "This article links to more heroes than other hero pages link back to it.";
  const link = document.querySelector("#detail-link");
  link.href = hero.url;
  link.hidden = false;
}

function displayedHeroes() {
  const query = heroSearch.value.trim().toLowerCase();
  return sortedBy("inDegree").filter((hero) => hero.inDegree >= Number(minDegree.value) && hero.name.toLowerCase().includes(query));
}

function renderInboundChart() {
  const matching = displayedHeroes();
  const items = matching.slice(0, Number(rowLimit.value));
  const width = 860;
  const rowHeight = 29;
  const top = 24;
  const left = 190;
  const right = 55;
  const height = Math.max(110, top + items.length * rowHeight + 32);
  const max = Math.max(...items.map((hero) => hero.inDegree), 1);

  inboundChart.replaceChildren();
  inboundChart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  degreeOutput.value = minDegree.value;
  filterSummary.textContent = matching.length
    ? `${format(matching.length)} matching heroes · showing the top ${Math.min(items.length, matching.length)} by inbound degree`
    : "No heroes match these filters.";

  [0, .25, .5, .75, 1].forEach((fraction) => {
    const x = left + fraction * (width - left - right);
    inboundChart.append(svgElement("line", { x1: x, y1: top - 4, x2: x, y2: height - 22, class: "gridline" }));
    appendText(inboundChart, format(Math.round(max * fraction)), x, height - 7, "axis-label").setAttribute("text-anchor", "middle");
  });

  items.forEach((hero, index) => {
    const y = top + index * rowHeight;
    const barWidth = (hero.inDegree / max) * (width - left - right);
    const label = appendText(inboundChart, hero.name, left - 13, y + 16, "chart-label");
    label.setAttribute("text-anchor", "end");
    const bar = svgElement("rect", { x: left, y: y + 4, width: barWidth, height: 16, rx: 2, class: `bar${selectedHero?.id === hero.id ? " is-selected" : ""}`, tabindex: 0, role: "button", "aria-label": `${hero.name}: ${hero.inDegree} incoming links` });
    const select = () => { updateDetails(hero); renderInboundChart(); };
    bar.addEventListener("click", select);
    bar.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(); } });
    inboundChart.append(bar);
    appendText(inboundChart, format(hero.inDegree), left + barWidth + 8, y + 16, "bar-value");
  });
}

function frequency(key) {
  const counts = new Map();
  heroes.forEach((hero) => counts.set(hero[key], (counts.get(hero[key]) || 0) + 1));
  return [...counts.entries()].sort((a, b) => a[0] - b[0]);
}

function heroFor(id) {
  return heroes.find((hero) => hero.id === id);
}

function addArrowMarker(svg) {
  const defs = svgElement("defs");
  const marker = svgElement("marker", { id: "selected-arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "5", markerHeight: "5", orient: "auto" });
  marker.append(svgElement("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "currentColor" }));
  defs.append(marker);
  svg.append(defs);
}

function updateGraphCopy({ title, copy, hero, visible }) {
  document.querySelector("#graph-detail-title").textContent = title;
  document.querySelector("#graph-detail-copy").textContent = copy;
  document.querySelector("#graph-detail-in").textContent = format(hero?.inDegree ?? 106);
  document.querySelector("#graph-detail-out").textContent = format(hero?.outDegree ?? 9);
  document.querySelector("#graph-detail-visible").textContent = format(visible);
}

function openingPositions(count) {
  return Array.from({ length: count }, (_, index) => {
    const angle = -1.18 + index * (2.36 / Math.max(count - 1, 1));
    return { x: 670 + Math.cos(angle) * 160, y: 280 + Math.sin(angle) * 223 };
  });
}

function renderOpeningWeb() {
  const spiderLinks = networkEdges.filter((edge) => edge.source === "Spider-Man");
  const origin = { x: 340, y: 300 };
  const positions = openingPositions(spiderLinks.length);
  spiderNetwork.replaceChildren();
  spiderNetwork.setAttribute("viewBox", "0 0 960 560");

  spiderLinks.forEach((edge, index) => {
    const target = heroFor(edge.target);
    const point = positions[index];
    const path = svgElement("path", { d: `M ${origin.x} ${origin.y} C ${origin.x + 155} ${origin.y - 70 + index * 12}, ${point.x - 105} ${point.y + 25}, ${point.x} ${point.y}`, class: "opening-edge" });
    path.style.animationDelay = `${index * 0.12}s`;
    spiderNetwork.append(path);
    spiderNetwork.append(svgElement("circle", { cx: point.x, cy: point.y, r: 7, class: "opening-node" }));
    const label = appendText(spiderNetwork, target.name, point.x + (point.x > 700 ? -14 : 14), point.y + 4, "opening-label");
    label.setAttribute("text-anchor", point.x > 700 ? "end" : "start");
  });
  updateGraphCopy({
    title: "A web of nine",
    copy: "Each endpoint is a real article Spider-Man links out to. Enter the constellation to inspect who is referenced across the whole network.",
    hero: heroFor("Spider-Man"),
    visible: spiderLinks.length,
  });
}

function networkNodes() {
  if (egoMode && selectedNetworkHero) {
    const directIds = new Set([selectedNetworkHero.id]);
    networkEdges.forEach((edge) => {
      if (edge.source === selectedNetworkHero.id) directIds.add(edge.target);
      if (edge.target === selectedNetworkHero.id) directIds.add(edge.source);
    });
    return heroes.filter((hero) => directIds.has(hero.id));
  }
  const minimum = Number(networkThreshold.value);
  const visible = heroes.filter((hero) => hero.inDegree >= minimum);
  if (selectedNetworkHero && !visible.some((hero) => hero.id === selectedNetworkHero.id)) visible.push(selectedNetworkHero);
  return visible;
}

function positionedNodes(nodes) {
  const positions = new Map();
  const ordered = [...nodes].sort((a, b) => b.inDegree - a.inDegree || a.name.localeCompare(b.name));
  const centre = { x: 496, y: 285 };
  const focus = selectedNetworkHero && ordered.find((hero) => hero.id === selectedNetworkHero.id);
  if (focus) positions.set(focus.id, centre);

  const rest = ordered.filter((hero) => hero.id !== focus?.id);
  rest.forEach((hero, index) => {
    const angle = index * 2.399963229728653;
    const radius = egoMode ? 120 + Math.sqrt(index) * 26 : 70 + Math.sqrt(index) * 49;
    positions.set(hero.id, {
      x: Math.max(48, Math.min(914, centre.x + Math.cos(angle) * radius)),
      y: Math.max(45, Math.min(515, centre.y + Math.sin(angle) * radius * .76)),
    });
  });
  return positions;
}

function selectNetworkHero(hero) {
  selectedNetworkHero = hero;
  egoMode = false;
  egoLens.disabled = false;
  egoLens.textContent = "Open ego lens";
  networkSearch.value = hero.name;
  heroResults.replaceChildren();
  renderConstellation();
}

function renderConstellation() {
  const nodes = networkNodes();
  const ids = new Set(nodes.map((hero) => hero.id));
  const positions = positionedNodes(nodes);
  const visibleEdges = networkEdges.filter((edge) => ids.has(edge.source) && ids.has(edge.target));
  const hubIds = new Set(sortedBy("inDegree").slice(0, 10).map((hero) => hero.id));

  spiderNetwork.replaceChildren();
  spiderNetwork.setAttribute("viewBox", "0 0 960 560");
  addArrowMarker(spiderNetwork);

  visibleEdges.forEach((edge) => {
    const from = positions.get(edge.source);
    const to = positions.get(edge.target);
    const isIncoming = selectedNetworkHero && edge.target === selectedNetworkHero.id;
    const isOutgoing = selectedNetworkHero && edge.source === selectedNetworkHero.id;
    const line = svgElement("line", { x1: from.x, y1: from.y, x2: to.x, y2: to.y, class: `constellation-edge${isIncoming ? " is-incoming" : ""}${isOutgoing ? " is-outgoing" : ""}` });
    if (isIncoming || isOutgoing) line.setAttribute("marker-end", "url(#selected-arrow)");
    if (selectedNetworkHero && !isIncoming && !isOutgoing) line.style.opacity = ".1";
    spiderNetwork.append(line);
  });

  nodes.forEach((hero) => {
    const point = positions.get(hero.id);
    const connected = selectedNetworkHero && networkEdges.some((edge) => (edge.source === hero.id && edge.target === selectedNetworkHero.id) || (edge.target === hero.id && edge.source === selectedNetworkHero.id));
    const muted = selectedNetworkHero && hero.id !== selectedNetworkHero.id && !connected;
    const radius = Math.max(4, Math.min(17, 4 + Math.sqrt(hero.inDegree) * 1.25));
    const node = svgElement("circle", { cx: point.x, cy: point.y, r: radius, class: `constellation-node${hubIds.has(hero.id) ? " is-hub" : ""}${hero.id === selectedNetworkHero?.id ? " is-selected" : ""}${muted ? " is-muted" : ""}`, tabindex: 0, role: "button", "aria-label": `${hero.name}: ${hero.inDegree} incoming links and ${hero.outDegree} outgoing links` });
    const choose = () => selectNetworkHero(hero);
    node.addEventListener("click", choose);
    node.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(); } });
    spiderNetwork.append(node);

    const outgoingEndpoint = egoMode && selectedNetworkHero && networkEdges.some((edge) => edge.source === selectedNetworkHero.id && edge.target === hero.id);
    if (hubIds.has(hero.id) || hero.id === selectedNetworkHero?.id || outgoingEndpoint) {
      const label = appendText(spiderNetwork, hero.name, point.x + radius + 6, point.y + 3, `constellation-label${hubIds.has(hero.id) ? " is-hub" : ""}${muted ? " is-muted" : ""}`);
      if (point.x > 760) { label.setAttribute("x", point.x - radius - 6); label.setAttribute("text-anchor", "end"); }
    }
  });

  const minimum = Number(networkThreshold.value);
  document.querySelector("#graph-kicker").textContent = egoMode ? "EGO LENS / DIRECT LINKS" : `REFERENCE CONSTELLATION / INBOUND ≥ ${minimum}`;
  document.querySelector("#spider-frame-title").textContent = egoMode ? `${selectedNetworkHero.name}'s ego lens` : "Who is referenced across the network?";
  document.querySelector("#graph-summary").textContent = egoMode
    ? "Direct inbound and outbound hero links around the selected article."
    : `${format(nodes.length)} visible hero articles. Search to reveal and inspect a different article.`;
  document.querySelector("#stage-note").textContent = egoMode ? `${format(visibleEdges.length)} direct visible links` : `${format(nodes.length)} heroes / ${format(visibleEdges.length)} visible links`;
  updateGraphCopy({
    title: selectedNetworkHero ? selectedNetworkHero.name : "Reference constellation",
    copy: selectedNetworkHero
      ? "Blue strands point into this article; coral strands point out. Other connections fade so the direction stays readable."
      : "Node size follows inbound degree. Use search or select a node to reveal the direction of its direct links.",
    hero: selectedNetworkHero,
    visible: nodes.length,
  });
}

function activateNetwork() {
  spiderFrame.classList.add("is-exploring");
  graphControls.hidden = false;
  renderConstellation();
}

function showHeroMatches() {
  const query = networkSearch.value.trim().toLowerCase();
  heroResults.replaceChildren();
  if (!query) return;
  heroes.filter((hero) => hero.name.toLowerCase().includes(query)).slice(0, 7).forEach((hero) => {
    const result = document.createElement("button");
    result.type = "button";
    result.className = "hero-result";
    result.setAttribute("role", "option");
    result.textContent = `${hero.name} · in ${hero.inDegree} / out ${hero.outDegree}`;
    result.addEventListener("click", () => selectNetworkHero(hero));
    heroResults.append(result);
  });
}

function setupSpiderFrame() {
  renderOpeningWeb();
  enterNetwork.addEventListener("click", activateNetwork);
  spiderStage.addEventListener("mouseenter", () => { if (!spiderFrame.classList.contains("is-exploring")) spiderStage.classList.add("is-preview"); });
  spiderStage.addEventListener("mouseleave", () => spiderStage.classList.remove("is-preview"));
  networkThreshold.addEventListener("input", () => {
    networkThresholdOutput.value = networkThreshold.value;
    egoMode = false;
    egoLens.textContent = "Open ego lens";
    renderConstellation();
  });
  networkSearch.addEventListener("input", showHeroMatches);
  egoLens.addEventListener("click", () => {
    if (!selectedNetworkHero) return;
    egoMode = !egoMode;
    egoLens.textContent = egoMode ? "Return to constellation" : "Open ego lens";
    renderConstellation();
  });
  document.querySelector("#spider-widget").addEventListener("click", () => {
    if (!spiderFrame.classList.contains("is-exploring")) return;
    selectedNetworkHero = heroFor("Spider-Man");
    egoMode = true;
    egoLens.disabled = false;
    egoLens.textContent = "Return to constellation";
    networkSearch.value = "Spider-Man";
    renderConstellation();
  });
}

function drawDistribution(svg, logScale = false) {
  const width = 520;
  const height = 260;
  const pad = { top: 20, right: 20, bottom: 38, left: 43 };
  const series = [
    { key: "inDegree", label: "in-degree", color: "point-in" },
    { key: "outDegree", label: "out-degree", color: "point-out" },
  ];
  const values = series.flatMap(({ key }) => frequency(key).filter(([degree]) => !logScale || degree > 0));
  const xValues = values.map(([degree]) => logScale ? Math.log10(degree) : degree);
  const yValues = values.map(([, count]) => logScale ? Math.log10(count) : count);
  const maxX = Math.max(...xValues, 1);
  const maxY = Math.max(...yValues, 1);
  const x = (value) => pad.left + (logScale ? Math.log10(value) : value) / maxX * (width - pad.left - pad.right);
  const y = (value) => height - pad.bottom - (logScale ? Math.log10(value) : value) / maxY * (height - pad.top - pad.bottom);

  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.append(svgElement("line", { x1: pad.left, y1: height - pad.bottom, x2: width - pad.right, y2: height - pad.bottom, class: "axis" }));
  svg.append(svgElement("line", { x1: pad.left, y1: pad.top, x2: pad.left, y2: height - pad.bottom, class: "axis" }));

  series.forEach(({ key, label, color }, seriesIndex) => {
    const items = frequency(key).filter(([degree]) => !logScale || degree > 0);
    if (logScale) {
      items.forEach(([degree, count]) => svg.append(svgElement("circle", { cx: x(degree), cy: y(count), r: 3.3, class: color })));
    } else {
      const offset = seriesIndex === 0 ? -2 : 2;
      items.forEach(([degree, count]) => {
        const barWidth = Math.max(2, (width - pad.left - pad.right) / (maxX + 1) * .38);
        svg.append(svgElement("rect", { x: x(degree) + offset - barWidth / 2, y: y(count), width: barWidth, height: height - pad.bottom - y(count), class: color }));
      });
    }
    const legendX = pad.left + seriesIndex * 104;
    svg.append(svgElement("circle", { cx: legendX, cy: 10, r: 4, class: color }));
    appendText(svg, label, legendX + 8, 14, "legend-text");
  });
  appendText(svg, logScale ? "log degree" : "degree", width - pad.right, height - 7, "axis-label").setAttribute("text-anchor", "end");
  appendText(svg, logScale ? "log hero count" : "hero count", pad.left, pad.top - 7, "axis-label");
}

function fillTable(target, primary, secondary) {
  target.replaceChildren();
  sortedBy(primary).slice(0, 8).forEach((hero, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${String(index + 1).padStart(2, "0")} · ${hero.name}</td><td>${format(hero[primary])}</td><td>${format(hero[secondary])}</td>`;
    target.append(row);
  });
}

function start(payload) {
  heroes = payload.heroes;
  networkEdges = payload.edges;
  const maxInbound = Math.max(...heroes.map((hero) => hero.inDegree));
  minDegree.max = maxInbound;
  document.querySelector("#node-count").textContent = format(payload.summary.nodes);
  document.querySelector("#edge-count").textContent = format(payload.summary.edges);
  document.querySelector("#isolate-count").textContent = format(payload.summary.isolates);
  document.querySelector("#top-in-stat").textContent = format(maxInbound);
  fillTable(document.querySelector("#inbound-table"), "inDegree", "outDegree");
  fillTable(document.querySelector("#outbound-table"), "outDegree", "inDegree");
  drawDistribution(document.querySelector("#linear-chart"));
  drawDistribution(document.querySelector("#log-chart"), true);
  updateDetails(sortedBy("inDegree")[0]);
  renderInboundChart();
  setupSpiderFrame();
}

[minDegree, heroSearch, rowLimit].forEach((control) => control.addEventListener("input", renderInboundChart));

fetch("heroes.json")
  .then((response) => response.ok ? response.json() : Promise.reject(new Error("Data unavailable")))
  .then(start)
  .catch(() => {
    filterSummary.textContent = "The network data could not be loaded. Serve this folder with a local web server and try again.";
  });
