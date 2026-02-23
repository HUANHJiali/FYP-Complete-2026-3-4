import { createRouter, createWebHashHistory } from 'vue-router'

// 路由懒加载 - 代码分割优化
const Login = () => import(/* webpackChunkName: "login" */ '../views/login.vue')
const Home = () => import(/* webpackChunkName: "home" */ '../views/home.vue')
const Welcome = () => import(/* webpackChunkName: "welcome" */ '../views/pages/welcome.vue')
const StudentRegister = () => import(/* webpackChunkName: "student-register" */ '../views/pages/studentRegister.vue')
const TaskCenter = () => import(/* webpackChunkName: "task-center" */ '../views/pages/taskCenter.vue')
const Exams = () => import(/* webpackChunkName: "exams" */ '../views/pages/exams.vue')
const Practises = () => import(/* webpackChunkName: "practises" */ '../views/pages/practises.vue')
const StudentExamLogs = () => import(/* webpackChunkName: "student-exam-logs" */ '../views/pages/studentExamLogs.vue')
const WrongQuestions = () => import(/* webpackChunkName: "wrong-questions" */ '../views/pages/wrongQuestions.vue')
const StudentProfile = () => import(/* webpackChunkName: "student-profile" */ '../views/pages/studentProfile.vue')
const PersonalDynamics = () => import(/* webpackChunkName: "personal-dynamics" */ '../views/pages/personalDynamics.vue')
const MessageCenter = () => import(/* webpackChunkName: "message-center" */ '../views/pages/messageCenter.vue')
const Answer = () => import(/* webpackChunkName: "answer" */ '../views/pages/answer.vue')
const PracticeResult = () => import(/* webpackChunkName: "practice-result" */ '../views/pages/practiceResult.vue')
const TaskResult = () => import(/* webpackChunkName: "task-result" */ '../views/pages/taskResult.vue')
const AIScoring = () => import(/* webpackChunkName: "ai-scoring" */ '../views/pages/aiScoring.vue')
const AIQuestionGenerator = () => import(/* webpackChunkName: "ai-question-generator" */ '../views/pages/aiQuestionGenerator.vue')
const AdminLogs = () => import(/* webpackChunkName: "admin-logs" */ '../views/pages/adminLogs.vue')
const AdminDashboard = () => import(/* webpackChunkName: "admin-dashboard" */ '../views/pages/adminDashboard.vue')
const AdminUsers = () => import(/* webpackChunkName: "admin-users" */ '../views/pages/adminUsers.vue')
const AdminQuestions = () => import(/* webpackChunkName: "admin-questions" */ '../views/pages/adminQuestions.vue')
const AdminExams = () => import(/* webpackChunkName: "admin-exams" */ '../views/pages/adminExams.vue')
const AdminPracticePapers = () => import(/* webpackChunkName: "admin-practice-papers" */ '../views/pages/adminPracticePapers.vue')
const AdminTasks = () => import(/* webpackChunkName: "admin-tasks" */ '../views/pages/adminTasks.vue')
const AdminMessages = () => import(/* webpackChunkName: "admin-messages" */ '../views/pages/adminMessages.vue')
const AdminSubjects = () => import(/* webpackChunkName: "admin-subjects" */ '../views/pages/adminSubjects.vue')
const DataVisualization = () => import(/* webpackChunkName: "data-visualization" */ '../views/pages/dataVisualization.vue')
const Colleges = () => import(/* webpackChunkName: "colleges" */ '../views/pages/colleges.vue')
const Grades = () => import(/* webpackChunkName: "grades" */ '../views/pages/grades.vue')
const Teachers = () => import(/* webpackChunkName: "teachers" */ '../views/pages/teachers.vue')
const Projects = () => import(/* webpackChunkName: "projects" */ '../views/pages/projects.vue')
const Students = () => import(/* webpackChunkName: "students" */ '../views/pages/students.vue')
const TeacherExamLogs = () => import(/* webpackChunkName: "teacher-exam-logs" */ '../views/pages/teacherExamLogs.vue')
const ExamMonitor = () => import(/* webpackChunkName: "exam-monitor" */ '../views/pages/examMonitor.vue')

