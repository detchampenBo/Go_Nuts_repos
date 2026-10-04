// The Tokenlingo cast: Marvel heroes from the course's character network, drawn in the
// style of lesson-app characters: full bodies with big rounded heads, flat colour with a
// one-sided cel shadow, solid dot eyes, chunky brows, and poses that act out the mood.
// Every drawing takes an expression: idle, happy, sad or think.
(function () {
  const INK = "#1f1f1f";
  const tileText = 'font-family="Nunito, system-ui, sans-serif" font-weight="800" text-anchor="middle"';

  // ---------- shared parts ----------
  // A rounded block with a darker crescent on its right side (flat cel shading).
  function block(x, y, w, h, r, light, shade, cut = 6) {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${shade}"/>` +
      `<rect x="${x}" y="${y}" width="${w - cut}" height="${h}" rx="${Math.min(r, (w - cut) / 2)}" fill="${light}"/>`;
  }

  function dotEye(x, y, expr, color = INK, shine = true) {
    if (expr === "happy") return `<path d="M${x - 4.6} ${y + 1.8} Q${x} ${y - 5.2} ${x + 4.6} ${y + 1.8}" fill="none" stroke="${color}" stroke-width="3.4" stroke-linecap="round"/>`;
    const dx = expr === "think" ? 1.6 : 0, dy = expr === "think" ? -1.6 : expr === "sad" ? 1.6 : 0;
    const ry = expr === "sad" ? 4.4 : 5.2;
    return `<ellipse cx="${x + dx}" cy="${y + dy}" rx="3.7" ry="${ry}" fill="${color}"/>` +
      (shine ? `<circle cx="${x + dx + 1.2}" cy="${y + dy - 1.8}" r="1.3" fill="#fff"/>` : "");
  }

  function brow(x, y, side, expr, color = INK, w = 3.6) {
    // side: -1 left eye, 1 right eye. "inner" is toward the face centre.
    const o = x + 5.5 * side, i = x - 5.5 * side;
    let d;
    if (expr === "happy") d = `M${i} ${y - 11} Q${x} ${y - 14} ${o} ${y - 11.5}`;
    else if (expr === "sad") d = `M${i} ${y - 13} L${o} ${y - 9}`;
    else if (expr === "think") d = side === 1 ? `M${i} ${y - 12} Q${x} ${y - 16.5} ${o} ${y - 13}` : `M${i} ${y - 9.5} L${o} ${y - 9.5}`;
    else d = `M${i} ${y - 10} Q${x} ${y - 12} ${o} ${y - 10}`;
    return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round"/>`;
  }

  function mouth(x, y, expr, w = 1, color = INK) {
    if (expr === "happy") {
      return `<path d="M${x - 8 * w} ${y - 1} Q${x} ${y + 13 * w} ${x + 8 * w} ${y - 1} Z" fill="#5b1a1f"/>` +
        `<path d="M${x - 7 * w} ${y - 0.2} L${x + 7 * w} ${y - 0.2} Q${x + 5 * w} ${y + 3.4} ${x} ${y + 3.6} Q${x - 5 * w} ${y + 3.4} ${x - 7 * w} ${y - 0.2} Z" fill="#fff"/>` +
        `<ellipse cx="${x}" cy="${y + 7.5 * w}" rx="${3.6 * w}" ry="${1.8 * w}" fill="#ff7b8a"/>`;
    }
    if (expr === "sad") return `<path d="M${x - 5 * w} ${y + 3} Q${x} ${y - 2.5} ${x + 5 * w} ${y + 3}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round"/>`;
    if (expr === "think") return `<path d="M${x - 4 * w} ${y + 1.5} Q${x + 1} ${y + 2} ${x + 4.5 * w} ${y - 1}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round"/>`;
    return `<path d="M${x - 5 * w} ${y} Q${x} ${y + 4.5} ${x + 5 * w} ${y}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round"/>`;
  }

  // Arm poses: shoulder → elbow → hand. "think" brings the right hand up to the chin.
  const POSES = {
    idle: [[[42, 66], [36, 80], [33, 93]], [[78, 66], [84, 80], [87, 93]]],
    happy: [[[42, 66], [29, 59], [23, 43]], [[78, 66], [91, 59], [97, 43]]],
    sad: [[[43, 67], [41, 81], [40, 95]], [[77, 67], [79, 81], [80, 95]]],
    think: [[[42, 66], [36, 80], [33, 93]], [[78, 66], [90, 76], [73, 63]]],
  };
  function armPoints(expr, spread) {
    return POSES[expr].map((pts, s) => pts.map(([x, y], k) => [x + (k ? spread * (s ? 1 : -1) : spread * 0.6 * (s ? 1 : -1)), y]));
  }
  function arm(pts, color, hand, w = 10) {
    const p = pts.map((q) => q.join(",")).join(" ");
    const [hx, hy] = pts[2];
    return `<polyline points="${p}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>` +
      `<circle cx="${hx}" cy="${hy}" r="${w * 0.62}" fill="${hand}"/>`;
  }

  // Assemble a figure from its parts in back-to-front order.
  function figure(expr, o) {
    const arms = armPoints(expr, o.spread || 0);
    const aw = o.armW || 10;
    const left = arm(arms[0], o.arm, o.hand, aw), right = arm(arms[1], o.arm, o.hand, aw);
    const legs = o.legs || `
      <rect x="47" y="93" width="11" height="20" rx="5.5" fill="${o.leg}"/><rect x="62" y="93" width="11" height="20" rx="5.5" fill="${o.leg}"/>
      <ellipse cx="50" cy="114" rx="8" ry="4.6" fill="${o.shoe}"/><ellipse cx="70" cy="114" rx="8" ry="4.6" fill="${o.shoe}"/>`;
    const t = o.torsoBox || [38, 58, 44, 40, 14];
    const h = o.headBox || [34, 8, 52, 52, 24];
    return (o.behind ? o.behind(expr) : "") + legs +
      block(...t, o.torso, o.torsoShade) + (o.torsoExtra || "") +
      left + (expr === "think" ? "" : right) + (o.hands ? o.hands(arms, expr) : "") +
      block(...h, o.head, o.headShade) +
      o.face(expr) +
      (expr === "think" ? right : "") + (o.front ? o.front(expr) : "");
  }

  // Wolverine's claws come out of the fist along the forearm.
  function claws([elbow, hand]) {
    const dx = hand[0] - elbow[0], dy = hand[1] - elbow[1], L = Math.hypot(dx, dy);
    const ux = dx / L, uy = dy / L;
    return [-0.32, 0, 0.32].map((a) => {
      const c = Math.cos(a), s = Math.sin(a);
      const vx = ux * c - uy * s, vy = ux * s + uy * c;
      return `<line x1="${hand[0] + vx * 4}" y1="${hand[1] + vy * 4}" x2="${hand[0] + vx * 18}" y2="${hand[1] + vy * 18}" stroke="#cfd8dc" stroke-width="2.6" stroke-linecap="round"/>`;
    }).join("");
  }

  // Mask eyes: white almonds whose shape carries the expression.
  function maskEye(x, y, side, expr, fill = "#fff", stroke = "") {
    const st = stroke ? `stroke="${stroke}" stroke-width="2.6" stroke-linejoin="round"` : "";
    if (expr === "happy") return `<path d="M${x - 6.5} ${y + 2.5} Q${x} ${y - 7} ${x + 6.5} ${y + 2.5} Q${x} ${y - 1.5} ${x - 6.5} ${y + 2.5} Z" fill="${fill}" ${st}/>`;
    const o = x + 7 * side, i = x - 6 * side;
    if (expr === "sad") return `<path d="M${o} ${y + 1} Q${x} ${y - 1} ${i} ${y - 4} Q${x} ${y + 6} ${o} ${y + 1} Z" fill="${fill}" ${st}/>`;
    if (expr === "think" && side === 1) return `<path d="M${o} ${y - 1} Q${x} ${y - 2.5} ${i} ${y + 0.5} Q${x} ${y + 2.6} ${o} ${y - 1} Z" fill="${fill}" ${st}/>`;
    return `<path d="M${o} ${y - 4} Q${x} ${y - 3} ${i} ${y + 1} Q${x} ${y + 6.5} ${o} ${y - 4} Z" fill="${fill}" ${st}/>`;
  }

  // Spider-Man's big rounded lenses. The left lens is drawn; the right one is its mirror image.
  function spideyLenses(expr) {
    const st = 'fill="#fff" stroke="#1d1d1d" stroke-width="2.8" stroke-linejoin="round"';
    const shape = {
      idle: "M57 36 Q55 25 41 23 Q36 31 41 37 Q49 41 57 36 Z",
      happy: "M57 34 Q52 22 40 25 Q38 30 40 32 Q50 27 57 34 Z",
      sad: "M57 29 Q50 26 41 31 Q38 37 44 39 Q53 39 57 29 Z",
      think: "M57 34 Q50 30 41 30 Q39 35 43 37 Q51 39 57 34 Z",
    };
    const left = `<path d="${expr === "think" ? shape.idle : shape[expr]}" ${st}/>`;
    const right = `<path d="${shape[expr]}" ${st} transform="translate(120 0) scale(-1 1)"/>`;
    return left + right;
  }

  // ---------- the heroes ----------
  const drawings = {
    wolverine: (e) => figure(e, {
      behind: () => `<path d="M39 24 L27 1 L50 15 Z M81 24 L93 1 L70 15 Z" fill="#1d1d1d"/>`,
      legs: `<rect x="47" y="93" width="11" height="20" rx="5.5" fill="#ffc800"/><rect x="62" y="93" width="11" height="20" rx="5.5" fill="#ffc800"/>
        <rect x="46" y="103" width="13" height="10" rx="4" fill="#1f4fbf"/><rect x="61" y="103" width="13" height="10" rx="4" fill="#1f4fbf"/>
        <ellipse cx="50" cy="114" rx="8" ry="4.6" fill="#1f4fbf"/><ellipse cx="70" cy="114" rx="8" ry="4.6" fill="#1f4fbf"/>`,
      torso: "#ffc800", torsoShade: "#e5a800",
      torsoExtra: `<path d="M39.5 68 Q41 60 50 58.5 L46 89 L39 89 Z M80.5 68 Q79 60 70 58.5 L74 89 L81 89 Z" fill="#1f4fbf"/>
        <path d="M38 86 H82 V88 Q82 98 72 98 H48 Q38 98 38 88 Z" fill="#1f4fbf"/>`,
      arm: "#ffc800", hand: "#1f4fbf",
      hands: (a) => claws(a[0].slice(1)) + claws(a[1].slice(1)),
      head: "#f3bf95", headShade: "#d99a6c",
      face: (e) => `
        <path d="M34 36 Q34 8 60 8 Q86 8 86 36 L86 41 Q74 45 60 46.5 Q46 45 34 41 Z" fill="#ffc800"/>
        <path d="M78 11 Q86 18 86 36 L86 41 L80.5 42.6 Q82 24 78 11 Z" fill="#e5a800"/>
        <path d="M37.5 34 Q42 22 56.5 28.5 L57.5 40 Q45 43 37.5 34 Z M82.5 34 Q78 22 63.5 28.5 L62.5 40 Q75 43 82.5 34 Z" fill="#1d1d1d"/>
        <path d="M34 40 Q33 54 44 59 L42 46 Z M86 40 Q87 54 76 59 L78 46 Z" fill="#3e2a1e"/>
        <g class="eyes">${maskEye(48.5, 34, -1, e)}${maskEye(71.5, 34, 1, e)}</g>
        <ellipse cx="60" cy="48" rx="3" ry="2.2" fill="#d99a6c"/>
        ${mouth(60, 53, e, 0.8)}`,
    }),

    antman: (e) => figure(e, {
      behind: () => `<path d="M51 12 L41 1 M69 12 L79 1" stroke="#90a4ae" stroke-width="2.6" stroke-linecap="round"/><circle cx="41" cy="1.5" r="2.4" fill="#90a4ae"/><circle cx="79" cy="1.5" r="2.4" fill="#90a4ae"/>`,
      leg: "#e53935", shoe: "#263238",
      torso: "#e53935", torsoShade: "#b71c1c",
      torsoExtra: `<path d="M39.5 68 Q41 60 48 58.5 L46 97 Q39 95 38.5 88 Z M80.5 68 Q79 60 72 58.5 L74 97 Q81 95 81.5 88 Z" fill="#263238"/>
        <rect x="38" y="84" width="44" height="5" fill="#263238"/><circle cx="60" cy="86.5" r="4" fill="#cfd8dc"/>`,
      arm: "#e53935", hand: "#263238",
      head: "#e53935", headShade: "#b71c1c",
      face: (e) => `
        <rect x="56" y="8" width="8" height="14" rx="4" fill="#cfd8dc"/>
        <path d="M37 45 Q40 59 60 60 Q80 59 83 45 Q60 51 37 45 Z" fill="#cfd8dc"/>
        <path d="M77 47.5 Q80 47 83 45 Q81 57 70 59.5 Q77 54 77 47.5 Z" fill="#a7b6bd"/>
        <circle cx="49" cy="33" r="9.5" fill="#263238"/><circle cx="71" cy="33" r="9.5" fill="#263238"/>
        <circle cx="45.5" cy="29.5" r="2.2" fill="#fff" opacity=".35"/><circle cx="67.5" cy="29.5" r="2.2" fill="#fff" opacity=".35"/>
        <g class="eyes">${dotEye(49, 34, e, "#fff", false)}${dotEye(71, 34, e, "#fff", false)}</g>
        ${e === "sad" || e === "think" ? brow(49, 33, -1, e, "#fff", 2.6) + brow(71, 33, 1, e, "#fff", 2.6) : ""}
        ${mouth(60, 53, e, 0.7, "#546e7a")}`,
      front: () => `<g fill="#1d1d1d"><ellipse cx="86" cy="61" rx="3.4" ry="2.6"/><circle cx="81" cy="62" r="2"/><circle cx="90.5" cy="59.5" r="2.2"/></g>
        <path d="M82 64 L80 67 M86 63.5 L86 67 M89 62.5 L91.5 65.5 M91.5 58 L94 55" stroke="#1d1d1d" stroke-width="1.2" stroke-linecap="round"/>`,
    }),

    hulk: (e) => figure(e, {
      spread: 6, armW: 15,
      legs: `<rect x="43" y="92" width="15" height="19" rx="6" fill="#7b3fa0"/><rect x="62" y="92" width="15" height="19" rx="6" fill="#7b3fa0"/>
        <path d="M43 106 L46 111 L49 106 L52 111 L55 106 L58 110 L58 100 L43 100 Z M62 106 L65 111 L68 106 L71 111 L74 106 L77 110 L77 100 L62 100 Z" fill="#7b3fa0"/>
        <ellipse cx="49" cy="114" rx="10" ry="5" fill="#5fb236"/><ellipse cx="71" cy="114" rx="10" ry="5" fill="#5fb236"/>`,
      torsoBox: [31, 57, 58, 41, 16],
      torso: "#6cc04a", torsoShade: "#4f9e35",
      torsoExtra: `<path d="M44 68 Q51 73 58 69 M62 69 Q69 73 76 68 M52 80 H57 M63 80 H68" fill="none" stroke="#4f9e35" stroke-width="2.4" stroke-linecap="round"/>
        <path d="M31 86 H89 V88 Q89 98 79 98 H41 Q31 98 31 88 Z" fill="#7b3fa0"/>`,
      arm: "#6cc04a", hand: "#5fb236",
      headBox: [30, 7, 60, 53, 20],
      head: "#6cc04a", headShade: "#4f9e35",
      face: (e) => `
        <path d="M29 30 Q28 4 60 4 Q92 4 91 30 L85 20 L81 27 L75 15 L69 24 L61 13 L54 24 L47 15 L41 26 L36 19 Z" fill="#1d1d1d"/>
        ${brow(50, 37, -1, e, "#1d1d1d", 4.8)}${brow(70, 37, 1, e, "#1d1d1d", 4.8)}
        <g class="eyes">${dotEye(50, 37, e)}${dotEye(70, 37, e)}</g>
        <ellipse cx="60" cy="45" rx="5" ry="3.2" fill="#4f9e35"/>
        ${mouth(60, 52, e, 1.15)}`,
    }),

    fury: (e) => figure(e, {
      leg: "#2a2f33", shoe: "#111",
      torso: "#353b40", torsoShade: "#1d2124",
      torsoExtra: `<path d="M38 88 L33 107 Q60 110.5 87 107 L82 88 Z" fill="#353b40"/>
        <path d="M76 88 H82 L87 107 Q84 107.6 80.5 108 Z" fill="#1d2124"/>
        <path d="M60 70 V108" stroke="#1d2124" stroke-width="1.6"/>
        <path d="M47.5 59 L56 77 L60 70 L64 77 L72.5 59" fill="none" stroke="#5d656c" stroke-width="2.2" stroke-linejoin="round"/>`,
      arm: "#353b40", hand: "#8d5a3b",
      head: "#8d5a3b", headShade: "#6b4129",
      face: (e) => `
        <ellipse cx="50" cy="15.5" rx="9" ry="4" fill="#a8714f" opacity=".7"/>
        <path d="M34 31 L86 24" stroke="#111" stroke-width="2.4"/>
        <ellipse cx="50" cy="35" rx="7" ry="6.5" fill="#111"/>
        ${brow(70, 35, 1, e, "#1d1d1d")}<g class="eyes">${dotEye(70, 35, e)}</g>
        <ellipse cx="60" cy="43" rx="3.2" ry="2.4" fill="#6b4129"/>
        <path d="M51 48.5 Q60 45 69 48.5 Q65.5 50.2 60 49.2 Q54.5 50.2 51 48.5 Z" fill="#241811"/>
        <path d="M51.5 49 Q50 56 55 60 M68.5 49 Q70 56 65 60" fill="none" stroke="#241811" stroke-width="2.2" stroke-linecap="round"/>
        <path d="M54.5 58.6 Q60 61.5 65.5 58.6 L64.5 60.4 Q60 62.4 55.5 60.4 Z" fill="#241811"/>
        ${mouth(60, 52.5, e, 0.85)}`,
    }),

    spidey: (e) => figure(e, {
      leg: "#1f4fbf", shoe: "#e23636",
      torso: "#1f4fbf", torsoShade: "#173d96",
      torsoExtra: `<path d="M49 58.5 H71 L69 97.5 H51 Z" fill="#e23636"/>
        <g stroke="#1d1d1d" stroke-width="1.5" stroke-linecap="round"><path d="M60 68 V80 M54.5 69 L60 73 L65.5 69 M54.5 79 L60 75 L65.5 79" fill="none"/></g><ellipse cx="60" cy="74" rx="2.4" ry="3.2" fill="#1d1d1d"/>`,
      arm: "#e23636", hand: "#e23636",
      head: "#e23636", headShade: "#b71c1c",
      face: (e) => `
        <g fill="none" stroke="#8e1b1b" stroke-width="1.1" opacity=".45">
          <path d="M60 8 V60 M47 9.5 Q42 34 47 59 M73 9.5 Q78 34 73 59 M35 26 Q60 32 80 26 M34 44 Q60 50 80 44"/>
        </g>
        <g class="eyes">${spideyLenses(e)}</g>
        ${mouth(60, 51, e, 0.8, "#7f1010")}`,
    }),

    loki: (e) => figure(e, {
      behind: () => `
        <path d="M38 60 L23 116 H97 L82 60 Z" fill="#1b5e20"/>
        <path d="M33 30 Q30 64 40 70 H80 Q90 64 87 30 Z" fill="#1d1d1d"/>
        <path d="M41 16 C37 2 28 -2 19 2 C29 5 33 13 34 27 Z M79 16 C83 2 92 -2 101 2 C91 5 87 13 86 27 Z" fill="#ffc800"/>`,
      leg: "#2e7d32", shoe: "#ffc800",
      torso: "#43a047", torsoShade: "#2e7d32",
      torsoExtra: `<path d="M45 59 L60 72 L75 59" fill="none" stroke="#ffc800" stroke-width="4" stroke-linejoin="round"/><rect x="38" y="86" width="44" height="4" fill="#ffc800"/>`,
      arm: "#2e7d32", hand: "#1b5e20",
      head: "#f6dcc8", headShade: "#e3bfa5",
      face: (e) => `
        <path d="M34 31 Q34 8 60 8 Q86 8 86 31 Q78 23 68 23 L60 33 L52 23 Q42 23 34 31 Z" fill="#ffc800"/>
        <path d="M78 12 Q86 19 86 31 Q83 28 79.5 25.5 Q81 18 78 12 Z" fill="#e0a800"/>
        <path d="M34 29 Q32 47 39 57 L41 33 Z M86 29 Q88 47 81 57 L79 33 Z" fill="#1d1d1d"/>
        ${brow(51, 39, -1, e)}${brow(69, 39, 1, e === "idle" ? "think" : e)}
        <g class="eyes">${dotEye(51, 39, e)}${dotEye(69, 39, e)}</g>
        <ellipse cx="60" cy="46" rx="2.8" ry="2.1" fill="#e3bfa5"/>
        ${e === "idle" ? `<path d="M54 52 Q62 56 67 50" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>` : mouth(60, 52, e, 0.9)}`,
      front: (e) => {
        const up = e === "happy";
        return `<g transform="rotate(-12 ${up ? 22 : 14} ${up ? 26 : 30})"><rect x="${up ? 10 : 2}" y="${up ? 20 : 24}" width="24" height="12" rx="4" fill="#fff" stroke="#d5dde1" stroke-width="1.5"/><text x="${up ? 22 : 14}" y="${up ? 28.8 : 32.8}" ${tileText} font-size="7.5" fill="#4b4b4b">ball</text></g>
          <g transform="rotate(12 ${up ? 98 : 106} ${up ? 26 : 30})"><rect x="${up ? 86 : 94}" y="${up ? 20 : 24}" width="24" height="12" rx="4" fill="#fff" stroke="#d5dde1" stroke-width="1.5"/><text x="${up ? 98 : 106}" y="${up ? 28.8 : 32.8}" ${tileText} font-size="7.5" fill="#4b4b4b">dog</text></g>`;
      },
    }),

    ironman: (e) => figure(e, {
      leg: "#c62828", shoe: "#ffc107",
      torso: "#c62828", torsoShade: "#8e0000",
      torsoExtra: `<path d="M49 80 H71 L69 97.5 H51 Z" fill="#ffc107"/><circle cx="60" cy="69" r="5.5" fill="#d9fbff" stroke="#4dd0e1" stroke-width="2.6"/>`,
      arm: "#c62828", hand: "#ffc107",
      head: "#c62828", headShade: "#8e0000",
      face: (e) => {
        const slit = (x, side) => {
          if (e === "happy") return `<path d="M${x - 6} ${y + 2} Q${x} ${y - 5} ${x + 6} ${y + 2}" fill="none" stroke="#d9fbff" stroke-width="3.6" stroke-linecap="round"/>`;
          const o = x + 6.5 * side, i = x - 6.5 * side;
          if (e === "sad") return `<path d="M${o} ${y + 1.5} L${i} ${y - 3} L${i} ${y + 1} L${o} ${y + 4.5} Z" fill="#d9fbff" stroke="#4dd0e1" stroke-width="1.4" stroke-linejoin="round"/>`;
          if (e === "think" && side === 1) return `<rect x="${x - 6.5}" y="${y - 0.5}" width="13" height="2.6" rx="1.3" fill="#d9fbff"/>`;
          return `<rect x="${x - 6.5}" y="${y - 2}" width="13" height="5" rx="2.5" fill="#d9fbff" stroke="#4dd0e1" stroke-width="1.4"/>`;
        };
        const y = 34;
        const m = e === "happy" ? `<path d="M52 51 Q60 57 68 51" fill="none" stroke="#8a6d00" stroke-width="2.8" stroke-linecap="round"/>`
          : e === "sad" ? `<path d="M53 54 Q60 49 67 54" fill="none" stroke="#8a6d00" stroke-width="2.8" stroke-linecap="round"/>`
          : e === "think" ? `<path d="M54 52.5 L66 51" stroke="#8a6d00" stroke-width="2.8" stroke-linecap="round"/>`
          : `<path d="M53 52 H67" stroke="#8a6d00" stroke-width="2.8" stroke-linecap="round"/>`;
        return `
          <path d="M40 23 Q60 19 80 23 L80 44 Q78 56 68 60 H52 Q42 56 40 44 Z" fill="#ffc107"/>
          <path d="M74 21.5 Q80 22 80 30 V44 Q78 56 68 60 H65 Q75 51 75 37 Z" fill="#e0a000"/>
          <path d="M44 44 L50 48 M76 44 L70 48" stroke="#d4a000" stroke-width="1.8" stroke-linecap="round"/>
          <g class="eyes">${slit(50, -1)}${slit(70, 1)}</g>${m}`;
      },
    }),
  };

  const CHARS = {
    wolverine: {
      name: "Wolverine", role: "The Tokenizer", color: "#ffc800", dark: "#1f4fbf",
      teaches: "Tokenization: cutting raw characters into tokens, types, token IDs and subword pieces.",
      quote: "Spaces are a suggestion, bub. I decide where the cuts go.",
      lines: ["Snikt. Every cut is a modelling choice.", "Raw characters in, tokens out.", "Where does one token end, bub?"],
    },
    antman: {
      name: "Ant-Man", role: "The Shrinker", color: "#e53935", dark: "#b71c1c",
      teaches: "Preprocessing: lowercasing, stopword removal and lemmatization shrink the vocabulary, and each throws something away.",
      quote: "I make words smaller. heroes → hero, Apple → apple. Small change, big consequences.",
      lines: ["Shrink carefully. Something always gets lost.", "Stopwords are tiny, but they're everywhere.", "Every cleaning step deletes information."],
    },
    hulk: {
      name: "Hulk", role: "The Counter", color: "#6cc04a", dark: "#7b3fa0",
      teaches: "Counting tokens, types and frequencies, and Zipf's law on linear and log-log axes.",
      quote: "HULK COUNT FIRST. HULK MODEL LATER.",
      lines: ["HULK COUNT FIRST!", "Few words BIG. Many words tiny.", "Log-log axes make curve STRAIGHT. Hulk like."],
    },
    fury: {
      name: "Nick Fury", role: "The Hapax", color: "#78909c", dark: "#37474f",
      teaches: "Hapax types: the words that show up exactly once in a corpus.",
      quote: "I show up once, after the credits. That makes me a hapax.",
      lines: ["Pay attention. I only show up once.", "36% of Marvel's word types are like me.", "Rare doesn't mean unimportant."],
    },
    spidey: {
      name: "Spider-Man", role: "The N-gram", color: "#e23636", dark: "#1f4fbf",
      teaches: "N-grams, concordances, similar() and collocations: words read in their context.",
      quote: "I'm from Queens. 'New York' is one place, not 'New' plus 'York'.",
      lines: ["My spider-sense says: check the context!", "Slide the window, web the neighbours.", "A count can't tell you how a word is used."],
    },
    loki: {
      name: "Loki", role: "The Bag of Words", color: "#43a047", dark: "#1b5e20",
      teaches: "Bag of Words, document vectors and the document-term matrix, which keep the counts and lose the order.",
      quote: "Same words, different story. My favourite trick.",
      lines: ["Mischief time: keep the counts, lose the order.", "Rows are documents, columns are words.", "Loki tricks Thor. Thor tricks Loki. Same vector."],
    },
    ironman: {
      name: "Iron Man", role: "The Cosine", color: "#c62828", dark: "#8e0000",
      teaches: "Cosine similarity between documents, and why counts know nothing about meaning.",
      quote: "Length doesn't matter. Direction does.",
      lines: ["Running cosine. Only the angle matters.", "dog and puppy at right angles? We'll upgrade that next week.", "Same direction, same story."],
    },
  };

  for (const [id, c] of Object.entries(CHARS)) {
    c.id = id;
    c.svg = (expr = "idle", cls = "") =>
      `<svg class="char expr-${expr} ${cls}" style="--blink:${(Math.random() * 4).toFixed(2)}s" viewBox="0 -2 120 122" role="img" aria-label="${c.name}, ${c.role}">${drawings[id](expr)}</svg>`;
  }

  window.TL_CHARS = CHARS;
})();
