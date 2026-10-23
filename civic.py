"""Residents: OTP + registration, reports with map pin, tracking, translation, officer (Karyadarsi) workflow, SMS."""
import os, re, math, json, time, hmac, base64, hashlib, secrets, urllib.parse, urllib.request
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from flask import Blueprint, render_template, request, session, redirect, flash, jsonify, current_app
import database as db
import threading, smtplib
from email.message import EmailMessage
from config import VILLAGES, CATEGORIES, KAZA, C_STATUS, PUBLIC, KAZA_CHECK, KAZA_PLACES, KAZA_MAXBOUNDS

bp = Blueprint("civic", __name__)
UPLOADS = Path(os.environ.get("UPLOAD_DIR", Path(__file__).parent / "static" / "uploads")); UPLOADS.mkdir(parents=True, exist_ok=True)
DEMO_OTP = os.environ.get("DEMO_OTP", "1") == "1"      # set DEMO_OTP=0 once real SMS works
now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
IN = ",".join("?" * len(PUBLIC))
OFFICER_STATUSES = ("acknowledged", "in_progress", "resolved", "rejected")

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

def in_kaza(lat, lng):
    pts, inside, j = KAZA_CHECK, False, len(KAZA_CHECK) - 1
    for i in range(len(pts)):
        yi, xi, yj, xj = pts[i][0], pts[i][1], pts[j][0], pts[j][1]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi: inside = not inside
        j = i
    return inside

def code_hash(phone, code): return hmac.new(current_app.secret_key.encode(), f"{phone}:{code}".encode(), hashlib.sha256).hexdigest()

