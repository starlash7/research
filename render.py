from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import unicodedata
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from figure_models import FIGURE_FIELDS, figure_context, text_field, validate_figure


BASE = Path(__file__).resolve().parent
ENV = Environment(
    loader=FileSystemLoader(BASE / "templates"),
    autoescape=True,
    undefined=StrictUndefined,
)
DEFAULT_ACCENT = "#0064FF"
SERIES_COLORS = (DEFAULT_ACCENT, "#123B7A", "#0C78B7")
PALETTE_PREVIEWS = {
    "vermillion": {"accent": "#E4492D", "data": "#E4492D", "text": "#B93822"},
    "lime": {"accent": "#C7F542", "data": "#526B16", "text": "#526B16"},
    "violet": {"accent": "#7546E8", "data": "#7546E8", "text": "#7546E8"},
    "teal": {"accent": "#008F86", "data": "#008F86", "text": "#006E67"},
    "magenta": {"accent": "#D62F8A", "data": "#D62F8A", "text": "#D62F8A"},
    "amber": {"accent": "#F2B233", "data": "#A86B08", "text": "#8C5800"},
    "burgundy": {"accent": "#8C2545", "data": "#8C2545", "text": "#8C2545"},
    "forest": {"accent": "#1D684F", "data": "#1D684F", "text": "#1D684F"},
    "coral": {"accent": "#F47568", "data": "#CC5045", "text": "#B64037"},
    "copper": {"accent": "#B76E3C", "data": "#B76E3C", "text": "#925327"},
    "indigo": {"accent": "#4338CA", "data": "#4338CA", "text": "#4338CA"},
    "cyan": {"accent": "#00A6C8", "data": "#00809B", "text": "#006E85"},
    "red": {"accent": "#D7263D", "data": "#D7263D", "text": "#D7263D"},
    "orange": {"accent": "#F0781E", "data": "#C85C10", "text": "#AF4B08"},
    "yellow": {"accent": "#EBCB20", "data": "#8D7900", "text": "#796700"},
    "olive": {"accent": "#718044", "data": "#718044", "text": "#5B6833"},
    "mint": {"accent": "#21B889", "data": "#008763", "text": "#007354"},
    "blue": {"accent": "#0064FF", "data": "#0064FF", "text": "#0064FF"},
    "navy": {"accent": "#183153", "data": "#183153", "text": "#183153"},
    "slate": {"accent": "#64748B", "data": "#64748B", "text": "#64748B"},
}


@dataclass(frozen=True)
class TemplateSpec:
    filename: str
    size: tuple[int, int]
    required: tuple[str, ...]


TEMPLATES = {
    "cover-editorial": TemplateSpec(
        "cover-editorial.html",
        (1440, 756),
        ("category", "title", "subtitle", "date"),
    ),
    "cover-object": TemplateSpec(
        "cover-object.html",
        (1440, 756),
        ("category", "title", "subtitle", "date"),
    ),
    "figure-framework": TemplateSpec(
        "figure-framework.html",
        (1440, 810),
        ("title", "nodes", "source", "date"),
    ),
    "figure-data": TemplateSpec(
        "figure-data.html",
        (1440, 1200),
        ("title", "source", "date", "chart"),
    ),
}
for name, fields in FIGURE_FIELDS.items():
    TEMPLATES[name] = TemplateSpec(f"{name}.html", (1440, 1200), ("title", "source", "date", *fields))
DATA_TEMPLATES = {"figure-data", *FIGURE_FIELDS}
TEXT_FIELDS = {
    "cover-editorial": ("category", "title", "subtitle", "date"),
    "cover-object": ("category", "title", "subtitle", "date"),
    "figure-framework": ("title", "source", "date"),
    "figure-data": ("title", "source", "date"),
}
TEXT_FIELDS.update({name: ("title", "source", "date") for name in FIGURE_FIELDS})


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


def _display_width(value: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1
        for character in value
    )


