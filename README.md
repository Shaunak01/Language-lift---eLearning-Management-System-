# 🎓 LanguageLift – eLearning Management System

A full-stack eLearning platform that enables instructors to create courses and lessons, and allows students to enroll, learn, and track their progress. Built with a scalable backend API, an interactive Dash frontend, and a production-ready deployment setup.

---

## 🚀 Tech Stack

**Backend**
- Python
- Flask (REST API)
- SQLAlchemy (ORM)
- MySQL (Database)
- JWT Authentication

**Frontend**
- Plotly Dash (Interactive Web UI)

**Infrastructure**
- Docker & Docker Compose (local development)
- AWS EC2 (deployment)
- Nginx (reverse proxy – later stage)

**Testing**
- Pytest
- Pytest-Cov (coverage)

---

## 🎯 Project Goals

This project is designed to demonstrate:

- End-to-end system design  
- REST API development  
- Database schema modeling  
- Role-based authentication & authorization  
- Full-stack integration (API + frontend)  
- Cloud deployment with production-style setup  

---

## 👥 User Roles

| Role        | Capabilities |
|------------|--------------|
| **Student** | Browse courses, enroll, view lessons, track progress |
| **Instructor** | Create courses, add lessons, manage content |
| **Admin** *(future)* | View platform analytics and manage users |

---

## 📦 Core Features (MVP)

### 🔐 Authentication
- User registration  
- Login with JWT authentication  
- Role-based access control  

### 📚 Courses
- Instructors can create courses  
- Students can view available courses  

### 🧑‍🎓 Enrollment
- Students can enroll in courses  
- View enrolled courses  

### 📖 Lessons
- Instructors can add lessons to courses  
- Students can view course lessons  

### ✅ Progress Tracking
- Students can mark lessons as completed  
- Track learning progress per course  

---

## 🗂️ Project Structure

```
languagelift/
│
├── backend/ # Flask REST API
│ ├── app/
│ │ ├── models/ # Database models
│ │ ├── routes/ # API route definitions
│ │ ├── services/ # Business logic layer
│ │ ├── schemas/ # Request/response schemas
│ │ └── init.py # App factory
│ ├── migrations/ # Database migrations
│ ├── tests/ # Backend tests
│ ├── config.py
│ └── run.py
│
├── frontend/ # Dash application
│ ├── pages/ # Dash multi-page views
│ ├── components/ # Reusable UI components
│ └── app.py
│
├── infra/ # Deployment & infra configs
│ ├── docker-compose.yml
│ └── nginx.conf (later)
│
├── docs/ # API docs, design notes
├── .env.example # Environment variables template
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema (High Level)

| Table | Purpose |
|------|---------|
| `users` | Stores students & instructors |
| `courses` | Course details created by instructors |
| `enrollments` | Mapping of students to courses |
| `lessons` | Course lesson content |
| `progress` | Tracks student lesson completion |

---

## 🔌 API Overview (Planned)

| Method | Endpoint | Description |
|-------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/courses` | List all courses |
| POST | `/courses` | Create a course (Instructor) |
| POST | `/courses/{id}/enroll` | Enroll in a course |
| GET | `/courses/{id}/lessons` | Get course lessons |
| POST | `/courses/{id}/lessons` | Add lesson (Instructor) |
| POST | `/lessons/{id}/complete` | Mark lesson complete |

---

## 🛠️ Local Development Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/languagelift.git
cd languagelift

2️⃣ Create Environment File
cp .env.example .env

3️⃣ Start Services (DB + Backend)
docker-compose up --build

4️⃣ Run Backend
cd backend
flask run

5️⃣ Run Frontend
cd frontend
python app.py

🧪 Running Tests
cd backend
pytest --cov=app


Goal: Maintain ~80% test coverage.

☁️ Deployment Plan (Later Stage)

Dockerize backend and frontend

Deploy containers to AWS EC2

Use Nginx as reverse proxy

Configure HTTPS with Let’s Encrypt

Optional: Move DB to AWS RDS

📈 Future Enhancements

File/video lesson uploads

Quizzes and grading

Instructor analytics dashboard

Notifications & email system

Admin control panel

🤝 Contributing

This project is built as a learning and portfolio system. Improvements, refactors, and new features are always welcome.


---

Language-lift---eLearning-Management-System
│
├── backend/
│   ├── app/
│   │   ├── __init__.py      ← Creates Flask app + connects DB + registers routes
│   │   ├── models/          ← Database table definitions
│   │   │   └── user.py      ← "users" table schema
│   │   └── routes/          ← API endpoints (controllers)
│   │       └── auth.py      ← /auth/register endpoint
│   │
│   ├── migrations/          ← Auto-generated DB version history (Alembic)
│   ├── config.py            ← Database connection settings
│   ├── run.py               ← Entry point to start the server
│   └── requirements.txt     ← Python packages used
│
├── frontend/                ← (we'll build later)
├── .env                     ← Secrets & DB credentials (NOT committed to Git)
└── README.md
