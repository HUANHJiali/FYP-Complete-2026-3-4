# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an intelligent student examination system (FYP 2025) built with Django + Vue.js, featuring AI-powered grading and question generation using ZhipuAI (GLM-4-Flash).

**Tech Stack:**
- Frontend: Vue.js 3.0 + View UI Plus + Vue Router 4 + Vuex 4
- Backend: Django 4.1.3 + MySQL 8.0+
- AI: ZhipuAI GLM-4-Flash (OpenAI-compatible API)
- Deployment: Docker Compose (recommended) or traditional Nginx + Gunicorn

**User Roles:**
- Admin (type=0): System management
- Teacher (type=1): Create exams, manage questions, grade analytics
- Student (type=2): Take exams, practice, review wrong questions

## Quick Start Commands

### Docker Deployment (Recommended - Zero Config)
```bash
# Windows
docker-start.bat

# Linux/Mac
./docker-start.sh

# Or directly
docker-compose up -d
```

### Local Development

**One-click deployment (requires Python 3.9+ and Node.js 16+):**
```bash
# Windows
cd source
一鍵部署.bat

# Linux/Mac
cd source
chmod +x 一鍵部署.sh
./一鍵部署.sh
```

**Manual startup:**
```bash
# Backend (Terminal 1)
cd source/server
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (Terminal 2)
cd source/client
npm install
npm run serve
```

### Testing
```bash
# Backend tests
cd source/server
python manage.py test

# Test AI functionality
cd source/server
python tools/diagnose_zhipuai.py

# Initialize test data
cd source/server
python init_practice_data.py
```

### Production Deployment
```bash
# Linux server (Ubuntu 20.04/22.04+)
sudo bash deploy/setup_server.sh \
  --project-root /path/to/FYP2025-main \
  --domain your.domain.com \
  --env-file /etc/exam/.env \
  --db-import yes
```

### Build Commands
```bash
# Frontend production build
cd source/client
npm run build  # Outputs to source/client/dist

# Backend uses standard Django management
python manage.py collectstatic  # Collect static files
python manage.py migrate        # Run migrations
```

## Architecture Overview

### Directory Structure
```
source/
├── client/              # Vue.js 3 frontend
│   ├── src/
│   │   ├── api/         # API layer (axios)
│   │   ├── router/      # Vue Router configuration
│   │   ├── store/       # Vuex state management
│   │   ├── views/       # Page components (30+ pages)
│   │   └── components/  # Reusable components
│   └── package.json
├── server/              # Django backend
│   ├── app/             # Main application
│   │   ├── models.py    # 12+ ORM models
│   │   ├── views.py     # Business logic (large file: 220KB)
│   │   ├── urls.py      # API routes
│   │   └── validators.py # Data validation
│   ├── comm/            # Shared utilities
│   │   ├── AIUtils.py   # AI integration (scoring, generation)
│   │   ├── ExamUtils.py # Exam logic
│   │   ├── CommUtils.py # Common utilities
│   │   └── BaseView.py  # Base view classes
│   ├── server/          # Django settings
│   │   └── settings.py  # Environment-based configuration
│   └── requirements.txt
└── env.example          # Environment variables template
```

### Database Models Architecture

**Core Models (12+ tables in `app/models.py`):**
1. Users, Students, Teachers - User authentication and profiles
2. Colleges, Grades - Organization structure
3. Practises, Options - Question bank
4. Exams, ExamLogs, AnswerLogs - Examination system
5. PracticePapers, PracticePaperQuestions, StudentPracticeLogs, StudentPracticeAnswers - Practice system
6. Tasks, TaskQuestions, StudentTaskLogs, StudentTaskAnswers - Task center
7. WrongQuestions, WrongQuestionReviews - Wrong question notebook
8. Messages, MessageReads - Messaging system

**All key fields have database indexes for performance.**

### API Structure

**Backend API routing (`app/urls.py`):**
```
/api/
├── auth/          # JWT authentication
├── users/         # User management
├── exams/         # Exam operations
├── practises/     # Practice system
├── tasks/         # Task center
├── wrong-questions/  # Wrong question notebook
├── messages/      # Messaging
└── ai/            # AI features
    ├── /score/    # AI scoring
    └── /generate/ # AI question generation
```

**Frontend proxy (`client/vue.config.js`):**
```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    ws: true
  }
}
```

## Key Components and Their Relationships

### AI Integration (`comm/AIUtils.py`)

**Three main AI functions:**
1. `ai_score_answer()` - Intelligent scoring for multiple question types (choice, fill-in-blank, true/false, programming). Returns: score, feedback, analysis, confidence.
2. `ai_generate_questions()` - Auto-generate questions by subject, topic, difficulty. Supports retry mechanism for quality.
3. `ai_analyze_wrong_answer()` - Analyze wrong answers and provide improvement suggestions.

