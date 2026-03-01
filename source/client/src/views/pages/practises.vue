<template>
	<div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-book" class="header-icon" />
                <div class="header-text">
                    <h2>练习试卷</h2>
                    <p>选择试卷进行练习，提升学习效果</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalPapers }}</div>
                    <div class="stat-label">试卷总数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ completedPapers }}</div>
                    <div class="stat-label">已完成</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ avgScore }}</div>
                    <div class="stat-label">平均分</div>
                </div>
                <div>
                    <Button type="primary" @click="showWrongDialog=true" style="margin-left:16px">错题专项</Button>
                    <Button @click="downloadPracticeLogs" style="margin-left:8px">导出练习记录</Button>
                </div>
            </div>
        </div>

        <Card class="filter-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-search" class="title-icon" />
                    <span>试卷筛选</span>
                </div>
			</template>
            <div class="filter-form">
                <Form :model="filterForm" inline class="modern-form">
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.paperType" 
                            placeholder="试卷类型"
                            class="modern-select" transfer>
                            <Option value="">全部类型</Option>
                            <Option value="fixed">固定试卷</Option>
                            <Option value="timed">时段试卷</Option>
                        </Select>
					</FormItem>
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.projectId" 
                            placeholder="选择科目"
                            class="modern-select" transfer>
                            <Option value="">全部科目</Option>
                            <Option v-for="project in projects" 
                                :key="project.id" 
                                :value="String(project.id)" :label="String(project.name)">{{ project.name }}</Option>
                        </Select>
					</FormItem>
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.difficulty" 
                            placeholder="难度等级"
                            class="modern-select" transfer>
                            <Option value="">全部难度</Option>
                            <Option value="easy">简单</Option>
                            <Option value="medium">中等</Option>
                            <Option value="hard">困难</Option>
                        </Select>
					</FormItem>
                    <FormItem class="form-item">
                        <Button 
                            type="primary" 
                            @click="filterPapers()"
                            class="filter-btn btn-ripple">
							<Icon type="ios-search" />
                            筛选
						</Button>
					</FormItem>
				</Form>
			</div>
		</Card>

        <div class="papers-grid animate-fade-in-up delay-200">
            <Card 
                v-for="paper in filteredPapers" 
                :key="paper.id" 
                class="paper-card"
                :class="{ 'completed': paper.status === 'completed' }">
			<template #title>
                    <div class="paper-header">
                        <div class="paper-info">
                            <Tag :type="getPaperTypeTag(paper.type)" class="type-tag">
                                {{ getPaperTypeText(paper.type) }}
                            </Tag>
                            <Tag :type="getDifficultyTag(paper.difficulty)" class="difficulty-tag">
                                {{ getDifficultyText(paper.difficulty) }}
                            </Tag>
                            <span class="paper-title">{{ paper.title }}</span>
                        </div>
                        <div class="paper-meta">
                            <span class="project-name">{{ paper.projectName }}</span>
                            <span class="create-time">{{ paper.createTime }}</span>
                        </div>
                    </div>
			</template>
                
                <div class="paper-content">
                    <div class="paper-description">
                        <p>{{ paper.description }}</p>
			</div>
                    
                    <div class="paper-details">
                        <div class="detail-item">
                            <Icon type="ios-ribbon" />
                            <span>科目：{{ paper.projectName }}</span>
                        </div>
                        <div class="detail-item">
                            <Icon type="ios-time" />
                            <span>时长：{{ paper.duration }}分钟</span>
                        </div>
                        <div class="detail-item">
                            <Icon type="ios-list" />
                            <span>题目：{{ paper.questionCount }}道</span>
                        </div>
                        <div class="detail-item">
                            <Icon type="ios-star" />
                            <span>总分：{{ paper.totalScore }}分</span>
                        </div>
                    </div>

                    <div v-if="paper.status === 'completed'" class="result-section">
                        <Divider>练习结果</Divider>
                        <div class="result-info">
                            <div class="result-item">
                                <span class="label">得分：</span>
                                <span class="score">{{ paper.score }}分</span>
                            </div>
                            <div class="result-item">
                                <span class="label">用时：</span>
                                <span class="time">{{ paper.usedTime }}分钟</span>
                            </div>
                            <div class="result-item">
                                <span class="label">正确率：</span>
                                <span class="accuracy">{{ paper.accuracy }}%</span>
                            </div>
                        </div>
                    </div>

                    <div class="paper-actions">
                        <Button 
                            v-if="paper.status === 'not_started'"
                            type="primary" 
                            @click="startPractice(paper)"
                            class="start-btn btn-ripple"
                            :loading="loading">
                            <Icon type="ios-play" />
                            开始练习
                        </Button>
                        <Button
                            v-else-if="paper.status === 'in_progress'"
                            type="warning"
                            @click="continuePractice(paper)"
                            class="continue-btn btn-ripple"
                            :loading="loading">
                            <Icon type="ios-play" />
                            继续练习
                        </Button>
                        <Button
                            v-else-if="paper.logId"
                            type="success"
                            @click="reviewPaper(paper)"
                            class="review-btn btn-ripple">
                            <Icon type="ios-eye" />
                            查看结果
                    </Button>
                        <Button
                            @click="showPaperDetail(paper)"
                            class="detail-btn btn-ripple">
                            <Icon type="ios-information" />
                            试卷详情
                    </Button>
                    </div>
                </div>
            </Card>
        </div>

        <!-- 试卷详情模态框 -->
        <Modal v-model="showDetailModal" title="试卷详情" width="700">
            <div v-if="selectedPaper" class="paper-detail">
                <h3>{{ selectedPaper.title }}</h3>
                <p class="detail-description">{{ selectedPaper.description }}</p>
                
                <Divider>试卷信息</Divider>
                <div class="detail-info">
                    <p><strong>试卷类型：</strong>{{ getPaperTypeText(selectedPaper.type) }}</p>
                    <p><strong>难度等级：</strong>{{ getDifficultyText(selectedPaper.difficulty) }}</p>
                    <p><strong>练习时长：</strong>{{ selectedPaper.duration }}分钟</p>
                    <p><strong>题目数量：</strong>{{ selectedPaper.questionCount }}道</p>
                    <p><strong>总分值：</strong>{{ selectedPaper.totalScore }}分</p>
                </div>

                <Divider>题目分布</Divider>
                <div class="question-distribution">
                    <div v-for="(count, type) in selectedPaper.questionDistribution" :key="type" class="dist-item">
                        <span class="type-name">{{ getQuestionTypeText(type) }}：</span>
                        <span class="type-count">{{ count }}道</span>
                    </div>
                </div>

                <Divider>注意事项</Divider>
                <ul class="notes">
                    <li>练习过程中可以随时保存进度</li>
                    <li>完成后可以查看详细解析</li>
                    <li>支持重复练习提升成绩</li>
                </ul>
            </div>
        </Modal>

        <!-- 错题专项生成弹窗 -->
        <Modal v-model="showWrongDialog" title="生成错题专项练习" width="520" @on-ok="generateWrong">
            <Form :label-width="90">
                <FormItem label="所属科目">
                    <Select v-model="wrongForm.projectId" placeholder="（可选）选择限定科目" clearable>
                        <Option v-for="p in projects" :key="p.id" :value="String(p.id)" :label="String(p.name)">{{ p.name }}</Option>
                    </Select>
                </FormItem>
                <FormItem label="题目数量">
                    <InputNumber v-model="wrongForm.limit" :min="1" :max="50" />
                </FormItem>
            </Form>
        </Modal>
    </div>
