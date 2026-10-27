// The 3D view: one pillar per page, standing where t-SNE puts the page. Height is the chosen measure (hyperlinks,
// times picked as a nearest neighbour, ...). Gold arcs run from every page that picks the selected page to it; mint
// arcs are the selected page's hyperlinks. The page's main script owns the state and calls centreSky.render().
import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';

const app = window.CENTRE_APP, D = window.CENTRE, N = D.nodes.length;
const box = document.getElementById('sky'), labelsBox = document.getElementById('sky-labels'), status = document.getElementById('sky-status');
const tip = document.getElementById('tip');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const S = 10, UNIT = 0.085;  // world half-width of the map, world height per count
const COL = { links: new THREE.Color('#5ee6ae'), picked: new THREE.Color('#f2b705'), centred: new THREE.Color('#ecdcae'),
  random: new THREE.Color('#9fb3bd'), sel: new THREE.Color('#ffffff'), dim: new THREE.Color('#2c5563') };

let renderer;
try { renderer = new THREE.WebGLRenderer({ antialias: true }); }
catch { status.textContent = 'This browser has no WebGL, so the 2D chart is shown.'; app.no3d(); throw new Error('no WebGL'); }
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
box.prepend(renderer.domElement);
renderer.domElement.setAttribute('aria-label', 'Interactive 3D skyline of the pages. Drag to orbit, scroll to zoom, click a pillar.');
renderer.domElement.tabIndex = 0;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#0b2634');
scene.fog = new THREE.Fog('#0b2634', 38, 70);
const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 200);
const HOME = new THREE.Vector3(0, 19, 33);
camera.position.copy(HOME);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.maxPolarAngle = 1.45; controls.minDistance = 7; controls.maxDistance = 60;
controls.target.set(0, 2.5, 0);
scene.add(new THREE.HemisphereLight('#e6f4ff', '#14303a', 1.7));
const sun = new THREE.DirectionalLight('#fff3d6', 2.4); sun.position.set(-10, 22, 12); scene.add(sun);

const sea = new THREE.Mesh(new THREE.CircleGeometry(S * 1.75, 64), new THREE.MeshStandardMaterial({ color: '#103746', roughness: .9 }));
sea.rotateX(-Math.PI / 2); scene.add(sea);
const grid = new THREE.GridHelper(S * 3.2, 32, '#1f5566', '#163f4e'); grid.position.y = 0.01; scene.add(grid);

const pillarGeo = new THREE.CylinderGeometry(0.17, 0.2, 1, 10); pillarGeo.translate(0, 0.5, 0);  // grows up from y=0
const pillars = new THREE.InstancedMesh(pillarGeo, new THREE.MeshStandardMaterial({ roughness: .55, metalness: .05 }), N);
pillars.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(pillars);
const fanArcs = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: '#f2b705', transparent: true, opacity: .8 }));
const linkArcs = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: '#5ee6ae', transparent: true, opacity: .7 }));
scene.add(fanArcs, linkArcs);

const toWorld = ([x, y]) => [x * S * 1.25, -y * S];
let pos = null, height = new Float32Array(N), view = null, morph = null;

function paint() {
  const m = new THREE.Matrix4(), c = new THREE.Color(), base = COL[view.state.measure], sel = view.state.page;
  const top = new Set(view.top);
  for (let i = 0; i < N; i++) {
    m.makeScale(1, Math.max(0.04, height[i]), 1); m.setPosition(pos[i][0], 0, pos[i][1]);
    pillars.setMatrixAt(i, m);
    c.copy(base);
    if (sel != null && i !== sel && !view.related.has(i)) c.lerp(COL.dim, .7);
    else if (!top.has(i) && i !== sel) c.lerp(COL.dim, .25);
    if (i === sel) c.copy(COL.sel);
    pillars.setColorAt(i, c);
  }
  pillars.instanceMatrix.needsUpdate = true; pillars.instanceColor.needsUpdate = true;
}

function arc(from, to, h0, h1, out) {
  const [ax, az] = pos[from], [bx, bz] = pos[to], lift = Math.hypot(ax - bx, az - bz) * .3 + 1;
  let prev = [ax, h0, az];
  for (let s = 1; s <= 16; s++) {
    const t = s / 16, p = [ax + (bx - ax) * t, h0 + (h1 - h0) * t + Math.sin(Math.PI * t) * lift, az + (bz - az) * t];
    out.push(...prev, ...p); prev = p;
  }
}
function drawArcs() {
  const fans = [], links = [], sel = view.state.page;
  if (sel != null && !morph) {
    if (view.state.fans) for (const i of view.fans) arc(i, sel, height[i], height[sel], fans);
    if (view.state.links) for (const j of view.neighbours) arc(sel, j, height[sel], height[j], links);
  }
  fanArcs.geometry.setAttribute('position', new THREE.Float32BufferAttribute(fans, 3)); fanArcs.geometry.computeBoundingSphere();
  linkArcs.geometry.setAttribute('position', new THREE.Float32BufferAttribute(links, 3)); linkArcs.geometry.computeBoundingSphere();
}

