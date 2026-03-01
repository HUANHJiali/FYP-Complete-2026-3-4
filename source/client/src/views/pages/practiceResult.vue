<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-checkmark-circle" class="header-icon" />
                <div class="header-text">
                    <h2>练习结果详情</h2>
                    <p>{{ paperTitle }} - 练习完成</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ result.score }}</div>
                    <div class="stat-label">得分</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ result.accuracy }}%</div>
                    <div class="stat-label">正确率</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ result.usedTime }}分钟</div>
                    <div class="stat-label">用时</div>
                </div>
                <div>
                    <Button @click="exportAnswers" icon="ios-cloud-download">导出答题明细</Button>
                </div>
            </div>
        </div>

        <Card class="result-summary animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-stats" class="title-icon" />
                    <span>练习总结</span>
                </div>
            </template>
            <div class="summary-content">
                <Row :gutter="24">
                    <Col span="8">
                        <div class="summary-item">
                            <div class="item-label">总题数</div>
                            <div class="item-value">{{ result.totalCount }}</div>
                        </div>
                    </Col>
                    <Col span="8">
                        <div class="summary-item">
                            <div class="item-label">正确题数</div>
                            <div class="item-value correct">{{ result.correctCount }}</div>
                        </div>
                    </Col>
                    <Col span="8">
                        <div class="summary-item">
                            <div class="item-label">错误题数</div>
                            <div class="item-value incorrect">{{ result.totalCount - result.correctCount }}</div>
                        </div>
                    </Col>
                </Row>
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
                        <span class="question-number">第{{ index + 1 }}题</span>
                        <Tag :type="getQuestionTypeTag(answer.questionType)" class="type-tag">
                            {{ getQuestionTypeText(answer.questionType) }}
                        </Tag>
                        <span class="score-info">
                            得分：<span class="score">{{ answer.score }}</span>
                        </span>
                    </div>
                    
                    <div class="question-content">
                        <div class="content-text"><QuestionContentRenderer :content="answer.questionContent" /></div>
                        <div v-if="answer.options && answer.options.length > 0" class="options-list">
                            <div 
                                v-for="(option, optIndex) in answer.options" 
                                :key="optIndex"
                                class="option-item"
                                :class="{ 
                                    'selected': answer.studentAnswer == option.id,
                                    'correct': answer.correctAnswer == option.id 
                                }">
                                {{ String.fromCharCode(65 + optIndex) }}. {{ option.name }}
                            </div>
                        </div>
                    </div>
                    
                    <div class="answer-section">
                        <div class="answer-row">
                            <span class="label">您的答案：</span>
                            <span class="value student-answer">{{ formatAnswer(answer.studentAnswer, answer.questionType, answer.options) }}</span>
                        </div>
                        <div class="answer-row">
                            <span class="label">正确答案：</span>
                            <span class="value correct-answer">{{ formatAnswer(answer.correctAnswer, answer.questionType, answer.options) }}</span>
                        </div>
                        <div v-if="answer.analyse" class="answer-row">
                            <span class="label">题目解析：</span>
                            <span class="value analyse"><QuestionContentRenderer :content="answer.analyse" compact /></span>
                        </div>
                        <div v-if="answer.aiConfidence !== null || answer.aiFeedback || answer.aiAnalysis" class="answer-row">
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
                @click="goBack"
                class="btn-ripple">
                <Icon type="ios-arrow-back" />
                返回练习列表
            </Button>
            <Button 
                @click="retryPractice"
                class="btn-ripple">
                <Icon type="ios-refresh" />
                重新练习
            </Button>
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

.stat-number {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    opacity: 0.9;
}

