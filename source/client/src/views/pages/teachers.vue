<template>
	<div class="fater-body-show">
        <Card>
            <template #title>
				信息查询
			</template>
			<div>
				<Form :model="qryForm" inline>
					<FormItem>
						<Input type="text" v-model="qryForm.name" placeholder="教师姓名……"></Input>
					</FormItem>
					<FormItem>
                        <Select style="width:200px;" v-model="qryForm.job" placeholder="选择职称……" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in jobs" 
                                :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
                        </Select>
					</FormItem>
					<FormItem>
                        <Select style="width:200px;" v-model="qryForm.record" placeholder="选择学历……" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in records" 
                                :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
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
			<template #title>
				<Button @click="showAddWin" type="primary">
					<Icon type="md-add" />
				</Button>
			</template>
			<div>
				<Table border :columns="columns" :loading="loading" :data="pageInfos">
					<template #action="{ row }">
						<Button style="margin-right: 5px;" 
                                size="small" type="info" icon="md-create" @click="showUpdWin(row)"></Button>
						<Button size="small" type="warning" icon="ios-trash" @click="delInfo(row.id)"></Button>
					</template>
				</Table>
				<Page style="margin-top: 15px;" v-if="pageTotal > 1" :current="pageIndex"
					@on-change="handleCurrentChange" :total="totalInfo" show-total/>
			</div>
		</Card>

        <Modal width="700" v-model="showAddFlag"
			title="信息编辑" ok-text="提交" cancel-text="取消" @on-ok="addInfo()">
            <Form :label-width="80" :model="teacherForm">
                <FormItem label="教师工号">
                    <Input v-model="teacherForm.id" placeholder="请输入教师工号..."></Input>
                </FormItem>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="教师账号">
                            <Input v-model="teacherForm.userName" placeholder="请输入教师账号..."></Input>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="教师姓名">
                            <Input v-model="teacherForm.name" placeholder="请输入教师姓名..."></Input>
                        </FormItem>
                    </Col>
                </Row>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="教师性别">
                            <RadioGroup v-model="teacherForm.gender">
                                <Radio label="男">男</Radio>
                                <Radio label="女">女</Radio>
                            </RadioGroup>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="教师年龄">
                            <Input v-model="teacherForm.age" placeholder="请输入教师年龄..."></Input>
                        </FormItem>
                    </Col>
                </Row>
                <FormItem label="联系电话">
                    <Input v-model="teacherForm.phone" placeholder="请输入联系电话..."></Input>
                </FormItem>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="教师职称">
                            <Select v-model="teacherForm.job" placeholder="选择教师职称……" transfer>
                                <Option v-for="(item, index) in jobs" 
                                    :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="教师学历">
                            <Select v-model="teacherForm.record" placeholder="选择教师学历……" transfer>
                                <Option v-for="(item, index) in records" 
                                    :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                </Row>
            </Form>
		</Modal>

        <Modal v-model="showUpdFlag"
			title="信息编辑" ok-text="提交" cancel-text="取消" @on-ok="updInfo()">
			<Form :label-width="80" :model="teacherForm">
                <FormItem label="联系电话">
                    <Input v-model="teacherForm.phone" placeholder="请输入联系电话..."></Input>
                </FormItem>
                <FormItem label="教师职称">
                    <Select v-model="teacherForm.job" placeholder="选择教师职称……" transfer>
                        <Option v-for="(item, index) in jobs" 
                            :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
                    </Select>
                </FormItem>
                <FormItem label="教师学历">
                    <Select v-model="teacherForm.record" placeholder="选择教师学历……" transfer>
                        <Option v-for="(item, index) in records" 
                            :key="index" :value="String(item)" :label="String(item)">{{ item }}</Option>
                    </Select>
                </FormItem>
			</Form>
		</Modal>

    </div>
</template>

