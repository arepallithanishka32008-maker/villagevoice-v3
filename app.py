import os, re, hmac, time, secrets
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser
from urllib.parse import urljoin
from flask import jsonify, Flask, g, render_template, request, redirect, url_for, session, flash, abort, make_response, send_from_directory
import database as db
import civic
from config import VILLAGES, CATEGORIES, STATUSES, C_STATUS, C_STATUS_TE, ICONS, KAZA_DATA, FACILITIES, PUBLIC, LOCALITIES, RESOURCES, EMERGENCY, KAZA_PLACES
from i18n import translate_html, TE

def _secret():
    k = os.environ.get("SECRET_KEY") or os.environ.get("VILLAGE_INTELLIGENCE_SECRET")
    if k: return k
    p = Path(__file__).with_name(".secret_key")
    if not p.exists(): p.write_text(secrets.token_hex(32))
    return p.read_text().strip()

app = Flask(__name__)
app.secret_key = _secret()
app.config.update(MAX_CONTENT_LENGTH=6 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_SECURE=os.environ.get("HTTPS") == "1")
db.init_db()
app.register_blueprint(civic.bp)
app.jinja_env.globals.update(share_url=civic.share_url, dir_url=civic.dir_url)

@app.before_request
def start():
    g.lang = "te" if (request.cookies.get("vv_lang") == "te" or request.headers.get("X-Lang") == "te") else "en"
    session.setdefault("csrf", secrets.token_hex(16))
    if request.method == "POST":
        t = request.form.get("csrf") or request.headers.get("X-CSRF", "")
        if not hmac.compare_digest(t, session["csrf"]): abort(400)

@app.after_request
def finish(r):
    r.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "SAMEORIGIN", "Referrer-Policy": "strict-origin-when-cross-origin"})
    if g.get("lang") == "te" and r.mimetype == "text/html" and not r.direct_passthrough:
        r.set_data(translate_html(r.get_data(as_text=True)))
    return r

