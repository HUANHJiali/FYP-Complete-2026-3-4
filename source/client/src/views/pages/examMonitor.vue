<template>
  <div class="exam-monitor">
    <Card :bordered="false" class="header-card">
      <div class="header">
        <h2>考试实时监控</h2>
        <div class="header-actions">
          <Select v-model="selectedExamId" style="width: 200px" placeholder="选择考试" @on-change="onExamChange">
            <Option v-for="exam in examList" :key="exam.id" :value="exam.id">
              {{ exam.name }} ({{ exam.gradeName }})
            </Option>
          </Select>
          <Button type="primary" @click="refreshData" :loading="loading">
            <Icon type="md-refresh" /> 刷新
          </Button>
          <Switch v-model="autoRefresh" @on-change="toggleAutoRefresh">
            <span slot="open">自动</span>
            <span slot="close">手动</span>
          </Switch>
        </div>
      </div>
    </Card>

    <div v-if="selectedExamId" class="monitor-content">
      <Row :gutter="16" class="stats-row">
        <Col :span="6">
          <Card class="stat-card">
            <Statistic title="应考人数" :value="examStatus.totalStudents">
              <template slot="suffix">
                <span class="unit">人</span>
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col :span="6">
          <Card class="stat-card success">
            <Statistic title="已提交" :value="examStatus.submittedCount">
              <template slot="suffix">
                <span class="unit">人 ({{ examStatus.submitRate }}%)</span>
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col :span="6">
          <Card class="stat-card warning">
            <Statistic title="答题中" :value="examStatus.inProgressCount">
              <template slot="suffix">
                <span class="unit">人</span>
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col :span="6">
          <Card class="stat-card info">
            <Statistic title="平均分" :value="examStatus.avgScore || 0">
              <template slot="suffix">
                <span class="unit">分</span>
              </template>
            </Statistic>
          </Card>
        </Col>
      </Row>

      <Row :gutter="16" class="charts-row">
        <Col :span="8">
          <Card title="提交状态分布">
            <div ref="pieChart" style="height: 250px;"></div>
          </Card>
        </Col>
        <Col :span="8">
          <Card title="成绩分布">
            <div ref="barChart" style="height: 250px;"></div>
          </Card>
        </Col>
        <Col :span="8">
          <Card title="最近提交">
            <div class="recent-list">
              <div v-for="item in recentSubmits" :key="item.submitTime" class="recent-item">
                <span class="name">{{ item.studentName }}</span>
                <span class="score">{{ item.score }}分</span>
                <span class="time">{{ item.submitTime }}</span>
              </div>
              <div v-if="recentSubmits.length === 0" class="empty-tip">暂无提交记录</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Card title="学生状态列表" class="student-list-card">
        <div class="filter-bar">
          <RadioGroup v-model="statusFilter" @on-change="filterStudents">
            <Radio label="">全部 ({{ examStatus.totalStudents }})</Radio>
            <Radio label="submitted">已提交 ({{ examStatus.submittedCount }})</Radio>
            <Radio label="in_progress">答题中 ({{ examStatus.inProgressCount }})</Radio>
            <Radio label="not_started">未开始 ({{ examStatus.notStartedCount }})</Radio>
          </RadioGroup>
        </div>
        <Table :columns="studentColumns" :data="studentList" :loading="tableLoading" stripe>
          <template #status="{ row }">
            <Tag :color="getStatusColor(row.status)">{{ row.statusText }}</Tag>
          </template>
          <template #score="{ row }">
            <span v-if="row.score !== null" :class="getScoreClass(row.score)">
              {{ row.score }}
            </span>
            <span v-else>-</span>
          </template>
        </Table>
        <div class="pagination">
          <Page :total="studentTotal" :current="pageIndex" :page-size="pageSize" 
                @on-change="onPageChange" show-total />
        </div>
      </Card>

      <Card title="题目正确率统计" class="question-stats-card">
        <Table :columns="questionColumns" :data="questionStats" stripe max-height="300">
          <template #correctRate="{ row }">
            <Progress :percent="row.correctRate" :status="getProgressStatus(row.correctRate)" />
          </template>
        </Table>
      </Card>
    </div>

    <div v-else class="empty-state">
      <Icon type="md-analytics" size="64" color="#dcdee2" />
      <p>请选择一个考试开始监控</p>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import http from '../../utils/http.js';

