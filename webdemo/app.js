// ============================================================================
// Evil Twin – Interaktive Live-Demo
// Läuft vollständig lokal im Browser. Simuliert Netzwerkverhalten rein visuell;
// es werden keine echten WLAN-Signale gesendet oder echte Geräte angesprochen.
// ============================================================================

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}, ...children) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  children.forEach((c) => c && e.appendChild(c));
  return e;
}

function randHex(len) {
  let s = "";
  for (let i = 0; i < len; i++) s += Math.floor(Math.random() * 16).toString(16);
  return s.toUpperCase();
}

function randomBssidPair() {
  const prefix = `02:${randHex(2)}:${randHex(2)}:${randHex(2)}`;
  return { legit: `${prefix}:00:11`, evil: `${prefix}:00:22` };
}

// ----------------------------------------------------------------------------
// Zustand
// ----------------------------------------------------------------------------
const initialBssids = randomBssidPair();

const state = {
  ssid: "Seminar-Gast",
  bssidLegit: initialBssids.legit,
  bssidEvil: initialBssids.evil,
  security: "wpa2", // open | wpa2 | wpa3
  legitSignal: 55,
  evilSignal: 85,
  deauthOn: true,
  portalOn: true,
  speed: 2,
  stepIdx: 0,
  playing: false,
};

let playTimer = null;

// ----------------------------------------------------------------------------
// Positionen der Knoten im 1000x560-Koordinatensystem
// ----------------------------------------------------------------------------
const POS = {
  legit: { x: 150, y: 120 },
  evil: { x: 150, y: 420 },
  attacker: { x: 385, y: 420 },
  client: { x: 575, y: 260 },
  cloud: { x: 870, y: 120 },
  wids: { x: 870, y: 420 },
};

// ----------------------------------------------------------------------------
// Schritt-Definitionen
// Jeder Schritt liefert: title, desc, logRows(state)->[...], phone(state)->key+payload,
// und wird in render() ausgewertet, um Sichtbarkeiten/Kanten/Annotationen zu setzen.
// ----------------------------------------------------------------------------
function winner(s) {
  return s.evilSignal >= s.legitSignal ? "evil" : "legit";
}

function fmtTime(offsetMs) {
  const base = new Date(2026, 0, 1, 10, 0, 0, 0);
  base.setMilliseconds(base.getMilliseconds() + offsetMs);
  return base.toLocaleTimeString("de-DE", { hour12: false }) + "." + String(offsetMs % 1000).padStart(3, "0").slice(0, 2);
}

