<template>
	<div class="fater-body-show">
		<!-- 首次使用引导 -->
		<Modal v-model="showWelcomeGuide" title="欢迎使用在线考试系统" width="600" :footer-hide="true" :mask-closable="false">
			<div class="welcome-guide">
				<Carousel :autoplay="false" :autoplay-speed="5000" v-model="currentSlide" dots="inside" height="320">
					<CarouselItem>
						<div class="guide-item">
							<div class="guide-icon">
								<Icon type="ios-book" size="80" color="#1890ff" />
							</div>
							<h3>参加考试</h3>
							<p>在"考���"模块查看可用考试，点击"开始答题"即可参加考试</p>
							<ul>
								<li>查看考试列表和详情</li>
								<li>在线答题，自动保存</li>
								<li>查看考试结果和反馈</li>
							</ul>
						</div>
					</CarouselItem>
					<CarouselItem>
						<div class="guide-item">
							<div class="guide-icon">
								<Icon type="ios-list" size="80" color="#f093fb" />
							</div>
							<h3>查看任务</h3>
							<p>在"任务中心"查看老师布置的学习任务和作业</p>
							<ul>
								<li>查看待完成任务</li>
								<li>按时完成学习任务</li>
								<li>查看任务完成情况</li>
							</ul>
						</div>
					</CarouselItem>
					<CarouselItem>
						<div class="guide-item">
							<div class="guide-icon">
								<Icon type="ios-refresh-circle" size="80" color="#4facfe" />
							</div>
							<h3>错题本</h3>
							<p>在"错题本"复习错题，巩固薄弱知识点</p>
							<ul>
								<li>查看错题记录</li>
								<li>重新答错题</li>
								<li>添加复习笔记</li>
							</ul>
						</div>
					</CarouselItem>
					<CarouselItem>
						<div class="guide-item">
							<div class="guide-icon">
								<Icon type="ios-stats" size="80" color="#43e97b" />
							</div>
							<h3>数据统计</h3>
							<p>在首页查看学习数据和进度分析</p>
							<ul>
								<li>今日学习概览</li>
								<li>学习趋势图表</li>
								<li>成绩统计分析</li>
							</ul>
						</div>
					</CarouselItem>
				</Carousel>
				<div class="guide-footer">
					<Button v-if="currentSlide > 0" @click="currentSlide--" style="margin-right: 8px;">
						上一步
					</Button>
					<Button v-if="currentSlide < 3" type="primary" @click="currentSlide++">
						下一步
					</Button>
					<Button v-else type="primary" @click="closeWelcomeGuide">
						我知道了
					</Button>
					<Checkbox v-model="dontShowAgain" style="margin-left: 16px;">不再显示</Checkbox>
				</div>
			</div>
		</Modal>
        <Row :gutter="20">
            <Col span="8">
                <div class="fater-calendar-panel">
                    <div class="calendar-header">
                        <Icon type="ios-calendar" class="calendar-icon" />
                        <span class="calendar-title">今日日历</span>
                    </div>
                    <Calendar cell-height="40" class="custom-calendar"/>
                </div>
            </Col>
            <Col span="16">
                <Card style="margin-top:16px;">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-stats" class="title-icon" />
                            <span>系统概览</span>
                        </div>
                    </template>
                    <Row :gutter="12">
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ today.todayNewQuestions }}</div><div class="stat-label">今日新增题目</div></div></Col>
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ today.todayNewPractices }}</div><div class="stat-label">今日新增练习</div></div></Col>
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ today.todayNewExams }}</div><div class="stat-label">今日新增考试</div></div></Col>
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ trend.activeUsers7d }}</div><div class="stat-label">近7天活跃用户</div></div></Col>
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ trend.passRate7d }}%</div><div class="stat-label">近7天通过率</div></div></Col>
                        <Col span="4"><div class="stat-card"><div class="stat-value">{{ trend.avgScore7d }}</div><div class="stat-label">近7天平均分</div></div></Col>
                    </Row>
                    <Row :gutter="12" style="margin-top:12px;">
                        <Col span="4"><div class="stat-card warn"><div class="stat-value">{{ review.pendingReviews }}</div><div class="stat-label">待人工覆核数</div></div></Col>
                    </Row>
                </Card>
            </Col>
        </Row>

        <Card style="margin-top:16px;">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-trending-up" class="title-icon" />
                    <span>趋势图表</span>
                </div>
            </template>
            <Row :gutter="12">
                <Col span="12">
                    <div style="height:300px;" ref="chartQuestions"></div>
                </Col>
                <Col span="12">
                    <div style="height:300px;" ref="chartActive"></div>
                </Col>
            </Row>
            <Row :gutter="12" style="margin-top:12px;">
                <Col span="24">
                    <div style="height:300px;" ref="chartDone"></div>
                </Col>
            </Row>
        </Card>

        
    </div>
