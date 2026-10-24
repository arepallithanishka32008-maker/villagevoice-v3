# VillageVoice - Kaza, Movva Mandal (complete, latest version)

START (Windows)
1. Extract this ZIP into a NEW folder.
2. Double-click start.bat  (or in the VS Code terminal: .\start.bat)
3. Open http://127.0.0.1:5000 in Chrome or Edge.

Logins: /admin (coordinator) and /officer/login (Karyadarsi). The passwords are the ones already stored in villagevoice.db.
Forgot them? Open keys.bat, add:  set ADMIN_PASSWORD=your-password   and   set OFFICER_PASSWORD=your-password   then run start.bat.

keys.bat holds the alert contacts and optional keys (Gmail app password, SMS, Google voice). start.bat loads it automatically.
In /admin use: "Send test alert now", "Test Telugu voice", "Remind about overdue reports", and the "Resources page" editor.

What is inside: Kaza-only satellite map with place names, report form with pin + photo + voice typing, OTP login (test mode shows OTP on screen),
instant alerts to the Karyadarsi (SMS + email), officer page, search, Telugu site + Telugu voice, resources guides, weekly summary, installable on phones.
Files you may edit: i18n.py (Telugu words), config.py (villages, Kaza outline, links), keys.bat (settings).

ElevenLabs voice: in keys.bat remove @rem before ELEVENLABS_API_KEY and paste your key (also pick a voice ID). Voice order: ElevenLabs, Google Cloud, free Google voice, device voice.
The site stops using ElevenLabs after ELEVENLABS_MONTHLY_CHARS (default 9000) characters a month and falls back to the next voice.
