# DeerFlow-BI 设计文档

**项目名**: DeerFlow-BI  
**副标题**: A Multi-Agent BI Analyst built on DeerFlow

## 1. 当前 DeerFlow 仓库结构理解（接入视角）

基于当前仓库，DeerFlow-BI 最关键的可复用能力集中在 backend harness：

- `deerflow/agents/*`：主 Agent 与中间件链，适合承接 BI 编排入口。
- `deerflow/subagents/*` + `tools/builtins/task_tool.py`：已具备子 Agent 委派和异步执行能力，是 multi-agent orchestration 的天然落点。
- `deerflow/skills/*`：技能发现和启停机制，适合承载业务词典、指标口径、SQL 风格等可插拔知识。
- `deerflow/sandbox/*`：线程隔离执行环境，可承载 SQL 执行辅助脚本、日志与中间产物管理。
- `deerflow/agents/memory/*`：现有 memory 队列与更新机制，适合沉淀 BI 用户偏好（维度偏好、展示风格、口径偏好）。
- `tools/builtins/present_file_tool.py` + outputs artifact 机制：适合输出 Markdown/图表配置/结果 JSON。

结论：DeerFlow-BI 应作为 `backend/packages/harness/deerflow/bi/` 子模块接入，复用现有 DeerFlow runtime，不应另起炉灶。

## 2. DeerFlow-BI 的接入方式

### 2.1 多 Agent 角色映射

- **Planner Agent**：将 NL 问题结构化为分析计划。
- **Schema Retrieval Agent**：执行 large-schema retrieval / schema linking。
- **SQL Generator Agent**：基于计划和 schema 生成候选 SQL。
- **Executor / Repair Agent**：执行 SQL，按错误进行 execution-guided repair。
- **Critic Agent**：业务语义审查（避免“能跑但答非所问”）。
- **Reporter Agent**：生成 Markdown/图表/结果 artifact，完成 end-to-end BI delivery。

### 2.2 DeerFlow 原生能力 -> BI 场景映射

- **multi-agent orchestration**：优先复用 subagent/task 调度能力。
- **skills**：行业词典、指标定义、SQL 方言规则做成可开关技能。
- **sandbox**：执行日志、诊断脚本、结果文件产出。
- **memory**：用户偏好记忆 + 历史修复经验沉淀。
- **artifacts**：报告、图表 spec、SQL 与执行摘要交付。

## 3. 推荐目录骨架（MVP）

推荐在 `backend/packages/harness/deerflow/bi/` 下采用如下骨架：

- `agents/`：六类 BI agent 占位实现
- `runtime/`：统一状态对象与编排
- `skills/`：BI 定制技能适配层
- `memory/`：BI 偏好与上下文记忆适配层
- `evaluation/`：benchmark/ablation runner 入口
- `artifacts/`：报告与图表产物构建
- `docs/`：模块内文档
- `tests/`：模块级测试

## 4. 运行时状态与协议（ISSUE-003）

统一状态定义在 `runtime/state.py`，核心字段：

- `user_question`
- `analysis_plan`
- `retrieved_schema`
- `candidate_sql`
- `final_sql`
- `execution_logs`
- `final_result`
- `critic_feedback`
- `report_artifacts`

并预留：
- `ablation_flags`
- `runtime_metadata`

状态流转：

1. Planner 写入 `analysis_plan`
2. Schema Retrieval 写入 `retrieved_schema`
3. SQL Generator 写入 `candidate_sql`
4. Executor/Repair 写入 `final_sql` / `execution_logs` / `final_result`
5. Critic 写入 `critic_feedback`
6. Reporter 写入 `report_artifacts`

该结构保持简洁，便于后续在 benchmark/ablation 中替换任意单一模块。

## 5. 分阶段实施建议

### MVP（当前）

- 目标：打通可 import、可运行、可测试的最小骨架。
- 内容：状态契约、基础编排、agent 占位、文档和测试。

### V2（可量化）

- 接入真实 schema linking / retrieval
- 接入 SQL dialect handling（至少 sqlite + postgres 抽象）
- 接入 execution-guided repair 错误分类
- 建立 benchmark 指标（EX/EM/Execution Accuracy）

