# W05 AI接入与回退策略（Weekly Log）

## 本周目标
- 接入AI评分与题目生成能力。
- 设计失败回退与提示机制。

## 已完成
- AI能力接入完成（评分/生成）。
- 增加接口兼容与参数健壮性处理。

## 风险/阻塞
- 第三方模型响应存在波动。

## 解决方案
- 采用统一AI工具层，增加重试与降级路径。

## 下周计划
- 完成考试/任务流程闭环并回归。

## 证据链接
- [source/docs/AI功能使用说明.md](../../source/docs/AI功能使用说明.md)
- [source/config/智谱AI配置.md](../../source/config/智谱AI配置.md)
- [source/server/app/views/ai_views.py](../../source/server/app/views/ai_views.py)
