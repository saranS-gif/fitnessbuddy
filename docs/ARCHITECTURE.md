# FitBuddy Project Architecture

FitBuddy is an AI-powered fitness plan and nutrition generator built with a modular, separated architecture.

---

## Directory Structure

```text
fitness.ai/
│
├── frontend/                          # All client-facing assets and templates
│   ├── static/                        # Static web assets
│   │   ├── css/                       # Stylesheets (modular CSS)
│   │   │   ├── style.css              # Main design system
│   │   │   ├── components.css         # UI components (cards, badges, modals)
│   │   │   ├── dashboard.css          # User dashboard styles
│   │   │   ├── onboarding.css         # Multi-step onboarding styles
│   │   │   ├── workout.css            # Workout viewer styles
│   │   │   ├── nutrition.css          # Nutrition guidance styles
│   │   │   └── admin.css              # Admin portal styles
│   │   ├── js/                        # Client-side JavaScript
│   │   │   ├── main.js                # Core UI scripts & interactions
│   │   │   ├── onboarding.js          # Multi-step onboarding wizard
│   │   │   ├── dashboard.js           # Progress & activity tracking
│   │   │   ├── workout.js             # Daily workout completion logic
│   │   │   ├── feedback.js            # Plan revision & feedback submission
│   │   │   └── firebase.js            # Client-side authentication
│   │   ├── images/                    # Logos, hero images, exercise icons
│   │   └── fonts/                     # Web fonts
│   └── templates/                     # Jinja2 HTML templates
│       ├── admin/                     # Admin portal views
│       ├── components/                # Reusable UI partials (navbar, cards, toast)
│       ├── dashboard/                 # User dashboard sub-views
│       ├── feedback/                  # Plan revision views
│       ├── onboarding/                # Step-by-step onboarding views
│       ├── public/                    # Landing and public informational pages
│       ├── base.html                  # Base HTML layout with theme & head
│       ├── index.html                 # Landing page
│       ├── onboarding.html            # Onboarding flow
│       ├── dashboard.html             # User dashboard
│       ├── workout.html               # Workout viewer
│       ├── feedback.html              # Plan adjustments & feedback
│       ├── history.html               # Plan revision history
│       └── admin.html                 # Administrator portal
│
├── backend/                           # Server-side application logic
│   └── app/                           # Core FastAPI application
│       ├── ai/                        # AI generation & prompt engineering
│       │   ├── gemini.py              # Google Gemini API client
│       │   ├── prompts.py             # Structured system prompts
│       │   ├── workout_generator.py   # Workout routine generation
│       │   ├── nutrition_generator.py # Dietary recommendation engine
│       │   └── plan_updater.py        # Iterative feedback refinement
│       ├── database/                  # Database management & session factory
│       │   └── database.py            # SQLite / SQLAlchemy engine & session
│       ├── models/                    # SQLAlchemy ORM database models
│       │   ├── user.py                # User entity
│       │   ├── workout.py             # Workout plan & plan revision models
│       │   ├── feedback.py            # User feedback records
│       │   └── admin.py               # Administrator credentials
│       ├── schemas/                   # Pydantic validation schemas
│       │   ├── user.py                # User input & output DTOs
│       │   ├── workout.py             # Workout & nutrition structures
│       │   └── feedback.py            # Feedback submission schemas
│       ├── services/                  # Business logic services
│       │   ├── user_service.py        # User CRUD & profiling
│       │   ├── workout_service.py     # Workout generation orchestration
│       │   ├── feedback_service.py    # Revision management
│       │   └── admin_service.py       # Administrative operations
│       ├── routes/                    # API and web endpoint controllers
│       │   ├── workout_routes.py      # Workout plan endpoints (/api/plan/*)
│       │   ├── user_routes.py         # User management endpoints (/api/users/*)
│       │   ├── feedback_routes.py     # Revision endpoints (/api/feedback/*)
│       │   ├── admin_routes.py        # Admin panel endpoints (/admin/*)
│       │   └── web_routes.py          # Server-rendered HTML page routes
│       ├── utils/                     # Utility functions & helpers
│       │   ├── security.py            # Password hashing & JWT helpers
│       │   └── helpers.py             # Common formatters
│       ├── config.py                  # Backend configuration wrapper
│       ├── dependencies.py            # FastAPI dependency injection
│       └── main.py                    # FastAPI application initialization & routes
│
├── config/                            # Environment & configuration management
│   ├── settings.py                    # Central Pydantic BaseSettings definition
│   └── .env.example                   # Environment variable template
│
├── docs/                              # Project documentation
│   ├── ARCHITECTURE.md                # System structure and architectural design
│   ├── API.md                         # API endpoints and specification
│   └── SETUP.md                       # Installation and setup guide
│
├── tests/                             # Comprehensive test suite
│   ├── conftest.py                    # Pytest test fixtures and path config
│   ├── test_app.py                    # End-to-end integration tests
│   ├── test_workouts.py               # Workout generation tests
│   ├── test_feedback.py               # Plan revision tests
│   ├── test_users.py                  # User management tests
│   └── test_admin.py                  # Admin authentication tests
│
├── main.py                            # Root ASGI entrypoint (Vercel & Uvicorn compatible)
├── run.py                             # Local development launcher
├── run.bat                            # Windows one-click launcher
├── setup.bat                          # Windows one-click environment installer
├── requirements.txt                   # Project Python dependencies
├── pyproject.toml                     # Pytest configuration and project metadata
└── README.md                          # Repository overview and quickstart
```

---

## Architectural Principles

1. **Separation of Concerns**:
   - `frontend/` contains only presentation layer code (HTML Jinja2 templates and client static assets).
   - `backend/` contains all business logic, AI integrations, data persistence, and REST endpoints.
   - `config/` centralizes all environment variables and configuration settings.
   - `docs/` houses technical guides and specifications.

2. **Clean Layered Backend**:
   - **Routes** (`routes/`): Handle HTTP requests, status codes, and input/output mapping.
   - **Services** (`services/`): Execute business logic, manage transactions, and interact with the AI engine.
   - **AI Layer** (`ai/`): Manages prompt composition, Gemini API integration, and fallback algorithms.
   - **Persistence** (`models/` & `database/`): Handles ORM mappings and SQLite storage.
   - **Validation** (`schemas/`): Guarantees data typing and contract compliance using Pydantic.

3. **High Portability**:
   - The root `main.py` and `run.py` automatically inject `backend` into `sys.path`.
   - Existing modules, test runners, and one-click batch scripts function seamlessly.
