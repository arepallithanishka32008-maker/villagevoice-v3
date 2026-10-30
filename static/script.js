const $ = (s, r = document) => r.querySelector(s);
const TE = () => document.documentElement.lang === "te";
const csrfToken = () => {
  const m = $('meta[name="csrf"]');
  return m ? m.content : "";
};
function toast(msg, ms = 7000) {
  const t = $("#toast");
  if (!t) {
    alert(msg);
    return;
  }
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast.h);
  toast.h = setTimeout(() => t.classList.remove("show"), ms);
}
document.addEventListener("DOMContentLoaded", () => {
  const m = $("#menu");
  if (m) m.onclick = () => document.body.classList.toggle("menuopen");
  document.querySelectorAll('form[method="post"]').forEach(f => {
    if (!f.querySelector('input[name="csrf"]')) {
      const i = document.createElement("input");
      i.type = "hidden";
      i.name = "csrf";
      i.value = csrfToken();
      f.appendChild(i);
    }
  });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
});
async function post(url, body) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRF": csrfToken() },
    body: JSON.stringify(body),
  });
}
async function toTelugu(text) {
  const r = await post("/api/translate", { text });
  const d = await r.json();
  if (!r.ok) throw new Error(d.error || "Translation failed");
  return d.text;
}
// ---------- Telugu voice: short scripts, no repeats, ElevenLabs/Google from the server, device voice as last choice ----------
let audioEl = new Audio(),
  voiceToken = 0,
  unlocked = false,
  speaking = false;
