<template>
	<div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-people" class="header-icon" />
                <div class="header-text">
                    <h2>学生管理</h2>
                    <p>管理系统中的所有学生信息</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalInfo }}</div>
                    <div class="stat-label">总学生数</div>
                </div>
            </div>
        </div>

        <Card class="search-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-search" class="title-icon" />
                    <span>信息查询</span>
                </div>
            </template>
			<div class="search-form">
				<Form :model="qryForm" inline class="modern-form">
					<FormItem class="form-item">
						<Input 
                            type="text" 
                            v-model="qryForm.name" 
                            placeholder="学生姓名……"
                            class="modern-input"
                            prefix="ios-person">
                        </Input>
					</FormItem>
					<FormItem class="form-item">
                        <Select 
                            style="width:200px;" 
                            v-model="qryForm.gradeId" 
                            placeholder="选择班级……"
                            class="modern-select" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in grades" 
                                :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                        </Select>
					</FormItem>
					<FormItem class="form-item">
                        <Select 
                            style="width:200px;" 
                            v-model="qryForm.collegeId" 
                            placeholder="选择学院……"
                            class="modern-select" transfer>
                            <Option value="">查看全部</Option>
                            <Option v-for="(item, index) in colleges" 
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
                    <span>学生列表</span>
                    <div class="title-actions">
                        <Button
                            @click="showBatchImport"
                            type="success"
                            class="batch-import-btn btn-ripple">
                            <Icon type="md-cloud-upload" />
                            批量导入
                        </Button>
                        <Button
                            @click="showAddWin()"
                            type="primary"
                            class="add-btn btn-ripple">
                            <Icon type="md-add" />
                            添加学生
                        </Button>
                    </div>
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
						<div class="action-buttons">
                            <Button 
                                size="small" 
                                type="info" 
                                icon="md-create" 
                                @click="showUpdWin(row)"
                                class="action-btn edit-btn">
                                编辑
                            </Button>
							<Button 
                                size="small" 
                                type="warning" 
                                icon="ios-trash" 
                                @click="delInfo(row.id)"
                                class="action-btn delete-btn">
                                删除
                            </Button>
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
			title="添加学生" 
            ok-text="提交" 
            cancel-text="取消" 
            @on-ok="addInfo()"
            class="modern-modal">
            <Form :label-width="80" :model="studentForm" class="modal-form">
                <FormItem label="学生学号">
                    <Input 
                        v-model="studentForm.id" 
                        placeholder="请输入学生学号..."
                        class="modern-input">
                    </Input>
                </FormItem>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="学生账号">
                            <Input 
                                v-model="studentForm.userName" 
                                placeholder="请输入学生账号..."
                                class="modern-input">
                            </Input>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="学生姓名">
                            <Input 
                                v-model="studentForm.name" 
                                placeholder="请输入学生姓名..."
                                class="modern-input">
                            </Input>
                        </FormItem>
                    </Col>
                </Row>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="学生性别">
                            <RadioGroup v-model="studentForm.gender" class="gender-group">
                                <Radio label="男" class="gender-radio">男</Radio>
                                <Radio label="女" class="gender-radio">女</Radio>
                            </RadioGroup>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="学生年龄">
                            <Input 
                                v-model="studentForm.age" 
                                placeholder="请输入学生年龄..."
                                class="modern-input">
                            </Input>
                        </FormItem>
                    </Col>
                </Row>
                <Row :gutter="15">
                    <Col span="12">
                        <FormItem label="所属学院">
                            <Select 
                                v-model="studentForm.collegeId" 
                                placeholder="选择学院……"
                                class="modern-select" transfer>
                                <Option v-for="(item, index) in colleges" 
                                    :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                    <Col span="12">
                        <FormItem label="所属班级">
                            <Select 
                                v-model="studentForm.gradeId" 
                                placeholder="选择班级……"
                                class="modern-select" transfer>
                                <Option v-for="(item, index) in grades" 
                                    :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                            </Select>
                        </FormItem>
                    </Col>
                </Row>
            </Form>
		</Modal>

        <Modal 
            v-model="showUpdFlag"
			title="编辑学生信息" 
            ok-text="提交" 
            cancel-text="取消" 
            @on-ok="updInfo()"
            class="modern-modal">
			<Form :label-width="80" :model="studentForm" class="modal-form">
                <FormItem label="所属学院">
                    <Select 
                        v-model="studentForm.collegeId" 
                        placeholder="选择学院……"
                        class="modern-select" transfer>
                        <Option v-for="(item, index) in colleges" 
                            :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                    </Select>
                </FormItem>
                <FormItem label="所属班级">
                    <Select 
                        v-model="studentForm.gradeId" 
                        placeholder="选择班级……"
                        class="modern-select" transfer>
                        <Option v-for="(item, index) in grades" 
                            :key="index" :value="String(item.id)" :label="String(item.name)">{{ item.name }}</Option>
                    </Select>
                </FormItem>
			</Form>
 		</Modal>

        <!-- 批量导入模态框 -->
        <Modal
            v-model="showBatchImportFlag"
            title="批量导入学生"
            width="800"
            class="batch-import-modal">
            <div class="batch-import-content">
                <div class="import-steps">
                    <Card class="step-card">
                        <template #title>
                            <div class="step-title">
                                <Icon type="ios-download-outline" />
                                步骤1: 下载模板
                            </div>
                        </template>
                        <p class="step-description">首先下载CSV模板文件，按照模板格式填写学生信息</p>
                        <Button
                            type="primary"
                            @click="downloadTemplate"
                            long
                            class="step-btn">
                            <Icon type="md-download" />
                            下载CSV模板
                        </Button>
                    </Card>

                    <Card class="step-card">
                        <template #title>
                            <div class="step-title">
                                <Icon type="ios-create-outline" />
                                步骤2: 填写信息
                            </div>
                        </template>
                        <p class="step-description">按照模板格式填写学生信息，必填字段包括：学号、账号、姓名、学院、班级</p>
                        <div class="template-preview">
                            <pre>学号,账号,姓名,性别,年龄,学院ID,班级ID