def _validate_chart(chart: Any) -> None:
    if not isinstance(chart, dict):
        raise ValueError("chart는 객체여야 합니다")
    if chart.get("type") not in {"line", "bar"}:
        raise ValueError("chart.type은 line 또는 bar여야 합니다")
    labels = chart.get("labels")
    series = chart.get("series")
    _require_text(chart, "unit")
    limit = 366 if chart["type"] == "line" else 12
    if not isinstance(labels, list) or not 2 <= len(labels) <= limit:
        raise ValueError(f"chart.labels는 2-{limit}개여야 합니다")
    if not all(isinstance(label, str) and label.strip() for label in labels):
        raise ValueError("chart.labels는 비어 있지 않은 텍스트여야 합니다")
    for label in labels:
        text_field(label, "chart.label", 8 if chart["type"] == "bar" and len(labels) > 6 else 16)
    if not isinstance(series, list) or not 1 <= len(series) <= 3:
        raise ValueError("chart.series는 1-3개여야 합니다")
    all_values = []
    for item in series:
        if not isinstance(item, dict):
            raise ValueError("각 chart.series는 객체여야 합니다")
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("각 chart.series에는 비어 있지 않은 name이 필요합니다")
        text_field(item["name"], "chart.series.name", 22)
        values = item.get("values")
        if not isinstance(values, list) or len(values) != len(labels):
            raise ValueError("각 chart.series values 수는 labels 수와 같아야 합니다")
        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            for value in values
        ):
            raise ValueError("chart.series values는 유한한 숫자여야 합니다")
        all_values.extend(float(value) for value in values)
        color = item.get("color")
        if color is not None and (
            not isinstance(color, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", color)
        ):
            raise ValueError("chart.series color는 #RRGGBB 형식이어야 합니다")
    for key in ("y_min", "y_max"):
        if key not in chart:
            continue
        value = chart[key]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"chart.{key}은 유한한 숫자여야 합니다")
    if "y_min" in chart and "y_max" in chart:
        if chart["y_min"] >= chart["y_max"]:
            raise ValueError("chart.y_max는 y_min보다 커야 합니다")
    if "y_min" in chart and min(all_values) < float(chart["y_min"]):
        raise ValueError("chart.y_min과 y_max 범위에 모든 값이 포함되어야 합니다")
    if "y_max" in chart and max(all_values) > float(chart["y_max"]):
        raise ValueError("chart.y_min과 y_max 범위에 모든 값이 포함되어야 합니다")
    lower, upper = _axis_bounds(chart)
    tick_values = [upper - (upper - lower) * index / 4 for index in range(5)]
    if any(len(_number_label(value, "")) > 7 for value in [*all_values, lower, upper, *tick_values]):
        raise ValueError("chart 수치가 너무 깁니다. 단위를 조정해 표시 수치를 7자 이내로 줄이세요")


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

    text = {key: _require_text(document, key) for key in TEXT_FIELDS[template_name]}
    title = text["title"]
    if template_name in DATA_TEMPLATES:
        if title.count("\n") > 1:
            raise ValueError("데이터 제목은 최대 두 줄까지 사용할 수 있습니다")
        for line in title.splitlines():
            text_field(line, "title", 44)
        text_field(text["source"], "source", 150)
        text_field(text["date"], "date", 16)
        if "period" in document:
            text_field(document["period"], "period", 66)
    if template_name.startswith("cover-"):
        if _display_width(text["category"]) > 24:
            raise ValueError("cover category는 영문 24자 폭 이하여야 합니다")
        if title.count("\n") > 1:
            raise ValueError("커버 제목은 최대 두 줄까지 사용할 수 있습니다")
        if any(_display_width(line) > 30 for line in title.splitlines()):
            raise ValueError("커버 제목 한 줄은 한글 15자 또는 영문 30자 이하여야 합니다")
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
        _validate_chart(document["chart"])
        text_field(document["chart"]["unit"], "chart.unit", 24)
        takeaways = document.get("takeaways", [])
        if not isinstance(takeaways, list) or not 0 <= len(takeaways) <= 3:
            raise ValueError("takeaways는 0-3개여야 합니다")
        for item in takeaways:
            if not isinstance(item, dict):
                raise ValueError("각 takeaway는 객체여야 합니다")
            for key in ("label", "value"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise ValueError(f"각 takeaway에는 비어 있지 않은 {key} 텍스트가 필요합니다")

    validate_figure(document)

    if "variant" in document:
        if document["variant"] != "editorial" or template_name not in {"figure-data", "figure-metrics"}:
            raise ValueError("variant는 figure-data 또는 figure-metrics의 editorial 시안만 지원합니다")
        if template_name == "figure-data" and document["chart"]["type"] != "line":
            raise ValueError("editorial 차트 시안은 line만 지원합니다")
    if "focus_index" in document:
        if document.get("variant") != "editorial":
            raise ValueError("focus_index는 variant: editorial에서만 사용할 수 있습니다")
        items = document["chart"]["series"] if template_name == "figure-data" else document["metrics"]
        index = document["focus_index"]
        if type(index) is not int or not 0 <= index < len(items):
            raise ValueError("focus_index는 0부터 시작하는 유효한 대상 번호여야 합니다")

    if "palette_preview" in document:
        palette = document["palette_preview"]
        if not isinstance(palette, str) or palette not in PALETTE_PREVIEWS:
            raise ValueError(f"palette_preview는 {', '.join(PALETTE_PREVIEWS)} 중 하나여야 합니다")
        if template_name != "cover-editorial" and not (
            template_name == "figure-data" and document.get("variant") == "editorial"
        ):
            raise ValueError("palette_preview는 밝은 커버와 editorial 추세 시안만 지원합니다")
        if "accent" in document:
            raise ValueError("palette_preview와 accent를 동시에 지정할 수 없습니다")

    return spec


def _axis_bounds(chart: dict[str, Any]) -> tuple[float, float]:
    values = [float(value) for series in chart["series"] for value in series["values"]]
    raw_min, raw_max = min(values), max(values)
    magnitude_source = max(abs(raw_min), abs(raw_max), 1.0)
    magnitude = 10 ** math.floor(math.log10(magnitude_source))
    step = magnitude / 5

    y_min_given = "y_min" in chart
    y_max_given = "y_max" in chart
    y_min = float(chart["y_min"]) if y_min_given else (
        0 if raw_min >= 0 else math.floor(raw_min / step) * step
    )
    y_max = float(chart["y_max"]) if y_max_given else math.ceil(raw_max / step) * step
    if not y_max_given and y_max <= raw_max:
        y_max += step
    if not y_min_given and y_min >= raw_min and raw_min < 0:
        y_min -= step
    if y_max == y_min:
        if y_max_given:
            y_min -= 1
        else:
            y_max += 1
    return y_min, y_max


def _number_label(value: float, unit: str) -> str:
    if math.isclose(value, round(value), abs_tol=1e-9):
        number = f"{value:,.0f}"
    elif abs(value) < 10:
        number = f"{value:,.2f}".rstrip("0").rstrip(".")
    else:
        number = f"{value:,.1f}".rstrip("0").rstrip(".")
    return f"{number}{unit}"


def _chart_context(chart: dict[str, Any], compact: bool = False, editorial: bool = False) -> dict[str, Any]:
    result = deepcopy(chart)
    width, height = 1264, 470 if compact else (680 if editorial else 640)
    dense_bar = chart["type"] == "bar" and len(chart["labels"]) > 6
    left, right_edge, top, bottom = 125, 1000 if editorial else 1100, 38, 110 if dense_bar else 64
    plot_width = right_edge - left
    plot_height = height - top - bottom
    y_min, y_max = _axis_bounds(chart)
    y_span = y_max - y_min
    unit = ""  # Units are displayed once in the shared figure header.

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
                if series_index % 2 == 0:
                    label_y = max(y - 18 - (series_index // 2) * 19, 20)
                else:
                    label_y = min(y + 34 + (series_index // 2) * 19, height - 42)
                points.append(
                    {
                        "x": x_positions[index],
                        "y": y,
                        "label_y": round(label_y, 2),
                        "label": _number_label(float(value), unit),
                        "show_label": index == len(labels) - 1,
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
                        "height": round(bar_height, 2),
                        "label_x": round(x + bar_width / 2, 2),
                        "label_y": round(value_y + 26 if value < 0 else max(y - 14 - series_index * 18, 19), 2),
                        "label": _number_label(float(value), unit),
                        "show_label": len(labels) <= 6 and len(chart["series"]) == 1,
                    }
                )
            series["points"] = []
            series["polyline"] = ""
            series["bars"] = bars
        enriched_series.append(series)

    if chart["type"] == "line":
        # Space end labels independently of the data points, including ties.
        ends = sorted((series["points"][-1] for series in enriched_series), key=lambda point: point["y"])
        label_gap = 52 if editorial else 34
        for index, point in enumerate(ends):
            point["end_label_y"] = max(point["y"], ends[index - 1]["end_label_y"] + label_gap if index else 24)
        overflow = max(0, ends[-1]["end_label_y"] - (height - bottom))
        for point in ends:
            point["end_label_y"] -= overflow

    tick_count = min(len(labels), 6)
    tick_indices = (
        range(len(labels)) if chart["type"] == "bar" else
        sorted({round(index * (len(labels) - 1) / (tick_count - 1)) for index in range(tick_count)})
    )
    result.update(
        {
            "width": width,
            "height": height,
            "left": left,
            "right_edge": right_edge,
            "dense_bar": dense_bar,
            "ticks": ticks,
            "x_labels": [
                {"x": x_positions[index], "label": labels[index]}
                for index in tick_indices
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
    preview_palette = PALETTE_PREVIEWS.get(document.get("palette_preview"))
    context = deepcopy(document)
    context.update(
        {
            "width": spec.size[0],
            "height": spec.size[1],
            "accent": preview_palette["accent"] if preview_palette else document.get("accent") or DEFAULT_ACCENT,
            "preview_palette": preview_palette,
            "assets_uri": (BASE / "assets").resolve().as_uri(),
            "hero_uri": _hero_uri(document, source_path),
            "highlight": document.get("highlight"),
            "period": document.get("period"),
            "editorial": document.get("variant") == "editorial",
            "focus_index": document.get("focus_index"),
        }
    )
    if document["template"] == "figure-data":
        context["takeaways"] = document.get("takeaways", [])
        context["chart"] = _chart_context(document["chart"], compact=bool(context["takeaways"]), editorial=context["editorial"])
        if context["editorial"]:
            focus_color = preview_palette["data"] if preview_palette else DEFAULT_ACCENT
            for index, series in enumerate(context["chart"]["series"]):
                series["color"] = focus_color if index == context["focus_index"] else "#8B95A1"
        context["figure_unit"] = document["chart"]["unit"]
    elif document["template"] in FIGURE_FIELDS:
        context.update(figure_context(document))
        context["figure_unit"] = document.get("unit")
    return context


def render_html(document: dict[str, Any], source_path: Path) -> str:
    spec = validate_document(document)
    return ENV.get_template(spec.filename).render(**build_context(document, source_path))


def output_path(output_dir: Path, slug: str, suffix: str) -> Path:
    if suffix not in {".html", ".png"}:
        raise ValueError("출력 확장자는 .html 또는 .png여야 합니다")
    return output_dir / f"{safe_slug(slug)}{suffix}"


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"유효한 PNG가 아닙니다: {path}")
    return struct.unpack(">II", header[16:24])


def update_manifest(
    output_dir: Path,
    *,
    slug: str,
    template: str,
    size: tuple[int, int],
    scale: int,
    source: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "manifest.json"
    if path.exists():
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"manifest.json을 읽을 수 없습니다: {exc}") from exc
    else:
        manifest = {}
    cards = manifest.setdefault("cards", {})
    if not isinstance(cards, dict):
        raise ValueError("manifest.json의 cards는 객체여야 합니다")
    cards[slug] = {
        "template": template,
        "file": f"{slug}.png",
        "source": source,
        "width": size[0] * scale,
        "height": size[1] * scale,
        "scale": scale,
    }
    manifest["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    temporary = output_dir / ".manifest.json.tmp"
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def render_document(page: Any, source_path: Path, output_dir: Path, scale: int = 1) -> Path:
    if scale not in {1, 2}:
        raise ValueError("scale은 1 또는 2여야 합니다")
    source_path = source_path.resolve()
    document = load_document(source_path)
    spec = validate_document(document)
    slug = safe_slug(document["slug"])
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_path(output_dir, slug, ".html")
    png_path = output_path(output_dir, slug, ".png")

    temporary_html = html_path.with_name(f".{html_path.name}.tmp")
    temporary_html.write_text(render_html(document, source_path), encoding="utf-8")
    temporary_html.replace(html_path)

    page.set_viewport_size({"width": spec.size[0], "height": spec.size[1]})
    page.goto(html_path.resolve().as_uri(), wait_until="load")
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_function(
        "Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)"
    )
    temporary_png = png_path.with_name(f".{png_path.stem}.tmp.png")
    try:
        page.screenshot(path=str(temporary_png))

        expected = (spec.size[0] * scale, spec.size[1] * scale)
        actual = png_size(temporary_png)
        if actual != expected:
            raise ValueError(
                "PNG 크기가 올바르지 않습니다: "
                f"{actual[0]}×{actual[1]}, expected {expected[0]}×{expected[1]}"
            )
        temporary_png.replace(png_path)
    finally:
        temporary_png.unlink(missing_ok=True)

    update_manifest(
        output_dir,
        slug=slug,
        template=document["template"],
        size=spec.size,
        scale=scale,
        source=source_path.name,
    )
    return png_path


def select_sources(input_path: Path | None, render_all: bool, examples_dir: Path) -> list[Path]:
    if (input_path is None) == (not render_all):
        raise ValueError("입력 JSON 또는 --all 중 하나만 선택해야 합니다")
    if render_all:
        sources = sorted(examples_dir.glob("*.json"))
        if not sources:
            raise ValueError(f"예제 JSON을 찾을 수 없습니다: {examples_dir}")
        return sources
    assert input_path is not None
    if not input_path.is_file():
        raise ValueError(f"입력 JSON을 찾을 수 없습니다: {input_path}")
    if input_path.suffix.lower() != ".json":
        raise ValueError("입력 파일은 .json이어야 합니다")
    return [input_path]


def render_sources(
    sources: list[Path],
    output_dir: Path,
    scale: int = 1,
    playwright_factory: Any = None,
) -> list[Path]:
    if not sources:
        raise ValueError("렌더할 JSON이 없습니다")
    if scale not in {1, 2}:
        raise ValueError("scale은 1 또는 2여야 합니다")
    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright가 설치되지 않았습니다: pip install -r requirements.txt") from exc
        playwright_factory = sync_playwright

    outputs = []
    with playwright_factory() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": 1, "height": 1},
                device_scale_factor=scale,
            )
            for source in sources:
                path = render_document(page, source, output_dir, scale)
                outputs.append(path)
                print(f"[ok] {path}")
        finally:
            browser.close()
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UNIT TX 리서치 이미지 렌더러")
    parser.add_argument("input", nargs="?", type=Path, help="렌더할 JSON 파일")
    parser.add_argument("--all", action="store_true", dest="render_all", help="examples의 모든 JSON 렌더")
    parser.add_argument("--output-dir", type=Path, default=BASE / "out", help="출력 디렉터리")
    parser.add_argument("--scale", type=int, choices=(1, 2), default=1, help="PNG 배율")
    args = parser.parse_args(argv)

    try:
        sources = select_sources(args.input, args.render_all, BASE / "examples")
        outputs = render_sources(sources, args.output_dir, args.scale)
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    print(f"[done] {len(outputs)} images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
