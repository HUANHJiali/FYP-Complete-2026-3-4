<template>
  <div v-if="visible" class="enhanced-loading">
    <div class="loading-overlay" @click="handleOverlayClick">
      <div class="loading-content" @click.stop>
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <p class="loading-text">{{ text }}</p>
        <div v-if="showProgress" class="loading-progress">
          <Progress :percent="progress" :status="progressStatus" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnhancedLoading',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      default: '加载中...'
    },
    showProgress: {
      type: Boolean,
      default: false
    },
    progress: {
      type: Number,
      default: 0
    },
    progressStatus: {
      type: String,
      default: 'active'
    },
    closable: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    handleOverlayClick() {
      if (this.closable) {
        this.$emit('close')
      }
    }
  }
}
</script>

<style scoped>
.enhanced-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.loading-overlay {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.loading-content {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  min-width: 200px;
}

.loading-spinner {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 4px solid transparent;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) {
  animation-delay: -0.45s;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.3s;
  border-top-color: #764ba2;
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.15s;
  border-top-color: #667eea;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-text {
  margin: 0;
  font-size: 16px;
  color: #262626;
  font-weight: 500;
}

.loading-progress {
  margin-top: 16px;
  width: 200px;
}
</style>