2021001,student001,张三,男,20,1,1
2021002,student002,李四,女,19,1,1</pre>
                        </div>
                    </Card>

                    <Card class="step-card">
                        <template #title>
                            <div class="step-title">
                                <Icon type="ios-cloud-upload-outline" />
                                步骤3: 上传文件
                            </div>
                        </template>
                        <p class="step-description">选择填写好的CSV文件上传，系统将自动验证并导入学生信息</p>
                        <Upload
                            :before-upload="handleBatchImport"
                            :show-upload-list="false"
                            action="#"
                            accept=".csv"
                            type="drag"
                            class="upload-area">
                            <div style="padding: 20px 0">
                                <Icon type="ios-cloud-upload" size="52" style="color: #3399ff"></Icon>
                                <p>点击或拖拽文件到此区域上传</p>
                                <p class="upload-hint">仅支持CSV格式，文件大小不超过10MB</p>
                            </div>
                        </Upload>
                    </Card>
                </div>

                <div v-if="importResult" class="import-result">
                    <Alert
                        :type="importResult.success ? 'success' : 'error'"
                        show-icon
                        closable
                        @on-close="importResult = null">
                        <template #title>
                            {{ importResult.success ? '导入完成' : '导入失败' }}
                        </template>
                        <div v-if="importResult.success">
                            <p>成功导入 {{ importResult.data.created }} 名学生</p>
                            <p v-if="importResult.data.failed > 0">
                                失败 {{ importResult.data.failed }} 条
                            </p>
                        </div>
                        <div v-else>
                            <p>{{ importResult.message }}</p>
                        </div>
                    </Alert>
                    <div v-if="importResult && importResult.data && importResult.data.errors && importResult.data.errors.length > 0" class="error-details">
                        <h4>错误详情：</h4>
                        <ul>
                            <li v-for="(error, index) in importResult.data.errors.slice(0, 10)" :key="index">
                                第{{ error.line }}行: {{ error.reason }}
                            </li>
                            <li v-if="importResult.data.errors.length > 10">
                                还有 {{ importResult.data.errors.length - 10 }} 条错误...
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <template #footer>
                <Button @click="showBatchImportFlag = false">关闭</Button>
            </template>
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

.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.action-btn {
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.edit-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    color: #fff;
}

.edit-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
    border: none;
    color: #fff;
}

.delete-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(255, 77, 79, 0.4);
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

.gender-group {
    display: flex;
    gap: 20px;
}

.gender-radio {
    margin-right: 0;
}

.gender-radio .ivu-radio-inner {
    border-radius: 50%;
    border: 2px solid rgba(24, 144, 255, 0.2);
    transition: all 0.3s ease;
}

.gender-radio .ivu-radio-checked .ivu-radio-inner {
    border-color: #1890ff;
    background: #1890ff;
}

.gender-radio .ivu-radio-checked .ivu-radio-inner::after {
    background: #fff;
}

.title-actions {
    display: flex;
    gap: 10px;
    margin-left: auto;
}

.batch-import-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    border: none;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #fff;
}

.batch-import-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

.batch-import-modal .ivu-modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

.batch-import-content {
    padding: 10px 0;
}

.import-steps {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 20px;
}

.step-card {
    border-radius: 8px;
    border: 1px solid #e8e8e8;
    transition: all 0.3s ease;
}

.step-card:hover {
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
    border-color: #1890ff;
}

.step-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: #262626;
}

.step-description {
    color: #595959;
    margin-bottom: 15px;
    line-height: 1.6;
}

.step-btn {
    border-radius: 8px;
    font-weight: 500;
}

.template-preview {
    background: #f5f5f5;
    border-radius: 6px;
    padding: 15px;
    margin-top: 10px;
}

