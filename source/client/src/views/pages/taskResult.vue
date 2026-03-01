<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-trophy" class="header-icon" />
                <div class="header-text">
                    <h2>任务结果</h2>
                    <p>恭喜你完成了任务！</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item score">
                    <div class="stat-number">{{ taskResult.score }}</div>
                    <div class="stat-label">得分</div>
                </div>
                <div class="stat-item accuracy">
                    <div class="stat-number">{{ taskResult.accuracy }}%</div>
                    <div class="stat-label">正确率</div>
                </div>
                <div class="stat-item time">
                    <div class="stat-number">{{ taskResult.usedTime }}分钟</div>
                    <div class="stat-label">用时</div>
                </div>
            </div>
        </div>

        <Card class="result-summary animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-information-circle" class="title-icon" />
                    <span>任务总结</span>
                </div>
            </template>
            <div class="summary-content">
                <div class="summary-item">
                    <span class="label">任务名称：</span>
                    <span class="value">{{ taskInfo.title }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">任务描述：</span>
                    <span class="value">{{ taskInfo.description }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">科目：</span>
                    <span class="value">{{ taskInfo.projectName }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">年级：</span>
                    <span class="value">{{ taskInfo.gradeName }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">开始时间：</span>
                    <span class="value">{{ formatTime(taskResult.startTime) }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">完成时间：</span>
                    <span class="value">{{ formatTime(taskResult.endTime) }}</span>
                </div>
                <div class="summary-item">
                    <span class="label">答题情况：</span>
                    <span class="value">{{ taskResult.correctCount }}/{{ taskResult.totalCount }} 题正确</span>
                </div>
            </div>
        </Card>

        <Card class="answers-review animate-fade-in-up delay-200">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-list" class="title-icon" />
                    <span>答题回顾</span>
                </div>
            </template>
            <div class="answers-list">
                <div 
                    v-for="(answer, index) in answers" 
                    :key="answer.id" 
                    class="answer-item"
                    :class="{ 'correct': answer.isCorrect, 'incorrect': !answer.isCorrect }">
                    <div class="question-header">
                        <div class="question-number">第{{ index + 1 }}题</div>
                        <div class="question-type">{{ getQuestionTypeText(answer.questionType) }}</div>
                        <div class="question-score">
                            <Icon :type="answer.isCorrect ? 'ios-checkmark-circle' : 'ios-close-circle'" />
                            {{ answer.score }}分
                        </div>
                    </div>
                    
                    <div class="question-content">
                        <div class="question-text"><QuestionContentRenderer :content="answer.questionContent" /></div>
                        
                        <!-- 选择题选项 -->
                        <div v-if="answer.questionType === 0 && answer.options" class="options-list">
                            <div 
                                v-for="(option, optIndex) in answer.options" 
                                :key="optIndex"
                                class="option-item"
                                :class="{ 
                                    'selected': option === answer.studentAnswer,
                                    'correct': option === answer.correctAnswer 
                                }">
                                <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
                                <span class="option-text">{{ option }}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="answer-details">
                        <div class="answer-item">
                            <span class="label">你的答案：</span>
                            <span class="value" :class="{ 'correct': answer.isCorrect, 'incorrect': !answer.isCorrect }">
                                <QuestionContentRenderer :content="answer.studentAnswer || '未作答'" compact />
                            </span>
                        </div>
                        <div class="answer-item">
                            <span class="label">正确答案：</span>
                            <span class="value correct"><QuestionContentRenderer :content="answer.correctAnswer" compact /></span>
                        </div>
                        <div v-if="answer.analyse" class="answer-item">
                            <span class="label">解析：</span>
                            <span class="value analyse"><QuestionContentRenderer :content="answer.analyse" compact /></span>
                        </div>
                        <div v-if="answer.aiConfidence !== null || answer.aiFeedback || answer.aiAnalysis" class="answer-item">
                            <span class="label">AI评分：</span>
                            <span class="value">
                                <div style="display:flex;flex-direction:column;gap:6px;">
                                    <div>
                                        <span>置信度：</span>
                                        <Tag :type="(answer.aiConfidence||0) < 0.6 ? 'warning' : 'success'">
                                            {{ Math.round(((answer.aiConfidence||0) * 100)) }}%
                                        </Tag>
                                        <Tag type="warning" v-if="answer.needsReview" style="margin-left:8px;">待人工覆核</Tag>
                                        <span v-if="answer.aiModel" style="margin-left:12px;color:#888;">模型：{{ answer.aiModel }}</span>
                                    </div>
                                    <div v-if="answer.aiFeedback">
                                        <span style="color:#888;">反馈：</span><QuestionContentRenderer :content="answer.aiFeedback" compact />
                                    </div>
                                    <div v-if="answer.aiAnalysis">
                                        <span style="color:#888;">分析：</span><QuestionContentRenderer :content="answer.aiAnalysis" compact />
                                    </div>
                                    <div v-if="answer.needsReview">
                                        <Button size="small" type="warning" @click="openReview(answer)">人工覆核</Button>
                                    </div>
                                </div>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </Card>

        <Modal v-model="reviewModal.visible" title="人工覆核" @on-ok="submitReview" @on-cancel="closeReview">
            <Form :label-width="80">
                <FormItem label="分数">
                    <Input v-model="reviewModal.form.score" placeholder="请输入分数" />
                </FormItem>
                <FormItem label="是否正确">
                    <i-switch v-model="reviewModal.form.isCorrect" />
                </FormItem>
                <FormItem label="反馈">
                    <Input v-model="reviewModal.form.feedback" type="textarea" :autosize="{minRows:2,maxRows:4}" />
                </FormItem>
                <FormItem label="分析">
                    <Input v-model="reviewModal.form.analysis" type="textarea" :autosize="{minRows:2,maxRows:4}" />
                </FormItem>
            </Form>
        </Modal>

        <div class="action-buttons animate-fade-in-up delay-300">
            <Button 
                type="primary" 
                @click="goToTaskCenter"
                class="action-btn btn-ripple">
                <Icon type="ios-list-box" />
                返回任务中心
            </Button>
            <Button 
                type="success" 
                @click="goToWrongQuestions"
                class="action-btn btn-ripple">
                <Icon type="ios-alert" />
                查看错题本
            </Button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
            <Spin size="large">
                <Icon type="ios-loading" class="spin-icon-load"></Icon>
                <div class="spin-text">加载中...</div>
            </Spin>
        </div>
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

.stat-item.score {
    background: rgba(255, 255, 255, 0.15);
}

.stat-item.accuracy {
    background: rgba(255, 255, 255, 0.12);
}

.stat-item.time {
    background: rgba(255, 255, 255, 0.1);
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

.result-summary,
.answers-review {
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

.summary-content {
    padding: 20px 0;
}

.summary-item {
    display: flex;
    margin-bottom: 16px;
    align-items: flex-start;
}

.summary-item .label {
    width: 120px;
    font-weight: 600;
    color: #595959;
    flex-shrink: 0;
}

.summary-item .value {
    color: #262626;
    flex: 1;
}

.answers-list {
    padding: 20px 0;
}

.answer-item {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.answer-item.correct {
    border-color: #1890ff;
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
}

.answer-item.incorrect {
    border-color: #ff4d4f;
    background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.question-number {
    font-size: 18px;
    font-weight: 600;
    color: #262626;
}

.question-type {
    background: #f0f0f0;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    color: #666;
}

.question-score {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #1890ff;
}

.question-score .ivu-icon {
    font-size: 18px;
}

.question-content {
    margin-bottom: 20px;
}

.question-text {
    font-size: 16px;
    color: #262626;
    line-height: 1.6;
    margin-bottom: 16px;
}

.options-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.option-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
}

.option-item.selected {
    background: #e6f7ff;
    border-color: #1890ff;
}

.option-item.correct {
    background: #f6ffed;
    border-color: #1890ff;
}

.option-label {
    font-weight: 600;
    color: #1890ff;
    min-width: 20px;
}

.option-text {
    color: #262626;
}

.answer-details {
    background: rgba(255, 255, 255, 0.5);
    padding: 16px;
    border-radius: 6px;
}

.answer-item {
    display: flex;
    margin-bottom: 8px;
    align-items: flex-start;
}

.answer-item:last-child {
    margin-bottom: 0;
}

.answer-item .label {
    width: 100px;
    font-weight: 600;
    color: #595959;
    flex-shrink: 0;
}

.answer-item .value {
    flex: 1;
    color: #262626;
}

.answer-item .value.correct {
    color: #1890ff;
    font-weight: 600;
}

.answer-item .value.incorrect {
    color: #ff4d4f;
    font-weight: 600;
}

.answer-item .value.analyse {
    color: #722ed1;
    font-style: italic;
}

.action-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 32px;
}

.action-btn {
    height: 48px;
    padding: 0 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
}

.action-btn.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.action-btn.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* 加载状态样式 */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.spin-icon-load {
    animation: spin-rotate 1s infinite linear;
}

.spin-text {
    margin-top: 8px;
    color: #666;
}

@keyframes spin-rotate {
    100% {
        transform: rotate(360deg);
    }
}

/* 动画效果 */
.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.animate-fade-in-up.delay-100 {
    animation-delay: 0.1s;
}

.animate-fade-in-up.delay-200 {
    animation-delay: 0.2s;
}

.animate-fade-in-up.delay-300 {
    animation-delay: 0.3s;
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
import { getTaskInfo, getTaskAnswers, getTaskLogInfo } from '../../api/index.js';
import http from '../../utils/http.js';
import QuestionContentRenderer from '@/components/QuestionContentRenderer.vue';

export default {
    name: 'TaskResult',
    components: {
        QuestionContentRenderer
    },
    data() {
        return {
            loading: false,
            taskId: null,
            logId: null,
            taskInfo: {},
            taskResult: {},
            answers: [],
            reviewModal: {
                visible: false,
                answerId: null,
                form: {
                    score: '',
                    isCorrect: false,
                    feedback: '',
                    analysis: ''
                }
            }
        };
    },
    methods: {
        // 加载任务信息
        loadTaskInfo() {
            if (!this.taskId) return;
            
            this.loading = true;
            getTaskInfo(this.taskId).then(resp => {
                if (resp.code === 0) {
                    this.taskInfo = resp.data;
                } else {
                    this.$Message.error(resp.msg || '加载任务信息失败');
                }
            }).catch(error => {
                console.error('加载任务信息失败:', error);
                this.$Message.error('加载任务信息失败，请检查网络连接');
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 加载答题记录和任务结果概览
        loadAnswers() {
            if (!this.logId) return;
            
            this.loading = true;
            
            // 先获取任务日志信息
            getTaskLogInfo(this.logId).then(resp => {
                if (resp.code === 0) {
                    this.taskResult = {
                        score: resp.data.score || 0,
                        accuracy: resp.data.accuracy || 0,
                        usedTime: resp.data.usedTime || 0,
                        correctCount: resp.data.correctCount || 0,
                        totalCount: resp.data.totalCount || 0,
                        startTime: resp.data.startTime,
                        endTime: resp.data.endTime
                    };
                } else {
                    this.$Message.error(resp.msg || '加载任务结果失败');
                }
            }).catch(error => {
                console.error('加载任务结果失败:', error);
                this.$Message.error('加载任务结果失败，请检查网络连接');
            });
            
            // 再获取答题记录
            getTaskAnswers(this.logId).then(resp => {
                if (resp.code === 0) {
                    this.answers = resp.data;
                } else {
                    this.$Message.error(resp.msg || '加载答题记录失败');
                }
            }).catch(error => {
                console.error('加载答题记录失败:', error);
                this.$Message.error('加载答题记录失败，请检查网络连接');
            }).finally(() => {
                this.loading = false;
            });
        },
        
        // 格式化时间
        formatTime(timeStr) {
            if (!timeStr) return '未知';
            const date = new Date(timeStr);
            return date.toLocaleString('zh-CN');
        },
        
        // 获取题目类型文本
        getQuestionTypeText(type) {
            const types = {
                0: '单选题',
                1: '多选题',
                2: '判断题',
                3: '填空题',
                4: '简答题'
            };
            return types[type] || '未知类型';
        },
        
        // 返回任务中心
        goToTaskCenter() {
            this.$router.push('/home/taskCenter');
        },
        
        // 查看错题本
        goToWrongQuestions() {
            this.$router.push('/home/wrongQuestions');
        },
        openReview(answer){
            this.reviewModal.visible = true;
            this.reviewModal.answerId = answer.id;
            this.reviewModal.form = {
                score: String(answer.score || ''),
                isCorrect: !!answer.isCorrect,
                feedback: answer.aiFeedback || '',
                analysis: answer.aiAnalysis || ''
            };
        },
        closeReview(){
            this.reviewModal.visible = false;
        },
        async submitReview(){
            try{
                const payload = new URLSearchParams();
                payload.append('id', this.reviewModal.answerId);
                if(this.reviewModal.form.score !== '') payload.append('score', this.reviewModal.form.score);
                payload.append('isCorrect', this.reviewModal.form.isCorrect ? 'true' : 'false');
                if(this.reviewModal.form.feedback) payload.append('feedback', this.reviewModal.form.feedback);
                if(this.reviewModal.form.analysis) payload.append('analysis', this.reviewModal.form.analysis);
                await http.post('/tasks/review/', payload);
                this.$Message.success('覆核成功');
                this.reviewModal.visible = false;
                // 重新加载答案
                this.loadAnswers();
            }catch(e){
                this.$Message.error('覆核失败');
            }
        }
    },
    mounted() {
        // 从路由参数获取任务ID和记录ID
        this.taskId = this.$route.query.taskId;
        this.logId = this.$route.query.logId;
        
        if (!this.taskId || !this.logId) {
            this.$Message.error('缺少必要参数');
            this.$router.push('/home/taskCenter');
            return;
        }
        
        // 加载数据
        this.loadTaskInfo();
        this.loadAnswers();
    }
};
</script>
