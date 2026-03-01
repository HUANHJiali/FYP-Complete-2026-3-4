<template>
  <div class="admin-questions">
    <div class="page-header">
      <h2>题目管理</h2>
      <div>
        <Upload :before-upload="beforeImport" :show-upload-list="false" action="#">
          <Button style="margin-right:8px" :loading="importLoading">导入CSV</Button>
        </Upload>
        <Button style="margin-right:8px" @click="downloadTemplate">下载模板</Button>
        <Button style="margin-right:8px" @click="exportCsv">导出CSV</Button>
        <Button type="primary" @click="showAddModal">创建题目</Button>
      </div>
    </div>

    <div class="search-section">
      <Input 
        v-model="searchKeyword" 
        placeholder="请输入题目内容或描述" 
        style="width: 300px; margin-right: 16px;"
        @on-enter="handleSearch"
      />
      <Select 
        v-model="searchType" 
        placeholder="题目类型" 
        style="width: 150px; margin-right: 16px;"
        clearable
      >
        <Option :value="0">选择题</Option>
        <Option :value="1">填空题</Option>
        <Option :value="2">判断题</Option>
        <Option :value="3">简答题</Option>
        <Option :value="4">编程题</Option>
        <Option :value="5">综合题</Option>
      </Select>
       <Select 
        v-model="searchProject" 
        placeholder="所属学科" 
        style="width: 150px; margin-right: 16px;"
         clearable
         filterable
      >
        <Option 
          v-for="project in projects" 
          :key="project.id" 
          :value="String(project.id)"
          :label="String(project.name)"
        >
          {{ project.name }}
        </Option>
      </Select>
      <Button type="primary" @click="handleSearch">搜索</Button>
      <Button @click="resetSearch" style="margin-left: 8px;">重置</Button>
    </div>

    <Table 
      :columns="columns" 
      :data="questions" 
      :loading="loading"
      :pagination="pagination"
      @on-page-change="handlePageChange"
      @on-page-size-change="handlePageSizeChange"
    >
      <template #questionContent="{ row }">
        <div style="max-width:300px;">
          <QuestionContentRenderer :content="row.name" compact />
        </div>
      </template>
      <template #action="{ row }">
        <Button type="primary" size="small" @click="editQuestion(row)" style="margin-right: 8px;">编辑</Button>
        <Button type="error" size="small" @click="deleteQuestion(row)">删除</Button>
      </template>
    </Table>

    <!-- 添加/编辑题目模态框 -->
    <Modal 
      v-model="showModal" 
      :title="isEdit ? '编辑题目' : '创建题目'"
      width="900"
      @on-ok="handleSubmit"
      @on-cancel="handleCancel"
    >
      <Form ref="formRef" :model="formData" :rules="formRules" :label-width="100">
        <Row :gutter="16">
          <Col span="12">
            <FormItem label="题目类型" prop="type">
              <Select v-model="formData.type" placeholder="请选择题目类型" @on-change="onTypeChange">
                <Option :value="0">选择题</Option>
                <Option :value="1">填空题</Option>
                <Option :value="2">判断题</Option>
                <Option :value="3">简答题</Option>
                <Option :value="4">编程题</Option>
                <Option :value="5">综合题</Option>
              </Select>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="所属学科" prop="project">
              <Select v-model="formData.project" placeholder="请选择学科" filterable>
                <Option 
                  v-for="project in projects" 
                  :key="project.id" 
                  :value="String(project.id)"
                  :label="String(project.name)"
                >
                  {{ project.name }}
                </Option>
              </Select>
            </FormItem>
          </Col>
        </Row>
        <Row :gutter="16">
          <Col span="12">
            <FormItem label="难度等级" prop="difficulty">
              <Select v-model="formData.difficulty" placeholder="请选择难度">
                <Option value="easy">简单</Option>
                <Option value="medium">中等</Option>
                <Option value="hard">困难</Option>
              </Select>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="分值" prop="score">
              <InputNumber v-model="formData.score" :min="1" :max="100" style="width: 100%" />
            </FormItem>
          </Col>
        </Row>
        <FormItem label="题目内容" prop="name">
          <Input 
            v-model="formData.name" 
            type="textarea" 
            :rows="4"
            placeholder="请输入题目内容，支持文本、图片、数学公式、表格等" 
          />
        </FormItem>
        
        <!-- 选项部分（仅选择题 0） -->
        <div v-if="formData.type === 0">
          <FormItem label="选项设置">
            <div v-for="(option, index) in formData.options" :key="index" class="option-item">
              <Row :gutter="16">
                <Col span="2">
                  <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
                </Col>
                <Col span="16">
                  <Input 
                    v-model="option.content" 
                    placeholder="请输入选项内容"
                    @on-blur="validateOptions"
                  />
                </Col>
                <Col span="4">
                  <Checkbox 
                    v-model="option.isCorrect" 
                    :disabled="formData.type === 0 && getCorrectOptionsCount() > 0 && !option.isCorrect"
                  >
                    正确答案
                  </Checkbox>
                </Col>
                <Col span="2" v-if="formData.options.length > 2">
                  <Button 
                    type="text" 
                    icon="md-close" 
                    @click="removeOption(index)"
                    :disabled="formData.options.length <= 2"
                  />
                </Col>
              </Row>
            </div>
            <Button type="dashed" @click="addOption" style="margin-top: 8px;">
              <Icon type="md-add" />
              添加选项
            </Button>
          </FormItem>
        </div>

        <!-- 判断题答案 -->
        <FormItem label="正确答案" prop="correctAnswer" v-if="formData.type === 2">
          <RadioGroup v-model="formData.correctAnswer">
            <Radio value="true">正确</Radio>
            <Radio value="false">错误</Radio>
          </RadioGroup>
        </FormItem>

        <!-- 填空题答案 -->
        <FormItem label="正确答案" prop="correctAnswer" v-if="formData.type === 1">
          <Input 
             v-model="formData.correctAnswer" 
             placeholder="请输入正确答案"
           />
         </FormItem>
 
         <!-- 简答题答案 -->
         <FormItem label="参考答案" prop="correctAnswer" v-if="formData.type === 3">
           <Input 
             v-model="formData.correctAnswer" 
             type="textarea" 
             :rows="3"
             placeholder="请输入参考答案" 
           />
         </FormItem>
 
         <!-- 编程题答案 -->
         <FormItem label="参考答案" prop="correctAnswer" v-if="formData.type === 4">
           <Input 
             v-model="formData.correctAnswer" 
             type="textarea" 
             :rows="5"
             placeholder="请输入参考答案或代码" 
           />
         </FormItem>
 
         <!-- 综合题答案 -->
         <FormItem label="参考答案" prop="correctAnswer" v-if="formData.type === 5">
           <Input 
             v-model="formData.correctAnswer" 
             type="textarea" 
             :rows="6"
             placeholder="请输入详细解答方案" 
           />
         </FormItem>

        <FormItem label="题目解析" prop="analysis">
          <Input 
            v-model="formData.analysis" 
            type="textarea" 
            :rows="3"
            placeholder="请输入题目解析" 
          />
        </FormItem>
        
        <FormItem label="是否启用" prop="isActive">
          <Switch v-model="formData.isActive" />
        </FormItem>
      </Form>
    </Modal>

    <!-- 删除确认模态框 -->
    <Modal v-model="showDeleteModal" title="确认删除" @on-ok="confirmDelete">
      <p>确定要删除这道题目吗？此操作不可恢复。</p>
    </Modal>
  </div>