.result-summary {
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
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.item-label {
    color: #8c8c8c;
    font-size: 14px;
    margin-bottom: 8px;
}

.item-value {
    font-size: 24px;
    font-weight: 700;
    color: #262626;
}

.item-value.correct {
    color: #1890ff;
}

.item-value.incorrect {
    color: #ff4d4f;
}

.answers-review {
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.answers-list {
    padding: 20px 0;
}

.answer-item {
    padding: 20px;
    margin-bottom: 20px;
    border: 2px solid #f0f0f0;
    border-radius: 8px;
    background: #fff;
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
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.question-number {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
}

.type-tag {
    font-weight: 600;
}

.score-info {
    margin-left: auto;
    color: #8c8c8c;
}

.score {
    color: #1890ff;
    font-weight: 600;
}

.question-content {
    margin-bottom: 20px;
}

.content-text {
    font-size: 16px;
    line-height: 1.6;
    color: #262626;
    margin-bottom: 16px;
}

.options-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

.option-item {
    padding: 12px 16px;
    border: 2px solid #e9ecef;
    border-radius: 6px;
    background: #fff;
    font-size: 14px;
    transition: all 0.3s ease;
}

.option-item.selected {
    border-color: #1890ff;
    background: #e6f7ff;
}

.option-item.correct {
    border-color: #1890ff;
    background: #f6ffed;
}

.answer-section {
    border-top: 1px solid #f0f0f0;
    padding-top: 16px;
}

.answer-row {
    display: flex;
    margin-bottom: 12px;
    align-items: flex-start;
}

.answer-row .label {
    width: 100px;
    font-weight: 600;
    color: #8c8c8c;
    flex-shrink: 0;
}

.answer-row .value {
    flex: 1;
    color: #262626;
}

.student-answer {
    color: #1890ff;
}

.correct-answer {
    color: #1890ff;
}

.analyse {
    color: #fa8c16;
    font-style: italic;
}

.action-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    padding: 24px 0;
}

.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    height: 40px;
    padding: 0 24px;
    border-radius: 8px;
}

.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
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
import { getPracticeAnswers } from '../../api/index.js';
import http from '../../utils/http.js';
import QuestionContentRenderer from '@/components/QuestionContentRenderer.vue';
import { triggerBlobDownload } from '@/utils/fileDownload';

export default {
    name: 'PracticeResult',
    components: {
        QuestionContentRenderer
    },
    data() {
        return {
            logId: null,
            paperId: null,
            paperTitle: '',
            result: {
                score: 0,
                accuracy: 0,
                usedTime: 0,
                correctCount: 0,
                totalCount: 0
            },
            answers: [],
            loading: false,
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
        async loadPracticeResult() {
            try {
                this.loading = true;
                
                // 从路由参数获取练习记录ID
                this.logId = this.$route.query.logId;
                this.paperId = this.$route.query.paperId;
                
                if (!this.logId) {
                    this.$Message.error('缺少练习记录ID');
                    return;
                }
                
                // 获取练习答题记录
                const response = await getPracticeAnswers(this.logId);
                
                if (response.code === 0) {
                    this.answers = response.data;
                    this.calculateResult();
                } else {
                    this.$Message.error(response.msg || '加载练习结果失败');
                }
            } catch (error) {
                console.error('加载练习结果失败:', error);
                this.$Message.error('加载练习结果失败，请重试');
            } finally {
                this.loading = false;
            }
        },

        async exportAnswers(){
            try{
                const api = await import('../../api/index.js')
                const resp = await api.exportPracticeAnswers(this.logId)
                const data = resp.data || resp
                triggerBlobDownload(data, 'practice_answers.csv', 'text/csv;charset=utf-8;')
            }catch(e){
                console.error('导出答题明细失败', e)
                this.$Message.error('导出答题明细失败')
            }
        },
        
        calculateResult() {
            if (this.answers.length === 0) return;
            
            const correctCount = this.answers.filter(a => a.isCorrect).length;
            const totalScore = this.answers.reduce((sum, a) => sum + a.score, 0);
            
            this.result = {
                score: totalScore,
                accuracy: Math.round((correctCount / this.answers.length) * 100),
                usedTime: 0, // 这个值应该从练习记录中获取
                correctCount: correctCount,
                totalCount: this.answers.length
            };
        },
        
        getQuestionTypeTag(type) {
            const tags = {
                0: 'primary',   // 选择题
                1: 'success',   // 填空题
                2: 'warning',   // 判断题
                3: 'error'      // 编程题
            };
            return tags[type] || 'default';
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
        
        formatAnswer(answer, type, options) {
            if (type === 0 && options && options.length > 0) {
                // 选择题：通过选项ID找到对应选项，显示为字母+选项名
                const idx = options.findIndex(opt => String(opt.id) === String(answer));
                if (idx >= 0) {
                    return String.fromCharCode(65 + idx) + '. ' + options[idx].name;
                }
                return answer || '未作答';
            }
            return answer || '未作答';
        },
        
        goBack() {
            this.$router.push('/practises');
        },
        
        retryPractice() {
            this.$router.push({
                name: 'answer',
                query: { 
                    type: 'practice',
                    paperId: this.paperId,
                    mode: 'fixed'
                }
            });
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
                await http.post('/studentpractice/review/', payload);
                this.$Message.success('覆核成功');
                this.reviewModal.visible = false;
                // 重新加载
                this.loadPracticeResult();
            }catch(e){
                this.$Message.error('覆核失败');
            }
        }
    },
    
    async mounted() {
        await this.loadPracticeResult();
    }
};
</script>
