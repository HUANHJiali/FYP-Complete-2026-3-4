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
						<Tag v-else-if="row.status == 1"
                                type="border" color="blue">等待审核</Tag>
                        <span v-else>{{ row.score }}</span>
					</template>
				</Table>
				<Page style="margin-top: 15px;" v-if="pageTotal > 1" :current="pageIndex"
					@on-change="handleCurrentChange" :total="totalInfo" show-total/>
			</div>
		</Card>
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
    color: #fff;
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

/* Table 美化 */
.ivu-table {
    border-radius: 8px;
    overflow: hidden;
}

.ivu-table th {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: #fff;
    font-weight: 600;
}

.ivu-table td {
    transition: background-color 0.3s ease;
}

.ivu-table:hover tr:hover td {
    background-color: rgba(24, 144, 255, 0.05) !important;
}

.ivu-table-border th,
.ivu-table-border td {
    border-color: rgba(24, 144, 255, 0.1);
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
    color: #fff;
}

.ivu-tag-blue {
    background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
    border-color: #40a9ff;
    color: #fff;
}

/* Page 美化 */
.ivu-page {
    text-align: right;
}

.ivu-page-item {
    border-radius: 6px;
    transition: all 0.3s ease;
}

.ivu-page-item:hover {
    background: #1890ff;
    color: #fff;
}

.ivu-page-item-active {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-color: #1890ff;
}

.ivu-page-total {
    color: #8c8c8c;
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
    getPageStudentExamLogs,
    getLoginUser,
    getAllProjects,
} from '../../api/index.js';
export default{
		
    data(){
        return {
            projects: [],
            userInfo: {},
            pageInfos: [],
            pageInfos: [],
            pageIndex: 1,
            pageSize: 10,
            pageTotal: 0,
            totalInfo: 0,
            loading: true,
            qryForm: {
                examName: "",
                studentId: "",
                projectId: "",
            },
            columns: [
                {title: '序号', type: 'index', width: 70, align: 'center'},
                {title: '考试名称', key: 'examName', align: 'center'},
                {title: '考核科目', key: 'projectName', align: 'center'},
                {title: '审核教师', key: 'teacherName', align: 'center'},
                {title: '考试时间', key: 'createTime', align: 'center'},
                {title: '考试结果', slot: 'action', align: 'center'}
            ]
        }
    },
    methods: {

        getPageInfo(pageIndex, pageSize) {
			
            getPageStudentExamLogs(pageIndex, pageSize,
                this.qryForm.examName, this.qryForm.studentId, this.qryForm.projectId).then(resp => {
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
        
        getAllProjects().then(resp =>{

            this.projects = resp.data;
        });
        getLoginUser(this.$store.state.token).then(resp =>{

            this.userInfo = resp.data;
            this.qryForm.studentId = resp.data.id;
            this.getPageInfo(1, this.pageSize);
        });
        
    }
}
</script>