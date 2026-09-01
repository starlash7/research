from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


BASE = Path(__file__).resolve().parent
ENV = Environment(
    loader=FileSystemLoader(BASE / "templates"),
    autoescape=True,
    undefined=StrictUndefined,
)
DEFAULT_ACCENT = "#E84B18"
SERIES_COLORS = (DEFAULT_ACCENT, "#2563A6", "#167547")


@dataclass(frozen=True)
class TemplateSpec:
    filename: str
    size: tuple[int, int]
    required: tuple[str, ...]


TEMPLATES = {
    "cover-editorial": TemplateSpec(
        "cover-editorial.html",
        (1440, 756),
        ("eyebrow", "title", "subtitle", "date"),
    ),
    "cover-object": TemplateSpec(
        "cover-object.html",
        (1440, 756),
        ("eyebrow", "title", "subtitle", "date"),
    ),
    "figure-framework": TemplateSpec(
        "figure-framework.html",
        (1440, 810),
        ("eyebrow", "title", "nodes", "source", "date"),
    ),
    "figure-data": TemplateSpec(
        "figure-data.html",
        (1440, 1200),
        ("title", "source", "date", "chart", "takeaways"),
    ),
}


def load_document(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("JSON 최상위 값은 객체여야 합니다")
    return document


def safe_slug(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("slug는 영문 소문자, 숫자, 하이픈만 사용할 수 있습니다")
    return value


def _require_text(document: dict[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} 값이 필요합니다")
    return value.strip()


def _validate_chart(chart: Any) -> None:
    if not isinstance(chart, dict):
        raise ValueError("chart는 객체여야 합니다")
    if chart.get("type") not in {"line", "bar"}:
        raise ValueError("chart.type은 line 또는 bar여야 합니다")
    labels = chart.get("labels")
    series = chart.get("series")
    if not isinstance(labels, list) or not 2 <= len(labels) <= 12:
        raise ValueError("chart.labels는 2-12개여야 합니다")
    if not isinstance(series, list) or not 1 <= len(series) <= 3:
        raise ValueError("chart.series는 1-3개여야 합니다")
    for item in series:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ValueError("각 chart.series에는 name이 필요합니다")
        values = item.get("values")
        if not isinstance(values, list) or len(values) != len(labels):
            raise ValueError("각 chart.series values 수는 labels 수와 같아야 합니다")
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            raise ValueError("chart.series values는 숫자여야 합니다")
        color = item.get("color")
        if color is not None and (
            not isinstance(color, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", color)
        ):
            raise ValueError("chart.series color는 #RRGGBB 형식이어야 합니다")
    for key in ("y_min", "y_max"):
        value = chart.get(key)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool)
        ):
            raise ValueError(f"chart.{key}은 숫자여야 합니다")
    if chart.get("y_min") is not None and chart.get("y_max") is not None:
        if chart["y_min"] >= chart["y_max"]:
            raise ValueError("chart.y_max는 y_min보다 커야 합니다")


def validate_document(document: dict[str, Any]) -> TemplateSpec:
    if not isinstance(document, dict):
        raise ValueError("문서는 객체여야 합니다")
    template_name = document.get("template")
    if template_name not in TEMPLATES:
        raise ValueError(f"지원하지 않는 템플릿입니다: {template_name}")
    spec = TEMPLATES[template_name]
    safe_slug(document.get("slug"))
    for key in spec.required:
        if key not in document or document[key] in (None, "", [], {}):
            raise ValueError(f"{key} 값이 필요합니다")

    title = _require_text(document, "title")
    if template_name.startswith("cover-"):
        if title.count("\n") > 1:
            raise ValueError("커버 제목은 최대 두 줄까지 사용할 수 있습니다")
        if len(title.replace("\n", "")) > 48:
            raise ValueError("커버 제목은 공백 포함 48자 이하여야 합니다")

    accent = document.get("accent")
    if accent is not None and (
        not isinstance(accent, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", accent)
    ):
        raise ValueError("accent는 #RRGGBB 형식이어야 합니다")

    if template_name == "figure-framework":
        nodes = document["nodes"]
        if not isinstance(nodes, list) or not 3 <= len(nodes) <= 5:
            raise ValueError("framework nodes는 3-5개여야 합니다")
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError("각 framework node는 객체여야 합니다")
            _require_text(node, "title")
            _require_text(node, "body")

    if template_name == "figure-data":
        _require_text(document, "source")
        _require_text(document, "date")
        _validate_chart(document["chart"])
        takeaways = document["takeaways"]
        if not isinstance(takeaways, list) or not 1 <= len(takeaways) <= 3:
            raise ValueError("takeaways는 1-3개여야 합니다")

    return spec


def _axis_bounds(chart: dict[str, Any]) -> tuple[float, float]:
    values = [float(value) for series in chart["series"] for value in series["values"]]
    raw_min, raw_max = min(values), max(values)
    magnitude_source = max(abs(raw_min), abs(raw_max), 1.0)
    magnitude = 10 ** math.floor(math.log10(magnitude_source))
    step = magnitude / 5

    y_min = float(chart.get("y_min", 0 if raw_min >= 0 else math.floor(raw_min / step) * step))
    y_max = float(chart.get("y_max", math.ceil(raw_max / step) * step))
    if y_max <= raw_max:
        y_max += step
    if y_min >= raw_min and raw_min < 0:
        y_min -= step
    if y_max == y_min:
        y_max = y_min + 1
    return y_min, y_max


def _number_label(value: float, unit: str) -> str:
    if math.isclose(value, round(value), abs_tol=1e-9):
        number = f"{value:,.0f}"
    elif abs(value) < 10:
        number = f"{value:,.2f}".rstrip("0").rstrip(".")
    else:
        number = f"{value:,.1f}".rstrip("0").rstrip(".")
    return f"{number}{unit}"


def _chart_context(chart: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(chart)
    width, height = 1304, 630
    left, right_edge, top, bottom = 92, 1276, 42, 78
    plot_width = right_edge - left
    plot_height = height - top - bottom
    y_min, y_max = _axis_bounds(chart)
    y_span = y_max - y_min
    unit = str(chart.get("unit") or "")

    def y_position(value: float) -> float:
        return round(top + (y_max - value) / y_span * plot_height, 2)

    ticks = []
    for index in range(5):
        value = y_max - y_span * index / 4
        ticks.append(
            {
                "value": value,
                "label": _number_label(value, unit),
                "y": round(top + plot_height * index / 4, 2),
            }
        )

    labels = chart["labels"]
    if chart["type"] == "line":
        x_positions = [
            round(left + plot_width * index / (len(labels) - 1), 2)
            for index in range(len(labels))
        ]
    else:
        slot_width = plot_width / len(labels)
        x_positions = [round(left + slot_width * (index + 0.5), 2) for index in range(len(labels))]

    enriched_series = []
    for series_index, original in enumerate(chart["series"]):
        series = deepcopy(original)
        series["color"] = original.get("color") or SERIES_COLORS[series_index]
        series["dash"] = ("", "14 10", "4 10")[series_index]
        if chart["type"] == "line":
            points = []
            for index, value in enumerate(original["values"]):
                y = y_position(float(value))
                label_y = y - 18 - series_index * 19
                if label_y < 20:
                    label_y = y + 31 + series_index * 19
                points.append(
                    {
                        "x": x_positions[index],
                        "y": y,
                        "label_y": round(label_y, 2),
                        "label": _number_label(float(value), unit),
                        "show_label": len(labels) <= 8 or index in {0, len(labels) - 1},
                    }
                )
            series["points"] = points
            series["polyline"] = " ".join(f'{point["x"]},{point["y"]}' for point in points)
            series["bars"] = []
        else:
            slot_width = plot_width / len(labels)
            group_width = slot_width * 0.68
            bar_width = group_width / len(chart["series"])
            baseline = y_position(min(max(0, y_min), y_max))
            bars = []
            for index, value in enumerate(original["values"]):
                value_y = y_position(float(value))
                x = left + slot_width * index + (slot_width - group_width) / 2 + bar_width * series_index
                y = min(value_y, baseline)
                bar_height = abs(value_y - baseline)
                bars.append(
                    {
                        "x": round(x + 2, 2),
                        "y": round(y, 2),
                        "width": round(max(bar_width - 4, 2), 2),
                        "height": round(max(bar_height, 1), 2),
                        "label_x": round(x + bar_width / 2, 2),
                        "label_y": round(max(y - 14 - series_index * 18, 19), 2),
                        "label": _number_label(float(value), unit),
                        "show_label": len(labels) <= 8 or index in {0, len(labels) - 1},
                    }
                )
            series["points"] = []
            series["polyline"] = ""
            series["bars"] = bars
        enriched_series.append(series)

    result.update(
        {
            "width": width,
            "height": height,
            "left": left,
            "right_edge": right_edge,
            "ticks": ticks,
            "x_labels": [
                {"x": x_positions[index], "label": label}
                for index, label in enumerate(labels)
            ],
            "series": enriched_series,
            "y_min": y_min,
            "y_max": y_max,
        }
    )
    return result


def _hero_uri(document: dict[str, Any], source_path: Path) -> str | None:
    hero_image = document.get("hero_image")
    if hero_image is None:
        return None
    if not isinstance(hero_image, str) or not hero_image.strip():
        raise ValueError("hero_image는 로컬 상대 경로여야 합니다")
    relative = Path(hero_image)
    if relative.is_absolute():
        raise ValueError("hero_image는 JSON 파일 기준 상대 경로여야 합니다")
    base = source_path.parent.resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("hero_image는 JSON 파일이 있는 폴더 밖으로 나갈 수 없습니다") from exc
    if not candidate.is_file():
        raise ValueError(f"hero_image 파일을 찾을 수 없습니다: {hero_image}")
    if candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("hero_image는 PNG, JPG 또는 WebP여야 합니다")
    return candidate.as_uri()


def build_context(document: dict[str, Any], source_path: Path) -> dict[str, Any]:
    spec = validate_document(document)
    context = deepcopy(document)
    context.update(
        {
            "width": spec.size[0],
            "height": spec.size[1],
            "accent": document.get("accent") or DEFAULT_ACCENT,
            "hero_uri": _hero_uri(document, source_path),
            "highlight": document.get("highlight"),
        }
    )
    if document["template"] == "figure-data":
        context["chart"] = _chart_context(document["chart"])
    return context


def render_html(document: dict[str, Any], source_path: Path) -> str:
    spec = validate_document(document)
    return ENV.get_template(spec.filename).render(**build_context(document, source_path))
