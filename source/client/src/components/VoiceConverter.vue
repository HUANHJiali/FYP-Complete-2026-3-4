<template>
    <div class="voice-converter">
        <div class="converter-header">
            <h3>語音轉換</h3>
            <div class="language-selector">
                <Select v-model="selectedLanguage" class="language-select">
                    <Option value="en-US">英語 (美國)</Option>
                    <Option value="en-GB">英語 (英國)</Option>
                    <Option value="zh-CN">中文 (簡體)</Option>
                    <Option value="zh-TW">中文 (繁體)</Option>
                </Select>
            </div>
        </div>
        
        <div class="converter-content">
            <div class="input-section">
                <div class="input-header">
                    <h4>輸入文字</h4>
                    <div class="input-actions">
                        <Button 
                            size="small" 
                            @click="clearText"
                            :disabled="!inputText"
                        >
                            清空
                        </Button>
                        <Button 
                            size="small" 
                            @click="copyText"
                            :disabled="!inputText"
                        >
                            複製
                        </Button>
                    </div>
                </div>
                <Input 
                    v-model="inputText"
                    type="textarea"
                    :rows="6"
                    placeholder="請輸入要轉換的文字..."
                    class="text-input"
                />
            </div>
            
            <div class="conversion-controls">
                <Button 
                    type="primary" 
                    @click="convertToSpeech"
                    :loading="isConverting"
                    :disabled="!inputText"
                    class="convert-btn"
                >
                    <Icon type="ios-mic" />
                    {{ isConverting ? '轉換中...' : '轉換為語音' }}
                </Button>
                
                <div class="voice-options">
                    <div class="option-group">
                        <label>語音速度:</label>
                        <Slider 
                            v-model="speechRate" 
                            :min="0.5" 
                            :max="2" 
                            :step="0.1"
                            class="rate-slider"
                        />
                        <span class="rate-value">{{ speechRate }}x</span>
                    </div>
                    
                    <div class="option-group">
                        <label>語音音調:</label>
                        <Slider 
                            v-model="speechPitch" 
                            :min="0.5" 
                            :max="2" 
                            :step="0.1"
                            class="pitch-slider"
                        />
                        <span class="pitch-value">{{ speechPitch }}x</span>
                    </div>
                </div>
            </div>
            
            <div class="output-section" v-if="audioUrl">
                <div class="output-header">
                    <h4>語音輸出</h4>
                    <div class="output-actions">
                        <Button 
                            size="small" 
                            @click="playAudio"
                            :disabled="isPlaying"
                        >
                            <Icon type="ios-play" />
                            {{ isPlaying ? '播放中...' : '播放' }}
                        </Button>
                        <Button 
                            size="small" 
                            @click="pauseAudio"
                            :disabled="!isPlaying"
                        >
                            <Icon type="ios-pause" />
                            暫停
                        </Button>
                        <Button 
                            size="small" 
                            @click="downloadAudio"
                        >
                            <Icon type="ios-download" />
                            下載
                        </Button>
                    </div>
                </div>
                
                <div class="audio-player">
                    <audio 
                        ref="audioPlayer"
                        :src="audioUrl"
                        @ended="onAudioEnded"
                        @timeupdate="onTimeUpdate"
                        @loadedmetadata="onAudioLoaded"
                    ></audio>
                    
                    <div class="progress-container">
                        <div class="time-display">
                            <span>{{ currentTime }}</span>
                            <span>{{ duration }}</span>
                        </div>
                        <div class="progress-bar">
                            <div 
                                class="progress-fill"
                                :style="{ width: progressPercent + '%' }"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="conversion-history">
            <h4>轉換歷史</h4>
            <div class="history-list">
                <div 
                    v-for="item in conversionHistory" 
                    :key="item.id"
                    class="history-item"
                    @click="loadHistoryItem(item)"
                >
                    <div class="history-content">
                        <div class="history-text">{{ item.text.substring(0, 50) }}{{ item.text.length > 50 ? '...' : '' }}</div>
                        <div class="history-meta">
                            <span class="history-language">{{ getLanguageName(item.language) }}</span>
                            <span class="history-time">{{ formatTime(item.timestamp) }}</span>
                        </div>
                    </div>
                    <Button 
                        size="small" 
                        type="text" 
                        @click.stop="deleteHistoryItem(item.id)"
                    >
                        <Icon type="ios-trash" />
                    </Button>
                </div>
                
                <div v-if="conversionHistory.length === 0" class="empty-history">
                    <Icon type="ios-mic-outline" />
                    <p>暫無轉換歷史</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'VoiceConverter',
    data() {
        return {
            inputText: '',
            selectedLanguage: 'en-US',
            speechRate: 1,
            speechPitch: 1,
            isConverting: false,
            isPlaying: false,
            audioUrl: null,
            currentTime: '00:00',
            duration: '00:00',
            progressPercent: 0,
            conversionHistory: [],
            speechSynthesis: null
        }
    },
    mounted() {
        this.loadHistory()
        this.initSpeechSynthesis()
    },
    methods: {
        initSpeechSynthesis() {
            if ('speechSynthesis' in window) {
                this.speechSynthesis = window.speechSynthesis
            } else {
                this.$Message.error('您的瀏覽器不支持語音合成功能')
            }
        },
        
        async convertToSpeech() {
            if (!this.inputText.trim()) {
                this.$Message.warning('請輸入要轉換的文字')
                return
            }
            
            this.isConverting = true
            
            try {
                if (this.speechSynthesis) {
                    // 使用瀏覽器內建的語音合成
                    await this.convertWithSpeechSynthesis()
                } else {
                    // 使用外部API（這裡可以集成第三方語音服務）
                    await this.convertWithExternalAPI()
                }
                
                // 保存到歷史記錄
                this.saveToHistory()
                
            } catch (error) {
                console.error('語音轉換失敗:', error)
                this.$Message.error('語音轉換失敗，請重試')
            } finally {
                this.isConverting = false
            }
        },
        
        async convertWithSpeechSynthesis() {
            return new Promise((resolve, reject) => {
                const utterance = new SpeechSynthesisUtterance(this.inputText)
                utterance.lang = this.selectedLanguage
                utterance.rate = this.speechRate
                utterance.pitch = this.speechPitch
                
                utterance.onend = () => {
                    this.isPlaying = false
                    resolve()
                }
                
                utterance.onerror = (error) => {
                    reject(error)
                }
                
                this.speechSynthesis.speak(utterance)
                this.isPlaying = true
            })
        },
        
        async convertWithExternalAPI() {
            // 這裡可以集成第三方語音服務，如Google Text-to-Speech API
            // 目前使用模擬實現
            await new Promise(resolve => setTimeout(resolve, 2000))
            
            // 創建模擬的音頻URL
            this.audioUrl = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT'
        },
        
        playAudio() {
            if (this.$refs.audioPlayer) {
                this.$refs.audioPlayer.play()
                this.isPlaying = true
            }
        },
        
        pauseAudio() {
            if (this.$refs.audioPlayer) {
                this.$refs.audioPlayer.pause()
                this.isPlaying = false
            }
        },
        
        downloadAudio() {
            if (this.audioUrl) {
                const link = document.createElement('a')
                link.href = this.audioUrl
                link.download = `voice_${Date.now()}.wav`
                link.click()
            }
        },
        
        onAudioEnded() {
            this.isPlaying = false
            this.progressPercent = 0
            this.currentTime = '00:00'
        },
        
        onTimeUpdate() {
            const audio = this.$refs.audioPlayer
            if (audio) {
                this.progressPercent = (audio.currentTime / audio.duration) * 100
                this.currentTime = this.formatAudioTime(audio.currentTime)
            }
        },
        
        onAudioLoaded() {
            const audio = this.$refs.audioPlayer
            if (audio) {
                this.duration = this.formatAudioTime(audio.duration)
            }
        },
        
        formatAudioTime(seconds) {
            const mins = Math.floor(seconds / 60)
            const secs = Math.floor(seconds % 60)
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        },
        
        clearText() {
            this.inputText = ''
        },
        
        copyText() {
            navigator.clipboard.writeText(this.inputText).then(() => {
                this.$Message.success('文字已複製到剪貼板')
            })
        },
        
        saveToHistory() {
            const historyItem = {
                id: Date.now(),
                text: this.inputText,
                language: this.selectedLanguage,
                timestamp: new Date().toISOString()
            }
            
            this.conversionHistory.unshift(historyItem)
            
            // 只保留最近20條記錄
            if (this.conversionHistory.length > 20) {
                this.conversionHistory = this.conversionHistory.slice(0, 20)
            }
            
            this.saveHistory()
        },
        
        loadHistoryItem(item) {
            this.inputText = item.text
            this.selectedLanguage = item.language
        },
        
        deleteHistoryItem(id) {
            this.conversionHistory = this.conversionHistory.filter(item => item.id !== id)
            this.saveHistory()
        },
        
        getLanguageName(code) {
            const languages = {
                'en-US': '英語 (美國)',
                'en-GB': '英語 (英國)',
                'zh-CN': '中文 (簡體)',
                'zh-TW': '中文 (繁體)'
            }
            return languages[code] || code
        },
        
        formatTime(timestamp) {
            const date = new Date(timestamp)
            return date.toLocaleString()
        },
        
        saveHistory() {
            localStorage.setItem('voiceConversionHistory', JSON.stringify(this.conversionHistory))
        },
        
        loadHistory() {
            const saved = localStorage.getItem('voiceConversionHistory')
            if (saved) {
                this.conversionHistory = JSON.parse(saved)
            }
        }
    }
}
</script>

