# 智能学生考试系统 (FYP 2025)

## 项目概述
这是一个基于 Django + Vue 3 的智能学生考试系统，集成 AI 智能评分与自动出题能力。

## 技术架构
- **前端**: Vue.js 3.x + View UI Plus + Vue Router 4 + Vuex 4
- **后端**: Django 4.1.3 + MySQL 8+ + REST API
- **AI集成**: 智谱AI (GLM-4-Flash)
- **部署**: Docker Compose（推荐）/ Nginx + Gunicorn

## 目录结构（核心）
```
source/
├── 📁 client/              # Vue前端代码
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   ├── dist/               # 构建输出
│   └── package.json        # 前端依赖
├── 📁 server/              # Django后端代码
│   ├── app/                # 应用模块
│   ├── comm/               # 公共工具
│   ├── manage.py           # Django管理脚本
│   └── requirements.txt    # Python依赖
├── 📁 docs/                # 文档与答辩材料
├── 📁 server/tools/        # 回归与验收脚本
│   ├── run_regression_baseline.py
│   ├── run_defense_demo_check.py
│   ├── run_defense_demo_check.bat
│   └── run_defense_demo_check.sh
├── 📁 docs/                # 核心功能文档
│   ├── AI功能使用说明.md    # AI功能说明
│   ├── 系统架构与演示说明.md # 系统架构说明
│   └── 删除日志功能说明.md  # 日志功能说明
├── 📄 README.md            # 项目主说明
├── 📄 PROJECT_STATUS.md    # 项目状态和进度
└── 📄 快速启动.md          # 快速启动指南
```

## 快速启动

### 方法1: Docker 启动（推荐）
```bash
# Windows
双击 ..\\docker-start.bat

# Linux/Mac
../docker-start.sh
```

### 方法2: 手动启动
```bash
# 后端
cd server
python -m venv .venv
.venv\Scripts\activate   # Linux/Mac 用: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 前端 (新终端)
cd client
npm install
npm run serve
```

## 访问地址
- **前端界面**: http://localhost:8080
- **后端API**: http://127.0.0.1:8000

## 测试账户
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |
| 教师 | teacher | 123456 |
| 学生 | student | 123456 |

## 核心功能
- ✅ **练习试卷系统** - 完整的练习流程
- ✅ **AI智能评分** - 支持多种题型
- ✅ **AI自动出题** - 按主题和难度生成
- ✅ **用户管理** - 多角色权限控制
- ✅ **错题本** - 智能错题分析
- ✅ **任务中心** - 学习任务管理

## 配置说明
1. 复制 `env.example` 为 `.env`
2. 填写数据库、CORS/CSRF 与 AI 参数
3. 生产环境必须：`DEBUG=False` 且配置强随机 `SECRET_KEY`

## 注意事项
- 首次运行需要安装依赖
- 确保数据库连接正常
- 未配置 AI Key 时，AI 功能接口将不可用

## 验收建议（答辩前）
```bash
cd server
python tools/run_defense_demo_check.py
```

Windows 可直接运行：`server\\tools\\run_defense_demo_check.bat`

## 项目状态
详细的项目进度和功能状态请查看 `PROJECT_STATUS.md`