// Labels for the tallest pillars and the selected page; one that would overlap a label already placed is hidden.
let labelEls = [];
function buildLabels() {
  labelsBox.replaceChildren();
  const ids = [...new Set([view.state.page, ...view.top].filter(i => i != null))];
  labelEls = ids.map(i => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'sky-label' + (i === view.state.page ? ' selected' : '');
    b.innerHTML = view.state.measure === 'random' ? `random point <span>${view.values[i]}</span>` : `${D.nodes[i].title.replace(/ \(.*\)$/, '')} <span>${view.values[i]}</span>`;
    b.onclick = () => app.select(i);
    labelsBox.append(b);
    return { el: b, i };
  });
}
const v3 = new THREE.Vector3();
function placeLabels() {
  const w = box.clientWidth, h = box.clientHeight, placed = [];
  for (const { el, i } of labelEls) {
    v3.set(pos[i][0], height[i] + 0.5, pos[i][1]).project(camera);
    const x = (v3.x + 1) / 2 * w, y = (1 - v3.y) / 2 * h, bw = el.offsetWidth, bh = el.offsetHeight, r = [x - bw / 2, y - bh, x + bw / 2, y];
    const hidden = v3.z > 1 || Math.abs(v3.x) > 1.1 || Math.abs(v3.y) > 1.1 || placed.some(q => r[0] < q[2] && r[2] > q[0] && r[1] < q[3] && r[3] > q[1]);
    if (!hidden) placed.push(r);
    el.style.visibility = hidden ? 'hidden' : 'visible';
    el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -100%)`;
  }
}

function render(next) {
  const first = !view;
  view = next;
  const targetPos = next.positions.map(toWorld), targetH = Float32Array.from(next.values, v => v * UNIT);
  if (first || !next.animate || reduced) { pos = targetPos; height = targetH; paint(); drawArcs(); buildLabels(); return; }
  const fromPos = pos.map(p => p.slice()), fromH = height.slice(), t0 = performance.now();
  labelsBox.replaceChildren(); labelEls = [];
  morph = now => {
    const t = Math.min(1, (now - t0) / 1000), e = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    pos = fromPos.map((p, i) => [p[0] + (targetPos[i][0] - p[0]) * e, p[1] + (targetPos[i][1] - p[1]) * e]);
    for (let i = 0; i < N; i++) height[i] = fromH[i] + (targetH[i] - fromH[i]) * e;
    paint();
    if (t >= 1) { morph = null; drawArcs(); buildLabels(); }
  };
  drawArcs();
}

// Pointer: hover shows a tooltip, a click (not a drag) selects the pillar.
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function pillarAt(e) {
  const r = renderer.domElement.getBoundingClientRect();
  ndc.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObject(pillars)[0];
  return hit ? hit.instanceId : null;
}
let down = null;
renderer.domElement.addEventListener('pointerdown', e => down = [e.clientX, e.clientY]);
renderer.domElement.addEventListener('pointerup', e => {
  if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
  const i = pillarAt(e);
  app.select(i);
});
renderer.domElement.addEventListener('pointermove', e => {
  if (e.buttons || !view) return;
  const i = pillarAt(e), r = box.getBoundingClientRect();
  if (i == null) { tip.hidden = true; renderer.domElement.style.cursor = ''; return; }
  renderer.domElement.style.cursor = 'pointer';
  tip.innerHTML = view.state.measure === 'random' ? `random point<small>stands in for ${D.nodes[i].title} · ${view.values[i]} ${view.unit}</small>` : `${D.nodes[i].title}<small>${view.values[i]} ${view.unit}</small>`;
  tip.style.left = e.clientX - r.left + 'px'; tip.style.top = e.clientY - r.top + 'px'; tip.hidden = false;
});
renderer.domElement.addEventListener('pointerleave', () => tip.hidden = true);

function resize() {
  const w = box.clientWidth, h = box.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.fov = Math.min(66, 36 * Math.max(1, 1.5 / camera.aspect));  // phones: widen the view so the whole map fits
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(box);
let visible = true;
new IntersectionObserver(([e]) => visible = e.isIntersecting).observe(box);
renderer.setAnimationLoop(now => {
  if (!visible || box.offsetParent === null) return;
  if (morph) morph(now);
  controls.update();
  renderer.render(scene, camera);
  placeLabels();
});

window.centreSky = {
  render,
  reset() { camera.position.copy(HOME); controls.target.set(0, 2.5, 0); controls.update(); },
  resize,
};
status.textContent = 'Drag to orbit · scroll or pinch to zoom · click a pillar';
app.ready();
