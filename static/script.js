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

    toast.h = setTimeout(
        () => t.classList.remove("show"),
        ms
    );
}

document.addEventListener("DOMContentLoaded", () => {
    const m = $("#menu");

    if (m) {
        m.onclick = () => document.body.classList.toggle("menuopen");
    }

    document.querySelectorAll('form[method="post"]').forEach(f => {
        if (!f.querySelector('input[name="csrf"]')) {
            const i = document.createElement("input");

            i.type = "hidden";
            i.name = "csrf";
            i.value = csrfToken();

            f.appendChild(i);
        }
    });

    if ("serviceWorker" in navigator) {
        navigator.serviceWorker
            .register("/sw.js")
            .catch(() => {});
    }
});

async function post(url, body) {
    return fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF": csrfToken()
        },
        body: JSON.stringify(body)
    });
}

async function toTelugu(text) {
    const r = await post("/api/translate", { text });
    const d = await r.json();

    if (!r.ok) {
        throw new Error(d.error || "Translation failed");
    }

    return d.text;
}

// ---------- Telugu voice: short scripts, no repeats,
// ElevenLabs/Google from the server, device voice as last choice ----------

let audioEl = new Audio();
let voiceToken = 0;
let unlocked = false;
let speaking = false;

function unlockAudio() {
    if (unlocked) return;

    unlocked = true;

    audioEl.src =
        "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=";

    const p = audioEl.play();

    if (p) {
        p.then(() => audioEl.pause()).catch(() => {});
    }
}

// lets phones play audio later
["click", "touchstart"].forEach(e => {
    document.addEventListener(e, unlockAudio, {
        once: true,
        passive: true
    });
});

function setSpeaking(on) {
    speaking = on;

    const b = $("#listenBtn");

    if (b) {
        b.textContent = on ? "⏹" : "🔊";
    }
}

function stopVoice() {
    voiceToken++;
    audioEl.pause();

    if ("speechSynthesis" in window) {
        speechSynthesis.cancel();
    }

    setSpeaking(false);
}

function voicesReady() {
    return new Promise(res => {
        if (!("speechSynthesis" in window)) {
            return res([]);
        }

        const v = speechSynthesis.getVoices();

        if (v.length) {
            return res(v);
        }

        speechSynthesis.onvoiceschanged = () => {
            res(speechSynthesis.getVoices());
        };

        setTimeout(
            () => res(speechSynthesis.getVoices()),
            1500
        );
    });
}

async function speakDevice(text, lang) {
    if (!("speechSynthesis" in window)) {
        toast(
            TE()
                ? "ఈ బ్రౌజర్‌లో వాయిస్ పనిచేయదు. Chrome లేదా Edge వాడండి."
                : "Voice is not supported in this browser. Use Chrome or Edge."
        );

        return;
    }

    const vs = (await voicesReady()).filter(x =>
        x.lang.replace("_", "-")
            .toLowerCase()
            .startsWith(lang.slice(0, 2))
    );

    const v =
        vs.find(x => /natural|online|google/i.test(x.name)) ||
        vs[0];

    if (!v && lang.startsWith("te")) {
        toast(
            TE()
                ? "ఈ పరికరంలో తెలుగు వాయిస్ లేదు. కంప్యూటర్‌లో Microsoft Edge వాడండి. ఫోన్‌లో: Settings > Text-to-speech > Google > Install voice data > Telugu."
                : "No Telugu voice on this device. On a computer use Microsoft Edge. On a phone: Settings > Text-to-speech > Google > Install voice data > Telugu.",
            12000
        );

        return;
    }

    speechSynthesis.cancel();

    const u = new SpeechSynthesisUtterance(text);

    u.lang = lang;

    if (v) {
        u.voice = v;
    }

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
    [/VV-(\d{4})-(\d+)/g, "వి వి $1 $2"]
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

    const seen = new Set();
    const out = [];

    s.split(/[.?!\n]+/)
        .map(x => x.replace(/\s+/g, " ").trim())
        .forEach(x => {
            if (x.length > 1 && !seen.has(x)) {
                seen.add(x);
                out.push(x);
            }
        });

    // each sentence once
    return out.join(". ") + ".";
}