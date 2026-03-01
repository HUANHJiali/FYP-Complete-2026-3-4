# Docker 运行验证报告（2026-02-28）

## 1. 验证目标
- 验证主开发栈（docker-compose.yml）可稳定启动、健康检查通过、核心接口可访问。
- 验证镜像部署栈（dockerpull/docker-compose.yml）可稳定启动、健康检查通过、默认账号可登录。
- 修复并消除启动过程中的关键不稳定因素（健康检查误判、迁移冲突、默认账号初始化失败）。

---

## 2. 本轮关键修复

### 2.1 主栈（docker-compose.yml）
1) 前端健康检查误判修复
- 问题：健康检查使用 localhost，容器内命中 IPv6 ::1 导致 ECONNREFUSED。
- 修复：改为 127.0.0.1。

2) 数据库初始化策略修复（根治迁移冲突）
- 问题：挂载 SQL 初始化脚本与 Django migrations 结构不一致，导致迁移冲突（外键/重复表/字段不一致）。
- 修复：移除 MySQL init SQL 挂载，改为纯 Django migrate 建表。

3) 默认账号初始化补齐
- 新增脚本：source/server/tools/seed_default_users.py
- 启动阶段执行：migrate 后执行种子脚本，创建 admin/teacher/student 及教师/学生关联记录。

### 2.2 镜像栈（dockerpull/docker-compose.yml）
1) 后端健康检查路径修复
- 问题：/api/health/simple/ 在镜像版返回 404。
- 修复：改为 /api/health/。

2) 前端健康检查与依赖顺序修复
- 前端 healthcheck 改为 127.0.0.1:8080。
- 前端 depends_on 改为依赖 backend service_healthy。

3) 默认账号种子逻辑兼容修复
- 问题：镜像模型中 Users 可能不存在 email/status 字段，且 pass_word 长度不足以存储哈希。
- 修复：种子脚本改为仅写入兼容字段，默认密码写明文 123456（镜像登录逻辑兼容并可后续迁移）。

4) 清理 compose 兼容性警告
- 移除 obsolete 的 version 字段。

---

## 3. 验证步骤与结果

### 3.1 主栈验证（docker-compose.yml）
- 工具链检查：Docker 与 Compose 可用。
- 配置校验：compose config 通过。
- 冷启动回归：down/up 全流程通过。
- 健康检查：db/backend/frontend 均 healthy。
- 连通性：
  - http://127.0.0.1:8000/api/health/simple/ => 200
  - http://127.0.0.1:8080 => 200
- 登录验证：admin/123456 成功（code=0）。

结论：主栈可稳定运行，且已消除历史迁移冲突风险。

### 3.2 镜像栈验证（dockerpull/docker-compose.yml）
- 配置校验：compose config 通过。
- 启动验证：25fyp_mysql / 25fyp_backend / 25fyp_frontend 均 healthy。
- 连通性：
  - http://127.0.0.1:8000/api/health/ => 200
  - http://127.0.0.1:8080 => 200
- 登录验证：admin/123456 成功（code=0）。

结论：dockerpull 镜像部署链路已可用并与主栈行为对齐。

---

## 4. 当前运行状态（收尾时）
- 已切回主开发栈运行。
- 当前容器：fyp_mysql / fyp_backend / fyp_frontend（均 healthy）。
- 无 dockerpull 残留容器占用端口。

---

## 5. 变更文件清单
- docker-compose.yml
- dockerpull/docker-compose.yml
- source/server/tools/seed_default_users.py
- source/client/src/api/index.js
- source/client/src/router/index.js
- source/client/src/utils/menus.js
- source/client/src/views/pages/adminDashboard.vue

---

## 6. 建议（后续）
1) 在 CI 增加两个 compose 的 smoke 流程：
   - 主栈：health/simple + login
   - 镜像栈：health + login
2) 若后续统一模型字段，建议将 dockerpull 中“明文种子密码”切回哈希方式。
3) 发布前保留一次 down -v 冷启动回归，确认默认账号与健康检查稳定。

---

## 7. 最终结论
截至 2026-02-28，本项目 Docker 双链路（主栈 + 镜像栈）均已通过可运行验证，核心健康检查、页面访问、登录链路均正常。