const ALL_STEPS = [
  {
    key: "start",
    title: "Ausgangslage",
    desc: "Das Opfergerät ist regulär mit dem legitimen Access Point verbunden. Beacons kündigen Name (SSID) und Adresse (BSSID) unverschlüsselt an.",
    optional: null,
    logRows: (s) => [
      ["beacon", `${s.bssidLegit} → *`, `SSID "${s.ssid}", Kanal 6`],
      ["auth", `Client ↔ ${s.bssidLegit}`, "Authentication / Association OK"],
    ],
    phone: (s) => ({ kind: "single", connected: "legit" }),
  },
  {
    key: "clone",
    title: "Angreifer klont den Netznamen",
    desc: "Ein zweiter Access Point sendet dieselbe SSID unter einer anderen BSSID. Für Nutzer und Gerät sieht das WLAN identisch aus.",
    optional: null,
    logRows: (s) => [
      ["beacon", `${s.bssidEvil} → *`, `SSID "${s.ssid}" (Duplikat!), Kanal 11`],
    ],
    phone: (s) => ({ kind: "list", connected: "legit" }),
  },
  {
    key: "deauth",
    title: "Deauthentication",
    desc: "Der Angreifer gibt sich als legitimer AP aus und sendet einen Trennungs-Frame an das Opfergerät.",
    optional: "deauthOn",
    logRows: (s) => {
      if (s.security === "wpa3") {
        return [["deauth", `${s.bssidLegit} (gespooft) → Client`, "Verworfen — PMF (802.11w) aktiv"]];
      }
      return [["deauth", `${s.bssidLegit} (gespooft) → Client`, "Angenommen — Verbindung getrennt"]];
    },
    phone: (s) => ({ kind: "list", connected: s.security === "wpa3" ? "legit" : null }),
  },
  {
    key: "scan",
    title: "Erneuter Scan",
    desc: "Das Gerät sucht aktiv nach bekannten Netzen. Beide Access Points antworten mit identischem Namen, aber unterschiedlicher Signalstärke.",
    optional: null,
    logRows: (s) => [
      ["probe", `Client → ${s.bssidLegit}`, `Probe Response, RSSI ${rssiFromPct(s.legitSignal)} dBm`],
      ["probe", `Client → ${s.bssidEvil}`, `Probe Response, RSSI ${rssiFromPct(s.evilSignal)} dBm`],
    ],
    phone: (s) => ({ kind: "list", connected: null }),
  },
  {
    key: "choice",
    title: "Verbindungswahl",
    desc: "Das Gerät verbindet sich automatisch mit dem Netz der höheren Signalqualität — unabhängig davon, wer es betreibt.",
    optional: null,
    logRows: (s) => {
      const w = winner(s);
      const bssid = w === "evil" ? s.bssidEvil : s.bssidLegit;
      return [["auth", `Client ↔ ${bssid}`, `Reassociation (${w === "evil" ? "Evil Twin" : "legitimer AP"})`]];
    },
    phone: (s) => ({ kind: "list", connected: winner(s) }),
  },
  {
    key: "portal",
    title: "Portal / Phishing-Seite",
    desc: "Nach dem Verbindungsaufbau erscheint eine Anmeldeseite. Ist der Client beim Evil Twin, stammt sie vom Angreifer.",
    optional: "portalOn",
    logRows: (s) => {
      const w = winner(s);
      if (w === "evil") {
        return [["http", "Client → Angreifer:80", "GET /portal — Zugangsdaten im Klartext sichtbar"]];
      }
      return [["http", `Client → ${s.bssidLegit}:80`, "GET /portal — regulärer Gastzugang"]];
    },
    phone: (s) => ({ kind: "portal", connected: winner(s) }),
  },
  {
    key: "mitm",
    title: "Man-in-the-Middle",
    desc: "Ist der Angreifer zwischengeschaltet, sieht er unverschlüsselten Datenverkehr. Korrekt geprüftes HTTPS bleibt inhaltlich geschützt.",
    optional: null,
    logRows: (s) => {
      const w = winner(s);
      if (w === "evil") {
        return [
          ["http", "Client → Angreifer → Internet", "HTTP: Inhalt im Klartext lesbar"],
          ["https", "Client → Angreifer → Internet", "HTTPS: Inhalt verschlüsselt, nur Metadaten sichtbar"],
        ];
      }
      return [["https", `Client → ${s.bssidLegit} → Internet`, "Regulärer, nicht abgefangener Pfad"]];
    },
    phone: (s) => ({ kind: "portal", connected: winner(s) }),
  },
  {
    key: "defense",
    title: "Erkennung & Abwehr",
    desc: "Ein WIDS-Sensor erkennt dieselbe SSID unter einer unbekannten BSSID und meldet eine Anomalie.",
    optional: null,
    logRows: (s) => [
      ["alert", `WIDS → Betrieb`, `Duplicate-SSID-Alarm: "${s.ssid}" an unbekannter BSSID ${s.bssidEvil}`],
    ],
    phone: (s) => ({ kind: "portal", connected: winner(s) }),
  },
];

function rssiFromPct(pct) {
  // 100% -> -30 dBm (sehr stark), 10% -> -90 dBm (sehr schwach)
  return Math.round(-30 - (100 - pct) * 0.65);
}

function activeSteps() {
  return ALL_STEPS.filter((st) => !st.optional || state[st.optional]);
}

function clampStepIdx() {
  const steps = activeSteps();
  if (state.stepIdx > steps.length - 1) state.stepIdx = steps.length - 1;
  if (state.stepIdx < 0) state.stepIdx = 0;
}

