<template>
  <div class="ai-question-generator">
    <div class="generator-header">
      <h2>AI智能题目生成器</h2>
      <p>使用人工智能技术自动生成高质量的教育题目</p>
    </div>

    <div class="generator-form">
      <div class="form-row">
        <div class="form-group">
          <label>科目：</label>
          <input 
            v-model="formData.subject" 
            placeholder="例如：数学、英语、计算机科学"
          />
        </div>

        <div class="form-group">
          <label>主题/章节：</label>
          <input 
            v-model="formData.topic" 
            placeholder="例如：函数、语法、数据结构"
          />
        </div>
      </div>

      <div class="form-row">
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
          <label>难度等级：</label>
          <select v-model="formData.difficulty">
            <option value="easy">简单</option>
            <option value="medium">中等</option>
            <option value="hard">困难</option>
          </select>
        </div>

        <div class="form-group">
          <label>生成数量：</label>
          <input 
            type="number" 
            v-model="formData.count" 
            min="1" 
            max="20"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>选择学科（用于入库/生成试卷）：</label>
          <select v-model="formData.subjectId">
            <option disabled value="">请选择学科</option>
            <option v-for="p in projects" :key="p.id" :value="String(p.id)">{{ p.name }}（ID: {{ p.id }}）</option>
          </select>
        </div>

        <div class="form-group">
          <label>选择教师（用于生成试卷）：</label>
          <select v-model="formData.teacherId">
            <option disabled value="">请选择教师</option>
            <option v-for="t in teachers" :key="t.id" :value="String(t.id)">{{ t.id }}（{{ t.name }}）</option>
          </select>
        </div>

        <div class="form-group">
          <label>试卷标题（可选）：</label>
          <input 
            v-model="formData.paperTitle" 
            placeholder="例如：AI自动生成练习卷"
          />
        </div>
      </div>

      <div class="form-actions">
        <button @click="generateQuestions" :disabled="loading" class="btn-primary">
          {{ loading ? '生成中...' : '仅生成（不入库）' }}
        </button>
        <button @click="generateAndSave" :disabled="loading || !formData.subjectId" class="btn-success">
          {{ loading ? '生成中...' : '生成并保存到题库' }}
        </button>
        <button @click="generateBatchAndSave" :disabled="loading || !formData.subjectId" class="btn-success">
          {{ loading ? '生成中...' : '多类型批量生成并保存' }}
        </button>
        <button @click="generatePracticePaper" :disabled="loading || !formData.subjectId || !formData.teacherId" class="btn-success">
          {{ loading ? '生成中...' : 'AI 生成练习试卷并入库' }}
        </button>
        <button @click="generatePracticePaperCounts" :disabled="loading || !formData.subjectId || !formData.teacherId" class="btn-success">
          {{ loading ? '生成中...' : '按题量一键生成试卷(10/10/10/2)' }}
        </button>
        <button v-if="loading" @click="cancelGeneration" class="btn-secondary">取消生成</button>
        <button @click="resetForm" class="btn-secondary">重置</button>
      </div>
    <div v-if="progressText" class="progress-message">{{ progressText }}</div>
    </div>

    <div v-if="generatedQuestions.length > 0" class="generated-questions">
      <h3>生成的题目 ({{ generatedQuestions.length }}道)</h3>
      
      <div class="questions-list">
        <div 
          v-for="(question, index) in generatedQuestions" 
          :key="index"
          class="question-card"
        >
          <div class="question-header">
            <span class="question-number">题目 {{ index + 1 }}</span>
            <span class="question-type">{{ getQuestionTypeName(question.type) }}</span>
            <span class="question-difficulty">{{ getDifficultyName(question.difficulty) }}</span>
          </div>

          <div class="question-content">
            <h4>题目内容：</h4>
            <p>{{ question.content }}</p>
          </div>

          <div v-if="question.options && question.options.length > 0" class="question-options">
            <h4>选项：</h4>
            <ul>
              <li v-for="(option, optIndex) in question.options" :key="optIndex">
                {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
              </li>
            </ul>
          </div>

          <div class="question-answer">
            <h4>正确答案：</h4>
            <p class="answer-text">{{ question.answer }}</p>
          </div>

          <div class="question-analysis">
            <h4>题目解析：</h4>
            <p>{{ question.analysis }}</p>
          </div>

          <div v-if="question.knowledge_points" class="question-knowledge">
            <h4>涉及知识点：</h4>
            <p>{{ question.knowledge_points }}</p>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <button @click="saveToDatabase" :disabled="saving" class="btn-success">
          {{ saving ? '保存中...' : '保存到题库' }}
        </button>
        <button @click="exportQuestions" class="btn-export">导出题目</button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import http from '../utils/http'

export default {
  name: 'AIQuestionGenerator',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const error = ref('')
    const progressText = ref('')
    const successMessage = ref('')
    const generatedQuestions = ref([])

    const projects = ref([])
    const teachers = ref([])
    const cancelSource = ref(null)

    const formData = reactive({
      subject: '',
      topic: '',
      questionType: '0',
      difficulty: 'medium',
      count: 5,
      subjectId: '', // 入库所需学科ID
      teacherId: '', // 生成试卷所需教师ID
      paperTitle: ''
    })

    // 载入学科与教师下拉
    const loadMeta = async () => {
      try {
        const pr = await http.get('/projects/all/')
        if (pr.code === 0) projects.value = pr.data || []
      } catch (_) {}
      try {
        const tr = await http.get('/teachers/page/', { params: { pageIndex: 1, pageSize: 500 } })
        if (tr.code === 0) {
          const d = tr.data || {}
          teachers.value = d.data || []
        }
      } catch (_) {}
    }
    onMounted(loadMeta)

    const withRetry = async (fn, { attempts = 3, baseDelayMs = 800 } = {}) => {
      let lastErr
      for (let i = 1; i <= attempts; i++) {
        try {
          progressText.value = i === 1 ? '正在请求AI服务…' : `AI繁忙，正在重试（第${i}次）…`
          const res = await fn()
          progressText.value = ''
          return res
        } catch (e) {
          if (axios.isCancel && axios.isCancel(e)) throw e
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

    const generateQuestions = async () => {
      // 验证表单
      if (!formData.subject || !formData.topic) {
        error.value = '请填写科目和主题'
        return
      }

      loading.value = true
      error.value = ''
      successMessage.value = ''

      cancelSource.value = axios.CancelToken ? axios.CancelToken.source() : null
      try {
        const response = await withRetry(() => http.post(
          '/ai/generate_questions/',
          {
            subject: formData.subject,
            topic: formData.topic,
            questionType: parseInt(formData.questionType),
            difficulty: formData.difficulty,
            count: parseInt(formData.count)
          },
          {
            // AI生成可能较慢，放宽超时时间，避免前端15s默认超时
            timeout: 60000,
            cancelToken: cancelSource.value ? cancelSource.value.token : undefined
          }
        ))
        if (response.code === 0) {
          generatedQuestions.value = response.data.questions
          successMessage.value = `成功生成 ${response.data.count} 道题目`
        } else {
          error.value = response.msg || '生成题目失败'
        }
      } catch (err) {
        if (axios.isCancel && axios.isCancel(err)) {
          error.value = '已取消'
        } else {
          console.error('AI生成题目失败:', err)
          error.value = 'AI繁忙或网络异常，请稍后重试'
        }
      } finally {
        loading.value = false
        cancelSource.value = null
      }
    }

    const generateAndSave = async () => {
      // 验证表单
      if (!formData.subject || !formData.topic) {
        error.value = '请填写科目和主题'
        return
      }
      if (!formData.subjectId) {
        error.value = '请选择或填写学科ID（用于入库）'
        return
      }

      loading.value = true
      error.value = ''
      successMessage.value = ''

      cancelSource.value = axios.CancelToken ? axios.CancelToken.source() : null
      try {
        const payload = {
          subject: formData.subject,
          topic: formData.topic,
          questionType: parseInt(formData.questionType),
          difficulty: formData.difficulty,
          count: parseInt(formData.count),
          subjectId: formData.subjectId
        }
        const response = await withRetry(() => http.post(
          '/admin/generateAIQuestions/',
          payload,
          { timeout: 60000, cancelToken: cancelSource.value ? cancelSource.value.token : undefined }
        ))
        if (response.code === 0) {
          successMessage.value = response.data?.message || '生成并保存成功'
          generatedQuestions.value = []
        } else {
          error.value = response.msg || '生成并保存失败'
        }
      } catch (err) {
        if (axios.isCancel && axios.isCancel(err)) {
          error.value = '已取消'
        } else {
          console.error('AI生成并保存失败:', err)
          error.value = 'AI繁忙或网络异常，请稍后重试'
        }
      } finally {
        loading.value = false
        cancelSource.value = null
      }
    }

    const generatePracticePaper = async () => {
      // 验证表单
      if (!formData.subject || !formData.topic) {
        error.value = '请填写科目和主题'
        return
      }
      if (!formData.subjectId || !formData.teacherId) {
        error.value = '请填写学科ID与教师ID'
        return
      }

      loading.value = true
      error.value = ''
      successMessage.value = ''

      cancelSource.value = axios.CancelToken ? axios.CancelToken.source() : null
      try {
        const payload = {
          subject: formData.subject,
          topic: formData.topic,
          questionType: parseInt(formData.questionType),
          difficulty: formData.difficulty,
          count: parseInt(formData.count),
          subjectId: formData.subjectId,
          teacherId: formData.teacherId,
          title: formData.paperTitle || undefined,
          duration: 60,
          totalScore: 100
        }
        const response = await withRetry(() => http.post(
          '/admin/generate_ai_practice_paper/',
          payload,
          { timeout: 90000, cancelToken: cancelSource.value ? cancelSource.value.token : undefined }
        ))
        if (response.code === 0) {
          const d = response.data || {}
          successMessage.value = `试卷已创建：${d.title || ''}（ID: ${d.paperId}，题数: ${d.questionCount}）`
          generatedQuestions.value = []
        } else {
          error.value = response.msg || '生成试卷失败'
        }
      } catch (err) {
        if (axios.isCancel && axios.isCancel(err)) {
          error.value = '已取消'
        } else {
          console.error('AI生成试卷失败:', err)
          error.value = 'AI繁忙或网络异常，请稍后重试'
        }
      } finally {
        loading.value = false
        cancelSource.value = null
      }
    }

    const generateBatchAndSave = async () => {
      if (!formData.subject || !formData.topic) { error.value = '请填写科目和主题'; return }
      if (!formData.subjectId) { error.value = '请选择或填写学科ID（用于入库）'; return }

      loading.value = true
      error.value = ''
      successMessage.value = ''

      cancelSource.value = axios.CancelToken ? axios.CancelToken.source() : null
      try {
        const types = [0,1,2,3]
        const payload = {
          subject: formData.subject,
          topic: formData.topic,
          difficulty: formData.difficulty,
          subjectId: formData.subjectId,
          questionTypes: JSON.stringify(types),
          count: parseInt(formData.count) || 20
        }
        const response = await withRetry(() => http.post(
          '/admin/generateAIQuestionsBatch/', payload, { timeout: 120000, cancelToken: cancelSource.value ? cancelSource.value.token : undefined }
        ))
        if (response.code === 0) {
          const d = response.data || {}
          successMessage.value = `生成成功：共 ${d.created} 题，各类型 ${JSON.stringify(d.createdByType)}`
          generatedQuestions.value = []
        } else {
          error.value = response.msg || '批量生成失败'
        }
      } catch (err) {
        if (axios.isCancel && axios.isCancel(err)) {
          error.value = '已取消'
        } else {
          console.error('批量生成失败:', err)
          error.value = 'AI繁忙或网络异常，请稍后重试'
        }
      } finally {
        loading.value = false
        cancelSource.value = null
      }
    }

    const generatePracticePaperCounts = async () => {
      if (!formData.subject || !formData.topic) { error.value = '请填写科目和主题'; return }
      if (!formData.subjectId || !formData.teacherId) { error.value = '请选择学科和教师'; return }
      loading.value = true
      error.value = ''
      successMessage.value = ''
      cancelSource.value = axios.CancelToken ? axios.CancelToken.source() : null
      try {
        const payload = {
          subject: formData.subject,
          topic: formData.topic,
          difficulty: formData.difficulty,
          subjectId: formData.subjectId,
          teacherId: formData.teacherId,
          title: formData.paperTitle || undefined,
          duration: 60,
          counts: '0:10,1:10,2:10,3:2'
        }
        const resp = await withRetry(() => http.post('/admin/generate_ai_practice_paper_counts/', payload, { timeout: 120000, cancelToken: cancelSource.value ? cancelSource.value.token : undefined }))
        if (resp.code === 0) {
          const d = resp.data || {}
          successMessage.value = `试卷已创建：${d.title}（ID: ${d.paperId}，总分：${d.totalScore}）`
        } else {
          error.value = resp.msg || '生成失败'
        }
      } catch (e) {
        if (axios.isCancel && axios.isCancel(e)) {
          error.value = '已取消'
        } else {
          console.error('按题量生成失败', e)
          error.value = 'AI繁忙或网络异常，请稍后重试'
        }
      } finally { loading.value = false; cancelSource.value = null }
    }

    const cancelGeneration = () => {
      try {
        if (cancelSource.value && typeof cancelSource.value.cancel === 'function') {
          cancelSource.value.cancel('canceled by user')
        }
      } catch (_) {}
      error.value = '已取消'
      progressText.value = ''
      loading.value = false
    }

    const exportQuestions = () => {
      if (generatedQuestions.value.length === 0) {
        error.value = '没有可导出的题目'
        return
      }

      const exportData = {
        subject: formData.subject,
        topic: formData.topic,
        difficulty: formData.difficulty,
        generatedTime: new Date().toISOString(),
        questions: generatedQuestions.value
      }

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `AI生成题目_${formData.subject}_${formData.topic}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      successMessage.value = '题目导出成功'
    }

    const resetForm = () => {
      formData.subject = ''
      formData.topic = ''
      formData.questionType = '0'
      formData.difficulty = 'medium'
      formData.count = 5
      generatedQuestions.value = []
      error.value = ''
      successMessage.value = ''
    }

    const getQuestionTypeName = (type) => {
      const types = {
        0: '选择题',
        1: '填空题',
        2: '判断题',
        3: '编程题'
      }
      return types[type] || '未知类型'
    }

    const getDifficultyName = (difficulty) => {
      const difficulties = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return difficulties[difficulty] || '未知难度'
    }

    return {
      loading,
      saving,
      error,
      progressText,
      successMessage,
      generatedQuestions,
      projects,
      teachers,
      formData,
      generateQuestions,
      generateAndSave,
      generateBatchAndSave,
      exportQuestions,
      generatePracticePaper,
      generatePracticePaperCounts,
      resetForm,
      getQuestionTypeName,
      getDifficultyName,
      cancelGeneration
    }
  }
}
</script>

<style scoped>
.ai-question-generator {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.generator-header {
  text-align: center;
  margin-bottom: 30px;
}

.generator-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.generator-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.generator-form {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
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
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-export {
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

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229954;
}

.btn-success:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-export {
  background: #f39c12;
  color: white;
}

.btn-export:hover {
  background: #e67e22;
}

.generated-questions {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.generated-questions h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.questions-list {
  display: grid;
  gap: 20px;
}

.question-card {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ecf0f1;
}

.question-number {
  font-weight: bold;
  color: #2c3e50;
}

.question-type {
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.question-difficulty {
  background: #e74c3c;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.question-content,
.question-options,
.question-answer,
.question-analysis,
.question-knowledge {
  margin-bottom: 15px;
}

.question-content h4,
.question-options h4,
.question-answer h4,
.question-analysis h4,
.question-knowledge h4 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 14px;
}

.question-content p,
.question-answer p,
.question-analysis p,
.question-knowledge p {
  margin: 0;
  line-height: 1.6;
  color: #34495e;
}

.question-options ul {
  margin: 0;
  padding-left: 20px;
}

.question-options li {
  margin-bottom: 5px;
  color: #34495e;
}

.answer-text {
  background: #d5f4e6;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #27ae60;
  font-weight: bold;
}

.actions-footer {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.error-message {
  background: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.success-message {
  background: #27ae60;
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
