  FYP2025 - 智能學生考試系統

  項目概述

這是一個基於 Django + Vue.js 的智能學生考試系統，集成了 AI 智能評分和自動出題功能。系統支持多角色權限管理、練習試卷、錯題本、任務中心等完整功能。

  技術架構

- **前端**: Vue.js 3.x + View UI Plus + Vue Router + Vuex
- **後端**: Django 4.1.3 + MySQL + REST API
- **AI集成**: 智譜AI (GLM-4-Flash) 智能評分和自動出題
- **數據庫**: MySQL 8.0+
- **部署**: 支持本地開發和生產環境部署

 快速啟動

### 🐳 Docker 一鍵啟動（最推薦 - 零配置）

**無需安裝任何開發環境，只需 Docker Desktop！**

```bash
# Windows 用戶
docker-start.bat

# Linux/Mac 用戶
chmod +x docker-start.sh
./docker-start.sh

# 或直接使用 Docker Compose
docker-compose up -d
```

📖 詳細 Docker 部署指南：[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### 🎯 組員一鍵部署（需要安裝開發環境）

```bash
# Windows 用戶 - 一鍵部署
cd source
一鍵部署.bat

# Linux/Mac 用戶 - 一鍵部署
cd source
chmod +x 一鍵部署.sh
./一鍵部署.sh
```

### 🛠️ 開發者配置 (推薦)

```bash
# Windows 用戶
setup_env.bat

# Linux/Mac 用戶
chmod +x setup_env.sh
./setup_env.sh

# 跨平台 Python 腳本
python setup_env.py
```

### 方法2: 手動啟動

```bash
# 1. 數據庫設置
mysql -u root -p
CREATE DATABASE db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql -u root -p db_exam < database/db_exam.sql
mysql -u root -p db_exam < database/init_practice_data.sql

# 2. 後端啟動
cd source/server
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 3. 前端啟動 (新終端)
cd source/client
npm install
npm run serve
```

### 生產部署（一鍵腳本）

推薦使用提供的部署腳本完成生產環境安裝、構建與啟動。

- Linux (Ubuntu 20.04/22.04+):
```bash
sudo bash deploy/setup_server.sh \
  --project-root /path/to/FYP2025-main \
  --domain your.domain.com \
  --env-file /etc/exam/.env \
  --db-import yes

# 可選：HTTPS 證書
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```

- Windows (PowerShell 以管理員執行):
```powershell
powershell -ExecutionPolicy Bypass -File deploy\setup_server.ps1 `
  -ProjectRoot "C:\\FYP2025-main" `
  -EnvFile "C:\\exam\\.env" `
  -DBImport Yes
```

相關樣例配置：
- Nginx: `deploy/nginx.conf`（含 gzip、超時、/api 代理）
- systemd: `deploy/exam-gunicorn.service`（Gunicorn + Uvicorn，含 access/error 日誌與 graceful-timeout）

重要注意：
- `.env` 檔建議放置於 `/etc/exam/.env` 並以 `EnvironmentFile` 方式被 systemd 載入
- Windows 若 `mysqlclient` 安裝失敗，腳本會回退使用 `PyMySQL` 完全兼容 Django ORM

##  訪問地址

- **前端界面**: http://localhost:8080
- **後端API**: http://localhost:8000
- **管理後台**: http://localhost:8000/admin

##  測試賬戶

| 角色 | 用戶名 | 密碼 | 說明 |
|------|--------|------|------|
| 管理員 | admin | 123456 | 系統管理員，可管理所有功能 |
| 教師 | teacher | 123456 | 教師賬戶，可創建和管理考試 |
| 學生 | student | 123456 | 學生賬戶，可參加考試和練習 |

##  核心功能

- ✅ **練習試卷系統** - 完整的練習流程和自動評分
- ✅ **AI智能評分** - 支持多種題型的智能評分
- ✅ **AI自動出題** - 按主題和難度自動生成題目
- ✅ **用戶管理** - 多角色權限控制和用戶管理
- ✅ **錯題本** - 智能錯題分析和重做功能
- ✅ **任務中心** - 學習任務管理和進度追蹤
- ✅ **消息中心** - 系統通知和消息管理
- ✅ **實時監控** - 學習進度和成績統計

## 📁 項目結構

```
FYP2025-main/
├── 📁 source/                    # 主要源代碼
│   ├── 📁 client/                # Vue.js 前端
│   │   ├── src/                  # 源代碼
│   │   ├── public/               # 靜態資源
│   │   └── package.json          # 前端依賴
│   ├── 📁 server/                # Django 後端
│   │   ├── app/                  # 主應用
│   │   ├── comm/                 # 公共工具
│   │   ├── manage.py             # Django 管理腳本
│   │   └── requirements.txt      # Python 依賴
│   ├── 📁 config/                # 配置文件
│   ├── 📁 tools/                 # 工具腳本
│   ├── 📁 docs/                  # 文檔
│   └── 📄 完整運行指南.md        # 詳細運行指南
├── 📁 database/                  # 數據庫文件
│   ├── db_exam.sql               # 數據庫結構
│   └── init_practice_data.sql    # 初始數據
└── 📁 ai-exam-system/            # AI 考試系統相關
```

## 🔧 環境配置

### 前置要求

#### Docker 部署（推薦）
- ✅ **Docker Desktop** - 容器運行環境

#### 本地開發部署
- ✅ **Python 3.9+** - 後端開發環境
- ✅ **Node.js 16+** - 前端開發環境
- ✅ **MySQL 8.0+** - 數據庫服務
- ✅ **Git** - 版本控制工具

### 配置說明
1. **環境配置**: 運行 `setup_env.py` 或使用對應平台的配置腳本
2. **AI配置**: 參考 `source/config/智谱AI配置.md`
3. **數據庫**: 確保 MySQL 服務運行並創建 `db_exam` 數據庫

## 📖 詳細文檔

- **🐳 [Docker 部署指南](DOCKER_DEPLOYMENT.md)** - 使用 Docker 零配置部署（最推薦）
- **👥 [組員部署指南](source/組員部署指南.md)** - 專門為組員準備的簡化部署指南
- **📋 [完整運行指南](source/完整运行指南.md)** - 詳細的部署和運行指南
- **⚡ [快速啟動指南](source/快速启动.md)** - 快速啟動步驟
- **🎯 [FYP 演示指南](source/FYP_DEMO_GUIDE.md)** - 適合 FYP 展示的指南
- **🔧 [環境配置說明](source/环境配置文件说明.md)** - 詳細的環境配置說明
- **🤖 [AI 功能說明](source/docs/AI功能使用说明.md)** - AI 功能使用說明

## 🛠️ 故障排除

### 常見問題
1. **數據庫連接失敗**: 檢查 MySQL 服務狀態和密碼配置
2. **端口被占用**: 修改端口配置或停止占用進程
3. **依賴安裝失敗**: 清理緩存後重新安裝
4. **AI 功能無法使用**: 檢查智譜 AI API 密鑰配置



