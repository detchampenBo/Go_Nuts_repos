// The Tokenlingo cast. Each character is drawn as an inline SVG and embodies one
// Week 5 idea. Every drawing takes an expression: idle, happy, sad or think.
(function () {
  const INK = "#22313a";

  function eye(x, y, r, expr) {
    if (expr === "happy") {
      return `<path d="M${x - r * 0.78} ${y + r * 0.3} Q${x} ${y - r * 0.95} ${x + r * 0.78} ${y + r * 0.3}" fill="none" stroke="${INK}" stroke-width="${Math.max(2.6, r * 0.34)}" stroke-linecap="round"/>`;
    }
    const dx = expr === "think" ? r * 0.3 : r * 0.1;
    const dy = expr === "think" ? -r * 0.36 : expr === "sad" ? r * 0.3 : r * 0.12;
    return `<circle cx="${x}" cy="${y}" r="${r}" fill="#fff"/>` +
      `<circle cx="${x + dx}" cy="${y + dy}" r="${r * 0.54}" fill="${INK}"/>` +
      `<circle cx="${x + dx + r * 0.2}" cy="${y + dy - r * 0.22}" r="${r * 0.17}" fill="#fff"/>`;
  }

  function brows(expr, eyes, r) {
    if (expr !== "sad" && expr !== "think") return "";
    return eyes.map(([x, y], i) => {
      const dir = i === 0 ? 1 : -1;
      if (expr === "think") {
        return i === 0 ? `<path d="M${x - r * 0.8} ${y - r * 1.45} Q${x} ${y - r * 1.9} ${x + r * 0.8} ${y - r * 1.5}" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>` : "";
      }
      return `<path d="M${x - r * 0.9 * dir} ${y - r * 1.15} L${x + r * 0.7 * dir} ${y - r * 1.6}" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`;
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

  function face(expr, eyes, r, m, w) {
    return brows(expr, eyes, r) + eyes.map(([x, y]) => eye(x, y, r, expr)).join("") + mouth(m[0], m[1], w, expr);
  }

  function cheeks(a, b, color) {
    return `<circle cx="${a[0]}" cy="${a[1]}" r="5" fill="${color}" opacity=".55"/><circle cx="${b[0]}" cy="${b[1]}" r="5" fill="${color}" opacity=".55"/>`;
  }

  const tileText = 'font-family="Nunito, system-ui, sans-serif" font-weight="800" text-anchor="middle"';

  const drawings = {
    toki: (e) => `
      <g stroke="#a7b6bd" stroke-width="6" stroke-linecap="round">
        <line x1="49" y1="46" x2="71" y2="6"/><line x1="71" y1="46" x2="49" y2="6"/>
      </g>
      <line x1="66" y1="16" x2="71" y2="6" stroke="#dfe7ea" stroke-width="2.4" stroke-linecap="round"/>
      <circle cx="60" cy="26" r="4" fill="#71828a"/>
      <ellipse cx="47" cy="112" rx="10" ry="5.5" fill="#ff9600"/>
      <ellipse cx="73" cy="112" rx="10" ry="5.5" fill="#ff9600"/>
      <ellipse cx="22" cy="78" rx="9" ry="17" fill="#58a700" transform="rotate(22 22 78)"/>
      <ellipse cx="98" cy="78" rx="9" ry="17" fill="#58a700" transform="rotate(-22 98 78)"/>
      <ellipse cx="60" cy="72" rx="38" ry="39" fill="#58cc02"/>
      <ellipse cx="60" cy="90" rx="24" ry="18" fill="#89e219"/>
      ${cheeks([33, 78], [87, 78], "#ff9db0")}
      ${face(e, [[46, 63], [74, 63]], 11.5, [60, 83], 9)}`,

    stoppy: (e) => `
      <line x1="101" y1="108" x2="101" y2="52" stroke="#a7b6bd" stroke-width="4" stroke-linecap="round"/>
      <path d="M95.2 30 L106.8 30 L115 38.2 L115 49.8 L106.8 58 L95.2 58 L87 49.8 L87 38.2 Z" fill="#ff4b4b" stroke="#fff" stroke-width="2"/>
      <text x="101" y="47.5" ${tileText} font-size="9" fill="#fff">STOP</text>
      <path d="M26 64 a32 32 0 0 1 64 0 v40 q-5.33 8 -10.67 0 q-5.33 -8 -10.67 0 q-5.33 8 -10.67 0 q-5.33 -8 -10.67 0 q-5.33 8 -10.67 0 q-5.33 -8 -10.67 0 z" fill="#cfd8dc"/>
      <ellipse cx="88" cy="74" rx="8" ry="5" fill="#cfd8dc"/>
      <rect x="42" y="82" width="32" height="15" rx="7.5" fill="#fff" opacity=".9"/>
      <text x="58" y="93" ${tileText} font-size="11" fill="#7b8a91">the</text>
      ${face(e, [[47, 60], [69, 60]], 9, [58, 74], 7)}`,

    zipfy: (e) => `
      <rect x="30" y="100" width="10" height="16" rx="5" fill="#a568cc"/>
      <rect x="52" y="102" width="10" height="14" rx="5" fill="#a568cc"/>
      <path d="M22 66 C16 98 40 106 62 104 C82 102 100 99 118 100 L118 103 C98 106 80 111 60 112 C30 114 12 96 22 66 Z" fill="#ce82ff"/>
      <circle cx="46" cy="101" r="5.5" fill="#ecc8ff"/>
      <circle cx="65" cy="104" r="3.7" fill="#ecc8ff"/>
      <circle cx="81" cy="104.6" r="2.6" fill="#ecc8ff"/>
      <circle cx="95" cy="104" r="1.8" fill="#ecc8ff"/>
      <circle cx="107" cy="103" r="1.2" fill="#ecc8ff"/>
      <path d="M22 30 l5 -12 l7 10 z M36 22 l7 -13 l7 12 z M52 26 l9 -10 l2 13 z" fill="#a568cc"/>
      <circle cx="40" cy="50" r="29" fill="#ce82ff"/>
      ${cheeks([20, 60], [60, 60], "#ff9db0")}
      ${face(e, [[30, 46], [51, 46]], 9, [40, 62], 7)}`,

    hapax: (e) => `
      <path d="M52 32 L60 3 L68 32 Z" fill="#ffc800"/>
      <path d="M55 22 L65 18 M54 28 L66 24 M57 14 L63 11" stroke="#e0a800" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M100 18 l3 7 l7 3 l-7 3 l-3 7 l-3 -7 l-7 -3 l7 -3 z" fill="#ffc800"/>
      <path d="M18 34 l2 5 l5 2 l-5 2 l-2 5 l-2 -5 l-5 -2 l5 -2 z" fill="#ffc800"/>
      <ellipse cx="46" cy="110" rx="9" ry="5" fill="#d860a8"/>
      <ellipse cx="74" cy="110" rx="9" ry="5" fill="#d860a8"/>
      <circle cx="60" cy="70" r="37" fill="#ff86d0"/>
      ${e === "sad" ? `<path d="M44 40 Q60 34 76 42" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>` : ""}
      ${eye(60, 61, 16, e)}
      <circle cx="38" cy="82" r="5" fill="#fff" opacity=".35"/><circle cx="82" cy="82" r="5" fill="#fff" opacity=".35"/>
      ${mouth(60, 88, 8, e)}`,

    gramps: (e) => `
      <circle cx="103" cy="97" r="2.6" fill="#cd7900"/><circle cx="82" cy="104" r="2.6" fill="#cd7900"/><circle cx="58" cy="104" r="2.6" fill="#cd7900"/>
      <circle cx="102" cy="86" r="12" fill="#ffb020"/>
      <circle cx="80" cy="89" r="14" fill="#ff9600"/>
      <circle cx="56" cy="88" r="15" fill="#ffb020"/>
      <text x="56" y="91" ${tileText} font-size="9" fill="#7a4300">new</text>
      <text x="80" y="92" ${tileText} font-size="9" fill="#fff">york</text>
      <text x="102" y="89" ${tileText} font-size="7.5" fill="#7a4300">city</text>
      <rect x="38" y="70" width="58" height="37" rx="18.5" fill="none" stroke="#1cb0f6" stroke-width="2.6" stroke-dasharray="5 4"/>
      <line x1="22" y1="44" x2="14" y2="24" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>
      <line x1="38" y1="43" x2="44" y2="22" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>
      <circle cx="14" cy="23" r="4" fill="#ff4b4b"/><circle cx="44" cy="21" r="4" fill="#ff4b4b"/>
      <circle cx="30" cy="62" r="22" fill="#ff9600"/>
      ${face(e, [[21, 60], [39, 60]], 6.5, [30, 74], 6)}
      <circle cx="21" cy="60" r="9" fill="none" stroke="${INK}" stroke-width="2.2"/>
      <circle cx="39" cy="60" r="9" fill="none" stroke="${INK}" stroke-width="2.2"/>
      <line x1="29.5" y1="59" x2="30.5" y2="59" stroke="${INK}" stroke-width="2.2"/>`,

    baggy: (e) => `
      <g transform="rotate(-16 40 30)"><rect x="24" y="21" width="32" height="17" rx="6" fill="#fff" stroke="#d5dde1" stroke-width="2"/><text x="40" y="33.5" ${tileText} font-size="10" fill="#4b4b4b">dog</text></g>
      <g transform="rotate(5 62 24)"><rect x="48" y="14" width="28" height="17" rx="6" fill="#fff" stroke="#d5dde1" stroke-width="2"/><text x="62" y="26.5" ${tileText} font-size="10" fill="#4b4b4b">the</text></g>
      <g transform="rotate(18 84 32)"><rect x="68" y="23" width="32" height="17" rx="6" fill="#fff" stroke="#d5dde1" stroke-width="2"/><text x="84" y="35.5" ${tileText} font-size="10" fill="#4b4b4b">ball</text></g>
      <path d="M24 54 Q10 114 60 114 Q110 114 96 54 Z" fill="#1cb0f6"/>
      <ellipse cx="60" cy="52" rx="38" ry="9" fill="#1899d6"/>
      <path d="M30 60 Q60 70 90 60" fill="none" stroke="#7fd4fb" stroke-width="3" stroke-linecap="round"/>
      <rect x="74" y="92" width="16" height="12" rx="3" fill="#7fd4fb" transform="rotate(-8 82 98)"/>
      ${face(e, [[47, 78], [73, 78]], 9.5, [60, 95], 8)}`,

    cosi: (e) => `
      <line x1="60" y1="44" x2="32" y2="10" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>
      <line x1="60" y1="44" x2="92" y2="14" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>
      <circle cx="32" cy="10" r="5.5" fill="#1cb0f6"/><circle cx="92" cy="14" r="5.5" fill="#ff4b4b"/>
      <path d="M50.5 32.5 A15 15 0 0 1 71 33.5" fill="none" stroke="#1cb0f6" stroke-width="2.6"/>
      <text x="60" y="27" ${tileText} font-size="10" fill="${INK}">θ</text>
      <ellipse cx="44" cy="110" rx="9" ry="5" fill="#e0a800"/><ellipse cx="76" cy="110" rx="9" ry="5" fill="#e0a800"/>
      <circle cx="60" cy="74" r="35" fill="#ffc800"/>
      ${cheeks([36, 82], [84, 82], "#ff9db0")}
      ${face(e, [[48, 68], [72, 68]], 9.5, [60, 87], 8)}`,
  };

  const CHARS = {
    toki: {
      name: "Toki", role: "The Tokenizer", color: "#58cc02", dark: "#58a700",
      teaches: "Tokens, types, token IDs and the subword pieces modern models read.",
      quote: "Spaces are a suggestion. I decide where the cuts go.",
      lines: ["Snip snip. Where does one token end?", "Every cut is a modelling choice.", "Raw characters in, tokens out."],
    },
    stoppy: {
      name: "Stoppy", role: "The Stopword", color: "#cfd8dc", dark: "#9aa7ad",
      teaches: "Preprocessing: lowercasing, stopwords and lemmatization, and what each throws away.",
      quote: "I'm the most common word in English and everyone filters me out.",
      lines: ["Careful what you clean. Something always leaves with me.", "the, of, in... we're everywhere.", "Every cleaning step deletes information."],
    },
    zipfy: {
      name: "Zipfy", role: "The Long Tail", color: "#ce82ff", dark: "#a568cc",
      teaches: "Counting, rank and frequency, and Zipf's law on linear and log-log axes.",
      quote: "My spots shrink like word frequencies: one over rank.",
      lines: ["Count first, model later.", "A few words everywhere, the rest almost nowhere.", "Log-log axes make my tail look straight."],
    },
    hapax: {
      name: "Hapax", role: "Seen Only Once", color: "#ff86d0", dark: "#d860a8",
      teaches: "Hapax types, the words that appear exactly once in a corpus.",
      quote: "You'll only ever meet me once. Make it count.",
      lines: ["I appear exactly once.", "More than a third of Marvel's types are like me.", "Rare, but never gone."],
    },
    gramps: {
      name: "Gramps", role: "The N-gram", color: "#ff9600", dark: "#cd7900",
      teaches: "N-grams, concordances, similar() and collocations: words in context.",
      quote: "Look at the neighbours. 'New' means more next to 'York'.",
      lines: ["Slide the window over my segments.", "Context first, conclusions later.", "A count can't tell you how a word is used."],
    },
    baggy: {
      name: "Baggy", role: "The Bag of Words", color: "#1cb0f6", dark: "#1899d6",
      teaches: "Bag of Words, document vectors and the document-term matrix.",
      quote: "Throw in a document, shake it, and I'll tell you the counts. Order? Never heard of it.",
      lines: ["Shake shake. The order falls out.", "Rows are documents, columns are words.", "Same words, same vector. Meaning not included."],
    },
    cosi: {
      name: "Cosi", role: "The Cosine", color: "#ffc800", dark: "#e0a800",
      teaches: "Cosine similarity between documents, and why counts know nothing about meaning.",
      quote: "Length doesn't matter to me. Only the angle does.",
      lines: ["Same direction? Then we're similar.", "dog and puppy are at right angles. For now.", "Next week, words get vectors of their own."],
    },
  };

  for (const [id, c] of Object.entries(CHARS)) {
    c.id = id;
    c.svg = (expr = "idle", cls = "") =>
      `<svg class="char ${cls}" viewBox="0 0 120 120" role="img" aria-label="${c.name}, ${c.role}">${drawings[id](expr)}</svg>`;
  }

  window.TL_CHARS = CHARS;
})();
