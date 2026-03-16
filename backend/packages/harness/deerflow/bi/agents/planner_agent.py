"""Planner agent for DeerFlow-BI MVP.

Responsibility:
- Convert a natural language BI question into a structured analysis plan.

The planner intentionally uses lightweight heuristics for the MVP stage.
It avoids heavy dependencies and keeps the output contract stable for
subsequent schema retrieval and SQL generation stages.
"""

import re

from deerflow.bi.runtime.state import BIState


class PlannerAgent:
    """MVP planner with deterministic parsing heuristics."""

    _TASK_TYPE_KEYWORDS = {
        "ranking": ["top", "排名", "排行", "前"],
        "comparison": ["对比", "比较", "环比", "同比", "vs"],
        "trend": ["趋势", "变化", "每天", "每日", "按天", "按周", "按月"],
        "aggregation": ["总", "总数", "多少", "统计", "sum", "count", "avg"],
    }

    _METRIC_CANDIDATES = [
        "新增用户数",
        "活跃用户数",
        "订单数",
        "销售额",
        "收入",
        "留存率",
        "转化率",
        "gmv",
        "revenue",
        "orders",
        "users",
    ]

    _DIMENSION_CANDIDATES = [
        "渠道",
        "地区",
        "城市",
        "国家",
        "产品",
        "品类",
        "用户类型",
        "端",
        "campaign",
        "channel",
        "region",
    ]

    def run(self, state: BIState) -> dict:
        """Build and persist a structured plan into runtime state."""
        question = state.user_question.strip()
        plan = {
            "task_type": self._infer_task_type(question),
            "target_metric": self._infer_target_metric(question),
            "dimensions": self._infer_dimensions(question),
            "filters": self._infer_filters(question),
            "time_range": self._infer_time_range(question),
            "assumptions": self._build_assumptions(question),
            "next_action": "schema_retrieval",
        }
        state.analysis_plan = plan
        return plan

    def _infer_task_type(self, question: str) -> str:
        lowered = question.lower()
        for task_type, keywords in self._TASK_TYPE_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return task_type
        return "aggregation"

    def _infer_target_metric(self, question: str) -> str:
        lowered = question.lower()
        for metric in self._METRIC_CANDIDATES:
            if metric.lower() in lowered:
                return metric
        return "unknown_metric"

    def _infer_dimensions(self, question: str) -> list[str]:
        lowered = question.lower()
        dimensions: list[str] = []
        for dim in self._DIMENSION_CANDIDATES:
            if dim.lower() in lowered:
                dimensions.append(dim)

        if "按" in question and not dimensions:
            dimensions.append("unknown_dimension")

        return list(dict.fromkeys(dimensions))

    def _infer_filters(self, question: str) -> list[str]:
        filters: list[str] = []

        for pattern in [r"([\w\u4e00-\u9fa5]+)\s*(>=|<=|=|>|<)\s*([\w\u4e00-\u9fa5%-]+)", r"(大于|小于|等于)\s*([\w\u4e00-\u9fa5%-]+)"]:
            for match in re.findall(pattern, question):
                if isinstance(match, tuple):
                    filters.append(" ".join(str(x) for x in match if x))
                else:
                    filters.append(str(match))

        return filters

    def _infer_time_range(self, question: str) -> str:
        q = question.lower()

        if re.search(r"最近\s*\d+\s*天", question):
            return re.search(r"最近\s*\d+\s*天", question).group(0)
        if re.search(r"最近\s*\d+\s*周", question):
            return re.search(r"最近\s*\d+\s*周", question).group(0)
        if re.search(r"最近\s*\d+\s*月", question):
            return re.search(r"最近\s*\d+\s*月", question).group(0)
        if "上周" in question:
            return "上周"
        if "上月" in question:
            return "上月"
        if "昨天" in question:
            return "昨天"
        if "today" in q:
            return "today"
        if "last" in q and "day" in q:
            return "last day"

        return "unspecified"

    def _build_assumptions(self, question: str) -> list[str]:
        assumptions = ["默认使用当前数据源默认 SQL 方言", "未指定时间范围时使用数据集默认窗口"]

        if "按" in question and "unknown_dimension" in self._infer_dimensions(question):
            assumptions.append("问题包含分组意图但维度未明确，后续需在 schema retrieval 阶段确认")

        if self._infer_target_metric(question) == "unknown_metric":
            assumptions.append("目标指标未显式识别，后续需基于 schema 和业务词典做指标对齐")

        return assumptions