### V3（可简历亮点）

- 多策略 ablation 自动跑批
- business-semantic critic 规则+LLM 混合评估
- artifact generation 标准化（Markdown + chart spec + result package）
- Spider / BIRD Mini-Dev / Spider2-DBT 数据集适配器接入

## 6. 后续优先级建议

1. **优先级 P0**：`runtime/state.py` + `runtime/orchestration.py` 协议稳定。
2. **优先级 P1**：Schema Retrieval 接口化（可替换检索策略）。
3. **优先级 P1**：Executor/Repair 错误类型抽象 + SQL dialect handling。
4. **优先级 P2**：Critic 与 Reporter 的质量评估闭环。
5. **优先级 P2**：benchmark/ablation runner 自动化。


## 7. ISSUE-004：Planner Agent 最小实现说明

`PlannerAgent` 当前提供一个轻量可运行版本：

- 输入：`BIState.user_question`
- 输出：结构化计划字段：
  - `task_type`
  - `target_metric`
  - `dimensions`
  - `filters`
  - `time_range`
  - `assumptions`
  - `next_action`
- 行为：`run()` 在返回 plan 的同时写回 `state.analysis_plan`，确保后续 agent 直接读取。

最小示例：
- 输入：`统计最近30天按渠道的新增用户数`
- 输出片段：`target_metric=新增用户数`，`time_range=最近30天`，`next_action=schema_retrieval`


## 8. ISSUE-005：SQL 执行 Skill（SQLite MVP）

新增 `skills/sql_execute/`，提供可本地跑通的 SQLite 执行能力：

- `execute_sql(sql, database_path, params, timeout_seconds)`
- 结构化返回：
  - `success`
  - `rows`
  - `error_message`
  - `metadata`（包含 `dialect`、`row_count`、`elapsed_ms`、`error_type` 等）
- `write_execution_result_to_state(state, sql, result)` 用于把执行结果写入：
  - `final_sql`
  - `final_result`
  - `execution_logs`

该接口保持简洁稳定，后续可扩展到 DuckDB / Postgres 等 SQL dialect。


## 9. ISSUE-006：SQL Generator Agent 最小实现说明

`SQLGeneratorAgent` 当前提供可运行 MVP：

- 输入：`user_question` + `analysis_plan` + `retrieved_schema`（可为空）
- 输出：
  - `candidate_sql`（默认返回 >= 1 条，当前返回 2 条模板候选）
  - `dialect`（当前固定 `sqlite`）
  - `generation_note`（简短生成说明）
- 写回 runtime state：
  - `state.candidate_sql`
  - `state.runtime_metadata["sql_generation"]`

当 schema context 存在时走 schema-aware 模板；不存在时走 fallback 模板，便于后续平滑接入 retrieval 结果。


## 10. ISSUE-007：Executor / Repair Agent 最小闭环

`ExecutorRepairAgent` 当前支持执行-修复闭环：

1. 读取 `candidate_sql` 并调用 `sql_execute` skill 执行
2. 若失败，基于 `error_message` 做最多 2 轮修复（可配置）
3. 输出并写回：
   - `final_sql`
   - `execution_logs`
   - `repair_rounds`
   - `final_result`

当前基础修复策略（可扩展）：
- `SELEC` -> `SELECT`
- 去除 `SELECT a, FROM t` 的尾随逗号
- `no such table` 时优先使用 retrieval 的首个表名进行替换


## 11. ISSUE-008：最小 Orchestration + Demo 入口

MVP 主流程在 `runtime/orchestration.py`：

1. Planner Agent
2. SQL Generator Agent
3. Executor / Repair Agent

输入：用户问题；输出：统一 `BIState`，至少包含 `analysis_plan`、`candidate_sql`、`final_sql`、`final_result`、`execution_logs`。

新增 demo 入口：`runtime/demo.py`

- 函数：`run_mvp_demo(question, sqlite_db_path=None)`
- CLI：`python -m deerflow.bi.runtime.demo "统计最近30天新增用户数" --sqlite-db-path <path>`
