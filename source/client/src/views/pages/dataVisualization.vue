<template>
  <div class="fater-body-show">
    <div class="page-header animate-fade-in-up">
      <div class="header-content">
        <Icon type="ios-analytics" class="header-icon" />
        <div class="header-text">
          <h2>数据可视化</h2>
          <p>查看您的学习数据统计和分析</p>
        </div>
      </div>
    </div>

    <Row :gutter="24" class="charts-row">
      <Col span="24">
        <StudentProgressChart />
      </Col>
    </Row>

    <Row :gutter="24" class="charts-row">
      <Col span="24">
        <ScoreTrendChart />
      </Col>
    </Row>

    <Row :gutter="24" class="charts-row">
      <Col span="24">
        <WrongQuestionStatsChart />
      </Col>
    </Row>

    <Row :gutter="24" class="charts-row">
      <Col span="24">
        <RadarChart />
      </Col>
    </Row>
  </div>
</template>

<script>
import StudentProgressChart from '@/components/StudentProgressChart.vue'
import ScoreTrendChart from '@/components/ScoreTrendChart.vue'
import WrongQuestionStatsChart from '@/components/WrongQuestionStatsChart.vue'
import RadarChart from '@/components/RadarChart.vue'

export default {
  name: 'DataVisualization',
  components: {
    StudentProgressChart,
    ScoreTrendChart,
    WrongQuestionStatsChart,
    RadarChart
  }
}
</script>

<style scoped>
.fater-body-show {
  padding: 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 30px rgba(24, 144, 255, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
}

.header-icon {
  font-size: 48px;
  margin-right: 20px;
  opacity: 0.9;
  color: #fff;
}

.header-text h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #fff;
}

.header-text p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
  color: rgba(255, 255, 255, 0.9);
}

.charts-row {
  margin-bottom: 24px;
}

.charts-row .ivu-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
  border: 1px solid rgba(24, 144, 255, 0.1);
  transition: all 0.3s ease;
}

.charts-row .ivu-card:hover {
  box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
  transform: translateY(-4px);
}

.animate-fade-in-up {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .fater-body-show {
    padding: 16px;
  }

  .page-header {
    padding: 20px;
  }

  .header-text h2 {
    font-size: 22px;
  }

  .header-icon {
    font-size: 36px;
  }
}
</style>

