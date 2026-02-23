# API Reference - 智能在线考试系统

## Overview

| Base URL | `http://localhost:8000/api/` |
|----------|------------------------------|
| Format   | JSON / Form-Data             |
| Auth     | Session-based (Django)       |

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [System & Health](#2-system--health)
3. [Admin APIs](#3-admin-apis)
4. [Statistics APIs](#4-statistics-apis)
5. [Backup & Export APIs](#5-backup--export-apis)
6. [Attachment APIs](#6-attachment-apis)
7. [Theme APIs](#7-theme-apis)
8. [User Management](#8-user-management)
9. [Question Bank](#9-question-bank)
10. [Exam System](#10-exam-system)
11. [Practice System](#11-practice-system)
12. [Task System](#12-task-system)
13. [Wrong Questions](#13-wrong-questions)
14. [AI Features](#14-ai-features)
15. [Error Codes](#15-error-codes)

---

## 1. Authentication

### Login
```
POST /api/sys/login/
```

**Request (form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| userName | string | Yes | Username |
| password | string | Yes | Password |

**Response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "userName": "admin",
    "name": "Administrator",
    "type": 0
  }
}
```

### Logout
```
POST /api/sys/logout/
```

### Get Current User
```
GET /api/sys/info/
```

---

## 2. System & Health

### Health Check (Full)
```
GET /api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "database": "ok",
  "cache": "ok",
  "timestamp": "2026-02-21T10:30:00Z"
}
```

### Health Check (Simple)
```
GET /api/health/simple/
```

**Response:**
```json
{
  "status": "ok"
}
```

### Prometheus Metrics
```
GET /api/metrics/
```

### System Logs
```
GET /api/logs/
```

---

## 3. Admin APIs

### Dashboard
```
GET /api/admin/dashboard/
```

**Response:**
```json
{
  "code": 200,
  "data": {
    "totalStudents": 100,
    "totalTeachers": 10,
    "totalExams": 25,
    "totalQuestions": 500,
    "recentExams": [...],
    "examStatus": {"pending": 5, "completed": 20},
    "subjectDistribution": [...]
  }
}
```

### Dashboard Cards
```
GET /api/admin/dashboard_cards/
```

**Response:**
```json
{
  "totalStudents": 100,
  "totalTeachers": 10,
  "totalSubjects": 8,
  "totalQuestions": 500,
  "totalExams": 25,
  "pendingReviews": 3,
  "todayActive": 45
}
```

### User List
```
GET /api/admin/users/
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| pageIndex | int | Page number (default: 1) |
| pageSize | int | Page size (default: 10) |
| type | string | User type: "1"=teacher, "2"=student |
| keyword | string | Search keyword |

### Exam Statistics
```
GET /api/admin/statistics_exam/?examId=1
```

**Response:**
```json
{
  "examName": "Midterm Exam",
  "totalParticipants": 50,
  "completedCount": 45,
  "avgScore": 78.5,
  "scoreDistribution": {
    "excellent": 10,
    "good": 15,
    "pass": 15,
    "fail": 5
  }
}
```

### Student Statistics
```
GET /api/admin/statistics_student/?studentId=1
```

### Class Statistics
```
GET /api/admin/statistics_class/?gradeId=1
```

### Subject Statistics
```
GET /api/admin/statistics_subject/?projectId=1
```

### Trends
```
GET /api/admin/trends/
```

---

## 4. Statistics APIs

### Compare Class Grades
```
GET /api/statistics/compare_classes/
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| gradeIds | string | Yes | Comma-separated grade IDs (e.g., "1,2,3") |
| examId | int | No | Specific exam ID for comparison |

**Response:**
```json
{
  "code": 200,
  "data": {
    "comparisonData": [
      {
        "gradeId": 1,
        "gradeName": "Class A",
        "studentCount": 30,
        "rank": 1,
        "examStats": {
          "avgScore": 85.5,
          "maxScore": 98,
          "minScore": 60,
          "passRate": 93.3,
          "excellentRate": 40.0
        },
        "practiceStats": {
          "avgScore": 82.0,
          "totalPractices": 150
        },
        "wrongQuestionStats": {
          "total": 45,
          "avgPerStudent": 1.5
        }
      }
    ],
    "totalGrades": 3
  }
}
```

### Student Progress
```
GET /api/statistics/student_progress/
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| studentId | int | Yes | Student ID |
| timeRange | string | No | week/month/semester/year (default: semester) |

**Response:**
```json
{
  "code": 200,
  "data": {
    "studentId": 1,
    "studentName": "Zhang San",
    "timeRange": "semester",
    "progressData": [...],
    "summary": {
      "totalRecords": 15,
      "avgScore": 78.5,
      "improvement": 12.0,
      "improvementRate": 18.5,
      "subjectAverages": {"Math": 80, "English": 75}
    }
  }
}
```

### Recommend Practice
```
GET /api/statistics/recommend_practice/
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| studentId | int | Yes | Student ID |
| count | int | No | Number of recommendations (default: 10) |

**Response:**
```json
{
  "code": 200,
  "data": {
    "studentId": 1,
    "recommendedPapers": [
      {
        "id": 1,
        "name": "Math Practice Set 1",
        "subject": "Math",
        "reason": "针对薄弱科目强化练习",
        "priority": 1,
        "questionCount": 20
      }
    ],
    "analysis": {
      "weakSubjects": ["Math", "Physics"],
      "weakTypes": {0: 15, 1: 8},
      "totalWrongQuestions": 23
    }
  }
}
```

### Recommend Wrong Questions
```
GET /api/statistics/recommend_wrong/
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| studentId | int | Yes | Student ID |
| count | int | No | Number of questions (default: 5) |

---

## 5. Backup & Export APIs

### Export System Data
```
GET /api/backup/export/
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| dataType | string | all/students/teachers/exams/questions/logs |
| format | string | json/csv (default: json) |

**Response:** File download (JSON or CSV)

### Generate Student Report
```
GET /api/report/student/
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| studentId | int | Yes | Student ID |
| timeRange | string | No | month/semester/year |

**Response:** HTML report page

### Export Teachers
```
GET /api/teachers/export/
```

**Response:** CSV file download

---

## 6. Attachment APIs

### Upload Attachment
```
POST /api/attachments/upload/
```

**Request (form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| taskId | int | Yes | Task ID |
| file | file | Yes | File to upload |
| userId | int | No | Uploader user ID |

**File Constraints:**
- Max size: 50MB
- Allowed types: pdf, doc, docx, xls, xlsx, ppt, pptx, txt, zip, rar, jpg, jpeg, png, gif, mp4, mp3

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "fileName": "document.pdf",
    "fileSize": 1024000,
    "fileType": ".pdf",
    "uploadTime": "2026-02-21T10:30:00Z"
  }
}
```

### List Attachments
```
GET /api/attachments/list/?taskId=1
```

### Download Attachment
```
GET /api/attachments/download/?attachmentId=1
```

**Response:** File download

### Delete Attachment
```
POST /api/attachments/delete/
```

**Request (form-data):**
| Field | Type | Required |
|-------|------|----------|
| attachmentId | int | Yes |

---

## 7. Theme APIs

### Get Theme Settings
```
GET /api/theme/get/?userId=1
```

**Response:**
```json
{
  "code": 200,
  "data": {
    "theme": "light",
    "primaryColor": "#2d8cf0",
    "fontSize": "medium",
    "sidebarCollapsed": false,
    "showAnimations": true,
    "compactMode": false
  }
}
```

### Save Theme Settings
```
POST /api/theme/save/
```

**Request (form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| userId | int | Yes | User ID |
| theme | string | No | light/dark |
| primaryColor | string | No | Hex color (e.g., #2d8cf0) |
| fontSize | string | No | small/medium/large |
| sidebarCollapsed | boolean | No | Sidebar collapsed state |
| showAnimations | boolean | No | Enable animations |
| compactMode | boolean | No | Enable compact mode |

### Reset Theme Settings
```
POST /api/theme/reset/
```

**Request (form-data):**
| Field | Type | Required |
|-------|------|----------|
| userId | int | Yes |

---

## 8. User Management

### Students CRUD
```
GET    /api/students/list/          # List students
POST   /api/students/save/          # Create/Update student
POST   /api/students/delete/        # Delete student
GET    /api/students/detail/        # Get student details
```

### Import Students
```
POST /api/students/import/
```

**Request:** Excel file upload

### Export Template
```
GET /api/students/export/template/
```

### Teachers CRUD
```
GET    /api/teachers/list/
POST   /api/teachers/save/
POST   /api/teachers/delete/
GET    /api/teachers/detail/
```

---

## 9. Question Bank

### Questions CRUD
```
GET    /api/practises/list/
POST   /api/practises/save/
POST   /api/practises/delete/
GET    /api/practises/detail/
```

**Question Types:**
| Value | Type |
|-------|------|
| 0 | Choice |
| 1 | Fill-in-blank |
| 2 | True/False |
| 3 | Short Answer |
| 4 | Programming |
| 5 | Comprehensive |

### Options CRUD
```
GET    /api/options/list/
POST   /api/options/save/
POST   /api/options/delete/
```

### Projects (Subjects) CRUD
```
GET    /api/projects/list/
POST   /api/projects/save/
POST   /api/projects/delete/
```

---

## 10. Exam System

### Exams CRUD
```
GET    /api/exams/list/
POST   /api/exams/save/
POST   /api/exams/delete/
GET    /api/exams/detail/
```

### Exam Logs
```
GET    /api/examlogs/list/
POST   /api/examlogs/save/
```

### Answer Logs
```
GET    /api/answerlogs/list/
POST   /api/answerlogs/save/
```

---

## 11. Practice System

### Practice Papers
```
GET    /api/practicepapers/list/
POST   /api/practicepapers/save/
POST   /api/practicepapers/delete/
GET    /api/practicepapers/detail/
```

### Student Practice
```
GET    /api/studentpractice/list/
POST   /api/studentpractice/start/     # Start practice
POST   /api/studentpractice/submit/    # Submit answers
GET    /api/studentpractice/result/    # Get results
```

---

## 12. Task System

### Tasks CRUD
```
GET    /api/tasks/list/
POST   /api/tasks/save/
POST   /api/tasks/delete/
GET    /api/tasks/detail/
```

---

## 13. Wrong Questions

### Wrong Questions Management
```
GET    /api/wrongquestions/list/
POST   /api/wrongquestions/add/
POST   /api/wrongquestions/delete/
POST   /api/wrongquestions/review/     # Mark as reviewed
```

---

## 14. AI Features

### AI Score Answer
```
POST /api/ai/score/
```

**Request (form-data):**
| Field | Type | Description |
|-------|------|-------------|
| questionId | int | Question ID |
| answer | string | Student's answer |
| questionType | int | Question type |

**Response:**
```json
{
  "code": 200,
  "data": {
    "score": 8,
    "feedback": "Correct approach with minor error",
    "analysis": "...",
    "confidence": 0.85
  }
}
```

### AI Generate Questions
```
POST /api/ai/generate/
```

**Request (form-data):**
| Field | Type | Description |
|-------|------|-------------|
| projectId | int | Subject/Project ID |
| type | int | Question type |
| count | int | Number to generate |
| difficulty | int | Difficulty level (1-5) |

---

## 15. Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 200 | success | Request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | User not logged in |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

### Response Format

**Success:**
```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

**Error:**
```json
{
  "code": 400,
  "msg": "Error message",
  "data": null
}
```

---

## API Summary

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Auth | 3 | Login, Logout, User Info |
| System | 4 | Health, Metrics, Logs |
| Admin | 15 | Dashboard, Statistics, User Management |
| Statistics | 4 | Class Comparison, Progress, Recommendations |
| Backup | 3 | Export, Reports |
| Attachments | 4 | Upload, List, Download, Delete |
| Theme | 3 | Get, Save, Reset |
| Students | 5 | CRUD + Import |
| Teachers | 4 | CRUD |
| Questions | 4 | CRUD |
| Exams | 4 | CRUD |
| Practice | 6 | Papers + Student Practice |
| Tasks | 4 | CRUD |
| Wrong Questions | 4 | CRUD + Review |
| AI | 2 | Score, Generate |
| **Total** | **65+** | |

---

## Request Examples

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/sys/login/ \
  -F "userName=admin" \
  -F "password=123456"

# Get Dashboard
curl http://localhost:8000/api/admin/dashboard/

# Upload Attachment
curl -X POST http://localhost:8000/api/attachments/upload/ \
  -F "taskId=1" \
  -F "file=@document.pdf"
```

### JavaScript (Axios)

```javascript
// Login
await axios.post('/api/sys/login/', {
  userName: 'admin',
  password: '123456'
});

// Get Statistics
const response = await axios.get('/api/statistics/compare_classes/', {
  params: { gradeIds: '1,2,3' }
});
```

---

## Default Test Accounts

| Role | Username | Password | Type |
|------|----------|----------|------|
| Admin | admin | 123456 | 0 |
| Teacher | teacher | 123456 | 1 |
| Student | student | 123456 | 2 |

---

*Last Updated: 2026-02-21*
