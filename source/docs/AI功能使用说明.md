# AI评分和AI自动创建题目功能使用说明

## 概述

本系统集成了基于OpenAI的AI评分和AI自动创建题目功能，为教育评估提供智能化解决方案。

## 功能特性

### 1. AI智能评分系统
- **多题型支持**: 支持选择题、填空题、判断题、编程题的智能评分
- **智能分析**: 提供详细的评分反馈和错误分析
- **灵活评分**: 支持部分正确评分，不局限于对错二分
- **备选方案**: AI评分失败时自动使用传统评分方法

### 2. AI自动创建题目
- **智能生成**: 根据科目、主题、难度自动生成高质量题目
- **多样化题型**: 支持生成选择题、填空题、判断题、编程题
- **质量控制**: 生成的题目包含详细解析和知识点标注
- **批量生成**: 支持一次性生成多道题目

### 3. AI错误答案分析
- **深度分析**: 分析学生错误答案的原因和知识点掌握情况
- **改进建议**: 提供针对性的学习建议
- **复习指导**: 推荐相关知识点复习内容

## 安装配置

### 1. 安装依赖
```bash
cd server
pip install -r requirements.txt
```

### 2. AI账号与API配置（每位用户需自行注册，赠送3个月使用）

为保障合规与资源隔离，团队采用“每位用户自行到官方平台注册账号并获取API Key”的模式。本项目对每位用户提供3个月的AI使用期（以项目政策为准）。

步骤：
1) 前往官方平台注册个人账号（建议使用学校/企业邮箱注册）。
2) 在个人控制台创建/查看 API Key，并复制保存。
3) 在项目根目录复制 `env.example` 为 `.env`，填写以下变量（示例变量名，按你们项目实际为准）：
```
AI_PROVIDER=openai              # 或 zhipuai 等
OPENAI_API_KEY=你的APIKey
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo      # 或项目支持的模型名
```
4) 将 `.env` 加入部署服务器（生产环境），并确保仅服务进程可读。
5) 本地或服务器上运行连通性测试：`python tools/verify_api_key.py` 或 `tools/test_ai_connection.py`。

如你们使用的是智谱AI，请参考 `config/智谱AI配置.md` 完成环境变量与可用模型配置。

在 `server/server/settings.py` 中也可直接配置（不推荐暴露密钥，生产请用环境变量）：

```python
# AI配置
OPENAI_API_KEY = 'your-openai-api-key'  # 替换为您的实际API密钥
OPENAI_MODEL = 'gpt-3.5-turbo'          # 使用的模型
OPENAI_BASE_URL = 'https://api.openai.com/v1'  # API基础URL
```

### 3. database迁移
```bash
cd server
python manage.py makemigrations
python manage.py migrate
```

## API接口说明

### 1. AI评分接口

**POST** `/ai/score_answer/`

**请求参数:**
```json
{
    "questionContent": "题目内容",
    "questionType": 0,  // 0-选择 1-填空 2-判断 3-编程
    "correctAnswer": "正确答案",
    "studentAnswer": "学生答案",
    "maxScore": 10.0
}
```

**响应示例:**
```json
{
    "code": 200,
    "data": {
        "score": 8.5,
        "feedback": "答案基本正确，但表达不够准确",
        "analysis": "学生理解了核心概念，但在细节表达上有偏差...",
        "is_correct": true
    }
}
```

### 2. AI题目生成接口

**POST** `/ai/generate_questions/`

**请求参数:**
```json
{
    "subject": "Python编程",
    "topic": "函数",
    "difficulty": "medium",  // easy/medium/hard
    "questionType": 0,  // 0-选择 1-填空 2-判断 3-编程
    "count": 5
}
```

**响应示例:**
```json
{
    "code": 200,
    "data": {
        "questions": [
            {
                "content": "题目内容",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "answer": "正确答案",
                "analysis": "题目解析",
                "difficulty": "medium",
                "knowledge_points": "涉及知识点"
            }
        ],
        "count": 5,
        "subject": "Python编程",
        "topic": "函数",
        "difficulty": "medium",
        "question_type": 0
    }
}
```

### 3. AI错误答案分析接口

**GET** `/ai/analyze_wrong_answer/`

**请求参数:**
```
?questionContent=题目内容&correctAnswer=正确答案&wrongAnswer=错误答案&questionType=1
```

**响应示例:**
```json
{
    "code": 200,
    "data": {
        "analysis": "详细错误分析",
        "suggestion": "改进建议",
        "knowledge_points": "相关知识点",
        "review_suggestions": "复习建议"
    }
}
```

## 前端组件使用

### 1. AI评分组件
```vue
<template>
  <AIScoring />
</template>

<script>
import AIScoring from '@/components/AIScoring.vue'

export default {
  components: {
    AIScoring
  }
}
</script>
```

### 2. AI题目生成组件
```vue
<template>
  <AIQuestionGenerator />
</template>

<script>
import AIQuestionGenerator from '@/components/AIQuestionGenerator.vue'

export default {
  components: {
    AIQuestionGenerator
  }
}
</script>
```

## 集成到现有系统

### 1. 自动评分集成
系统已自动集成AI评分功能到练习和任务提交流程中：
- 填空题和编程题自动使用AI评分
- 选择题和判断题使用传统评分
- AI评分失败时自动降级到传统评分

### 2. 管理后台集成
在管理员后台的题目管理页面中，新增了"AI生成题目"功能：
- 选择科目、主题、难度
- 指定题目类型和数量
- 一键生成并保存到题库

## 测试功能

### 运行测试
```bash
cd server
python test_ai_functions.py
```

### 测试内容
- AI评分功能测试
- AI题目生成测试
- AI错误答案分析测试
- 传统评分备选方案测试

## 注意事项

### 1. API密钥安全
- 请妥善保管OpenAI API密钥
- 建议使用环境变量存储敏感信息
- 生产环境中请使用HTTPS

### 2. 使用限制
- OpenAI API有调用频率限制
- 建议合理控制生成题目数量
- 长时间运行建议添加重试机制

### 3. 成本控制
- AI API调用会产生费用
- 建议监控API使用量
- 可以考虑缓存常用结果

### 4. 质量保证
- 生成的题目需要人工审核
- 建议建立题目质量评估机制
- 定期更新和优化提示词

## 故障排除

### 1. API连接失败
- 检查网络连接
- 验证API密钥是否正确
- 确认API配额是否充足

### 2. 评分结果异常
- 检查题目类型设置
- 验证答案格式
- 查看错误日志

### 3. 生成题目失败
- 检查主题描述是否清晰
- 验证难度设置
- 确认生成数量在合理范围内

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持AI评分和题目生成
- 集成到现有系统
- 提供完整的前端组件

## 技术支持

如有问题，请联系开发团队或查看项目文档。
