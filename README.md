# FitBuddy — AI Personal Fitness Companion
> **"Your Workout. Designed Around You."**

FitBuddy is a complete, single-application AI fitness planning web application powered by **FastAPI**, **Google Gemini AI**, **SQLite**, and **Vanilla HTML5/CSS3/JavaScript**.

---

## 1. Quick Start (Windows)

### The Easiest Way: One-Click Setup & Run
To install everything and start the app automatically, double-click or run:
```cmd
setup.bat
```
After the initial setup, you can launch the app at any time with:
```cmd
run.bat
```

---

### Manual Setup (Step-by-Step)

If you prefer to run commands manually in PowerShell or Windows Command Prompt:

#### 1. Navigate to the project directory:
```powershell
cd "c:\Users\SARAN S\OneDrive\Desktop\fitness.ai"
```

#### 2. Create the Python virtual environment:
```powershell
python -m venv venv
```

#### 3. Install required dependencies:
```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### 4. Configure environment variables:
```powershell
copy .env.example .env
```
Open `.env` and set your Google Gemini API key:
```env
APP_NAME=FitBuddy
APP_ENV=development
DEBUG=True
PORT=8000
HOST=127.0.0.1

DATABASE_URL=sqlite:///./fitbuddy.db

# Google Gemini AI Settings
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```
*(FitBuddy accepts both modern `AQ.` format keys and legacy `AIza` keys).*

#### 5. Start FitBuddy:
```powershell
venv\Scripts\python.exe run.py
```

---

## 2. Accessing the Application

- **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Onboarding Questionnaire:** [http://127.0.0.1:8000/onboarding](http://127.0.0.1:8000/onboarding)
- **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Admin Dashboard:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 3. Project Architecture & Structure

```
FitBuddy/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server, page routing & API endpoints
│   ├── config.py                # Environment configuration & settings
│   ├── database.py              # SQLite connection & table initialization
│   ├── models.py                # SQLAlchemy models (User, WorkoutPlan, PlanRevision, Feedback)
│   ├── schemas.py               # Pydantic schemas for data validation
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini.py            # Gemini API client, JSON parser & prompt engine
│   │   └── workout_generator.py # Deterministic 7-day fallback routine generator
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── workout_service.py   # Business logic (plan generation, revisions, feedback)
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── index.html           # Professional SaaS landing page
│   │   ├── onboarding.html      # User biometrics & preferences form
│   │   ├── loading.html         # Loading state screen
│   │   ├── dashboard.html       # 7-day workout split & nutrition guide
│   │   ├── workout.html         # Single workout day session view
│   │   ├── feedback.html        # "Improve My Plan" adaptive feedback form
│   │   ├── history.html         # Plan revision timeline & comparison
│   │   └── admin.html           # Administrator user management
│   │
│   └── static/
│       ├── css/
│       │   └── style.css        # Clean, modern, responsive CSS design
│       └── js/
│           ├── app.js           # API request helpers & toast notifications
│           ├── onboarding.js    # Interactive form & plan generation logic
│           ├── workout.js       # 7-day cards & day completion tracking
│           └── feedback.js      # Feedback submission & version update logic
│
├── tests/
│   ├── __init__.py
│   └── test_app.py              # Automated test suite (Pytest)
│
├── .env                         # Local environment configuration
├── .env.example                 # Example configuration template
├── .gitignore                   # Ignored files (venv, .env, __pycache__)
├── requirements.txt             # Minimal Python dependencies
├── run.py                       # Application entrypoint
├── run.bat                      # One-click startup script for Windows
├── setup.bat                    # One-click installation & startup script
└── README.md                    # Project documentation
```

---

## 4. How Plan Generation Works

1. **User Input:**
   The user enters Name, Age, Weight, Height, Goal, Intensity, Experience, Location, Available Equipment, and Preferred Days.
2. **API Endpoint (`POST /api/generate`):**
   FastAPI validates the payload using Pydantic (`UserCreate`) and persists the user record in SQLite.
3. **Gemini AI Call:**
   `app/ai/gemini.py` constructs a structured prompt requesting strict JSON.
   The model returns:
   - Summary and weekly physiological goal
   - 7 days (Monday through Sunday) with focus, warm-up, exercises (sets, reps, rest, cues), cooldown, and recovery
   - Nutrition targets (calories, protein, hydration, tips)
4. **Fallback Resilience:**
   If the Gemini API key is missing or invalid, or if Google's API encounters an issue, FitBuddy automatically engages `generate_fallback_plan()`. The website never crashes and provides a high-quality 7-day plan.
5. **Persistence & Versioning:**
   The plan is saved to `workout_plans` with Version 1 stored in `plan_revisions`.

---

## 5. Adaptive Feedback & Revision History

- When you request changes (e.g., *"Add more cardio"*, *"Make workouts easier"*, *"More rest days"*), FitBuddy sends your feedback, profile, and current plan to Gemini via `POST /api/feedback`.
- **The original plan is NEVER overwritten.**
- A new version (Version 2, 3, etc.) is created and displayed, while previous versions remain inspectable in `/history`.

---

## 6. Running Tests

Run the test suite with:
```powershell
venv\Scripts\python.exe -m pytest tests/test_app.py -v
```
