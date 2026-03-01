import {getLoginUser} from "../api";

export const adminMenus = {
    path: '/home',
    name: 'home',
    component: require("../views/home.vue").default,
    children: [
        {
            path: '/welcome',
            name: '系统首页',
            translationKey: 'menu.home',
            icon: "ios-home",
            component: require("../views/pages/welcome.vue").default
        },
        {
            path: '/colleges',
            name: '学院信息管理',
            translationKey: 'menu.colleges',
            icon: "ios-ribbon",
            component: require("../views/pages/colleges.vue").default
        },
        {
            path: '/grades',
            name: '班级信息管理',
            translationKey: 'menu.grades',
            icon: "ios-appstore",
            component: require("../views/pages/grades.vue").default
        },
        {
            path: '/projects',
            name: '考试科目管理',
            translationKey: 'menu.projects',
            icon: "ios-list-box",
            component: require("../views/pages/projects.vue").default
        },
        {
            path: '/students',
            name: '学生信息管理',
            translationKey: 'menu.students',
            icon: "ios-people",
            component: require("../views/pages/students.vue").default
        },
        {
            path: '/teachers',
            name: '教师信息管理',
            translationKey: 'menu.teachers',
            icon: "md-ribbon",
            component: require("../views/pages/teachers.vue").default
        },
        {
            path: '/adminQuestions',
            name: '习题管理',
            translationKey: 'menu.practises',
            icon: 'md-bookmarks',
            component: require('../views/pages/adminQuestions.vue').default
        },
        {
            path: '/exams',
            name: '校园考试管理',
            translationKey: 'menu.exams',
            icon: "md-speedometer",
            component: require("../views/pages/adminExams.vue").default
        },
        {
            path: '/aiScoring',
            name: 'AI评分',
            translationKey: 'menu.aiScoring',
            icon: 'ios-analytics',
            component: require('../views/pages/aiScoring.vue').default
        },
        {
            path: '/aiQuestionGenerator',
            name: 'AI生成题目',
            translationKey: 'menu.aiQuestionGenerator',
            icon: 'md-create',
            component: require('../views/pages/aiQuestionGenerator.vue').default
        },
        {
            path: '/adminPracticePapers',
            name: '练习试卷管理',
            translationKey: 'menu.practicePapersAdmin',
            icon: 'ios-paper',
            component: require('../views/pages/adminPracticePapers.vue').default
        },
        {
            path: '/adminTasks',
            name: '任务管理',
            translationKey: 'menu.adminTasks',
            icon: 'ios-checkmark-circle',
            component: require('../views/pages/adminTasks.vue').default
        },
        {
            path: '/practiceLogs',
            name: '学生练习记录',
            translationKey: 'menu.practiceLogs',
            icon: 'ios-book',
            component: require('../views/pages/studentExamLogs.vue').default
        },
        {
            path: '/adminMessages',
            name: '消息管理',
            translationKey: 'menu.adminMessages',
            icon: 'ios-mail',
            component: require('../views/pages/adminMessages.vue').default
        },
        {
            path: '/adminLogs',
            name: '操作日志',
            translationKey: 'menu.adminLogs',
            icon: 'ios-document',
            component: require('../views/pages/adminLogs.vue').default
        },
        {
            path: '/dataDashboard',
            name: '数据大屏',
            translationKey: 'menu.dataDashboard',
            icon: 'ios-podium',
            component: require('../views/pages/DataDashboard.vue').default
        },
        {
            path: '/classComparison',
            name: '班级对比分析',
            translationKey: 'menu.classComparison',
            icon: 'ios-git-compare',
            component: require('../views/pages/ClassComparison.vue').default
        },
        {
            path: '/studentProgress',
            name: '学生进步分析',
            translationKey: 'menu.studentProgress',
            icon: 'ios-trending-up',
            component: require('../views/pages/StudentProgress.vue').default
        }

    ]
}

