# System Architecture - 智能在线考试系统

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Vue.js 3.0 + View UI Plus + Vuex 4 + Vue Router 4          ││
│  │  - 30+ Page Components                                      ││
│  │  - Responsive Design                                        ││
│  │  - Real-time Updates                                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Nginx (Production) / Vue Dev Server (Development)          ││
│  │  - Reverse Proxy                                            ││
│  │  - Static File Serving                                      ││
│  │  - Load Balancing                                           ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Django 4.1.3 + Gunicorn + Uvicorn                          ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   ││
│  │  │   Views   │ │  Models   │ │   Utils   │ │    AI     │   ││
│  │  │ (65+ APIs)│ │(28 Tables)│ │ (Helpers) │ │(ZhipuAI)  │   ││
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │   MySQL 8.0+      │  │   Redis (Optional)│                   │
│  │   - 28 Tables     │  │   - Caching       │                   │
│  │   - Indexed       │  │   - Sessions      │                   │
│  └───────────────────┘  └───────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI SERVICE LAYER                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ZhipuAI GLM-4-Flash (OpenAI-compatible API)                ││
│  │  - Intelligent Scoring                                       ││
│  │  - Question Generation                                       ││
│  │  - Answer Analysis                                           ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Vue.js | 3.0 | Core framework |
| View UI Plus | Latest | UI component library |
| Vuex | 4.0 | State management |
| Vue Router | 4.0 | Routing |
| Axios | Latest | HTTP client |
| ECharts | Latest | Charts and visualization |
| Monaco Editor | Latest | Code editor for programming questions |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 4.1.3 | Web framework |
| Gunicorn | Latest | WSGI server |
| Uvicorn | Latest | ASGI server |
| PyMySQL | Latest | MySQL driver |
| django-cors-headers | Latest | CORS handling |
| django-redis | Latest | Redis caching |

### Database

| Technology | Version | Purpose |
|------------|---------|---------|
| MySQL | 8.0+ | Primary database |
| Redis | 6.0+ | Caching (optional) |

### AI Integration

| Service | Model | Purpose |
|---------|-------|---------|
| ZhipuAI | GLM-4-Flash | AI scoring, question generation, analysis |

### DevOps

| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Reverse proxy, static files |
| Prometheus | Metrics collection |
| GitHub Actions | CI/CD (optional) |

---

## Database Schema

### Core Models (28 Tables)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER MANAGEMENT                          │
├─────────────────────────────────────────────────────────────┤
│  Users          - User accounts (id, userName, password)    │
│  Students       - Student profiles (user, grade, college)   │
│  Teachers       - Teacher profiles (user, phone, job)       │
│  UserThemeSettings - Theme preferences per user             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ORGANIZATION                             │
├─────────────────────────────────────────────────────────────┤
│  Colleges       - College/Department info                   │
│  Grades         - Class/Grade info                          │
│  Projects       - Subjects/Courses                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    QUESTION BANK                            │
├─────────────────────────────────────────────────────────────┤
│  Practises      - Questions (name, type, answer, project)   │
│  Options        - Choice options for questions              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXAM SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│  Exams          - Exam definitions                          │
│  ExamLogs       - Student exam attempts                     │
│  AnswerLogs     - Individual answer records                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PRACTICE SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│  PracticePapers         - Practice paper definitions        │
│  PracticePaperQuestions - Questions in papers               │
│  StudentPracticeLogs    - Student practice attempts         │
│  StudentPracticeAnswers - Practice answer records           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    TASK SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│  Tasks           - Task definitions                         │
│  TaskQuestions   - Questions in tasks                       │
│  StudentTaskLogs - Student task attempts                    │
│  StudentTaskAnswers - Task answer records                   │
│  TaskAttachments - Task attachment files                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    WRONG QUESTIONS                          │
├─────────────────────────────────────────────────────────────┤
│  WrongQuestions       - Wrong question records              │
│  WrongQuestionReviews - Review history                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MESSAGING                                │
├─────────────────────────────────────────────────────────────┤
│  Messages     - System messages/announcements               │
│  MessageReads - Message read status                         │
└─────────────────────────────────────────────────────────────┘
```

### Entity Relationship Diagram

```
Users ─┬─< Students >── Grades
       │                │
       │                └── Colleges
       │
       ├─< Teachers
       │
       └─< UserThemeSettings

