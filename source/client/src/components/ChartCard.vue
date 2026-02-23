<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <Icon :type="icon" class="title-icon" />
        <span>{{ title }}</span>
      </div>
      <div class="chart-actions">
        <Select 
          v-if="chartTypes && chartTypes.length > 1"
          v-model="currentType" 
          size="small" 
          style="width: 100px;"
          @on-change="handleTypeChange">
          <Option 
            v-for="type in chartTypes" 
            :key="type.value" 
            :value="type.value">
            {{ type.label }}
          </Option>
        </Select>
        <Button 
          v-if="showRefresh"
          type="text" 
          size="small" 
          @click="handleRefresh"
          :loading="loading">
          <Icon type="ios-refresh" />
        </Button>
      </div>
    </div>
    <div class="chart-content" :style="{ height: height + 'px' }">
      <div v-if="loading" class="chart-loading">
        <Spin size="large" />
      </div>
      <div v-else-if="error" class="chart-error">
        <Icon type="ios-alert" size="48" color="#ff4d4f" />
        <p>{{ error }}</p>
        <Button size="small" @click="handleRefresh">重试</Button>
      </div>
      <div v-else-if="!hasData" class="chart-empty">
        <Icon type="ios-pie-outline" size="48" color="#bfbfbf" />
        <p>暂无数据</p>
      </div>
      <v-chart 
        v-else
        :option="chartOption" 
        :theme="theme"
        :autoresize="true"
        class="chart" />
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

export default {
  name: 'ChartCard',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: 'ios-analytics'
    },
    height: {
      type: Number,
      default: 300
    },
    chartOption: {
      type: Object,
      required: true
    },
    chartTypes: {
      type: Array,
      default: null
    },
    showRefresh: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    theme: {
      type: String,
      default: 'default'
    }
  },
  data() {
    return {
      currentType: this.chartTypes ? this.chartTypes[0].value : null
    }
  },
  computed: {
    hasData() {
      return this.chartOption && (
        (this.chartOption.series && this.chartOption.series.length > 0) ||
        (this.chartOption.data && this.chartOption.data.length > 0)
      )
    }
  },
  methods: {
    handleTypeChange(value) {
      this.$emit('type-change', value)
    },
    handleRefresh() {
      this.$emit('refresh')
    }
  }
}
</script>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.chart-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.chart-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.title-icon {
  margin-right: 8px;
  color: #667eea;
  font-size: 20px;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-content {
  position: relative;
  width: 100%;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-loading,
.chart-error,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8c8c8c;
}

.chart-error p,
.chart-empty p {
  margin: 12px 0;
  font-size: 14px;
}
</style>

