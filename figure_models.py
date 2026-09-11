"""Validated data and geometry for the four additional research figures."""

from copy import deepcopy
import math
import unicodedata


FIGURE_FIELDS = {
    "figure-ranking": ("unit", "items"),
    "figure-composition": ("unit", "categories", "groups"),
    "figure-metrics": ("metrics",),
    "figure-comparison": ("columns", "rows"),
}
COMPOSITION_COLORS = ("#0064FF", "#123B7A", "#0C78B7", "#9DC3FF")


def text_field(value, field, width=36):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}는 비어 있지 않은 텍스트여야 합니다")
    if "\n" in value or "—" in value or "–" in value:
        raise ValueError(f"{field}에는 줄바꿈 또는 긴 대시를 사용할 수 없습니다")
    length = sum(2 if unicodedata.east_asian_width(c) in {"W", "F"} else 1 for c in value)
    if length > width:
        raise ValueError(f"{field}는 영문 {width}자 폭 이하여야 합니다")


def finite_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field}는 유한한 숫자여야 합니다")
    if not math.isfinite(value):
        raise ValueError(f"{field}는 유한한 숫자여야 합니다")


def number_label(value):
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def validate_figure(document):
    kind = document["template"]
    if kind not in FIGURE_FIELDS:
        return
    if "unit" in FIGURE_FIELDS[kind]:
        text_field(document["unit"], "unit", 24)

    if kind == "figure-ranking":
        items = document["items"]
        if not isinstance(items, list) or not 2 <= len(items) <= 8:
            raise ValueError("items는 2-8개여야 합니다")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("각 item은 객체여야 합니다")
            text_field(item.get("label"), "item.label", 18)
            finite_number(item.get("value"), "item.value")
            if len(number_label(item["value"])) > 10:
                raise ValueError("item.value 단위를 줄여 10자 이내로 표시하세요")

    elif kind == "figure-composition":
        if document["unit"] != "%":
            raise ValueError("구성비 unit은 %여야 합니다")
        categories, groups = document["categories"], document["groups"]
        if not isinstance(categories, list) or not 2 <= len(categories) <= 4:
            raise ValueError("categories는 2-4개여야 합니다")
        for category in categories:
            text_field(category, "category", 18)
        if len(set(categories)) != len(categories):
            raise ValueError("categories는 중복될 수 없습니다")
        if not isinstance(groups, list) or not 1 <= len(groups) <= 3:
            raise ValueError("groups는 1-3개여야 합니다")
        for group in groups:
            if not isinstance(group, dict):
                raise ValueError("각 group은 객체여야 합니다")
            text_field(group.get("label"), "group.label", 40)
            values = group.get("values")
            if not isinstance(values, list) or len(values) != len(categories):
                raise ValueError("group.values 수는 categories 수와 같아야 합니다")
            for value in values:
                finite_number(value, "group.value")
                if not 0 <= value <= 100:
                    raise ValueError("구성비는 0-100 범위여야 합니다")
            if not math.isclose(sum(values), 100, abs_tol=0.01, rel_tol=0):
                raise ValueError("구성비 합계는 100%여야 합니다")

    elif kind == "figure-metrics":
        metrics = document["metrics"]
        if not isinstance(metrics, list) or len(metrics) != 4:
            raise ValueError("metrics는 정확히 4개여야 합니다")
        for metric in metrics:
            if not isinstance(metric, dict):
                raise ValueError("각 metric은 객체여야 합니다")
            text_field(metric.get("label"), "metric.label", 30)
            text_field(metric.get("unit"), "metric.unit", 24)
            finite_number(metric.get("value"), "metric.value")
            if len(number_label(metric["value"])) > 9:
                raise ValueError("metric.value 단위를 줄여 9자 이내로 표시하세요")
            if "change" in metric:
                change = metric["change"]
                if not isinstance(change, dict):
                    raise ValueError("metric.change는 객체여야 합니다")
                finite_number(change.get("value"), "change.value")
                text_field(change.get("unit"), "change.unit", 8)
                text_field(change.get("period"), "change.period", 24)
                if len(number_label(change["value"])) > 8:
                    raise ValueError("change.value는 8자 이내로 표시하세요")

    elif kind == "figure-comparison":
        columns, rows = document["columns"], document["rows"]
        if not isinstance(columns, list) or not 2 <= len(columns) <= 4:
            raise ValueError("columns는 2-4개여야 합니다")
        for column in columns:
            text_field(column, "column", 18)
        if not isinstance(rows, list) or not 3 <= len(rows) <= 6:
            raise ValueError("rows는 3-6개여야 합니다")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("각 row는 객체여야 합니다")
            text_field(row.get("label"), "row.label", 24)
            values = row.get("values")
            if not isinstance(values, list) or len(values) != len(columns):
                raise ValueError("row.values 수는 columns 수와 같아야 합니다")
            for value in values:
                text_field(value, "row.value", 24)


def figure_context(document):
    kind = document["template"]
    if kind == "figure-ranking":
        items = sorted(deepcopy(document["items"]), key=lambda item: item["value"], reverse=True)
        minimum = min(0, min(item["value"] for item in items))
        maximum = max(0, max(item["value"] for item in items))
        raw_step = (maximum - minimum or 1) / 4
        magnitude = 10 ** math.floor(math.log10(raw_step))
        step = next(value * magnitude for value in (1, 2, 2.5, 5, 10) if value * magnitude >= raw_step)
        minimum = math.floor(minimum / step) * step
        maximum = math.ceil(maximum / step) * step
        if maximum == minimum:
            maximum = minimum + step * 4
        span = maximum - minimum
        left, width = 300, 750
        zero = left + (0 - minimum) / span * width
        for index, item in enumerate(items):
            position = left + (item["value"] - minimum) / span * width
            item.update({
                "x": min(position, zero), "y": 32 + index * (560 / len(items)),
                "width": abs(position - zero), "formatted": number_label(item["value"]),
            })
        ticks = [
            {"x": left + width * i * step / span, "label": number_label(minimum + i * step)}
            for i in range(round(span / step) + 1)
        ]
        return {"ranked_items": items, "ranking_zero": zero, "ranking_ticks": ticks}

    if kind == "figure-composition":
        groups = deepcopy(document["groups"])
        for group in groups:
            group["segments"] = [
                {"name": name, "value": value, "formatted": number_label(value), "color": color}
                for name, value, color in zip(document["categories"], group["values"], COMPOSITION_COLORS)
            ]
        return {"composition_groups": groups}

    if kind == "figure-metrics":
        metrics = deepcopy(document["metrics"])
        for metric in metrics:
            metric["formatted"] = number_label(metric["value"])
            if "change" in metric:
                change = metric["change"]
                change["formatted"] = ("+" if change["value"] > 0 else "") + number_label(change["value"])
        return {"metrics": metrics}
    return {}