// ----------------------------------------------------------------------------
// DOM-Referenzen
// ----------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const appEl = $("app");
const svg = $("topoSvg");
const stepbarEl = $("stepbar");
const stepIndexLabel = $("stepIndexLabel");
const stepTitleEl = $("stepTitle");
const stepDescEl = $("stepDesc");
const logBody = $("logBody");
const logWrap = document.querySelector(".log-table-wrap");
const phoneScreen = $("phoneScreen");
const bssidLegitEl = $("bssidLegit");
const bssidEvilEl = $("bssidEvil");
const securityHintEl = $("securityHint");

// ----------------------------------------------------------------------------
// SVG-Grundstruktur einmalig aufbauen
// ----------------------------------------------------------------------------
const layers = {
  edges: svgEl("g", { id: "layerEdges" }),
  nodes: svgEl("g", { id: "layerNodes" }),
  fx: svgEl("g", { id: "layerFx" }),
  annotations: svgEl("g", { id: "layerAnnotations" }),
};
svg.appendChild(layers.edges);
svg.appendChild(layers.nodes);
svg.appendChild(layers.fx);
svg.appendChild(layers.annotations);

function iconRouter(cls) {
  return svgEl(
    "g",
    { class: cls, transform: "translate(0,-20)" },
    svgEl("path", { d: "M-10,10 L-18,-6 M10,10 L18,-6", stroke: "currentColor", "stroke-width": 2.5, "stroke-linecap": "round", fill: "none" }),
    svgEl("rect", { x: -24, y: 8, width: 48, height: 20, rx: 6, fill: "currentColor" }),
    svgEl("circle", { cx: -12, cy: 18, r: 2.4, fill: "#fff" }),
    svgEl("circle", { cx: 0, cy: 18, r: 2.4, fill: "#fff" }),
    svgEl("circle", { cx: 12, cy: 18, r: 2.4, fill: "#fff" })
  );
}

function iconLaptop(cls) {
  return svgEl(
    "g",
    { class: cls, transform: "translate(0,-18)" },
    svgEl("rect", { x: -20, y: -6, width: 40, height: 26, rx: 3, fill: "currentColor" }),
    svgEl("rect", { x: -17, y: -3, width: 34, height: 19, rx: 1.5, fill: "#fff" }),
    svgEl("path", { d: "M-26,20 L26,20 L20,26 L-20,26 Z", fill: "currentColor" })
  );
}

function iconPhone(cls) {
  return svgEl(
    "g",
    { class: cls, transform: "translate(0,-20)" },
    svgEl("rect", { x: -14, y: -16, width: 28, height: 44, rx: 7, fill: "currentColor" }),
    svgEl("rect", { x: -11, y: -11, width: 22, height: 30, rx: 2, fill: "#fff" }),
    svgEl("circle", { cx: 0, cy: 22, r: 2.2, fill: "currentColor" })
  );
}

function iconCloud(cls) {
  return svgEl("path", {
    class: cls,
    d: "M-40,10 a18,18 0 0,1 10,-33 a24,24 0 0,1 46,-4 a20,20 0 0,1 16,36 z",
    transform: "translate(0,2)",
  });
}

