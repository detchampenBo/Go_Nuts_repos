const fs = require("fs");
const vm = require("vm");

class ClassList {
  constructor(...names) { this.names = new Set(names); }
  add(name) { this.names.add(name); }
  remove(name) { this.names.delete(name); }
  contains(name) { return this.names.has(name); }
  toggle(name, force) {
    const next = force === undefined ? !this.names.has(name) : force;
    if (next) this.add(name); else this.remove(name);
  }
}

class Element {
  constructor({ id = "", classes = [], dataset = {} } = {}) {
    this.id = id;
    this.classList = new ClassList(...classes);
    this.dataset = dataset;
    this.listeners = {};
    this.children = [];
    this.textContent = "";
    this.hidden = false;
    this.value = "";
    this.disabled = false;
    this._innerHTML = "";
  }
  addEventListener(type, handler) { (this.listeners[type] ||= []).push(handler); }
  dispatch(type, event = {}) {
    const action = { preventDefault() {}, ...event, currentTarget: this, target: event.target || this };
    for (const handler of this.listeners[type] || []) handler(action);
  }
  querySelectorAll(selector) {
    if (selector === ".word-chip") return this.children.filter((child) => child.classList.contains("word-chip"));
    if (selector === ".bank-word") return this.children.filter((child) => child.classList.contains("bank-word"));
    return [];
  }
  closest(selector) { return selector === ".word-chip" && this.classList.contains("word-chip") ? this : null; }
  set innerHTML(value) {
    this._innerHTML = value;
    this.children = [];
    const pattern = /data-word="([^"]+)" data-index="(\d+)"/g;
    for (const match of value.matchAll(pattern)) {
      this.children.push(new Element({ classes: ["word-chip"], dataset: { word: match[1], index: match[2] } }));
    }
  }
  get innerHTML() { return this._innerHTML; }
  scrollIntoView() {}
}

class DataTransfer {
  constructor() { this.data = {}; }
  setData(type, value) { this.data[type] = value; }
  getData(type) { return this.data[type] || ""; }
}

const elements = {};
const byId = (id) => (elements[id] ||= new Element({ id }));
const zones = [0, 1, 2].map((lane) => new Element({ classes: ["dropzone"], dataset: { laneTarget: String(lane) } }));
const bank = byId("word-bank");
for (const word of ["robots", "help", "humans", "and", "doctors"]) {
  bank.children.push(new Element({ classes: ["bank-word"], dataset: { word } }));
}
const document = {
  querySelector(selector) {
    if (selector === "#word-bank") return bank;
    if (selector === ".dropzone") return zones[0];
    if (selector.startsWith("#sentence-")) return byId(selector.slice(1));
    return byId(selector.slice(1));
  },
  querySelectorAll(selector) { return selector === ".dropzone" ? zones : []; },
};
byId("prediction");
byId("compare");
byId("reset");
byId("status");
byId("reveal").hidden = true;
byId("prediction-result");
byId("sentence-stack");
byId("vector-table");

const context = { document, console };
vm.runInNewContext(fs.readFileSync("showcases/explorable widget/script.js", "utf8"), context);

const compare = byId("compare");
const prediction = byId("prediction");
const orderings = [
  ["robots", "help", "humans", "and", "doctors"],
  ["doctors", "help", "robots", "and", "humans"],
  ["humans", "help", "doctors", "and", "robots"],
];

for (const word of orderings[0]) {
  const tile = bank.children.find((candidate) => candidate.dataset.word === word);
  const dataTransfer = new DataTransfer();
  tile.dispatch("dragstart", { dataTransfer });
  zones[0].dispatch("drop", { dataTransfer, target: zones[0] });
}

for (const lane of [1, 2]) {
  const chip = zones[lane].children.find((candidate) => candidate.dataset.word === orderings[lane][0]);
  chip.closest = () => zones[lane];
  const dataTransfer = new DataTransfer();
  chip.dispatch("dragstart", { dataTransfer });
  zones[lane].dispatch("drop", { dataTransfer, target: zones[lane].children[0] });
}

console.log(`complete_without_prediction: ${compare.disabled ? "disabled" : "enabled"}`);
prediction.value = "same";
prediction.dispatch("change", { target: prediction });
console.log(`complete_with_prediction: ${compare.disabled ? "disabled" : "enabled"}`);
compare.dispatch("click");
console.log(`comparison_reveal: ${byId("reveal").hidden ? "hidden" : "visible"}`);

if (!compare.disabled || byId("reveal").hidden) process.exitCode = 1;