<style scoped>
.voice-converter {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}

.converter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.converter-header h3 {
    margin: 0;
    color: #333;
    font-size: 20px;
    font-weight: 600;
}

.language-selector {
    display: flex;
    align-items: center;
    gap: 10px;
}

.language-select {
    width: 150px;
}

.converter-content {
    display: grid;
    gap: 20px;
}

.input-section, .output-section {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
}

.input-header, .output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.input-header h4, .output-header h4 {
    margin: 0;
    color: #333;
    font-size: 16px;
    font-weight: 600;
}

.input-actions, .output-actions {
    display: flex;
    gap: 8px;
}

.text-input {
    width: 100%;
}

.conversion-controls {
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    color: white;
}

.convert-btn {
    padding: 12px 30px;
    font-size: 16px;
    border-radius: 25px;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    transition: all 0.3s ease;
}

.convert-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.voice-options {
    display: flex;
    gap: 30px;
    align-items: center;
}

.option-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.option-group label {
    font-size: 14px;
    font-weight: 500;
    min-width: 80px;
}

.rate-slider, .pitch-slider {
    width: 120px;
}

.rate-value, .pitch-value {
    font-size: 12px;
    font-weight: 600;
    min-width: 40px;
    text-align: center;
}

.audio-player {
    background: #fff;
    border-radius: 8px;
    padding: 15px;
}