export default {
  name: 'ExamMonitor',
  data() {
    return {
      loading: false,
      tableLoading: false,
      autoRefresh: false,
      refreshTimer: null,
      selectedExamId: null,
      examList: [],
      examStatus: {},
      studentList: [],
      studentTotal: 0,
      pageIndex: 1,
      pageSize: 10,
      statusFilter: '',
      recentSubmits: [],
      questionStats: [],
      pieChart: null,
      barChart: null,
      studentColumns: [
        { title: '学号', key: 'studentNo', width: 120 },
        { title: '姓名', key: 'studentName', width: 100 },
        { title: '状态', slot: 'status', width: 100 },
        { title: '已答题数', key: 'answerCount', width: 100 },
        { title: '正确数', key: 'correctCount', width: 100 },
        { title: '分数', slot: 'score', width: 80 },
        { title: '提交时间', key: 'submitTime', width: 160 }
      ],
      questionColumns: [
        { title: '序号', type: 'index', width: 60 },
        { title: '题目', key: 'questionName', ellipsis: true },
        { title: '类型', key: 'questionTypeText', width: 80 },
        { title: '答题数', key: 'totalAnswers', width: 80 },
        { title: '正确数', key: 'correctAnswers', width: 80 },
        { title: '正确率', slot: 'correctRate', width: 150 }
      ]
    };
  },
  mounted() {
    this.loadExamList();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    this.stopAutoRefresh();
    window.removeEventListener('resize', this.handleResize);
    if (this.pieChart) this.pieChart.dispose();
    if (this.barChart) this.barChart.dispose();
  },
  methods: {
    async loadExamList() {
      try {
        const response = await http.get('/exam-monitor/exams/');
        if (response.code === 0) {
          this.examList = response.data || [];
          if (this.examList.length > 0 && !this.selectedExamId) {
            this.selectedExamId = this.examList[0].id;
            this.loadAllData();
          }
        } else {
          this.$Message.error(response.msg || '获取考试列表失败');
        }
      } catch (error) {
        this.$Message.error('获取考试列表失败');
      }
    },
    onExamChange() {
      this.pageIndex = 1;
      this.statusFilter = '';
      this.loadAllData();
    },
    async loadAllData() {
      if (!this.selectedExamId) return;
      this.loading = true;
      try {
        await Promise.all([
          this.loadExamStatus(),
          this.loadStudentList(),
          this.loadQuestionStats()
        ]);
        this.initCharts();
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadExamStatus() {
      try {
        const response = await http.get('/exam-monitor/status/', {
          params: { examId: this.selectedExamId }
        });
        if (response.code === 0) {
          this.examStatus = response.data;
        } else {
          this.$Message.error(response.msg || '获取考试状态失败');
        }
      } catch (error) {
        console.error('获取考试状态失败:', error);
      }
    },
    async loadStudentList() {
      this.tableLoading = true;
      try {
        const response = await http.get('/exam-monitor/students/', {
          params: {
            examId: this.selectedExamId,
            pageIndex: this.pageIndex,
            pageSize: this.pageSize,
            status: this.statusFilter
          }
        });
        if (response.code === 0) {
          this.studentList = response.data.list || [];
          this.studentTotal = response.data.total || 0;
        } else {
          this.$Message.error(response.msg || '获取学生列表失败');
        }
      } catch (error) {
        console.error('获取学生列表失败:', error);
      } finally {
        this.tableLoading = false;
      }
    },
    async loadQuestionStats() {
      try {
        const response = await http.get('/exam-monitor/questions/', {
          params: { examId: this.selectedExamId }
        });
        if (response.code === 0) {
          this.questionStats = response.data || [];
        } else {
          this.$Message.error(response.msg || '获取题目统计失败');
        }
      } catch (error) {
        console.error('获取题目统计失败:', error);
      }
    },
    async loadRealtimeData() {
      try {
        const response = await http.get('/exam-monitor/realtime/', {
          params: { examId: this.selectedExamId }
        });
        if (response.code === 0) {
          const data = response.data;
          this.examStatus.submittedCount = data.submittedCount;
          this.examStatus.inProgressCount = data.inProgressCount;
          this.recentSubmits = data.recentSubmits || [];
          this.updatePieChart();
        } else {
          this.$Message.error(response.msg || '获取实时数据失败');
        }
      } catch (error) {
        console.error('获取实时数据失败:', error);
      }
    },
    initCharts() {
      this.$nextTick(() => {
        this.initPieChart();
        this.initBarChart();
      });
    },
    initPieChart() {
      if (!this.$refs.pieChart) return;
      if (this.pieChart) this.pieChart.dispose();
      
      this.pieChart = echarts.init(this.$refs.pieChart);
      const option = {
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, itemWidth: 10, itemHeight: 10 },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: false,
          label: { show: false },
          emphasis: { label: { show: true, fontSize: '14' } },
          data: [
            { value: this.examStatus.submittedCount || 0, name: '已提交', itemStyle: { color: '#19be6b' } },
            { value: this.examStatus.inProgressCount || 0, name: '答题中', itemStyle: { color: '#ff9900' } },
            { value: this.examStatus.notStartedCount || 0, name: '未开始', itemStyle: { color: '#c5c8ce' } }
          ]
        }]
      };
      this.pieChart.setOption(option);
    },
    initBarChart() {
      if (!this.$refs.barChart) return;
      if (this.barChart) this.barChart.dispose();
      
      this.barChart = echarts.init(this.$refs.barChart);
      
      const scores = this.studentList
        .filter(s => s.score !== null)
        .map(s => s.score);
      
      const ranges = [
        { name: '0-59', min: 0, max: 59 },
        { name: '60-69', min: 60, max: 69 },
        { name: '70-79', min: 70, max: 79 },
        { name: '80-89', min: 80, max: 89 },
        { name: '90-100', min: 90, max: 100 }
      ];
      
      const data = ranges.map(r => scores.filter(s => s >= r.min && s <= r.max).length);
      
      const option = {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ranges.map(r => r.name) },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{
          type: 'bar',
          data: data,
          itemStyle: {
            color: (params) => {
              const colors = ['#ed4014', '#ff9900', '#2d8cf0', '#19be6b', '#19be6b'];
              return colors[params.dataIndex];
            }
          }
        }]
      };
      this.barChart.setOption(option);
    },
    updatePieChart() {
      if (!this.pieChart) return;
      this.pieChart.setOption({
        series: [{
          data: [
            { value: this.examStatus.submittedCount || 0, name: '已提交' },
            { value: this.examStatus.inProgressCount || 0, name: '答题中' },
            { value: this.examStatus.notStartedCount || 0, name: '未开始' }
          ]
        }]
      });
    },
    refreshData() {
      this.loadAllData();
    },
    toggleAutoRefresh(val) {
      if (val) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    },
    startAutoRefresh() {
      this.refreshTimer = setInterval(() => {
        this.loadRealtimeData();
      }, 5000);
    },
    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
        this.refreshTimer = null;
      }
    },
    filterStudents() {
      this.pageIndex = 1;
      this.loadStudentList();
    },
    onPageChange(page) {
      this.pageIndex = page;
      this.loadStudentList();
    },
    getStatusColor(status) {
      const colors = {
        'submitted': 'success',
        'in_progress': 'warning',
        'not_started': 'default'
      };
      return colors[status] || 'default';
    },
    getScoreClass(score) {
      if (score >= 90) return 'score-excellent';
      if (score >= 80) return 'score-good';
      if (score >= 60) return 'score-pass';
      return 'score-fail';
    },
    getProgressStatus(percent) {
      if (percent >= 80) return 'success';
      if (percent >= 60) return 'normal';
      return 'error';
    },
    handleResize() {
      if (this.pieChart) this.pieChart.resize();
      if (this.barChart) this.barChart.resize();
    }
  }
};
</script>

