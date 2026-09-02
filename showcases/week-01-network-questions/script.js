const graph = document.querySelector("#network-graph");
const resetButton = document.querySelector("#reset-graph");
const details = {
  index: document.querySelector("#selected-index"),
  title: document.querySelector("#selected-title"),
  copy: document.querySelector("#selected-copy"),
  connections: document.querySelector("#selected-connections"),
  status: document.querySelector("#selected-status"),
};

let network;
let selectedId;

function makeSvgElement(name, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  return element;
}

function connectionsFor(id) {
  return network.edges.filter((edge) => edge.source === id || edge.target === id);
}

function selectNode(id) {
  selectedId = id;
  const node = network.nodes.find((item) => item.id === id);
  const connections = connectionsFor(id);
  const connectedIds = new Set(connections.flatMap((edge) => [edge.source, edge.target]));

  document.querySelectorAll(".graph-node").forEach((element) => {
    element.classList.toggle("is-selected", element.dataset.nodeId === id);
  });
  document.querySelectorAll(".graph-edge").forEach((element) => {
    const edge = element.dataset;
    element.classList.toggle("is-active", edge.source === id || edge.target === id);
  });

  details.index.textContent = `${String(node.order).padStart(2, "0")} / ${String(network.nodes.length).padStart(2, "0")}`;
  details.title.textContent = node.label;
  details.copy.textContent = node.question;
  details.connections.textContent = `${connectedIds.size - 1} question${connectedIds.size === 2 ? "" : "s"}`;
  details.status.textContent = node.status;
}

function drawNetwork() {
  const defs = makeSvgElement("defs");
  const marker = makeSvgElement("marker", {
    id: "arrow", viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "6", markerHeight: "6", orient: "auto-start-reverse",
  });
  marker.appendChild(makeSvgElement("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#526175" }));
  defs.appendChild(marker);
  graph.appendChild(defs);

  const edgeLayer = makeSvgElement("g", { "aria-hidden": "true" });
  network.edges.forEach((edge) => {
    const source = network.nodes.find((node) => node.id === edge.source);
    const target = network.nodes.find((node) => node.id === edge.target);
    edgeLayer.appendChild(makeSvgElement("line", {
      x1: source.x, y1: source.y, x2: target.x, y2: target.y,
      class: "graph-edge", "marker-end": "url(#arrow)", "data-source": edge.source, "data-target": edge.target,
    }));
  });
  graph.appendChild(edgeLayer);

  const nodeLayer = makeSvgElement("g");
  network.nodes.forEach((node) => {
    const group = makeSvgElement("g", { class: "graph-node", tabindex: "0", role: "button", "aria-label": `Explore ${node.label}`, "data-node-id": node.id });
    group.appendChild(makeSvgElement("circle", { cx: node.x, cy: node.y, r: 17, fill: node.color }));
    const label = makeSvgElement("text", { x: node.x + 27, y: node.y + 5 });
    label.textContent = node.label;
    group.appendChild(label);
    group.addEventListener("click", () => selectNode(node.id));
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectNode(node.id);
      }
    });
    nodeLayer.appendChild(group);
  });
  graph.appendChild(nodeLayer);
  selectNode(network.nodes[0].id);
}

fetch("data/graph-data.json")
  .then((response) => {
    if (!response.ok) throw new Error("The network data could not be loaded.");
    return response.json();
  })
  .then((data) => {
    network = data;
    drawNetwork();
  })
  .catch(() => {
    graph.replaceChildren();
    graph.insertAdjacentHTML("afterbegin", '<text x="40" y="70" fill="white">Network data is unavailable. Check data/graph-data.json.</text>');
  });

resetButton.addEventListener("click", () => {
  if (network) selectNode(network.nodes[0].id);
});
