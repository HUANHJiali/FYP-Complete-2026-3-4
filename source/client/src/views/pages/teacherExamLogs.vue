<template>
    <div class="fater-body-show">
        <Card>
            <template #title>
				信息查询
			</template>
			<div>
				<Form :model="qryForm" inline>
					<FormItem>
						<Input type="text" v-model="qryForm.examName" placeholder="考试名称……"></Input>
					</FormItem>
					<FormItem>
						<Select style="width:200px;" v-model="qryForm.gradeId" placeholder="选择班级……">
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in grades" 
                                :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                        </Select>
					</FormItem>
					<FormItem>
						<Select style="width:200px;" v-model="qryForm.projectId" placeholder="选择科目……">
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in projects" 
                                :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                        </Select>
					</FormItem>
					<FormItem>
						<Button type="primary" @click="getPageInfo()">
							<Icon type="ios-search" />
						</Button>
					</FormItem>
				</Form>
			</div>
		</Card>

        <Card>
			<div>
				<Table border :columns="columns" :loading="loading" :data="pageInfos">
					<template #action="{ row }">
                        <Tag v-if="row.status == 0" type="border" color="primary">考试中</Tag>
						<Button v-else-if="row.status == 1"
                                size="small" type="warning" @click="putScore(row)">公布成绩</Button>
                        <span v-else>处理完毕(得分{{ row.score }})</span>
					</template>
					<template #action1="{ row }">
						<Button v-if="row.status == 1"
                                size="small" type="success" @click="showAuditWin_1(row)">审核</Button>
                        <Button v-else
                                size="small" type="info" disabled>审核</Button>
					</template>
					<template #action2="{ row }">
						<Button v-if="row.status == 1"
                                size="small" type="success" @click="showAuditWin_2(row)">审核</Button>
                        <Button v-else
                                size="small" type="info" disabled>审核</Button>
					</template>
				</Table>
				<Page style="margin-top: 15px;" v-if="pageTotal > 1" :current="pageIndex"
					@on-change="handleCurrentChange" :total="totalInfo" show-total/>
			</div>
		</Card>

        <Modal fullscreen="true" v-model="showAuditFlag_1" footer-hide="true" title="填空题审核">
            <Table border :columns="pracCols1" :data="ansers_1">
                <template #practiseName="{ row }">
                    <QuestionContentRenderer :content="row.practiseName" compact />
                </template>
                <template #practiseAnswerText="{ row }">
                    <QuestionContentRenderer :content="row.practiseAnswer" compact />
                </template>
                <template #action="{ row }">
                    <Button v-if="row.status==0" size="small" style="margin-right: 5px;"
                                    type="success" @click="auditLog(row.id, 1, 0)">正确</Button>
                    <Button v-if="row.status==1" size="small" disabled
                             style="margin-right: 5px;" type="success">正确</Button>
                    <Button v-if="row.status==0" size="small" type="error" @click="auditLog(row.id, 1, 1)">错误</Button>
                    <Button v-if="row.status==1" size="small" type="error" disabled>错误</Button>
                </template>
                <template #score="{ row }">
                    <Tag v-if="row.status==0" type="border" color="green">待审</Tag>
                    <span v-if="row.status==1" >{{ row.score }}</span>
                </template>
                <template #action1="{ row }">
                    <QuestionContentRenderer v-if="row.answer" :content="row.answer" compact />
                    <span v-else>未作答</span>
                </template>
            </Table>
        </Modal>
        
        <Modal fullscreen="true" v-model="showAuditFlag_2" footer-hide="true" title="编程题审核">
            <Table border :columns="pracCols2" :data="ansers_2">
                <template #practiseName="{ row }">
                    <QuestionContentRenderer :content="row.practiseName" compact />
                </template>
                <template #practiseAnswer="{ row }">
                    <Input v-model="row.practiseAnswer" type="textarea" :rows="6" :border="false"/>    
                </template>
                <template #answer="{ row }">
                    <Input v-if="row.answer" v-model="row.answer" type="textarea" :rows="6" :border="false"/>   
                    <span v-else>未作答</span> 
                </template>
                <template #score="{ row }">
                    <Tag v-if="row.status==0" type="border" color="green">待审</Tag>
                    <span v-if="row.status==1" >{{ row.score }}</span>
                </template>
                <template #action="{ row }">
                    <Button v-if="row.status==0" size="small" style="margin-right: 5px;"
                                    type="success" @click="auditLog(row.id, 3, 0)">正确</Button>
                    <Button v-if="row.status==1" size="small" disabled
                             style="margin-right: 5px;" type="success">正确</Button>
                    <Button v-if="row.status==0" size="small" type="error" @click="auditLog(row.id, 3, 1)">错误</Button>
                    <Button v-if="row.status==1" size="small" type="error" disabled>错误</Button>
                </template>                
            </Table>
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

