KAZA = (16.198141, 81.005063)
VILLAGES = ["Kaza", "Paddarayuduthota", "Kollapalem", "Racharlapalem", "Other area in Kaza"]
CATEGORIES = ["Roads", "Water", "Drainage", "Sanitation", "Streetlights", "Public facilities", "Agriculture", "Education", "Other"]
STATUSES = ["Reported", "Under Review", "In Progress", "Completed", "On Hold"]
C_STATUS = {"reported": "Reported", "verified": "Verified", "sent": "Sent to office", "acknowledged": "Acknowledged",
            "in_progress": "In progress", "resolved": "Resolved", "rejected": "Rejected"}
PUBLIC = ("verified", "sent", "acknowledged", "in_progress", "resolved")
C_STATUS_TE = {"reported": "నమోదైంది", "verified": "ధృవీకరించబడింది", "sent": "కార్యాలయానికి పంపబడింది", "acknowledged": "స్వీకరించబడింది",
               "in_progress": "పనులు జరుగుతున్నాయి", "resolved": "పరిష్కారమైంది", "rejected": "తిరస్కరించబడింది"}
ICONS = {"Roads": "🛣️", "Water": "💧", "Drainage": "🚰", "Sanitation": "🧹", "Streetlights": "💡", "Public facilities": "🏫", "Agriculture": "🌾", "Education": "📚", "Other": "📌"}

# Kaza outline traced from the Google Maps boundary (approximate, about +/-200 m). Replace with exact points when the Panchayat gives them.
KAZA_BOUNDARY = [[16.234805, 80.991738], [16.229259, 80.986941], [16.224843, 80.986941], [16.218681, 80.982464], [16.210157, 80.97756], [16.207384, 80.976814], [16.199682, 80.973083], [16.191465, 80.97255], [16.185303, 80.973723], [16.179963, 80.972443], [16.174828, 80.968819], [16.170104, 80.960931], [16.170925, 80.976068], [16.172261, 80.97756], [16.17298, 80.982037], [16.172158, 80.986941], [16.171747, 80.995469], [16.169898, 81.006662], [16.168666, 81.007408], [16.167845, 81.013378], [16.175855, 81.014657], [16.175444, 81.019987], [16.173185, 81.027449], [16.176574, 81.028089], [16.177293, 81.031713], [16.174725, 81.037043], [16.174623, 81.038535], [16.179039, 81.040028], [16.182017, 81.03651], [16.183763, 81.035551], [16.1966, 81.041307], [16.199887, 81.043439], [16.204611, 81.045891], [16.202762, 81.044505], [16.202557, 81.042373], [16.20533, 81.040028], [16.207692, 81.035444], [16.210465, 81.033845], [16.20913, 81.027982], [16.209438, 81.024251], [16.213854, 81.023398], [16.224124, 81.021266], [16.225767, 81.01519], [16.230491, 81.005063], [16.232546, 80.997601]]
KAZA_CHECK = [[16.237239, 80.990681], [16.23136, 80.985597], [16.226679, 80.985597], [16.220148, 80.980851], [16.211112, 80.975653], [16.208173, 80.974862], [16.200009, 80.970907], [16.191299, 80.970342], [16.184767, 80.971585], [16.179106, 80.970229], [16.173663, 80.966387], [16.168656, 80.958026], [16.169526, 80.974071], [16.170942, 80.975653], [16.171704, 80.980398], [16.170833, 80.985597], [16.170398, 80.994636], [16.168438, 81.006501], [16.167132, 81.007292], [16.166261, 81.01362], [16.174752, 81.014976], [16.174316, 81.020625], [16.171922, 81.028535], [16.175514, 81.029213], [16.176276, 81.033055], [16.173554, 81.038705], [16.173446, 81.040286], [16.178127, 81.041869], [16.181284, 81.03814], [16.183134, 81.037123], [16.196742, 81.043225], [16.200226, 81.045484], [16.205233, 81.048084], [16.203273, 81.046614], [16.203056, 81.044354], [16.205995, 81.041869], [16.208499, 81.03701], [16.211439, 81.035315], [16.210023, 81.0291], [16.21035, 81.025145], [16.215031, 81.024241], [16.225917, 81.021981], [16.227659, 81.015541], [16.232666, 81.004806], [16.234844, 80.996896]]     # outline enlarged 6% so pins just on the edge are accepted
KAZA_BOUNDS = [[16.16384, 80.95693], [16.23881, 81.04989]]
LOCALITIES = [{"name": "Kaza", "te": "కాజా", "lat": 16.198141, "lng": 81.005063}, {"name": "Paddarayuduthota", "te": "పద్దరాయుడుతోట", "lat": 16.206357, "lng": 81.023718}, {"name": "Kollapalem", "te": "కొల్లపాలెం", "lat": 16.201735, "lng": 81.033845}, {"name": "Racharlapalem", "te": "రాచర్లపాలెం", "lat": 16.19126, "lng": 81.029581}]
FACILITIES = ["MPPS Kaza (R)", "SPNR ZPHS Kaza", "Good Shepherd EM TM HS Kaza", "Raafsun Blue UP (EM) Kaza", "Andhra Bank, Kaza Branch", "Kaza Church", "The Baptist Church, Kaza"]
KAZA_DATA = dict(boundary=KAZA_BOUNDARY, check=KAZA_CHECK, bounds=KAZA_BOUNDS, localities=LOCALITIES, center=list(KAZA))