<style>
.fater-body-show {
	padding: 20px;
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

/* 页面头部 */
.page-header {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	border-radius: 15px;
	padding: 30px;
	margin-bottom: 20px;
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
}

.header-text p {
	font-size: 14px;
	opacity: 0.9;
	margin: 0;
}

.header-stats {
	display: flex;
	gap: 20px;
}

.stat-item {
	text-align: center;
	padding: 15px 25px;
	background: rgba(255, 255, 255, 0.15);
	border-radius: 10px;
	backdrop-filter: blur(10px);
	min-width: 100px;
}

.stat-number {
	font-size: 28px;
	font-weight: bold;
	margin-bottom: 5px;
}

.stat-label {
	font-size: 12px;
	opacity: 0.9;
}

/* 卡片样式 */
.ivu-card {
	border-radius: 12px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: none;
	margin-bottom: 20px;
	transition: all 0.3s ease;
}

.ivu-card:hover {
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.ivu-card-head {
	border-bottom: 2px solid #f0f0f0;
	padding: 16px 20px;
}

.ivu-card-body {
	padding: 20px;
}

/* 卡片标题 */
.card-title {
	display: flex;
	align-items: center;
	gap: 10px;
	font-size: 16px;
	font-weight: 600;
	color: #333;
}

.title-icon {
	font-size: 18px;
	color: #1890ff;
}

/* 搜索表单 */
.search-form .ivu-form-item {
	margin-right: 20px;
	margin-bottom: 0;
}

.search-form .ivu-input,
.search-form .ivu-select {
	border-radius: 8px;
	transition: all 0.3s ease;
}

.search-form .ivu-input:focus,
.search-form .ivu-select-focused {
	border-color: #1890ff;
	box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 按钮样式 */
.search-btn {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	border: none;
	border-radius: 8px;
	padding: 8px 20px;
	font-weight: 500;
	transition: all 0.3s ease;
}

.search-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.add-btn {
	background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
	border: none;
	border-radius: 8px;
	font-weight: 500;
	transition: all 0.3s ease;
}

.add-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

/* 表格样式 */
.ivu-table {
	border-radius: 8px;
	overflow: hidden;
}

.ivu-table th {
	background: #f8f9fa;
	font-weight: 600;
	color: #333;
}

.ivu-table td {
	transition: background-color 0.3s ease;
}

.ivu-table tr:hover td {
	background-color: rgba(24, 144, 255, 0.05) !important;
}

/* 分页样式 */
.ivu-page {
	text-align: center;
	margin-top: 20px;
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

/* 模态框样式 */
.ivu-modal-header {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	color: #fff;
	border-radius: 12px 12px 0 0;
}

.ivu-modal-header-inner {
	color: #fff;
	font-weight: 600;
}

.ivu-modal-body {
	padding: 24px;
}

.ivu-modal-footer {
	border-top: 1px solid #f0f0f0;
	padding: 16px 24px;
}

/* 表单样式 */
.form-item .ivu-input,
.form-item .ivu-select {
	border-radius: 8px;
	transition: all 0.3s ease;
}

.form-item .ivu-input:focus,
.form-item .ivu-select-focused {
	border-color: #1890ff;
	box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 单选按钮组 */
.ivu-radio-group {
	display: flex;
	gap: 20px;
}

.ivu-radio-wrapper {
	margin-right: 0;
}

.ivu-radio-checked .ivu-radio-inner {
	border-color: #1890ff;
	background: #1890ff;
}

/* 操作按钮 */
.action-btn {
	border-radius: 6px;
	transition: all 0.3s ease;
}

.action-btn-edit {
	background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
	border: none;
}

.action-btn-edit:hover {
	transform: translateY(-1px);
	box-shadow: 0 3px 8px rgba(24, 144, 255, 0.3);
}

.action-btn-delete {
	background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
	border: none;
}

.action-btn-delete:hover {
	transform: translateY(-1px);
	box-shadow: 0 3px 8px rgba(255, 77, 79, 0.3);
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	height: 300px;
	background: #fafafa;
	border-radius: 8px;
	color: #8c8c8c;
}

.empty-state .ivu-icon {
	font-size: 64px;
	margin-bottom: 16px;
	opacity: 0.5;
}

.empty-title {
	font-size: 16px;
	font-weight: 500;
	margin-bottom: 8px;
}

.empty-desc {
	font-size: 14px;
	color: #8c8c8c;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.fater-body-show {
		padding: 15px;
	}

	.page-header {
		flex-direction: column;
		gap: 20px;
		padding: 20px;
	}

	.header-stats {
		width: 100%;
		justify-content: space-around;
	}

	.stat-item {
		padding: 10px 15px;
		min-width: auto;
		flex: 1;
	}

	.search-form .ivu-form-item {
		margin-right: 0;
		margin-bottom: 15px;
		width: 100%;
	}
}
</style>

<script>
import {
    getPageTeachers,
    addTeachers,
    updTeachers,
    delTeachers,
} from '../../api/index.js';
export default{
		
    data(){
        return {
            records: ["专科", "本科", "研究生", "其他"],
            jobs: ["普通教员", "助理讲师", "中级讲师", "高级讲师"],
            pageInfos: [],
            pageIndex: 1,
            pageSize: 10,
            pageTotal: 0,
            totalInfo: 0,
            loading: true,
            showAddFlag: false,
            showUpdFlag: false,
            qryForm: {
                name: "",
                record: "",
                job: ""
            },
            teacherForm: {
                id: "",
                userName: "",
                name: "",
                gender: "",
                age: "",
                phone: "",
                record: "",
                job: ""
            },
            columns: [
                {title: '教师工号', key: 'id', align: 'center'},
                {title: '教师账号', key: 'userName', align: 'center'},
                {title: '教师姓名', key: 'name', align: 'center'},
                {title: '教师性别', key: 'gender', align: 'center'},
                {title: '教师年龄', key: 'age', align: 'center'},
                {title: '联系电话', key: 'phone', align: 'center'},
                {title: '教师学历', key: 'record', align: 'center'},
                {title: '教师职称', key: 'job', align: 'center'},
                {title: '操作', slot: 'action', align: 'center'}
            ]
        }
    },
    methods:{
			
		getPageInfo(pageIndex, pageSize) {
			
            getPageTeachers(pageIndex, pageSize, 
                    this.qryForm.name, this.qryForm.record, this.qryForm.job).then(resp => {
                
                this.pageInfos = resp.data.data;
                this.pageIndex = resp.data.pageIndex;
                this.pageSize = resp.data.pageSize;
                this.pageTotal = resp.data.pageTotal;
                this.totalInfo = resp.data.count;
        
                this.loading = false;
            });
        },
        handleCurrentChange(pageIndex) {
        
            this.getPageInfo(pageIndex, this.pageSize);
        },
        showAddWin(){

            this.teacherForm = {
                id: "",
                userName: "",
                name: "",
                gender: "",
                age: "",
                phone: "",
                record: "",
                job: ""
            };
            this.showAddFlag = true;
        },	
        showUpdWin(row) {
			
            this.teacherForm = row;
            this.showUpdFlag = true;
        },
        addInfo() {
			
            addTeachers(this.teacherForm).then(resp => {
                
                if(resp.code == 0){

                    this.$Notice.success({
                        duration: 3,
                        title: resp.msg
                    });
                    
                    this.getPageInfo(1, this.pageSize);
                    
                    this.showAddFlag = false;
                }else{

                    this.$Notice.warning({
                        duration: 3,
                        title: resp.msg
                    });
                }
            });
        },
        updInfo() {
        
            updTeachers(this.teacherForm).then(resp => {
        
                this.$Notice.success({
                    duration: 3,
                    title: resp.msg
                });
        
                this.getPageInfo(1, this.pageSize);
        
                this.showUpdFlag = false;
            });
        },
        delInfo(id){

            this.$Modal.confirm({
                title: '系统提示',
                content: '即将删除相关信息, 是否继续?',
                onOk: () => {
                    delTeachers(id).then(resp =>{
                        
                        if(resp.code == 0){
                            this.$Notice.success({
                                duration: 3,
                                title: resp.msg
                            });
                            
                            this.getPageInfo(1, this.pageSize);
                        }else{
                            
                            this.$Notice.warning({
                                duration: 3,
                                title: resp.msg
                            });
                        }
                    });
                },
            });
        }		
    },
    mounted(){

        this.getPageInfo(1, this.pageSize);
    }
}
</script>