</template>

<style scoped>
.page-header {
    margin-bottom: 24px;
    padding: 24px;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 12px;
    color: #000;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.header-icon {
    font-size: 32px;
    color: #000;
}

.header-text h2 {
    margin: 0 0 8px 0;
    font-size: 28px;
    font-weight: 600;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
}

.header-stats {
    display: flex;
    gap: 24px;
}

.stat-item {
    text-align: center;
    background: rgba(255, 255, 255, 0.1);
    padding: 16px 24px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    opacity: 0.9;
}

.filter-card {
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
}

.title-icon {
    color: #1890ff;
}

.filter-form {
    padding: 20px 0;
}

.modern-form {
    display: flex;
    align-items: center;
    gap: 16px;
}

.form-item {
    margin-bottom: 0;
}

.modern-select {
    width: 180px;
}

.filter-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    height: 36px;
    padding: 0 20px;
    border-radius: 8px;
}

.papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
    gap: 24px;
}

.paper-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.paper-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.paper-card.completed {
    border-color: #1890ff;
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
}

.paper-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.paper-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    flex: 1;
}

.type-tag,
.difficulty-tag {
    font-weight: 600;
}

.paper-title {
    color: #262626;
}

.paper-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    font-size: 12px;
    color: #8c8c8c;
}

.project-name {
    background: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
}

.paper-content {
    padding: 16px 0;
}

.paper-description p {
    color: #595959;
    line-height: 1.6;
    margin-bottom: 20px;
}

.paper-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #8c8c8c;
    font-size: 14px;
}

.result-section {
    margin-bottom: 20px;
}

.result-info {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.result-item {
    text-align: center;
    padding: 12px;
    background: #f0f8ff;
    border-radius: 8px;
}

.result-item .label {
    display: block;
    color: #8c8c8c;
    font-size: 12px;
    margin-bottom: 4px;
}

.result-item .score {
    color: #1890ff;
    font-size: 18px;
    font-weight: 600;
}

.result-item .time {
    color: #1890ff;
    font-size: 18px;
    font-weight: 600;
}

.result-item .accuracy {
    color: #fa8c16;
    font-size: 18px;
    font-weight: 600;
}

.paper-actions {
    display: flex;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
}

.start-btn,
.continue-btn,
.review-btn,
.detail-btn {
    height: 36px;
    padding: 0 16px;
    border-radius: 8px;
    font-size: 14px;
}

.start-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
}

