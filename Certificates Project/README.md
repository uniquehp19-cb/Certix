# KITE Certificate Portal (Flask Web App)

A web UI version of your certificate generator + emailer script, built with Flask.

## 📁 Folder Structure

```
kite_certificate_portal/
├── app.py                     # Main Flask app (all routes)
├── config.py                  # Loads settings from .env
├── requirements.txt
├── .env.example                # Copy to .env and fill in your secrets
├── credentials.json            # YOUR Google service account key (you must add this)
├── fonts/
│   └── GreatVibes-Regular.ttf  # YOU must add this font file
├── static/
│   ├── certificate_template.png # YOU must add your certificate background
│   ├── css/style.css
│   └── js/script.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── add_data.html
│   ├── view_data.html
│   ├── delete_row.html
│   ├── generate_certificates.html
│   ├── send_emails.html
│   └── schedule_emails.html
├── utils/
│   ├── sheet_helper.py     # Google Sheet read/write
│   ├── certificate_generator.py
│   ├── email_sender.py
│   └── processor.py        # bulk send logic + live progress tracking
└── certificates/           # generated PDFs land here (auto-created)
```

## 🚀 Setup Steps

1. **Install Python packages**
   ```
   pip install -r requirements.txt
   ```

2. **Add your secret files** (these are NOT included for security/size reasons):
   - `credentials.json` → your Google service account key, place in the project root.
   - `fonts/GreatVibes-Regular.ttf` → your certificate font.
   - `static/certificate_template.png` → your certificate background image.

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in `SENDER_EMAIL`, `SENDER_PASSWORD` (Gmail App Password), `GOOGLE_SHEET_KEY`, and a random `FLASK_SECRET_KEY`.
   - ⚠️ Your old code had the Gmail password hardcoded directly in the script — moving it to `.env` keeps it out of your code/GitHub. Never commit `.env`.

4. **Run the app**
   ```
   python app.py
   ```
   Then open **http://127.0.0.1:5000** in your browser.

## ✅ Features (mapped from your original menu)

| Old menu option | New web page |
|---|---|
| 1. Add Data to Sheet | `/add` |
| 2. View Sheet Data | `/view` |
| 3. Delete Row | `/delete` |
| 4. Generate Certificates | `/generate` |
| 5. Send Emails Immediately | `/send` |
| 6. Send Emails at Custom Time (Alarm Mode) | `/schedule` |
| 8. Dashboard | `/` (home page) |

Sending and scheduling now run in a **background thread**, and the page shows a **live log** that auto-refreshes every 3 seconds (via `/job-status`), so you don't have to watch a terminal.

## 📝 Notes
- Keep the Flask app/server running for "Schedule Send" (alarm mode) to trigger at the chosen time — just like your original script needed the terminal open.
- `certificates/` folder auto-fills with generated PDFs; you can download any of them from the "Generate Certificates" page.
