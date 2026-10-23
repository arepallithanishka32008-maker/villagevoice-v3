"""Telugu for the whole site. When the visitor picks Telugu, every page is translated here before it is sent.
Add or fix a phrase by editing the TE dictionary (English text on the left, Telugu on the right)."""
import re
from html import escape, unescape

TE = {
 # menu, footer
 "Home": "హోమ్", "Village map": "ఊరి మ్యాప్", "Reports": "ఫిర్యాదులు", "Track": "స్థితి", "Projects": "పనులు", "Resources": "సమాచారం",
 "Report a problem": "సమస్య చెప్పండి", "Report": "చెప్పండి", "Map": "మ్యాప్", "Kaza · Movva Mandal": "కాజా · మొవ్వ మండలం", "Log out": "లాగౌట్",
 "Listen to this page": "ఈ పేజీ వినండి", "Menu": "మెనూ", "Main": "ప్రధాన",
 "VillageVoice is a community initiative of Kaza residents. It is not an official government website. A VillageVoice ID is not a government complaint number.":
   "విలేజ్‌వాయిస్ కాజా ఊరి ప్రజల సొంత కార్యక్రమం. ఇది ప్రభుత్వ వెబ్‌సైట్ కాదు. ఇందులో వచ్చే ఐడి ప్రభుత్వ ఫిర్యాదు నంబర్ కాదు.",
 "Officer login": "అధికారి లాగిన్", "Coordinator login": "కోఆర్డినేటర్ లాగిన్",
 # home
 "Community initiative · Kaza, Movva Mandal, Krishna District": "ఊరి ప్రజల కార్యక్రమం · కాజా, మొవ్వ మండలం, కృష్ణా జిల్లా",
 "Your village.": "మీ ఊరు.", "Your voice.": "మీ మాట.",
 "Report a problem with a photo and the exact spot on the map. Volunteers check it, the Sachivalayam sees it, and you can follow it until it is fixed.":
   "ఫోటో తీసి, మ్యాప్‌లో ఆ చోటు చూపించి సమస్య చెప్పండి. వాలంటీర్లు చూసి నిర్ధారిస్తారు. సచివాలయం చూస్తుంది. పరిష్కారం అయ్యే వరకు మీరు ఇక్కడే చూడవచ్చు.",
 "🔊 Listen in Telugu": "🔊 తెలుగులో వినండి", "Reports received": "వచ్చిన ఫిర్యాదులు", "Checked by volunteers": "వాలంటీర్లు చూసినవి",
 "With offices": "కార్యాలయాల్లో ఉన్నవి", "Resolved": "పరిష్కారమైంది", "How it works": "ఇది ఎలా పని చేస్తుంది",
 "Verify your mobile": "మొబైల్ నంబర్ నిర్ధారించండి", "Browse freely. An OTP is needed only to send a report.": "అందరూ చూడవచ్చు. ఫిర్యాదు చేయడానికి మాత్రమే OTP కావాలి.",
 "Pin the exact spot": "ఆ చోటు మ్యాప్‌లో చూపండి", "Drop a pin on the map and add a photo.": "మ్యాప్‌లో పిన్ పెట్టండి, ఫోటో కూడా పెట్టండి.",
 "Volunteers check it": "వాలంటీర్లు చూస్తారు", "Duplicates are merged and facts are confirmed.": "ఒకే సమస్య రెండుసార్లు వస్తే కలుపుతారు. నిజమో కాదో చూసి నిర్ధారిస్తారు.",
 "Sachivalayam acts": "సచివాలయం చర్య తీసుకుంటుంది", "The Karyadarsi gets directions and updates the status you can see.": "కార్యదర్శికి ఆ చోటుకు దారి వెళ్తుంది. ఆయన స్థితి మారుస్తారు, మీరు ఇక్కడే చూడవచ్చు.",
 "Latest checked problems": "ఇటీవల నిర్ధారించిన సమస్యలు", "See all problems →": "అన్ని సమస్యలు చూడండి →", "No checked reports yet.": "ఇంకా నిర్ధారించిన ఫిర్యాదులు లేవు.",
 "Report the first problem in your village.": "మీ ఊరి మొదటి సమస్య చెప్పండి.", "Be the first to report a problem.": "మొదట మీరే సమస్య చెప్పండి.",
 "See a problem in your village?": "మీ ఊరిలో సమస్య కనిపిస్తోందా?", "It takes two minutes. Add the spot on the map and a photo.": "రెండు నిమిషాలు చాలు. మ్యాప్‌లో చోటు, ఒక ఫోటో పెట్టండి.",
 "Problems at a glance": "సమస్యల వివరాలు", "By category": "రకం ప్రకారం", "By status": "స్థితి ప్రకారం", "Development projects": "ఊరి అభివృద్ధి పనులు", "All projects →": "అన్ని పనులు →",
 # cards
 "Me too": "నాకూ ఉంది", "Directions ↗": "దారి ↗", "Get directions ↗": "దారి చూడండి ↗", "Photo": "ఫోటో", "Share on WhatsApp": "వాట్సాప్‌లో పంపండి",
 # reports / filters
 "Problems in our villages": "మన ఊరి సమస్యలు",
 "Reports that volunteers have checked. If you face the same problem, tap Me too. More support moves a problem up the list.":
   "వాలంటీర్లు నిర్ధారించిన ఫిర్యాదులు. మీకూ ఇదే సమస్య ఉంటే 'నాకూ ఉంది' నొక్కండి. ఎక్కువ మంది నొక్కితే ఆ సమస్య పైకి వస్తుంది.",
 "Village": "ఊరు", "All villages": "అన్ని ఊర్లు", "Category": "రకం", "All categories": "అన్ని రకాలు", "Filter": "చూపించు",
 "Kaza": "కాజా", "Paddarayuduthota": "పద్దరాయుడుతోట", "Kollapalem": "కొల్లపాలెం", "Racharlapalem": "రాచర్లపాలెం", "Other area in Kaza": "కాజాలోని ఇతర ప్రాంతం",
 "Movva": "మొవ్వ", "Kuchipudi": "కూచిపూడి", "Nidumolu": "నిడుమోలు", "Kosuru": "కోసూరు", "Pedamuttevi": "పెదముత్తేవి", "China Muttevi": "చినముత్తేవి",
 "Roads": "రోడ్లు", "Water": "తాగునీరు", "Drainage": "మురుగు కాలువలు", "Sanitation": "పారిశుధ్యం", "Streetlights": "వీధి దీపాలు",
 "Public facilities": "ప్రజా సౌకర్యాలు", "Agriculture": "వ్యవసాయం", "Education": "విద్య", "Other": "ఇతరాలు",
 # status
 "Reported": "నమోదైంది", "Verified": "నిర్ధారించారు", "Sent to office": "కార్యాలయానికి పంపారు", "Acknowledged": "అధికారులు చూశారు",
 "In progress": "పని జరుగుతోంది", "Rejected": "తిరస్కరించారు",
 # map
 "Kaza village map": "కాజా ఊరి మ్యాప్",
 "The red outline is Kaza village. Satellite view, problem pins and directions are limited to Kaza.": "ఎర్ర గీత లోపల ఉన్నదే కాజా ఊరు. శాటిలైట్ ఫోటో, సమస్య పిన్‌లు, దారి అన్నీ కాజాకే పరిమితం.",
 "↻ Reload map": "↻ మ్యాప్ మళ్లీ చూపండి", "📍 My location": "📍 నేను ఉన్న చోటు", "With office / in progress": "కార్యాలయంలో / పని జరుగుతోంది",
 "Directions to Kaza ↗": "కాజాకు దారి ↗", "Places in Kaza": "కాజాలోని ప్రాంతాలు",
 "Localities inside the Google Maps outline of Kaza. Positions are approximate. Check with the Gram Panchayat.": "గూగుల్ మ్యాప్స్‌లో కాజా గీత లోపల ఉన్న ప్రాంతాలు. చోటు సుమారుగా ఇచ్చాం. పంచాయతీ దగ్గర సరిచూసుకోండి.",
 "Directions": "దారి", "Street View ↗": "వీధి ఫోటోలు ↗", "Public places in Kaza": "కాజాలోని ప్రజా ప్రదేశాలు",
 "From the Krishna District public utilities list. Tap to find on Google Maps.": "కృష్ణా జిల్లా వెబ్‌సైట్‌లోని జాబితా నుండి. గూగుల్ మ్యాప్స్‌లో చూడడానికి నొక్కండి.",
 "Google Maps satellite view of Kaza": "కాజా గూగుల్ మ్యాప్స్ శాటిలైట్ ఫోటో", "Village problems": "ఊరి సమస్యలు",
 # login / register
 "FOLLOW PROGRESS": "ఎంతవరకు వచ్చిందో చూడండి", "Track a report": "ఫిర్యాదు స్థితి చూడండి", "Report ID": "ఫిర్యాదు ఐడి", "My reports": "నా ఫిర్యాదులు", "ID": "ఐడి", "Area": "ప్రాంతం", "Status": "స్థితి",
 "Report received": "ఫిర్యాదు అందింది", "VERIFY MOBILE": "మొబైల్ నిర్ధారణ", "Verify your mobile number": "మీ మొబైల్ నంబర్ నిర్ధారించండి",
 "Browsing is open to everyone. A one-time password is needed only to send a report. Your number stays private.": "అందరూ చూడవచ్చు. ఫిర్యాదు చేయడానికి మాత్రమే ఒక్కసారి వాడే పాస్‌వర్డ్ (OTP) కావాలి. మీ నంబర్ ఎవరికీ కనిపించదు.",
 "Mobile number": "మొబైల్ నంబర్", "Send OTP →": "OTP పంపండి →", "Test mode:": "పరీక్ష విధానం:", "your OTP is": "మీ OTP:", ". Real SMS is not connected yet.": ". నిజమైన SMS ఇంకా కలపలేదు.",
 "Verify and continue →": "నిర్ధారించి ముందుకు వెళ్లండి →", "Change number": "నంబర్ మార్చండి", "6-digit OTP": "6 అంకెల OTP",
 "CREATE YOUR PROFILE": "మీ వివరాలు", "Welcome! Register once": "స్వాగతం! ఒక్కసారి నమోదు చేసుకోండి",
 "Your mobile number is verified. Add your name and village so volunteers know who reported.": "మీ నంబర్ నిర్ధారణ అయింది. ఎవరు చెప్పారో వాలంటీర్లకు తెలియడానికి మీ పేరు, ఊరు రాయండి.",
 "Your name": "మీ పేరు", "Your village": "మీ ఊరు",
 "I agree that my name and mobile number are used only to verify my reports. They are not shown publicly.": "నా పేరు, మొబైల్ నంబర్‌ను నా ఫిర్యాదులు నిర్ధారించడానికి మాత్రమే వాడతారు. ఇవి ఎవరికీ కనిపించవు. ఇందుకు నేను ఒప్పుకుంటున్నాను.",
 "Save and continue →": "భద్రపరిచి ముందుకు వెళ్లండి →",
 # report form
 "Report a village problem": "ఊరి సమస్య చెప్పండి",
 "Mark the exact spot, describe the problem, and add a photo. Volunteers check each report and share verified ones with the Gram Panchayat and Grama Sachivalayam.":
   "ఆ చోటు మ్యాప్‌లో చూపండి, సమస్య రాయండి, ఫోటో పెట్టండి. వాలంటీర్లు చూసి, నిర్ధారించినవి పంచాయతీ, గ్రామ సచివాలయానికి పంపుతారు.",
 "🔊 Listen to instructions in Telugu": "🔊 ఎలా చేయాలో తెలుగులో వినండి", "Where is the problem?": "సమస్య ఎక్కడ ఉంది?",
 "Tap inside the red outline to drop the pin, or drag the pin. The button jumps to where you are standing.": "ఎర్ర గీత లోపల నొక్కి పిన్ పెట్టండి, లేదా పిన్‌ను జరపండి. 'నేను ఉన్న చోటు' బటన్ మీరు నిలబడిన చోటుకు తీసుకెళ్తుంది.",
 "📍 Use my location": "📍 నేను ఉన్న చోటు", "Check in Google Maps ↗": "గూగుల్ మ్యాప్స్‌లో చూడండి ↗", "No pin yet.": "ఇంకా పిన్ పెట్టలేదు.",
 "What is the problem?": "సమస్య ఏమిటి?", "Street or landmark": "వీధి పేరు లేదా గుర్తు", "Describe the problem": "సమస్య వివరంగా రాయండి",
 "🎙️ Speak in English": "🎙️ ఇంగ్లీష్‌లో చెప్పండి", "🔊 Read in Telugu": "🔊 తెలుగులో చదివి వినిపించు", "Photo (optional)": "ఫోటో (కావాలంటే)",
 "Your exact pin is seen only by volunteers and officers, who use it to get directions to the spot. By sending, you agree to share this report with the Gram Panchayat and Grama Sachivalayam.":
   "మీరు పెట్టిన పిన్‌ను వాలంటీర్లు, అధికారులు మాత్రమే చూస్తారు. ఆ చోటుకు రావడానికి వారు దీన్ని వాడతారు. పంపితే, ఈ ఫిర్యాదును పంచాయతీ, సచివాలయానికి ఇవ్వడానికి మీరు ఒప్పుకున్నట్టే.",
 "Send report": "ఫిర్యాదు పంపండి", "e.g. near the church": "ఉదా. చర్చి దగ్గర", "10-digit number": "10 అంకెల నంబర్",
 "REPORT RECEIVED": "ఫిర్యాదు అందింది", "Your report is saved": "మీ ఫిర్యాదు నమోదైంది",
 "Keep this ID. Volunteers will check your report, and once verified it appears on the map and dashboard.": "ఈ ఐడి భద్రంగా ఉంచుకోండి. వాలంటీర్లు చూసి నిర్ధారించాక ఇది మ్యాప్‌లో కనిపిస్తుంది.",
 "Copy ID": "ఐడి కాపీ చేయండి", "Track this report →": "ఈ ఫిర్యాదు స్థితి చూడండి →", "Report another": "ఇంకొకటి చెప్పండి", "Directions to the spot": "ఆ చోటుకు దారి",
 # projects / resources
 "TRANSPARENCY & PROGRESS": "ఊరి పనుల వివరాలు", "Browse recorded local work by village and category. DEMO entries are sample data.": "ఊరు, రకం ప్రకారం నమోదైన పనులు చూడండి. DEMO అని ఉన్నవి నమూనా మాత్రమే.",
 "No matching records. Try another filter.": "ఏమీ దొరకలేదు. వేరే ఎంపిక ప్రయత్నించండి.",
 "LEARN · GROW · CONNECT": "నేర్చుకోండి · ఎదగండి", "Resources & opportunities": "ఉపయోగకరమైన సమాచారం, అవకాశాలు",
 "Starting points for useful public information. Verify eligibility and deadlines with the official provider.": "ఉపయోగపడే ప్రభుత్వ సమాచారానికి లింకులు. అర్హత, చివరి తేదీలు అధికారిక సైట్‌లో సరిచూసుకోండి.",
 "ⓘ These are external resources; VillageIntel does not issue benefits or guarantee eligibility.": "ⓘ ఇవి బయటి వెబ్‌సైట్లు. విలేజ్‌వాయిస్ ఏ సాయమూ ఇవ్వదు, అర్హతకు హామీ ఇవ్వదు.",
 "Farmers": "రైతులు", "Agriculture information": "వ్యవసాయ సమాచారం", "Explore agriculture services and resources.": "వ్యవసాయ సేవలు చూడండి.", "AP Agriculture portal ↗": "ఏపీ వ్యవసాయ పోర్టల్ ↗",
 "Students": "విద్యార్థులు", "Scholarships & education": "స్కాలర్‌షిప్‌లు, చదువు", "Check scholarship eligibility and notices.": "స్కాలర్‌షిప్ అర్హత, ప్రకటనలు చూడండి.", "National Scholarship Portal ↗": "జాతీయ స్కాలర్‌షిప్ పోర్టల్ ↗",
 "Skills & jobs": "నైపుణ్యాలు, ఉద్యోగాలు", "Training and employment": "శిక్షణ, ఉపాధి", "Explore skill-development and employment services.": "నైపుణ్య శిక్షణ, ఉపాధి సేవలు చూడండి.", "Skill India Digital ↗": "స్కిల్ ఇండియా డిజిటల్ ↗",
 "Public services": "ప్రజా సేవలు", "Government information": "ప్రభుత్వ సమాచారం", "Check official state services and announcements.": "రాష్ట్ర ప్రభుత్వ సేవలు, ప్రకటనలు చూడండి.", "Andhra Pradesh portal ↗": "ఆంధ్రప్రదేశ్ పోర్టల్ ↗",
 "Businesses": "వ్యాపారాలు", "Local enterprise support": "చిన్న వ్యాపారాలకు సాయం", "Explore public information for small enterprises.": "చిన్న వ్యాపారాల కోసం సమాచారం చూడండి.", "Udyam Registration ↗": "ఉద్యమ్ రిజిస్ట్రేషన్ ↗",
 "Community": "ఊరి ప్రజలు", "Share a local resource": "ఊరిలో ఉన్న సౌకర్యం చెప్పండి", "Suggest a local service or opportunity for review.": "ఊరిలో ఉన్న సేవ లేదా అవకాశం గురించి చెప్పండి.", "Report a problem →": "సమస్య చెప్పండి →",
 # officer
 "GRAMA SACHIVALAYAM": "గ్రామ సచివాలయం", "Officer sign in": "అధికారి లాగిన్",
 "For the Karyadarsi and Sachivalayam staff. See verified village problems, get directions, and update progress.": "కార్యదర్శి, సచివాలయ సిబ్బంది కోసం. ఊరి సమస్యలు చూడండి, దారి తెలుసుకోండి, పని ఎంతవరకు వచ్చిందో మార్చండి.",
 "Password": "పాస్‌వర్డ్", "Sign in →": "లాగిన్ →", "Verified village problems": "నిర్ధారించిన ఊరి సమస్యలు",
 "Volunteers have checked these reports. Open directions, read in Telugu, and update the status so villagers can see progress.": "వాలంటీర్లు ఈ ఫిర్యాదులు చూశారు. దారి చూడండి, తెలుగులో చదవండి, ఊరి వాళ్లకు కనిపించేలా స్థితి మార్చండి.",
 "Print report": "రిపోర్ట్ ప్రింట్", "Sign out": "లాగౌట్", "Open": "కొత్తవి", "Problem": "సమస్య", "Where / evidence": "ఎక్కడ / ఫోటో", "Update": "మార్పు",
 "No reports in this list.": "ఈ జాబితాలో ఏమీ లేవు.", "days open": "రోజులుగా ఉంది", "Overdue": "ఆలస్యం", "Save": "భద్రపరచు",
 "This page isn't on the map.": "ఈ పేజీ దొరకలేదు.", "Check the address or return to the dashboard.": "చిరునామా సరిచూడండి, లేదా హోమ్‌కి వెళ్లండి.", "Return to dashboard": "హోమ్‌కి వెళ్లండి",
}
TE.update({
 "Search problems, places, schemes": "సమస్యలు, ప్రాంతాలు, పథకాలు వెతకండి", "Search a problem, place or scheme": "సమస్య, ప్రాంతం లేదా పథకం వెతకండి", "Search": "వెతకండి", "Search results": "వెతికిన ఫలితాలు",
 "Type a word like road, water, a place name, a scheme or a report ID.": "రోడ్డు, నీరు, ఊరి పేరు, పథకం లేదా ఫిర్యాదు ఐడి రాయండి.", "Nothing found. Try another word.": "ఏమీ దొరకలేదు. వేరే పదం ప్రయత్నించండి.",
 "Problems": "సమస్యలు", "Places": "ప్రాంతాలు", "Schemes and links": "పథకాలు, లింకులు", "Map": "మ్యాప్",
 "Important numbers": "ముఖ్యమైన ఫోన్ నంబర్లు", "Tap a number to call.": "ఫోన్ చేయడానికి నంబర్ నొక్కండి.", "Emergency": "అత్యవసరం", "Ambulance": "అంబులెన్స్", "Police": "పోలీస్", "Fire": "అగ్నిమాపక",
 "Photo, pin, done in 2 minutes": "ఫోటో, పిన్ — రెండు నిమిషాల్లో", "Satellite view of Kaza": "కాజా శాటిలైట్ ఫోటో", "Check progress with your ID": "మీ ఐడితో చూడండి", "Listen in Telugu": "తెలుగులో వినండి", "How to report, spoken": "ఎలా చెప్పాలో వినండి",
 "Open in new tab ↗": "కొత్త ట్యాబ్‌లో ↗", "✕ Close": "✕ మూసివేయండి", "Open here": "ఇక్కడే తెరవండి", "New tab ↗": "కొత్త ట్యాబ్ ↗",
 "Official websites. Tap Open here to view inside this site. Some government websites do not allow this, then use New tab.": "అధికారిక వెబ్‌సైట్లు. 'ఇక్కడే తెరవండి' నొక్కితే ఈ సైట్‌లోనే చూడవచ్చు. కొన్ని ప్రభుత్వ సైట్లు ఇలా చూపనివ్వవు, అప్పుడు 'కొత్త ట్యాబ్' వాడండి.",
 "Agriculture department": "వ్యవసాయ శాఖ", "Schemes, advice and services for farmers (Government of India).": "రైతులకు పథకాలు, సలహాలు, సేవలు (భారత ప్రభుత్వం).", "PM-KISAN": "పీఎం కిసాన్", "Income support for farmer families.": "రైతు కుటుంబాలకు ఆదాయ సహాయం.",
 "Farmers Portal": "రైతుల పోర్టల్", "Weather, market prices and schemes for farmers.": "రైతులకు వాతావరణం, మార్కెట్ ధరలు, పథకాలు.", "Scholarships": "స్కాలర్‌షిప్‌లు", "Skill training": "నైపుణ్య శిక్షణ", "Training and job services.": "శిక్షణ, ఉద్యోగ సేవలు.",
 "Krishna District website": "కృష్ణా జిల్లా వెబ్‌సైట్", "Official district notices, offices and directory.": "జిల్లా ప్రకటనలు, కార్యాలయాలు, వివరాలు.", "India.gov.in": "ఇండియా.గవ్.ఇన్", "National portal for government services.": "ప్రభుత్వ సేవల జాతీయ పోర్టల్.",
 "Udyam Registration": "ఉద్యమ్ రిజిస్ట్రేషన్", "Registration for small businesses.": "చిన్న వ్యాపారాల రిజిస్ట్రేషన్.", "Resources & opportunities": "ఉపయోగకరమైన సమాచారం, అవకాశాలు", "Search": "వెతకండి",
})
TE.update({"Read": "చదవండి", "Guide": "గైడ్", "← Back to resources": "← వనరులకు తిరిగి",
 "Guides written for Kaza villagers and official websites. Verify eligibility and dates with the office before you apply.": "కాజా ప్రజల కోసం రాసిన గైడ్‌లు, అధికారిక వెబ్‌సైట్లు. దరఖాస్తు చేసే ముందు అర్హత, తేదీలు కార్యాలయంలో సరిచూసుకోండి."})
