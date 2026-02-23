<template>
    <div class="fater-answer-panle">
        <!-- 顶部工具栏 -->
        <div class="fater-answer-toolbar">
            <Button type="error" ghost @click="confirmExit" icon="ios-close-circle">
                退出考试
            </Button>
            <div class="toolbar-info">
                <span class="exam-name">{{ examInfo.name }}</span>
                <span class="exam-time">{{ examInfo.examTime }}</span>
            </div>
            <Button type="primary" ghost @click="showHelpModal = true" icon="ios-help-circle-outline">
                帮助
            </Button>
        </div>

        <!-- 帮助模态框 -->
        <Modal
            v-model="showHelpModal"
            title="考试帮助"
            width="520"
            :footer-hide="true">
            <div class="help-content">
                <div class="help-section">
                    <h3><Icon type="ios-book-outline" /> 答题操作</h3>
                    <ul>
                        <li>点击左侧题号切换题目</li>
                        <li>选择答案后会自动保存</li>
                        <li>使用快捷键可提高效率</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h3><Icon type="ios-keypad" /> 快捷键</h3>
                    <ul class="shortcut-list">
                        <li><kbd>←</kbd> <kbd>→</kbd> 切换上一题/下一题</li>
                        <li><kbd>1</kbd>-<kbd>9</kbd> 快速跳转到指定题目</li>
                        <li><kbd>Ctrl</kbd>+<kbd>S</kbd> 手动保存答案</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h3><Icon type="ios-time-outline" /> 注意事项</h3>
                    <ul>
                        <li>注意考试倒计时，合理安排时间</li>
                        <li>时间结束前 5 分钟会收到提醒</li>
                        <li>可以随时退出，答案会自动保存</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h3><Icon type="ios-call-outline" /> 遇到问题？</h3>
                    <p>如有技术问题，请联系监考老师或管理员</p>
                </div>
            </div>
        </Modal>
        <div class="fater-answer-left">
            <div class="fater-answer-time">
                倒计时  {{ countDown.text }}
            </div>
            <!-- 答题进度 -->
            <div class="fater-answer-progress">
                <div class="progress-header">
                    <span class="progress-title">答题进度</span>
                    <span class="progress-text">{{ completedCount }} / {{ totalCount }}</span>
                </div>
                <Progress
                    :percent="progressPercent"
                    :stroke-color="progressColor"
                    :show-info="false"
                    stroke-width="8"
                />
            </div>
            <div class="fater-answer-select-list">
                <Divider>选择题</Divider>
                <Row class="fater-answer-select-item" :gutter="15">
                    <Col v-for="(item, index) in p_list_0" :key="index" span="6">
                        <Button
                            @click="getItem(item.id, item.no)"
                            :class="getButtonClass(item)"
                            :type="getButtonType(item)">
                            {{ item.no }}
                        </Button>
                    </Col>
                </Row>
                <Divider>填空题</Divider>
                <Row class="fater-answer-select-item" :gutter="15">
                    <Col v-for="(item, index) in p_list_1" :key="index" span="6">
                        <Button
                            @click="getItem(item.id, item.no)"
                            :class="getButtonClass(item)"
                            :type="getButtonType(item)">
                            {{ item.no }}
                        </Button>
                    </Col>
                </Row>
                <Divider>判断题</Divider>
                <Row class="fater-answer-select-item" :gutter="15">
                    <Col v-for="(item, index) in p_list_2" :key="index" span="6">
                        <Button
                            @click="getItem(item.id, item.no)"
                            :class="getButtonClass(item)"
                            :type="getButtonType(item)">
                            {{ item.no }}
                        </Button>
                    </Col>
                </Row>
                <Divider>编程题</Divider>
                <Row class="fater-answer-select-item" :gutter="15">
                    <Col v-for="(item, index) in p_list_3" :key="index" span="6">
                        <Button
                            @click="getItem(item.id, item.no)"
                            :class="getButtonClass(item)"
                            :type="getButtonType(item)">
                            {{ item.no }}
                        </Button>
                    </Col>
                </Row>
            </div>
            <div class="fater-answer-flag">
                仔细阅读，认真答题，遵守考试纪律
            </div>
        </div>
        <div class="fater-answer-right">
            <div class="fater-answer-info">
                <div class="fater-answer-info-item">
                    <span>学生学号：</span>
                    <span>{{ userInfo.id }}</span>
                </div>
                <div class="fater-answer-info-item">
                    <span>学生姓名：</span>
                    <span>{{ userInfo.name }}</span>
                </div>
                <div class="fater-answer-info-item">
                    <span>学生性别：</span>
                    <span>{{ userInfo.gender }}</span>
                </div>
                <div class="fater-answer-info-item">
                    <span>所属学院：</span>
                    <span>{{ userInfo.collegeName }}</span>
                </div>
                <div class="fater-answer-info-item">
                    <span>所在班级：</span>
                    <span>{{ userInfo.gradeName }}</span>
                </div>
            </div>
            <div class="fater-answer-body">
                <div class="fater-answer-practise" v-if="practise && practise.id">
                    {{ practise.no }}. {{ practise.name }}
                </div>
                <div class="fater-answer-input">
                    <RadioGroup v-if="practise.type==0" v-model="practise.answer" vertical>
                        <Radio v-for="(item, index) in practise.options" 
                                :key="index" :label="item.id">{{ item.name }}</Radio>
                    </RadioGroup>
                    <Input v-else-if="practise.type==1" 
                            v-model="practise.answer" placeholder="输入正确答案..."/>
                    <RadioGroup v-else-if="practise.type==2" v-model="practise.answer">
                        <Radio label="正确">正确</Radio>
                        <Radio label="错误">错误</Radio>
                    </RadioGroup>
                    <Input v-else-if="practise.type==3" type="textarea" 
                           :rows="15" v-model="practise.answer" placeholder="输入正确答案..."/>
                    <div v-else class="empty-state">
                        <Icon type="ios-document-outline" size="64" color="#bfbfbf" />
                        <p class="empty-title">暂无题目</p>
                        <p class="empty-desc">该考试尚未配置题目，请联系监考老师或管理员</p>
                        <Button type="primary" @click="goBack" icon="ios-arrow-back">
                            返回
                        </Button>
                    </div>
                </div>
            </div>
            <div class="fater-answer-foot">
                <div class="fater-answer-foot-desc">
                    本次针对{{ examInfo.gradeName }}{{ examInfo.projectName }}考试, 其中选择题10道(每道2分), 填空题10道(每道2分),
                    判断题10道(每道2分), 编程题2道(每道20分), 考试时间120分钟, 满分100分
                </div>
                <div class="fater-answer-foot-subbtn">
                    <Button @click="subAnswers()" type="primary">交卷</Button>
                </div>
            </div>
        </div>
        <div style="clear:both"></div>
    </div>
