// The Tokenlingo cast: Marvel heroes from the course's character network, drawn in a
// flat, round, big-eyed lesson-app style. Each hero embodies one Week 5 idea.
// Every drawing takes an expression: idle, happy, sad or think.
(function () {
  const INK = "#22313a";

  function eye(x, y, r, expr, arc = INK) {
    if (expr === "happy") {
      return `<path d="M${x - r * 0.78} ${y + r * 0.3} Q${x} ${y - r * 0.95} ${x + r * 0.78} ${y + r * 0.3}" fill="none" stroke="${arc}" stroke-width="${Math.max(2.6, r * 0.34)}" stroke-linecap="round"/>`;
    }
    const dx = expr === "think" ? r * 0.3 : r * 0.1;
    const dy = expr === "think" ? -r * 0.36 : expr === "sad" ? r * 0.3 : r * 0.12;
    return `<circle cx="${x}" cy="${y}" r="${r}" fill="#fff"/>` +
      `<circle cx="${x + dx}" cy="${y + dy}" r="${r * 0.54}" fill="${INK}"/>` +
      `<circle cx="${x + dx + r * 0.2}" cy="${y + dy - r * 0.22}" r="${r * 0.17}" fill="#fff"/>`;
  }

  function brows(expr, eyes, r, color = INK) {
    if (expr !== "sad" && expr !== "think") return "";
    return eyes.map(([x, y], i) => {
      const dir = i === 0 ? 1 : -1;
      if (expr === "think") {
        return i === 0 ? `<path d="M${x - r * 0.8} ${y - r * 1.45} Q${x} ${y - r * 1.9} ${x + r * 0.8} ${y - r * 1.5}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round"/>` : "";
      }
      return `<path d="M${x - r * 0.9 * dir} ${y - r * 1.15} L${x + r * 0.7 * dir} ${y - r * 1.6}" stroke="${color}" stroke-width="3" stroke-linecap="round"/>`;
    }).join("");
  }

  function mouth(x, y, w, expr) {
    if (expr === "happy") {
      return `<path d="M${x - w} ${y} Q${x} ${y + w * 1.6} ${x + w} ${y} Z" fill="${INK}"/>` +
        `<ellipse cx="${x}" cy="${y + w * 0.52}" rx="${w * 0.42}" ry="${w * 0.2}" fill="#ff7b8a"/>`;
    }
    if (expr === "sad") {
      return `<path d="M${x - w * 0.55} ${y + w * 0.45} Q${x} ${y - w * 0.25} ${x + w * 0.55} ${y + w * 0.45}" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`;
    }
    if (expr === "think") {
      return `<path d="M${x - w * 0.4} ${y + 2} Q${x} ${y + 4} ${x + w * 0.45} ${y - 1}" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`;
    }
    return `<path d="M${x - w * 0.6} ${y} Q${x} ${y + w * 0.75} ${x + w * 0.6} ${y}" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`;
  }

  function face(expr, eyes, r, m, w, opts = {}) {
    return brows(expr, eyes, r, opts.brow) + eyes.map(([x, y]) => eye(x, y, r, expr, opts.arc)).join("") + mouth(m[0], m[1], w, expr);
  }

  const cheeks = (a, b, color = "#ff9db0") =>
    `<circle cx="${a[0]}" cy="${a[1]}" r="5" fill="${color}" opacity=".5"/><circle cx="${b[0]}" cy="${b[1]}" r="5" fill="${color}" opacity=".5"/>`;

  const tileText = 'font-family="Nunito, system-ui, sans-serif" font-weight="800" text-anchor="middle"';

  // Spider-Man's mask lenses carry his whole expression.
  function lens(cx, cy, side, expr) {
    const st = 'fill="#fff" stroke="#1d1d1d" stroke-width="3.6" stroke-linejoin="round"';
    if (expr === "happy") {
      return `<path d="M${cx - 12} ${cy + 3} Q${cx} ${cy - 13} ${cx + 12} ${cy + 3} Q${cx} ${cy - 3} ${cx - 12} ${cy + 3} Z" ${st}/>`;
    }
    if (expr === "sad") {
      return `<ellipse cx="${cx}" cy="${cy + 2}" rx="11" ry="7" transform="rotate(${22 * side} ${cx} ${cy + 2})" ${st}/>`;
    }
    if (expr === "think" && side === 1) {
      return `<ellipse cx="${cx}" cy="${cy}" rx="11" ry="4" transform="rotate(-18 ${cx} ${cy})" ${st}/>`;
    }
    return `<ellipse cx="${cx}" cy="${cy}" rx="12" ry="8.5" transform="rotate(${-20 * side} ${cx} ${cy})" ${st}/>`;
  }

  // Iron Man's glowing eye slits.
  function slit(cx, cy, side, expr) {
    const glow = 'fill="#e6fdff" stroke="#4dd0e1" stroke-width="2"';
    if (expr === "happy") {
      return `<path d="M${cx - 8} ${cy + 3} Q${cx} ${cy - 6} ${cx + 8} ${cy + 3}" fill="none" stroke="#b3f5ff" stroke-width="4.5" stroke-linecap="round"/>`;
    }
    const o = cx + 8 * side, i = cx - 8 * side; // outer and inner x
    if (expr === "sad") return `<path d="M${o} ${cy + 1} L${i} ${cy - 4} L${i} ${cy + 1} L${o} ${cy + 5} Z" ${glow}/>`;
    if (expr === "think" && side === 1) return `<path d="M${o} ${cy} L${i} ${cy} L${i} ${cy + 2.5} L${o} ${cy + 2.5} Z" ${glow}/>`;
    return `<rect x="${cx - 8}" y="${cy - 2}" width="16" height="5.5" rx="2.5" ${glow}/>`;
  }

  const drawings = {
    wolverine: (e) => `
      <g stroke="#cfd8dc" stroke-width="3.2" stroke-linecap="round">
        <line x1="20" y1="92" x2="7" y2="62"/><line x1="24" y1="91" x2="17" y2="58"/><line x1="28" y1="92" x2="27" y2="61"/>
        <line x1="100" y1="92" x2="113" y2="62"/><line x1="96" y1="91" x2="103" y2="58"/><line x1="92" y1="92" x2="93" y2="61"/>
      </g>
      <path d="M34 92 Q60 84 86 92 L90 120 L30 120 Z" fill="#ffc800"/>
      <path d="M34 92 L45 89 L42 120 L30 120 Z M86 92 L75 89 L78 120 L90 120 Z" fill="#1f4fbf"/>
      <rect x="38" y="108" width="44" height="5" rx="2" fill="#e0a800"/>
      <circle cx="24" cy="98" r="9" fill="#1f4fbf"/><circle cx="96" cy="98" r="9" fill="#1f4fbf"/>
      <path d="M33 40 Q20 22 13 5 Q30 15 42 29 Z M87 40 Q100 22 107 5 Q90 15 78 29 Z" fill="#1d1d1d"/>
      <circle cx="60" cy="54" r="32" fill="#f6c9a0"/>
      <path d="M31 66 Q33 80 45 85 L42 70 Z M89 66 Q87 80 75 85 L78 70 Z" fill="#3a2a1e"/>
      <path d="M28 62 Q28 22 60 22 Q92 22 92 62 Q76 55 60 58 Q44 55 28 62 Z" fill="#ffc800"/>
      <path d="M31 54 Q37 39 53 47 Q57 55 51 61 Q38 62 31 54 Z M89 54 Q83 39 67 47 Q63 55 69 61 Q82 62 89 54 Z" fill="#1d1d1d"/>
      ${face(e, [[45, 53], [75, 53]], 7.5, [60, 73], 7, { arc: "#fff", brow: "#ffc800" })}`,

    antman: (e) => `
      <line x1="48" y1="24" x2="36" y2="5" stroke="#90a4ae" stroke-width="3" stroke-linecap="round"/>
      <line x1="72" y1="24" x2="84" y2="5" stroke="#90a4ae" stroke-width="3" stroke-linecap="round"/>
      <circle cx="36" cy="5" r="3" fill="#90a4ae"/><circle cx="84" cy="5" r="3" fill="#90a4ae"/>
      <path d="M36 94 Q60 86 84 94 L88 120 L32 120 Z" fill="#e53935"/>
      <rect x="36" y="106" width="48" height="6" rx="2" fill="#263238"/>
      <circle cx="28" cy="104" r="7.5" fill="#263238"/><circle cx="92" cy="104" r="7.5" fill="#263238"/>
      <circle cx="60" cy="54" r="34" fill="#e53935"/>
      <rect x="55" y="20" width="10" height="18" rx="5" fill="#cfd8dc"/>
      <path d="M36 68 Q60 96 84 68 Q60 77 36 68 Z" fill="#cfd8dc"/>
      <path d="M48 80 L50 86 M56 82 L56 89 M64 82 L64 89 M72 80 L70 86" stroke="#90a4ae" stroke-width="2" stroke-linecap="round"/>
      <ellipse cx="45" cy="53" rx="13" ry="12" fill="#1d2a33"/><ellipse cx="75" cy="53" rx="13" ry="12" fill="#1d2a33"/>
      ${brows(e, [[45, 53], [75, 53]], 8.5, "#fff")}
      ${eye(45, 53, 8.5, e, "#fff")}${eye(75, 53, 8.5, e, "#fff")}
      ${mouth(60, 75, 6, e)}
      <g fill="#1d1d1d"><circle cx="104" cy="88" r="3.4"/><circle cx="99" cy="90" r="2.6"/><circle cx="109" cy="86" r="2.6"/></g>
      <path d="M99 92 L96 96 M104 91 L104 96 M108 89 L111 93 M110 84 L113 80" stroke="#1d1d1d" stroke-width="1.4" stroke-linecap="round"/>`,

    hulk: (e) => `
      <path d="M20 102 Q60 82 100 102 L102 120 L18 120 Z" fill="#5fb236"/>
      <path d="M44 102 Q52 108 60 104 Q68 108 76 102" fill="none" stroke="#2e7d32" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M24 116 L96 116 L98 120 L22 120 Z" fill="#7b3fa0"/>
      <circle cx="15" cy="104" r="12" fill="#5fb236"/><circle cx="105" cy="104" r="12" fill="#5fb236"/>
      <path d="M10 100 Q15 97 20 100 M100 100 Q105 97 110 100" fill="none" stroke="#2e7d32" stroke-width="2" stroke-linecap="round"/>
      <path d="M27 50 Q27 18 60 18 Q93 18 93 50 L93 64 Q93 90 60 90 Q27 90 27 64 Z" fill="#6abf3c"/>
      <path d="M25 48 Q22 14 60 12 Q98 14 95 48 L89 34 L85 42 L79 29 L73 38 L65 27 L59 37 L51 27 L45 37 L39 29 L35 42 Z" fill="#1d1d1d"/>
      ${e === "idle" || e === "happy" ? `<path d="M35 43 Q46 39 55 45 M85 43 Q74 39 65 45" fill="none" stroke="#2e7d32" stroke-width="4" stroke-linecap="round"/>` : ""}
      ${face(e, [[46, 55], [74, 55]], 8.5, [60, 73], 10, { brow: "#1d1d1d" })}`,

    fury: (e) => `
      <path d="M34 92 Q60 84 86 92 L90 120 L30 120 Z" fill="#37474f"/>
      <path d="M43 91 L56 120 M77 91 L64 120" stroke="#eceff1" stroke-width="4"/>
      <path d="M48 88 L60 96 L72 88" fill="#263238"/>
      <circle cx="60" cy="55" r="31" fill="#f2c09a"/>
      <path d="M29 50 Q29 21 60 21 Q91 21 91 50 Q85 33 60 33 Q35 33 29 50 Z" fill="#4e342e"/>
      <path d="M29 50 Q29 40 33 35 L36 51 Z M91 50 Q91 40 87 35 L84 51 Z" fill="#b0bec5"/>
      <path d="M44 74 Q60 86 76 74 Q74 84 60 86 Q46 84 44 74 Z" fill="#8d6e63" opacity=".45"/>
      <path d="M30 45 L90 37" stroke="#1d1d1d" stroke-width="3"/>
      <circle cx="46" cy="54" r="9.5" fill="#1d1d1d"/>
      ${e === "sad" ? `<path d="M82 45 L67 41" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>` : e === "think" ? `<path d="M66 43 Q74 38 82 42" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>` : `<path d="M66 44 L82 43" stroke="#4e342e" stroke-width="3" stroke-linecap="round"/>`}
      ${eye(74, 54, 8, e)}
      ${mouth(60, 72, 7, e)}`,

    spidey: (e) => `
      <path d="M34 92 Q60 84 86 92 L90 120 L30 120 Z" fill="#1f4fbf"/>
      <path d="M46 89 Q60 86 74 89 L72 120 L48 120 Z" fill="#e23636"/>
      <g stroke="#1d1d1d" stroke-width="1.6" stroke-linecap="round"><line x1="60" y1="94" x2="60" y2="106"/><path d="M54 95 L60 99 L66 95 M54 105 L60 101 L66 105" fill="none"/></g>
      <circle cx="60" cy="100" r="2.6" fill="#1d1d1d"/>
      <circle cx="25" cy="100" r="7.5" fill="#e23636"/><circle cx="95" cy="100" r="7.5" fill="#e23636"/>
      <path d="M95 93 L113 30" stroke="#b0bec5" stroke-width="1.6"/>
      <ellipse cx="60" cy="52" rx="33" ry="35" fill="#e23636"/>
      <g fill="none" stroke="#8e1b1b" stroke-width="1.3" opacity=".55">
        <path d="M60 58 L60 17 M60 58 L37 26 M60 58 L83 26 M60 58 L27 52 M60 58 L93 52 M60 58 L35 79 M60 58 L85 79 M60 58 L60 87"/>
        <ellipse cx="60" cy="57" rx="13" ry="12"/><ellipse cx="60" cy="55" rx="25" ry="25"/>
      </g>
      ${lens(45, 50, -1, e)}${lens(75, 50, 1, e)}
      ${mouth(60, 74, 6, e)}`,

    loki: (e) => `
      <path d="M44 30 C40 12 30 3 21 5 C31 9 35 19 35 36 Z M76 30 C80 12 90 3 99 5 C89 9 85 19 85 36 Z" fill="#ffc800"/>
      <path d="M22 96 Q60 80 98 96 L106 120 L14 120 Z" fill="#1b5e20"/>
      <path d="M38 92 Q60 86 82 92 L84 120 L36 120 Z" fill="#43a047"/>
      <path d="M44 92 L60 104 L76 92" fill="none" stroke="#ffc800" stroke-width="4" stroke-linejoin="round"/>
      <path d="M30 50 Q25 80 34 94 L41 70 Z M90 50 Q95 80 86 94 L79 70 Z" fill="#1d1d1d"/>
      <circle cx="60" cy="57" r="28" fill="#f5d9c6"/>
      <path d="M31 52 Q31 25 60 25 Q89 25 89 52 Q85 44 76 42 L60 53 L44 42 Q35 44 31 52 Z" fill="#ffc800"/>
      <path d="M44 42 L60 53 L76 42" fill="none" stroke="#e0a800" stroke-width="2"/>
      ${cheeks([40, 70], [80, 70])}
      ${brows(e, [[48, 61], [72, 61]], 7)}
      ${eye(48, 61, 7, e)}${eye(72, 61, 7, e)}
      ${e === "idle" ? `<path d="M52 74 Q61 79 68 71" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>` : mouth(60, 74, 7, e)}
      <g transform="rotate(-14 13 66)"><rect x="1" y="59" width="24" height="13" rx="4" fill="#fff" stroke="#d5dde1" stroke-width="1.6"/><text x="13" y="68.5" ${tileText} font-size="8" fill="#4b4b4b">ball</text></g>
      <g transform="rotate(14 107 66)"><rect x="95" y="59" width="24" height="13" rx="4" fill="#fff" stroke="#d5dde1" stroke-width="1.6"/><text x="107" y="68.5" ${tileText} font-size="8" fill="#4b4b4b">dog</text></g>`,

    ironman: (e) => `
      <path d="M34 92 Q60 84 86 92 L90 120 L30 120 Z" fill="#c62828"/>
      <path d="M48 106 L72 106 L70 120 L50 120 Z" fill="#ffc107"/>
      <circle cx="60" cy="98" r="6" fill="#b3f5ff" stroke="#4dd0e1" stroke-width="2.6"/>
      <circle cx="26" cy="102" r="8" fill="#ffc107"/><circle cx="94" cy="102" r="8" fill="#ffc107"/>
      <path d="M28 52 Q28 18 60 18 Q92 18 92 52 L90 70 Q86 88 60 90 Q34 88 30 70 Z" fill="#c62828"/>
      <path d="M36 40 Q60 33 84 40 L84 62 Q82 80 70 86 L50 86 Q38 80 36 62 Z" fill="#ffc107"/>
      <path d="M41 66 L49 71 M79 66 L71 71" stroke="#d4a000" stroke-width="2" stroke-linecap="round"/>
      ${slit(46, 53, -1, e)}${slit(74, 53, 1, e)}
      ${e === "happy" ? `<path d="M50 75 Q60 83 70 75" fill="none" stroke="#8a6d00" stroke-width="3" stroke-linecap="round"/>`
        : e === "sad" ? `<path d="M51 80 Q60 73 69 80" fill="none" stroke="#8a6d00" stroke-width="3" stroke-linecap="round"/>`
        : e === "think" ? `<path d="M53 78 L67 76" stroke="#8a6d00" stroke-width="3" stroke-linecap="round"/>`
        : `<path d="M52 77 L68 77" stroke="#8a6d00" stroke-width="3" stroke-linecap="round"/>`}`,
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
      name: "Hulk", role: "The Counter", color: "#6abf3c", dark: "#7b3fa0",
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
      `<svg class="char ${cls}" viewBox="0 0 120 120" role="img" aria-label="${c.name}, ${c.role}">${drawings[id](expr)}</svg>`;
  }

  window.TL_CHARS = CHARS;
})();