KAZA_MAXBOUNDS = [[16.14784, 80.94093], [16.25481, 81.06589]]     # how far the map may be moved (about 2 km around Kaza)
KAZA_DATA["maxbounds"] = KAZA_MAXBOUNDS
EMERGENCY = [("112", "Emergency", "🚨"), ("108", "Ambulance", "🚑"), ("100", "Police", "👮"), ("101", "Fire", "🚒")]
RESOURCES = [
    ("Agriculture department", "Farmers", "Schemes, advice and services for farmers (Government of India).", "https://agriwelfare.gov.in/"),
    ("PM-KISAN", "Farmers", "Income support for farmer families.", "https://pmkisan.gov.in/"),
    ("Farmers Portal", "Farmers", "Weather, market prices and schemes for farmers.", "https://farmer.gov.in/"),
    ("Scholarships", "Students", "Check scholarship eligibility and notices.", "https://scholarships.gov.in/"),
    ("Skill training", "Skills & jobs", "Training and job services.", "https://www.skillindiadigital.gov.in/"),
    ("Krishna District website", "Public services", "Official district notices, offices and directory.", "https://krishna.ap.gov.in/"),
    ("India.gov.in", "Public services", "National portal for government services.", "https://www.india.gov.in/"),
    ("Udyam Registration", "Businesses", "Registration for small businesses.", "https://udyamregistration.gov.in/"),
]

KAZA_DATA["nearby"] = [{"name": "Pedamuttevi", "te": "పెదముత్తేవి", "lat": 16.233573, "lng": 80.951763}, {"name": "Kosuru", "te": "కోసూరు", "lat": 16.206871, "lng": 80.957413}, {"name": "Mallampalli", "te": "మల్లంపల్లి", "lat": 16.188898, "lng": 80.963276}, {"name": "Bollapadu", "te": "బొల్లపాడు", "lat": 16.16959, "lng": 80.955814}, {"name": "Polavaram", "te": "పోలవరం", "lat": 16.173493, "lng": 81.041307}, {"name": "Rayavaram", "te": "రాయవరం", "lat": 16.191465, "lng": 81.063693}, {"name": "Kanchakodur", "te": "కంచకోడుర్", "lat": 16.213033, "lng": 81.049089}, {"name": "Maddipatla", "te": "మద్దిపట్ల", "lat": 16.223302, "lng": 81.031287}, {"name": "Mallavolu", "te": "మల్లవోలు", "lat": 16.164763, "lng": 81.056231}]   # nearby villages, labels only (approximate)

KAZA_PLACES = ["Kaza", "Paddarayuduthota", "Kollapalem", "Racharlapalem", "Other area in Kaza"]
VILLAGES = KAZA_PLACES + [n["name"] for n in KAZA_DATA["nearby"]]      # dropdown: Kaza places first, then the nearby villages shown on the map
