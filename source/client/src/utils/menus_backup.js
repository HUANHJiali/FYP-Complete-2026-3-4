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
            path: '/create-subject',
            name: '学科创编',
            translationKey: 'menu.createSubject',
            icon: "ios-add-circle",
            component: require("../views/pages/createSubject.vue").default
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
            path: '/exams',
            name: '校园考试管理',
            translationKey: 'menu.exams',
            icon: "md-speedometer",
            component: require("../views/pages/exams.vue").default
        },
        {
            path: '/create-exam-admin',
            name: '试卷创编',
            translationKey: 'menu.createExamAdmin',
            icon: "ios-create",
            component: require("../views/pages/createExamAdmin.vue").default
        },
        {
            path: '/questions-admin',
            name: '题目管理',
            translationKey: 'menu.questionsAdmin',
            icon: "ios-help-circle",
            component: require("../views/pages/questionsAdmin.vue").default
        },
        {
            path: '/create-question-admin',
            name: '题目创建',
            translationKey: 'menu.createQuestionAdmin',
            icon: "ios-add-circle",
            component: require("../views/pages/createQuestionAdmin.vue").default
        },
        {
            path: '/tasks-admin',
            name: '任务管理',
            translationKey: 'menu.tasksAdmin',
            icon: "ios-list",
            component: require("../views/pages/tasksAdmin.vue").default
        },
        {
            path: '/messages-admin',
            name: '消息管理',
            translationKey: 'menu.messagesAdmin',
            icon: "ios-mail",
            component: require("../views/pages/messagesAdmin.vue").default
        },
        {
            path: '/send-message-admin',
            name: '消息发送',
            translationKey: 'menu.sendMessageAdmin',
            icon: "ios-send",
            component: require("../views/pages/sendMessageAdmin.vue").default
        },
        {
            path: '/user-logs-admin',
            name: '用户日志',
            translationKey: 'menu.userLogsAdmin',
            icon: "ios-analytics",
            component: require("../views/pages/userLogsAdmin.vue").default
        },
        {
            path: '/admin-profile',
            name: '个人资料',
            translationKey: 'menu.adminProfile',
            icon: "ios-person",
            component: require("../views/pages/adminProfile.vue").default
        },
        {
            path: '/update-admin-info',
            name: '修改资料',
            translationKey: 'menu.updateAdminInfo',
            icon: "ios-settings",
            component: require("../views/pages/updateAdminInfo.vue").default
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
            path: '/practises',
            name: '习题管理',
            translationKey: 'menu.practises',
            icon: "md-bookmarks",
            component: require("../views/pages/practises.vue").default
        },
        {
            path: '/questions',
            name: '题目管理',
            translationKey: 'menu.questions',
            icon: "ios-help-circle",
            component: require("../views/pages/questions.vue").default
        },
        {
            path: '/create-question',
            name: '题目创建',
            translationKey: 'menu.createQuestion',
            icon: "ios-add-circle",
            component: require("../views/pages/createQuestion.vue").default
        },
        {
            path: '/exams',
            name: '考试安排',
            translationKey: 'menu.exams',
            icon: "ios-glasses-outline",
            component: require("../views/pages/exams.vue").default
        },
        {
            path: '/create-exam',
            name: '试卷创编',
            translationKey: 'menu.createExam',
            icon: "ios-create",
            component: require("../views/pages/createExam.vue").default
        },
        {
            path: '/tasks',
            name: '任务管理',
            translationKey: 'menu.tasks',
            icon: "ios-list",
            component: require("../views/pages/tasks.vue").default
        },
        {
            path: '/examlogs/teacher',
            name: '试卷审核',
            translationKey: 'menu.examlogs',
            icon: "ios-brush",
            component: require("../views/pages/teacherExamLogs.vue").default
        },
        {
            path: '/messages',
            name: '消息管理',
            translationKey: 'menu.messages',
            icon: "ios-mail",
            component: require("../views/pages/messages.vue").default
        },
        {
            path: '/send-message',
            name: '消息发送',
            translationKey: 'menu.sendMessage',
            icon: "ios-send",
            component: require("../views/pages/sendMessage.vue").default
        },
        {
            path: '/user-logs',
            name: '用户日志',
            translationKey: 'menu.userLogs',
            icon: "ios-analytics",
            component: require("../views/pages/userLogs.vue").default
        },
        {
            path: '/teacher-profile',
            name: '个人资料',
            translationKey: 'menu.teacherProfile',
            icon: "ios-person",
            component: require("../views/pages/teacherProfile.vue").default
        },
        {
            path: '/update-teacher-info',
            name: '修改资料',
            translationKey: 'menu.updateTeacherInfo',
            icon: "ios-settings",
            component: require("../views/pages/updateTeacherInfo.vue").default
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
            path: '/task-center',
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
            path: '/fixed-papers',
            name: '固定试卷',
            translationKey: 'menu.fixedPapers',
            icon: "ios-document",
            component: require("../views/pages/fixedPapers.vue").default
        },
        {
            path: '/timed-papers',
            name: '时段试卷',
            translationKey: 'menu.timedPapers',
            icon: "ios-timer",
            component: require("../views/pages/timedPapers.vue").default
        },
        {
            path: '/examlogs/student',
            name: '考试记录',
            translationKey: 'menu.studentExamLogs',
            icon: "ios-archive",
            component: require("../views/pages/studentExamLogs.vue").default
        },
        {
            path: '/wrong-questions',
            name: '错题本',
            translationKey: 'menu.wrongQuestions',
            icon: "ios-close-circle",
            component: require("../views/pages/wrongQuestions.vue").default
        },
        {
            path: '/profile',
            name: '个人信息',
            translationKey: 'menu.profile',
            icon: "ios-person",
            component: require("../views/pages/profile.vue").default
        },
        {
            path: '/update-info',
            name: '更新信息',
            translationKey: 'menu.updateInfo',
            icon: "ios-settings",
            component: require("../views/pages/updateInfo.vue").default
        },
        {
            path: '/personal-activities',
            name: '个人动态',
            translationKey: 'menu.personalActivities',
            icon: "ios-pulse",
            component: require("../views/pages/personalActivities.vue").default
        },
        {
            path: '/message-center',
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

        router.push('/welcome');
	});
}