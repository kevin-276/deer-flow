# DeerFlow-BI

**A Multi-Agent BI Analyst built on DeerFlow**

## 1. 项目简介

DeerFlow-BI 是 DeerFlow 的二次开发方向，目标是将自然语言业务问题转为可执行 SQL，并产出结构化结果与运行 artifacts。当前版本为可本地跑通的 MVP，聚焦工程链路打通与后续扩展接口稳定。

## 2. DeerFlow-BI 的目标

围绕 Text-to-SQL / BI Agent 端到端流程构建可演进系统：

1. Planner：将自然语言问题转换为结构化分析计划
2. SQL Generator：根据计划（及可选 schema 上下文）生成候选 SQL
3. Executor / Repair：执行 SQL 并进行基础执行修复
4. Artifact Export：输出 run-specific 产物用于调试、评估、复现

## 3. 当前已实现的 MVP 模块

代码目录：`backend/packages/harness/deerflow/bi/`

- `agents/planner_agent.py`：最小 Planner（结构化 plan）
- `agents/sql_generator_agent.py`：最小 SQL 生成（多候选 + dialect + note）
- `agents/executor_repair_agent.py`：最小执行修复闭环（最多 2 轮）
- `skills/sql_execute/`：SQLite 执行 skill
- `runtime/orchestration.py`：MVP 主流程（Planner -> SQL Generator -> Executor/Repair）
- `runtime/demo.py`：CLI/demo 入口
- `artifacts/exporter.py`：artifact 导出器

## 4. 如何安装依赖

在仓库根目录准备配置后，进入 backend 安装依赖：

```bash
cd backend
make install
```

如果只运行 DeerFlow-BI MVP demo，核心依赖来自 backend 现有环境（含 Python + uv 工作流）。

## 5. 如何运行 demo

在 backend 目录运行：

```bash
cd backend
PYTHONPATH=. uv run python -m deerflow.bi.runtime.demo "统计最近30天新增用户数"
```

指定 SQLite 数据库文件与 artifact 输出根目录：

```bash
cd backend
PYTHONPATH=. uv run python -m deerflow.bi.runtime.demo \
  "统计最近30天新增用户数" \
  --sqlite-db-path /tmp/bi_demo.db \
  --artifacts-root-dir /tmp/bi_artifacts_demo
```

输出包含：
- `analysis_plan`
- `candidate_sql`
- `final_sql`
- `final_result`
- `execution_logs`
- `artifact_run_dir`

## 6. Artifact 输出说明

每次运行都会生成独立目录，默认根目录：

- `artifacts/deerflow_bi_runs/`

目录示例：

- `artifacts/deerflow_bi_runs/run_20260316T173211Z_74928080/`

至少包含：

- `plan.json`
- `candidate_sql.sql`
- `execution_log.json`
- `final_result.json`（若结果是表格行可输出 `final_result.csv`）

## 7. 后续 roadmap（简述）

1. Schema Retrieval 最小可用版（Top-K + score）
2. SQL Generator 接入 retrieval 上下文增强
3. Executor/Repair 引入可配置错误分类和修复策略
4. Critic + Reporter 接入，形成更完整 BI 交付链路
5. Benchmark/Ablation 自动化（Spider/BIRD Mini-Dev/Spider2-DBT 适配）
