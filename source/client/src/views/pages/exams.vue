<template>
	<div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-document" class="header-icon" />
                <div class="header-text">
                    <h2>考试管理</h2>
                    <p>管理系统中的所有考试安排</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalInfo }}</div>
                    <div class="stat-label">总考试数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ activeExams }}</div>
                    <div class="stat-label">进行中</div>
                </div>
            </div>
        </div>

        <Card class="search-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-search" class="title-icon" />
                    <span>考试查询</span>
                </div>
            </template>
			<div class="search-form">
				<Form :model="qryForm" inline class="modern-form">
					<FormItem class="form-item">
						<Input 
                            type="text" 
                            v-model="qryForm.name" 
                            placeholder="考试名称……"
                            class="modern-input"
                            prefix="ios-document">
                        </Input>
					</FormItem>
                    <FormItem v-if="userInfo.type != 2" class="form-item">
                        <Select 
                            style="width:200px;" 
                            v-model="qryForm.gradeId" 
                            placeholder="选择考试班级……"
                            class="modern-select" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in grades" 
                                :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                        </Select>
					</FormItem>
                    <FormItem class="form-item">
                        <Select 
                            style="width:200px;" 
                            v-model="qryForm.projectId" 
                            placeholder="选择考试科目……"
                            class="modern-select" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in projects" 
                                :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                        </Select>
					</FormItem>
					<FormItem class="form-item">
						<Button 
                            type="primary" 
                            @click="getPageInfo()"
                            class="search-btn btn-ripple">
							<Icon type="ios-search" />
							搜索
						</Button>
					</FormItem>
				</Form>
			</div>
		</Card>

        <Card class="data-card animate-fade-in-up delay-200">
			<template #title>
				<div class="card-title">
                    <Icon type="ios-list" class="title-icon" />
                    <span>考试列表</span>
                    <Button 
                        v-if="userInfo.type == 0" 
                        @click="showAddWin()" 
                        type="primary"
                        class="add-btn btn-ripple">
						<Icon type="md-add" />
						添加考试
					</Button>
                </div>
			</template>
			<div class="table-container">
				<Table 
                    border 
                    :columns="columns" 
                    :loading="loading" 
                    :data="pageInfos"
                    class="modern-table">
                    <template #action="{ row }">
                        <div class="action-container">
                            <Button 
                                v-if="row.status !== 2" 
                                @click="startExam(row.id)" 
                                size="small" 
                                type="info"
                                class="start-btn">
                                <Icon type="ios-play" />
                                开始考试
                            </Button>
                            <Tag 
                                v-else 
                                type="border" 
                                color="#FF9900"
                                class="status-tag finished">
                                考试结束
                            </Tag>
                        </div>
                    </template>
				</Table>
				<div class="pagination-container">
					<Page 
                        v-if="pageTotal > 1" 
                        :current="pageIndex"
						@on-change="handleCurrentChange" 
                        :total="totalInfo" 
                        show-total
                        class="modern-pagination"/>
				</div>
			</div>
		</Card>

        <Modal 
            width="700" 
            v-model="showAddFlag"
			title="添加考试" 
            ok-text="提交" 
            cancel-text="取消" 
            @on-ok="addInfo()"
            class="modern-modal">
			<Form :label-width="80" :model="examForm" class="modal-form">
				<FormItem label="考试名称">
					<Input 
                        v-model="examForm.name" 
                        placeholder="请输入考试名称..."
                        class="modern-input">
                    </Input>
				</FormItem>
                <FormItem label="考试时间">
                    <DatePicker 
                        v-model="examForm.examTime" 
                        type="datetime" 
                        placeholder="请选择考试时间..." 
                        style="width: 100%"
                        class="modern-datepicker" transfer />
                    <div style="margin-top:8px;color:#909399;font-size:12px">未选择将默认当前时间</div>
				</FormItem>
                <FormItem label="开始时间">
                    <DatePicker 
                        v-model="examForm.startTime" 
                        type="datetime" 
                        placeholder="可选：考试开始时间"
                        style="width: 100%"
                        class="modern-datepicker" transfer />
                </FormItem>
                <FormItem label="结束时间">
                    <DatePicker 
                        v-model="examForm.endTime" 
                        type="datetime" 
                        placeholder="可选：考试结束时间"
                        style="width: 100%"
                        class="modern-datepicker" transfer />
                </FormItem>
                <FormItem label="审核教师">
                    <Select 
                        v-model="examForm.teacherId" 
                        placeholder="选择审核教师……"
                        class="modern-select" transfer>
                        <Option v-for="(item, index) in teachers" 
                            :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}（{{ item.id }}）</Option>
                    </Select>
                </FormItem>
                <FormItem label="考核班级">
                    <Select 
                        style="width: 100%" 
                        v-model="examForm.gradeId" 
                        placeholder="选择考试班级……"
                        class="modern-select" transfer>
                        <Option v-for="(item, index) in grades" 
                            :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                    </Select>
                </FormItem>
				<FormItem label="考核科目">
                    <Select 
                        style="width: 100%" 
                        v-model="examForm.projectId" 
                        placeholder="选择考试科目……"
                        class="modern-select" transfer>
                        <Option v-for="(item, index) in projects" 
                            :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                    </Select>
                </FormItem>
			</Form>
		</Modal>
    </div>
