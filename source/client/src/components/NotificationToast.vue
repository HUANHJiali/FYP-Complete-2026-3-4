<template>
    <transition name="notification">
        <div v-if="visible" class="notification-toast" :class="type">
            <div class="notification-icon">
                <Icon :type="iconType" />
            </div>
            <div class="notification-content">
                <div class="notification-title">{{ title }}</div>
                <div class="notification-message">{{ message }}</div>
            </div>
            <div class="notification-close" @click="close">
                <Icon type="ios-close" />
            </div>
        </div>
    </transition>
</template>

<script>
export default {
    name: 'NotificationToast',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        type: {
            type: String,
            default: 'info',
            validator: value => ['success', 'warning', 'error', 'info'].includes(value)
        },
        title: {
            type: String,
            default: ''
        },
        message: {
            type: String,
            default: ''
        },
        duration: {
            type: Number,
            default: 3000
        }
    },
    computed: {
        iconType() {
            const icons = {
                success: 'ios-checkmark-circle',
                warning: 'ios-warning',
                error: 'ios-close-circle',
                info: 'ios-information-circle'
            }
            return icons[this.type] || icons.info
        }
    },
    watch: {
        visible(newVal) {
            if (newVal && this.duration > 0) {
                setTimeout(() => {
                    this.close()
                }, this.duration)
            }
        }
    },
    methods: {
        close() {
            this.$emit('close')
        }
    }
}
</script>

<style scoped>
.notification-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    min-width: 300px;
    max-width: 400px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    padding: 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    z-index: 10000;
    border-left: 4px solid;
    animation: slideInRight 0.3s ease;
}

.notification-toast.success {
    border-left-color: #19be6b;
}

.notification-toast.warning {
    border-left-color: #ff9900;
}

.notification-toast.error {
    border-left-color: #ed4014;
}

.notification-toast.info {
    border-left-color: #2db7f5;
}

.notification-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 16px;
}

.notification-toast.success .notification-icon {
    background: rgba(25, 190, 107, 0.1);
    color: #19be6b;
}

.notification-toast.warning .notification-icon {
    background: rgba(255, 153, 0, 0.1);
    color: #ff9900;
}

.notification-toast.error .notification-icon {
    background: rgba(237, 64, 20, 0.1);
    color: #ed4014;
}

.notification-toast.info .notification-icon {
    background: rgba(45, 183, 245, 0.1);
    color: #2db7f5;
}

.notification-content {
    flex: 1;
    min-width: 0;
}

.notification-title {
    font-size: 14px;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
    line-height: 1.4;
}

.notification-message {
    font-size: 13px;
    color: #666;
    line-height: 1.4;
}

.notification-close {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    color: #999;
    transition: all 0.3s ease;
}

.notification-close:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #666;
}

/* 动画效果 */
.notification-enter-active,
.notification-leave-active {
    transition: all 0.3s ease;
}

.notification-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.notification-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .notification-toast {
        top: 10px;
        right: 10px;
        left: 10px;
        min-width: auto;
        max-width: none;
    }
}
</style>
