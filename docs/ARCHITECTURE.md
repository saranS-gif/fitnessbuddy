# FitBuddy Project Architecture

FitBuddy is an intelligent fitness and nutrition planning web application powered by FastAPI, Google Gemini AI, SQLite, and vanilla HTML5/CSS3/JavaScript.

---

## Directory Structure

```text
fitness.ai/
│
├── app/                               # All Python backend application logic
│   ├── main.py                        # FastAPI application entry & router mounts
│   ├── config.py                      # Application configuration & settings
│   ├── dependencies.py                # Request dependencies & admin auth checks
│   │
│   ├── ai/                            # Gemini AI integration & prompt engine
│   │   ├── gemini.py                  # Gemini API client & JSON validator
│   │   ├── prompts.py                 # Structured system prompts
│   │   ├── workout_generator.py       # Workout plan generation engine
│   │   ├── nutrition_generator.py     # Nutrition calculation engine
│   │   └── plan_updater.py            # Iterative feedback refinement
│   │
│   ├── database/                      # SQLite persistence & database session
│   │   └── database.py                # SQLAlchemy engine & session factory
│   │
│   ├── models/                        # SQLAlchemy database models
│   │   ├── user.py                    # User profile entity
│   │   ├── workout.py                 # WorkoutPlan and PlanRevision models
│   │   ├── feedback.py                # User feedback records
│   │   └── admin.py                   # Administrator model
│   │
│   ├── schemas/                       # Pydantic validation schemas
│   │   ├── user.py                    # User input/output schemas
│   │   ├── workout.py                 # Workout & nutrition schemas
│   │   └── feedback.py                # Feedback schemas
│   │
│   ├── services/                      # Business logic services
│   │   ├── user_service.py            # User management operations
│   │   ├── workout_service.py         # Plan generation & persistence
│   │   ├── feedback_service.py        # Feedback & revision handling
│   │   └── admin_service.py           # Admin operations
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
│       └── helpers.py                 # Common utility helpers
│
├── templates/                         # Jinja2 HTML templates
│   ├── index.html                     # Main landing page
│   ├── onboarding.html                # Multi-step biometrics questionnaire
│   ├── dashboard.html                 # 7-Day workout plan dashboard
│   ├── workout.html                   # Single workout session view
│   ├── feedback.html                  # "Improve My Plan" feedback form
│   ├── history.html                   # Plan revision timeline
│   ├── loading.html                   # AI generation loading screen
│   ├── admin.html                     # Administrator portal
│   ├── auth_modal.html                # Authentication modal partial
│   ├── base.html                      # Base HTML layout
│   ├── admin/                         # Admin portal views
│   ├── components/                    # Reusable UI partials
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
