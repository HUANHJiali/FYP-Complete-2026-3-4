<template>
  <div class="ai-scoring-container">
    <div class="ai-scoring-header">
      <h2>AI智能评分系统</h2>
      <p>使用人工智能技术对学生答案进行智能评分和分析</p>
    </div>

    <div class="ai-scoring-form">
      <div class="form-group">
        <label>题目内容：</label>
        <textarea 
          v-model="formData.questionContent" 
          placeholder="请输入题目内容"
          rows="4"
        ></textarea>
      </div>

      <div class="form-group">
        <label>题目类型：</label>
        <select v-model="formData.questionType">
          <option value="0">选择题</option>
          <option value="1">填空题</option>
          <option value="2">判断题</option>
          <option value="3">编程题</option>
        </select>
      </div>

      <div class="form-group">
        <label>正确答案：</label>
        <textarea 
          v-model="formData.correctAnswer" 
          placeholder="请输入正确答案"
          rows="3"
        ></textarea>
      </div>

      <div class="form-group">
        <label>学生答案：</label>
        <textarea 
          v-model="formData.studentAnswer" 
          placeholder="请输入学生答案"
          rows="3"
        ></textarea>
      </div>

      <div class="form-group">
        <label>最大分值：</label>
        <input 
          type="number" 
          v-model="formData.maxScore" 
          min="1" 
          max="100"
          step="0.5"
        />
      </div>

      <div class="form-actions">
        <button @click="scoreAnswer" :disabled="loading" class="btn-primary">
          {{ loading ? '评分中...' : '开始AI评分' }}
        </button>
        <button @click="resetForm" class="btn-secondary">重置</button>
      </div>

    <div v-if="progressText" class="progress-message">{{ progressText }}</div>
    </div>

    <div v-if="scoringResult" class="scoring-result">
      <h3>评分结果</h3>
      <div class="result-card">
        <div class="score-section">
          <div class="score-display">
            <span class="score">{{ scoringResult.score }}</span>
            <span class="max-score">/ {{ formData.maxScore }}</span>
          </div>
          <div class="score-percentage">
            {{ ((scoringResult.score / formData.maxScore) * 100).toFixed(1) }}%
          </div>
        </div>

        <div class="result-details">
          <div class="detail-item">
            <label>是否正确：</label>
            <span :class="scoringResult.isCorrect ? 'correct' : 'incorrect'">
              {{ scoringResult.isCorrect ? '正确' : '错误' }}
            </span>
          </div>

          <div class="detail-item">
            <label>AI反馈：</label>
            <p class="feedback">{{ scoringResult.feedback }}</p>
          </div>

          <div class="detail-item">
            <label>详细分析：</label>
            <p class="analysis">{{ scoringResult.analysis }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import http from '../utils/http'

export default {
  name: 'AIScoring',
  setup() {
    const loading = ref(false)
    const error = ref('')
    const progressText = ref('')
    const scoringResult = ref(null)

    const formData = reactive({
      questionContent: '',
      questionType: '0',
      correctAnswer: '',
      studentAnswer: '',
      maxScore: 10.0
    })

    const withRetry = async (fn, { attempts = 3, baseDelayMs = 800 } = {}) => {
      let lastErr
      for (let i = 1; i <= attempts; i++) {
        try {
          progressText.value = i === 1 ? '正在请求AI服务…' : `AI繁忙，正在重试（第${i}次）…`
          const res = await fn()
          progressText.value = ''
          return res
        } catch (e) {
          lastErr = e
          if (i < attempts) {
            const delay = baseDelayMs * i
            await new Promise(r => setTimeout(r, delay))
          }
        }
      }
      progressText.value = ''
      throw lastErr
    }

    const scoreAnswer = async () => {
      if (!formData.questionContent || !formData.correctAnswer || !formData.studentAnswer) {
        error.value = '请填写所有必要字段'
        return
      }

      loading.value = true
      error.value = ''

      try {
        const response = await withRetry(() => http.post('/ai/score_answer/', {
          questionContent: formData.questionContent,
          questionType: parseInt(formData.questionType),
          correctAnswer: formData.correctAnswer,
          studentAnswer: formData.studentAnswer,
          maxScore: parseFloat(formData.maxScore)
        }))
        if (response.code === 0) {
          scoringResult.value = response.data
        } else {
          error.value = response.msg || '评分失败'
        }
      } catch (err) {
        console.error('AI评分失败:', err)
        error.value = 'AI繁忙或网络异常，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      formData.questionContent = ''
      formData.questionType = '0'
      formData.correctAnswer = ''
      formData.studentAnswer = ''
      formData.maxScore = 10.0
      scoringResult.value = null
      error.value = ''
      progressText.value = ''
    }

    return {
      loading,
      error,
      progressText,
      scoringResult,
      formData,
      scoreAnswer,
      resetForm
    }
  }
}
</script>

<style scoped>
.ai-scoring-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.ai-scoring-header {
  text-align: center;
  margin-bottom: 30px;
}

.ai-scoring-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.ai-scoring-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.ai-scoring-form {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.scoring-result {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.scoring-result h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.result-card {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  overflow: hidden;
}

.score-section {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  padding: 30px;
  text-align: center;
}

.score-display {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
}

.max-score {
  font-size: 24px;
  opacity: 0.8;
}

.score-percentage {
  font-size: 18px;
  opacity: 0.9;
}

.result-details {
  padding: 30px;
}

.detail-item {
  margin-bottom: 20px;
}

.detail-item label {
  font-weight: 600;
  color: #2c3e50;
  display: block;
  margin-bottom: 8px;
}

.detail-item p {
  margin: 0;
  line-height: 1.6;
  color: #34495e;
}

.feedback,
.analysis {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.correct {
  color: #27ae60;
  font-weight: bold;
}

.incorrect {
  color: #e74c3c;
  font-weight: bold;
}

.error-message {
  background: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.progress-message {
  background: #fff8e1;
  color: #8a6d3b;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border-left: 4px solid #f39c12;
}
</style>
