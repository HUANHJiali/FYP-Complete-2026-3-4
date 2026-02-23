<template>
    <div class="loading-overlay" v-if="visible">
        <div class="loading-container">
            <div class="loading-spinner">
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
            </div>
            <div class="loading-text">{{ text }}</div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'LoadingSpinner',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        text: {
            type: String,
            default: '加载中...'
        }
    }
}
</script>

<style scoped>
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    animation: fadeIn 0.3s ease;
}

.loading-container {
    text-align: center;
    padding: 40px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.loading-spinner {
    position: relative;
    width: 60px;
    height: 60px;
    margin: 0 auto 20px;
}

.spinner-ring {
    position: absolute;
    width: 100%;
    height: 100%;
    border: 3px solid transparent;
    border-top: 3px solid #667eea;
    border-radius: 50%;
    animation: spin 1.2s linear infinite;
}

.spinner-ring:nth-child(2) {
    width: 80%;
    height: 80%;
    top: 10%;
    left: 10%;
    border-top-color: #764ba2;
    animation-delay: -0.4s;
}

.spinner-ring:nth-child(3) {
    width: 60%;
    height: 60%;
    top: 20%;
    left: 20%;
    border-top-color: #19be6b;
    animation-delay: -0.8s;
}

.loading-text {
    font-size: 16px;
    font-weight: 500;
    color: #333;
    margin-top: 10px;
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

/* 响应式设计 */
@media (max-width: 768px) {
    .loading-container {
        padding: 30px 20px;
        margin: 20px;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
    }
    
    .loading-text {
        font-size: 14px;
    }
}
</style>