export const teacherMenus = {
    path: '/home',
    name: 'home',
    component: require("../views/home.vue").default,
    children: [
        {
            path: '/welcome',
            name: '系统首页',
            translationKey: 'menu.home',
            icon: "ios-home",
            component: require("../views/pages/welcome.vue").default
        },
        {
            path: '/adminQuestions',
            name: '习题管理',
            translationKey: 'menu.practises',
            icon: "md-bookmarks",
            component: require("../views/pages/adminQuestions.vue").default
        },
        {
            path: '/exams',
            name: '考试安排',
            translationKey: 'menu.exams',
            icon: "ios-glasses-outline",
            component: require("../views/pages/exams.vue").default
        },
        {
            path: '/aiQuestionGenerator',
            name: 'AI生成题目',
            translationKey: 'menu.aiQuestionGenerator',
            icon: 'md-create',
            component: require('../views/pages/aiQuestionGenerator.vue').default
        },
        {
            path: '/adminPracticePapers',
            name: '练习试卷管理',
            translationKey: 'menu.practicePapersAdmin',
            icon: 'ios-paper',
            component: require('../views/pages/adminPracticePapers.vue').default
        },
        {
            path: '/examlogs/teacher',
            name: '试卷审核',
            translationKey: 'menu.examlogs',
            icon: "ios-brush",
            component: require("../views/pages/teacherExamLogs.vue").default
        },
        {
            path: '/examMonitor',
            name: '考试监控',
            translationKey: 'menu.examMonitor',
            icon: "ios-eye",
            component: require("../views/pages/examMonitor.vue").default
        },
        {
            path: '/practiceLogs',
            name: '学生练习记录',
            translationKey: 'menu.practiceLogs',
            icon: 'ios-book',
            component: require('../views/pages/studentExamLogs.vue').default
        }
    ]
}

export const studentMenus = {
    path: '/home',
    name: 'home',
    component: require("../views/home.vue").default,
    children: [
        {
            path: '/welcome',
            name: '系统首页',
            translationKey: 'menu.home',
            icon: "ios-home",
            component: require("../views/pages/welcome.vue").default
        },
        {
            path: '/taskCenter',
            name: '任务中心',
            translationKey: 'menu.taskCenter',
            icon: "ios-list-box",
            component: require("../views/pages/taskCenter.vue").default
        },
        {
            path: '/exams',
            name: '考试安排',
            translationKey: 'menu.exams',
            icon: "ios-clock",
            component: require("../views/pages/exams.vue").default
        },
        {
            path: '/practises',
            name: '练习试卷',
            translationKey: 'menu.practises',
            icon: "ios-book",
            component: require("../views/pages/practises.vue").default
        },
        {
            path: '/aiScoring',
            name: 'AI评分',
            translationKey: 'menu.aiScoring',
            icon: 'ios-analytics',
            component: require('../views/pages/aiScoring.vue').default
        },
        {
            path: '/examlogs/student',
            name: '考试记录',
            translationKey: 'menu.studentExamLogs',
            icon: "ios-archive",
            component: require("../views/pages/studentExamLogs.vue").default
        },
        {
            path: '/wrongQuestions',
            name: '错题本',
            translationKey: 'menu.wrongQuestions',
            icon: "ios-alert",
            component: require("../views/pages/wrongQuestions.vue").default
        },
        {
            path: '/dataVisualization',
            name: '数据可视化',
            translationKey: 'menu.dataVisualization',
            icon: "ios-analytics",
            component: require("../views/pages/dataVisualization.vue").default
        },
        {
            path: '/studentProgress',
            name: '学习分析',
            translationKey: 'menu.studentProgress',
            icon: 'ios-trending-up',
            component: require('../views/pages/StudentProgress.vue').default
        },
        {
            path: '/studentProfile',
            name: '个人信息',
            translationKey: 'menu.studentProfile',
            icon: "ios-person",
            component: require("../views/pages/studentProfile.vue").default
        },
        {
            path: '/personalDynamics',
            name: '个人动态',
            translationKey: 'menu.personalDynamics',
            icon: "ios-pulse",
            component: require("../views/pages/personalDynamics.vue").default
        },
        {
            path: '/messageCenter',
            name: '消息中心',
            translationKey: 'menu.messageCenter',
            icon: "ios-mail",
            component: require("../views/pages/messageCenter.vue").default
        }
    ]
}

export default function initMenu(router, store){

    let token = null;
	if(store.state.token){

		token = store.state.token;
	}else{

		token = sessionStorage.getItem("token");
		store.state.token = sessionStorage.getItem("token");
	}

	getLoginUser(token).then(resp =>{

		if(resp.data.type == 0){
			router.addRoute(adminMenus);
			store.commit("setMenus", adminMenus);
		}
	
		if(resp.data.type == 1){
			router.addRoute(teacherMenus);
			store.commit("setMenus", teacherMenus);
		}
		
		if(resp.data.type == 2){
			router.addRoute(studentMenus);
			store.commit("setMenus", studentMenus);
		}

        // 确保答题页路由始终存在（作为 home 的子路由）
        try{
            router.addRoute('home', {
                path: 'answer',
                name: 'answer',
                component: require("../views/pages/answer.vue").default
            });
        }catch(e){}

        router.push('/welcome').catch(() => {});
	}).catch(err => {
        console.error('获取用户信息失败，请重新登录', err);
    });
}