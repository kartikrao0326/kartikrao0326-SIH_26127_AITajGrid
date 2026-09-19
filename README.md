# TrajGrid Demo Prototype

TrajGrid is a demo prototype linking ANPR plate reads from multiple isolated cameras into ordered vehicle trajectories, deriving traffic analytics, and triggering watchlist alerts.

## Setup Instructions

Ensure you have Python 3.11+ and Node.js 20+ installed.

### 1. Backend Setup
Open a terminal in the root folder and run:
```bash
python -m venv backend/venv
# Windows
backend\venv\Scripts\pip install -r backend/requirements.txt
# Mac/Linux
# source backend/venv/bin/activate && pip install -r backend/requirements.txt
```

Start the backend server:
```bash
# Windows
backend\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Mac/Linux
# ./backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
Open a new terminal in the `frontend` folder and run:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

## Judged Demo Script (< 2 minutes)

1. **Login:** Log in as Operator (Username: `operator`, Password: `operator123`).
2. **Start Simulation:** Click the green "Seed DB (Run Sim)" button in the top right to start emitting live events.
3. **Live Pulses:** Point at the live Leaflet map pulsing with reads.
4. **Clean Trajectory:** Under "Trajectory Search", search for a known clean vehicle plate (e.g., check the backend terminal for a clean plate from phase 3 or pick one from the Live Map). Enter a reason and search. Show the 3-4 hops (solid lines).
5. **Anomalous Trajectory:** Search for an anomalous plate (e.g., cloned/impossible speed). Show the flagged dashed/red hop.
6. **Analytics:** Scroll down to point at the congestion chart updating live.
7. **Watchlist Alert:** Wait for or point at the watchlist alert firing in the "Watchlist Alerts" panel on the right.