TE.update({"Satellite view ↗": "శాటిలైట్ ఫోటో ↗"})
TE.update({"This week's summary →": "ఈ వారం సారాంశం →", "This week's summary": "ఈ వారం సారాంశం", "New reports this week": "ఈ వారం కొత్త ఫిర్యాదులు", "Open for 7+ days": "7 రోజులకు పైగా ఉన్నవి",
 "Average days to fix": "పరిష్కారానికి సగటు రోజులు", "🔊 Listen to the summary in Telugu": "🔊 సారాంశం తెలుగులో వినండి", "🔊 Listen: places of Kaza": "🔊 కాజా ప్రాంతాలు వినండి",
 "A short picture of what has happened in Kaza. Good to read aloud at a Gram Sabha.": "కాజాలో ఏం జరిగిందో చిన్న సారాంశం. గ్రామసభలో చదివి వినిపించడానికి బాగుంటుంది.", "Summary": "సారాంశం"})
TE.update({"Nearby villages": "చుట్టుపక్కల ఊర్లు", "Mallampalli": "మల్లంపల్లి", "Bollapadu": "బొల్లపాడు", "Polavaram": "పోలవరం", "Rayavaram": "రాయవరం", "Kanchakodur": "కంచకోడుర్", "Maddipatla": "మద్దిపట్ల", "Mallavolu": "మల్లవోలు"})
TE.update({"Open website ↗": "వెబ్‌సైట్ తెరవండి ↗"})
PAT = [
 (re.compile(r"^OTP sent to \+91 (.+?)\. Valid for 5 minutes\.$"), lambda m: f"OTP +91 {m[1]} నంబర్‌కు పంపబడింది. 5 నిమిషాలు చెల్లుతుంది."),
 (re.compile(r"^Official reference: (.+?) · Updated (.+)$"), lambda m: "అధికారిక సంఖ్య: " + ("ఇంకా లేదు" if m[1] == "not yet available" else m[1]) + f" · నవీకరణ: {m[2]}"),
 (re.compile(r"^No report found with ID (.+?)\. Check the ID and try again\.$"), lambda m: f"ఐడి {m[1]} తో రిపోర్ట్ కనబడలేదు. ఐడిని సరిచూసి మళ్లీ ప్రయత్నించండి."),
]

def _tr(t):
    if t in TE: return TE[t]
    for rx, f in PAT:
        m = rx.match(t)
        if m: return f(m)

def translate_html(html):
    def text(m):
        tag, raw = m.group(1), m.group(2)
        if tag.startswith("<option") and "value=" not in tag: return m.group(0)   # never change a submitted value
        te = _tr(unescape(raw).strip())
        if not te: return m.group(0)
        return tag + raw[:len(raw) - len(raw.lstrip())] + escape(te, quote=False) + raw[len(raw.rstrip()):]
    html = re.sub(r"(<[^<>]*>)([^<>]+)(?=<)", text, html)
    def attr(m):
        te = TE.get(unescape(m.group(2)))
        return f'{m.group(1)}="{escape(te)}"' if te else m.group(0)
    return re.sub(r'\b(placeholder|aria-label|label)="([^"]*)"', attr, html)
