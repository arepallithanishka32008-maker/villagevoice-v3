@rem Fill in your values. start.bat loads this file automatically.
@rem ---- Alerts to the Karyadarsi (new reports) ----
set KARYADARSI_PHONE=7997872871
set KARYADARSI_EMAIL=arepallithanishka03@gmail.com
@rem Email sender: a Gmail account and its APP PASSWORD (not the normal password)
set SMTP_USER=arepallithanishka03@gmail.com
set SMTP_PASSWORD=
@rem ---- SMS (OTP + alerts): choose ONE and fill its values ----
@rem set SMS_PROVIDER=fast2sms
@rem set FAST2SMS_KEY=
@rem set SMS_PROVIDER=twilio
@rem set TWILIO_SID=
@rem set TWILIO_TOKEN=
@rem set TWILIO_FROM=
@rem ---- ElevenLabs Telugu voice (very natural; free plan = about 10 minutes of audio a month) ----
@rem set ELEVENLABS_API_KEY=
@rem set ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
@rem set ELEVENLABS_MODEL=eleven_v3
@rem ---- Clear Telugu voice (Google Cloud key) ----
set GOOGLE_TTS_KEY=
set GOOGLE_TRANSLATE_KEY=
@rem ---- When the website is online ----
@rem set SITE_URL=https://your-site-link
@rem set HTTPS=1
@rem Test mode shows the OTP on the screen. Real SMS turns it off by itself once SMS works. To force it off: set DEMO_OTP=0
