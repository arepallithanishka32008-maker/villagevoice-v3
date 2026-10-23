import os, secrets, sqlite3
from datetime import datetime
from pathlib import Path
from config import RESOURCES
from werkzeug.security import generate_password_hash, check_password_hash

DB = os.environ.get("DB_PATH", str(Path(__file__).with_name("villagevoice.db")))


SEED_GUIDES = [
 ("How to follow up a problem", "సమస్య పరిష్కారం కోసం ఎలా అనుసరించాలి", "Guide", "Steps to take if a problem is not fixed.", "సమస్య పరిష్కారం కాకపోతే ఏమి చేయాలి.",
  "1. Report it on VillageVoice and keep your report ID.\n2. Meet the Sachivalayam staff (Karyadarsi) with the ID and ask for an acknowledgement.\n3. If nothing happens in 7 days, meet the Sarpanch or Panchayat Secretary.\n4. After 15 days, give a written complaint at the Mandal office (MPDO or Tahsildar) and take a stamped copy.\n5. After 30 days, submit it to the District Collector's grievance programme. Ask the Sachivalayam for the current process.\n6. Keep photos and copies of everything.",
  "1. విలేజ్‌వాయిస్‌లో సమస్య చెప్పి, మీ ఫిర్యాదు ఐడి ఉంచుకోండి.\n2. ఆ ఐడితో సచివాలయం కార్యదర్శిని కలిసి, రసీదు (acknowledgement) అడగండి.\n3. 7 రోజుల్లో పని జరగకపోతే సర్పంచ్ లేదా పంచాయతీ కార్యదర్శిని కలవండి.\n4. 15 రోజుల తర్వాత రాతపూర్వక ఫిర్యాదును మండల కార్యాలయంలో (ఎంపీడీవో లేదా తహసీల్దార్) ఇచ్చి, స్టాంపు వేసిన కాపీ తీసుకోండి.\n5. 30 రోజుల తర్వాత జిల్లా కలెక్టర్ గ్రీవెన్స్ కార్యక్రమంలో ఇవ్వండి. ప్రస్తుత పద్ధతి సచివాలయంలో అడగండి.\n6. ఫోటోలు, కాపీలు అన్నీ భద్రంగా ఉంచుకోండి."),
 ("Help for farmers", "రైతులకు సహాయం", "Farmers", "Where to get farming advice and scheme information.", "వ్యవసాయ సలహా, పథకాల సమాచారం ఎక్కడ దొరుకుతుంది.",
  "Your village Rythu Seva Kendram (RBK) has a Village Agriculture Assistant. Ask there for seeds, advice, crop information and scheme details.\nFor PM-KISAN and other schemes, ask the Sachivalayam staff to check your eligibility and status.\nCarry your Aadhaar, bank passbook and land passbook (pattadar passbook).\nSchemes, amounts and dates change. Confirm at the office before you pay money to anyone.",
  "మీ ఊరి రైతు సేవా కేంద్రంలో (ఆర్‌బీకే) గ్రామ వ్యవసాయ సహాయకులు ఉంటారు. విత్తనాలు, సలహాలు, పంట సమాచారం, పథకాల వివరాలు అక్కడ అడగండి.\nపీఎం కిసాన్ లాంటి పథకాల్లో మీరు అర్హులో కాదో, స్థితి ఏమిటో సచివాలయంలో అడిగి తెలుసుకోండి.\nఆధార్, బ్యాంకు పాస్‌బుక్, భూమి పాస్‌బుక్ తీసుకెళ్లండి.\nపథకాలు, మొత్తాలు, తేదీలు మారుతుంటాయి. ఎవరికైనా డబ్బు ఇచ్చే ముందు కార్యాలయంలో నిర్ధారించుకోండి."),
 ("Pension and welfare services", "పెన్షన్, సంక్షేమ సేవలు", "Public services", "Many services are available at the Sachivalayam.", "చాలా సేవలు సచివాలయంలో దొరుకుతాయి.",
  "Ask the Grama Sachivalayam staff about pensions, ration card services, certificates and welfare schemes.\nCarry Aadhaar, ration card, bank passbook and a passport photo.\nAlways take an acknowledgement slip with a number and date.\nPay only the official fee shown on the receipt. If anyone asks for a bribe, tell the Karyadarsi or the Mandal officers.",
  "పెన్షన్లు, రేషన్ కార్డు సేవలు, సర్టిఫికెట్లు, సంక్షేమ పథకాల గురించి గ్రామ సచివాలయం సిబ్బందిని అడగండి.\nఆధార్, రేషన్ కార్డు, బ్యాంకు పాస్‌బుక్, పాస్‌పోర్ట్ ఫోటో తీసుకెళ్లండి.\nనంబర్, తేదీ ఉన్న రసీదు (acknowledgement) తప్పకుండా తీసుకోండి.\nరసీదులో ఉన్న అధికారిక రుసుము మాత్రమే చెల్లించండి. ఎవరైనా లంచం అడిగితే కార్యదర్శికి లేదా మండల అధికారులకు చెప్పండి."),
 ("Scholarships and education", "స్కాలర్‌షిప్‌లు, చదువు", "Students", "How students can find and apply for scholarships.", "విద్యార్థులు స్కాలర్‌షిప్ ఎలా వెతికి దరఖాస్తు చేయాలి.",
  "Check scholarship schemes on the National Scholarship Portal, or ask your school or college office.\nKeep Aadhaar, income and caste certificates, marks memos and a bank passbook ready.\nNote the last date and apply early.",
  "జాతీయ స్కాలర్‌షిప్ పోర్టల్‌లో లేదా మీ స్కూల్, కాలేజీ కార్యాలయంలో స్కాలర్‌షిప్ పథకాలు చూడండి.\nఆధార్, ఆదాయ, కుల ధ్రువపత్రాలు, మార్కుల మెమో, బ్యాంకు పాస్‌బుక్ సిద్ధంగా ఉంచుకోండి.\nచివరి తేదీ గుర్తుపెట్టుకుని ముందుగానే దరఖాస్తు చేయండి."),
 ("Drinking water and sanitation problems", "తాగునీరు, పారిశుధ్య సమస్యలు", "Guide", "Who to contact for water, drains and cleaning.", "నీరు, కాలువలు, శుభ్రత కోసం ఎవరిని కలవాలి.",
  "Tell the Panchayat Secretary or Sarpanch first. The Gram Panchayat looks after local water supply, drains, street lights and cleaning.\nBig pipeline or tank problems may need the Mandal or Rural Water Supply office.\nReport on VillageVoice with a photo and pin so officials can find the exact spot.",
  "ముందు పంచాయతీ కార్యదర్శికి లేదా సర్పంచ్‌కు చెప్పండి. ఊరి నీటి సరఫరా, కాలువలు, వీధి దీపాలు, శుభ్రత గ్రామ పంచాయతీ చూస్తుంది.\nపెద్ద పైపులైను, ట్యాంకు సమస్యలకు మండల కార్యాలయం లేదా గ్రామీణ నీటి సరఫరా కార్యాలయం అవసరం కావచ్చు.\nఅధికారులకు ఆ చోటు సులభంగా తెలియడానికి విలేజ్‌వాయిస్‌లో ఫోటో, పిన్‌తో చెప్పండి."),
]

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, village TEXT NOT NULL,
        category TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL,
        progress INTEGER NOT NULL DEFAULT 0, is_demo INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS needs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, village TEXT NOT NULL,
        category TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL,
        created_at TEXT NOT NULL)""")
        c.execute("CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)")
        c.executescript("""
        CREATE TABLE IF NOT EXISTS complaints(id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT UNIQUE,
          village TEXT NOT NULL, area TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'reported', latitude REAL, longitude REAL, gps_accuracy_m REAL, photo TEXT,
          reporter_phone TEXT NOT NULL, official_reference TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT NOT NULL,
          status TEXT NOT NULL, note TEXT, at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users(phone TEXT PRIMARY KEY, name TEXT NOT NULL, village TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS resources(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, title_te TEXT, tag TEXT NOT NULL DEFAULT 'Guide', description TEXT, description_te TEXT, url TEXT, body TEXT, body_te TEXT, sort INTEGER NOT NULL DEFAULT 100, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS votes(complaint_id TEXT NOT NULL, phone TEXT NOT NULL, at TEXT NOT NULL, PRIMARY KEY(complaint_id, phone));
        CREATE TABLE IF NOT EXISTS otps(phone TEXT NOT NULL, code_hash TEXT NOT NULL, expires REAL NOT NULL,
          attempts INTEGER NOT NULL DEFAULT 0, created REAL NOT NULL);""")
        for who, envname in (("officer", "OFFICER_PASSWORD"),):
            pw = os.environ.get(envname); r = c.execute("SELECT id FROM admins WHERE username=?", (who,)).fetchone()
            if pw:
                h = generate_password_hash(pw)
                if r: c.execute("UPDATE admins SET password_hash=? WHERE username=?", (h, who))
                else: c.execute("INSERT INTO admins(username,password_hash) VALUES(?,?)", (who, h))
            elif not r:
                pw = secrets.token_urlsafe(9)
                c.execute("INSERT INTO admins(username,password_hash) VALUES(?,?)", (who, generate_password_hash(pw)))
                print(f"\n*** First-run {who} login -> username: {who}  password: {pw}  (set {envname} to choose your own) ***\n")
        if c.execute("SELECT COUNT(*) FROM resources").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d")
            for i, g in enumerate(SEED_GUIDES):
                c.execute("INSERT INTO resources(title,title_te,tag,description,description_te,body,body_te,sort,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (g[0], g[1], g[2], g[3], g[4], g[5], g[6], i, now))
            for i, (t, tag, desc, url) in enumerate(RESOURCES):
                c.execute("INSERT INTO resources(title,tag,description,url,sort,created_at) VALUES(?,?,?,?,?,?)", (t, tag, desc, url, 50 + i, now))
        c.execute("UPDATE resources SET url=? WHERE url=?", ("https://agriwelfare.gov.in/", "https://agricoop.nic.in/"))
        env_pw = os.environ.get("ADMIN_PASSWORD")
        row = c.execute("SELECT id FROM admins WHERE username='admin'").fetchone()
        if env_pw:   # set ADMIN_PASSWORD to create or change the admin password
            h = generate_password_hash(env_pw)
            if row: c.execute("UPDATE admins SET password_hash=? WHERE username='admin'", (h,))
            else: c.execute("INSERT INTO admins(username,password_hash) VALUES(?,?)", ("admin", h))
        elif not row:
            pw = secrets.token_urlsafe(9)
            c.execute("INSERT INTO admins(username,password_hash) VALUES(?,?)", ("admin", generate_password_hash(pw)))
            print(f"\n*** First-run admin login -> username: admin  password: {pw}  (set ADMIN_PASSWORD to choose your own) ***\n")

def projects(village="All villages", category="All categories"):
    q="SELECT * FROM projects WHERE 1=1"; a=[]
    if village != "All villages": q+=" AND village=?"; a.append(village)
    if category != "All categories": q+=" AND category=?"; a.append(category)
    q+=" ORDER BY id DESC"
    with connect() as c: return c.execute(q,a).fetchall()

def needs():
    with connect() as c: return c.execute("SELECT * FROM needs ORDER BY id DESC").fetchall()

def add_project(d):
    with connect() as c:
        c.execute("INSERT INTO projects(title,village,category,description,status,progress,is_demo,created_at) VALUES(?,?,?,?,?,?,0,?)",
        (d["title"],d["village"],d["category"],d["description"],d["status"],d["progress"],datetime.now().strftime("%Y-%m-%d")))

def update_project(pid,status,progress):
    with connect() as c: c.execute("UPDATE projects SET status=?,progress=? WHERE id=?",(status,progress,pid))

def update_need(nid,status):
    with connect() as c: c.execute("UPDATE needs SET status=? WHERE id=?",(status,nid))

def verify(username,password):
    with connect() as c: row=c.execute("SELECT * FROM admins WHERE username=?",(username,)).fetchone()
    return bool(row and check_password_hash(row["password_hash"],password))

def resources():
    with connect() as c: return c.execute("SELECT * FROM resources ORDER BY sort, id").fetchall()

def get_resource(rid):
    with connect() as c: return c.execute("SELECT * FROM resources WHERE id=?", (rid,)).fetchone()

def add_resource(d):
    with connect() as c:
        c.execute("INSERT INTO resources(title,title_te,tag,description,description_te,url,body,body_te,sort,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (d["title"][:120], d["title_te"][:120], (d["tag"] or "Guide")[:30], d["description"][:200], d["description_te"][:200], d["url"][:300], d["body"][:4000], d["body_te"][:4000], 10, datetime.now().strftime("%Y-%m-%d")))

def delete_resource(rid):
    with connect() as c: c.execute("DELETE FROM resources WHERE id=?", (rid,))
