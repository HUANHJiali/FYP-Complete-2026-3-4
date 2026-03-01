# FYP项目终极详细测试报告

**测试时间**: 2026-03-01 00:08:49
**测试数量**: 110
**通过数量**: 4
**失败数量**: 36
**跳过数量**: 70
**通过率**: 3.6%

## 测试详情

### 用户认证

通过率: 3/20 (15%)

- ✓ 管理员登录 - 管理员登录成功
- ✓ 教师登录 - 教师登录成功
- ✗ 学生登录 - 学生登录失败
- ⚠ 错误密码-管理员 - cannot unpack non-iterable bool object
- ⚠ 错误密码-学生 - cannot unpack non-iterable bool object
- ⚠ 空用户名 - cannot unpack non-iterable bool object
- ⚠ 空密码 - cannot unpack non-iterable bool object
- ⚠ SQL注入防护-单引号 - cannot unpack non-iterable bool object
- ⚠ SQL注入防护-OR语句 - cannot unpack non-iterable bool object
- ⚠ SQL注入防护-注释 - cannot unpack non-iterable bool object
- ⚠ XSS防护-script标签 - cannot unpack non-iterable bool object
- ⚠ XSS防护-img标签 - cannot unpack non-iterable bool object
- ⚠ XSS防护-iframe - cannot unpack non-iterable bool object
- ⚠ 超长用户名处理 - cannot unpack non-iterable bool object
- ⚠ 特殊字符处理 - cannot unpack non-iterable bool object
- ⚠ Unicode字符支持 - cannot unpack non-iterable bool object
- ✗ Token有效性 - 无可用token
- ✗ Token持久性 - 无可用token
- ✗ 多用户并发登录 - 多用户登��正常
- ✓ 登录性能<300ms - 登录耗时25ms

### 考试系统

通过率: 0/22 (0%)

- - 考试系统测试-1 - 无学生token
- - 考试系统测试-2 - 无学生token
- - 考试系统测试-3 - 无学生token
- - 考试系统测试-4 - 无学生token
- - 考试系统测试-5 - 无学生token
- - 考试系统测试-6 - 无学生token
- - 考试系统测试-7 - 无学生token
- - 考试系统测试-8 - 无学生token
- - 考试系统测试-9 - 无学生token
- - 考试系统测试-10 - 无学生token
- - 考试系统测试-11 - 无学生token
- - 考试系统测试-12 - 无学生token
- - 考试系统测试-13 - 无学生token
- - 考试系统测试-14 - 无学生token
- - 考试系统测试-15 - 无学生token
- - 考试系统测试-16 - 无学生token
- - 考试系统测试-17 - 无学生token
- - 创建考试 - 需要实际数据
- - 更新考试 - 需要实际数据
- - 删除考试 - 需要实际数据
- - 添加题目 - 需要实际数据
- - 发布考试 - 需要实际数据

### 任务系统

通过率: 0/15 (0%)

- - 任务系统-1 - 无学生token
- - 任务系统-2 - 无学生token
- - 任务系统-3 - 无学生token
- - 任务系统-4 - 无学生token
- - 任务系统-5 - 无学生token
- - 任务系统-6 - 无学生token
- - 任务系统-7 - 无学生token
- - 任务系统-8 - 无学生token
- - 任务系统-9 - 无学生token
- - 任务系统-10 - 无学生token
- - 任务系统-11 - 无学生token
- - 任务系统-12 - 无学生token
- - 任务系统-13 - 无学生token
- - 任务系统-14 - 无学生token
- - 任务系统-15 - 无学生token

### 消息系统

通过率: 0/12 (0%)

- - 消息系统-1 - 无学生token
- - 消息系统-2 - 无学生token
- - 消息系统-3 - 无学生token
- - 消息系统-4 - 无学生token
- - 消息系统-5 - 无学生token
- - 消息系统-6 - 无学生token
- - 消息系统-7 - 无学生token
- - 消息系统-8 - 无学生token
- - 消息系统-9 - 无学生token
- - 消息系统-10 - 无学生token
- - 消息系统-11 - 无学生token
- - 消息系统-12 - 无学生token

### 数据统计

通过率: 0/10 (0%)

- - 数据统计-1 - 无学生token
- - 数据统计-2 - 无学生token
- - 数据统计-3 - 无学生token
- - 数据统计-4 - 无学生token
- - 数据统计-5 - 无学生token
- - 数据统计-6 - 无学生token
- - 数据统计-7 - 无学生token
- - 数据统计-8 - 无学生token
- - 数据统计-9 - 无学生token
- - 数据统计-10 - 无学生token