.continue-btn {
    background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
    border: none;
}

.review-btn {
    background: #1890ff;
    border: none;
}

.detail-btn {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #6c757d;
}

.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.paper-detail h3 {
    color: #262626;
    margin-bottom: 16px;
}

.detail-description {
    color: #595959;
    line-height: 1.6;
    margin-bottom: 20px;
}

.detail-info p {
    margin-bottom: 8px;
    color: #595959;
}

.question-distribution {
    margin-bottom: 20px;
}

.dist-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.type-name {
    color: #8c8c8c;
}

.type-count {
    color: #1890ff;
    font-weight: 600;
}

.notes {
    color: #595959;
    padding-left: 20px;
}

.notes li {
    margin-bottom: 8px;
}

.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.animate-fade-in-up.delay-100 {
    animation-delay: 0.1s;
}

.animate-fade-in-up.delay-200 {
    animation-delay: 0.2s;
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
</style>

<script>
import { getAllProjects, getStudentPracticePapers, startPractice as apiStartPractice, submitPractice as apiSubmitPractice, generateWrongPracticePaper, exportPracticeLogs } from '../../api/index.js';
import { triggerBlobDownload } from '../../utils/fileDownload';

export default {
    name: 'Practises',
    data() {
        return {
            projects: [],
            papers: [],
            showDetailModal: false,
            selectedPaper: null,
            showWrongDialog: false,
            wrongForm: { projectId: '', limit: 10 },
            filterForm: {
                paperType: '',
                projectId: '',
                difficulty: ''
            },
            loading: false,
            currentPracticeLog: null
        };
    },
    computed: {
        filteredPapers() {
            let filtered = this.papers;
            
            if (this.filterForm.paperType) {
                filtered = filtered.filter(p => p.type === this.filterForm.paperType);
            }
            
            if (this.filterForm.projectId) {
                filtered = filtered.filter(p => p.projectId == this.filterForm.projectId);
            }
            
            if (this.filterForm.difficulty) {
                filtered = filtered.filter(p => p.difficulty === this.filterForm.difficulty);
            }
            
            return filtered;
        },
        totalPapers() {
            return this.papers.length;
        },
        completedPapers() {
            return this.papers.filter(p => p.status === 'completed').length;
        },
        avgScore() {
            const completed = this.papers.filter(p => p.status === 'completed');
            if (completed.length === 0) return 0;
            const totalScore = completed.reduce((sum, p) => sum + p.score, 0);
            return Math.round(totalScore / completed.length);
        }
    },
    methods: {
        filterPapers() {
            console.log('筛选条件：', this.filterForm);
        },
        
        async startPractice(paper) {
            try {
                this.loading = true;
                
                // 调用API开始练习
                const token = this.$store.state.token || sessionStorage.getItem('token');
                const response = await apiStartPractice(token, paper.id);
                
                if (response.code === 0) {
                    this.currentPracticeLog = response.data.logId;
                    
                    if (response.data && response.data.message === '继续现有练习') {
                        this.$Modal.confirm({
                            title: '继续练习',
                            content: '检测到您有未完成的练习，是否继续？',
                            onOk: () => {
                                this.continuePractice(paper);
                            }
                        });
                    } else {
                        // 开始新练习
                        this.initializePractice(paper);
                    }
                } else {
                    this.$Message.error(response.msg || '开始练习失败');
                }
            } catch (error) {
                console.error('开始练习失败:', error);
                this.$Message.error('开始练习失败，请重试');
            } finally {
                this.loading = false;
            }
        },

        async generateWrong() {
            try {
                const token = this.$store.state.token || sessionStorage.getItem('token');
                const resp = await generateWrongPracticePaper(token, this.wrongForm.projectId || null, this.wrongForm.limit || 10);
                if (resp.code === 0) {
                    this.$Message.success('生成成功，正在进入练习...');
                    // 直接开始该练习
                    const start = await apiStartPractice(token, resp.data.paperId);
                    if (start.code === 0) {
                        this.currentPracticeLog = start.data.logId;
                        this.$router.push({
                            name: 'answer',
                            query: { type: 'practice', paperId: resp.data.paperId, mode: 'fixed', logId: this.currentPracticeLog }
                        });
                    } else {
                        this.$Message.warning(start.msg || '进入练习失败');
                        this.loadPracticePapers();
                    }
                } else {
                    this.$Message.error(resp.msg || '生成错题专项失败');
                }
            } catch (e) {
                console.error('生成错题专项失败', e);
                this.$Message.error('生成错题专项失败，请重试');
            } finally {
                this.showWrongDialog = false;
            }
        },

        async downloadPracticeLogs(){
            try{
                const token = this.$store.state.token || sessionStorage.getItem('token');
                const resp = await exportPracticeLogs(token)
                triggerBlobDownload(resp.data || resp, 'practice_logs.csv', 'text/csv;charset=utf-8;')
            }catch(e){
                console.error('导出失败', e)
                this.$Message.error('导出练习记录失败')
            }
        },
        
        continuePractice(paper) {
            // 继续练习，跳转到答题页面
            this.$router.push({
                name: 'answer',
                query: { 
                    type: 'practice',
                    paperId: paper.id,
                    mode: paper.type,
                    logId: this.currentPracticeLog,
                    resume: 'true'
                }
            });
        },
        
        reviewPaper(paper) {
            // 显示练习结果
            this.showPracticeResult(paper);
        },
        
        async initializePractice(paper) {
            this.$Message.loading({
                content: '正在加载试卷...',
                duration: 0
            });
            
            try {
                // 跳转到答题页面
                this.$router.push({
                    name: 'answer',
                    query: { 
                        type: 'practice',
                        paperId: paper.id,
                        mode: paper.type,
                        logId: this.currentPracticeLog
                    }
                });
            } catch (error) {
                console.error('初始化练习失败:', error);
                this.$Message.error('初始化练习失败，请重试');
            } finally {
                this.$Message.destroy();
            }
        },
        
        showPracticeResult(paper) {
            this.$Modal.info({
                title: '练习结果',
                content: `
                    <div style="text-align: center; padding: 20px;">
                        <h3>${paper.title}</h3>
                        <div style="margin: 20px 0;">
                            <p><strong>得分：</strong><span style="color: #1890ff; font-size: 18px;">${paper.score}分</span></p>
                            <p><strong>用时：</strong><span style="color: #1890ff; font-size: 18px;">${paper.usedTime}分钟</span></p>
                            <p><strong>正确率：</strong><span style="color: #fa8c16; font-size: 18px;">${paper.accuracy}%</span></p>
                        </div>
                        <p>点击"查看详情"可以查看每道题的解析</p>
                    </div>
                `,
                okText: '查看详情',
                onOk: () => {
                    // 只有在有logId时才跳转到结果详情页面
                    if (paper.logId) {
                        this.$router.push({
                            name: 'practiceResult',
                            query: {
                                paperId: paper.id,
                                logId: paper.logId
                            }
                        });
                    } else {
                        this.$Message.warning('暂无练习记录，请先完成练习');
                    }
                }
            });
        },
        
        showPaperDetail(paper) {
            this.selectedPaper = paper;
            this.showDetailModal = true;
        },
        
        getPaperTypeTag(type) {
            const tags = {
                'fixed': 'success',
                'timed': 'warning'
            };
            return tags[type] || 'default';
        },
        
        getPaperTypeText(type) {
            const texts = {
                'fixed': '固定试卷',
                'timed': '时段试卷'
            };
            return texts[type] || '未知类型';
        },
        
        getDifficultyTag(difficulty) {
            const tags = {
                'easy': 'success',
                'medium': 'warning',
                'hard': 'error'
            };
            return tags[difficulty] || 'default';
        },
        
        getDifficultyText(difficulty) {
            const texts = {
                'easy': '简单',
                'medium': '中等',
                'hard': '困难'
            };
            return texts[difficulty] || '未知';
        },
        
        getQuestionTypeText(type) {
            const texts = {
                0: '选择题',
                1: '填空题',
                2: '判断题',
                3: '编程题'
            };
            return texts[type] || '未知类型';
        },
        
        async loadProjects() {
            try {
                const response = await getAllProjects();
                if (response.code === 0) {
                    this.projects = response.data;
                }
            } catch (error) {
                console.error('加载科目失败:', error);
            }
        },
        
        async loadPracticePapers() {
            try {
                this.loading = true;
                const token = this.$store.state.token || sessionStorage.getItem('token');
                const response = await getStudentPracticePapers(token);
                
                if (response.code === 0) {
                    this.papers = response.data;
                } else {
                    this.$Message.error(response.msg || '加载练习试卷失败');
                }
            } catch (error) {
                console.error('加载练习试卷失败:', error);
                this.$Message.error('加载练习试卷失败，请重试');
            } finally {
                this.loading = false;
            }
        }
    },
    
    async mounted() {
        await this.loadProjects();
        await this.loadPracticePapers();
        // 如果是从错题本跳转过来，自动弹出错题专项对话框
        if (this.$route.query && this.$route.query.wrongPractice === '1') {
            this.showWrongDialog = true;
        }
    }
};
</script>