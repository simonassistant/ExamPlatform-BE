# ExamPlatform-BE

FastAPI backend API server for the ExamPlatform examination system.

## Overview

ExamPlatform-BE is the backend service that powers the ExamPlatform examination system. It provides:

- RESTful APIs for examinee exam-taking and proctor management
- JWT-based authentication for both examinees and proctors
- PostgreSQL database integration via SQLAlchemy ORM
- Alibaba Cloud STS credentials for secure file uploads
- Exam paper management with markdown-based paper creation

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115+ | Web framework |
| SQLAlchemy | 2.0+ | ORM and database operations |
| PostgreSQL | — | Primary database |
| psycopg2 | — | PostgreSQL adapter |
| PyJWT | 2.10+ | JWT authentication |
| python-dotenv | 1.1+ | Environment configuration |
| python-ulid | 3.0+ | Unique ID generation |
| Pandas | 2.2+ | Data processing |
| openpyxl | — | Excel file handling |
| markdown-it-py | 3.0+ | Markdown parsing (exam papers) |
| Alibaba Cloud SDK | — | STS credentials & OSS integration |

## Prerequisites

- **Python**: 3.10+
- **PostgreSQL**: Running instance with a database created
- **pip**: Package manager (or use a virtual environment)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Bob8259/ExamPlatform-BE.git
cd ExamPlatform-BE
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the development environment file and adjust values:

```bash
cp .env.dev .env
```

Environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/ep` |
| `ALI_ENDPOINT` | Alibaba Cloud STS endpoint | `sts.cn-shenzhen.aliyuncs.com` |

### 5. Set Up Database

Ensure PostgreSQL is running and the database exists:

```sql
CREATE DATABASE ep;
```

> **Note**: The application uses SQLAlchemy models. Tables are created automatically on first connection if using `create_all()`.

### 6. Start Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
ExamPlatform-BE/
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── test.py                  # Test file
├── app/
│   ├── __init__.py          # App initialization
│   ├── ui/                  # API routes (presentation layer)
│   │   ├── common/          # Shared route utilities
│   │   ├── examinee/        # Examinee-facing endpoints
│   │   └── proctor/         # Proctor-facing endpoints
│   ├── data/                # Data layer
│   │   ├── dao/             # Data Access Objects
│   │   ├── dto/             # Data Transfer Objects
│   │   ├── entity/          # SQLAlchemy models
│   │   ├── tool/            # Data utilities
│   │   └── database.py      # Database connection
│   └── util/                # Utility functions
│       ├── util.py          # General utilities
│       ├── util_ali.py      # Alibaba Cloud utilities
│       └── util_jwt.py      # JWT encoding/decoding
└── deploy/                  # Deployment configurations
```

## API Reference

### Route Prefixes

| Prefix | Role | Description |
|--------|------|-------------|
| `/examinee/exam` | Examinee | Exam-taking operations |
| `/proctor/proctor` | Proctor | Exam management and grading |

### Examinee Endpoints (`/examinee/exam`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/login` | Authenticate examinee (ID + key) |
| `POST` | `/ali_credentials` | Get Alibaba Cloud STS credentials |
| `POST` | `/get_exam` | Get exam details |
| `POST` | `/get_section` | Get section with questions |
| `POST` | `/start_section` | Start a timed section |
| `POST` | `/get_question` | Get question by sequence |
| `POST` | `/list_questions_in_group` | List questions in a group |
| `POST` | `/save_answer` | Save answer (auto-save) |
| `POST` | `/mark` | Mark question for review |
| `POST` | `/section_submit` | Submit section |
| `POST` | `/exam_submit` | Submit entire exam |
| `POST` | `/behavior` | Record examinee behavior |

### Proctor Endpoints (`/proctor/proctor`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/login` | Authenticate proctor (email + password) |
| `GET` | `/schedules` | List exam schedules |
| `GET` | `/session` | Get session details with exams |
| `GET` | `/sessions` | List sessions for a schedule |

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication:

1. **Login**: Client sends credentials to `/login` endpoint
2. **Token**: Server returns `access_token` with `bearer` type
3. **Authorize**: Client includes `Authorization: Bearer <token>` header in requests
4. **Validation**: Protected endpoints use `get_current_user_id` dependency

## Database Entities

| Entity | Description |
|--------|-------------|
| `Users` | Examinee and proctor accounts |
| `Exam` | Individual exam instance for an examinee |
| `ExamSection` | Section within an exam (timed segments) |
| `ExamAnswer` | Examinee's answers |
| `Paper` | Exam template/paper definition |
| `PaperSection` | Section within a paper template |
| `Question` | Individual question |
| `QuestionGroup` | Group of related questions |
| `QuestionOption` | Answer options (for choice questions) |
| `Schedule` | Exam schedule (dates, proctor assignment) |
| `ScheduleSession` | Specific exam session within a schedule |
| `Behavior` | Examinee behavior logs (proctoring) |

## Question Types

| Code | Type | Markdown Key | Category |
|------|------|--------------|----------|
| 1 | Single Choice | `single choice` | Reading |
| 2 | True/False | `true/false` | Reading |
| 3 | Definite Multiple Choice | `definite multiple choice` | Reading |
| 4 | Indefinite Multiple Choice | `indefinite multiple choice` | Reading |
| 5 | Fill-in-the-Blank | `fill in the blank` | Reading/Writing |
| 6 | Writing | `writing` | Writing |
| 7 | Listening | `listening` | Listening |
| 8 | Speaking | `speaking` | Speaking |

## Environment Files

| File | Purpose |
|------|---------|
| `.env.dev` | Development configuration |
| `.env.test` | Testing configuration |
| `.env.prod` | Production configuration |

## Development Notes

### Code Style

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Use **Form()** for POST request parameters

### Naming Conventions

- Routes: `snake_case` (e.g., `section_submit`, `get_exam`)
- DAOs: `{Entity}DAO` with static methods
- Constants: `SCREAMING_SNAKE_CASE`
- Tables: `snake_case` singular (e.g., `exam`, `paper_section`)

### CORS Configuration
>
> **Warning**: CORS is currently permissive (allows all origins). Restrict this in production.

## Related

- [ExamPlatform-FE](../ExamPlatform-FE/README.md) — Frontend examinee application
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
