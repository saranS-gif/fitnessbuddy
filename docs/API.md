# FitBuddy API Documentation

FitBuddy provides both server-rendered web routes and RESTful JSON API endpoints.

---

## Interactive Documentation

When running locally, interactive API documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Core API Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Description**: Returns the server operational status.
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "FitBuddy AI"
  }
  ```

---

### 2. Generate Workout Plan
- **Endpoint**: `POST /api/generate`
- **Description**: Creates a user profile and generates a personalized 7-day workout and nutrition plan via Gemini AI (with intelligent fallback).
- **Request Body**:
  ```json
  {
    "name": "Alex",
    "age": 28,
    "weight": 75.0,
    "height": 178.0,
    "goal": "Muscle Gain",
    "intensity": "High",
    "experience": "Intermediate",
    "location": "Gym",
    "equipment": "Full Gym",
    "preferred_days": ["Monday", "Tuesday", "Thursday", "Friday"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "user_id": 1,
    "plan_id": 1,
    "plan": {
      "days": [...],
      "nutrition": {...},
      "disclaimer": "..."
    }
  }
  ```

---

### 3. Retrieve Plan by ID
- **Endpoint**: `GET /api/plan/{plan_id}`
- **Description**: Retrieves full details of a specific workout plan including completed days and current revision.
- **Response**:
  ```json
  {
    "success": true,
    "id": 1,
    "user_id": 1,
    "original_plan": {...},
    "updated_plan": {...},
    "active_plan": {...},
    "completed_days": ["Monday"],
    "created_at": "2026-10-02 14:00:00"
  }
  ```

---

### 4. Toggle Day Completion
- **Endpoint**: `POST /api/plan/{plan_id}/complete`
- **Description**: Marks a specific day in the routine as completed or incomplete.
- **Request Body**:
  ```json
  {
    "day": "Monday",
    "completed": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "day": "Monday",
    "completed": true,
    "completed_days": ["Monday"]
  }
  ```

---

### 5. Submit Plan Feedback / Adjustment
- **Endpoint**: `POST /api/feedback`
- **Description**: Submits user feedback (e.g., "Add more cardio", "Reduce leg volume") to generate a revised plan version while preserving history.
- **Request Body**:
  ```json
  {
    "plan_id": 1,
    "feedback": "I have knee soreness, replace lunges with low-impact exercises."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "plan_id": 1,
    "plan": {...}
  }
  ```

---

### 6. Plan Revision History
- **Endpoint**: `GET /api/history/{user_id}`
- **Description**: Retrieves all versions and feedback history for a user's latest plan.
- **Response**:
  ```json
  {
    "success": true,
    "plan_id": 1,
    "user_id": 1,
    "history": [
      { "version": 1, "created_at": "...", "feedback": null },
      { "version": 2, "created_at": "...", "feedback": "Add more cardio" }
    ]
  }
  ```

---

### 7. Admin Endpoints
- **`GET /admin`**: Admin dashboard view listing all users, metrics, and plan counts.
- **`POST /admin/delete/{user_id}`**: Deletes a user profile and their associated plans.