</template>

<style scoped>
.fater-body-show {
    padding: 24px;
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    min-height: 100vh;
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.page-header {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    box-shadow: 0 10px 30px rgba(24, 144, 255, 0.3);
}

.header-content {
    display: flex;
    align-items: center;
    gap: 15px;
}

.header-icon {
    font-size: 40px;
    color: #fff;
}

.header-text h2 {
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 5px 0;
    color: #fff;
}

.header-text p {
    font-size: 14px;
    opacity: 0.9;
    margin: 0;
    color: rgba(255, 255, 255, 0.9);
}

.header-stats {
    display: flex;
    gap: 20px;
}

.stat-item {
    text-align: center;
    padding: 15px 25px;
    background: rgba(255,255,255,0.15);
    border-radius: 10px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.stat-item:hover {
    background: rgba(255,255,255,0.25);
    transform: translateY(-2px);
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
    color: #fff;
}

.stat-label {
    font-size: 12px;
    opacity: 0.8;
    color: rgba(255, 255, 255, 0.9);
}

.search-card, .data-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    border: 1px solid rgba(24, 144, 255, 0.1);
    margin-bottom: 24px;
    background: #fff;
    transition: all 0.3s ease;
}

.search-card:hover,
.data-card:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
}

.card-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    font-weight: 600;
    color: #262626;
}

.title-icon {
    font-size: 18px;
    color: #1890ff;
}

.search-form {
    padding: 10px 0;
}

.modern-form {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
}

.form-item {
    margin-bottom: 0;
}

.modern-input {
    border-radius: 8px;
    border: 1px solid rgba(24, 144, 255, 0.2);
    transition: all 0.3s ease;
}

.modern-input:hover {
    border-color: #1890ff;
}

.modern-input:focus {
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.modern-select {
    border-radius: 8px;
}

.modern-datepicker {
    border-radius: 8px;
}

.search-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #fff;
}

.search-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.add-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    border: none;
    border-radius: 8px;
    margin-left: auto;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #fff;
}

.add-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

.table-container {
    padding: 10px 0;
}

.modern-table {
    border-radius: 8px;
    overflow: hidden;
}

.modern-table .ivu-table th {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    font-weight: 600;
    color: #fff;
}

.modern-table .ivu-table td {
    transition: background-color 0.3s ease;
}

.modern-table .ivu-table tr:hover td {
    background-color: rgba(24, 144, 255, 0.05) !important;
}

.action-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.status-tag {
    border-radius: 15px;
    padding: 4px 12px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.status-tag.waiting {
    background: rgba(0, 153, 102, 0.1);
    border-color: #009966;
    color: #009966;
}

.status-tag.finished {
    background: rgba(255, 153, 0, 0.1);
    border-color: #faad14;
    color: #faad14;
}

.start-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #fff;
}