/* Card 美化 */
.ivu-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    border: 1px solid rgba(24, 144, 255, 0.1);
    margin-bottom: 24px;
    transition: all 0.3s ease;
}

.ivu-card:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
}

.ivu-card-head {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 12px 12px 0 0;
    padding: 16px 20px;
}

.ivu-card-head-inner {
    color: #000;
    font-size: 16px;
    font-weight: 600;
}

.ivu-card-body {
    padding: 24px;
}

/* Form 美化 */
.ivu-form-inline .ivu-form-item {
    margin-right: 16px;
    margin-bottom: 16px;
}

.ivu-input {
    border-radius: 8px;
    transition: all 0.3s ease;
    border: 1px solid rgba(24, 144, 255, 0.2);
    color: #333 !important;
}

.ivu-input:focus {
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.ivu-select {
    border-radius: 8px;
}

.ivu-select-selection {
    border-radius: 8px;
    border: 1px solid rgba(24, 144, 255, 0.2);
}

.ivu-select-focused .ivu-select-selection {
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* Button 美化 */
.ivu-btn-primary {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    transition: all 0.3s ease;
}

.ivu-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.ivu-btn-warning {
    background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
    border: none;
    border-radius: 8px;
}

.ivu-btn-warning:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(250, 173, 20, 0.4);
}

.ivu-btn-success {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    border: none;
    border-radius: 8px;
}

.ivu-btn-success:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

.ivu-btn-info {
    background: linear-gradient(135deg, #909399 0%, #606266 100%);
    border: none;
    border-radius: 8px;
}

/* Table 美化 */
.ivu-table {
    border-radius: 8px;
    overflow: hidden;
}

.ivu-table th {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: #000 !important;
    font-weight: 600;
}

.ivu-table td {
    color: #333 !important;
    transition: background-color 0.3s ease;
}

.ivu-table:hover tr:hover td {
    background-color: rgba(24, 144, 255, 0.05) !important;
}

.ivu-table-border th,
.ivu-table-border td {
    border-color: rgba(24, 144, 255, 0.1);
}

.ivu-table .ivu-table-cell {
    white-space: normal;
    line-height: 1.6;
}

.ivu-table-tip {
    color: #8c8c8c;
}

/* Modal 美化 */
.ivu-modal .ivu-table th,
.ivu-modal .ivu-table td {
    color: #333;
}

.ivu-modal-header {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 12px 12px 0 0;
}

.ivu-modal-header-inner {
    color: #000;
    font-weight: 600;
}

/* Tag 美化 */
.ivu-tag {
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 500;
}

.ivu-tag-primary {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-color: #1890ff;
    color: #000;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .fater-body-show {
        padding: 16px;
    }

    .ivu-card-body {
        padding: 16px;
    }

    .ivu-form-inline .ivu-form-item {
        display: block;
        margin-right: 0;
        width: 100%;
    }

    .ivu-input,
    .ivu-select {
        width: 100% !important;
    }

    .ivu-table {
        font-size: 12px;
    }
}
</style>

<script>
import {
    getPageTeacherExamLogs,
    getLoginUser,
    getAllProjects,
    getAllGrades,
    getAnswers,
    checkAnswers,
    aduitAnswerLog,
    putExamLog
} from '../../api/index.js';
import QuestionContentRenderer from '@/components/QuestionContentRenderer.vue';
export default{
    components: {
        QuestionContentRenderer
    },
		
    data(){
        return {
            grades: [],
            projects: [],
            userInfo: {},
            pageInfos: [],
            ansers_1: [],
            ansers_2: [],
            showAuditFlag_1: false,
            showAuditFlag_2: false,
            pageInfos: [],
            pageIndex: 1,
            pageSize: 10,
            pageTotal: 0,
            totalInfo: 0,
            loading: true,
            qryForm: {
                examName: "",
                token: this.$store.state.token || sessionStorage.getItem('token') || '',
                gradeId: "",
                projectId: "",
            },
            answersForm: {
                studentId: "",
                type: "",
                examId: "",
                flag: "",
                score: ""
            },
            columns: [
                {title: '序号', type: 'index', width: 70, align: 'center'},
                {title: '考试名称', key: 'examName', align: 'center'},
                {title: '考试班级', key: 'gradeName', align: 'center'},
                {title: '考核科目', key: 'projectName', align: 'center'},
                {title: '参考学生', key: 'studentName', align: 'center'},
                {title: '填空审核', slot: 'action1', width: 150, align: 'center'},
                {title: '编程审核', slot: 'action2', width: 150, align: 'center'},
                {title: '操作', slot: 'action', align: 'center'}
            ],
            pracCols1: [
                {title: '序号', type: 'index', width: 70, align: 'center'},
                {title: '考试题目', slot: 'practiseName', width: 620, align: 'left'},
                {title: '参考答案', slot: 'practiseAnswerText', align: 'left'},
                {title: '考生提交', slot: 'action1', align: 'left'},
                {title: '审核结果', slot: 'score', width: 120, align: 'center'},
                {title: '操作', slot: 'action', width: 300, align: 'center'}
            ],
            pracCols2: [
                {title: '序号', type: 'index', width: 70, align: 'center'},
                {title: '考试题目', slot: 'practiseName', width: 580, align: 'left'},
                {title: '参考答案', slot: 'practiseAnswer', align: 'left'},
                {title: '考生提交', slot: 'answer', align: 'left'},
                {title: '审核结果', slot: 'score', width: 120, align: 'center'},
                {title: '操作', slot: 'action', width: 180, align: 'center'}
            ]
        }
    },
    methods: {

        showAuditWin_1(row){

            this.answersForm = {
                studentId: row.studentId,
                type: 1,
                examId: row.examId,
            }
            getAnswers(row.studentId, 
                    1, row.examId).then(resp =>{
                
                this.ansers_1 = resp.data;
                this.showAuditFlag_1 = true;
            });
        },
        showAuditWin_2(row){

            this.answersForm = {
                studentId: row.studentId,
                type: 3,
                examId: row.examId,
            }
            getAnswers(row.studentId, 
                    3, row.examId).then(resp =>{
                
                this.ansers_2 = resp.data;
                this.showAuditFlag_2 = true;
            });
        },
        putScore(row){

            checkAnswers(row.studentId, row.examId).then(resp =>{
                
                if(resp.data.flag){

                    this.$Notice.warning({
                        duration: 3,
                        title: "系统提示",
                        desc: "填空或者编程类型题目未完全审核，不能发布成绩"
                    });
                }else{
                    this.$Modal.confirm({
                        title: '系统提示',
                        content: '成绩发布之后, 结果将无法修改, 是否继续?',
                        onOk: () => {

                            putExamLog({
                                studentId: row.studentId,
                                examId: row.examId
                            }).then(res =>{

                                this.getPageInfo(1, this.pageSize);
                                this.$Notice.success({
                                    duration: 3,
                                    title: "发布成绩成功"
                                });
                            });
                        }
                    });
                }
            })
             
        },
        auditLog(id, type, flag){

             this.$Modal.confirm({
                title: '系统提示',
                content: '提交之后, 结果将无法修改, 是否继续?',
                onOk: () => {
                    aduitAnswerLog({
                        id: id,
                        type: type,
                        flag: flag
                    }).then(resp =>{

                        getAnswers(this.answersForm.studentId, 
                                this.answersForm.type, 
                                this.answersForm.examId).then(resp =>{
                            
                            if(type == 1){

                                this.ansers_1 = resp.data;
                            }else{

                                this.ansers_2 = resp.data;
                            }
                        });
                        this.$Notice.success({
                            duration: 3,
                            title: resp.msg
                        });
                    });
                },
            });
        },
        getPageInfo(pageIndex, pageSize) {
			
            getPageTeacherExamLogs(pageIndex, pageSize,
                this.qryForm.examName, this.qryForm.token,
                this.qryForm.gradeId, this.qryForm.projectId).then(resp => {
                const page = resp.data || {};
                this.pageInfos = page.data || [];
                this.pageIndex = page.pageIndex || 1;
                this.pageSize = page.pageSize || 10;
                this.pageTotal = page.pageTotal || 0;
                this.totalInfo = page.count || (this.pageInfos.length);
                this.loading = false;
            }).catch(() => {
                this.pageInfos = [];
                this.loading = false;
            });
        },
        handleCurrentChange(pageIndex) {
        
            this.getPageInfo(pageIndex, this.pageSize);
        },
    },
    mounted(){
        const token = this.$store.state.token || sessionStorage.getItem('token') || ''
        this.qryForm.token = token
        
        getAllProjects().then(resp =>{

            this.projects = resp.data;
        });
        getAllGrades().then(resp =>{

            this.grades = resp.data;
        });
        getLoginUser(token).then(resp =>{

            this.userInfo = resp.data;
        });
        this.getPageInfo(1, this.pageSize);
    }
}
</script>