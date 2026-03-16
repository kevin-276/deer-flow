# DeerFlow-BI 路线图（MVP -> v1）

## 阶段 0：脚手架（已完成）

- [x] 明确多 agent 职责边界
- [x] 设计跨阶段数据契约
- [x] 建立 pipeline 编排骨架
- [x] 预留 benchmark 与 ablation 目录

## 阶段 1：MVP 可运行闭环

- [ ] Planner：自然语言任务结构化
- [ ] Schema Retrieval：基于 schema 元数据返回 Top-K 候选
- [ ] SQL Generation：生成首版 SQL
- [ ] Execution-Guided Repair：按错误类型进行有限轮修复
- [ ] Critic：基础一致性与风险审查
- [ ] Reporter：输出面向用户的结论与 caveat

交付标准：
- [ ] 端到端跑通 20+ 条内部样例
- [ ] 输出标准化 artifacts（sql/report/execution）

## 阶段 2：质量提升

- [ ] 引入错误分类器（语法、schema、语义、权限）
- [ ] 引入 schema linking 特征（列名相似度 + 业务词典）
- [ ] 支持多 SQL 候选 + Critic rerank
- [ ] 增加 memory 驱动的用户偏好适配

交付标准：
- [ ] 执行通过率较阶段 1 提升
- [ ] 平均修复轮数下降

## 阶段 3：Benchmark + Ablation

- [ ] 构建离线评测集接口
- [ ] 增加 EX/EM/Execution Accuracy 指标
- [ ] 完成 ablation 套件（Planner/Critic/Repair/TopK/Memory）
- [ ] 输出实验报告模板

交付标准：
- [ ] 单命令运行基准评测
- [ ] 单命令运行 ablation 组合

## 阶段 4：生产化与可观测

- [ ] 阶段级 tracing 与可视化
- [ ] 失败样本自动归档与回放
- [ ] 结果置信度和风险分级
- [ ] 前端展示 SQL + 解释 + 证据链

交付标准：
- [ ] 接入 DeerFlow 前端工作台
- [ ] 可支持真实 BI 场景灰度试运行