.start-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
}

.modern-pagination .ivu-page-item {
    border-radius: 6px;
    transition: all 0.3s ease;
}

.modern-pagination .ivu-page-item:hover {
    background: #1890ff;
    color: #fff;
}

.modern-pagination .ivu-page-item-active {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-color: #1890ff;
}

.modern-modal .ivu-modal-header {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: #fff;
    border-radius: 8px 8px 0 0;
}

.modern-modal .ivu-modal-header-inner {
    color: #fff;
    font-weight: 600;
}

.modal-form {
    padding: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .fater-body-show {
        padding: 16px;
    }

    .page-header {
        flex-direction: column;
        gap: 20px;
        text-align: center;
        padding: 20px;
    }

    .header-content {
        flex-direction: column;
        gap: 10px;
    }

    .header-stats {
        justify-content: center;
        flex-wrap: wrap;
    }

    .modern-form {
        flex-direction: column;
        align-items: stretch;
    }

    .form-item {
        width: 100%;
    }

    .modern-input,
    .modern-select {
        width: 100% !important;
    }
}
</style>

<script>
import {
    getLoginUser,
    getAllProjects,
    getAllGrades,
    getPageExams,
    addExams,
    updExams,
    addExamLog
} from '../../api/index.js';
import http from '../../utils/http.js';
import {
    formatDate,
    contrastNow
} from '../../utils/date.js';
import authMixin from '@/mixins/authMixin';

