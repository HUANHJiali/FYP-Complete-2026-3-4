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
							<span>{{ roleType === 0 ? '管理概览' : (roleType === 1 ? '教学概览' : '学习概览') }}</span>
                        </div>
                    </template>
					<div v-if="!roleReady" style="padding: 20px 0; text-align: center;">
						<Spin size="large" />
					</div>
					<template v-else-if="roleType === 0">
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
					</template>
					<template v-else-if="roleType === 1">
						<Row :gutter="12">
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ teacherStats.totalLogs }}</div><div class="stat-label">考试记录总数</div></div></Col>
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ teacherStats.ongoingExams }}</div><div class="stat-label">考试中</div></div></Col>
							<Col span="6"><div class="stat-card warn"><div class="stat-value">{{ teacherStats.pendingPublish }}</div><div class="stat-label">待公布成绩</div></div></Col>
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ teacherStats.finishedExams }}</div><div class="stat-label">已完成处理</div></div></Col>
						</Row>
					</template>
					<template v-else>
						<Row :gutter="12">
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ studentStats.availableExams }}</div><div class="stat-label">可参加考试</div></div></Col>
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ studentStats.practicePapers }}</div><div class="stat-label">可用练习试卷</div></div></Col>
							<Col span="6"><div class="stat-card warn"><div class="stat-value">{{ studentStats.pendingTasks }}</div><div class="stat-label">待完成任务</div></div></Col>
							<Col span="6"><div class="stat-card"><div class="stat-value">{{ studentStats.completedTasks }}</div><div class="stat-label">已完成任务</div></div></Col>
						</Row>
					</template>
                </Card>
            </Col>
        </Row>

		<Card v-if="roleType === 0" style="margin-top:16px;">
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

		<Card v-else-if="roleType === 1" style="margin-top:16px;">
			<template #title>
				<div class="card-title">
					<Icon type="ios-trending-up" class="title-icon" />
					<span>教学趋势</span>
				</div>
			</template>
			<Row :gutter="12">
				<Col span="12">
					<div style="height:300px;" ref="chartTeacherStatus"></div>
				</Col>
				<Col span="12">
					<div style="height:300px;" ref="chartTeacherProject"></div>
				</Col>
			</Row>
		</Card>

		<Card v-else-if="roleType === 2" style="margin-top:16px;">
			<template #title>
				<div class="card-title">
					<Icon type="ios-trending-up" class="title-icon" />
					<span>学习趋势</span>
				</div>
			</template>
			<Row :gutter="12">
				<Col span="12">
					<div style="height:300px;" ref="chartStudentExam"></div>
				</Col>
				<Col span="12">
					<div style="height:300px;" ref="chartStudentTask"></div>
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
import { getEmptyTeacherStats, getEmptyStudentStats } from '../../utils/welcomeDashboard'
import { buildAdminQuestionsOption, buildAdminActiveOption, buildAdminDoneOption, buildTeacherStatusOption, buildTeacherProjectOption, buildStudentExamOption, buildStudentTaskOption } from '../../utils/welcomeChartOptions'
import { setChartInstance, disposeAllChartInstances } from '../../utils/chartInstanceManager'
import { resolveWelcomeRole, fetchAdminDashboardBundle, fetchTeacherDashboardBundle, fetchStudentDashboardBundle } from '../../utils/welcomeDataProvider'
import { shouldShowWelcomeGuide, markWelcomeGuideHidden, scheduleWelcomeGuide, clearWelcomeGuideTimer } from '../../utils/welcomeGuide'
import { getEmptyAdminToday, getEmptyAdminTrend, getEmptyAdminReview, createWelcomeChartInstances } from '../../utils/welcomeDefaults'
echarts.use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

