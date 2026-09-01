from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
