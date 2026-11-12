# coding-contest-agent (Codename: UpsolveAgent)

## Problem Statement
> **How might we turn competitive coding contests from missed calendar events into an automated growth loop: effortlessly syncing upcoming rounds to any phone or laptop calendar with timely alarms, and delivering a clean AI post-mortem report that diagnoses submission mistakes and guides upsolving?**

---

## Recommended Direction: Installable Progressive Web App (PWA) + AI Upsolve Engine

Built specifically as an interactive, showcase-ready mini-project that **anyone can install on their phone or laptop within 10 seconds** without touching a terminal or configuring API keys.

1. **Installable Anywhere (PWA Architecture):**
   - **On Phones (iOS / Android):** Visitors tap *"Install"* or *"Add to Home Screen"* to install the app with an icon, opening full-screen like a native mobile app.
   - **On Laptops (Windows / macOS):** Users can install it via Chrome/Edge into a dedicated standalone desktop app window.
   - **Zero Setup Friction:** Evaluators and peers can test it live via a single URL or QR code without running code locally.

2. **Pre-Contest: Live Contest Hub & 1-Click Calendar Alarms:**
   - Aggregates upcoming contests across **LeetCode** and **Codeforces** with live countdown timers and platform filters.
   - **1-Click Calendar Sync:** Generates an `.ics` event or Google Calendar link with built-in alarms (e.g., 2 hours and 15 minutes before) so users receive native phone and laptop notifications.

3. **Post-Contest: AI Blunder Diagnosis & Socratic Upsolving:**
   - The user inputs their LeetCode or Codeforces handle.
   - The agent retrieves their latest contest submissions live via public APIs.
   - When a problem was attempted and failed (or unsolved), the AI agent compares their submission against the official contest editorial and produces:
     - **Blunder Diagnosis:** Pinpoints why the code failed (e.g., $O(N^2)$ Time Limit Exceeded, integer overflow, missed edge case).
     - **Interactive Socratic Hints:** 3 progressive, spoiler-free hints that encourage the user to solve it themselves before revealing the solution.
     - **Rebound Practice:** Links to 2 similar past contest problems to reinforce the concept.
     - **Exportable Markdown Report:** A clean, downloadable Markdown debrief file for the user's personal notes.

---

## Key Assumptions to Validate

- [ ] **Assumption 1 (PWA Install Experience):** The app manifest and service worker allow seamless "Add to Home Screen" on both Android (Chrome) and iOS (Safari) with a responsive, app-like UI.  
  *How to test:* Deploy a minimal PWA template and verify installation flow on both a smartphone and a laptop.
- [ ] **Assumption 2 (Zero-Auth Platform Scraping):** Codeforces REST API and LeetCode GraphQL API can reliably retrieve a user's recent contest submissions and verdicts without requiring passwords or private session cookies.  
  *How to test:* Prototype API requests fetching recent contest submissions for a public handle.
- [ ] **Assumption 3 (AI Editorial Grounding):** The Gemini free-tier API can accurately diagnose submission blunders and formulate spoiler-free hints when conditioned on the official contest editorial.  
  *How to test:* Run sample failed submissions through the prompt with official editorials and evaluate diagnostic precision.

---

## MVP Scope (v1)

### What's In:
1. **Frontend (Installable PWA):**
   - Clean, modern, responsive UI (dark-mode friendly for programmers).
   - "Install App" prompt banner for phones and laptops.
   - Upcoming Contest Tab: Cards displaying contest names, start times, durations, and countdowns.
   - 1-Click "Add to Calendar" button (downloads `.ics` file with `-2h` and `-15m` alarms or opens Google Calendar).
2. **AI Post-Contest Debrief Tab:**
   - Handle input field (LeetCode / Codeforces).
   - Contest submission selector showing solved vs. failed problems.
   - Interactive debrief card displaying:
     - Topic tags (e.g., *Dynamic Programming, Prefix Sums*).
     - Failure analysis (e.g., *TLE on test case 14: nested loop over $10^5$ items*).
     - Accordion-style collapsible Socratic hints.
     - "Download Markdown Report" button.
3. **Backend Service (Python FastAPI):**
   - Live scraper endpoint for upcoming LeetCode & Codeforces contests.
   - User contest submission fetcher (Codeforces API + LeetCode public GraphQL).
   - AI debrief generator endpoint powered by Google Gemini API.
4. **Cloud Deployment:**
   - Free deployment configuration (e.g., Render / Hugging Face Spaces / Vercel) providing a live public URL ready for presentation.

---

## Not Doing (and Why)

- **Not Publishing to Google Play Store / Apple App Store:** App stores require paid developer licenses ($99/year for Apple, $25 for Google) and week-long review processes. A PWA delivers the same installed home screen experience instantly and for free.
- **Not Doing Full Google Calendar OAuth in v1:** Direct `.ics` download and web intents provide universal calendar sync without forcing users through Google Cloud Console credential setups.
- **Not Doing CodeChef in v1:** CodeChef has aggressive bot-blocking and frequent layout changes that could break during a live project presentation. LeetCode + Codeforces provide stable APIs.
- **Not Building Complex User Accounts / Database:** Everything is driven by public usernames and client-side storage (localStorage), keeping the app lightweight, fast, and free to host.

---

## Tech Stack Summary

- **Backend:** Python (FastAPI) + `requests` / `httpx` + `icalendar`
- **Frontend:** Responsive HTML5 / TailwindCSS / Vanilla JS (with PWA Web App Manifest and Service Worker)
- **AI Brain:** Google Gemini 2.5/Flash API (Free Tier)
- **Deployment:** Render / Vercel / Hugging Face Spaces (Free Tier)