export default{
    mixins: [authMixin],
    data(){
        return {
            userInfo: {},
            projects: [],
            grades: [],
			teachers: [],
            pageInfos: [],
            pageIndex: 1,
            pageSize: 10,
            pageTotal: 0,
            totalInfo: 0,
            loading: true,
            showAddFlag: false,
            qryForm: {
                name: "",
                gradeId: "",
                projectId: "",
                teacherId: ""
            },
            examForm: {
                id: "",
                name: "",
                examTime: "",
                startTime: "",
                endTime: "",
                gradeId: "",
                projectId: "",
                teacherId: ""
            },
            columns: []
        }
    },
    computed: {
        activeExams() {
            return this.pageInfos.filter(exam => exam.status === 0).length;
        }
    },
    methods:{
		getPageInfo(pageIndex, pageSize) {
			
            getPageExams(pageIndex, pageSize,
                this.qryForm.name, this.qryForm.teacherId,
                this.qryForm.gradeId, this.qryForm.projectId).then(resp => {

                const page = resp.data || {};
                const list = page.data || [];
                const now = new Date();
                list.forEach(item => {
                    const hasStart = !!item.startTime;
                    const hasEnd = !!item.endTime;
                    if (hasStart || hasEnd) {
                        const s = hasStart ? new Date(String(item.startTime).replace(/-/g,'/')) : null;
                        const e = hasEnd ? new Date(String(item.endTime).replace(/-/g,'/')) : null;
                        if (s && now < s) item.status = 1; // 未开始
                        else if (e && now > e) item.status = 2; // 已结束
                        else item.status = 0; // 进行中
                    } else {
                        // 兼容旧逻辑：examTime <= now 视为进行中，否则未开始
                        item.status = contrastNow(item.examTime) <= 0 ? 0 : 1;
                    }
                    // 如果该学生已经有考试日志且状态为2（结束），强制标记为已结束
                    if (item.studentStatus === 2) {
                        item.status = 2;
                    }
                });

                this.pageInfos = list;
                this.pageIndex = page.pageIndex || 1;
                this.pageSize = page.pageSize || 10;
                this.pageTotal = page.pageTotal || 0;
                this.totalInfo = page.count || list.length;
                this.loading = false;
            }).catch(() => {
                this.pageInfos = [];
                this.loading = false;
            });
        },
        handleCurrentChange(pageIndex) {
        
            this.getPageInfo(pageIndex, this.pageSize);
        },	
        showAddWin(){

            this.examForm = {
                id: "",
                name: "",
                examTime: "",
                startTime: "",
                endTime: "",
                gradeId: "",
                projectId: "",
                teacherId: ""
            }
            this.showAddFlag = true;
        },
        addInfo() {
			
            this.examForm.examTime = this.examForm.examTime ? formatDate(this.examForm.examTime) : '';
            this.examForm.startTime = this.examForm.startTime ? formatDate(this.examForm.startTime) : '';
            this.examForm.endTime = this.examForm.endTime ? formatDate(this.examForm.endTime) : '';
            addExams(this.examForm).then(resp => {
                
                if(resp.code == 0){

                    this.$Notice.success({
                        duration: 3,
                        title: resp.msg
                    });
                    
                    this.getPageInfo(1, this.pageSize);
                    
                    this.showAddFlag = false;
                }else{

                    this.$Message.warning({
                        background: true,
                        content: resp.msg
                    });
                    this.showAddFlag = true;
                }
            });
        },
        startExam(id){

            // 添加登录检查
            if (!this.checkLogin('请先登录后再开始考试')) {
                return
            }

            this.$Modal.confirm({
                title: '确认开始考试',
                content: '开始考试后将无法暂停，确定要开始吗？',
                okText: '开始',
                cancelText: '取消',
                onOk: () => {
                    addExamLog(this.getAuthParams({ examId: id })).then(() =>{

                    }).catch((error) => {
                        console.error('记录考试开始失败:', error);
                        // 记录失败不阻断进入答题页
                    }).then(() => {
                        // 使用路径跳转，如未匹配到路由则退回 hash 方式，避免热更新路由未就绪
                        const to = { path: '/home/answer', query: { id: id } };
                        const r = this.$router.resolve(to);
                        if (!r || !r.matched || r.matched.length === 0) {
                            window.location.hash = `#/home/answer?id=${id}`;
                            return;
                        }
                        this.$router.push(to);
                    });
                }
            });
        }
    },
    mounted(){

        getLoginUser(this.token).then(resp =>{

            this.userInfo = resp.data;

            if(this.userInfo.type == 0){

                this.columns = [
                    {title: '序号', type: 'index', width: 70, align: 'center'},
                    {title: '考试名称', key: 'name', align: 'center'},
                    {title: '考试时间', key: 'examTime', align: 'center'},
                    {title: '考试科目', key: 'projectName', align: 'center'},
                    {title: '考试班级', key: 'gradeName', align: 'center'},
                    {title: '审核教师', key: 'teacherName', align: 'center'}
                ]
                this.getPageInfo(1, this.pageSize);
            }else if(this.userInfo.type == 1){

                this.columns = [
                    {title: '序号', type: 'index', width: 70, align: 'center'},
                    {title: '考试名称', key: 'name', align: 'center'},
                    {title: '考试时间', key: 'examTime', align: 'center'},
                    {title: '考试科目', key: 'projectName', align: 'center'},
                    {title: '考试班级', key: 'gradeName', align: 'center'}
                ]
                this.qryForm.teacherId = this.userInfo.id;
                this.getPageInfo(1, this.pageSize);
            }else if(this.userInfo.type == 2){

                this.columns = [
                    {title: '序号', type: 'index', width: 70, align: 'center'},
                    {title: '考试名称', key: 'name', align: 'center'},
                    {title: '考试时间', key: 'examTime', align: 'center'},
                    {title: '考试科目', key: 'projectName', align: 'center'},
                    {title: '考试班级', key: 'gradeName', align: 'center'},
                    {title: '审核教师', key: 'teacherName', align: 'center'},
                    {title: '操作', slot: 'action', align: 'center'}
                ]
                this.qryForm.gradeId = this.userInfo.gradeId;
                this.getPageInfo(1, this.pageSize);
            }
        });
		getAllProjects().then(resp =>{

            this.projects = resp.data;
        });
        getAllGrades().then(resp =>{

            this.grades = resp.data;
        });
		// 载入教师下拉（前500条）
		http.get('/teachers/page/', { params: { pageIndex: 1, pageSize: 500 } }).then(resp => {
			if (resp.code === 0) this.teachers = (resp.data && resp.data.data) || []
		});
    }
}
</script>