<style scoped>
.exam-monitor {
  padding: 16px;
}

.header-card {
  margin-bottom: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  text-align: center;
}

.stat-card.success :deep(.ivu-statistic-title) {
  color: #19be6b;
}

.stat-card.warning :deep(.ivu-statistic-title) {
  color: #ff9900;
}

.stat-card.info :deep(.ivu-statistic-title) {
  color: #2d8cf0;
}

.unit {
  font-size: 14px;
  color: #808695;
}

.charts-row {
  margin-bottom: 16px;
}

.recent-list {
  height: 250px;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-item .name {
  flex: 1;
  font-weight: 500;
}

.recent-item .score {
  width: 50px;
  text-align: right;
  color: #19be6b;
  font-weight: 500;
}

.recent-item .time {
  width: 80px;
  text-align: right;
  color: #808695;
  font-size: 12px;
}

.empty-tip {
  text-align: center;
  color: #c5c8ce;
  padding: 40px 0;
}

.student-list-card {
  margin-bottom: 16px;
}

.filter-bar {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  text-align: right;
}

.score-excellent {
  color: #19be6b;
  font-weight: 600;
}

.score-good {
  color: #2d8cf0;
  font-weight: 500;
}

.score-pass {
  color: #ff9900;
}

.score-fail {
  color: #ed4014;
}

.empty-state {
  text-align: center;
  padding: 100px 0;
  color: #c5c8ce;
}

.empty-state p {
  margin-top: 16px;
  font-size: 16px;
}
</style>
