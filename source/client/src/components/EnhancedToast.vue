<template>
  <transition name="toast">
    <div v-if="visible" :class="['enhanced-toast', `toast-${type}`]" @click="handleClick">
      <div class="toast-icon">
        <Icon :type="iconType" :size="24" />
      </div>
      <div class="toast-content">
        <div v-if="title" class="toast-title">{{ title }}</div>
        <div class="toast-message">{{ message }}</div>
      </div>
      <div v-if="closable" class="toast-close" @click.stop="handleClose">
        <Icon type="ios-close" :size="20" />
      </div>
      <div class="toast-progress" v-if="duration > 0">
        <div 
          class="toast-progress-bar" 
          :style="{ width: progressPercent + '%' }">
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'EnhancedToast',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      required: true
    },
    duration: {
      type: Number,
      default: 3000
    },
    closable: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      progressPercent: 100,
      timer: null,
      progressTimer: null
    }
  },
  computed: {
    iconType() {
      const iconMap = {
        success: 'ios-checkmark-circle',
        error: 'ios-close-circle',
        warning: 'ios-alert',
        info: 'ios-information-circle'
      }
      return iconMap[this.type] || 'ios-information-circle'
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.duration > 0) {
        this.startProgress()
        this.startTimer()
      } else {
        this.clearTimers()
      }
    }
  },
  methods: {
    startProgress() {
      this.progressPercent = 100
      const interval = 50
      const decrement = (100 / (this.duration / interval))
      
      this.progressTimer = setInterval(() => {
        this.progressPercent -= decrement
        if (this.progressPercent <= 0) {
          this.progressPercent = 0
          this.clearTimers()
        }
      }, interval)
    },
    startTimer() {
      this.timer = setTimeout(() => {
        this.handleClose()
      }, this.duration)
    },
    clearTimers() {
      if (this.timer) {
        clearTimeout(this.timer)
        this.timer = null
      }
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
    },
    handleClose() {
      this.clearTimers()
      this.$emit('close')
    },
    handleClick() {
      if (this.closable) {
        this.handleClose()
      }
    }
  },
  beforeUnmount() {
    this.clearTimers()
  }
}
</script>

<style scoped>
.enhanced-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  z-index: 10000;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.enhanced-toast:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  transform: translateX(-4px);
}

.toast-success {
  border-left-color: #52c41a;
}

.toast-error {
  border-left-color: #ff4d4f;
}

.toast-warning {
  border-left-color: #faad14;
}

.toast-info {
  border-left-color: #1890ff;
}

.toast-icon {
  margin-right: 12px;
  flex-shrink: 0;
}

.toast-success .toast-icon {
  color: #52c41a;
}

.toast-error .toast-icon {
  color: #ff4d4f;
}

.toast-warning .toast-icon {
  color: #faad14;
}

.toast-info .toast-icon {
  color: #1890ff;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 14px;
  color: #595959;
  line-height: 1.5;
}

.toast-close {
  margin-left: 12px;
  color: #8c8c8c;
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.3s;
}

.toast-close:hover {
  color: #262626;
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 0 0 12px 12px;
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  background: currentColor;
  transition: width 0.05s linear;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 768px) {
  .enhanced-toast {
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
}
</style>

