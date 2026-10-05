// Tokenlingo engine: learning path, lesson runner, cast and guidebook.
(function () {
  const UNITS = window.TL_UNITS;
  const CHARS = window.TL_CHARS;
  const GLOSSARY = window.TL_GLOSSARY;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const el = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const pick = (a) => a[Math.floor(Math.random() * a.length)];

  // ---------- icons ----------
  const ICONS = {
    star: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4l-5.8 3.1 1.1-6.5L2.6 9.4l6.5-.9z"/></svg>',
    check: '<svg class="ico" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.5l5 5L19.5 7"/></svg>',
    cross: '<svg class="ico" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>',
    lock: '<svg class="ico" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" rx="2.5" fill="currentColor"/><path d="M8 10.5V8a4 4 0 018 0v2.5" fill="none" stroke="currentColor" stroke-width="2.6"/></svg>',
    trophy: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M7 3h10v2h3v3a4 4 0 01-4 4h-.3A5 5 0 0113 14.9V18h3v3H8v-3h3v-3.1A5 5 0 018.3 12H8a4 4 0 01-4-4V5h3zm-1 4v1a2 2 0 002 2V7zm12 0v3a2 2 0 002-2V7z"/></svg>',
    flame: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2c1 3.5 5.5 6 5.5 11.2A5.6 5.6 0 0112 19a5.6 5.6 0 01-5.5-5.8c0-2.5 1.4-4.2 2.6-5.3.1 1.8.8 3 2 3.5C10.6 8 11.4 4.6 12 2z"/><path fill="#ffc800" d="M12 12c.6 1.4 2.4 2.3 2.4 4.4a2.4 2.4 0 01-4.8 0c0-1.3.8-2 1.6-2.6.1.6.4 1 .8 1.1-.3-1.2-.2-2.1 0-2.9z"/></svg>',
    bolt: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M13.5 2L4 13.5h6.5L9.5 22 20 9.5h-6.6z"/></svg>',
    heart: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M12 21s-8.5-5.3-8.5-11.4A4.8 4.8 0 0112 6.8a4.8 4.8 0 018.5 2.8C20.5 15.7 12 21 12 21z"/></svg>',
    target: '<svg class="ico" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="#ff4b4b"/><circle cx="12" cy="12" r="6" fill="#fff"/><circle cx="12" cy="12" r="3" fill="#ff4b4b"/></svg>',
    book: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M4 4.5A2.5 2.5 0 016.5 2H20v16H6.5a1 1 0 000 2H20v2H6.5A2.5 2.5 0 014 19.5z"/></svg>',
    chart: '<svg class="ico" viewBox="0 0 24 24"><rect x="3" y="12" width="4.5" height="9" rx="1.5" fill="currentColor"/><rect x="9.75" y="7" width="4.5" height="14" rx="1.5" fill="currentColor"/><rect x="16.5" y="3" width="4.5" height="18" rx="1.5" fill="currentColor"/></svg>',
    home: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M12 3l9 7.5V21h-6v-6H9v6H3V10.5z"/></svg>',
    cast: '<svg class="ico" viewBox="0 0 24 24"><circle cx="8" cy="9" r="4" fill="currentColor"/><circle cx="17" cy="10" r="3" fill="currentColor" opacity=".7"/><path fill="currentColor" d="M1.5 20a6.5 6.5 0 0113 0zM14 20a5 5 0 0110 0z"/></svg>',
    sound: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M4 9h4l5-4v14l-5-4H4z"/><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M16 8.5a5 5 0 010 7M18.5 6a8.5 8.5 0 010 12"/></svg>',
    mute: '<svg class="ico" viewBox="0 0 24 24"><path fill="currentColor" d="M4 9h4l5-4v14l-5-4H4z"/><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M16.5 9.5l5 5M21.5 9.5l-5 5"/></svg>',
  };
  const icon = (n) => ICONS[n] || "";

  // ---------- saved progress (per browser, optional) ----------
  const STORE = "tokenlingo-v1";
  const dayKey = (d = new Date()) => `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
  const state = load();
  function load() {
    let s = {};
    try { s = JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { s = {}; }
    return Object.assign({ done: {}, xp: 0, streak: 0, lastDay: null, muted: false, day: null, dayXp: 0, dayLessons: 0, dayCombo: 0 }, s);
  }
  function save() { try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* storage blocked: progress lasts this visit */ } }
  function rollDay() {
    const k = dayKey();
    if (state.day !== k) { state.day = k; state.dayXp = 0; state.dayLessons = 0; state.dayCombo = 0; }
    if (state.lastDay) {
      const y = new Date(); y.setDate(y.getDate() - 1);
      if (state.lastDay !== k && state.lastDay !== dayKey(y)) state.streak = 0;
    }
  }

  // ---------- sound ----------
  let audio = null;
  function tone(seq) {
    if (state.muted) return;
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      const t0 = audio.currentTime + 0.01;
      for (const [f, at, dur, type = "sine", vol = 0.16, f2] of seq) {
        const o = audio.createOscillator(), g = audio.createGain();
        o.type = type;
        o.frequency.setValueAtTime(f, t0 + at);
        if (f2) o.frequency.exponentialRampToValueAtTime(f2, t0 + at + dur);
        g.gain.setValueAtTime(0.0001, t0 + at);
        g.gain.exponentialRampToValueAtTime(vol, t0 + at + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + at + dur);
        o.connect(g).connect(audio.destination);
        o.start(t0 + at); o.stop(t0 + at + dur + 0.05);
      }
    } catch (e) { /* no audio available */ }
  }
  const SFX = {
    good: () => tone([[660, 0, 0.12], [990, 0.09, 0.25]]),
    bad: () => tone([[240, 0, 0.16, "square", 0.06], [190, 0.12, 0.26, "square", 0.06]]),
    win: () => tone([[523, 0, 0.16], [659, 0.13, 0.16], [784, 0.26, 0.16], [1047, 0.39, 0.5]]),
    tap: () => tone([[520, 0, 0.05, "triangle", 0.05]]),
    slash: () => tone([[1800, 0, 0.14, "sawtooth", 0.05, 300], [1500, 0.06, 0.14, "sawtooth", 0.04, 250]]),
    thwip: () => tone([[500, 0, 0.12, "triangle", 0.1, 1800]]),
    smash: () => tone([[110, 0, 0.3, "square", 0.08, 50], [70, 0.02, 0.35, "sawtooth", 0.06, 40]]),
    pew: () => tone([[1600, 0, 0.2, "sawtooth", 0.06, 180]]),
    sparkle: () => tone([[1320, 0, 0.08, "sine", 0.1], [1760, 0.07, 0.08, "sine", 0.1], [2093, 0.14, 0.14, "sine", 0.1]]),
    shrink: () => tone([[900, 0, 0.25, "sine", 0.1, 180], [180, 0.32, 0.25, "sine", 0.1, 1100]]),
    stamp: () => tone([[140, 0, 0.14, "triangle", 0.22, 60]]),
  };

  // ---------- lesson order ----------
  const FLAT = [];
  UNITS.forEach((u, ui) => u.lessons.forEach((l, li) => FLAT.push({ u, l, ui, li, key: `${u.id}.${l.id}` })));
  const isDone = (key) => !!state.done[key];
  const nextKey = () => (FLAT.find((f) => !isDone(f.key)) || {}).key;
  const unlocked = (i) => i === 0 || FLAT[i].u.id === "data" || isDone(FLAT[i - 1].key) || isDone(FLAT[i].key);

  // ---------- header stats ----------
  function renderStats() {
    rollDay();
    const s = $("#stat-streak");
    s.innerHTML = `${icon("flame")}<span>${state.streak}</span>`;
    s.classList.toggle("cold", state.lastDay !== dayKey());
    s.title = `${state.streak}-day streak`;
    $("#stat-xp").innerHTML = `${icon("bolt")}<span>${state.xp} XP</span>`;
    const st = $("#sound-toggle");
    st.innerHTML = icon(state.muted ? "mute" : "sound");
    st.setAttribute("aria-label", state.muted ? "Turn sound on" : "Turn sound off");
    renderQuests();
  }

  function renderQuests() {
    const q = [
      ["Earn 30 XP", state.dayXp, 30, "bolt", "var(--gold)"],
      ["Finish 2 lessons", state.dayLessons, 2, "target", ""],
      ["Get 5 right in a row", state.dayCombo, 5, "flame", "var(--orange)"],
    ];
    $("#quests").innerHTML = `<h3>Daily quests</h3>` + q.map(([t, v, max, ic, col]) => {
      const p = Math.min(1, v / max);
      return `<div class="quest"><span style="color:${col}">${icon(ic)}</span><strong>${t}</strong>
        <div class="qbar ${p >= 1 ? "full" : ""}"><span style="width:${p * 100}%"></span><em>${Math.min(v, max)} / ${max}</em></div></div>`;
    }).join("");
  }

  const FACTS = [
    ["fury", "36% of the ~27,000 word types in the full Marvel pages occur exactly once.", "Section 3"],
    ["hulk", "In a 28-token corpus about Iron Man, the top two types are 'the' and '.'. That's English, not superheroes.", "Section 3"],
    ["wolverine", "Kuuk Thaayorre speakers lay out time from east to west, whichever way they sit.", "Section 1"],
    ["ironman", "With raw counts, Quicksilver is Wolverine's second-closest page. Blame 'the', 'and' and 'of'.", "Section 5"],
    ["loki", "The full Marvel document-term matrix has ~27,000 columns, and almost every cell is zero.", "Section 4"],
    ["spidey", "'New York' means more than 'New' and 'York' counted separately. That's what n-grams keep.", "Section 3"],
    ["wolverine", "95% of the 'men' tokens in Marvel's Wikipedia pages are names, and 1,500 of them are X-Men.", "Our finding"],
    ["hulk", "After 'she', the second most common word in the Marvel pages is 'hulk'. Blame She-Hulk's hyphen.", "Our finding"],
    ["ironman", "The rarest half of Marvel's vocabulary is only 2.4% of the text. The top 50 words are 39.5%.", "Our finding"],
  ];
  function renderFact() {
    const [c, text, sec] = pick(FACTS);
    $("#fact").innerHTML = `<h3>Did you know?</h3><div class="fact"><div class="alive">${CHARS[c].svg("happy")}</div><p>${text}<small>${CHARS[c].name} · ${sec.startsWith("Section") ? `Week 5, ${sec}` : sec}</small></p></div>`;
  }

  // ---------- comic bursts ----------
  const STAR = "polygon(" + Array.from({ length: 24 }, (_, k) => {
    const a = (k / 24) * Math.PI * 2, r = k % 2 ? 35 : 50;
    return `${(50 + r * Math.cos(a)).toFixed(1)}% ${(50 + r * Math.sin(a)).toFixed(1)}%`;
  }).join(",") + ")";
  document.documentElement.style.setProperty("--star", STAR);
  const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  // A starburst with a sound-effect word, centred on (x, y) inside `box`.
  function burst(box, text, x, y, color, rot = -8) {
    const b = el(`<div class="burst" style="left:${x}px;top:${y}px;--bc:${color}"><span>${text}</span></div>`);
    box.append(b);
    b.animate([
      { transform: `scale(0) rotate(${rot - 30}deg)`, opacity: 0 },
      { transform: `scale(1.2) rotate(${rot}deg)`, opacity: 1, offset: 0.22 },
      { transform: `scale(1) rotate(${rot}deg)`, opacity: 1, offset: 0.36 },
      { transform: `scale(1) rotate(${rot}deg)`, opacity: 1, offset: 0.82 },
      { transform: `scale(.85) rotate(${rot}deg)`, opacity: 0 },
    ], { duration: 1150, easing: "ease-out", fill: "forwards" });
    setTimeout(() => b.remove(), 1200);
  }

  // Three claw marks that rip across a point.
  function claws3(box, x, y, len) {
    [-20, 0, 20].forEach((off, i) => {
      const c = el(`<div class="claw" style="left:${x - len / 2}px;top:${y + off}px;width:${len}px"></div>`);
      box.append(c);
      c.animate([
        { transform: "rotate(-18deg) scaleX(0)", opacity: 1 },
        { transform: "rotate(-18deg) scaleX(1)", opacity: 1, offset: 0.45 },
        { transform: "rotate(-18deg) scaleX(1)", opacity: 0 },
      ], { duration: 480, delay: i * 55, easing: "ease-out", fill: "both" });
      setTimeout(() => c.remove(), 700);
    });
  }

  // ---------- opening stage: text → tokens → numbers ----------
  const STAGE_TOKENS = ["Loki", "tricks", "Thor", "and", "Thor", "tricks", "Loki"];
  const STAGE_VOCAB = ["and", "loki", "thor", "tricks"];
  const STAGE_COUNTS = STAGE_VOCAB.map((v) => STAGE_TOKENS.filter((t) => t.toLowerCase() === v).length);
  const BAG = `<svg viewBox="0 0 80 80" role="img" aria-label="A bag of words"><path d="M17 30 Q6 77 40 77 Q74 77 63 30 Z" fill="#43a047"/><path d="M57 31 Q66 60 58 72 Q70 66 70 50 Q69 38 63 30 Z" fill="#2e7d32"/><ellipse cx="40" cy="29" rx="24" ry="6.5" fill="#1b5e20"/><path d="M20 36 Q40 45 60 36" fill="none" stroke="#ffc800" stroke-width="3.2" stroke-linecap="round"/><text x="40" y="63" text-anchor="middle" font-family="Nunito, system-ui, sans-serif" font-weight="900" font-size="13" fill="#fff">BoW</text></svg>`;
  let introStarted = false, introRun = 0;

  function stageEl() {
    const s = el(`<section class="stage" aria-label="Week 5 in one sentence">
      <p class="stage-kicker">Week 5 · From language to numbers</p>
      <div class="stage-text">${STAGE_TOKENS.map((t) => `<span class="tok">${t}</span>`).join("")}</div>
      <div class="stage-floor">
        <div class="stage-hero stage-wolverine"></div>
        <div class="stage-mid">
          <div class="stage-bag">${BAG}</div>
          <div class="stage-vec" aria-label="Count vector: ${STAGE_VOCAB.map((v, i) => `${v} ${STAGE_COUNTS[i]}`).join(", ")}"><span class="br">[</span>${STAGE_VOCAB.map((v) => `<span class="vcell2"><b>${v}</b><output>0</output></span>`).join("")}<span class="br">]</span></div>
        </div>
        <div class="stage-hero stage-loki"></div>
      </div>
      <p class="stage-cap">Text → tokens → numbers. <span>Word order didn't survive the bag.</span></p>
      <button class="stage-replay" type="button">↻ Replay</button>
      <div class="stage-fx" aria-hidden="true"></div>
    </section>`);
    $(".stage-replay", s).addEventListener("click", () => playIntro(s));
    return s;
  }

  function setStageHero(s, who, expr) {
    $(`.stage-${who}`, s).innerHTML = `<div class="alive">${CHARS[who].svg(expr)}</div>`;
  }

  function stageRest(s) {
    s.classList.add("rest");
    $(".stage-text", s).classList.add("cut");
    $$(".tok", s).forEach((t) => { t.getAnimations().forEach((a) => a.cancel()); t.style.transform = ""; });
    $(".stage-wolverine", s).classList.remove("off");
    $(".stage-loki", s).classList.remove("off");
    $(".stage-bag", s).classList.remove("show");
    $(".stage-vec", s).classList.add("show");
    $$(".vcell2 output", s).forEach((o, i) => (o.textContent = STAGE_COUNTS[i]));
    setStageHero(s, "wolverine", "idle");
    setStageHero(s, "loki", "idle");
  }

  async function playIntro(s) {
    introStarted = true;
    const run = ++introRun;
    if (reducedMotion()) return stageRest(s);
    const live = () => run === introRun && s.isConnected && !s.closest("[hidden]");
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const text = $(".stage-text", s), bag = $(".stage-bag", s), vec = $(".stage-vec", s), fx = $(".stage-fx", s);
    const toks = $$(".tok", s), outs = $$(".vcell2 output", s);
    const wolv = $(".stage-wolverine", s), loki = $(".stage-loki", s);

    // Start: one plain sentence, heroes off stage.
    s.classList.remove("rest");
    text.classList.remove("cut");
    toks.forEach((t) => { t.getAnimations().forEach((a) => a.cancel()); t.style.transform = ""; });
    vec.classList.remove("show");
    bag.classList.remove("show");
    outs.forEach((o) => (o.textContent = "0"));
    fx.innerHTML = "";
    setStageHero(s, "wolverine", "idle");
    setStageHero(s, "loki", "idle");
    wolv.classList.add("off");
    loki.classList.add("off");

    // Wolverine runs in and slices the sentence into tokens.
    await wait(450); if (!live()) return;
    wolv.classList.remove("off");
    await wait(620); if (!live()) return;
    setStageHero(s, "wolverine", "happy");
    const sr = s.getBoundingClientRect(), tr = text.getBoundingClientRect();
    claws3(fx, tr.left - sr.left + tr.width / 2, tr.top - sr.top + tr.height / 2, tr.width + 40);
    burst(fx, "SNIKT!", Math.min(tr.right - sr.left + 10, sr.width - 64), tr.top - sr.top + 6, "#1f4fbf", -10);
    SFX.slash();
    await wait(330); if (!live()) return;
    text.classList.add("cut");
    toks.forEach((t) => (t.style.transform = `rotate(${(Math.random() * 12 - 6).toFixed(1)}deg) translateY(${(Math.random() * 6 - 3).toFixed(1)}px)`));
    await wait(950); if (!live()) return;

    // Loki arrives with the bag and every token flies in.
    loki.classList.remove("off");
    await wait(450); if (!live()) return;
    bag.classList.add("show");
    setStageHero(s, "loki", "happy");
    await wait(480); if (!live()) return;
    const b = bag.getBoundingClientRect();
    const bx = b.left + b.width / 2, by = b.top + b.height * 0.36;
    toks.forEach((t, i) => {
      const r = t.getBoundingClientRect();
      const dx = bx - (r.left + r.width / 2), dy = by - (r.top + r.height / 2);
      const base = t.style.transform || "none", spin = i % 2 ? 1 : -1;
      t.animate([
        { transform: base, opacity: 1 },
        { transform: `translate(${dx * 0.45}px, ${dy * 0.45 - 46}px) rotate(${160 * spin}deg) scale(.75)`, opacity: 1, offset: 0.55 },
        { transform: `translate(${dx}px, ${dy}px) rotate(${320 * spin}deg) scale(.15)`, opacity: 0 },
      ], { duration: 640, delay: i * 120, easing: "ease-in", fill: "forwards" });
      setTimeout(() => {
        if (!live()) return;
        bag.animate([{ transform: "scale(1)" }, { transform: "scale(1.14, .88) rotate(-6deg)" }, { transform: "scale(1)" }], { duration: 220 });
        SFX.tap();
      }, 600 + i * 120);
    });
    await wait(640 + toks.length * 120 + 120); if (!live()) return;
    bag.animate([{ transform: "scale(1)" }, { transform: "scale(1.15) rotate(9deg)" }, { transform: "scale(1.15) rotate(-9deg)" }, { transform: "scale(1)" }], { duration: 420 });
    await wait(440); if (!live()) return;

    // Out comes a count vector.
    bag.classList.remove("show");
    vec.classList.add("show");
    SFX.good();
    for (let k = 1; k <= Math.max(...STAGE_COUNTS); k++) {
      await wait(280); if (!live()) return;
      outs.forEach((o, i) => {
        if (STAGE_COUNTS[i] < k) return;
        o.textContent = k;
        o.animate([{ transform: "scale(1.6)" }, { transform: "scale(1)" }], { duration: 260, easing: "ease-out" });
      });
      SFX.tap();
    }
    await wait(300); if (!live()) return;

    // Rest: tokens back on top, vector below, caption and replay.
    toks.forEach((t) => {
      t.getAnimations().forEach((a) => a.cancel());
      t.style.transform = "";
      t.animate([{ opacity: 0, transform: "translateY(-8px)" }, { opacity: 1, transform: "none" }], { duration: 360, easing: "ease-out" });
    });
    s.classList.add("rest");
    await wait(1700); if (!live()) return;
    setStageHero(s, "wolverine", "idle");
    setStageHero(s, "loki", "idle");
  }

  // ---------- learn path ----------
  const OFFSETS = [0, 52, 78, 52, 0, -52, -78, -52];
  function renderPath() {
    const view = $("#view-learn");
    view.innerHTML = "";
    const stage = stageEl();
    view.append(stage);
    const nk = nextKey();
    let flatIndex = 0;
    UNITS.forEach((u, ui) => {
      const flip = ui % 2 ? -1 : 1;
      const light = u.id === "u5";
      const sec = el(`<section class="unit ${light ? "u-light" : ""}" id="unit-${u.id}" style="--u:${u.color};--u-dark:${u.dark}">
        <header class="unit-banner">
          <div><p class="unit-kicker">Unit ${ui + 1} · ${u.section}</p><h2>${u.title}</h2></div>
          ${GLOSSARY[u.id] ? `<button class="guide-btn" type="button" data-guide="${u.id}">${icon("book")}<span>Guidebook</span></button>` : ""}
        </header>
        <div class="unit-path"></div>
      </section>`);
      const path = $(".unit-path", sec);
      const cast = [u.char, ...new Set(u.lessons.map((l) => l.char).filter(Boolean))];
      path.append(el(`<div class="unit-char alive ${flip > 0 ? "left" : "right"}" style="animation-delay:-${(Math.random() * 3).toFixed(2)}s">${CHARS[cast[0]].svg(isDone(`${u.id}.${u.lessons[0].id}`) ? "happy" : "idle")}</div>`));
      u.lessons.forEach((l, li) => {
        const i = flatIndex++;
        const key = `${u.id}.${l.id}`;
        const done = isDone(key), open = unlocked(i), isNext = key === nk;
        const off = l.legend ? 0 : OFFSETS[li % OFFSETS.length] * flip;
        const cls = ["node", done ? "done" : "", open ? "" : "locked", isNext ? "next" : "", l.legend ? "legend" : ""].join(" ");
        const ic = l.legend ? "trophy" : done ? "check" : open ? "star" : "lock";
        const row = el(`<div class="node-row" style="--x:${off}px">
          ${isNext ? `<div class="start-bubble">${done ? "Again" : "Start"}</div>` : ""}
          <button class="${cls}" type="button" aria-label="${esc(l.title)}${done ? ", completed" : open ? "" : ", locked"}">${icon(ic)}</button>
        </div>`);
        $("button", row).addEventListener("click", () => togglePop(row, u, l, { done, open, i, ui, li }));
        path.append(row);
      });
      view.append(sec);
    });
    $$("[data-guide]", view).forEach((b) => b.addEventListener("click", () => go("guide", b.dataset.guide)));
    if (introStarted) stageRest(stage); else playIntro(stage);
  }

  function togglePop(row, u, l, info) {
    const had = $(".pop", row);
    $$(".pop").forEach((p) => p.remove());
    if (had) return;
    SFX.tap();
    const total = u.lessons.length;
    const pop = el(`<div class="pop ${info.open ? "" : "locked"}">
      <h3>${esc(l.title)}</h3>
      <p>${info.open ? esc(l.desc) : "Finish the lessons before this one to unlock it, or jump ahead."}</p>
      <button class="btn ${info.open ? "btn-white" : "btn-ghost"}" type="button" style="--btn-ink:${u.dark}">
        ${info.open ? (info.done ? "Practice +5 XP" : `Start +${l.legend ? 30 : 10} XP`) : "Jump here"}
      </button>
    </div>`);
    if (!l.legend) $("p", pop).insertAdjacentHTML("beforebegin", `<p style="margin:2px 0 0;font-size:.8rem;opacity:.8">Lesson ${info.li + 1} of ${total}</p>`);
    $("button", pop).addEventListener("click", () => startLesson(u, l));
    row.append(pop);
    pop.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".node-row")) $$(".pop").forEach((p) => p.remove());
  });

  // ---------- cast ----------
  const CAST_ORDER = ["wolverine", "antman", "hulk", "fury", "spidey", "loki", "ironman"];
  function renderCast() {
    const v = $("#view-cast");
    v.innerHTML = `<div class="page-head"><h1>Meet the cast</h1><p>Seven heroes from the Marvel network you have studied since week 1, each standing for one Week 5 idea. Tap a hero to see how they react to your answers.</p></div><div class="cast-grid"></div>`;
    const grid = $(".cast-grid", v);
    const moods = ["idle", "happy", "think", "sad"];
    CAST_ORDER.forEach((id) => {
      const c = CHARS[id];
      const card = el(`<button type="button" class="cast-card" style="--cc:${c.color};--cd:${c.dark}">
        <div class="cast-art"><div class="alive" style="animation-delay:-${(Math.random() * 3).toFixed(2)}s">${c.svg("idle")}</div></div>
        <div class="cast-info"><span class="cast-role">${c.role}</span><h2>${c.name}</h2><p>${c.teaches}</p><blockquote>${esc(c.quote)}</blockquote></div>
      </button>`);
      let m = 0;
      card.addEventListener("click", () => { m = (m + 1) % moods.length; $(".cast-art .alive", card).innerHTML = c.svg(moods[m]); SFX.tap(); });
      grid.append(card);
    });
  }

  // ---------- guidebook ----------
  function renderGuide() {
    const v = $("#view-guide");
    v.innerHTML = `<div class="page-head"><h1>Guidebook</h1><p>The Week 5 essentials, unit by unit. This is the closed-book core for Test 2.</p></div>`;
    UNITS.filter((u) => GLOSSARY[u.id]).forEach((u, i) => {
      v.append(el(`<section class="guide-unit" id="guide-${u.id}" style="border-top:6px solid ${u.color}">
        <header>${CHARS[u.char].svg("think")}<div><p>Unit ${i + 1} · ${u.section}</p><h2>${u.title}</h2></div></header>
        <dl>${GLOSSARY[u.id].map(([t, d]) => `<div><dt>${t}</dt><dd>${d}</dd></div>`).join("")}</dl>
      </section>`));
    });
  }

  // ---------- views ----------
  function go(view, anchor) {
    for (const name of ["learn", "cast", "guide"]) $(`#view-${name}`).hidden = name !== view;
    $$(".nav-item").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
    if (view === "cast") renderCast();
    if (view === "guide") renderGuide();
    if (view === "learn") renderPath();
    if (anchor) {
      const t = $(`#guide-${anchor}`);
      if (t) { t.scrollIntoView({ behavior: "smooth", block: "start" }); t.classList.add("flash"); }
    } else window.scrollTo(0, 0);
    if (location.hash !== `#${view}`) history.replaceState(null, "", `#${view}`);
  }
  $$("[data-view]").forEach((a) => a.addEventListener("click", (e) => { e.preventDefault(); go(a.dataset.view); }));

  // ---------- lesson runner ----------
  let L = null;

  function buildLegend() {
    const pool = [];
    UNITS.forEach((u) => u.lessons.forEach((l) => (l.ex || []).forEach((e) => {
      if (e.type !== "match") pool.push({ ...e, char: e.char || l.char || u.char });
    })));
    const byChar = {};
    shuffle(pool).forEach((e) => (byChar[e.char] = byChar[e.char] || []).push(e));
    const picked = [];
    Object.values(byChar).forEach((list) => picked.push(list[0]));
    shuffle(pool).forEach((e) => { if (picked.length < 10 && !picked.includes(e)) picked.push(e); });
    return shuffle(picked.slice(0, 10));
  }

  function startLesson(unit, lesson) {
    const ex = lesson.legend ? buildLegend() : lesson.ex.map((e) => ({ ...e }));
    L = { unit, lesson, queue: ex, total: ex.length, pos: 0, right: 0, hearts: 5, combo: 0, best: 0, mistakes: 0, answered: false, handler: null };
    $$(".pop").forEach((p) => p.remove());
    $("#lesson").hidden = false;
    document.body.style.overflow = "hidden";
    renderTop();
    renderEx();
  }

  function closeLesson() {
    $("#lesson").hidden = true;
    $("#sheet").hidden = true;
    document.body.style.overflow = "";
    L = null;
    renderStats();
    go("learn");
    const n = $(".node.next");
    if (n) n.scrollIntoView({ block: "center" });
  }

  function renderTop() {
    const p = L.right / L.total;
    $("#l-bar").style.width = `${p * 100}%`;
    $(".l-progress").setAttribute("aria-valuenow", Math.round(p * 100));
    $("#l-hearts").innerHTML = `${icon("heart")}<span>${L.hearts}</span>`;
    const c = $("#l-combo");
    c.textContent = L.combo >= 3 ? `${L.combo} in a row` : "";
    c.classList.toggle("on", L.combo >= 3);
  }

  function speakerChar(cur) { return CHARS[cur.char || L.lesson.char || L.unit.char]; }

  function renderEx() {
    const cur = L.queue[L.pos];
    const ch = speakerChar(cur);
    L.answered = false;
    const body = $("#l-body");
    const say = cur.say || pick(ch.lines);
    body.innerHTML = `
      ${cur.retry ? `<p style="color:var(--orange);font-weight:900;letter-spacing:.06em;text-transform:uppercase;font-size:.85rem;margin-bottom:8px">Previous mistake</p>` : ""}
      <h2 class="l-q">${esc(cur.q)}</h2>
      <div class="speaker"><div class="speaker-art alive">${ch.svg("idle")}</div><div class="bubble">${esc(say)}</div></div>
      ${cur.visual || ""}
      <div class="answer" id="answer"></div>`;
    const foot = $("#l-foot");
    foot.className = "l-foot";
    $("#l-feedback").innerHTML = "";
    const check = $("#l-check");
    check.textContent = "Check";
    check.disabled = true;
    L.handler = TYPES[cur.type](cur, $("#answer"), (ok) => { if (!L.answered) check.disabled = !ok; });
    $(".l-scroll").scrollTop = 0;
    fxBox().innerHTML = "";
  }

  // ---------- signature moves ----------
  const fxBox = () => $("#fx");
  function addFx(html) { const n = el(html); fxBox().append(n); return n; }
  function handPoint() {
    const r = $(".speaker-art").getBoundingClientRect();
    return [r.left + r.width * 0.81, r.top + r.height * 0.37];
  }
  function targetPoint() {
    const t = $("#answer .opt.right") || $("#answer");
    const r = t.getBoundingClientRect();
    const y = Math.min(Math.max(r.top + Math.min(r.height / 2, 60), 90), innerHeight - 170);
    return [Math.min(Math.max(r.left + r.width / 2, 70), innerWidth - 70), y];
  }
  function beam(cls, d, fade = 900) {
    const svg = addFx(`<svg class="fx-svg" aria-hidden="true">${d}</svg>`);
    $$(`.${cls}`, svg).forEach((p) => p.animate([{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }], { duration: 230, easing: "ease-out", fill: "forwards" }));
    setTimeout(() => svg.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 380, fill: "forwards" }), fade);
    setTimeout(() => svg.remove(), fade + 420);
    return svg;
  }

  const MOVES = {
    spidey() {
      const [x1, y1] = handPoint(), [x2, y2] = targetPoint();
      const ring = (r) => Array.from({ length: 9 }, (_, k) => `${k ? "L" : "M"}${(x2 + Math.cos(k * Math.PI / 4) * r).toFixed(1)} ${(y2 + Math.sin(k * Math.PI / 4) * r).toFixed(1)}`).join(" ");
      const spokes = Array.from({ length: 8 }, (_, k) => `M${x2} ${y2} L${(x2 + Math.cos(k * Math.PI / 4) * 20).toFixed(1)} ${(y2 + Math.sin(k * Math.PI / 4) * 20).toFixed(1)}`).join(" ");
      const svg = beam("web-line", `<path class="web-line" pathLength="1" d="M${x1} ${y1} Q${(x1 + x2) / 2} ${Math.max(y1, y2) + 36} ${x2} ${y2}"/><path class="web-splat" style="transform-origin:${x2}px ${y2}px" d="${spokes} ${ring(9)} ${ring(16)}"/>`);
      $(".web-splat", svg).animate([{ transform: "scale(0)" }, { transform: "scale(1)" }], { duration: 220, delay: 200, fill: "backwards", easing: "cubic-bezier(.3,1.6,.5,1)" });
      burst(fxBox(), "THWIP!", Math.min(x2 + 90, innerWidth - 64), y2 - 34, "#e23636", 8);
      SFX.thwip();
    },
    hulk() {
      const bar = $(".l-progress"), r = bar.getBoundingClientRect();
      burst(fxBox(), "SMASH!", r.left + r.width * 0.5, r.bottom + 46, "#7b3fa0", -6);
      bar.animate([{ transform: "none" }, { transform: "translateY(6px) scaleY(1.6)" }, { transform: "translateY(-3px)" }, { transform: "none" }], { duration: 380 });
      $(".l-scroll").animate([{ transform: "none" }, { transform: "translate(-6px, 3px)" }, { transform: "translate(6px, -3px)" }, { transform: "translate(-3px, 2px)" }, { transform: "none" }], { duration: 330 });
      SFX.smash();
    },
    wolverine() {
      const [x, y] = targetPoint();
      claws3(fxBox(), x, y, Math.min(340, innerWidth * 0.8));
      burst(fxBox(), "SNIKT!", Math.min(x + 120, innerWidth - 64), y - 54, "#1f4fbf", -10);
      SFX.slash();
    },
    ironman() {
      const [x1, y1] = handPoint(), [x2, y2] = targetPoint();
      const line = `x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" pathLength="1"`;
      const svg = beam("beam", `<line class="beam beam-glow" ${line}/><line class="beam" ${line}/><circle class="blast" cx="${x2}" cy="${y2}" r="24" style="transform-origin:${x2}px ${y2}px"/>`, 520);
      $(".blast", svg).animate([{ transform: "scale(0)", opacity: 1 }, { transform: "scale(1.4)", opacity: 0 }], { duration: 480, delay: 200, fill: "both", easing: "ease-out" });
      burst(fxBox(), "PEW!", Math.min(x2 + 90, innerWidth - 64), y2 - 36, "#c62828", 7);
      SFX.pew();
    },
    loki() {
      const [x, y] = targetPoint();
      for (let i = 0; i < 18; i++) {
        const a = (i / 18) * Math.PI * 2 + Math.random() * 0.3, d = 50 + Math.random() * 70;
        const sp = addFx(`<i class="spark" style="left:${x}px;top:${y}px;background:${i % 3 ? "#43a047" : "#ffc800"}"></i>`);
        sp.animate([
          { transform: "translate(-50%,-50%) scale(.4) rotate(0deg)", opacity: 1 },
          { transform: `translate(calc(-50% + ${Math.cos(a) * d}px), calc(-50% + ${Math.sin(a) * d}px)) scale(1) rotate(180deg)`, opacity: 1, offset: 0.6 },
          { transform: `translate(calc(-50% + ${Math.cos(a) * d * 1.2}px), calc(-50% + ${Math.sin(a) * d * 1.2 + 12}px)) scale(.3) rotate(270deg)`, opacity: 0 },
        ], { duration: 900, easing: "ease-out", fill: "forwards" });
        setTimeout(() => sp.remove(), 950);
      }
      burst(fxBox(), "TA-DA!", Math.min(x + 100, innerWidth - 64), y - 40, "#43a047", 8);
      SFX.sparkle();
    },
    antman() {
      $(".speaker-art").animate([
        { transform: "scale(1)" }, { transform: "scale(.22)", offset: 0.35 }, { transform: "scale(.22)", offset: 0.55 },
        { transform: "scale(1.18)", offset: 0.8 }, { transform: "scale(1)" },
      ], { duration: 950, easing: "ease-in-out" });
      const [x, y] = targetPoint();
      burst(fxBox(), "TINY!", Math.min(x + 100, innerWidth - 64), y - 40, "#e53935", 6);
      SFX.shrink();
    },
    fury() {
      const [x, y] = targetPoint();
      const st = addFx(`<div class="stamp" style="left:${x}px;top:${y}px">Cleared</div>`);
      st.animate([
        { transform: "translate(-50%,-50%) rotate(-12deg) scale(2.6)", opacity: 0 },
        { transform: "translate(-50%,-50%) rotate(-12deg) scale(.94)", opacity: 1, offset: 0.25 },
        { transform: "translate(-50%,-50%) rotate(-12deg) scale(1)", opacity: 1, offset: 0.82 },
        { transform: "translate(-50%,-50%) rotate(-12deg) scale(1)", opacity: 0 },
      ], { duration: 1300, easing: "ease-out", fill: "forwards" });
      setTimeout(() => st.remove(), 1350);
      SFX.stamp();
    },
  };

  function signature(id) {
    if (reducedMotion() || !MOVES[id]) return;
    try { MOVES[id](); } catch (e) { /* effects are decoration; never block the lesson */ }
  }

  // Loki taunts a wrong answer by shuffling the options in place.
  function lokiTaunt() {
    if (reducedMotion()) return;
    const list = $("#answer .options");
    if (!list) return;
    const items = $$(".opt", list);
    const before = new Map(items.map((o) => [o, o.getBoundingClientRect().top]));
    shuffle(items).forEach((o) => list.append(o));
    items.forEach((o) => {
      const dy = before.get(o) - o.getBoundingClientRect().top;
      if (dy) o.animate([{ transform: `translateY(${dy}px)` }, { transform: "none" }], { duration: 460, easing: "cubic-bezier(.3,1.3,.5,1)" });
    });
    const r = list.getBoundingClientRect();
    burst(fxBox(), "HA!", Math.min(r.right - 30, innerWidth - 64), r.top - 6, "#43a047", 10);
  }

  function setExpr(expr) {
    const art = $(".speaker-art");
    if (!art) return;
    art.innerHTML = speakerChar(L.queue[L.pos]).svg(expr, expr === "happy" ? "react-happy" : expr === "sad" ? "react-sad" : "");
  }

  function resolve(res) {
    const cur = L.queue[L.pos];
    L.answered = true;
    $("#answer").classList.add("locked-input");
    const foot = $("#l-foot");
    const check = $("#l-check");
    if (res.ok) {
      L.right++; L.combo++; L.best = Math.max(L.best, L.combo);
      SFX.good(); setExpr("happy");
      signature(speakerChar(cur).id);
      foot.className = "l-foot ok";
      const praise = L.combo >= 5 ? `${L.combo} in a row!` : pick(["Nice!", "Great job!", "Correct!", "Amazing!", "You got it!"]);
      $("#l-feedback").innerHTML = `<span class="fb-ico">${icon("check")}</span><div><h3>${praise}</h3>${cur.why ? `<p>${esc(cur.why)}</p>` : ""}</div>`;
    } else {
      L.hearts--; L.mistakes++; L.combo = 0;
      SFX.bad(); setExpr("sad");
      if (speakerChar(cur).id === "loki") lokiTaunt();
      $("#l-hearts").classList.remove("hit"); void $("#l-hearts").offsetWidth; $("#l-hearts").classList.add("hit");
      L.queue.push({ ...cur, retry: true });
      foot.className = "l-foot bad";
      $("#l-feedback").innerHTML = `<span class="fb-ico">${icon("cross")}</span><div><h3>Correct answer:</h3><p class="fb-answer">${esc(res.correct)}</p>${cur.why ? `<p>${esc(cur.why)}</p>` : ""}</div>`;
    }
    check.disabled = false;
    check.textContent = res.ok ? "Continue" : "Got it";
    check.focus({ preventScroll: true });
    renderTop();
  }

  function onCheck() {
    if (!L) return;
    if (L.answered) return advance();
    const res = L.handler.check();
    if (res) resolve(res);
  }

  function advance() {
    L.pos++;
    if (L.hearts <= 0) return outOfHearts();
    if (L.pos >= L.queue.length) return finish();
    renderEx();
  }

  function finish() {
    fxBox().innerHTML = "";
    rollDay();
    const key = `${L.unit.id}.${L.lesson.id}`;
    const first = !isDone(key);
    const gained = L.lesson.legend ? 30 : first ? 10 + (L.mistakes === 0 ? 5 : 0) : 5;
    state.done[key] = true;
    state.xp += gained; state.dayXp += gained; state.dayLessons++;
    state.dayCombo = Math.max(state.dayCombo, L.best);
    if (state.lastDay !== dayKey()) { state.streak += 1; state.lastDay = dayKey(); }
    save();
    SFX.win();
    const acc = Math.round((L.right / (L.right + L.mistakes)) * 100);
    const ch = CHARS[L.lesson.char || L.unit.char];
    $("#l-body").innerHTML = `<div class="finish">
      ${L.lesson.legend ? `<div class="cast-parade">${CAST_ORDER.map((id, i) => CHARS[id].svg("happy").replace('class="char ', `style="animation-delay:${i * 0.08}s" class="char `)).join("")}</div>` : ch.svg("happy", "react-happy")}
      <h2>${L.lesson.legend ? "Week 5 is Legendary!" : "Lesson complete!"}</h2>
      <p>${L.lesson.legend ? "Tokens, counts, context and bags. You're ready for the language half of Test 2." : esc(`${ch.name}: ${ch.quote}`)}</p>
      <div class="tiles3">
        <div class="stat-tile" style="--tc:var(--gold)"><b>Total XP</b><span>${icon("bolt")}${gained}</span></div>
        <div class="stat-tile" style="--tc:var(--green)"><b>${acc === 100 ? "Perfect" : "Accuracy"}</b><span>${icon("target")}${acc}%</span></div>
        <div class="stat-tile" style="--tc:var(--orange)"><b>Best streak</b><span>${icon("flame")}${L.best}</span></div>
      </div>
      ${L.lesson.link ? `<a class="btn btn-blue finish-link" href="${L.lesson.link.href}" target="_blank" rel="noopener">${esc(L.lesson.link.label)} ↗</a>` : ""}
    </div>`;
    confetti();
    $("#l-foot").className = "l-foot";
    $("#l-feedback").innerHTML = "";
    const check = $("#l-check");
    check.textContent = "Continue"; check.disabled = false;
    L.answered = true;
    L.pos = Infinity;
    check.focus({ preventScroll: true });
    $("#l-bar").style.width = "100%";
    L.done = true;
  }

  function outOfHearts() {
    fxBox().innerHTML = "";
    L.done = true;
    $("#l-body").innerHTML = `<div class="finish sad">${CHARS.hulk.svg("sad", "react-sad")}
      <h2>Out of hearts</h2><p>Mistakes are how this works. Every one you made comes back as a question, so try again with five fresh hearts.</p></div>`;
    $("#l-foot").className = "l-foot";
    $("#l-feedback").innerHTML = `<button class="btn btn-ghost" type="button" id="l-retry">Try again</button>`;
    $("#l-retry").addEventListener("click", () => startLesson(L.unit, L.lesson));
    const check = $("#l-check");
    check.textContent = "Back to path"; check.disabled = false;
    L.answered = true; L.pos = Infinity;
  }

  function confetti() {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const box = el(`<div class="confetti" aria-hidden="true"></div>`);
    const cols = ["#58cc02", "#1cb0f6", "#ff9600", "#ce82ff", "#ffc800", "#ff4b4b", "#ff86d0"];
    for (let i = 0; i < 70; i++) {
      const p = document.createElement("i");
      p.style.left = `${Math.random() * 100}%`;
      p.style.background = pick(cols);
      p.style.animationDuration = `${1.6 + Math.random() * 1.8}s`;
      p.style.animationDelay = `${Math.random() * 0.5}s`;
      p.style.transform = `rotate(${Math.random() * 360}deg)`;
      box.append(p);
    }
    document.body.append(box);
    setTimeout(() => box.remove(), 4200);
  }

  $("#l-check").addEventListener("click", () => {
    if (L && L.done) return closeLesson();
    onCheck();
  });

  $("#l-close").innerHTML = icon("cross");
  $("#l-close").addEventListener("click", () => {
    if (!L || L.done || (L.right === 0 && L.mistakes === 0)) return closeLesson();
    const sheet = $("#sheet");
    sheet.innerHTML = `<div class="sheet-card">${speakerChar(L.queue[Math.min(L.pos, L.queue.length - 1)]).svg("sad")}
      <h3>Wait, don't go!</h3><p>You'll lose your progress in this lesson if you quit now.</p>
      <button class="btn btn-blue" type="button" id="keep">Keep learning</button>
      <button class="btn-text" type="button" id="quit">End session</button></div>`;
    sheet.hidden = false;
    $("#keep").addEventListener("click", () => (sheet.hidden = true));
    $("#quit").addEventListener("click", closeLesson);
    $("#keep").focus();
  });

  document.addEventListener("keydown", (e) => {
    if (!L || $("#lesson").hidden || !$("#sheet").hidden) return;
    if (e.key === "Enter") {
      if (e.target.closest && e.target.closest("button") && e.target.id !== "l-check") return;
      e.preventDefault();
      if (!$("#l-check").disabled) $("#l-check").click();
    } else if (/^[1-9]$/.test(e.key) && !L.answered && e.target.tagName !== "INPUT") {
      const opts = $$("#answer .options .opt");
      const o = opts[Number(e.key) - 1];
      if (o) o.click();
    } else if (e.key === "Escape") $("#l-close").click();
  });

  // ---------- exercise types ----------
  const TYPES = {
    choice(cur, area, ready) {
      const order = shuffle(cur.options.map((_, i) => i));
      area.innerHTML = `<div class="options">${order.map((i, k) => `<button type="button" class="opt" data-i="${i}"><span class="key">${k + 1}</span><span>${esc(cur.options[i])}</span></button>`).join("")}</div>`;
      let sel = null;
      $$(".opt", area).forEach((b) => b.addEventListener("click", () => {
        $$(".opt", area).forEach((x) => x.classList.remove("sel"));
        b.classList.add("sel"); sel = Number(b.dataset.i); SFX.tap(); ready(true);
      }));
      return {
        check() {
          const ok = sel === cur.answer;
          $$(".opt", area).forEach((b) => {
            const i = Number(b.dataset.i);
            if (i === cur.answer) b.classList.add("right");
            else if (i === sel) b.classList.add("wrong");
          });
          return { ok, correct: cur.options[cur.answer] };
        },
      };
    },

    multi(cur, area, ready) {
      const order = shuffle(cur.options.map((_, i) => i));
      area.innerHTML = `<p style="color:var(--muted);margin-bottom:10px">Select all that apply</p><div class="options">${order.map((i, k) => `<button type="button" class="opt multi" aria-pressed="false" data-i="${i}"><span class="key">${k + 1}</span><span>${esc(cur.options[i])}</span></button>`).join("")}</div>`;
      const sel = new Set();
      $$(".opt", area).forEach((b) => b.addEventListener("click", () => {
        const i = Number(b.dataset.i);
        sel.has(i) ? sel.delete(i) : sel.add(i);
        b.classList.toggle("sel", sel.has(i)); b.setAttribute("aria-pressed", sel.has(i));
        SFX.tap(); ready(sel.size > 0);
      }));
      return {
        check() {
          const want = new Set(cur.answer);
          const ok = sel.size === want.size && [...sel].every((i) => want.has(i));
          $$(".opt", area).forEach((b) => {
            const i = Number(b.dataset.i);
            if (want.has(i)) b.classList.add("right");
            else if (sel.has(i)) b.classList.add("wrong");
          });
          return { ok, correct: cur.answer.map((i) => cur.options[i]).join(", ") };
        },
      };
    },

    build(cur, area, ready) {
      let order;
      do { order = shuffle(cur.tiles.map((_, i) => i)); } while (cur.tiles.length > 1 && order.map((i) => cur.tiles[i]).join("|") === cur.answer.join("|"));
      area.innerHTML = `<div class="build-line" aria-label="Your answer"></div><div class="bank" aria-label="Word bank"></div>`;
      const line = $(".build-line", area), bank = $(".bank", area);
      const placed = [];
      order.forEach((i) => {
        const t = el(`<button type="button" class="tile" data-i="${i}">${esc(cur.tiles[i])}</button>`);
        t.addEventListener("click", () => {
          if (t.classList.contains("ghost")) return;
          t.classList.add("ghost"); placed.push(i); SFX.tap(); draw();
        });
        bank.append(t);
      });
      function draw() {
        line.innerHTML = "";
        placed.forEach((i, k) => {
          const t = el(`<button type="button" class="tile pop-in">${esc(cur.tiles[i])}</button>`);
          t.addEventListener("click", () => {
            placed.splice(k, 1);
            $(`.tile[data-i="${i}"]`, bank).classList.remove("ghost");
            SFX.tap(); draw();
          });
          line.append(t);
        });
        ready(placed.length > 0);
      }
      return {
        check() {
          const got = placed.map((i) => cur.tiles[i]);
          const ok = got.join("\u0001") === cur.answer.join("\u0001");
          return { ok, correct: cur.answer.join(cur.answer.some((a) => a.includes(" ")) ? "  →  " : " ") };
        },
      };
    },

    match(cur, area, ready) {
      const left = shuffle(cur.pairs.map((p, i) => i)), right = shuffle(cur.pairs.map((p, i) => i));
      area.innerHTML = `<div class="match"><div class="match-col">${left.map((i) => `<button type="button" class="opt" data-side="l" data-i="${i}">${esc(cur.pairs[i][0])}</button>`).join("")}</div>
        <div class="match-col">${right.map((i) => `<button type="button" class="opt" data-side="r" data-i="${i}">${esc(cur.pairs[i][1])}</button>`).join("")}</div></div>`;
      let sel = { l: null, r: null }, matched = 0, slips = 0;
      $$(".opt", area).forEach((b) => b.addEventListener("click", () => {
        const side = b.dataset.side;
        $$(`.opt[data-side="${side}"]`, area).forEach((x) => x.classList.remove("sel"));
        b.classList.add("sel"); sel[side] = b;
        if (!sel.l || !sel.r) { SFX.tap(); return; }
        const a = sel.l, c = sel.r;
        sel = { l: null, r: null };
        a.classList.remove("sel"); c.classList.remove("sel");
        if (a.dataset.i === c.dataset.i) {
          SFX.good(); matched++;
          [a, c].forEach((x) => { x.classList.add("right"); setTimeout(() => { x.classList.remove("right"); x.classList.add("done"); }, 380); });
          if (matched === cur.pairs.length) {
            const run = L, pos = L.pos;
            setTimeout(() => { if (L === run && L.pos === pos && !L.answered) resolve({ ok: true }); }, 450);
          }
        } else {
          SFX.bad(); slips++;
          [a, c].forEach((x) => { x.classList.add("wrong"); setTimeout(() => x.classList.remove("wrong"), 450); });
        }
      }));
      ready(false);
      return { check: () => null };
    },

    number(cur, area, ready) {
      area.innerHTML = `<div class="num-wrap"><input class="num-input" id="num-answer" type="text" inputmode="decimal" autocomplete="off" placeholder="?" aria-label="Your answer"></div>`;
      const inp = $("input", area);
      inp.addEventListener("input", () => ready(inp.value.trim() !== "" && !isNaN(parse(inp.value))));
      setTimeout(() => inp.focus({ preventScroll: true }), 50);
      function parse(v) { return Number(String(v).replace(/[, ]/g, "")); }
      return {
        check() {
          inp.disabled = true;
          return { ok: Math.abs(parse(inp.value) - cur.answer) <= (cur.tol || 0), correct: String(cur.answer) };
        },
      };
    },

    cut(cur, area, ready) {
      const w = cur.word;
      const cuts = new Set();
      const cols = ["var(--blue)", "var(--orange)", "#ce82ff", "var(--green)", "#ff86d0", "var(--gold)"];
      area.innerHTML = `<div class="vocab-chips"><span class="vchip letters">vocabulary:</span>${cur.vocab.map((v) => `<span class="vchip">${v}</span>`).join("")}<span class="vchip letters">+ every single letter</span></div>
        <div class="cut-word"></div><div class="cut-pieces" aria-live="polite"></div><p class="cut-hint">Tap between letters to snip. Tap again to undo.</p>`;
      const word = $(".cut-word", area);
      [...w].forEach((ch, i) => {
        if (i > 0) {
          const g = el(`<button type="button" class="gap" aria-label="Cut between ${w[i - 1]} and ${ch}" aria-pressed="false"></button>`);
          g.addEventListener("click", () => {
            cuts.has(i) ? cuts.delete(i) : cuts.add(i);
            g.classList.toggle("on", cuts.has(i)); g.setAttribute("aria-pressed", cuts.has(i));
            SFX.tap(); draw();
          });
          word.append(g);
        }
        word.append(el(`<span class="letter" data-i="${i}">${ch}</span>`));
      });
      const pieces = () => {
        const out = []; let s = 0;
        [...cuts].sort((a, b) => a - b).forEach((c) => { out.push(w.slice(s, c)); s = c; });
        out.push(w.slice(s)); return out;
      };
      function draw() {
        const ps = pieces();
        let pos = 0;
        ps.forEach((p, k) => { for (let j = 0; j < p.length; j++) $(`.letter[data-i="${pos + j}"]`, word).style.setProperty("--seg", cols[k % cols.length]); pos += p.length; });
        $(".cut-pieces", area).innerHTML = ps.map((p) => {
          const cls = p.length === 1 ? "letter1" : cur.vocab.includes(p) ? "ok" : "bad";
          return `<span class="piece ${cls}">${p}</span>`;
        }).join("");
        ready(cuts.size > 0);
      }
      draw();
      return {
        check() {
          const ps = pieces();
          return { ok: ps.join("|") === cur.answer.join("|"), correct: cur.answer.join(" · ") };
        },
      };
    },

    vector(cur, area, ready) {
      const v = cur.vocab.map(() => 0);
      area.innerHTML = `<div class="doc-tokens" aria-label="Document">${cur.doc.split(" ").map((t) => `<span>${esc(t)}</span>`).join("")}</div>
        <div class="vec"></div><p class="vecline"></p>`;
      const grid = $(".vec", area);
      cur.vocab.forEach((word, i) => {
        const cell = el(`<div class="vcell"><b>${esc(word)}</b><output aria-live="polite">0</output>
          <div class="vsteps"><button type="button" class="vstep" aria-label="One less ${esc(word)}">−</button><button type="button" class="vstep" aria-label="One more ${esc(word)}">+</button></div></div>`);
        const [minus, plus] = $$(".vstep", cell);
        const upd = (d) => { v[i] = Math.max(0, Math.min(9, v[i] + d)); $("output", cell).textContent = v[i]; cell.classList.toggle("nz", v[i] > 0); SFX.tap(); draw(); };
        minus.addEventListener("click", () => upd(-1));
        plus.addEventListener("click", () => upd(1));
        grid.append(cell);
      });
      function draw() { $(".vecline", area).textContent = `[${v.join(", ")}]`; ready(true); }
      draw();
      return { check: () => ({ ok: v.join() === cur.answer.join(), correct: `[${cur.answer.join(", ")}]` }) };
    },
  };

  // ---------- boot ----------
  $$("[data-icon]").forEach((n) => (n.innerHTML = icon(n.dataset.icon)));
  $("#logo-mark").innerHTML = CHARS.spidey.svg("happy");
  $("#lesson").append(el(`<div class="fx" id="fx" aria-hidden="true"></div>`));
  $("#sound-toggle").addEventListener("click", () => { state.muted = !state.muted; save(); renderStats(); SFX.tap(); });
  renderStats();
  renderFact();
  const start = (location.hash || "#learn").slice(1);
  go(["learn", "cast", "guide"].includes(start) ? start : "learn");
  const n = $(".node.next");
  if (n && start === "learn" && Object.keys(state.done).length) n.scrollIntoView({ block: "center" });
})();