</template>

<style>
.fater-body-show {
	padding: 20px;
}

.calendar-header {
	display: flex;
	align-items: center;
	gap: 10px;
	margin-bottom: 15px;
	padding-bottom: 10px;
	border-bottom: 2px solid #f0f0f0;
}

.calendar-icon {
	font-size: 20px;
	color: #1890ff;
}

.calendar-title {
	font-size: 16px;
	font-weight: 600;
	color: #333;
}

.custom-calendar {
	border-radius: 8px;
	overflow: hidden;
}

.system-info-card {
	border-radius: 12px;
	box-shadow: 0 4px 20px rgba(0,0,0,0.08);
	border: none;
}

.card-title {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 16px;
	font-weight: 600;
	color: #333;
}

.title-icon {
	font-size: 18px;
	color: #1890ff;
}

.info-icon {
	font-size: 16px;
	color: #1890ff;
	margin-right: 8px;
}

.welcome-content {
	position: relative;
	z-index: 2;
	text-align: center;
	padding: 40px;
}

.welcome-text h1 {
	font-size: 48px;
	font-weight: 300;
	margin-bottom: 10px;
	color: #fff;
	text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.welcome-text h2 {
	font-size: 36px;
	font-weight: 600;
	margin-bottom: 20px;
	color: #fff;
	text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.welcome-text p {
	font-size: 18px;
	color: rgba(255,255,255,0.9);
	margin-bottom: 40px;
	text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.welcome-features {
	display: flex;
	justify-content: center;
	flex-wrap: wrap;
	gap: 30px;
	margin-top: 40px;
}

.feature-item {
	display: flex;
	align-items: center;
	gap: 10px;
	background: rgba(255,255,255,0.1);
	padding: 15px 25px;
	border-radius: 25px;
	backdrop-filter: blur(10px);
	border: 1px solid rgba(255,255,255,0.2);
	transition: all 0.3s ease;
}

.feature-item:hover {
	background: rgba(255,255,255,0.2);
	transform: translateY(-2px);
	box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

.feature-icon {
	font-size: 20px;
	color: #fff;
}

.feature-item span {
	color: #fff;
	font-weight: 500;
	font-size: 14px;
}

.voice-section {
	margin-top: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.fater-body-show {
		padding: 15px;
	}
	
	.welcome-text h1 {
		font-size: 32px;
	}
	
	.welcome-text h2 {
		font-size: 24px;
	}
	
	.welcome-text p {
		font-size: 16px;
	}
	
	.welcome-features {
		gap: 15px;
	}
	
	.feature-item {
		padding: 12px 20px;
	}
}

/* 欢迎引导样式 */
.welcome-guide {
	padding: 20px 0;
}

.guide-item {
	text-align: center;
	padding: 20px;
}

.guide-icon {
	margin-bottom: 24px;
}

.guide-item h3 {
	font-size: 24px;
	font-weight: 600;
	color: #262626;
	margin-bottom: 12px;
}

.guide-item p {
	font-size: 14px;
	color: #8c8c8c;
	margin-bottom: 16px;
	line-height: 1.6;
}

.guide-item ul {
	list-style: none;
	padding: 0;
	text-align: left;
	max-width: 400px;
	margin: 0 auto;
}

.guide-item ul li {
	padding: 8px 16px;
	color: #595959;
	font-size: 14px;
	line-height: 1.6;
}

.guide-item ul li:before {
	content: "✓";
	color: #52c41a;
	font-weight: bold;
	display: inline-block;
	width: 1em;
	margin-left: -1em;
}

.guide-footer {
	text-align: center;
	padding-top: 20px;
	border-top: 1px solid #f0f0f0;
	margin-top: 20px;
}
</style>

<script>
import * as echarts from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

export default{
    data(){
        return {
            today: { todayNewQuestions: 0, todayNewPractices: 0, todayNewExams: 0 },
            trend: { activeUsers7d: 0, passRate7d: 0, avgScore7d: 0 },
            review: { pendingReviews: 0 },
            // 欢迎引导
            showWelcomeGuide: false,
            currentSlide: 0,
            dontShowAgain: false

        }
    },
    methods:{
        async loadDashboard(){
            try{
                const api = await import('../../utils/http.js')
                const resp = await api.default.get('/admin/dashboard_cards/')
                if(resp.code === 0){
                    const d = resp.data || {}
                    this.today = { todayNewQuestions: d.todayNewQuestions || 0, todayNewPractices: d.todayNewPractices || 0, todayNewExams: d.todayNewExams || 0 }
                    this.trend = { activeUsers7d: d.activeUsers7d || 0, passRate7d: d.passRate7d || 0, avgScore7d: d.avgScore7d || 0 }
                    this.review = { pendingReviews: d.pendingReviews || 0 }
                }
            }catch(e){
                // ignore
            }
        }
        ,
        async loadTrends(){
            try{
                const api = await import('../../utils/http.js')
                const resp = await api.default.get('/admin/trends/')
                if(resp.code === 0){
                    const d = resp.data || {}
                    // 题目月度新增（柱状）
                    const chartQuestions = echarts.init(this.$refs.chartQuestions)
                    chartQuestions.setOption({
                        tooltip: { trigger: 'axis' },
                        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                        xAxis: { type: 'category', data: d.months || [] },
                        yAxis: { type: 'value' },
                        series: [{ name: '题目数', type: 'bar', data: d.questionsByMonth || [], barWidth: '50%' }]
                    })
                    // 活跃用户（折线）
                    const chartActive = echarts.init(this.$refs.chartActive)
                    chartActive.setOption({
                        tooltip: { trigger: 'axis' },
                        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                        xAxis: { type: 'category', data: d.days || [], boundaryGap: false },
                        yAxis: { type: 'value' },
                        series: [{ name: '活跃用户', type: 'line', smooth: true, data: d.activeUsersDaily || [] }]
                    })
                    // 练习/任务完成（堆叠柱状）
                    const chartDone = echarts.init(this.$refs.chartDone)
                    chartDone.setOption({
                        tooltip: { trigger: 'axis' },
                        legend: { data: ['练习完成', '任务完成'] },
                        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                        xAxis: { type: 'category', data: d.days || [] },
                        yAxis: { type: 'value' },
                        series: [
                            { name: '练习完成', type: 'bar', stack: 'total', data: d.practiceDoneDaily || [] },
                            { name: '任务完成', type: 'bar', stack: 'total', data: d.taskDoneDaily || [] }
                        ]
                    })
                }
            }catch(e){
                // ignore
            }
        }
        ,
        // 关闭欢迎引导
        closeWelcomeGuide() {
            if (this.dontShowAgain) {
                localStorage.setItem('fyp_welcome_guide_shown', 'true');
            }
            this.showWelcomeGuide = false;
        },
        // 检查是否显示欢迎引导
        checkWelcomeGuide() {
            const hasShown = localStorage.getItem('fyp_welcome_guide_shown');
            if (!hasShown) {
                // 延迟 1 秒显示，让用户先看到页面
                setTimeout(() => {
                    this.showWelcomeGuide = true;
                }, 1000);
            }
        }
    },
    mounted(){
        this.loadDashboard()
        this.$nextTick(() => this.loadTrends())
        // 检查是否显示欢迎引导
        this.checkWelcomeGuide()
    }
}
</script>