Projects ─< Practises ─< Options
    │          │
    │          └─< WrongQuestions
    │
    ├─< Exams ─< ExamLogs ─< AnswerLogs
    │
    ├─< PracticePapers ─< PracticePaperQuestions
    │         │
    │         └─< StudentPracticeLogs ─< StudentPracticeAnswers
    │
    └─< Tasks ─< TaskQuestions
              │
              ├─< StudentTaskLogs ─< StudentTaskAnswers
              │
              └─< TaskAttachments
```

---

## API Architecture

### URL Pattern

```
/api/{module}/{action}/
```

### Module Organization

```
app/views/
├── __init__.py           # View exports
├.py                      # Main views (legacy, large)
├── admin_views.py        # Admin functionality
├── backup_views.py       # Backup and export
├── attachment_views.py   # File attachments
├── theme_views.py        # Theme settings
├── log_views.py          # System logs
├── health_view.py        # Health checks
├── import_export_views.py# Import/export students
└── ai_views.py           # AI features
```

### Request Flow

```
1. Client Request
       │
       ▼
2. Nginx/Vue Proxy
       │
       ▼
3. Django URL Router (urls.py)
       │
       ▼
4. View Class/Function
       │
       ├── Permission Check
       ├── Validation
       ├── Business Logic
       └── Database Query
       │
       ▼
5. JSON Response
       │
       ▼
6. Client
```

---

## Frontend Architecture

### Directory Structure

```
source/client/
├── public/              # Static assets
├── src/
│   ├── api/             # API service layer
│   ├── assets/          # Images, styles
│   ├── components/      # Reusable components
│   │   ├── ThemeSwitcher.vue
│   │   └── ...
│   ├── router/          # Vue Router config
│   ├── store/           # Vuex modules
│   │   ├── index.js
│   │   └── modules/
│   │       └── theme.js
│   ├── views/           # Page components
│   │   ├── home.vue     # Main layout
│   │   ├── login.vue    # Login page
│   │   └── pages/       # Feature pages
│   │       ├── admin/   # Admin pages
│   │       ├── teacher/ # Teacher pages
│   │       ├── student/ # Student pages
│   │       ├── ClassComparison.vue
│   │       ├── StudentProgress.vue
│   │       └── DataDashboard.vue
│   ├── App.vue          # Root component
│   └── main.js          # Entry point
├── package.json
└── vue.config.js        # Vue CLI config
```

### State Management (Vuex)

```
store/
├── index.js           # Root store
├── modules/
│   ├── user.js        # User state
│   ├── exam.js        # Exam state
│   ├── practice.js    # Practice state
│   └── theme.js       # Theme preferences
```

### Route Structure

```
/                       → Login
/admin                  → Admin Dashboard
  /dashboard            → Dashboard
  /users                → User Management
  /statistics           → Statistics
  /compare-classes      → Class Comparison
  /student-progress     → Student Progress

/teacher                → Teacher Dashboard
  /questions            → Question Bank
  /exams                → Exam Management
  /practice-papers      → Practice Papers
  /tasks                → Task Center

/student                → Student Dashboard
  /exams                → Available Exams
  /practice             → Practice Center
  /wrong-questions      → Wrong Question Notebook
  /tasks                → Assigned Tasks
```

---

## AI Integration

### AIUtils Module

```python
comm/AIUtils.py