function iconShield(cls) {
  return svgEl(
    "g",
    { class: cls, transform: "translate(0,-6)" },
    svgEl("path", { d: "M0,-22 L20,-13 V6 C20,20 10,27 0,31 C-10,27 -20,20 -20,6 V-13 Z", fill: "currentColor" }),
    svgEl("path", { d: "M-8,2 L-2,9 L10,-6", stroke: "#fff", "stroke-width": 3, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" })
  );
}

function iconSensor(cls) {
  return svgEl(
    "g",
    { class: cls, transform: "translate(0,-10)" },
    svgEl("circle", { cx: 0, cy: 0, r: 7, fill: "currentColor" }),
    svgEl("path", { d: "M-16,-14 A24,24 0 0,1 16,-14", stroke: "currentColor", "stroke-width": 3, fill: "none", "stroke-linecap": "round" }),
    svgEl("path", { d: "M-24,-24 A36,36 0 0,1 24,-24", stroke: "currentColor", "stroke-width": 3, fill: "none", "stroke-linecap": "round", opacity: 0.55 })
  );
}

function makeNode(id, iconFn, label, extra = "") {
  const pos = POS[id];
  const g = svgEl("g", { class: `node-card`, transform: `translate(${pos.x},${pos.y})`, id: `node-${id}` });
  const rect = svgEl("rect", { class: "card-bg", x: -90, y: -50, width: 180, height: 96, rx: 16 });
  const iconWrap = svgEl("g", { color: "var(--ink)" }, iconFn("node-icon"));
  const labelText = svgEl("text", { class: "node-label", x: 0, y: 24, "text-anchor": "middle" }, document.createTextNode(label));
  const subText = svgEl("text", { class: "node-sub", x: 0, y: 40, "text-anchor": "middle" }, document.createTextNode(extra));
  g.appendChild(rect);
  g.appendChild(iconWrap);
  g.appendChild(labelText);
  g.appendChild(subText);
  const tag = svgEl("g", { class: "node-tag-wrap", opacity: 0 });
  const tagBg = svgEl("rect", { class: "tag-bg", x: -46, y: -72, width: 92, height: 20, rx: 10 });
  const tagText = svgEl("text", { x: 0, y: -58, "text-anchor": "middle", class: "node-tag" }, document.createTextNode("EVIL TWIN"));
  tag.appendChild(tagBg);
  tag.appendChild(tagText);
  g.appendChild(tag);
  layers.nodes.appendChild(g);
  return { g, rect, iconWrap, labelText, subText, tag };
}

function makeEdge(id, from, to) {
  const p1 = POS[from];
  const p2 = POS[to];
  const midX = (p1.x + p2.x) / 2;
  const midY = (p1.y + p2.y) / 2;
  const curveOffset = from === "attacker" || to === "attacker" ? 0 : 18;
  const path = svgEl("path", {
    id: `edge-${id}`,
    class: "edge-line neutral",
    d: `M${p1.x},${p1.y} Q${midX},${midY - curveOffset} ${p2.x},${p2.y}`,
  });
  layers.edges.appendChild(path);
  return path;
}

const nodes = {
  legit: makeNode("legit", iconRouter, "Campus-Access-Point", ""),
  evil: makeNode("evil", iconRouter, "Zweiter Access Point", ""),
  attacker: makeNode("attacker", iconLaptop, "Angreifer", "steuert den Zwilling"),
  client: makeNode("client", iconPhone, "Opfergerät", ""),
  cloud: makeNode("cloud", iconCloud, "Internet", ""),
  wids: makeNode("wids", iconSensor, "WIDS-Sensor", "Überwachung"),
};
nodes.cloud.rect.setAttribute("rx", 48);

const edges = {
  legitClient: makeEdge("legit-client", "legit", "client"),
  evilClient: makeEdge("evil-client", "evil", "client"),
  attackerEvil: makeEdge("attacker-evil", "attacker", "evil"),
  legitCloud: makeEdge("legit-cloud", "legit", "cloud"),
  attackerCloud: makeEdge("attacker-cloud", "attacker", "cloud"),
  widsEvil: makeEdge("wids-evil", "wids", "evil"),
};

function setNodeVisible(node, visible) {
  node.g.style.opacity = visible ? "1" : "0";
  node.g.style.pointerEvents = visible ? "auto" : "none";
}

function setEdgeState(edge, { visible = true, cls = "neutral", dashed = false } = {}) {
  edge.style.opacity = visible ? "1" : "0";
  edge.setAttribute("class", `edge-line ${cls}${dashed ? " dashed" : ""}`);
}

// ----------------------------------------------------------------------------
// Paket-Flug-Animation (eine kleine Markierung entlang einer Bezierkurve)
// ----------------------------------------------------------------------------
function flyPacket(from, to, { color = "var(--red)", label = "", duration = 1100, curveUp = true } = {}) {
  const p1 = POS[from];
  const p2 = POS[to];
  const midX = (p1.x + p2.x) / 2;
  const midY = (p1.y + p2.y) / 2 - (curveUp ? 24 : -24);

  const g = svgEl("g", { class: "packet-dot" });
  const dot = svgEl("circle", { r: 8, fill: color });
  const txt = svgEl("text", { y: -14, "text-anchor": "middle", fill: color, "font-size": 11, "font-weight": 700, "font-family": "var(--font)" }, document.createTextNode(label));
  g.appendChild(dot);
  if (label) g.appendChild(txt);
  layers.fx.appendChild(g);

  const start = performance.now();
  function frame(now) {
    const t = Math.min(1, (now - start) / duration);
    const x = (1 - t) * (1 - t) * p1.x + 2 * (1 - t) * t * midX + t * t * p2.x;
    const y = (1 - t) * (1 - t) * p1.y + 2 * (1 - t) * t * midY + t * t * p2.y;
    g.setAttribute("transform", `translate(${x},${y})`);
    g.style.opacity = t < 0.08 ? t / 0.08 : t > 0.85 ? (1 - t) / 0.15 : 1;
    if (t < 1) requestAnimationFrame(frame);
    else g.remove();
  }
  requestAnimationFrame(frame);
}

// ----------------------------------------------------------------------------
// Annotation (Sprechblasen-Text an fester Position im SVG)
// ----------------------------------------------------------------------------
function setAnnotation(text, x, y) {
  layers.annotations.innerHTML = "";
  if (!text) return;
  const t = svgEl("text", { x, y: y + 5, "text-anchor": "middle", class: "annotation" }, document.createTextNode(text));
  layers.annotations.appendChild(t); // erst einhängen, um die reale Textbreite messen zu können
  const bbox = t.getBBox();
  const padX = 16;
  const bg = svgEl("rect", {
    x: bbox.x - padX,
    y: y - 16,
    width: bbox.width + padX * 2,
    height: 34,
    rx: 10,
    class: "annotation-bg",
  });
  layers.annotations.insertBefore(bg, t);
}

// ----------------------------------------------------------------------------
// Handy-Mockup
// ----------------------------------------------------------------------------
function barsHtml(pct) {
  const level = Math.ceil(pct / 25); // 1..4
  let html = '<span class="wifi-bars">';
  for (let i = 1; i <= 4; i++) {
    const h = 3 + i * 3;
    html += `<i style="height:${h}px" class="${i <= level ? "on" : ""}"></i>`;
  }
  html += "</span>";
  return html;
}

function renderPhone(payload, s) {
  const { kind, connected } = payload;

  if (kind === "single") {
    phoneScreen.innerHTML = `
      <div class="ph-statusbar"><span>9:41</span><span>●●●●</span></div>
      <div class="ph-body">
        <div class="ph-title">WLAN</div>
        <div class="wifi-item active">
          <div style="flex:1">
            <div class="wifi-name">${s.ssid}</div>
            <span class="wifi-sub">Verbunden · ${s.bssidLegit}</span>
          </div>
          ${barsHtml(s.legitSignal)}
        </div>
      </div>`;
    return;
  }

  if (kind === "list") {
    const legitActive = connected === "legit";
    const evilActive = connected === "evil";
    phoneScreen.innerHTML = `
      <div class="ph-statusbar"><span>9:41</span><span>●●●●</span></div>
      <div class="ph-body">
        <div class="ph-title">WLAN · Netzwerke</div>
        <div class="wifi-item ${legitActive ? "active" : ""}">
          <div style="flex:1">
            <div class="wifi-name">${s.ssid}</div>
            <span class="wifi-sub">${legitActive ? "Verbunden" : "Offen"} · ${s.bssidLegit}</span>
          </div>
          ${barsHtml(s.legitSignal)}
        </div>
        <div class="wifi-item ${evilActive ? "active" : ""}">
          <div style="flex:1">
            <div class="wifi-name">${s.ssid}</div>
            <span class="wifi-sub">${evilActive ? "Verbunden" : "Offen"} · ${s.bssidEvil}</span>
          </div>
          ${barsHtml(s.evilSignal)}
        </div>
        ${!connected ? '<p style="font-size:10px;color:var(--muted);margin-top:8px;">Zwei identische Netznamen — nicht unterscheidbar.</p>' : ""}
      </div>`;
    return;
  }

  if (kind === "portal") {
    const isEvil = connected === "evil";
    phoneScreen.innerHTML = `
      <div class="ph-statusbar"><span>9:41</span><span>●●●●</span></div>
      <div class="ph-body">
        <div class="ph-title">${s.ssid} · Anmeldung</div>
        <div class="portal-card ${isEvil ? "evil" : ""}">
          <h4>${isEvil ? "⚠ Nicht verifiziertes Portal" : "Gast-Zugang"}</h4>
          <p>${isEvil ? "Dieses Portal stammt vom Angreifer und fragt gezielt Zugangsdaten ab." : "Regulärer Zugang ohne Kontoanmeldung."}</p>
          <div class="portal-input">${isEvil ? "E-Mail-Adresse" : "Nutzungsbedingungen akzeptieren"}</div>
          ${isEvil ? '<div class="portal-input">Passwort ••••••••</div>' : ""}
          <div class="portal-btn">${isEvil ? "Anmelden (simuliert)" : "Verbinden"}</div>
        </div>
        <div class="lock-row ${isEvil ? "insecure" : "secure"}">
          ${isEvil ? "⚠ HTTP — unverschlüsselt" : "🔒 Verbindung regulär"}
        </div>
      </div>`;
    return;
  }

  phoneScreen.innerHTML = "";
}

// ----------------------------------------------------------------------------
// Log-Tabelle
// ----------------------------------------------------------------------------
const FTYPE_LABEL = {
  beacon: ["BEACON", "ftype-beacon"],
  probe: ["PROBE", "ftype-probe"],
  auth: ["AUTH", "ftype-auth"],
  deauth: ["DEAUTH", "ftype-deauth"],
  http: ["HTTP", "ftype-http"],
  https: ["HTTPS", "ftype-https"],
  alert: ["ALERT", "ftype-alert"],
};

function rebuildLog() {
  const steps = activeSteps();
  logBody.innerHTML = "";
  let t = 0;
  let rowIndex = 0;
  const totalRows = steps
    .slice(0, state.stepIdx + 1)
    .reduce((acc, st) => acc + st.logRows(state).length, 0);
  for (let i = 0; i <= state.stepIdx; i++) {
    const rows = steps[i].logRows(state);
    rows.forEach((row) => {
      t += 180 + Math.floor(Math.random() * 260);
      const [type, from, details] = row;
      const [label, cls] = FTYPE_LABEL[type] || ["FRAME", "ftype-beacon"];
      const tr = document.createElement("tr");
      const isNew = i === state.stepIdx;
      if (isNew) tr.classList.add("row-new");
      tr.innerHTML = `<td>${fmtTime(t)}</td><td><span class="ftype ${cls}">${label}</span></td><td>${from}</td><td>${details}</td>`;
      logBody.appendChild(tr);
      rowIndex++;
    });
  }
  logWrap.scrollTop = logWrap.scrollHeight;
}

// ----------------------------------------------------------------------------
// Stepbar
// ----------------------------------------------------------------------------
function renderStepbar() {
  stepbarEl.innerHTML = "";
  const steps = activeSteps();
  steps.forEach((st, i) => {
    const pill = document.createElement("div");
    pill.className = "step-pill" + (i === state.stepIdx ? " active" : i < state.stepIdx ? " done" : "");
    pill.innerHTML = `<span class="num">${i + 1}</span><span class="lbl">${st.title}</span>`;
    pill.addEventListener("click", () => goTo(i));
    stepbarEl.appendChild(pill);
  });
}

// ----------------------------------------------------------------------------
// Haupt-Render
// ----------------------------------------------------------------------------
function render() {
  const steps = activeSteps();
  clampStepIdx();
  const step = steps[state.stepIdx];
  const w = winner(state);

  // --- Konfig-Spiegel ---
  bssidLegitEl.textContent = state.bssidLegit;
  bssidEvilEl.textContent = state.bssidEvil;

  // --- Sichtbarkeit der Knoten ---
  const evilVisible = state.stepIdx >= 1;
  setNodeVisible(nodes.legit, true);
  setNodeVisible(nodes.client, true);
  setNodeVisible(nodes.cloud, true);
  setNodeVisible(nodes.evil, evilVisible);
  setNodeVisible(nodes.attacker, evilVisible);
  setNodeVisible(nodes.wids, step.key === "defense");

  nodes.legit.subText.textContent = state.bssidLegit;
  nodes.evil.subText.textContent = state.bssidEvil;
  nodes.evil.tag.style.opacity = evilVisible ? "1" : "0";
  nodes.evil.g.classList.toggle("bad", evilVisible);

  // --- Kanten je nach Schritt ---
  const atLeastScan = ["scan", "choice", "portal", "mitm", "defense"].includes(step.key);
  const connectedLegit = step.key === "start" || (step.key === "deauth" && state.security === "wpa3") ||
    (["choice", "portal", "mitm", "defense"].includes(step.key) && w === "legit");
  const connectedEvil = ["choice", "portal", "mitm", "defense"].includes(step.key) && w === "evil";

  setEdgeState(edges.legitClient, {
    visible: true,
    cls: connectedLegit ? "good" : "neutral",
    dashed: !connectedLegit,
  });
  setEdgeState(edges.evilClient, {
    visible: evilVisible,
    cls: connectedEvil ? "bad" : "neutral",
    dashed: !connectedEvil,
  });
  setEdgeState(edges.attackerEvil, { visible: evilVisible, cls: "bad", dashed: true });
  setEdgeState(edges.legitCloud, { visible: true, cls: connectedLegit ? "good" : "neutral", dashed: !connectedLegit });
  setEdgeState(edges.attackerCloud, {
    visible: ["mitm", "defense"].includes(step.key) && w === "evil",
    cls: "bad",
    dashed: true,
  });
  setEdgeState(edges.widsEvil, { visible: step.key === "defense", cls: "bad", dashed: true });

  // --- Annotation ---
  let annotation = "";
  if (step.key === "choice") {
    annotation =
      w === "evil"
        ? "Stärkeres Signal gewinnt — das Gerät verbindet sich mit dem Evil Twin."
        : "Der legitime AP hat das stärkere Signal — keine Übernahme in diesem Durchlauf.";
    setAnnotation(annotation, POS.client.x, POS.client.y + 95);
  } else if (step.key === "deauth") {
    annotation = state.security === "wpa3" ? "PMF (802.11w) blockiert den Trennversuch." : "Ohne PMF wird der Frame akzeptiert.";
    setAnnotation(annotation, (POS.evil.x + POS.client.x) / 2, 300);
  } else if (step.key === "mitm" && w === "legit") {
    setAnnotation("Kein Identitätswechsel — der Datenpfad bleibt regulär.", POS.client.x, POS.client.y + 95);
  } else {
    setAnnotation("", 0, 0);
  }

  // --- Text / Stepbar / Log / Phone ---
  stepIndexLabel.textContent = `Schritt ${state.stepIdx + 1} / ${steps.length}`;
  stepTitleEl.textContent = step.title;
  stepDescEl.textContent = step.desc;
  renderStepbar();
  rebuildLog();
  renderPhone(step.phone(state), state);

  // --- Security-Hinweis ---
  const hints = {
    open: "Offenes Netz: keine Verschlüsselung, keine Authentifizierung der Gegenstelle.",
    wpa2: "WPA2: verschlüsselt, aber Management-Frames (Deauth) meist ungeschützt.",
    wpa3: "WPA3 + PMF: Management-Frames sind geschützt — Deauth wird abgewiesen.",
  };
  securityHintEl.textContent = hints[state.security];

  // --- Paket-Animationen für diesen Schritt ---
  playStepEffects(step, w);
}

let lastAnimatedStepKey = null;
function playStepEffects(step, w) {
  // Nur abspielen, wenn der Schritt neu betreten wurde (nicht bei jedem Re-Render durch Slider etc.)
  if (lastAnimatedStepKey === step.key + "-" + state.stepIdx) return;
  lastAnimatedStepKey = step.key + "-" + state.stepIdx;

  if (step.key === "clone") {
    flyPacket("evil", "client", { color: "var(--red)", label: "Beacon", duration: 900 });
  }
  if (step.key === "deauth") {
    const blocked = state.security === "wpa3";
    flyPacket("evil", "client", {
      color: blocked ? "var(--green)" : "var(--red)",
      label: blocked ? "Deauth ✕" : "Deauth",
      duration: 1000,
    });
  }
  if (step.key === "scan") {
    flyPacket("legit", "client", { color: "var(--muted)", label: "Probe", duration: 800, curveUp: false });
    setTimeout(() => flyPacket("evil", "client", { color: "var(--muted)", label: "Probe", duration: 800 }), 250);
  }
  if (step.key === "choice") {
    flyPacket(w === "evil" ? "evil" : "legit", "client", {
      color: w === "evil" ? "var(--red)" : "var(--green)",
      label: "Assoc.",
      duration: 900,
    });
  }
  if (step.key === "mitm") {
    const from = w === "evil" ? "attacker" : "legit";
    flyPacket("client", from, { color: "var(--amber)", label: "HTTP", duration: 850, curveUp: false });
    setTimeout(() => flyPacket("client", from, { color: "var(--green)", label: "HTTPS", duration: 850 }), 300);
  }
  if (step.key === "defense") {
    flyPacket("wids", "evil", { color: "var(--red)", label: "Alarm", duration: 900, curveUp: false });
  }
}

// ----------------------------------------------------------------------------
// Navigation
// ----------------------------------------------------------------------------
function goTo(i) {
  const steps = activeSteps();
  state.stepIdx = Math.max(0, Math.min(steps.length - 1, i));
  render();
}
function next() {
  const steps = activeSteps();
  if (state.stepIdx < steps.length - 1) goTo(state.stepIdx + 1);
  else pause();
}
function prev() {
  goTo(state.stepIdx - 1);
}
function play() {
  state.playing = true;
  $("btnPlay").textContent = "⏸";
  const interval = { 1: 4200, 2: 3000, 3: 1900 }[state.speed];
  clearInterval(playTimer);
  playTimer = setInterval(() => {
    const steps = activeSteps();
    if (state.stepIdx >= steps.length - 1) {
      pause();
      return;
    }
    next();
  }, interval);
}
function pause() {
  state.playing = false;
  $("btnPlay").textContent = "▶";
  clearInterval(playTimer);
}
function togglePlay() {
  state.playing ? pause() : play();
}

// ----------------------------------------------------------------------------
// Event-Listener
// ----------------------------------------------------------------------------
$("ssid").addEventListener("input", (e) => {
  state.ssid = e.target.value || "Seminar-Gast";
  render();
});

$("btnRandomize").addEventListener("click", () => {
  const b = randomBssidPair();
  state.bssidLegit = b.legit;
  state.bssidEvil = b.evil;
  render();
});

document.querySelectorAll("#securityMode .seg-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#securityMode .seg-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.security = btn.dataset.value;
    render();
  });
});

