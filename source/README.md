# 智能学生考试系统 (FYPPPP)

## 项目概述
这是一个基于Django + Vue.js的智能学生考试系统，集成了AI智能评分和自动出题功能。

## 技术架构
- **前端**: Vue.js 2.x + iView UI + Vue Router + Vuex
- **后端**: Django 4.1.3 + MySQL + REST API
- **AI集成**: 智谱AI (GLM-4-Flash)
- **database**: MySQL

## 精简目录结构
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
├── 📁 config/              # 配置文件
│   ├── 智谱AI配置.md        # AI配置说明
│   ├── setup_zhipuai_env.ps1  # 环境配置脚本
│   └── 删除日志表.sql       # database脚本
├── 📁 tools/               # 工具脚本
│   ├── debug_jwt.py        # JWT调试工具
│   ├── diagnose_zhipuai.py # AI诊断工具
│   └── verify_api_key.py   # API密钥验证
├── 📁 startup/             # 启动脚本
│   ├── start_services.bat  # Windows启动脚本
│   ├── start_services.sh   # Linux启动脚本
│   └── stop_services.bat   # 停止服务脚本
├── 📁 docs/                # 核心功能文档
│   ├── AI功能使用说明.md    # AI功能说明
│   ├── 系统架构与演示说明.md # 系统架构说明
│   └── 删除日志功能说明.md  # 日志功能说明
├── 📄 README.md            # 项目主说明
├── 📄 PROJECT_STATUS.md    # 项目状态和进度
└── 📄 快速启动.md          # 快速启动指南
```

## 快速启动

### 方法1: 使用启动脚本 (推荐)
```bash
# Windows用户
双击 startup/start_services.bat

# Linux/Mac用户
./startup/start_services.sh
```

### 方法2: 手动启动
```bash
# 后端
cd server
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
1. **AI配置**: 参考 `config/智谱AI配置.md`
2. **环境配置**: 运行 `config/setup_zhipuai_env.ps1`
3. **database**: 确保MySQL服务运行

## 注意事项
- 首次运行需要安装依赖
- 确保database连接正常
- 配置智谱AI API密钥

## 项目状态
详细的项目进度和功能状态请查看 `PROJECT_STATUS.md`