</template>

<style scoped>
/* 主容器顶部内边距 - 避免被工具栏遮挡 */
.fater-answer-panle {
    padding-top: 60px;
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

/* 顶部工具栏 */
.fater-answer-toolbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.95) 0%, rgba(0, 80, 179, 0.95) 100%);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    z-index: 1000;
}

.toolbar-info {
    display: flex;
    align-items: center;
    gap: 16px;
}

.exam-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
}

.exam-time {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
}

/* 答题进度样式 */
.fater-answer-progress {
    padding: 20px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.15);
    border: 1px solid rgba(24, 144, 255, 0.1);
    transition: all 0.3s ease;
}

.fater-answer-progress:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.25);
    transform: translateY(-2px);
}

.progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.progress-title {
    font-size: 14px;
    color: #262626;
    font-weight: 600;
}

.progress-text {
    font-size: 16px;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

/* 题目按钮状态 */
.question-btn.answered {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    border-color: #52c41a;
    color: #fff;
    box-shadow: 0 2px 8px rgba(82, 196, 26, 0.3);
    transition: all 0.3s ease;
}

.question-btn.answered:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

.question-btn.current {
    box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.3);
    border-color: #1890ff;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: #fff;
    transform: scale(1.05);
}

.question-btn.answered.current {
    box-shadow: 0 0 0 3px rgba(82, 196, 26, 0.3);
    transform: scale(1.05);
}

