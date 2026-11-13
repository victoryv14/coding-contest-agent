# ContestPulse (coding-contest-agent)

> **A 100% free, one-time setup contest calendar agent that syncs upcoming rounds from Codeforces, LeetCode, and CodeChef directly to your smartphone with native 15-minute phone alarms.**

---

## 🎯 Problem Statement
Competitive programmers often miss scheduled rounds because:
* Chat group reminders (Telegram, Discord, WhatsApp) get buried under message noise.
* Automated phone calls and SMS require expensive paid telecom APIs (Twilio, Exotel).
* Manually adding individual contests to Google Calendar is tedious and easy to forget.

**ContestPulse** solves this with a **zero-cost, one-time setup live calendar subscription feed (`.ics` / WebCal)** and **1-click Google Calendar Event Popups**. Users configure their platform and division preferences once, and their phone calendar automatically stays up to date with loud alarms ringing 15 minutes before every round.

---

## 📁 Repository Structure

```
coding-contest-agent/
├── backend/                       # Server-side Python logic
│   ├── __init__.py
│   ├── main.py                   # FastAPI server & route handlers
│   ├── models/                   # Data structures
│   │   ├── __init__.py
│   │   └── contest.py            # Canonical Contest schema
│   ├── fetchers/                 # Platform APIs & scraping
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base contract
│   │   ├── codeforces.py         # Codeforces REST client
│   │   ├── leetcode.py           # LeetCode GraphQL client
│   │   ├── codechef.py           # CodeChef fetcher + fallback
│   │   └── service.py            # Ingestion manager & TTL cache
│   └── calendar_engine/          # Calendar standards
│       ├── __init__.py
│       └── generator.py          # RFC-5545 .ics & VALARM generator
│
├── frontend/                      # Client-side UI
│   └── index.html                # Mobile web hub & 1-click Google Calendar popup
│
├── requirements.txt               # Dependencies
├── render.yaml                    # Cloud deployment specification
└── README.md                      # Documentation
```

---

## 🚀 Key Features

### Version 1 (Completed & Operational)
- **Zero Cost Forever ($0.00):** Built entirely on free public APIs and standard calendar protocols. No credit card or paid services required.
- **1-Click Google Calendar Event Popups:** Tap any contest card to open Google Calendar with title, timings, and alarms pre-filled!
- **True One-Time Setup Calendar Feed:** Subscribe to `.ics` feed once on iPhone or Google Calendar for permanent background sync.
- **Multi-Platform Aggregation:**
  - **Codeforces:** Official REST API (Div. 1–4, Educational, Global rounds).
  - **LeetCode:** Public GraphQL endpoint (Weekly & Biweekly contests).
  - **CodeChef:** Structured contest ingestion with resilient fallback (Starters, DSA Monday Munch, Cook-Off).
- **Native Phone Alarms (RFC-5545 `VALARM`):** Embeds automatic 15-minute sound/popup alarm triggers directly into calendar events for Android and iOS.
- **Fine-Grained Filtering:** Users can filter by platform and specific contest divisions.
- **Customizable Alarm Labels:** Choose your own lock screen alarm prefix (e.g. `🚨 Contest Alert`).

### Version 2 (Planned: Generative AI Upsolve Engine)
- **Automated Contest Debrief:** Fetches user submissions from Codeforces and LeetCode after a contest ends.
- **AI Blunder Diagnosis:** Uses the Google Gemini API to analyze failed submissions (*Time Limit Exceeded*, *Wrong Answer*) against official contest editorials.
- **Socratic Upsolving:** Generates progressive, spoiler-free hints to help you solve missed problems yourself.

---

## 💻 How to Run Locally

### 1. Set up virtual environment & install dependencies
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the ContestPulse server
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Open in browser
Visit **`http://localhost:8000`** in your browser.

---

## 📡 API Endpoints

| Endpoint | Method | Description | Example Query |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | Lightweight keep-alive health check | `http://localhost:8000/health` |
| `/` | `GET` | Responsive mobile web UI | `http://localhost:8000/` |
| `/api/contests` | `GET` | JSON list of upcoming contests with live countdowns | `/api/contests?platforms=codeforces,leetcode` |
| `/calendar.ics` | `GET` | Dynamic RFC-5545 calendar subscription feed with alarms | `/calendar.ics?platforms=codeforces,leetcode&alarm=15` |
## Cloud Deployment 
The cloud deployment was done with the render plat form using free tier plan of 0.1 CPU and 512 MB storage. But the drawback is that according to render policies the free tier deployed websites will shut down after 15 minutes of inactivity. The time we login again after 15 minutes of inactivity it again goes to start and load the project.

---

## Inactivity Issue Solution
To overcome the inactivity of the website and to  make it online 24/7/365 we send the pings for every 10 minute interval using third party website cron-job.org console
