# 📘 LanguageLift – Project Status & Architecture Overview

This document summarizes the current state of the **LanguageLift eLearning Management System** project, including architecture decisions, implemented features, and how different components interact.

This serves as a **checkpoint** so future development (or onboarding new contributors) can quickly understand what has already been built.

---

## 🧠 Project Goal

LanguageLift is a full-stack **eLearning Management System** where:

- Students can register, log in, enroll in courses, and track learning progress
- Instructors can create courses and lessons
- The system supports secure authentication and structured relational data

---

## 🏗️ High-Level Architecture

```

Browser (Dash Frontend)
│
▼
Flask REST API (Backend)
│
▼
MySQL Database

```

- **Frontend**: Dash app running on port `8050`
- **Backend**: Flask API running on port `5000`
- **Database**: MySQL (local now → AWS RDS later)

---

## ⚙️ Backend (Flask API)

### 📁 Backend Structure

```

backend/
│
├── app/
│   ├── **init**.py      → Flask app factory, DB + JWT + CORS setup
│   ├── models/
│   │   └── user.py      → User database model
│   └── routes/
│       └── auth.py      → Authentication endpoints
│
├── migrations/          → Database migration history (Alembic)
├── config.py            → App + database configuration
├── run.py               → Entry point to start Flask server
└── requirements.txt     → Backend dependencies

```

---

### 🗄️ Database

We are using **MySQL** because the system has structured, relational data:

| Entity | Reason for relational DB |
|-------|--------------------------|
| Users | Unique emails, roles |
| Courses | Instructor ownership |
| Enrollments | Many-to-many (users ↔ courses) |
| Lessons | Belong to a course |
| Progress | Tracks lesson completion |

**Benefits of MySQL**
- Foreign key constraints
- ACID transactions
- Strong analytical queries
- Easy migration to AWS RDS

---

### 🔄 Database Migrations

We use **Flask-Migrate (Alembic)** to version-control the database schema.

Commands used:
```

flask db init
flask db migrate -m "create users table"
flask db upgrade

```

The `migrations/` folder stores schema history so changes can be safely applied in development and production.

---

### 👤 User Model

File: `backend/app/models/user.py`

Fields:
- `id` (primary key)
- `name`
- `email` (unique)
- `password_hash` (bcrypt hashed)
- `role` (student/instructor/admin)
- `created_at`

---

### 🔐 Authentication System

We implemented **JWT-based authentication**.

#### Endpoints

| Method | Endpoint | Description |
|-------|----------|-------------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Verify credentials and return JWT |
| GET | `/auth/me` | Protected route, returns current user info |

**Flow:**
1. User registers → password is hashed with bcrypt
2. User logs in → backend returns JWT token
3. Token is sent in future requests via:
```

Authorization: Bearer <token>

````

---

### 🌐 CORS

CORS is enabled using:

```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
````

This allows the Dash frontend (port 8050) to call the Flask backend (port 5000).

---

## 🎨 Frontend (Dash App)

### 📁 Frontend Structure

```
frontend/
│
├── app.py       → Dash application with routing + auth logic
└── fenv/        → Frontend virtual environment
```

---

### 🔐 Frontend Authentication Flow

We use `dcc.Store(storage_type="session")` to keep the JWT token during the session.

Pages implemented:

| Page         | Purpose                  |
| ------------ | ------------------------ |
| `/register`  | User registration form   |
| `/login`     | User login form          |
| `/dashboard` | Protected dashboard page |

---

### 🔁 Routing Logic

Dash router callback:

* Reads `url.pathname`
* Checks for stored JWT
* If token exists → calls backend `/auth/me`
* If valid → shows dashboard
* Otherwise → redirects to login

---

### 🚪 Logout Handling

Logout clears session storage and redirects:

```python
if not n or n < 1:
    raise PreventUpdate
return True, "/login"
```

This prevents unwanted redirect loops.

---

## ✅ What’s Fully Working

✔ Flask backend connected to MySQL
✔ Database migrations system
✔ User registration (hashed passwords)
✔ User login with JWT
✔ Protected backend routes
✔ Dash frontend with auth flow
✔ Session-based token handling
✔ Proper login/logout redirects

---

## 🚀 Next Development Steps

### Backend

* Course model + endpoints
* Lesson model + endpoints
* Enrollment system
* Progress tracking

### Frontend

* Course catalog page
* Course detail + lessons view
* Enrollment button
* Progress UI

### Deployment

* Move MySQL → AWS RDS
* Deploy Flask + Dash to AWS EC2
* Add Nginx + HTTPS

---

## 🧠 Summary

We now have a **production-style authentication system** and full backend-frontend integration.

The project is ready to expand into core eLearning features.

This document reflects the system state as of:
**Authentication + Dashboard milestone completed**