.template-preview pre {
    margin: 0;
    font-size: 12px;
    color: #595959;
    line-height: 1.8;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.upload-area {
    margin-top: 10px;
}

.upload-hint {
    font-size: 12px;
    color: #8c8c8c;
    margin-top: 5px;
}

.import-result {
    margin-top: 20px;
}

.error-details {
    margin-top: 15px;
    padding: 15px;
    background: #fff2f0;
    border-radius: 6px;
    border: 1px solid #ffccc7;
}

.error-details h4 {
    margin: 0 0 10px 0;
    color: #cf1322;
    font-size: 14px;
}

.error-details ul {
    margin: 0;
    padding-left: 20px;
}

.error-details li {
    color: #8c8c8c;
    font-size: 13px;
    line-height: 1.8;
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

    .action-buttons {
        flex-direction: column;
        gap: 5px;
    }
}
</style>

<script>
import {
    getAllColleges,
    getAllGrades,
    getPageStudents,
    addStudents,
    updStudents,
    delStudents,
    batchImportStudents,
    downloadStudentsTemplate,
} from '../../api/index.js';
export default{
		
    data(){
        return {
            colleges: [],
            grades: [],
            pageInfos: [],
            pageIndex: 1,
            pageSize: 10,
            pageTotal: 0,
            totalInfo: 0,
            loading: true,
            showAddFlag: false,
            showUpdFlag: false,
            showBatchImportFlag: false,
            importResult: null,
            qryForm: {
                name: "",
                collegeId: "",
                gradeId: ""
            },
            studentForm: {
                id: "",
                userName: "",
                name: "",
                gender: "",
                age: "",
                collegeId: "",
                gradeId: ""
            },
            columns: [
                {title: '学生学号', key: 'id', align: 'center'},
                {title: '学生账号', key: 'userName', align: 'center'},
                {title: '学生姓名', key: 'name', align: 'center'},
                {title: '学生性别', key: 'gender', align: 'center'},
                {title: '学生年龄', key: 'age', align: 'center'},
                {title: '所属学院', key: 'collegeName', align: 'center'},
                {title: '所属班级', key: 'gradeName', align: 'center'},
                {title: '操作', slot: 'action', align: 'center'}
            ]
        }
    },
    methods:{
			
		getPageInfo(pageIndex, pageSize) {
			
            getPageStudents(pageIndex, pageSize, 
                    this.qryForm.name, this.qryForm.collegeId, this.qryForm.gradeId).then(resp => {
                
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

            this.studentForm = {
                id: "",
                userName: "",
                name: "",
                gender: "",
                age: "",
                collegeId: "",
                gradeId: ""
            };
            this.showAddFlag = true;
        },	
        showUpdWin(row) {
			
            this.studentForm = row;
            this.showUpdFlag = true;
        },
        addInfo() {
			
            addStudents(this.studentForm).then(resp => {
                
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
        
            updStudents(this.studentForm).then(resp => {
        
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
                    delStudents(id).then(resp =>{
                        
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
        },
        showBatchImport() {
            this.showBatchImportFlag = true
            this.importResult = null
        },
        async downloadTemplate() {
            try {
                const resp = await downloadStudentsTemplate()
                const blob = new Blob([resp.data || resp], { type: 'text/csv;charset=utf-8;' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'students_template.csv'
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
                this.$Message.success('模板下载成功')
            } catch (e) {
                console.error('下载模板失败', e)
                this.$Message.error('下载模板失败')
            }
        },
        async handleBatchImport(file) {
            try {
                if (!file.name.endsWith('.csv')) {
                    this.$Message.error('只支持CSV格式文件')
                    return false
                }

                if (file.size > 10 * 1024 * 1024) {
                    this.$Message.error('文件大小不能超过10MB')
                    return false
                }

                const fd = new FormData()
                fd.append('file', file)

                const resp = await batchImportStudents(fd)

                if (resp.code === 0) {
                    this.importResult = {
                        success: true,
                        data: resp.data
                    }
                    this.$Message.success(`导入完成：成功 ${resp.data.created} 条，失败 ${resp.data.failed || 0} 条`)
                    this.getPageInfo(1, this.pageSize)
                } else {
                    this.importResult = {
                        success: false,
                        message: resp.msg || '导入失败'
                    }
                    this.$Message.error(resp.msg || '导入失败')
                }
            } catch (e) {
                console.error('导入失败', e)
                let errorMsg = '导入失败'
                if (e.response) {
                    if (e.response.status === 413) {
                        errorMsg = '文件过大，请上传小于10MB的文件'
                    } else if (e.response.data && e.response.data.msg) {
                        errorMsg = e.response.data.msg
                    }
                } else if (e.message && e.message.includes('Network')) {
                    errorMsg = '网络连接失败，请检查网络后重试'
                }
                this.importResult = {
                    success: false,
                    message: errorMsg
                }
                this.$Message.error(errorMsg)
            }
            return false
        }
    },
    mounted(){

        getAllColleges().then(resp =>{

            this.colleges = resp.data;
        });
        getAllGrades().then(resp =>{

            this.grades = resp.data;
        });
        this.getPageInfo(1, this.pageSize);
    }
}
</script>