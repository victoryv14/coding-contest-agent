# ContestPulse (coding-contest-agent)

> **A 100% free, one-time setup contest calendar agent that syncs upcoming rounds from Codeforces, LeetCode, and CodeChef directly to your calendar with 1-click automated subscriptions and reminders.**

---

## 🎯 Problem Statement
Competitive programmers often miss scheduled rounds because:
* Chat group reminders (Telegram, Discord, WhatsApp) get buried under message noise.
* Automated phone calls and SMS require expensive paid telecom APIs (Twilio, Exotel).
* Manually adding individual contests to Google Calendar is tedious and easy to forget.

**ContestPulse** solves this with **1-Click Universal Calendar Auto-Sync (`.ics` / WebCal)**. Users configure their platform and category preferences once, and their phone/desktop calendar automatically stays up to date with all upcoming and future rounds synced in the background.

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
│   └── index.html                # 1-Click Auto-Sync hub & contest schedule
│
├── requirements.txt               # Dependencies
├── render.yaml                    # Cloud deployment specification
└── README.md                      # Documentation
```

---

## 🚀 Key Features

### Version 1 (Completed & Operational)
- **Zero Cost Forever ($0.00):** Built entirely on free public APIs and standard calendar protocols. No credit card or paid services required.
- **⚡ 1-Click Google Calendar Auto-Sync:** One click subscribes your Google Calendar directly to the live feed. All current and future rounds automatically appear on your schedule without adding them one-by-one.
- **🍏 1-Click Apple / Outlook Auto-Sync:** Native `webcal://` integration that opens your device's calendar app and sets up automatic background synchronization in a single tap.
- **Direct Contest Access:** Contest cards provide one-click direct links to registration and problem pages on Codeforces, LeetCode, and CodeChef.
- **Multi-Platform Aggregation:**
  - **Codeforces:** Official REST API (Div. 1–4, Educational, Global rounds).
  - **LeetCode:** Public GraphQL endpoint (Weekly & Biweekly contests).
  - **CodeChef:** Structured contest ingestion with resilient fallback (Starters, DSA Monday Munch, Cook-Off).
- **Embedded Reminder Alarms (RFC-5545 `VALARM`):** Generates standard reminder offsets (15m, 30m, 1h) directly inside the `.ics` events for compatible calendar clients.
- **Fine-Grained Filtering:** Filter by platform and specific contest categories/divisions.
- **Customizable Event Prefixes:** Customize the reminder title prefix (e.g., `🚨 Contest Reminder`).

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