/* 帮助模态框样式 */
.help-content {
    padding: 8px 0;
}

.help-section {
    margin-bottom: 24px;
    padding: 16px;
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    border-radius: 8px;
    border-left: 4px solid #1890ff;
    transition: all 0.3s ease;
}

.help-section:hover {
    background: linear-gradient(135deg, #e6f7ff 0%, #fff 100%);
    transform: translateX(4px);
}

.help-section:last-child {
    margin-bottom: 0;
}

.help-section h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1890ff;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.help-section h3 .ivu-icon {
    color: #1890ff;
    font-size: 18px;
}

.help-section ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.help-section ul li {
    padding: 6px 0;
    color: #595959;
    font-size: 14px;
    line-height: 1.6;
}

.help-section ul li:before {
    content: "•";
    color: #1890ff;
    font-weight: bold;
    display: inline-block;
    width: 1em;
    margin-left: -1em;
}

.help-section .shortcut-list li {
    display: flex;
    align-items: center;
    gap: 8px;
}

.help-section kbd {
    display: inline-block;
    padding: 2px 8px;
    font-size: 11px;
    line-height: 1.4;
    color: #262626;
    vertical-align: middle;
    background-color: #f5f5f5;
    border: 1px solid #d9d9d9;
    border-radius: 3px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.2);
    font-family: monospace;
    min-width: 24px;
    text-align: center;
}

.help-section p {
    color: #595959;
    font-size: 14px;
    line-height: 1.6;
}

/* 空状态样式 */
.empty-state {
    text-align: center;
    padding: 80px 40px;
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    border-radius: 12px;
    margin: 20px 0;
    border: 2px dashed rgba(24, 144, 255, 0.2);
    transition: all 0.3s ease;
}

.empty-state:hover {
    border-color: rgba(24, 144, 255, 0.4);
}

.empty-state .ivu-icon {
    margin-bottom: 16px;
    color: #1890ff;
}

.empty-title {
    font-size: 18px;
    font-weight: 600;
    color: #262626;
    margin: 16px 0 8px;
}

.empty-desc {
    font-size: 14px;
    color: #8c8c8c;
    margin-bottom: 24px;
    line-height: 1.6;
}
</style>

