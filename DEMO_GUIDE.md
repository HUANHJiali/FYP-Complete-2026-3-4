# Demo Guide - 智能在线考试系统

## Demo Preparation Checklist

### System Requirements
- [ ] Docker containers running (fyp_frontend, fyp_backend, fyp_mysql)
- [ ] All APIs accessible (http://localhost:8000/api/health/)
- [ ] Frontend accessible (http://localhost:8080)
- [ ] Test data loaded

### Test Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | admin | 123456 | Full system access |
| Teacher | teacher | 123456 | Question bank, exams, tasks |
| Student | student | 123456 | Take exams, practice |

### Demo Data Summary

| Data Type | Count |
|-----------|-------|
| Users | 10 |
| Students | 5 |
| Teachers | 3 |
| Questions | 50 |
| Exams | 1 |
| Practice Papers | 4 |
| Wrong Questions | 9 |
| Exam Logs | 5 |
| Practice Logs | 9 |

---

## Demo Flow (15-20 minutes)

### Part 1: Admin Dashboard (3 minutes)

#### Step 1: Login as Admin
1. Open http://localhost:8080
2. Login with admin/123456
3. Show dashboard with statistics

**Key Points to Highlight:**
- System overview (students, teachers, exams, questions)
- Real-time statistics
- Recent activity

#### Step 2: User Management
1. Navigate to User Management
2. Show student list
3. Show teacher list
4. Demonstrate search/filter

#### Step 3: Statistics Dashboard
1. Show class comparison (if available)
2. Show system trends
3. Show subject distribution

---

### Part 2: Teacher Features (5 minutes)

#### Step 4: Login as Teacher
1. Logout from admin
2. Login with teacher/123456
3. Show teacher dashboard

#### Step 5: Question Bank
1. Navigate to Question Bank
2. Show existing questions
3. Filter by subject/type
4. Demonstrate question preview

**Demo Adding a Question:**
1. Click "Add Question"
2. Select question type (Choice/Fill-in/True-False)
3. Enter question content
4. Add options (for choice questions)
5. Set correct answer
6. Save question

#### Step 6: Exam Management
1. Navigate to Exams
2. Show existing exams
3. Demonstrate exam details

**Demo Creating an Exam:**
1. Click "Create Exam"
2. Enter exam name: "期中测试"
3. Select subject
4. Set duration: 60 minutes
5. Add questions from bank
6. Set exam schedule
7. Publish exam

#### Step 7: Practice Papers
1. Navigate to Practice Papers
2. Show existing practice papers
3. Show question distribution

#### Step 8: Task Assignment
1. Navigate to Tasks
2. Show task list
3. Demonstrate task creation (if applicable)

---

### Part 3: Student Features (5 minutes)

#### Step 9: Login as Student
1. Logout from teacher
2. Login with student/123456
3. Show student dashboard

#### Step 10: View Available Exams
1. Navigate to Exams
2. Show available exams
3. Show exam details

#### Step 11: Take an Exam (Demo)
1. Click on an exam
2. Show exam instructions
3. Start exam
4. Answer questions:
   - Choice questions: Select option
   - Fill-in: Enter answer
   - True/False: Select answer
5. Navigate between questions
6. Submit exam
7. View results

#### Step 12: Practice Center
1. Navigate to Practice Center
2. Show available practice papers
3. Start a practice
4. Answer questions
5. View results with explanations

#### Step 13: Wrong Question Notebook
1. Navigate to Wrong Questions
2. Show wrong question history
3. Demonstrate review functionality
4. Show question analysis

---

### Part 4: AI Features (3 minutes)

#### Step 14: AI Intelligent Scoring
1. Navigate to a completed exam/practice
2. Show AI-scoring results
3. Highlight:
   - Score accuracy
   - Detailed feedback
   - Suggestions for improvement

#### Step 15: AI Question Generation (If Available)
1. Navigate to Question Bank
2. Click "AI Generate Questions"
3. Select subject
4. Select question type
5. Generate questions
6. Review and edit generated questions

---

### Part 5: Reports & Analytics (2 minutes)

#### Step 16: Student Progress Report
1. Login as teacher
2. Navigate to Student Progress
3. Select a student
4. Show progress chart
5. Highlight:
   - Score trends
   - Subject performance
   - Improvement areas

#### Step 17: Class Comparison
1. Navigate to Class Comparison
2. Select classes to compare
3. Show comparison charts
4. Highlight:
   - Average scores
   - Pass rates
   - Top performers

---

## Demo Script (Chinese)

### 开场白
"各位老师好，今天我将演示智能在线考试系统。该系统集成了AI智能评分、学习数据分析、个性化推荐等功能，支持管理员、教师、学生三种角色。"

### Part 1: 管理员视角
"首先以管理员身份登录。可以看到系统仪表盘，展示了学生总数、教师总数、考试数量等核心数据。管理员可以管理用户、查看系统统计数据。"

### Part 2: 教师视角
"现在切换到教师视角。教师可以管理题库、创建考试、发布练习。让我演示如何创建一道选择题..."

"考试创建完成后，学生即可参加考试。系统支持自动评分和AI智能评分。"

### Part 3: 学生视角
"以学生身份登录，可以看到待参加的考试和推荐的练习。让我演示考试流程..."

"系统会记录学生的错题，并智能推荐相关练习。"

### Part 4: AI功能
"系统的核心亮点是AI智能评分功能。对于主观题，AI会给出分数和详细反馈..."

### Part 5: 数据分析
"最后，系统提供丰富的数据分析功能，帮助教师了解学生学习情况，进行针对性教学..."

### 结束语
"演示结束，欢迎提问。系统已部署在Docker容器中，可以随时访问测试。"

---

## Backup Demo Plan

### If Live Demo Fails:

1. **Use Screenshots**
   - Prepare key interface screenshots
   - Show in presentation mode

2. **Use Pre-recorded Video**
   - Record demo beforehand
   - Have video ready as backup

3. **Use Static Data**
   - If system is slow, use cached data
   - Skip real-time features

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials: admin/123456 |
| Page not loading | Check Docker containers: docker ps |
| API errors | Check backend logs: docker logs fyp_backend |
| Slow response | Clear cache, restart containers |
| Data missing | Run data population script |

---

## Quick Commands

```bash
# Check system status
docker ps

# Restart all containers
docker-compose restart

# View backend logs
docker logs fyp_backend --tail 50

# Health check
curl http://localhost:8000/api/health/

# Restart backend only
docker restart fyp_backend
```

---

## Demo Data Reset

If needed, reset to initial state:

```bash
# Enter backend container
docker exec -it fyp_backend bash

# Reset database
python manage.py flush

# Run migrations
python manage.py migrate

# Load fixtures (if available)
python manage.py loaddata demo_data.json
```

---

*Document prepared for FYP Demo - 2026*