const routes = [
  {
    path: '/',
    name: 'login',
    component: Login
  },
  {
    path: '/home',
    name: 'home',
    component: Home,
    children: [
      {
        path: '',
        name: 'welcome',
        component: Welcome
      },
      {
        path: 'studentRegister',
        name: 'studentRegister',
        component: StudentRegister
      },
      {
        path: 'taskCenter',
        name: 'taskCenter',
        component: TaskCenter
      },
      {
        path: 'exams',
        name: 'exams',
        component: Exams
      },
      {
        path: 'practises',
        name: 'practises',
        component: Practises
      },
      {
        path: 'studentExamLogs',
        name: 'studentExamLogs',
        component: StudentExamLogs
      },
      {
        path: 'wrongQuestions',
        name: 'wrongQuestions',
        component: WrongQuestions
      },
      {
        path: 'studentProfile',
        name: 'studentProfile',
        component: StudentProfile
      },
      {
        path: 'personalDynamics',
        name: 'personalDynamics',
        component: PersonalDynamics
      },
      {
        path: 'messageCenter',
        name: 'messageCenter',
        component: MessageCenter
      },
      {
        path: '/home/answer',
        name: 'answer',
        component: Answer
      },
      {
        path: 'practiceResult',
        name: 'practiceResult',
        component: PracticeResult
      },
      {
        path: 'taskResult',
        name: 'taskResult',
        component: TaskResult
      },
      {
        path: 'aiScoring',
        name: 'aiScoring',
        component: AIScoring
      },
      {
        path: 'aiQuestionGenerator',
        name: 'aiQuestionGenerator',
        component: AIQuestionGenerator
      },
      {
        path: 'adminLogs',
        name: 'adminLogs',
        component: AdminLogs
      },
      // 管理员功能路由
      {
        path: 'adminDashboard',
        name: 'adminDashboard',
        component: AdminDashboard
      },
      {
        path: 'adminUsers',
        name: 'adminUsers',
        component: AdminUsers
      },
      {
        path: 'adminQuestions',
        name: 'adminQuestions',
        component: AdminQuestions
      },
      {
        path: 'adminExams',
        name: 'adminExams',
        component: AdminExams
      },
      {
        path: 'adminPracticePapers',
        name: 'adminPracticePapers',
        component: AdminPracticePapers
      },
      {
        path: 'adminTasks',
        name: 'adminTasks',
        component: AdminTasks
      },
      {
        path: 'adminMessages',
        name: 'adminMessages',
        component: AdminMessages
      },
      {
        path: 'adminSubjects',
        name: 'adminSubjects',
        component: AdminSubjects
      },
      {
        path: 'dataVisualization',
        name: 'dataVisualization',
        component: DataVisualization
      },
      // 基础数据管理
      {
        path: 'colleges',
        name: 'colleges',
        component: Colleges
      },
      {
        path: 'grades',
        name: 'grades',
        component: Grades
      },
      {
        path: 'teachers',
        name: 'teachers',
        component: Teachers
      },
      {
        path: 'projects',
        name: 'projects',
        component: Projects
      },
      {
        path: 'students',
        name: 'students',
        component: Students
      },
      // 教师功能
      {
        path: 'teacherExamLogs',
        name: 'teacherExamLogs',
        component: TeacherExamLogs
      },
      {
        path: 'examMonitor',
        name: 'examMonitor',
        component: ExamMonitor
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 预加载关键路由（可选 - 提升用户体验）
// router.beforeEach((to, from, next) => {
//   if (to.name) {
//     const component = to.matched[0].components.default
//     // 预加载即将访问的页面
//   }
//   next()
// })

export default router