<script>
import {
    getPractiseInfo,
    makeExams,
    getExamInfo,
    getLoginUser,
    addAnswerLog,
    getPracticePaperQuestions,
    getPracticePaperInfo,
    submitPractice
} from '../../api/index.js';
import {
    countDown,
    formatCountDown,
    contrastCountDown,
    formatDate
} from '../../utils/date.js';
export default{
    data(){
        return {
            userInfo: {},
            p_list_0: [],
            p_list_1: [],
            p_list_2: [],
            p_list_3: [],
            examInfo: {},
            countDown: {
                text: "",
                startTime: "",
                endTime: ""
            },
            practise: {
                no: 1,
                id: "",
                name: "",
                answer: null,
                type: "",
                options: [],
            },
            showHelpModal: false,
            timer: null  // 定时器引用，用于清��
        }
    },
    computed: {
        // 已完成题目数量
        completedCount() {
            let count = 0;
            [...this.p_list_0, ...this.p_list_1, ...this.p_list_2, ...this.p_list_3].forEach(item => {
                if (item.answer && item.answer !== '') {
                    count++;
                }
            });
            return count;
        },
        // 总题目数量
        totalCount() {
            return this.p_list_0.length + this.p_list_1.length + this.p_list_2.length + this.p_list_3.length;
        },
        // 进度百分比
        progressPercent() {
            if (this.totalCount === 0) return 0;
            return Math.round((this.completedCount / this.totalCount) * 100);
        },
        // 进度条颜色
        progressColor() {
            const percent = this.progressPercent;
            if (percent < 30) return '#ff4d4f';
            if (percent < 60) return '#faad14';
            if (percent < 100) return '#1890ff';
            return '#52c41a';
        }
    },
    methods: {
        
        getAnswerIsNull(){

            let resl = [];

            this.p_list_0.forEach(item =>{

                if(item.answer){

                }else{
                    resl.push(item.no);
                }
            });
            this.p_list_1.forEach(item =>{

                if(item.answer){

                }else{
                    resl.push(item.no);
                }
            });
            this.p_list_2.forEach(item =>{

                if(item.answer){

                }else{
                    resl.push(item.no);
                }
            });
            this.p_list_3.forEach(item =>{

                if(item.answer){

                }else{
                    resl.push(item.no);
                }
            });

            return resl;
        },
        // 提取实际提交逻辑为独立方法（带重试机制）
        async doSubmit(retryCount = 0){
            const MAX_RETRY = 2
            let answers=[], nos=[], practiseIds=[];
            this.p_list_0.forEach(item =>{
                answers.push(item.answer);
                nos.push(item.no);
                practiseIds.push(item.id);
            });
            this.p_list_1.forEach(item =>{
                answers.push(item.answer);
                nos.push(item.no);
                practiseIds.push(item.id);
            });
            this.p_list_2.forEach(item =>{
                answers.push(item.answer);
                nos.push(item.no);
                practiseIds.push(item.id);
            });
            this.p_list_3.forEach(item =>{
                answers.push(item.answer);
                nos.push(item.no);
                practiseIds.push(item.id);
            });

            // 本地保存答案作为备份
            const storageKey = `exam_${this.$route.query.id}_backup`
            sessionStorage.setItem(storageKey, JSON.stringify({ answers, nos, practiseIds }))

            try {
                const resp = await addAnswerLog({
                    token: this.$store.state.token || sessionStorage.getItem('token'),
                    examId: this.$route.query.id,
                    answers: answers,
                    nos: nos,
                    practiseIds: practiseIds
                })

                this.$Notice.success({
                    title: '交卷成功',
                    desc: '试卷已提交，请耐心等待教师审核结果'
                });
                this.$router.push('/welcome');

                // 清除备份
                sessionStorage.removeItem(storageKey)
            } catch (err) {
                const msg = (err && err.msg) ? err.msg : '提交失败'

                // 网络错误，尝试重试
                if (retryCount < MAX_RETRY && (!err.response || err.response.status >= 500)) {
                    this.$Message.warning(`提交失败，正在重试 (${retryCount + 1}/${MAX_RETRY})...`)
                    setTimeout(() => {
                        this.doSubmit(retryCount + 1)
                    }, 2000)
                    return
                }

                // 重试失败，显示提示
                this.$Modal.error({
                    title: '提交失败',
                    content: `${msg}\n\n您的答案已保存在本地，您可以稍后重新登录从"我的记录"进入查看并重新提交。`,
                    okText: '我知道了'
                })

                // 保存到本地存储以便恢复
                sessionStorage.setItem(`exam_${this.$route.query.id}_draft`, JSON.stringify({ answers, nos, practiseIds }))
            }
        },
        subAnswers(){
            let answersIsNull = this.getAnswerIsNull();
            const totalCount = this.p_list_0.length + this.p_list_1.length + this.p_list_2.length + this.p_list_3.length;
            const answeredCount = totalCount - answersIsNull.length;

            // 无论是否完成，都显示确认对话框
            if(answersIsNull.length > 0){
                // 有未完成题目
                this.$Modal.confirm({
                    title: '还有题目未完成',
                    content: `您已完成 ${answeredCount} 题，还有 ${answersIsNull.length} 题未完成（第 ${answersIsNull.join('、')} 题）。确定要交卷吗？`,
                    okText: '强制交卷',
                    cancelText: '继续答题',
                    onOk: () => {
                        this.doSubmit();
                    }
                });
            } else {
                // 全部完成
                this.$Modal.confirm({
                    title: '确认交卷？',
                    content: `您已完成全部 ${answeredCount} 道题目，交卷后将无法修改答案。确定要提交吗？`,
                    okText: '确认交卷',
                    cancelText: '再检查一下',
                    onOk: () => {
                        this.doSubmit();
                    }
                });
            }
        },
        getItem(id, no){

            getPractiseInfo(id).then(resp =>{

                if(resp.data.type == 0){

                    let temp = this.p_list_0[no-1];
                    // 使用 Object.assign 保持对象引用，只更新属性
                    Object.assign(this.practise, {
                        token: this.$store.state.token || sessionStorage.getItem('token'),
                        examId: this.$route.query.id,
                        no: no,
                        id: resp.data.id,
                        name: resp.data.name,
                        answer: temp.answer ? temp.answer : null,
                        type: resp.data.type,
                        options: resp.data.options,
                    });
                }else if(resp.data.type == 1){

                    let temp = this.p_list_1[no-1-10];
                    // 使用 Object.assign 保持对象引用，只更新属性
                    Object.assign(this.practise, {
                        token: this.$store.state.token || sessionStorage.getItem('token'),
                        examId: this.$route.query.id,
                        no: no,
                        id: resp.data.id,
                        name: resp.data.name,
                        answer: temp.answer ? temp.answer : null,
                        type: resp.data.type,
                        options: [],  // 清空选项
                    });
                }else if(resp.data.type == 2){

                    let temp = this.p_list_2[no-1-20];
                    // 使用 Object.assign 保持对象引用，只更新属性
                    Object.assign(this.practise, {
                        token: this.$store.state.token || sessionStorage.getItem('token'),
                        examId: this.$route.query.id,
                        no: no,
                        id: resp.data.id,
                        name: resp.data.name,
                        answer: temp.answer ? temp.answer : null,
                        type: resp.data.type,
                        options: [],  // 清空选项
                    });
                }else if(resp.data.type == 3){

                    let temp = this.p_list_3[no-1-30];
                    // 使用 Object.assign 保持对象引用，只更新属性
                    Object.assign(this.practise, {
                        token: this.$store.state.token || sessionStorage.getItem('token'),
                        examId: this.$route.query.id,
                        no: no,
                        id: resp.data.id,
                        name: resp.data.name,
                        answer: temp.answer ? temp.answer : null,
                        type: resp.data.type,
                        options: [],  // 清空选项
                    });
                }
            });
        },
        initCountDown(){

            let temp1 = new Date();
            this.countDown.startTime = formatDate(temp1);
            let temp2 = new Date();
            temp1.setTime(temp2.getTime() + 1000*60*60*2);
            this.countDown.endTime = formatDate(temp1);
        },
        // 获取按钮类型
        getButtonType(item) {
            // 如果是当前题目，返回 primary
            if (this.practise && item.id === this.practise.id) {
                return 'primary';
            }
            // 如果已答题，返回 default
            if (item.answer && item.answer !== '') {
                return 'default';
            }
            // 未答题，返回 ghost
            return 'ghost';
        },
        // 获取按钮自定义类名
        getButtonClass(item) {
            let classes = ['question-btn'];

            // 是否为当前题目
            if (this.practise && item.id === this.practise.id) {
                classes.push('current');
            }

            // 是否已答题
            if (item.answer && item.answer !== '') {
                classes.push('answered');
            }

            return classes.join(' ');
        },
        // 保存答案到 sessionStorage
        saveAnswer(practise) {
            if (!practise || !practise.id) return;

            const storageKey = `exam_${this.$route.query.id}_answers`;
            const answers = JSON.parse(sessionStorage.getItem(storageKey) || '{}');
            answers[practise.id] = practise.answer;
            sessionStorage.setItem(storageKey, JSON.stringify(answers));
        },
        // 从 sessionStorage 恢复答案
        restoreAnswers() {
            const storageKey = `exam_${this.$route.query.id}_answers`;
            const savedAnswers = JSON.parse(sessionStorage.getItem(storageKey) || '{}');

            // 恢复选择题答案
            this.p_list_0.forEach(item => {
                if (savedAnswers[item.id]) {
                    item.answer = savedAnswers[item.id];
                }
            });

            // 恢复填空题答案
            this.p_list_1.forEach(item => {
                if (savedAnswers[item.id]) {
                    item.answer = savedAnswers[item.id];
                }
            });

            // 恢复判断题答案
            this.p_list_2.forEach(item => {
                if (savedAnswers[item.id]) {
                    item.answer = savedAnswers[item.id];
                }
            });

            // 恢复编程题答案
            this.p_list_3.forEach(item => {
                if (savedAnswers[item.id]) {
                    item.answer = savedAnswers[item.id];
                }
            });
        },
        // 确认退出考试
        confirmExit() {
            const answeredCount = this.completedCount;
            const totalCount = this.totalCount;

            this.$Modal.confirm({
                title: '确认退出考试？',
                content: `您已完成 ${answeredCount}/${totalCount} 题。退出后答题进度将被保存，可以重新进入继续答题。确定要退出吗？`,
                okText: '确认退出',
                cancelText: '继续答题',
                onOk: () => {
                    this.$router.push('/exams');
                }
            });
        },
        // 获取所有题目列表（合并）
        getAllQuestions() {
            return [
                ...this.p_list_0,
                ...this.p_list_1,
                ...this.p_list_2,
                ...this.p_list_3
            ];
        },
        // 获取当前题目索引
        getCurrentQuestionIndex() {
            if (!this.practise || !this.practise.no) return -1;
            return this.practise.no - 1;
        },
        // 上一题
        previousQuestion() {
            const currentIndex = this.getCurrentQuestionIndex();
            if (currentIndex > 0) {
                const prevQuestion = this.getAllQuestions()[currentIndex - 1];
                this.getItem(prevQuestion.id, prevQuestion.no);
            }
        },
        // 下一题
        nextQuestion() {
            const currentIndex = this.getCurrentQuestionIndex();
            const allQuestions = this.getAllQuestions();
            if (currentIndex < allQuestions.length - 1) {
                const nextQuestion = this.getAllQuestions()[currentIndex + 1];
                this.getItem(nextQuestion.id, nextQuestion.no);
            }
        },
        // 跳转到指定题目
        jumpToQuestion(questionNum) {
            const allQuestions = this.getAllQuestions();
            if (questionNum >= 1 && questionNum <= allQuestions.length) {
                const question = allQuestions[questionNum - 1];
                this.getItem(question.id, question.no);
            }
        },
        // 处理键盘事件
        handleKeyPress(e) {
            // 如果在输入框中，不响应快捷键
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                // Ctrl + S 除外
                if (!(e.ctrlKey && e.key === 's')) {
                    return;
                }
            }

            // 左箭头：上一题
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.previousQuestion();
            }

            // 右箭头：下一题
            if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.nextQuestion();
            }

            // Ctrl + S：保存答案（提供反馈）
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveAnswer(this.practise);
                this.$Message.success('答案已保存');
            }

            // 数字键 1-9：快速跳转
            if (/^[1-9]$/.test(e.key)) {
                const questionNum = parseInt(e.key);
                const allQuestions = this.getAllQuestions();
                if (questionNum <= allQuestions.length) {
                    e.preventDefault();
                    this.jumpToQuestion(questionNum);
                }
            }
        },
        // 返回上一页
        goBack() {
            this.$router.push('/exams');
        }
    },
    watch: {

        practise(newVal, oldVal){

            // 保存旧题目的答案
            if (oldVal && oldVal.id) {
                this.saveAnswer(oldVal);
            }

            // 更新列表中的答案
            if(oldVal && oldVal.type == 0){

                (this.p_list_0[oldVal.no-1])['answer'] = oldVal['answer'] ? oldVal['answer'] : null;
            }else if(oldVal && oldVal.type == 1){

                (this.p_list_1[oldVal.no-1-10])['answer'] = oldVal['answer'] ? oldVal['answer'] : null;
            }else if(oldVal && oldVal.type == 2){

                (this.p_list_2[oldVal.no-1-20])['answer'] = oldVal['answer'] ? oldVal['answer'] : null;
            }else if(oldVal && oldVal.type == 3){

                (this.p_list_3[oldVal.no-1-30])['answer'] = oldVal['answer'] ? oldVal['answer'] : null;
            }
        },

        // 加载练习试卷
        loadPracticePaper(paperId) {
            getPracticePaperInfo(paperId).then(resp => {
                this.examInfo = {
                    name: resp.data.title,
                    examTime: resp.data.duration + '分钟',
                    projectId: resp.data.projectId
                };

                // 获取练习试卷的题目
                getPracticePaperQuestions(paperId).then(qres => {
                    const questions = qres.data || [];
                    let questionNo = 1;

                    questions.forEach((q, index) => {
                        const questionData = {
                            no: questionNo,
                            id: q.practiseId,
                            answer: q.studentAnswer || "",
                            type: parseInt(q.practiseType)
                        };

                        // 根据题目类型添加到对应列表
                        if (questionData.type === 0) {
                            this.p_list_0.push({...questionData, no: this.p_list_0.length + 1});
                        } else if (questionData.type === 1) {
                            this.p_list_1.push({...questionData, no: this.p_list_1.length + 1});
                        } else if (questionData.type === 2) {
                            this.p_list_2.push({...questionData, no: this.p_list_2.length + 1});
                        } else if (questionData.type === 3) {
                            this.p_list_3.push({...questionData, no: this.p_list_3.length + 1});
                        }
                        questionNo++;
                    });

                    // 加载第一道题
                    if (questions.length > 0) {
                        const firstQ = questions[0];
                        getPractiseInfo(firstQ.practiseId).then(re => {
                            Object.assign(this.practise, {
                                token: this.$store.state.token || sessionStorage.getItem('token'),
                                examId: paperId, // 练习模式使用paperId
                                paperId: paperId,
                                no: 1,
                                id: re.data.id,
                                name: re.data.name,
                                answer: firstQ.studentAnswer || null,
                                type: re.data.type,
                                options: re.data.options || [],
                            });
                        }).catch(() => {
                            this.$Message.error('加载题目失败');
                        });
                    }

                    if (questions.length === 0) {
                        this.$Message.warning('该练习试卷暂无题目');
                    } else {
                        // 恢复已保存的答案
                        this.$nextTick(() => {
                            this.restoreAnswers();
                        });
                    }
                }).catch((err) => {
                    this.$Message.error((err && err.msg) ? err.msg : '无法加载练习题目');
                });
            }).catch((err) => {
                this.$Message.error((err && err.msg) ? err.msg : '无法获取练习试卷信息');
            });
        },

        // 加载考试
        loadExam(examId) {
            getExamInfo(examId).then(resp =>{

                this.examInfo = resp.data;

                // 若设置了开始/结束时间，进行校验；只要未过期即可继续
                try {
                    const hasStart = !!this.examInfo.startTime;
                    const hasEnd = !!this.examInfo.endTime;
                    if (hasStart || hasEnd) {
                        const now = new Date();
                        const s = hasStart ? new Date(String(this.examInfo.startTime).replace(/-/g,'/')) : null;
                        const e = hasEnd ? new Date(String(this.examInfo.endTime).replace(/-/g,'/')) : null;
                        if (s && now < s) {
                            this.$Message.warning('考试未开始（当前允许进入用于测试）');
                        }
                        if (e && now > e) {
                            this.$Message.warning('考试已结束（当前允许进入用于测试）');
                        }
                    }
                } catch(error) {
                    console.error('考试时间验证失败:', error);
                    // 时间解析失败不影响考试流程
                }

                makeExams(this.examInfo.projectId).then(res =>{

                    const item0 = res.data.item_0 || []
                    const item1 = res.data.item_1 || []
                    const item2 = res.data.item_2 || []
                    const item3 = res.data.item_3 || []

                    item0.forEach((item, index) =>{

                        if(index == 0){
                            getPractiseInfo(item).then(re =>{

                                // 使用 Object.assign 保持对象引用，确保 v-model 响应性
                                this.practise.no = index + 1;
                                this.practise.id = re.data.id;
                                this.practise.name = re.data.name;
                                this.practise.answer = null;
                                this.practise.type = 0;
                                this.practise.options = re.data.options;
                                this.practise.token = this.$store.state.token || sessionStorage.getItem('token');
                                this.practise.examId = this.$route.query.id;
                            }).catch(()=>{
                                // 没有取到题目时，保持空白提示
                            });
                        }

                        this.p_list_0.push({
                            no: index+1,
                            id: item,
                            answer: "",
                            type: 0
                        });
                    });
                    item1.forEach((item, index) =>{

                        this.p_list_1.push({
                            no: index+1+10,
                            id: item,
                            answer: "",
                            type: 1
                        });
                    });
                    item2.forEach((item, index) =>{

                        this.p_list_2.push({
                            no: index+1+20,
                            id: item,
                            answer: "",
                            type: 2
                        });
                    });
                    item3.forEach((item, index) =>{

                        this.p_list_3.push({
                            no: index+1+30,
                            id: item,
                            answer: "",
                            type: 3
                        });
                    });
                    // 若四类题目都为空，给出提示
                    if (!item0.length && !item1.length && !item2.length && !item3.length) {
                        this.$Message.warning('该学科题库题量不足，请先在题库中补充题目后再开始考试');
                    } else {
                        // 恢复已保存的答案
                        this.$nextTick(() => {
                            this.restoreAnswers();
                        });
                    }
                }).catch((err)=>{
                    this.$Message.error((err && err.msg) ? err.msg : '无法生成试卷，请先补充题库');
                });
            }).catch((err)=>{
                this.$Message.error((err && err.msg) ? err.msg : '无法获取考试信息');
            });
        }
    },
    mounted(){
        // 判断是练习模式还是考试模式
        const isPractice = this.$route.query.type === 'practice';
        const paperId = this.$route.query.paperId;
        const examId = this.$route.query.id;

        // 验证ID参���
        if (isPractice) {
            if (!paperId) {
                this.$Message.error('练习试卷ID不能为空')
                this.$router.push('/home/practises')
                return
            }
        } else {
            if (!examId) {
                this.$Message.error('考试ID不能为空')
                this.$router.push('/home/exams')
                return
            }
        }

        getLoginUser(this.$store.state.token || sessionStorage.getItem('token')).then(resp =>{

            this.userInfo = resp.data;
        }).catch(error => {
            console.error('获取用户信息失败:', error);
            // 不影响考试流程，静默处理
        });

        if (isPractice) {
            // 练习模式
            this.initCountDown();
            this.startTimer();
            this.loadPracticePaper(paperId);
        } else {
            // 考试模式
            this.initCountDown();
            this.startTimer();
            this.loadExam(examId);
        }

        // 添加键盘事件监听
        document.addEventListener('keydown', this.handleKeyPress);
    },

    // 启动定时器
    startTimer() {
        // 记录警告状态，避免重复提醒
        let warning5min = false;
        let warning1min = false;

        // 保存定时器引用，便于清理
        this.timer = setInterval(() =>{

            let temp = countDown(this.countDown.startTime, this.countDown.endTime);
            const totalSeconds = temp.h * 3600 + temp.m * 60 + temp.s;

            // 剩余 5 分钟警告
            if (totalSeconds === 300 && !warning5min) {
                this.$Notice.warning({
                    title: '考试提醒',
                    desc: '距离考试结束还有 5 分钟，请抓紧时间！',
                    duration: 0 // 不自动关闭
                });
                warning5min = true;
            }

            // 剩余 1 分钟警告
            if (totalSeconds === 60 && !warning1min) {
                this.$Notice.warning({
                    title: '考试提醒',
                    desc: '距离考试结束还有 1 分钟！请尽快完成答题！',
                    duration: 0
                });
                warning1min = true;
            }

            if(contrastCountDown(temp.h, temp.m, temp.s)){

                this.$Modal.warning({
                    title: '考试时间已到',
                    content: '考试时间已到，系统将自动提交您的试卷',
                    onOk: () => {
                        this.doSubmit();
                        if (this.timer) {
                            clearInterval(this.timer);
                            this.timer = null;
                        }
                    },
                });
            }else{

                this.countDown.text = formatCountDown(temp.h, temp.m, temp.s);
                this.countDown.startTime = formatDate(new Date());
            }
        }, 1000);
    },
    beforeUnmount() {
        // 清理定时器，防止内存泄漏
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        // 移除键盘事件监听
        document.removeEventListener('keydown', this.handleKeyPress);
    }
}
</script>