**AI Configuration:**
- Provider: ZhipuAI (GLM-4-Flash)
- API Format: OpenAI-compatible
- Environment variables: `ZHIPUAI_API_KEY`, `ZHIPUAI_MODEL`, `ZHIPUAI_BASE_URL`
- Fallback: Can be configured for OpenAI or other compatible APIs

### Practice Paper System

**Complete workflow:**
1. Create practice paper (`PracticePapers`)
2. Associate questions (`PracticePaperQuestions`)
3. Student practice session (`StudentPracticeLogs`)
4. Answer recording (`StudentPracticeAnswers`)
5. Auto-scoring (AI or traditional)
6. Result display (`client/src/views/pages/practiceResult.vue`)

### User Authentication

**JWT-based authentication:**
- Token generation in `app/views.py` (login endpoint)
- Token validation in middleware
- Tokens stored in frontend Vuex store
- Role-based access control via `type` field (0=admin, 1=teacher, 2=student)

**Default test accounts:**
```
admin/123456    (admin)
teacher/123456  (teacher)
student/123456  (student)
```

### Frontend State Management (Vuex)

**Store structure (`client/src/store/`):**
- User state (current user, token)
- Practice state
- Exam state
- Cross-component state sharing

### Frontend Routing

**Route configuration (`client/src/router/index.js`):**
- Lazy-loaded components for performance
- Role-based route guards
- 30+ route definitions for different pages

## Environment Configuration

**Required environment variables (`source/env.example`):**
```bash
# Database
DB_NAME=db_exam
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306

# Django
SECRET_KEY=django-insecure-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS/CSRF
CORS_ALLOWED_ORIGINS=http://localhost:8080
CSRF_TRUSTED_ORIGINS=http://localhost:8080

# AI (ZhipuAI)
ZHIPUAI_API_KEY=your_api_key
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**Configuration loading:** `settings.py` uses `python-dotenv` to load from `.env` file or environment variables. Production must set `SECRET_KEY` via environment.

## Important Implementation Details

### Database Connection
- Uses PyMySQL with `pymysql.install_as_MySQLdb()` for Django MySQL compatibility
- Fallback from `mysqlclient` to `PyMySQL` handled in deployment scripts

### CORS Configuration
- CSRF middleware is **commented out** in `settings.py` line 69 for API-only mode
- CORS handled by `django-cors-headers`
- Configure via `CORS_ALLOWED_ORIGINS` environment variable

### Caching
- Redis support via `django-redis` (optional)
- Falls back to in-memory caching if Redis unavailable
- Cache decorators in `comm/cache_decorator.py`

### Performance Optimizations

**Frontend:**
- Code splitting: vendor, elementUI, echarts, common
- Route lazy loading
- Gzip compression
- Source maps disabled in production

**Backend:**
- Database indexes on all key fields
- Query monitoring middleware (DEBUG only)
- Cache decorators for expensive operations
- Error handling with `comm/error_handler.py`

## Port Allocation

| Service | Development | Production |
|---------|-------------|------------|
| Frontend | 8080 | 80/443 (Nginx) |
| Backend API | 8000 | 8000 (Gunicorn) |
| Database | 3307 (Docker) / 3306 (local) | 3306 |

## Common Development Patterns

### Adding New API Endpoints
1. Define URL in `app/urls.py`
2. Implement view function in `app/views.py` (use `BaseView` from `comm/BaseView.py` for common functionality)
3. Add validation in `app/validators.py` if needed
4. Create frontend API wrapper in `client/src/api/`
5. Update Vuex store if state management needed

### Adding New Frontend Pages
1. Create component in `client/src/views/pages/`
2. Add route in `client/src/router/index.js`
3. Add menu entry in `client/src/views/home.vue` (sidebar menu)
4. Implement API calls using existing API wrappers

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Known Issues and Considerations

1. **Large view file**: `app/views.py` is 220KB+ with mixed concerns. Consider refactoring into separate view modules.
2. **CSRF disabled**: Line 69 in `settings.py` comments out CSRF middleware for API-first design.
3. **Rate limiting**: Available via `django-ratelimit` but middleware commented out (line 74).
4. **Query monitoring**: Only enabled in DEBUG mode, currently commented out to avoid import errors.

## Documentation

**Key documentation files:**
- `source/完整运行指南.md` - Detailed startup guide
- `source/FYP_DEMO_GUIDE.md` - Demo presentation guide
- `source/docs/AI功能使用说明.md` - AI features documentation
- `DOCKER_DEPLOYMENT.md` - Docker deployment guide
- `source/PROJECT_STATUS.md` - Project status and roadmap

## Deployment Architecture

**Development:**
```
Vue Dev Server (8080) → Proxy → Django (8000) → MySQL (3306/3307)
```

**Production (Docker):**
```
Nginx (80/443)
  ├→ Static files (Vue dist)
  └→ /api/* → Gunicorn + Uvicorn (8000) → Django App → MySQL
```

**Production (Traditional):**
- Nginx reverse proxy
- Gunicorn + Uvicorn workers
- systemd service management
- Logs: `/var/log/exam_gunicorn_*.log`
