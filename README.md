# FitBuddy — AI Personal Fitness Companion
> **"Your Workout. Designed Around You."**

FitBuddy is an intelligent fitness and nutrition planning web application powered by **FastAPI**, **Google Gemini AI**, **SQLite**, and modern **HTML5/CSS3/JavaScript**.

---

## 1. Clean Architecture Overview

FitBuddy is organized with strict separation of frontend, backend, configuration, and documentation:

```text
fitness.ai/
│
├── frontend/                          # Client-Side Presentation Layer
│   ├── static/                        # Static assets (CSS stylesheets, JS scripts, icons, images)
│   │   ├── css/                       # Modular CSS (style, components, dashboard, etc.)
│   │   ├── js/                        # Client-side JS (main, onboarding, dashboard, workout, etc.)
│   │   ├── images/                    # Logos, hero images, exercise icons
│   │   └── fonts/                     # Web fonts
│   └── templates/                     # Jinja2 HTML Templates
│       ├── admin/                     # Admin portal views
│       ├── components/                # Reusable partials (navbar, cards, toast)
│       ├── dashboard/                 # User dashboard sub-views
│       ├── feedback/                  # Plan revision & feedback views
│       ├── onboarding/                # Multi-step onboarding views
│       ├── public/                    # Landing and informational pages
│       ├── base.html                  # Base HTML layout
│       ├── index.html                 # Main landing page
│       ├── onboarding.html            # User onboarding questionnaire
│       ├── dashboard.html             # User 7-day dashboard
│       ├── workout.html               # Single workout viewer
│       ├── feedback.html              # Plan adjustment form
│       ├── history.html               # Plan revision timeline
│       └── admin.html                 # Administrator portal
│
├── backend/                           # Server-Side Application Layer
│   └── app/                           # Core FastAPI application package
│       ├── ai/                        # AI prompt engineering & Gemini integration
│       │   ├── gemini.py              # Gemini client and JSON schema parser
│       │   ├── prompts.py             # System and user prompts
│       │   ├── workout_generator.py   # Workout generation engine
│       │   ├── nutrition_generator.py # Nutrition planning engine
│       │   └── plan_updater.py        # Feedback plan modifier
│       ├── database/                  # SQLAlchemy engine, session, and init
│       │   └── database.py            # SQLite database connection setup
│       ├── models/                    # Database ORM models
│       │   ├── user.py                # User profile model
│       │   ├── workout.py             # WorkoutPlan and PlanRevision models
│       │   ├── feedback.py            # User feedback model
│       │   └── admin.py               # Administrator model
│       ├── schemas/                   # Pydantic data validation schemas
│       │   ├── user.py                # User request/response schemas
│       │   ├── workout.py             # Workout & nutrition schemas
│       │   └── feedback.py            # Feedback schemas
│       ├── services/                  # Business logic services
│       │   ├── user_service.py        # User operations
│       │   ├── workout_service.py     # Workout plan orchestration
│       │   ├── feedback_service.py    # Feedback & revision handling
│       │   └── admin_service.py       # Admin operations
│       ├── routes/                    # API & Web route controllers
│       │   ├── workout_routes.py      # Workout plan endpoints
│       │   ├── user_routes.py         # User management endpoints
│       │   ├── feedback_routes.py     # Revision endpoints
│       │   ├── admin_routes.py        # Admin panel endpoints
│       │   └── web_routes.py          # HTML page routes
│       ├── utils/                     # Helpers & security
│       │   ├── security.py            # JWT and password hashing
│       │   └── helpers.py             # Common utilities
│       ├── config.py                  # Settings adapter
│       ├── dependencies.py            # Request dependencies
│       └── main.py                    # FastAPI application initialization
│
├── config/                            # Configuration & Environment
│   ├── settings.py                    # Central Pydantic BaseSettings
│   └── .env.example                   # Environment variable template
│
├── docs/                              # Technical Documentation
│   ├── ARCHITECTURE.md                # System structure and design patterns
│   ├── API.md                         # API endpoints and specification
│   └── SETUP.md                       # Comprehensive setup & developer guide
│
├── tests/                             # Automated Test Suite
│   ├── conftest.py                    # Test configuration and fixtures
│   ├── test_app.py                    # End-to-end integration tests
│   ├── test_workouts.py               # Workout generation tests
│   ├── test_feedback.py               # Revision & feedback tests
│   ├── test_users.py                  # User management tests
│   └── test_admin.py                  # Admin authentication tests
│
├── main.py                            # Root ASGI entrypoint (Vercel & Uvicorn compatible)
├── run.py                             # Local development launcher
├── run.bat                            # Windows one-click runner
├── setup.bat                          # Windows one-click environment installer
├── requirements.txt                   # Project Python dependencies
├── pyproject.toml                     # Pytest and project settings
└── README.md                          # Project overview
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
copy config\.env.example .env

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

## 4. Documentation

Detailed documentation is available in the `docs/` folder:
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Setup & Developer Guide](docs/SETUP.md)

---

## 5. Running Tests

Run the full pytest suite:
```powershell
venv\Scripts\python.exe -m pytest tests
```
