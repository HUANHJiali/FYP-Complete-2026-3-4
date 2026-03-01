import http from "../utils/http.js";


/** 系统接口 */
export function login(param){
	
	return http.post('/login/', param);
}
export function exit(token){
	
	return http.post('/exit/', {token: token});
}
export function getLoginUser(token){
	
	return http.get('/info/', {params: {token: token}});
}
export function updSessionInfo(param){
	
	return http.post('/info/', param);
}
export function updSessionPwd(param){
	
	return http.post('/pwd/', param);
}

/** 学院信息处理接口 */
export function getAllColleges(){

	return http.get('/colleges/all/');
}
export function getPageColleges(pageIndex, pageSize, name){

	return http.get('/colleges/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name}});
}
export function addColleges(params){
	
	return http.post('/colleges/add/', params);
}
export function updColleges(params){
	
	return http.post('/colleges/upd/', params);
}
export function delColleges(id){
	
	return http.post('/colleges/del/', {id: id});
}

/** 班级信息处理接口 */
export function getAllGrades(){

	return http.get('/grades/all/');
}
export function getPageGrades(pageIndex, pageSize, name){

	return http.get('/grades/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name}});
}
export function addGrades(params){
	
	return http.post('/grades/add/', params);
}
export function updGrades(params){
	
	return http.post('/grades/upd/', params);
}
export function delGrades(id){
	
	return http.post('/grades/del/', {id: id});
}

/** 科目信息处理接口 */
export function getAllProjects(){

	return http.get('/projects/all/');
}
export function getPageProjects(pageIndex, pageSize, name){

	return http.get('/projects/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name}});
}
export function addProjects(params){
	
	return http.post('/projects/add/', params);
}
export function updProjects(params){
	
	return http.post('/projects/upd/', params);
}
export function delProjects(id){
	
	return http.post('/projects/del/', {id: id});
}

/** 学生信息处理接口 */
export function getPageStudents(pageIndex, pageSize, name, collegeId, gradeId){

	return http.get('/students/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name, collegeId: collegeId, gradeId: gradeId}});
}
export function getStudentInfo(id){

	return http.get('/students/info/', {params: {id: id}});
}
export function addStudents(params){
	
	return http.post('/students/add/', params);
}
export function updStudents(params){
	
	return http.post('/students/upd/', params);
}
export function delStudents(id){
	
	return http.post('/students/del/', {id: id});
}

/** 学生注册接口 */
export function studentRegister(params){
	
	return http.post('/students/add/', params);
}

/** 教师信息处理接口 */
export function getPageTeachers(pageIndex, pageSize, name, record, job){

	return http.get('/teachers/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name, record: record, job: job}});
}
export function addTeachers(params){
	
	return http.post('/teachers/add/', params);
}
export function updTeachers(params){
	
	return http.post('/teachers/upd/', params);
}
export function delTeachers(id){
	
	return http.post('/teachers/del/', {id: id});
}

/** 习题信息处理接口 */
export function getPagePractises(pageIndex, pageSize, name, type, projectId){

	return http.get('/practises/page/', 
        {params: {pageIndex: pageIndex, pageSize: pageSize, name: name, type: type, projectId: projectId}});
}
export function getPractiseInfo(id){

	return http.get('/practises/info/', {params: {id: id}});
}
export function addPractises(params){
	
	return http.post('/practises/add/', params);
}
export function setPractiseAnswer(params){
	
	return http.post('/practises/setanswer/', params);
}

/** 习题选项处理接口 */
export function getOptionsByPId(practiseId){

	return http.get('/options/list/', {params: {practiseId: practiseId}});
}
export function addOptions(params){
	
	return http.post('/options/add/', params);
}
export function updOptions(params){
	
	return http.post('/options/upd/', params);
}

/** 考试信息处理接口 */
export function getPageExams(pageIndex, pageSize, name, teacherId, gradeId, projectId){
    return http.get('/exams/page/', {
        params: {
            pageIndex: pageIndex || 1,
            pageSize: pageSize || 10,
            name: name || '',
            teacherId: teacherId || '',
            gradeId: gradeId || '',
            projectId: projectId || '',
            token: sessionStorage.getItem('token') || ''
        }
    });
}
export function getExams(params = {}){
    return getPageExams(
        params.pageIndex || 1,
        params.pageSize || 10,
        params.name || '',
        params.teacherId || '',
        params.gradeId || '',
        params.projectId || ''
    )
}
export function getExamInfo(id){

	return http.get('/exams/info/', {params: {id: id}});
}
export function addExams(params){
	
	return http.post('/exams/add/', params);
}
export function updExams(params){
	
	return http.post('/exams/upd/', params);
}
export function makeExams(id){
	
	return http.post('/exams/make/', {projectId: id});
}

/** 考试记录处理接口 */
export function getPageStudentExamLogs(pageIndex, pageSize, examName, studentId, projectId){
    return http.get('/examlogs/pagestu/', {
        params: {
            pageIndex: pageIndex || 1,
            pageSize: pageSize || 10,
            examName: examName || '',
            studentId: studentId || '',
            projectId: projectId || ''
        }
    });
}
export function getStudentExams(token, pageIndex = 1, pageSize = 100){
    return http.get('/examlogs/pagestu/', {
        params: {
            pageIndex: pageIndex || 1,
            pageSize: pageSize || 100
        }
    });
}
export function getPageTeacherExamLogs(pageIndex, pageSize, examName, token, gradeId, projectId){
    return http.get('/examlogs/pagetea/', {
        params: {
            pageIndex: pageIndex || 1,
            pageSize: pageSize || 10,
            examName: examName || '',
            token: token || '',
            gradeId: gradeId || '',
            projectId: projectId || ''
        }
    });
}
export function getPageExamLog(id){

	return http.get('/examlogs/info/', {params: {id: id}});
}
export function addExamLog(params){
	
	return http.post('/examlogs/add/', params);
}
export function updExamLog(params){
	
	return http.post('/examlogs/upd/', params);
}
export function putExamLog(params){
	
	return http.post('/examlogs/put/', params);
}

/** 答题记录处理接口 */
export function getAnswers(studentId, type, examId){

	return http.get('/answerlogs/answers/', 
        {params: {studentId: studentId, type: type, examId: examId}});
}
export function checkAnswers(studentId, examId){

	return http.get('/answerlogs/check/', 
        {params: {studentId: studentId, examId: examId}});
}
export function addAnswerLog(params){
    return http.post('/answerlogs/add/', params, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 180000
    });
}
export function aduitAnswerLog(params){
	
	return http.post('/answerlogs/audit/', params);
}

/** 练习试卷相关接口 */
export function getStudentPracticePapers(token) {
    return http.get('/practicepapers/student/', { params: { token: token || '' } });
}

export function getPracticePaperInfo(id) {
    return http.get('/practicepapers/info/', {params: {id: id}});
}

export function getPracticePaperQuestions(paperId) {
    return http.get('/practicepapers/questions/', {params: {paperId: paperId}});
}

export function startPractice(token, paperId) {
    return http.post('/studentpractice/start/', { token: token || '', paperId: paperId });
}

export function savePracticeProgress(logId, practiseId, studentAnswer) {
    return http.post('/studentpractice/save/', {
        logId: logId,
        practiseId: practiseId,
        studentAnswer: studentAnswer
    });
}

export function submitPractice(logId) {
    return http.post('/studentpractice/submit/', { logId: logId });
}

// 基于错题生成专项练习
export function generateWrongPracticePaper(token, projectId, limit = 10) {
    return http.post('/practicepapers/generate_wrong/', { token, projectId, limit });
}

// AI智能组卷
export function generateAIPracticePaper(params) {
    // params: { title, projectId, difficulty, duration, questionCounts }
    return http.post('/practicepapers/generate_ai/', params);
}

export function getPracticeLogs(token) {
    return http.get('/studentpractice/logs/', {params: {token: token}});
}

export function getPracticeAnswers(logId) {
	
	return http.get('/studentpractice/answers/', {params: {logId: logId}});
}

// 导出练习记录/答题明细
export function exportPracticeLogs(token) {
    return http.get('/studentpractice/export/', { params: { token: token }, responseType: 'blob' });
}
export function exportPracticeAnswers(logId) {
    return http.get('/studentpractice/export_answers/', { params: { logId }, responseType: 'blob' });
}

/** 任务管理接口 */
export function getPageTasks(pageIndex, pageSize, title, type, projectId, gradeId) {
	
	return http.get('/tasks/page/', 
		{params: {pageIndex: pageIndex, pageSize: pageSize, title: title, type: type, projectId: projectId, gradeId: gradeId}});
}

export function getTaskInfo(id) {
	
	return http.get('/tasks/info/', {params: {id: id}});
}

export function addTask(params) {
	
	return http.post('/tasks/add/', params);
}

export function updTask(params) {
	
	return http.post('/tasks/upd/', params);
}

export function delTask(id) {
	
	return http.post('/tasks/del/', {id: id});
}

/** 学生任务接口 */
export function getStudentTasks(token) {
	
	return http.get('/tasks/student/', {params: {token: token}});
}

export function getTaskQuestions(taskId) {
	
	return http.get('/tasks/questions/', {params: {taskId: taskId}});
}

export function startTask(token, taskId) {
	
	return http.post('/tasks/start/', {token: token, taskId: taskId});
}

export function saveTaskProgress(logId, practiseIds, answers) {
	
	return http.post('/tasks/save/', {logId: logId, practiseIds: practiseIds, answers: answers});
}

export function submitTask(logId) {
	
	return http.post('/tasks/submit/', {logId: logId});
}

export function getTaskLogs(token) {
	
	return http.get('/tasks/logs/', {params: {token: token}});
}

export function getTaskLogInfo(logId) {
	
	return http.get('/tasks/loginfo/', {params: {logId: logId}});
}

export function getTaskAnswers(logId) {
	
	return http.get('/tasks/answers/', {params: {logId: logId}});
}

/** 错题本相关接口 */
export function getWrongQuestionInfo(id) {
    return http.get('/wrongquestions/info/', {params: {id: id}});
}

export function getPageWrongQuestions(pageIndex, pageSize, studentId, search, filters = {}) {
    // 从 sessionStorage 获取 token
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const params = {
        page: pageIndex,
        limit: pageSize,
        studentId: studentId,
        search: search,
        projectId: filters.projectId || '',
        type: filters.type || '',
        reviewStatus: filters.reviewStatus || '',
        startDate: filters.startDate || '',
        endDate: filters.endDate || ''
    };
    if (token) {
        params.token = token;
    }
    return http.get('/wrongquestions/getPageInfos/', { params });
}

// AI 错题分析
export function analyzeWrongAnswer(params) {
    // params: { questionContent, correctAnswer, wrongAnswer, questionType }
    return http.get('/ai/analyze_wrong_answer/', { params });
}

export function getStudentWrongQuestions(studentId) {
    return http.get('/wrongquestions/getStudentWrongQuestions/', {
        params: {studentId: studentId}
    });
}

export function getWrongQuestionDetail(id) {
    return http.get('/wrongquestions/getWrongQuestionDetail/', {
        params: {id: id}
    });
}

export function getReviewHistory(id) {
    return http.get('/wrongquestions/getReviewHistory/', {
        params: {id: id}
    });
}

export function addWrongQuestion(params) {
    return http.post('/wrongquestions/addWrongQuestion/', params);
}

export function markAsReviewed(id) {
    return http.post('/wrongquestions/markAsReviewed/', {id: id});
}

export function addReview(params) {
    return http.post('/wrongquestions/addReview/', params);
}

export function deleteWrongQuestion(id) {
    return http.post('/wrongquestions/deleteWrongQuestion/', {id: id});
}

export function exportWrongQuestions(filters = {}) {
    const params = {
        studentId: filters.studentId || '',
        projectId: filters.projectId || '',
        type: filters.type || '',
        reviewStatus: filters.reviewStatus || '',
        startDate: filters.startDate || '',
        endDate: filters.endDate || '',
        search: filters.search || ''
    };
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (token) {
        params.token = token;
    }
    return http.get('/wrongquestions/export/', { params, responseType: 'blob' });
}

/** 管理员功能接口 */
// 仪表板
export function getAdminDashboard() {
    return http.get('/admin/dashboard/');
}

export function getAdminDashboardCards() {
    return http.get('/admin/dashboard_cards/');
}

export function getAdminTrends() {
    return http.get('/admin/trends/');
}

// 用户管理
export function getAdminUsers(params) {
    return http.get('/admin/users/', { params });
}
export function addAdminUser(params) {
    return http.post('/admin/users/', { ...params, action: 'add' });
}
export function updateAdminUser(params) {
    return http.post('/admin/users/', { ...params, action: 'update' });
}
export function deleteAdminUser(id) {
    return http.post('/admin/users/', { id, action: 'delete' });
}
export function disableAdminUser(id) {
    return http.post('/admin/users/', { id, action: 'disable' });
}

// 学科管理
export function getAdminSubjects(params) {
    return http.get('/admin/subjects/', { params });
}
export function addAdminSubject(params) {
    return http.post('/admin/subjects/', { ...params, action: 'add' });
}
export function updateAdminSubject(params) {
    return http.post('/admin/subjects/', { ...params, action: 'update' });
}
export function deleteAdminSubject(id) {
    return http.post('/admin/subjects/', { id, action: 'delete' });
}

// 试卷管理
export function getAdminExams(params) {
    return http.get('/admin/exams/', { params });
}
export function addAdminExam(params) {
    return http.post('/admin/exams/', { ...params, action: 'add' });
}
export function updateAdminExam(params) {
    return http.post('/admin/exams/', { ...params, action: 'update' });
}
export function deleteAdminExam(id) {
    return http.post('/admin/exams/', { id, action: 'delete' });
}

// 题目管理
export function getAdminQuestions(params) {
    return http.get('/admin/questions/', { params });
}
export function addAdminQuestion(params) {
    return http.post('/admin/questions/', { ...params, action: 'add' });
}
export function updateAdminQuestion(params) {
    return http.post('/admin/questions/', { ...params, action: 'update' });
}
export function deleteAdminQuestion(id) {
    return http.post('/admin/questions/', { id, action: 'delete' });
}

// AI 生成并保存到题库（管理员）
export function adminGenerateAIQuestions(params) {
    // params: { subject, topic, difficulty, questionType, count, subjectId }
    return http.post('/admin/generateAIQuestions/', params);
}

// 题目批量导入（CSV）
export function importAdminQuestions(formData) {
    return http.post('/admin/questions_import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
}

// 题目批量导出（CSV）
export function exportAdminQuestions(filters) {
    return http.post('/admin/questions_export/', filters, { responseType: 'blob' });
}

// 下载题目导入模板（CSV）
export function downloadQuestionsTemplate() {
    return http.post('/admin/questions_template/', {}, { responseType: 'blob' });
}

// 学生批量导入/导出/统计
export function importAdminStudents(formData) {
    return http.post('/admin/students_import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
}

export function batchImportStudents(formData) {
    return http.post('/students/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
}

export function downloadStudentsTemplate() {
    return http.get('/admin/students_template/', { responseType: 'blob' });
}

export function exportAdminStudents(params = {}) {
    return http.get('/admin/export_students/', { params, responseType: 'blob' });
}

export function exportAdminTeachers() {
    return http.get('/admin/export_teachers/', { responseType: 'blob' });
}

export function exportAdminExamResults(examId) {
    return http.get('/admin/export_exam_results/', {
        params: { examId },
        responseType: 'blob'
    });
}

export function exportAdminPracticeResults(practiceId) {
    return http.get('/admin/export_practice_results/', {
        params: { practiceId },
        responseType: 'blob'
    });
}

export function getAdminExamStatistics(examId) {
    return http.get('/admin/statistics_exam/', { params: { examId } });
}

export function getAdminStudentStatistics(studentId, days = 30) {
    return http.get('/admin/statistics_student/', { params: { studentId, days } });
}

export function getStudentProgressStats(studentId, timeRange = 'semester') {
    return http.get('/statistics/student_progress/', { params: { studentId, timeRange } });
}

export function getAdminClassStatistics(gradeId) {
    return http.get('/admin/statistics_class/', { params: { gradeId } });
}

export function getAdminSubjectStatistics(projectId) {
    return http.get('/admin/statistics_subject/', { params: { projectId } });
}

// 管理端：练习试卷分页查询
export function getAdminPracticePapers(params) {
	return http.get('/practicepapers/page/', { params });
}

// 新增：获取教师列表（用于下拉）
export function listTeachers(pageIndex=1, pageSize=500, name=''){
    return http.get('/teachers/page/', { params: { pageIndex, pageSize, name } });
}

// 新增：获取年级列表（用于下拉）
export function listGrades(pageIndex=1, pageSize=500, name=''){
    return http.get('/grades/page/', { params: { pageIndex, pageSize, name } });
}

// 任务管理
export function getAdminTasks(params) {
    return http.get('/admin/tasks/', { params });
}
export function addAdminTask(params) {
    return http.post('/admin/tasks/', { ...params, action: 'add' });
}
export function updateAdminTask(params) {
    return http.post('/admin/tasks/', { ...params, action: 'update' });
}
export function deleteAdminTask(id) {
    return http.post('/admin/tasks/', { id, action: 'delete' });
}

// 消息管理
export function getAdminMessages(params) {
    return http.get('/admin/messages/', { params });
}
export function sendAdminMessage(payload) {
    // payload 可以是 FormData（用于文件/数组），也可以是普通对象
    return http.post('/admin/messages/', payload);
}
export function forwardMessage(params) {
    return http.post('/admin/messages/', { ...params, action: 'forward' });
}
export function deleteAdminMessage(id) {
    return http.post('/admin/messages/', { id, action: 'delete' });
}

// 消息附件下载
export function downloadMessageAttachment(id) {
    return http.get('/admin/message_attachment/', {
        params: { id },
        responseType: 'blob'
    });
}

// 管理端：查看消息已读详情
export function getMessageReaders(params) {
    return http.get('/admin/message_readers/', { params });
}

// 学生端消息中心：个人消息
export function getUserMessages(token, type='') {
    return http.get('/messages/', {
        params: {
            token: token || '',
            type: type || ''
        }
    });
}

export function markUserMessageRead(token, id) {
    return http.post('/messages/', {
        token: token || '',
        action: 'mark_read',
        messageId: id  // 修改：后端期望 messageId 而不是 id
    });
}

export function markAllUserMessagesRead(token) {
    return http.post('/messages/', {
        token: token || '',
        action: 'mark_all_read'
    });
}

export function deleteUserMessage(token, id) {
    return http.post('/messages/', {
        token: token || '',
        action: 'delete',
        messageId: id  // 修改：后端期望 messageId 而不是 id
    });
}

// 一键为所有学科补齐基础题量（选择10/填空10/判断10/编程2），只补缺口
export function fillAllSubjectsMinimum(params={}) {
    return http.post('/admin/fill_all_subjects/', params, { timeout: 180000 });
}

/** 操作日志接口 */
export function getPageOperationLogs(params) {
    return http.get('/logs/', { params });
}

export function deleteOperationLogs(ids) {
    return http.delete('/logs/', { params: { ids } });
}

export function exportOperationLogs(filters) {
    return http.put('/logs/', { filters }, { responseType: 'blob' });
}