export default{
    data(){
        return {
            today: getEmptyAdminToday(),
            trend: getEmptyAdminTrend(),
            review: getEmptyAdminReview(),
			isAdmin: false,
			roleType: null,
			roleReady: false,
			teacherStats: getEmptyTeacherStats(),
			studentStats: getEmptyStudentStats(),
			chartInstances: createWelcomeChartInstances(),
            // 欢迎引导
            showWelcomeGuide: false,
            currentSlide: 0,
			dontShowAgain: false,
			welcomeGuideTimer: null

        }
    },
    methods:{
		async initDashboardByRole(){
			try{
				const token = (this.$store && this.$store.state && this.$store.state.token) || sessionStorage.getItem('token') || ''
				if (!token) {
                    this.roleReady = true
                    return
                }
				const roleData = await resolveWelcomeRole(token)
				this.roleType = roleData.roleType
				this.isAdmin = roleData.isAdmin
				if (this.roleType === 0){
					await this.loadDashboardAndTrends()
				} else if (this.roleType === 1) {
                    await this.loadTeacherDashboard(token)
                } else if (this.roleType === 2) {
                    await this.loadStudentDashboard(token)
				}
			}catch(e){
				this.roleType = null
				this.isAdmin = false
			} finally {
                this.roleReady = true
			}
		},
        async loadDashboardAndTrends(){
            try{
				const bundle = await fetchAdminDashboardBundle()
				const cardsData = bundle.cardsData || {}
				const trendsData = bundle.trendsData || {}
				this.today = {
					...getEmptyAdminToday(),
					todayNewQuestions: cardsData.todayNewQuestions ?? 0,
					todayNewPractices: cardsData.todayNewPractices ?? 0,
					todayNewExams: cardsData.todayNewExams ?? 0
				}
				this.trend = {
					...getEmptyAdminTrend(),
					activeUsers7d: cardsData.activeUsers7d ?? 0,
					passRate7d: cardsData.passRate7d ?? 0,
					avgScore7d: cardsData.avgScore7d ?? 0
				}
				this.review = {
					...getEmptyAdminReview(),
					pendingReviews: cardsData.pendingReviews ?? 0
				}
				this.$nextTick(() => this.renderAdminTrends(trendsData))
            }catch(e){
                // ignore
            }
        }
        ,
		renderAdminTrends(data){
			setChartInstance(this.chartInstances, 'chartQuestions', this.$refs.chartQuestions, echarts, buildAdminQuestionsOption(data))
			setChartInstance(this.chartInstances, 'chartActive', this.$refs.chartActive, echarts, buildAdminActiveOption(data))
			setChartInstance(this.chartInstances, 'chartDone', this.$refs.chartDone, echarts, buildAdminDoneOption(data))
		}
		,
		async loadTeacherDashboard(token){
			const teacherData = await fetchTeacherDashboardBundle(token)
			this.teacherStats = teacherData.stats || getEmptyTeacherStats()
			this.$nextTick(() => this.renderTeacherTrends(teacherData.chart || { statusData: [0, 0, 0], projectNames: ['暂无数据'], projectValues: [0] }))
		}
		,
		async loadStudentDashboard(token){
			const studentData = await fetchStudentDashboardBundle(token)
			this.studentStats = studentData.stats || getEmptyStudentStats()
			this.$nextTick(() => this.renderStudentTrends(studentData.chart || { examSeries: [0, 0, 0, 0], taskSeries: [0, 0, 0, 0] }))
		}
		,
		renderTeacherTrends(chartData){
			if (!this.$refs.chartTeacherStatus || !this.$refs.chartTeacherProject) return

			setChartInstance(this.chartInstances, 'chartTeacherStatus', this.$refs.chartTeacherStatus, echarts, buildTeacherStatusOption(chartData))

			setChartInstance(this.chartInstances, 'chartTeacherProject', this.$refs.chartTeacherProject, echarts, buildTeacherProjectOption(chartData))
		}
		,
		renderStudentTrends(chartData){
			if (!this.$refs.chartStudentExam || !this.$refs.chartStudentTask) return

			setChartInstance(this.chartInstances, 'chartStudentExam', this.$refs.chartStudentExam, echarts, buildStudentExamOption(chartData))

			setChartInstance(this.chartInstances, 'chartStudentTask', this.$refs.chartStudentTask, echarts, buildStudentTaskOption(chartData))
		}
		,
        // 关闭欢迎引导
        closeWelcomeGuide() {
			markWelcomeGuideHidden(this.dontShowAgain)
            this.showWelcomeGuide = false;
        },
        // 检查是否显示欢迎引导
        checkWelcomeGuide() {
			if (shouldShowWelcomeGuide()) {
				this.welcomeGuideTimer = scheduleWelcomeGuide(() => {
					this.showWelcomeGuide = true
				}, 1000)
            }
        }
    },
    mounted(){
		this.initDashboardByRole()
        // 检查是否显示欢迎引导
        this.checkWelcomeGuide()
	},
	beforeUnmount() {
		clearWelcomeGuideTimer(this.welcomeGuideTimer)
		disposeAllChartInstances(this.chartInstances)
    }
}
</script>