# ---------- SMS (Twilio built in; other providers: add a branch in send_text) ----------
LAST_ERR = ""
def send_text(phone, message):
    """Send an SMS to a 10-digit Indian number. Returns True when the provider accepted it."""
    global LAST_ERR
    prov = os.environ.get("SMS_PROVIDER", "").lower(); LAST_ERR = ""
    try:
        if prov == "twilio":
            sid, tok, frm = os.environ["TWILIO_SID"], os.environ["TWILIO_TOKEN"], os.environ["TWILIO_FROM"]
            data = urllib.parse.urlencode({"To": "+91" + phone, "From": frm, "Body": message}).encode()
            req = urllib.request.Request(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json", data=data)
            req.add_header("Authorization", "Basic " + base64.b64encode(f"{sid}:{tok}".encode()).decode())
            urllib.request.urlopen(req, timeout=10).read(); return True
        if prov == "fast2sms":      # India. OTP messages use Fast2SMS's OTP route; other texts use the quick route
            q = {"authorization": os.environ["FAST2SMS_KEY"], "numbers": phone, "flash": "0"}
            m = re.search(r"OTP is (\d{4,8})", message)
            q.update({"route": "otp", "variables_values": m.group(1)} if m else {"route": "q", "message": message, "language": "english"})
            data = json.load(urllib.request.urlopen("https://www.fast2sms.com/dev/bulkV2?" + urllib.parse.urlencode(q), timeout=10))
            if data.get("return"): return True
            LAST_ERR = str(data.get("message", data)); print("SMS failed:", LAST_ERR); return False
    except Exception as e:
        LAST_ERR = str(e); print("SMS failed:", e); return False
    LAST_ERR = "SMS_PROVIDER is not set (see keys.bat)"
    print(f"[SMS not configured] +91{phone}: {message}")
    return False

def send_email(subject, body, photo=None):
    """Email the Karyadarsi. Returns (ok, detail)."""
    to, user, pw = os.environ.get("KARYADARSI_EMAIL"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")
    if not (to and user and pw): return False, "KARYADARSI_EMAIL, SMTP_USER or SMTP_PASSWORD is not set (see keys.bat)"
    try:
        m = EmailMessage(); m["Subject"] = subject; m["From"] = user; m["To"] = to; m.set_content(body)
        if photo and Path(photo).exists():
            p = Path(photo); m.add_attachment(p.read_bytes(), maintype="image", subtype="jpeg" if p.suffix == ".jpg" else p.suffix.lstrip("."), filename=p.name)
        with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", "465")), timeout=15) as s:
            s.login(user, pw); s.send_message(m)
        return True, f"sent to {to}"
    except Exception as e:
        print("email failed:", e)
        return False, ("Gmail rejected the login. Use a Gmail App password, not your normal password. " if "535" in str(e) else "") + str(e)

def test_alert():
    out = []
    phone = re.sub(r"\D", "", os.environ.get("KARYADARSI_PHONE", ""))[-10:]
    if not phone: out.append("SMS: not sent - KARYADARSI_PHONE is not set.")
    elif send_text(phone, "VillageVoice test alert. If you can read this, SMS alerts work."): out.append(f"SMS: sent to +91 {phone}.")
    else: out.append(f"SMS: not sent - {LAST_ERR}")
    ok, why = send_email("VillageVoice test alert", "If you can read this, email alerts work.\n")
    out.append("Email: " + ("sent - " if ok else "not sent - ") + why)
    return out

def notify_officer(cid):
    phone = re.sub(r"\D", "", os.environ.get("KARYADARSI_PHONE", ""))[-10:]
    if not phone: return False
    with db.connect() as c: r = c.execute("SELECT category,village,area FROM complaints WHERE complaint_id=?", (cid,)).fetchone()
    if not r: return False
    site = os.environ.get("SITE_URL", "").rstrip("/")
    return send_text(phone, f"VillageVoice: new verified report {cid} ({r['category']}, {r['village']}, {r['area']}). Open {site}/officer")

def announce(cid):
    """Send a new report to the Sachivalayam Karyadarsi at once: SMS (photo link) + email (photo attached)."""
    try:
        with db.connect() as c: r = c.execute("SELECT * FROM complaints WHERE complaint_id=?", (cid,)).fetchone()
        if not r: return
        site = os.environ.get("SITE_URL", "").rstrip("/")
        photo_url = f"{site}/static/uploads/{r['photo']}" if (r["photo"] and site) else ""
        phone = re.sub(r"\D", "", os.environ.get("KARYADARSI_PHONE", ""))[-10:]
        if phone:
            send_text(phone, (f"VillageVoice NEW {cid}: {r['category']}, {r['village']}, {r['area']}. Directions: {dir_url(r)}"
                              + (f" Photo: {photo_url}" if photo_url else "") + f" Open: {site}/officer")[:400])
        send_email(f"VillageVoice: new {r['category']} problem in {r['village']} ({cid})",
                   f"{r['description']}\n\nWhere: {r['village']}, {r['area']}\nDirections (Google Maps): {dir_url(r)}\nOpen the officer page: {site}/officer\nReport ID: {cid}\n"
                   + ("The photo is attached.\n" if r["photo"] else ""), (UPLOADS / r["photo"]) if r["photo"] else None)
    except Exception as e:
        print("announce failed:", e)

def dir_url(r):
    return f"https://www.google.com/maps/dir/?api=1&destination={r['latitude']},{r['longitude']}&travelmode=driving" if r["latitude"] else ""

def share_url(r):
    site = os.environ.get("SITE_URL", "").rstrip("/")
    lines = [f"VillageVoice report {r['complaint_id']}", f"{r['category']} - {r['village']}, {r['area']}", r["description"][:300]]
    if r["latitude"]: lines.append("Directions: " + dir_url(r))
    if r["photo"] and site: lines.append(f"Photo: {site}/static/uploads/{r['photo']}")
    if site: lines.append(f"Track: {site}/track?id={r['complaint_id']}")
    num = re.sub(r"\D", "", os.environ.get("KARYADARSI_PHONE", ""))[-10:]
    return "https://wa.me/" + ("91" + num if num else "") + "?text=" + urllib.parse.quote("\n".join(lines))

# ---------- login / registration ----------
def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("phone"):
            flash("Please verify your mobile number to report a problem.", "success"); return redirect("/otp")
        if not session.get("name"): return redirect("/register")
        return f(*a, **k)
    return w

@bp.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "GET": return render_template("otp.html", step=1)
    phone = re.sub(r"\D", "", request.form.get("phone", ""))[-10:]
    if not re.fullmatch(r"[6-9]\d{9}", phone):
        flash("Enter a valid 10-digit mobile number.", "error"); return render_template("otp.html", step=1)
    t = time.time()
    with db.connect() as c:
        if c.execute("SELECT COUNT(*) FROM otps WHERE phone=? AND created>?", (phone, t - 600)).fetchone()[0] >= 3:
            flash("Too many OTP requests. Try again after 10 minutes.", "error"); return render_template("otp.html", step=1)
        code = f"{secrets.randbelow(10**6):06d}"
        c.execute("INSERT INTO otps(phone,code_hash,expires,created) VALUES(?,?,?,?)", (phone, code_hash(phone, code), t + 300, t))
    sent = send_text(phone, f"Your VillageVoice OTP is {code}. Valid for 5 minutes. Do not share it with anyone.")
    if not sent and not DEMO_OTP:
        flash("SMS could not be sent right now. Please try again later.", "error"); return render_template("otp.html", step=1)
    session["pending"] = phone
    return render_template("otp.html", step=2, phone=phone, demo=code if (DEMO_OTP and not sent) else None)

@bp.post("/otp/verify")
def otp_verify():
    phone, code = session.get("pending"), request.form.get("code", "").strip()
    if not phone: return redirect("/otp")
    with db.connect() as c:
        row = c.execute("SELECT rowid AS rid, * FROM otps WHERE phone=? ORDER BY created DESC LIMIT 1", (phone,)).fetchone()
        if not row or row["expires"] < time.time() or row["attempts"] >= 5:
            session.pop("pending", None); flash("OTP expired. Please request a new one.", "error"); return redirect("/otp")
        c.execute("UPDATE otps SET attempts=attempts+1 WHERE rowid=?", (row["rid"],))
        ok = hmac.compare_digest(row["code_hash"], code_hash(phone, code))
        if ok: c.execute("DELETE FROM otps WHERE phone=?", (phone,))
        user = c.execute("SELECT name FROM users WHERE phone=?", (phone,)).fetchone() if ok else None
    if not ok:
        flash("Wrong OTP. Check the code and try again.", "error"); return render_template("otp.html", step=2, phone=phone)
    keep = {k: session[k] for k in ("admin", "officer") if session.get(k)}
    session.clear(); session.update(keep); session["phone"] = phone; session["csrf"] = secrets.token_hex(16)
    if user: session["name"] = user["name"]; return redirect("/report")
    return redirect("/register")

@bp.route("/register", methods=["GET", "POST"])
def register():
    phone = session.get("phone")
    if not phone: return redirect("/otp")
    if session.get("name"): return redirect("/report")
    if request.method == "POST":
        name, village = request.form.get("name", "").strip()[:80], request.form.get("village")
        if len(name) < 2 or village not in VILLAGES or not request.form.get("agree"):
            flash("Enter your name, choose your village and accept the privacy note.", "error"); return render_template("register.html")
        with db.connect() as c: c.execute("INSERT OR REPLACE INTO users(phone,name,village,created_at) VALUES(?,?,?,?)", (phone, name, village, now()))
        session["name"] = name; return redirect("/report")
    return render_template("register.html")

@bp.post("/otp/logout")
def otp_logout():
    for k in ("phone", "name", "pending"): session.pop(k, None)
    return redirect("/")

# ---------- reporting ----------
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

def save_photo(f):
    if not f or not f.filename: return None
    head = f.stream.read(12); f.stream.seek(0)
    ext = ".jpg" if head[:2] == b"\xff\xd8" else ".png" if head[:4] == b"\x89PNG" else ".webp" if head[:4] == b"RIFF" and head[8:12] == b"WEBP" else None
    if not ext: return False
    if Image:      # shrink big phone photos so they load fast and fit in email
        try:
            im = ImageOps.exif_transpose(Image.open(f.stream)); im.thumbnail((1280, 1280)); name = secrets.token_hex(8) + ".jpg"
            im.convert("RGB").save(UPLOADS / name, "JPEG", quality=80, optimize=True); return name
        except Exception: return False
    name = secrets.token_hex(8) + ext
    f.save(UPLOADS / name); return name

@bp.route("/report", methods=["GET", "POST"])
@login_required
def report():
    with db.connect() as c: u = c.execute("SELECT village FROM users WHERE phone=?", (session["phone"],)).fetchone()
    home = u["village"] if u else "Kaza"
    if request.method == "GET": return render_template("report.html", f={"village": home}, KAZA=KAZA)
    f, phone = request.form, session["phone"]
    village, cat, area, desc = f.get("village"), f.get("category"), f.get("area", "").strip()[:150], f.get("description", "").strip()
    bad = lambda m: (flash(m, "error"), render_template("report.html", f=f, KAZA=KAZA))[1]
    if village not in VILLAGES or cat not in CATEGORIES or not area or not 10 <= len(desc) <= 3000:
        return bad("Choose a village and category, enter the area, and describe the problem (at least 10 characters).")
    with db.connect() as c:
        if c.execute("SELECT COUNT(*) FROM complaints WHERE reporter_phone=? AND created_at>?", (phone, now()[:10])).fetchone()[0] >= 10:
            return bad("You can send up to 10 reports a day. Please try again tomorrow.")
    try:
        lat, lng = float(f.get("latitude")), float(f.get("longitude"))
        B = KAZA_MAXBOUNDS
        ok_pin = in_kaza(lat, lng) if village in KAZA_PLACES else (B[0][0] <= lat <= B[1][0] and B[0][1] <= lng <= B[1][1])
        if not ok_pin: return bad("The pin is outside the area for the village you chose. For Kaza places, put it inside the red outline. For other villages, put it near that village.")
    except (TypeError, ValueError): lat = lng = None
    try: acc = float(f.get("accuracy") or 0) if lat is not None else None
    except ValueError: acc = None
    photo = save_photo(request.files.get("photo"))
    if photo is False: return bad("Photo must be a JPG, PNG or WebP image.")
    t = now()
    with db.connect() as c:
        cur = c.execute("INSERT INTO complaints(complaint_id,village,area,category,description,latitude,longitude,gps_accuracy_m,photo,reporter_phone,created_at,updated_at) "
                        "VALUES('TMP',?,?,?,?,?,?,?,?,?,?,?)", (village, area, cat, desc, lat, lng, acc, photo, phone, t, t))
        cid = f"VV-{t[:4]}-{cur.lastrowid:06d}"
        c.execute("UPDATE complaints SET complaint_id=? WHERE id=?", (cid, cur.lastrowid))
        c.execute("INSERT INTO history(complaint_id,status,note,at) VALUES(?,?,?,?)", (cid, "reported", "Report received", t))
    threading.Thread(target=announce, args=(cid,), daemon=True).start()   # tell the Karyadarsi straight away
    return render_template("done.html", cid=cid, located=lat is not None, lat=lat, lng=lng)

@bp.route("/track")
def track():
    cid, c_row, hist, mine = request.args.get("id", "").strip().upper(), None, [], []
    with db.connect() as c:
        if cid:
            c_row = c.execute("SELECT complaint_id,village,area,category,status,official_reference,created_at,updated_at FROM complaints WHERE complaint_id=?", (cid,)).fetchone()
            if c_row: hist = c.execute("SELECT status,note,at FROM history WHERE complaint_id=? ORDER BY id", (cid,)).fetchall()
        if session.get("phone"):
            mine = c.execute("SELECT complaint_id,area,category,status FROM complaints WHERE reporter_phone=? ORDER BY id DESC", (session["phone"],)).fetchall()
    return render_template("track.html", cid=cid, c=c_row, hist=hist, mine=mine)

@bp.route("/api/map")
def api_map():
    with db.connect() as c:
        rows = c.execute(f"SELECT complaint_id,village,area,category,status,ROUND(latitude,5) lat,ROUND(longitude,5) lng FROM complaints WHERE latitude IS NOT NULL AND status IN ({IN})", PUBLIC).fetchall()
    return jsonify([dict(r) | {"status_name": C_STATUS[r["status"]]} for r in rows])

@bp.post("/api/translate")
def api_translate():
    if not (session.get("phone") or session.get("admin") or session.get("officer")): return jsonify(error="Please log in first."), 401
    text = str((request.get_json(silent=True) or {}).get("text", "")).strip()[:500]
    if not text: return jsonify(error="No text to translate."), 400
    try:
        key = os.environ.get("GOOGLE_TRANSLATE_KEY")
        if key:
            req = urllib.request.Request("https://translation.googleapis.com/language/translate/v2?key=" + urllib.parse.quote(key),
                                         data=json.dumps({"q": text, "target": "te", "format": "text"}).encode(), headers={"Content-Type": "application/json"})
            out = json.load(urllib.request.urlopen(req, timeout=8))["data"]["translations"][0]["translatedText"]
        else:   # free fallback with daily limits; use GOOGLE_TRANSLATE_KEY for steady service
            url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": text, "langpair": "en|te"})
            out = json.load(urllib.request.urlopen(url, timeout=8))["responseData"]["translatedText"]
        return jsonify(text=out)
    except Exception as e:
        print("translate failed:", e); return jsonify(error="Translation is not available right now."), 502

# ---------- admin helpers ----------
def all_complaints(status=""):
    q = ("SELECT c.*, u.name reporter_name FROM complaints c LEFT JOIN users u ON u.phone=c.reporter_phone "
         + ("WHERE c.status=? " if status in C_STATUS else "") + "ORDER BY c.id DESC LIMIT 300")
    with db.connect() as c: return c.execute(q, (status,) if status in C_STATUS else ()).fetchall()

def update_complaint(cid, status, ref, note):
    if status not in C_STATUS: return False
    t = now()
    with db.connect() as c:
        c.execute("UPDATE complaints SET status=?, official_reference=COALESCE(NULLIF(?,''),official_reference), updated_at=? WHERE complaint_id=?", (status, ref[:60], t, cid))
        c.execute("INSERT INTO history(complaint_id,status,note,at) VALUES(?,?,?,?)", (cid, status, (note or C_STATUS[status])[:200], t))
    return True

# ---------- officer / Karyadarsi ----------
def officer_required(f):
    @wraps(f)
    def w(*a, **k): return f(*a, **k) if session.get("officer") else redirect("/officer/login")
    return w

@bp.route("/officer/login", methods=["GET", "POST"])
def officer_login():
    if request.method == "POST":
        if db.verify("officer", request.form.get("password", "")): session["officer"] = True; return redirect("/officer")
        time.sleep(1); flash("Wrong password.", "error")
    return render_template("officer_login.html")

@bp.post("/officer/logout")
def officer_logout(): session.pop("officer", None); return redirect("/")

def officer_rows(status=""):
    show = (status,) if status in C_STATUS else ("reported", "verified", "sent", "acknowledged", "in_progress")
    with db.connect() as c:
        return c.execute(f"SELECT *, CAST(julianday('now')-julianday(created_at) AS INTEGER) age FROM complaints WHERE status IN ({','.join('?' * len(show))}) ORDER BY id DESC LIMIT 300", show).fetchall()

@bp.route("/officer")
@officer_required
def officer():
    st = request.args.get("status", ""); return render_template("officer.html", rows=officer_rows(st), flt=st)

@bp.route("/officer/print")
@officer_required
def officer_print(): return render_template("officer_print.html", rows=officer_rows(), today=now()[:10])

@bp.post("/officer/update")
@officer_required
def officer_update():
    ok = request.form.get("status") in OFFICER_STATUSES and update_complaint(request.form.get("cid", ""), request.form["status"],
                                                                         request.form.get("official_reference", "").strip(), request.form.get("note", "").strip())
    flash("Report updated." if ok else "Invalid update.", "success" if ok else "error")
    return redirect(request.referrer or "/officer")

# ---------- public feed, support votes, duplicate check, Telugu voice ----------
def public_feed(limit=30, village="", category=""):
    q = ("SELECT c.complaint_id,c.village,c.area,c.category,c.status,c.created_at,c.latitude,c.longitude,"
         "(SELECT COUNT(*) FROM votes v WHERE v.complaint_id=c.complaint_id) votes FROM complaints c WHERE c.status IN (%s)" % IN)
    a = list(PUBLIC)
    if village in VILLAGES: q += " AND c.village=?"; a.append(village)
    if category in CATEGORIES: q += " AND c.category=?"; a.append(category)
    with db.connect() as c: return c.execute(q + " ORDER BY votes DESC, c.id DESC LIMIT ?", a + [limit]).fetchall()

def complaint_stats():
    with db.connect() as c:
        one = lambda s, *a: c.execute(s, a).fetchone()[0]
        d = dict(total=one("SELECT COUNT(*) FROM complaints"), public=one("SELECT COUNT(*) FROM complaints WHERE status IN (%s)" % IN, *PUBLIC),
                 progress=one("SELECT COUNT(*) FROM complaints WHERE status IN ('sent','acknowledged','in_progress')"),
                 resolved=one("SELECT COUNT(*) FROM complaints WHERE status='resolved'"))
        d["by_cat"] = [dict(label=r[0], n=r[1]) for r in c.execute("SELECT category,COUNT(*) FROM complaints WHERE status IN (%s) GROUP BY category ORDER BY 2 DESC" % IN, PUBLIC)]
        d["by_status"] = [dict(label=C_STATUS[r[0]], n=r[1]) for r in c.execute("SELECT status,COUNT(*) FROM complaints WHERE status IN (%s) GROUP BY status ORDER BY 2 DESC" % IN, PUBLIC)]
    return d

@bp.route("/reports")
def reports():
    v, cat = request.args.get("village", ""), request.args.get("category", "")
    return render_template("reports.html", feed=public_feed(60, v, cat), v=v, cat=cat)

@bp.post("/api/vote")
def api_vote():
    if not session.get("phone") or not session.get("name"): return jsonify(error="login"), 401
    cid = str((request.get_json(silent=True) or {}).get("cid", ""))
    with db.connect() as c:
        if not c.execute("SELECT 1 FROM complaints WHERE complaint_id=? AND status IN (%s)" % IN, (cid, *PUBLIC)).fetchone(): return jsonify(error="not found"), 404
        c.execute("INSERT OR IGNORE INTO votes(complaint_id,phone,at) VALUES(?,?,?)", (cid, session["phone"], now()))
        n = c.execute("SELECT COUNT(*) FROM votes WHERE complaint_id=?", (cid,)).fetchone()[0]
    return jsonify(votes=n)

@bp.route("/api/nearby")
def api_nearby():
    try: lat, lng = float(request.args["lat"]), float(request.args["lng"])
    except (KeyError, ValueError): return jsonify([])
    with db.connect() as c:
        rows = c.execute("SELECT complaint_id,area,status,latitude,longitude FROM complaints WHERE latitude IS NOT NULL AND category=? AND status IN ('verified','sent','acknowledged','in_progress')",
                         (request.args.get("category", ""),)).fetchall()
    return jsonify([dict(complaint_id=r["complaint_id"], area=r["area"], status_name=C_STATUS[r["status"]]) for r in rows if km((lat, lng), (r["latitude"], r["longitude"])) <= 0.06][:3])

_tts_hits = {}
def _split(text, n=90):
    parts, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n: parts.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return parts + ([cur] if cur else [])

def _free_tts(text):
    """Telugu voice from Google Translate. No key and no installation needed. Unofficial: it may stop working one day."""
    out = b""
    for p in _split(text):
        url = "https://translate.google.com/translate_tts?" + urllib.parse.urlencode({"ie": "UTF-8", "client": "tw-ob", "tl": "te", "q": p})
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36", "Referer": "https://translate.google.com/"})
        out += urllib.request.urlopen(req, timeout=10).read()
    if len(out) < 200: raise ValueError("no audio returned")
    return out

@bp.post("/api/tts")
def api_tts():
    """Telugu audio. Uses your Google Cloud key if set (best), otherwise the free Google Translate voice. Audio is cached on disk."""
    import urllib.error
    key = os.environ.get("GOOGLE_TTS_KEY") or os.environ.get("GOOGLE_TRANSLATE_KEY")
    free_ok = os.environ.get("FREE_TTS", "1") == "1"
    if not key and not free_ok: return jsonify(error="not configured"), 501
    text = str((request.get_json(silent=True) or {}).get("text", "")).strip()[:900]
    if not text: return jsonify(error="No text."), 400
    voice = os.environ.get("TTS_VOICE", "te-IN-Standard-A")        # te-IN-Standard-B is the male voice
    cache = Path(__file__).with_name("tts_cache"); cache.mkdir(exist_ok=True)
    f = cache / (hashlib.sha256(f"{'g' if key else 'f'}|{voice}|{text}".encode()).hexdigest()[:32] + ".mp3")
    if f.exists(): return jsonify(audio=base64.b64encode(f.read_bytes()).decode())
    ip, t = request.remote_addr, time.time()
    hits = [x for x in _tts_hits.get(ip, []) if x > t - 3600]
    if len(hits) >= 120: return jsonify(error="Too many requests."), 429
    _tts_hits[ip] = hits + [t]
    def official(v):
        body = json.dumps({"input": {"text": text}, "voice": v, "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.9}}).encode()
        req = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + urllib.parse.quote(key), data=body, headers={"Content-Type": "application/json"})
        return base64.b64decode(json.load(urllib.request.urlopen(req, timeout=10))["audioContent"])
    data = None
    if key:
        try:
            try: data = official({"languageCode": "te-IN", "name": voice})
            except urllib.error.HTTPError: data = official({"languageCode": "te-IN"})
        except Exception as e: print("google tts failed:", e)
    if data is None and free_ok:
        try: data = _free_tts(text)
        except Exception as e: print("free tts failed:", e)
    if data is None: return jsonify(error="Voice is not available right now."), 502
    f.write_bytes(data)
    return jsonify(audio=base64.b64encode(data).decode())

# ---------- reminders and voice test (admin buttons) ----------
def remind_overdue():
    """One message to the Karyadarsi listing every report open for 7+ days."""
    with db.connect() as c:
        rows = c.execute("SELECT complaint_id,category,village,area,CAST(julianday('now')-julianday(created_at) AS INTEGER) age FROM complaints "
                         "WHERE status IN ('reported','verified','sent','acknowledged','in_progress') AND julianday('now')-julianday(created_at)>=7 ORDER BY age DESC").fetchall()
    if not rows: return ["Reminder: no overdue reports. Nothing to send."]
    site = os.environ.get("SITE_URL", "").rstrip("/")
    text = f"VillageVoice reminder: {len(rows)} problem(s) open for 7+ days. " + "; ".join(f"{r['complaint_id']} {r['category']} {r['area']} ({r['age']}d)" for r in rows[:5]) + f". Open {site}/officer"
    out = []
    phone = re.sub(r"\D", "", os.environ.get("KARYADARSI_PHONE", ""))[-10:]
    if phone: out.append("Reminder SMS: sent." if send_text(phone, text[:400]) else f"Reminder SMS: not sent - {LAST_ERR}")
    ok, why = send_email("VillageVoice: problems open for 7+ days", text + "\n\n" + "\n".join(f"{r['complaint_id']} | {r['category']} | {r['village']}, {r['area']} | {r['age']} days" for r in rows))
    out.append("Reminder email: " + ("sent - " if ok else "not sent - ") + why)
    return out

def test_voice():
    import urllib.error
    key = os.environ.get("GOOGLE_TTS_KEY") or os.environ.get("GOOGLE_TRANSLATE_KEY")
    if key:
        try:
            body = json.dumps({"input": {"text": "నమస్కారం"}, "voice": {"languageCode": "te-IN"}, "audioConfig": {"audioEncoding": "MP3"}}).encode()
            req = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + urllib.parse.quote(key), data=body, headers={"Content-Type": "application/json"})
            json.load(urllib.request.urlopen(req, timeout=10)); return "Voice: Google Telugu voice works (your key)."
        except urllib.error.HTTPError as e:
            return f"Voice: Google rejected your key ({e.code}). " + e.read().decode("utf8", "replace")[:300] + " The free voice will be used instead."
        except Exception as e:
            return f"Voice: could not reach Google with your key ({e})."
    try:
        _free_tts("నమస్కారం"); return "Voice: the free Telugu voice works (no key needed)."
    except Exception as e:
        return f"Voice: the free Telugu voice failed ({e}). Check your internet, or add a Google key in keys.bat."