</template>

<script>
  import { getAdminQuestions, addAdminQuestion, updateAdminQuestion, deleteAdminQuestion, getAllProjects, importAdminQuestions, exportAdminQuestions, downloadQuestionsTemplate } from '@/api'
  import QuestionContentRenderer from '@/components/QuestionContentRenderer.vue'
  import { triggerBlobDownload } from '@/utils/fileDownload'

export default {
  name: 'AdminQuestions',
  components: {
    QuestionContentRenderer
  },
  data() {
    return {
      loading: false,
      searchKeyword: '',
      searchType: '',
      searchProject: '',
      questions: [],
      projects: [],
      columns: [
        { title: 'ID', key: 'id', width: 80 },
        { title: '题目内容', slot: 'questionContent', minWidth: 300 },
        { title: '题目类型', key: 'type', width: 100,
          render: (h, params) => {
            const typeMap = {
              0: '选择题',
              1: '填空题',
              2: '判断题',
              3: '简答题',
              4: '编程题',
              5: '综合题'
            }
            const typeVal = Number(params.row.type)
            const typeText = typeMap[typeVal] || '未知'
            return h('Tag', {
              props: {
                color: this.getTypeColor(typeVal)
              }
            }, typeText)
          }
        },
        { title: '学科', key: 'projectName', width: 120 },
        { title: '难度', key: 'difficulty', width: 100,
          render: (h, params) => {
            const difficultyMap = {
              'easy': '简单',
              'medium': '中等',
              'hard': '困难'
            }
            return h('Tag', {
              props: {
                color: params.row.difficulty === 'easy' ? 'success' : params.row.difficulty === 'medium' ? 'warning' : 'error'
              }
            }, difficultyMap[params.row.difficulty] || params.row.difficulty)
          }
        },
        { title: '分值', key: 'score', width: 80 },
        { title: '状态', key: 'isActive', width: 100,
          render: (h, params) => {
            return h('Tag', {
              props: {
                color: params.row.isActive ? 'success' : 'default'
              }
            }, params.row.isActive ? '启用' : '禁用')
          }
        },
        { title: '创建时间', key: 'createTime', width: 150 },
        { title: '操作', slot: 'action', width: 150, fixed: 'right' }
      ],
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
      },
      showModal: false,
      isEdit: false,
      formData: {
        name: '',
        type: 0, // 0选择 1填空 2判断 3编程
        project: null,
        difficulty: 'medium',
        score: 5,
        options: [
          { content: '', isCorrect: false },
          { content: '', isCorrect: false }
        ],
        correctAnswer: '',
        analysis: '',
        isActive: true
      },
      formRules: {
        name: [
          { required: true, message: '请输入题目内容', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择题目类型', trigger: 'change' }
        ],
        project: [
          { required: true, message: '请选择学科', trigger: 'change' }
        ],
        difficulty: [
          { required: true, message: '请选择难度等级', trigger: 'change' }
        ],
        score: [
          { required: true, message: '请输入分值', trigger: 'blur' }
        ]
      },
      showDeleteModal: false,
      questionToDelete: {},
      importLoading: false
    }
  },
  mounted() {
    this.loadQuestions()
    this.loadProjects()
  },
  methods: {
    getTypeColor(type) {
      const colorMap = {
        0: 'blue',
        1: 'purple',
        2: 'orange',
        3: 'red',
        4: 'cyan',
        5: 'magenta'
      }
      return colorMap[Number(type)] || 'default'
    },

    async loadQuestions() {
      this.loading = true
      try {
        const response = await getAdminQuestions({
          page: this.pagination.current,
          pageSize: this.pagination.pageSize,
          keyword: this.searchKeyword,
          type: this.searchType,
          project: this.searchProject
        })
        if (response.code === 0) {
          this.questions = response.data.list
          this.pagination.total = response.data.total
        } else {
          this.$Message.error(response.msg || '加载题目列表失败')
        }
      } catch (error) {
        console.error('加载题目列表失败:', error)
        this.$Message.error('加载题目列表失败')
      } finally {
        this.loading = false
      }
    },

    async loadProjects() {
      try {
        const response = await getAllProjects()
        if (response.code === 0) {
          this.projects = response.data
        }
      } catch (error) {
        console.error('加载学科列表失败:', error)
      }
    },

    handleSearch() {
      this.pagination.current = 1
      this.loadQuestions()
    },

    resetSearch() {
      this.searchKeyword = ''
      this.searchType = ''
      this.searchProject = ''
      this.pagination.current = 1
      this.loadQuestions()
    },

    async beforeImport(file) {
      this.importLoading = true
      try {
        // 验证文件类型
        if (!file.name.endsWith('.csv')) {
          this.$Message.error('只支持CSV格式文件')
          return false
        }

        // 验证文件大小（10MB限制）
        if (file.size > 10 * 1024 * 1024) {
          this.$Message.error('文件大小不能超过10MB')
          return false
        }

        // 验证是否选择了学科
        if (!this.searchProject) {
          this.$Message.error('请先选择要导入的学科')
          return false
        }

        const precheck = await this.preValidateImportCsv(file)
        if (!precheck.ok) {
          this.$Message.error(precheck.message || '导入文件预校验失败')
          return false
        }

        if (precheck.warningMessage) {
          this.$Message.warning(precheck.warningMessage)
        }

        const fd = new FormData()
        fd.append('file', file)
        fd.append('subjectId', this.searchProject || '')
        const resp = await importAdminQuestions(fd)

        if (resp.code === 0) {
          const created = resp.data.created || 0
          const failed = resp.data.failed || []
          const total = resp.data.total || (created + failed.length)
          this.$Message.success(`导入完成：总计 ${total} 条，成功 ${created} 条，失败 ${failed.length} 条`)

          // 显示失败详情
          if (failed.length > 0) {
            console.table(failed)
            const reasonSummary = this.buildImportReasonSummary(failed)
            const sampleErrors = failed.slice(0, 8).map(f => `第${f.line}行: ${f.reason}`).join('\n')
            const moreMsg = failed.length > 8 ? `\n...还有 ${failed.length - 8} 条错误` : ''

            this.$Modal.warning({
              title: '题库导入完成（存在失败项）',
              width: 700,
              content: `失败原因汇总：\n${reasonSummary}\n\n示例错误：\n${sampleErrors}${moreMsg}\n\n已自动下载失败明细CSV。`,
              okText: '我知道了'
            })

            this.downloadImportFailedReport(failed)
          }
          this.loadQuestions()
        } else {
          this.$Message.error(resp.msg || '导入失败，请检查文件格式是否正确')
        }
      } catch (e) {
        console.error('导入失败', e)

        // 根据错误类型提供更具体的提示
        let errorMsg = '导入失败'
        if (e.response) {
          if (e.response.status === 413) {
            errorMsg = '文件过大，请上传小于10MB的文件'
          } else if (e.response.status === 400) {
            errorMsg = '文件格式错误，请检查CSV格式是否正确'
          } else if (e.response.status === 401 || e.response.status === 403) {
            errorMsg = '登录已过期，请重新登录'
          } else if (e.response.data && e.response.data.msg) {
            errorMsg = e.response.data.msg
          }
        } else if (e.message && e.message.includes('Network')) {
          errorMsg = '网络连接失败，请检查网络后重试'
        }

        this.$Message.error(errorMsg)
      } finally {
        this.importLoading = false
      }
      return false
    },

    async preValidateImportCsv(file) {
      try {
        const text = await this.readTextFile(file)
        const lines = text.split(/\r?\n/).filter(line => String(line || '').trim() !== '')
        if (lines.length < 2) {
          return { ok: false, message: 'CSV中没有可导入的数据行' }
        }

        const headers = this.splitCsvLine(lines[0]).map(h => String(h || '').replace(/^\uFEFF/, '').trim())
        const hasName = headers.includes('name') || headers.includes('题目')
        const hasAnswer = headers.includes('answer') || headers.includes('答案')
        if (!hasName || !hasAnswer) {
          return { ok: false, message: 'CSV缺少必要列：name/题目、answer/答案' }
        }

        let warningMessage = ''
        if (lines.length > 2001) {
          warningMessage = '检测到导入数据超过2000行，建议分批导入以便排查错误'
        }

        return { ok: true, warningMessage }
      } catch (error) {
        console.error('导入文件预校验失败:', error)
        return { ok: false, message: '无法读取CSV文件，请检查文件编码或内容' }
      }
    },

    readTextFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result || '')
        reader.onerror = () => reject(new Error('读取文件失败'))
        reader.readAsText(file, 'utf-8')
      })
    },

    splitCsvLine(line) {
      const result = []
      let current = ''
      let inQuotes = false

      for (let i = 0; i < line.length; i++) {
        const char = line[i]
        const nextChar = line[i + 1]

        if (char === '"') {
          if (inQuotes && nextChar === '"') {
            current += '"'
            i += 1
          } else {
            inQuotes = !inQuotes
          }
          continue
        }

        if (char === ',' && !inQuotes) {
          result.push(current)
          current = ''
          continue
        }

        current += char
      }

      result.push(current)
      return result
    },

    buildImportReasonSummary(failed) {
      const reasonMap = {}
      failed.forEach(item => {
        const reason = item.reason || '未知错误'
        reasonMap[reason] = (reasonMap[reason] || 0) + 1
      })
      return Object.keys(reasonMap)
        .sort((a, b) => reasonMap[b] - reasonMap[a])
        .slice(0, 8)
        .map(reason => `- ${reason}: ${reasonMap[reason]}条`)
        .join('\n')
    },

    downloadImportFailedReport(failed) {
      const escaped = (text) => `"${String(text || '').replace(/"/g, '""')}"`
      const rows = ['line,reason']
      failed.forEach(item => {
        rows.push(`${item.line || ''},${escaped(item.reason || '')}`)
      })
      const csvContent = `\uFEFF${rows.join('\n')}`
      triggerBlobDownload(csvContent, `questions_import_failed_${Date.now()}.csv`, 'text/csv;charset=utf-8;')
    },

    async exportCsv() {
      try {
        const filters = { subjectId: this.searchProject || '', search: this.searchKeyword || '', questionType: this.searchType !== '' ? this.searchType : '' }
        const resp = await exportAdminQuestions(filters)
        // 检查响应状态
        if (resp.code !== undefined && resp.code !== 0) {
          this.$Message.error(resp.msg || '导出失败')
          return
        }
        triggerBlobDownload(resp.data || resp, 'questions_export.csv', 'text/csv;charset=utf-8;')
      } catch (e) {
        console.error('导出失败', e)
        this.$Message.error('导出失败')
      }
    },

    async downloadTemplate(){
      try{
        const resp = await downloadQuestionsTemplate()
        // 检查响应状态
        if (resp.code !== undefined && resp.code !== 0) {
          this.$Message.error(resp.msg || '下载模板失败')
          return
        }
        triggerBlobDownload(resp.data || resp, 'questions_template.csv', 'text/csv;charset=utf-8;')
      }catch(e){
        console.error('下载模板失败', e)
        this.$Message.error('下载模板失败')
      }
    },

    handlePageChange(page) {
      this.pagination.current = page
      this.loadQuestions()
    },

    handlePageSizeChange(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.current = 1
      this.loadQuestions()
    },

    onTypeChange(type) {
      // 重置选项和答案
      this.formData.options = [
        { content: '', isCorrect: false },
        { content: '', isCorrect: false }
      ]
      this.formData.correctAnswer = ''
      
      // 为判断题设置默认答案
      if (type === 2) {
        this.formData.correctAnswer = 'true'
      }
      
      // 为编程题和综合题提供提示
      if (type === 4) {
        this.$Message.info('编程题：请提供代码示例或详细解题步骤')
      }
      if (type === 5) {
        this.$Message.info('综合题：请提供完整的解答方案和评分标准')
      }
    },

    addOption() {
      this.formData.options.push({ content: '', isCorrect: false })
    },

    removeOption(index) {
      if (this.formData.options.length > 2) {
        this.formData.options.splice(index, 1)
      }
    },

    getCorrectOptionsCount() {
      return this.formData.options.filter(option => option.isCorrect).length
    },

    validateOptions() {
      // 验证选项内容不能为空
      const hasEmptyContent = this.formData.options.some(option => !option.content.trim())
      if (hasEmptyContent) {
        this.$Message.warning('请填写所有选项内容')
        return false
      }

      // 验证必须有正确答案
      const correctCount = this.getCorrectOptionsCount()
      if (correctCount === 0) {
        this.$Message.warning('请至少选择一个正确答案')
        return false
      }

      // 单选题只能有一个正确答案
      if (this.formData.type === 0 && correctCount > 1) {
        this.$Message.warning('单选题只能有一个正确答案')
        return false
      }

      return true
    },

    showAddModal() {
      this.isEdit = false
      this.formData = {
        name: '',
        type: 0,
        project: null,
        difficulty: 'medium',
        score: 5,
        options: [
          { content: '', isCorrect: false },
          { content: '', isCorrect: false }
        ],
        correctAnswer: '',
        analysis: '',
        isActive: true
      }
      this.showModal = true
    },

    editQuestion(question) {
      this.isEdit = true
      this.formData = {
        ...question,
        project: question.project || question.subjectId || null,
        analysis: question.analysis || question.analyse || ''
      }
      
      // 如果是选择题，确保选项格式正确
      if (question.type === 0 && !question.options) {
        this.formData.options = [
          { content: '', isCorrect: false },
          { content: '', isCorrect: false }
        ]
      }
      
      this.showModal = true
    },

    async handleSubmit() {
      try {
        if (!this.formData.name || !String(this.formData.name).trim()) {
          this.$Message.warning('请输入题目内容')
          return
        }
        if (this.formData.type === null || this.formData.type === undefined || this.formData.type === '') {
          this.$Message.warning('请选择题目类型')
          return
        }
        if (!this.formData.project && !this.formData.subjectId) {
          this.$Message.warning('请选择学科')
          return
        }

        // 验证选项（如果是选择题）
        if ([0].includes(this.formData.type)) {
          if (!this.validateOptions()) return
        }

        // 验证其他题型的答案
        if ([1,2,3,4,5].includes(this.formData.type)) {
          if (!this.formData.correctAnswer) {
            this.$Message.warning('请输入正确答案')
            return
          }
        }

        let response
        if (this.isEdit) {
          response = await updateAdminQuestion(this.formData)
        } else {
          // 组合后端所需字段
          const payload = {
            name: this.formData.name,
            type: this.formData.type,
            subjectId: this.formData.project || this.formData.subjectId,
            answer: this.formData.correctAnswer,
            analyse: this.formData.analysis,
          }
          // 选择题选项
          if (this.formData.type === 0) {
            payload['options[]'] = this.formData.options.map(o => o.content)
            payload['correctOptions[]'] = this.formData.options
              .map((o, i) => (o.isCorrect ? String(i) : null))
              .filter(i => i !== null)
          }
          response = await addAdminQuestion(payload)
        }

        if (response.code === 0) {
          this.$Message.success(this.isEdit ? '编辑成功' : '创建成功')
          this.showModal = false
          this.loadQuestions()
        } else {
          this.$Message.error(response.msg || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        const msg = error?.msg || error?.response?.data?.msg || '操作失败'
        this.$Message.error(msg)
      }
    },

    handleCancel() {
      this.showModal = false
      this.$refs.formRef.resetFields()
    },

    deleteQuestion(question) {
      this.questionToDelete = question
      this.showDeleteModal = true
    },

    async confirmDelete() {
      try {
        const response = await deleteAdminQuestion(this.questionToDelete.id)
        if (response.code === 0) {
          this.$Message.success('删除成功')
          this.loadQuestions()
        } else {
          this.$Message.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除失败:', error)
        this.$Message.error('删除失败')
      } finally {
        this.showDeleteModal = false
      }
    }
  }
}
</script>

<style scoped>
.admin-questions {
  padding: 24px;
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

/* 页面头部 - 橙色渐变主题 */
.page-header {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  box-shadow: 0 10px 30px rgba(250, 140, 22, 0.3);
}

.page-header h2 {
  margin: 0;
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

/* 搜索区域美化 */
.search-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.search-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.search-section .ivu-input,
.search-section .ivu-select {
  margin-right: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.search-section .ivu-input:focus,
.search-section .ivu-select-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 选项美化 */
.option-item {
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #e8eaec;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.option-item:hover {
  background: #fff8f0;
  border-color: #fa8c16;
}

.option-label {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

/* 按钮美化 */
.ivu-btn-primary {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.3);
}

.ivu-btn-error {
  background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-btn-error:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
}

/* 表格美化 */
.ivu-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.ivu-table th {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: #fff;
  font-weight: 600;
}

.ivu-table td {
  transition: background-color 0.3s ease;
}

.ivu-table tr:hover td {
  background-color: rgba(250, 140, 22, 0.05) !important;
}

/* 分页美化 */
.ivu-page-item {
  border-radius: 6px;
  transition: all 0.3s ease;
}

.ivu-page-item:hover {
  background: #fa8c16;
  color: #fff;
}

.ivu-page-item-active {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border-color: #fa8c16;
}

/* 模态框美化 */
.ivu-modal-header {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: #fff;
  border-radius: 12px 12px 0 0;
}

.ivu-modal-header-inner {
  color: #fff;
  font-weight: 600;
}

/* 表单美化 */
.ivu-form-item-label {
  font-weight: 500;
  color: #333;
}

.ivu-input,
.ivu-select,
.ivu-input-number {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-input:focus,
.ivu-select-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-questions {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
  }

  .search-section {
    padding: 16px;
  }

  .search-section .ivu-input,
  .search-section .ivu-select {
    width: 100%;
    margin-right: 0;
    margin-bottom: 12px;
  }
}
</style>