Functions:
├── ai_score_answer()      # Intelligent scoring
│   ├── Input: question, answer, type
│   └── Output: score, feedback, analysis, confidence
│
├── ai_generate_questions()# Question generation
│   ├── Input: subject, type, difficulty, count
│   └── Output: generated questions with answers
│
└── ai_analyze_wrong_answer()# Wrong answer analysis
    ├── Input: question, wrong_answer
    └── Output: error analysis, suggestions
```

### AI Configuration

```bash
# Environment Variables
ZHIPUAI_API_KEY=your_api_key
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### AI Features

| Feature | Description | Model |
|---------|-------------|-------|
| Intelligent Scoring | Score subjective answers | GLM-4-Flash |
| Question Generation | Auto-generate questions | GLM-4-Flash |
| Answer Analysis | Analyze wrong answers | GLM-4-Flash |

---

## Deployment Architecture

### Docker Deployment

```yaml
# docker-compose.yml
services:
  frontend:
    image: nginx:alpine
    ports: ["8080:8080"]
    volumes: [./dist:/usr/share/nginx/html]
    
  backend:
    build: ./source/server
    ports: ["8000:8000"]
    environment:
      - DB_HOST=mysql
      - DB_NAME=db_exam
      
  mysql:
    image: mysql:8.0
    ports: ["3307:3306"]
    environment:
      - MYSQL_ROOT_PASSWORD=123456
      - MYSQL_DATABASE=db_exam
```

### Container Overview

```
┌─────────────────────────────────────────────────────┐
│                 Docker Network                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ fyp_frontend│ │ fyp_backend │ │  fyp_mysql  │  │
│  │   :8080     │──│   :8000    │──│   :3306    │  │
│  │   Nginx     │  │   Django   │  │   MySQL    │  │
│  └─────────────┘ └─────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication Flow

```
1. User Login
       │
       ▼
2. Validate Credentials (Django Auth)
       │
       ▼
3. Create Session
       │
       ▼
4. Return Session Cookie
       │
       ▼
5. Subsequent Requests Include Cookie
       │
       ▼
6. Session Validation
       │
       ▼
7. Permission Check (Role-based)
       │
       ▼
8. Allow/Deny Access
```

### Role-Based Access Control

| Role | Type | Permissions |
|------|------|-------------|
| Admin | 0 | Full system access |
| Teacher | 1 | Question bank, exams, student data |
| Student | 2 | Take exams, practice, view own results |

### Security Measures

- Password hashing (Django's make_password)
- CORS configuration
- CSRF protection (configurable)
- Input validation
- SQL injection prevention (ORM)
- XSS prevention (Vue auto-escaping)

---

## Performance Optimizations

### Frontend

- Code splitting (vendor, elementUI, echarts)
- Route lazy loading
- Gzip compression
- Asset optimization
- CDN-ready

### Backend

- Database indexing on key fields
- Query optimization (select_related, prefetch_related)
- Redis caching (optional)
- Connection pooling
- Efficient pagination

### Database

- Indexes on foreign keys and frequently queried fields
- Optimized query patterns
- Regular maintenance scripts

---

## Monitoring & Logging

### Health Endpoints

```
GET /api/health/        # Full health check
GET /api/health/simple/ # Simple status
GET /api/metrics/       # Prometheus metrics
```

### Logging

- Django logging to files
- Error tracking
- Request logging (DEBUG mode)
- Operation logs in database

---

## Scalability Considerations

### Horizontal Scaling

```
                ┌─────────────┐
                │   Nginx     │
                │ Load Balancer│
                └──────┬──────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │Backend 1│   │Backend 2│   │Backend 3│
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
                ┌──────▼──────┐
                │    MySQL    │
                │  (Primary)  │
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │   Redis     │
                │  (Cluster)  │
                └─────────────┘
```

### Future Enhancements

- Message queue (Celery + Redis)
- Microservices architecture
- GraphQL API option
- Real-time features (WebSockets)
- Mobile app API

---

*Last Updated: 2026-02-21*