def admin_only(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not session.get("admin"): return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrapped

@app.context_processor
def common():
    return {"villages": VILLAGES, "categories": CATEGORIES, "statuses": STATUSES, "c_status": C_STATUS, "c_status_te": C_STATUS_TE, "icons": ICONS, "kaza": KAZA_DATA, "facilities": FACILITIES, "emergency": EMERGENCY, "kaza_places": KAZA_PLACES, "resources": RESOURCES,
            "lang": g.get("lang", "en"), "csrf": session.get("csrf", ""), "resident": session.get("phone"), "resident_name": session.get("name")}

def stats():
    with db.connect() as c:
        q = lambda s: c.execute(s).fetchone()["n"]
        return dict(total=q("SELECT COUNT(*) n FROM projects WHERE is_demo=0"), complete=q("SELECT COUNT(*) n FROM projects WHERE is_demo=0 AND status='Completed'"),
                    active=q("SELECT COUNT(*) n FROM projects WHERE is_demo=0 AND status IN ('In Progress','Under Review')"))

REV = {TE[k]: k for k in (CATEGORIES + VILLAGES) if k in TE}

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()[:80]
    res = dict(problems=[], places=[], projects=[], links=[])
    if re.fullmatch(r"(?i)vv-\d{4}-\d+", q): return redirect(url_for("civic.track", id=q.upper()))
    if q:
        qe = next((en for te, en in REV.items() if te in q), q)          # Telugu word -> English word
        like, low = f"%{qe}%", qe.lower()
        mark = ",".join("?" * len(PUBLIC))
        with db.connect() as c:
            res["problems"] = c.execute("SELECT complaint_id,village,area,category,status,created_at,latitude,longitude,(SELECT COUNT(*) FROM votes v WHERE v.complaint_id=complaints.complaint_id) votes "
                                        f"FROM complaints WHERE status IN ({mark}) AND (area LIKE ? OR category LIKE ? OR village LIKE ? OR complaint_id LIKE ?) ORDER BY id DESC LIMIT 30", (*PUBLIC, like, like, like, like)).fetchall()
            res["projects"] = c.execute("SELECT * FROM projects WHERE is_demo=0 AND (title LIKE ? OR description LIKE ? OR category LIKE ? OR village LIKE ?) ORDER BY id DESC LIMIT 20", (like,) * 4).fetchall()
        res["places"] = [dict(name=l["name"], lat=l["lat"], lng=l["lng"], te=l["te"]) for l in LOCALITIES if low in l["name"].lower() or q in l["te"]] + \
                        [dict(name=f) for f in FACILITIES if low in f.lower()]
        with db.connect() as c:
            res["links"] = c.execute("SELECT * FROM resources WHERE title LIKE ? OR description LIKE ? OR tag LIKE ? OR body LIKE ? OR title_te LIKE ? ORDER BY sort, id LIMIT 12", (like, like, like, like, f"%{q}%")).fetchall()
    return render_template("search.html", q=q, res=res)

@app.route("/lang/<code>")
def set_lang(code):
    ref = request.referrer or ""
    resp = make_response(redirect(ref if urlparse(ref).netloc == request.host else "/"))
    resp.set_cookie("vv_lang", "te" if code == "te" else "en", max_age=31536000, samesite="Lax")
    return resp

@app.route("/sw.js")
def sw():
    r = send_from_directory(app.static_folder, "sw.js"); r.headers["Service-Worker-Allowed"] = "/"; r.headers["Cache-Control"] = "no-cache"; return r

@app.route("/")
def home(): return render_template("index.html", s=stats(), cs=civic.complaint_stats(), feed=civic.public_feed(6), recent=db.projects()[:3])

@app.route("/projects")
def project_list():
    v = request.args.get("village", "All villages"); cat = request.args.get("category", "All categories")
    return render_template("projects.html", items=db.projects(v, cat), v=v, cat=cat)

@app.route("/map")
def map_page(): return render_template("map.html")

@app.route("/opportunities")
def opportunities(): return render_template("opportunities.html", items=db.resources())

class _Reader(HTMLParser):
    """Turns a web page into plain headings, paragraphs and links (for sites that do not allow being embedded)."""
    SKIP = {"script", "style", "noscript", "svg", "iframe", "template"}
    BLOCK = {"h1", "h2", "h3", "h4", "h5", "p", "li", "td", "th", "dd", "dt", "div", "section", "article", "tr", "header", "footer"}
    HEAD = {"h1", "h2", "h3", "h4", "h5"}
    def __init__(s, base):
        super().__init__(convert_charrefs=True)
        s.base, s.skip, s.title, s.in_title, s.cur, s.blocks, s.links, s.a, s.meta, s.seen = base, 0, "", False, None, [], [], None, "", set()
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "title": s.in_title = True
        if t == "meta" and (a.get("name") or "").lower() == "description": s.meta = a.get("content") or ""
        if t in s.SKIP: s.skip += 1
        if t in s.BLOCK: s._flush(); s.cur = [t, ""]
        if t == "a" and a.get("href"): s.a = [urljoin(s.base, a["href"]), ""]
    def handle_endtag(s, t):
        if t == "title": s.in_title = False
        if t in s.SKIP and s.skip: s.skip -= 1
        if t in s.BLOCK: s._flush()
        if t == "a" and s.a:
            txt = " ".join(s.a[1].split())
            if txt and len(s.links) < 120 and s.a[0].startswith(("http://", "https://")) and (txt[:100], s.a[0]) not in s.links: s.links.append((txt[:100], s.a[0]))
            s.a = None
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.skip: return
        if s.a is not None: s.a[1] += d
        if s.cur is None: s.cur = ["p", ""]
        s.cur[1] += d
    def _flush(s):
        if s.cur:
            txt = " ".join(s.cur[1].split())
            keep = (s.cur[0] in s.HEAD and len(txt) >= 3) or len(txt) >= 30
            if keep and txt not in s.seen and len(s.blocks) < 150: s.seen.add(txt); s.blocks.append((s.cur[0], txt[:600]))
        s.cur = None

_read_cache = {}
@app.route("/read")
def read_page():
    """Reader view: shows the text of a Resources-page website inside this site."""
    import urllib.request
    url = request.args.get("url", "")
    p = urlparse(url)
    hosts = {urlparse(r["url"]).netloc.lower() for r in db.resources() if r["url"]}
    if p.scheme not in ("http", "https") or p.netloc.lower() not in hosts: abort(400)
    hit = _read_cache.get(url)
    if hit and time.time() - hit[0] < 900: return render_template("reader.html", **hit[1])
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36", "Accept": "text/html,*/*", "Accept-Language": "en,te"}), timeout=12)
        raw, final, enc = resp.read(1_500_000), resp.geturl(), resp.headers.get_content_charset() or "utf-8"
        try: html = raw.decode(enc, "replace")
        except LookupError: html = raw.decode("utf-8", "replace")
    except Exception as e:
        return render_template("reader.html", url=url, error=str(e)[:150], blocks=[], links=[], title="", meta="")
    r = _Reader(final); r.feed(html)
    ctx = dict(url=url, error="", blocks=r.blocks, links=[(t, u, urlparse(u).netloc.lower() in hosts) for t, u in r.links], title=" ".join(r.title.split())[:150], meta=" ".join(r.meta.split())[:400])
    _read_cache[url] = (time.time(), ctx)
    return render_template("reader.html", **ctx)

@app.route("/summary")
def summary():
    with db.connect() as c:
        one = lambda q: c.execute(q).fetchone()[0]
        pub = "('verified','sent','acknowledged','in_progress','resolved')"
        s = dict(week=one("SELECT COUNT(*) FROM complaints WHERE created_at >= date('now','-7 day')"), checked=one(f"SELECT COUNT(*) FROM complaints WHERE status IN {pub}"),
                 resolved=one("SELECT COUNT(*) FROM complaints WHERE status='resolved'"),
                 overdue=one("SELECT COUNT(*) FROM complaints WHERE status IN ('reported','verified','sent','acknowledged','in_progress') AND julianday('now')-julianday(created_at)>=7"),
                 avg=c.execute("SELECT AVG(julianday(h.at)-julianday(c.created_at)) FROM complaints c JOIN (SELECT complaint_id, MIN(at) at FROM history WHERE status='resolved' GROUP BY complaint_id) h ON h.complaint_id=c.complaint_id").fetchone()[0],
                 top=c.execute(f"SELECT category FROM complaints WHERE status IN {pub} GROUP BY category ORDER BY COUNT(*) DESC LIMIT 1").fetchone())
    avg = round(s["avg"], 1) if s["avg"] is not None else None
    top = s["top"][0] if s["top"] else None
    te = (f"ఈ వారం {s['week']} కొత్త ఫిర్యాదులు వచ్చాయి. వాలంటీర్లు మొత్తం {s['checked']} ఫిర్యాదులను నిర్ధారించారు. {s['resolved']} సమస్యలు పరిష్కారమయ్యాయి. "
          f"{s['overdue']} సమస్యలు ఏడు రోజులకు పైగా పరిష్కారం కాలేదు." + (f" ఎక్కువగా వచ్చిన సమస్య: {TE.get(top, top)}." if top else "") + (f" సమస్య పరిష్కారానికి సగటున {avg} రోజులు పట్టింది." if avg is not None else ""))
    return render_template("summary.html", s=s, avg=avg, top=top, te=te)

@app.route("/api/can-embed")
def can_embed():
    """Tell the viewer if a Resources link can be shown inside this site, or is blocked / not responding."""
    import urllib.request, urllib.error
    url = request.args.get("url", "")
    with db.connect() as c: known = c.execute("SELECT 1 FROM resources WHERE url=?", (url,)).fetchone()
    if not known: return jsonify(error="unknown link"), 400
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VillageVoice-linkcheck"}), timeout=8).headers
    except urllib.error.HTTPError as e: h = e.headers                  # the site answered (even with an error page)
    except Exception as e: return jsonify(reachable=False, embeddable=False, reason=str(e)[:100])
    xfo, csp = (h.get("X-Frame-Options") or "").lower(), (h.get("Content-Security-Policy") or "").lower()
    blocked = "deny" in xfo or "sameorigin" in xfo or ("frame-ancestors" in csp and "frame-ancestors *" not in csp)
    return jsonify(reachable=True, embeddable=not blocked)

@app.route("/resource/<int:rid>")
def resource(rid):
    r = db.get_resource(rid)
    if not r or not r["body"]: abort(404)
    te = g.lang == "te"
    pick = lambda en, tel: tel if (te and tel) else en
    return render_template("resource.html", r=r, title=pick(r["title"], r["title_te"]), desc=pick(r["description"] or "", r["description_te"]),
                           body=pick(r["body"], r["body_te"]), voice=r["body_te"] or r["body"])

@app.route("/share-need")
def share_need(): return redirect(url_for("civic.report"))

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if db.verify(request.form.get("username", ""), request.form.get("password", "")):
            session["admin"] = True; return redirect(url_for("admin"))
        time.sleep(1); flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/admin/logout", methods=["POST"])
def logout(): session.clear(); return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
@admin_only
def admin():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            d = {k: request.form.get(k, "").strip() for k in ["title", "village", "category", "description", "status"]}
            try: d["progress"] = max(0, min(100, int(request.form.get("progress", "0"))))
            except ValueError: d["progress"] = 0
            if d["title"] and d["description"] and d["village"] in VILLAGES and d["category"] in CATEGORIES and d["status"] in STATUSES:
                db.add_project(d); flash("Project added.", "success")
            else: flash("Check the project fields.", "error")
        elif action == "update":
            try:
                pid = int(request.form["id"]); progress = max(0, min(100, int(request.form["progress"])))
                if request.form["status"] in STATUSES: db.update_project(pid, request.form["status"], progress)
            except (ValueError, KeyError): flash("Invalid update.", "error")
        elif action == "need":
            if request.form.get("status") in ["Received", "Reviewing", "Action Planned", "Addressed"]:
                db.update_need(int(request.form["id"]), request.form["status"])
        elif action == "resource_add":
            d = {k: request.form.get(k, "").strip() for k in ("title", "title_te", "tag", "description", "description_te", "url", "body", "body_te")}
            if d["url"] and not d["url"].startswith(("http://", "https://")): d["url"] = ""
            if d["title"]: db.add_resource(d); flash("Added to the Resources page.", "success")
            else: flash("Enter a title.", "error")
        elif action == "resource_delete":
            try: db.delete_resource(int(request.form["id"])); flash("Resource deleted.", "success")
            except (ValueError, KeyError): flash("Invalid request.", "error")
        elif action == "test_alert":
            for line in civic.test_alert(): flash(line, "success" if ": sent" in line or "Email: sent" in line else "error")
        elif action == "remind_now":
            for line in civic.remind_overdue(): flash(line, "success" if ("sent." in line or "sent -" in line and "not sent" not in line or "Nothing to send" in line) and "not sent" not in line else "error")
        elif action == "test_voice":
            line = civic.test_voice(); flash(line, "success" if "works" in line else "error")
        elif action == "complaint":
            ok = civic.update_complaint(request.form.get("cid", ""), request.form.get("status", ""), request.form.get("official_reference", "").strip(), request.form.get("note", "").strip())
            if ok and request.form.get("status") == "sent": civic.notify_officer(request.form.get("cid", ""))
            flash("Report updated." if ok else "Invalid update.", "success" if ok else "error")
        return redirect(url_for("admin", cstatus=request.args.get("cstatus", "")))
    return render_template("admin.html", items=db.projects(), needs=db.needs(), s=stats(),
                           complaints=civic.all_complaints(request.args.get("cstatus", "")), resources_list=db.resources(), cstatus=request.args.get("cstatus", ""))

@app.errorhandler(404)
def missing(e): return render_template("404.html"), 404

if __name__ == "__main__": app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG") == "1")