function unlockAudio() {
  if (unlocked) return;
  unlocked = true;
  audioEl.src =
    "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=";
  const p = audioEl.play();
  if (p) p.then(() => audioEl.pause()).catch(() => {});
} // lets phones play audio later
["click", "touchstart"].forEach(e =>
  document.addEventListener(e, unlockAudio, { once: true, passive: true }),
);
function setSpeaking(on) {
  speaking = on;
  const b = $("#listenBtn");
  if (b) b.textContent = on ? "⏹" : "🔊";
}
function stopVoice() {
  voiceToken++;
  audioEl.pause();
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  setSpeaking(false);
}
function voicesReady() {
  return new Promise(res => {
    if (!("speechSynthesis" in window)) return res([]);
    const v = speechSynthesis.getVoices();
    if (v.length) return res(v);
    speechSynthesis.onvoiceschanged = () => res(speechSynthesis.getVoices());
    setTimeout(() => res(speechSynthesis.getVoices()), 1500);
  });
}
async function speakDevice(text, lang) {
  if (!("speechSynthesis" in window)) {
    toast(
      TE()
        ? "ఈ బ్రౌజర్‌లో వాయిస్ పనిచేయదు. Chrome లేదా Edge వాడండి."
        : "Voice is not supported in this browser. Use Chrome or Edge.",
    );
    return;
  }
  const vs = (await voicesReady()).filter(x =>
    x.lang.replace("_", "-").toLowerCase().startsWith(lang.slice(0, 2)),
  );
  const v = vs.find(x => /natural|online|google/i.test(x.name)) || vs[0];
  if (!v && lang.startsWith("te")) {
    toast(
      TE()
        ? "ఈ పరికరంలో తెలుగు వాయిస్ లేదు. కంప్యూటర్‌లో Microsoft Edge వాడండి. ఫోన్‌లో: Settings > Text-to-speech > Google > Install voice data > Telugu."
        : "No Telugu voice on this device. On a computer use Microsoft Edge. On a phone: Settings > Text-to-speech > Google > Install voice data > Telugu.",
      12000,
    );
    return;
  }
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang;
  if (v) u.voice = v;
  u.rate = 0.85;
  u.onend = u.onerror = () => setSpeaking(false);
  setSpeaking(true);
  speechSynthesis.speak(u);
}
const SAY = [
  [/OTP/g, "ఓటీపీ"],
  [/\bID\b/gi, "ఐడి"],
  [/GPS/g, "జీపీఎస్"],
  [/SMS/g, "ఎస్ఎంఎస్"],
  [/WhatsApp/gi, "వాట్సాప్"],
  [/Google Maps/gi, "గూగుల్ మ్యాప్స్"],
  [/VillageVoice/gi, "విలేజ్ వాయిస్"],
  [/PM-KISAN/gi, "పీఎం కిసాన్"],
  [/Aadhaar/gi, "ఆధార్"],
  [/MPDO/g, "ఎంపీడీఓ"],
  [/RBK/g, "ఆర్‌బీకే"],
  [/Sachivalayam/gi, "సచివాలయం"],
  [/Karyadarsi/gi, "కార్యదర్శి"],
  [/Kaza/gi, "కాజా"],
  [/Telugu/gi, "తెలుగు"],
  [/VV-(\d{4})-(\d+)/g, "వి వి $1 $2"],
];
function speakable(t) {
  let s = t;
  SAY.forEach(([a, b]) => {
    s = s.replace(a, b);
  });
  s = s
    .replace(/[·•|]/g, ", ")
    .replace(/[→↗↻©ⓘ]/g, " ")
    .replace(/[^\u0C00-\u0C7F\u200c\u200d0-9A-Za-z\s.,?!:;'"()\-]/g, " ");
  const seen = new Set(),
    out = [];
  s.split(/[.?!\n]+/)
    .map(x => x.replace(/\s+/g, " ").trim())
    .forEach(x => {
      if (x.length > 1 && !seen.has(x)) {
        seen.add(x);
        out.push(x);
      }
    }); // each sentence once
  return out.join(". ") + ".";
}
function chunks(t, max = 220) {
  const sents = t.match(/[^.]+\.?/g) || [t],
    out = [];
  let cur = "";
  const push = p => {
    p = p.trim();
    if (p) out.push(p);
  };
  sents.forEach(s => {
    s = s.trim();
    if (!s) return;
    if (s.length > max) {
      push(cur);
      cur = "";
      let part = "";
      s.split(" ").forEach(w => {
        if (part && (part + " " + w).length > max) {
          push(part);
          part = w;
        } else part = (part + " " + w).trim();
      });
      push(part);
      return;
    }
    if (cur && (cur + " " + s).length > max) {
      push(cur);
      cur = s;
    } else cur = (cur + " " + s).trim();
  });
  push(cur);
  return out;
}
function showSource(s) {
  if (showSource.done || !s) return;
  showSource.done = true;
  if (/^(localhost|127\.|192\.168\.|10\.)/.test(location.hostname))
    toast(
      "🔊 " +
        ({
          elevenlabs: "ElevenLabs voice",
          google: "Google Cloud voice",
          free: "Free Google voice",
        }[s] || s),
      3500,
    );
}
async function fetchAudio(text) {
  const r = await post("/api/tts", { text });
  if (!r.ok) return null;
  const d = await r.json();
  showSource(d.source);
  return "data:audio/mp3;base64," + d.audio;
}
async function playTelugu(text) {
  stopVoice();
  const my = voiceToken,
    list = chunks(speakable(text).slice(0, 1500));
  if (!list.length) return;
  setSpeaking(true);
  let next = fetchAudio(list[0]).catch(() => null);
  for (let i = 0; i < list.length; i++) {
    if (my !== voiceToken) return;
    const src = await next;
    next = i + 1 < list.length ? fetchAudio(list[i + 1]).catch(() => null) : null; // next sentence is fetched while this one plays
    if (my !== voiceToken) return;
    try {
      if (!src) throw 0;
      audioEl.src = src;
      await new Promise((res, rej) => {
        audioEl.onended = res;
        audioEl.onerror = rej;
        audioEl.play().catch(rej);
      });
    } catch (e) {
      if (my === voiceToken) speakDevice(list.slice(i).join(" "), "te-IN");
      return;
    }
  }
  if (my === voiceToken) setSpeaking(false);
}
async function speakTelugu(btn) {
  if (speaking) {
    stopVoice();
    return;
  }
  const src = btn.dataset.text || (document.getElementById(btn.dataset.target) || {}).value || "";
  const t = src.trim();
  if (!t) {
    toast(TE() ? "చదవడానికి ఏమీ లేదు." : "Nothing to read yet.");
    return;
  }
  const old = btn.innerHTML;
  btn.disabled = true;
  btn.textContent = "...";
  try {
    const te = /[\u0C00-\u0C7F]/.test(t) ? t : await toTelugu(t);
    if (btn.dataset.show) document.getElementById(btn.dataset.show).textContent = te;
    playTelugu(te);
  } catch (e) {
    toast(e.message);
  }
  btn.disabled = false;
  btn.innerHTML = old;
}
async function listenPage() {
  if (speaking) {
    stopVoice();
    return;
  }
  const m = document.querySelector('meta[name="voice-te"]');
  let t = m ? m.content.trim() : "";
  if (!t) {
    try {
      const r = await fetch(location.pathname + location.search, {
        headers: { "X-Lang": "te" },
        credentials: "same-origin",
      });
      const d = new DOMParser().parseFromString(await r.text(), "text/html");
      t = [...d.querySelectorAll("main h1,main h2,main h3,main p,main li")]
        .map(x => x.textContent)
        .join(". ");
    } catch (e) {}
  }
  if (!t.trim()) {
    toast(TE() ? "చదవడానికి ఏమీ లేదు." : "Nothing to read on this page.");
    return;
  }
  playTelugu(t);
}
function dictate(btn) {
  const R = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!R) {
    toast(TE() ? "వాయిస్ టైపింగ్ Chrome లో పనిచేస్తుంది." : "Voice typing works in Chrome.");
    return;
  }
  const r = new R();
  r.lang = btn.dataset.lang || "te-IN";
  r.interimResults = false;
  const box = document.getElementById(btn.dataset.target);
  btn.textContent = "🎙️ ...";
  r.onresult = e => {
    box.value = (box.value + " " + e.results[0][0].transcript).trim();
  };
  r.onend = r.onerror = () => {
    btn.textContent = btn.dataset.label;
  };
  r.start();
}
async function voteMe(cid, btn) {
  const r = await post("/api/vote", { cid });
  if (r.status === 401) {
    location.href = "/otp";
    return;
  }
  const d = await r.json();
  if (r.ok) {
    const n = btn.querySelector(".n");
    if (n) n.textContent = d.votes;
    btn.classList.add("on");
  }
}
async function copyTracking() {
  const e = $("#trackingCode");
  if (!e) return;
  const v = e.textContent.trim();
  try {
    await navigator.clipboard.writeText(v);
    toast(TE() ? "ఐడి కాపీ అయింది" : "Report ID copied!");
  } catch {
    window.prompt("Copy your report ID:", v);
  }
}
// ---------- maps ----------
function ensureLeaflet(ok, fail) {
  if (window.L) return ok();
  const u = [
    "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js",
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js",
  ];
  let i = 0;
  (function next() {
    if (i >= u.length) {
      if (fail) fail();
      return;
    }
    const s = document.createElement("script");
    s.src = u[i++];
    s.onload = ok;
    s.onerror = next;
    document.head.appendChild(s);
  })();
}
function kazaLayers(map, KD) {
  const te = TE(),
    E = "https://server.arcgisonline.com/ArcGIS/rest/services/";
  const T = (u, a) => L.tileLayer(u, { maxZoom: 19, attribution: a });
  const sat = T(E + "World_Imagery/MapServer/tile/{z}/{y}/{x}", "Tiles © Esri"),
    sat2 = T(E + "World_Imagery/MapServer/tile/{z}/{y}/{x}", "Tiles © Esri"),
    lab = T(
      E + "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      "Labels © Esri",
    ),
    osm = T("https://tile.openstreetmap.org/{z}/{x}/{y}.png", "© OpenStreetMap contributors");
  const hyb = L.layerGroup([sat, lab]).addTo(map);
  sat.on("tileerror", () => {
    if (!map.hasLayer(osm)) {
      map.removeLayer(hyb);
      osm.addTo(map);
    }
  });
  L.control.layers({ "Satellite + names": hyb, Map: osm, "Satellite only": sat2 }).addTo(map);
  (KD.nearby || []).forEach(n =>
    L.circleMarker([n.lat, n.lng], {
      radius: 3,
      color: "#fff",
      weight: 1,
      fillColor: "#444",
      fillOpacity: 0.9,
      interactive: false,
    })
      .addTo(map)
      .bindTooltip(te ? n.te : n.name, {
        permanent: true,
        direction: "right",
        offset: [4, 0],
        className: "nb-label",
      }),
  );
  const DIRS = ["left", "top", "right", "bottom"];
  KD.localities.forEach((l, i) => {
    const d = DIRS[i % 4],
      o = { left: [-8, 0], right: [8, 0], top: [0, -8], bottom: [0, 8] }[d];
    L.circleMarker([l.lat, l.lng], {
      radius: 6,
      color: "#fff",
      weight: 2,
      fillColor: "#173f35",
      fillOpacity: 1,
      interactive: false,
    })
      .addTo(map)
      .bindTooltip(te ? l.te : l.name, {
        permanent: true,
        direction: d,
        offset: o,
        className: "kz-label",
      });
  });
}
function addPanPad(map, reset) {
  const c = L.control({ position: "bottomleft" });
  c.onAdd = () => {
    const d = L.DomUtil.create("div", "dpad");
    d.innerHTML =
      '<span></span><button type="button" data-d="up" aria-label="Move up">▲</button><span></span><button type="button" data-d="left" aria-label="Move left">◀</button><button type="button" data-d="reset" aria-label="Show whole Kaza">◎</button><button type="button" data-d="right" aria-label="Move right">▶</button><span></span><button type="button" data-d="down" aria-label="Move down">▼</button><span></span>';
    L.DomEvent.disableClickPropagation(d);
    d.addEventListener("click", e => {
      const k = e.target.dataset && e.target.dataset.d;
      if (!k) return;
      const s = 140;
      ({
        up: () => map.panBy([0, -s]),
        down: () => map.panBy([0, s]),
        left: () => map.panBy([-s, 0]),
        right: () => map.panBy([s, 0]),
        reset,
      })[k]();
    });
    return d;
  };
  c.addTo(map);
}
// ---------- open maps and websites inside this site ----------
function openViewer(title, src, ext, hint) {
  $("#vTitle").textContent = title || "";
  $("#vMsg").hidden = true;
  $("#vAlt").hidden = true;
  $("#vFrame").hidden = false;
  $("#vFrame").src = src;
  $("#vOpen").href = ext;
  $("#vHint").textContent = hint || "";
  $("#viewer").hidden = false;
  document.body.classList.add("noscroll");
}
function viewerMsg(text, url) {
  $("#vFrame").src = "about:blank";
  $("#vFrame").hidden = true;
  $("#vHint").textContent = "";
  $("#vMsg p").textContent = text;
  $("#vMsgOpen").href = url;
  $("#vMsg").hidden = false;
}
function closeViewer() {
  $("#viewer").hidden = true;
  $("#vFrame").src = "about:blank";
  document.body.classList.remove("noscroll");
}
function viewDir(la, ln, title) {
  const go = o =>
    openViewer(
      title || "Directions",
      "https://maps.google.com/maps?" +
        (o ? "saddr=" + o + "&" : "") +
        "daddr=" +
        la +
        "," +
        ln +
        "&dirflg=d&output=embed",
      "https://www.google.com/maps/dir/?api=1&destination=" + la + "," + ln + "&travelmode=driving",
      TE() ? "మీ ఫోన్ లొకేషన్ నుండి దారి చూపిస్తుంది." : "Shows the way from where you are.",
    );
  if (navigator.geolocation)
    navigator.geolocation.getCurrentPosition(
      p => go(p.coords.latitude + "," + p.coords.longitude),
      () => go(""),
      { timeout: 5000, maximumAge: 60000 },
    );
  else go("");
}
function viewPano(la, ln, title) {
  openViewer(
    title || "Street View",
    "https://maps.google.com/maps?q=&layer=c&cbll=" +
      la +
      "," +
      ln +
      "&cbp=11,0,0,0,0&output=svembed",
    "https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=" + la + "," + ln,
    TE()
      ? "ఈ చోటు వీధి ఫోటోలు. లేకపోతే 'కొత్త ట్యాబ్' వాడండి."
      : "Street photos of this place. If none show, use New tab.",
  );
}
function viewSearch(q, title) {
  openViewer(
    title || q,
    "https://maps.google.com/maps?q=" + encodeURIComponent(q) + "&output=embed",
    "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(q),
    "",
  );
}
function viewSat(la, ln) {
  openViewer(
    TE() ? "శాటిలైట్ ఫోటో" : "Satellite view",
    "https://maps.google.com/maps?q=" + la + "," + ln + "&t=k&z=17&output=embed",
    "https://www.google.com/maps/@?api=1&map_action=map&center=" +
      la +
      "," +
      ln +
      "&zoom=17&basemap=satellite",
    "",
  );
}
function viewWeb(url, title) {
  openViewer(
    title || url,
    "/read?url=" + encodeURIComponent(url),
    url,
    TE()
      ? "ఇది టెక్స్ట్ రూపంలో చూపే రీడర్ వీక్షణ. అసలు పేజీ కోసం పై బటన్ నొక్కండి."
      : "Reader view (text). Tap the top button to try the original page here.",
  );
  const b = $("#vAlt");
  b.hidden = false;
  b.dataset.mode = "reader";
  b.textContent = TE() ? "అసలు పేజీ ఇక్కడ చూపండి" : "Show original page here";
  b.onclick = () => {
    if (b.dataset.mode === "reader") {
      $("#vFrame").src = url;
      b.dataset.mode = "orig";
      b.textContent = TE() ? "రీడర్ వీక్షణ" : "Reader view";
      $("#vHint").textContent = TE()
        ? "ఖాళీగా ఉంటే ఆ వెబ్‌సైట్ ఇక్కడ చూపడానికి అనుమతించదు. రీడర్ వీక్షణ నొక్కండి."
        : "If this stays blank, that website does not allow it. Tap Reader view.";
    } else {
      $("#vFrame").src = "/read?url=" + encodeURIComponent(url);
      b.dataset.mode = "reader";
      b.textContent = TE() ? "అసలు పేజీ ఇక్కడ చూపండి" : "Show original page here";
      $("#vHint").textContent = "";
    }
  };
}
document.addEventListener("click", e => {
  const a = e.target.closest && e.target.closest("a[href]");
  if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
  const u = a.href;
  let m;
  if (a.hasAttribute("data-embed")) {
    e.preventDefault();
    viewWeb(a.getAttribute("data-embed") || u, a.dataset.title);
  } else if ((m = u.match(/maps\/dir\/\?api=1&destination=(-?[\d.]+),(-?[\d.]+)/))) {
    e.preventDefault();
    viewDir(m[1], m[2], a.textContent.replace("↗", "").trim());
  } else if ((m = u.match(/map_action=map&center=(-?[\d.]+),(-?[\d.]+)/))) {
    e.preventDefault();
    viewSat(m[1], m[2]);
  } else if ((m = u.match(/map_action=pano&viewpoint=(-?[\d.]+),(-?[\d.]+)/))) {
    e.preventDefault();
    viewPano(m[1], m[2]);
  } else if ((m = u.match(/google\.com\/maps\/search\/\?api=1&query=([^&]+)/))) {
    e.preventDefault();
    viewSearch(decodeURIComponent(m[1]), a.textContent.replace("↗", "").trim());
  } else if ((m = u.match(/google\.com\/maps\?q=(-?[\d.]+),(-?[\d.]+)/))) {
    e.preventDefault();
    viewSearch(m[1] + "," + m[2]);
  }
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && $("#viewer") && !$("#viewer").hidden) closeViewer();
});