.progress-container {
    margin-top: 15px;
}

.time-display {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #666;
    margin-bottom: 8px;
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    transition: width 0.1s ease;
}

.conversion-history {
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.conversion-history h4 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 16px;
    font-weight: 600;
}

.history-list {
    max-height: 300px;
    overflow-y: auto;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    margin-bottom: 8px;
    background: #f8f9fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.history-item:hover {
    background: #e9ecef;
    transform: translateX(5px);
}

.history-content {
    flex: 1;
}

.history-text {
    font-size: 14px;
    color: #333;
    margin-bottom: 4px;
}

.history-meta {
    display: flex;
    gap: 15px;
    font-size: 12px;
    color: #666;
}

.history-language {
    background: #667eea;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
}

.empty-history {
    text-align: center;
    padding: 40px 20px;
    color: #999;
}

.empty-history .ivu-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.empty-history p {
    margin: 0;
    font-size: 14px;
}

/* 深色主題適配 */
.dark-theme .voice-converter {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .converter-header h3,
.dark-theme .input-header h4,
.dark-theme .output-header h4,
.dark-theme .conversion-history h4 {
    color: #fff;
}

.dark-theme .input-section,
.dark-theme .output-section {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .history-item {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .history-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.dark-theme .history-text {
    color: #fff;
}

.dark-theme .history-meta {
    color: #ccc;
}

.dark-theme .time-display {
    color: #ccc;
}

.dark-theme .progress-bar {
    background: #404040;
}

.dark-theme .audio-player {
    background: rgba(255, 255, 255, 0.05);
}

/* 響應式設計 */
@media (max-width: 768px) {
    .converter-header {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }
    
    .language-select {
        width: 100%;
    }
    
    .voice-options {
        flex-direction: column;
        gap: 15px;
    }
    
    .option-group {
        width: 100%;
        justify-content: space-between;
    }
    
    .rate-slider, .pitch-slider {
        width: 100px;
    }
}
</style>