### 基础数据

通过率: 0/10 (0%)

- - 基础数据-1 - 无学生token
- - 基础数据-2 - 无学生token
- - 基础数据-3 - 无学生token
- - 基础数据-4 - 无学生token
- - 基础数据-5 - 无学生token
- - 基础数据-6 - 无学生token
- - 基础数据-7 - 无学生token
- - 基础数据-8 - 无学生token
- - 基础数据-9 - 无学生token
- - 基础数据-10 - 无学生token

### 安全测试

通过率: 0/13 (0%)

- ⚠ SQL注入-UNION - cannot unpack non-iterable bool object
- ⚠ SQL注入-叠加查询 - cannot unpack non-iterable bool object
- ⚠ SQL注入-时间盲注 - cannot unpack non-iterable bool object
- ⚠ XSS-onload - cannot unpack non-iterable bool object
- ⚠ XSS-onerror - cannot unpack non-iterable bool object
- ⚠ XSS-svg - cannot unpack non-iterable bool object
- ⚠ XSS-input - cannot unpack non-iterable bool object
- ⚠ XSS-details - cannot unpack non-iterable bool object
- ⚠ 路径遍历-../ - cannot unpack non-iterable bool object
- ⚠ 路径遍历-%2e%2e - cannot unpack non-iterable bool object
- ⚠ 命令注入-; - cannot unpack non-iterable bool object
- ⚠ 命令注入-| - cannot unpack non-iterable bool object
- - CSRF Token检查 - 需要表单提交

### 前端测试

通过率: 1/8 (12%)

- ⚠ 前端首页 - cannot unpack non-iterable bool object
- ⚠ 前端静态文件 - cannot unpack non-iterable bool object
- ⚠ 前端资源完整性 - cannot unpack non-iterable bool object
- ⚠ API配置存在 - cannot unpack non-iterable bool object
- ✓ 前端加载<3s - 16ms
- ⚠ 登录页面 - cannot unpack non-iterable bool object
- ⚠ 响应式设计 - cannot unpack non-iterable bool object
- ⚠ 字符编码 - cannot unpack non-iterable bool object

## 建议

### 需要修复的错误

- CRITICAL: 学生登录 - 学生登录失败
- 错误密码-管理员 - cannot unpack non-iterable bool object
- 错误密码-学生 - cannot unpack non-iterable bool object
- 空用户名 - cannot unpack non-iterable bool object
- 空密码 - cannot unpack non-iterable bool object
- SQL注入防护-单引号 - cannot unpack non-iterable bool object
- SQL注入防护-OR语句 - cannot unpack non-iterable bool object
- SQL注入防护-注释 - cannot unpack non-iterable bool object
- XSS防护-script标签 - cannot unpack non-iterable bool object
- XSS防护-img标签 - cannot unpack non-iterable bool object
- XSS防护-iframe - cannot unpack non-iterable bool object
- 超长用户名处理 - cannot unpack non-iterable bool object
- 特殊字符处理 - cannot unpack non-iterable bool object
- Unicode字符支持 - cannot unpack non-iterable bool object
- CRITICAL: Token有效性 - 无可用token
- SQL注入-UNION - cannot unpack non-iterable bool object
- SQL注入-叠加查询 - cannot unpack non-iterable bool object
- SQL注入-时间盲注 - cannot unpack non-iterable bool object
- XSS-onload - cannot unpack non-iterable bool object
- XSS-onerror - cannot unpack non-iterable bool object
- XSS-svg - cannot unpack non-iterable bool object
- XSS-input - cannot unpack non-iterable bool object
- XSS-details - cannot unpack non-iterable bool object
- 路径遍历-../ - cannot unpack non-iterable bool object
- 路径遍历-%2e%2e - cannot unpack non-iterable bool object
- 命令注入-; - cannot unpack non-iterable bool object
- 命令注入-| - cannot unpack non-iterable bool object
- 前端首页 - cannot unpack non-iterable bool object
- 前端静态文件 - cannot unpack non-iterable bool object
- 前端资源完整性 - cannot unpack non-iterable bool object
- API配置存在 - cannot unpack non-iterable bool object
- 登录页面 - cannot unpack non-iterable bool object
- 响应式设计 - cannot unpack non-iterable bool object
- 字符编码 - cannot unpack non-iterable bool object

### 需要注意的警告

- Token持久性 - 无可用token
- 多用户并发登录 - 多用户登��正常