$("legitSignal").addEventListener("input", (e) => {
  state.legitSignal = Number(e.target.value);
  $("legitSignalVal").textContent = state.legitSignal + "%";
  render();
});
$("evilSignal").addEventListener("input", (e) => {
  state.evilSignal = Number(e.target.value);
  $("evilSignalVal").textContent = state.evilSignal + "%";
  render();
});

$("toggleDeauth").addEventListener("change", (e) => {
  state.deauthOn = e.target.checked;
  render();
});
$("togglePortal").addEventListener("change", (e) => {
  state.portalOn = e.target.checked;
  render();
});

$("speed").addEventListener("input", (e) => {
  state.speed = Number(e.target.value);
  if (state.playing) play();
});

$("btnReset").addEventListener("click", () => {
  pause();
  state.stepIdx = 0;
  render();
});

$("btnPrev").addEventListener("click", () => {
  pause();
  prev();
});
$("btnNext").addEventListener("click", () => {
  pause();
  next();
});
$("btnPlay").addEventListener("click", togglePlay);

$("btnPresent").addEventListener("click", () => {
  appEl.classList.toggle("present");
});

document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;
  if (e.key === "ArrowRight") {
    pause();
    next();
  }
  if (e.key === "ArrowLeft") {
    pause();
    prev();
  }
  if (e.key === " ") {
    e.preventDefault();
    togglePlay();
  }
});

// ----------------------------------------------------------------------------
// Initiales Rendern
// ----------------------------------------------------------------------------
render();
