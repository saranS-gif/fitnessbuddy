# FitBuddy — AI Personal Fitness Companion
> **"Your Workout. Designed Around You."**

FitBuddy is an intelligent fitness and nutrition planning web application powered by **FastAPI**, **Google Gemini AI**, **SQLite**, and clean **HTML5/CSS3/JavaScript**.

---

## 1. Project File Structure

The project follows a clean, standardized structure matching modern FastAPI architecture:

```text
fitness.ai/
│
├── app/                               # All Python backend application logic
│   ├── main.py                        # FastAPI application & API router mounts
│   ├── config.py                      # Application settings & environment variables
│   ├── dependencies.py                # Request dependencies & admin auth checks
│   │
│   ├── ai/                            # Gemini AI prompt engineering & generator
│   │   ├── gemini.py                  # Gemini 1.5 Flash client & JSON validator
│   │   ├── prompts.py                 # Structured system & generation prompts
│   │   ├── workout_generator.py       # Workout split builder & fallback logic
│   │   ├── nutrition_generator.py     # Macronutrient calculation engine
│   │   └── plan_updater.py            # Plan revision & feedback engine
│   │
│   ├── database/                      # SQLite persistence & database session
│   │   └── database.py                # SQLAlchemy engine, session maker & init
│   │
│   ├── models/                        # SQLAlchemy database models
│   │   ├── user.py                    # User entity & biometrics
│   │   ├── workout.py                 # WorkoutPlan and PlanRevision models
│   │   ├── feedback.py                # User feedback records
│   │   └── admin.py                   # Administrator credentials
│   │
│   ├── schemas/                       # Pydantic validation schemas
│   │   ├── user.py                    # User profile input/output schemas
│   │   ├── workout.py                 # Routine & nutrition guidance schemas
│   │   └── feedback.py                # Plan revision request schemas
│   │
│   ├── services/                      # Business logic services
│   │   ├── user_service.py            # User management operations
│   │   ├── workout_service.py         # Plan generation & persistence
│   │   ├── feedback_service.py        # Versioning & feedback handling
│   │   └── admin_service.py           # Admin queries & user deletion
│   │
│   ├── routes/                        # API & web endpoint controllers
│   │   ├── workout_routes.py          # Plan generation & completion endpoints
│   │   ├── user_routes.py             # User profile endpoints
│   │   ├── feedback_routes.py         # Feedback & history endpoints
│   │   ├── admin_routes.py            # Admin panel endpoints
│   │   └── web_routes.py              # Server HTML page routes
│   │
│   └── utils/                         # Helper functions & security
│       ├── security.py                # Password hashing & JWT helpers
│       └── helpers.py                 # Data formatting helpers
│
├── templates/                         # Jinja2 HTML templates
│   ├── index.html                     # Main landing page
│   ├── onboarding.html                # Multi-step biometrics questionnaire
│   ├── dashboard.html                 # 7-Day workout plan dashboard
│   ├── workout.html                   # Single workout session view
│   ├── feedback.html                  # "Improve My Plan" feedback form
│   ├── history.html                   # Plan revision timeline & comparison
│   ├── loading.html                   # AI generation loading screen
│   ├── admin.html                     # Administrator user management
│   ├── auth_modal.html                # Authentication modal partial
│   ├── base.html                      # Base template layout
│   ├── admin/                         # Admin portal views
│   ├── components/                    # Reusable UI partials (navbar, cards, toast)
│   ├── dashboard/                     # Dashboard view partials
│   ├── feedback/                      # Feedback view partials
│   ├── onboarding/                    # Onboarding step partials
│   └── public/                        # Public informational pages
│
├── static/                            # Static frontend assets
│   ├── css/                           # Stylesheets (style.css, components.css, etc.)
│   ├── js/                            # Client-side JavaScript (app.js, firebase.js, etc.)
│   ├── images/                        # Logos, icons, and hero illustrations
│   └── fonts/                         # Web fonts
│
├── .env                               # Environment variables (API keys & configuration)
├── .env.example                       # Example environment variable template
├── requirements.txt                   # Python dependencies list
├── run.py                             # Development server launcher
├── run.bat                            # Windows one-click launcher
├── setup.bat                          # Windows one-click environment installer
├── pyproject.toml                     # Pytest configuration & project metadata
└── README.md                          # Repository documentation
```

---

## 2. Quick Start (Windows)

### The Easiest Way: One-Click Setup & Run
To install everything and start the app automatically, double-click:
```cmd
setup.bat
```
After the initial setup, you can launch the app at any time with:
```cmd
run.bat
```

---

### Manual Setup (Step-by-Step)

```powershell
# 1. Create the virtual environment
python -m venv venv

# 2. Install dependencies
venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env

# 4. Start the application
venv\Scripts\python.exe run.py
```

---

## 3. Accessing the Application

- **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Onboarding Questionnaire:** [http://127.0.0.1:8000/onboarding](http://127.0.0.1:8000/onboarding)
- **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Admin Dashboard:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 4. Running Tests

Run the full pytest suite:
```powershell
venv\Scripts\python.exe -m pytest tests
```
