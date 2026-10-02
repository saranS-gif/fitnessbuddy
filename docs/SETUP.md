# FitBuddy Setup & Developer Guide

This guide covers getting started with the FitBuddy codebase, running the server, executing tests, and understanding the project layout.

---

## Prerequisites

- **Python 3.10+** installed
- **Git** installed

---

## Quick Start (Windows)

### Option 1: One-Click Setup
1. Double-click **`setup.bat`**:
   - Automatically sets up a virtual environment in `venv/`.
   - Copies `config/.env.example` to `.env`.
   - Installs all requirements.
   - Starts the application.
2. For subsequent launches, double-click **`run.bat`**.

---

### Option 2: Command Line Setup

```bash
# 1. Clone repository and navigate to root
cd fitness.ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create environment file
copy config\.env.example .env

# 6. Start the development server
python run.py
```

The application will start at: **http://localhost:8000**

---

## Environment Configuration

Configuration variables are managed in `config/settings.py` and read from `.env`:

| Variable | Default Value | Description |
|---|---|---|
| `APP_NAME` | `FitBuddy` | Application title |
| `APP_ENV` | `development` | Environment name |
| `DATABASE_URL` | `sqlite:///./fitbuddy.db` | SQLite database URI |
| `GEMINI_API_KEY` | *(empty)* | Optional Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model variant |
| `PORT` | `8000` | Port for the Uvicorn server |
| `HOST` | `127.0.0.1` | Host address |

> **Note**: An API key is optional! If no key is set or the Gemini API is unreachable, FitBuddy automatically uses its built-in rule-based fitness generator with 100% full functionality.

---

## Running the Test Suite

Run the full pytest suite with:

```bash
pytest
```

or with Python executable:

```bash
venv\Scripts\python.exe -m pytest tests
```

---

## Key Directories

- **`frontend/`**: Contains HTML templates (`frontend/templates/`) and static CSS/JS/images (`frontend/static/`).
- **`backend/`**: Contains the FastAPI app, AI routines, database models, services, and route handlers.
- **`config/`**: Central configuration files and settings schemas.
- **`docs/`**: Architecture diagrams, setup instructions, and API docs.
- **`tests/`**: Automated unit and integration tests.
