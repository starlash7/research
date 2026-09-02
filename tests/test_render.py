from __future__ import annotations

import unittest
import contextlib
import hashlib
import io
import json
import re
import struct
import tempfile
from pathlib import Path

from render import (
    DEFAULT_ACCENT,
    SERIES_COLORS,
    TEMPLATES,
    build_context,
    load_document,
    output_path,
    png_size,
    render_document,
    render_html,
    render_sources,
    safe_slug,
    select_sources,
    update_manifest,
    validate_document,
)


def cover_document(**overrides):
    document = {
        "template": "cover-editorial",
        "slug": "sample-cover",
        "category": "ONCHAIN RESEARCH",
        "title": "온체인 결제의 다음 단계",
        "subtitle": "보유에서 실제 사용으로 이동하는 시장을 읽습니다.",
        "date": "2026.09.01",
    }
    document.update(overrides)
    return document


def data_document(**overrides):
    document = {
        "template": "figure-data",
        "slug": "sample-data",
        "title": "상위 토큰의 생존율은 빠르게 낮아진다",
        "source": "Example data",
        "date": "2026.09.01",
        "chart": {
            "type": "line",
            "unit": "%",
            "labels": ["1Y", "2Y", "3Y"],
            "series": [{"name": "생존율", "values": [92.0, 78.0, 63.0]}],
        },
        "takeaways": [{"label": "표본", "value": "1,539"}],
    }
    document.update(overrides)
    return document


def object_cover_document(**overrides):
    document = cover_document(
        template="cover-object",
        slug="sample-object-cover",
        title="스테이블코인은\n결제 레이어가 될 수 있을까",
    )
    document.update(overrides)
    return document


def framework_document(**overrides):
    document = {
        "template": "figure-framework",
        "slug": "sample-framework",
        "title": "온체인 결제는 네 단계로 완결된다",
        "source": "UNIT TX Research",
        "date": "2026.09.01",
        "nodes": [
            {"title": "Intent", "body": "사용자가 결제 의사를 만든다."},
            {"title": "Route", "body": "최적 경로와 자산을 선택한다."},
            {"title": "Settle", "body": "네트워크에서 거래를 확정한다."},
        ],
    }
    document.update(overrides)
    return document


class ValidationTests(unittest.TestCase):
    def test_unit_tx_uses_toss_blue_as_the_default_accent(self):
        self.assertEqual(DEFAULT_ACCENT, "#0064FF")
        self.assertEqual(SERIES_COLORS, ("#0064FF", "#123B7A", "#0C78B7"))

    def test_every_template_has_fixed_dimensions(self):
        self.assertEqual(TEMPLATES["cover-editorial"].size, (1440, 756))
        self.assertEqual(TEMPLATES["cover-object"].size, (1440, 756))
        self.assertEqual(TEMPLATES["figure-framework"].size, (1440, 810))
        self.assertEqual(TEMPLATES["figure-data"].size, (1440, 1200))

    def test_unknown_template_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "지원하지 않는 템플릿"):
            validate_document({"template": "unknown", "slug": "sample"})

    def test_unsafe_slug_is_rejected(self):
        for slug in ("../escape", "UPPERCASE", "two words", "ends-"):
            with self.subTest(slug=slug), self.assertRaisesRegex(ValueError, "slug"):
                safe_slug(slug)

    def test_quantitative_figure_requires_source_and_date(self):
        for missing in ("source", "date"):
            document = data_document()
            document.pop(missing)
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, missing):
                validate_document(document)

    def test_both_covers_require_category(self):
        for document in (cover_document(), object_cover_document()):
            document.pop("category")
            with self.subTest(template=document["template"]), self.assertRaisesRegex(
                ValueError, "category"
            ):
                validate_document(document)

    def test_cover_category_has_a_fixed_display_width_limit(self):
        with self.assertRaisesRegex(ValueError, "category"):
            validate_document(cover_document(category="A" * 25))

    def test_cover_rejects_more_than_two_title_lines(self):
        document = cover_document(title="첫째 줄\n둘째 줄\n셋째 줄")
        with self.assertRaisesRegex(ValueError, "두 줄"):
            validate_document(document)

    def test_cover_rejects_a_line_too_wide_for_the_canvas(self):
        document = cover_document(title="가" * 16)
        with self.assertRaisesRegex(ValueError, "한 줄"):
            validate_document(document)

    def test_invalid_accent_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "accent"):
            validate_document(cover_document(accent="orange"))

    def test_framework_accepts_only_three_to_five_nodes(self):
        document = {
            "template": "figure-framework",
            "slug": "framework",
            "title": "결제 트랜잭션의 흐름",
            "source": "UNIT TX Research",
            "date": "2026.09.01",
            "nodes": [{"title": "Node", "body": "Body"}] * 2,
        }
        with self.assertRaisesRegex(ValueError, "3-5"):
            validate_document(document)

    def test_chart_rejects_unknown_type_and_mismatched_series(self):
        unknown = data_document()
        unknown["chart"]["type"] = "pie"
        with self.assertRaisesRegex(ValueError, "line 또는 bar"):
            validate_document(unknown)

        mismatched = data_document()
        mismatched["chart"]["series"][0]["values"] = [92.0]
        with self.assertRaisesRegex(ValueError, "labels"):
            validate_document(mismatched)

    def test_chart_requires_unit_text_labels_and_named_series(self):
        missing_unit = data_document()
        missing_unit["chart"].pop("unit")
        with self.assertRaisesRegex(ValueError, "unit"):
            validate_document(missing_unit)

        invalid_label = data_document()
        invalid_label["chart"]["labels"][0] = None
        with self.assertRaisesRegex(ValueError, "labels"):
            validate_document(invalid_label)

        unnamed_series = data_document()
        unnamed_series["chart"]["series"][0]["name"] = "   "
        with self.assertRaisesRegex(ValueError, "name"):
            validate_document(unnamed_series)

    def test_chart_rejects_non_finite_values_and_null_bounds(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            document = data_document()
            document["chart"]["series"][0]["values"][0] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "유한"):
                validate_document(document)

        document = data_document()
        document["chart"]["y_min"] = None
        with self.assertRaisesRegex(ValueError, "y_min"):
            validate_document(document)

    def test_chart_bounds_must_contain_every_value(self):
        document = data_document()
        document["chart"].update({"y_min": 0, "y_max": 50})
        with self.assertRaisesRegex(ValueError, "범위"):
            validate_document(document)

    def test_takeaways_require_label_and_value_text(self):
        document = data_document()
        document["takeaways"] = [{"label": "표본"}]
        with self.assertRaisesRegex(ValueError, "takeaway"):
            validate_document(document)

    def test_required_copy_fields_must_be_text(self):
        document = cover_document(subtitle=42)
        with self.assertRaisesRegex(ValueError, "subtitle"):
            validate_document(document)


class DocumentationTests(unittest.TestCase):
    def test_goal_defines_clone_and_data_only_workflow(self):
        goal = Path("goal.md").read_text(encoding="utf-8")
        for phrase in ("clone", "자료와 데이터", "일관된", "render.py"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, goal)

    def test_typography_uses_local_suit_variable_font(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn('font-family: "SUIT Variable"', styles)
        self.assertIn('url("./SUIT-Variable.woff2")', styles)
        self.assertNotIn("Pretendard", styles)
        self.assertTrue(Path("assets/SUIT-Variable.woff2").is_file())
        self.assertTrue(Path("assets/SUIT-LICENSE.txt").is_file())

    def test_typography_uses_only_the_shared_weight_tokens(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        weights = set(re.findall(r"font-weight:\s*([^;]+);", styles))
        self.assertEqual(
            weights,
            {
                "100 900",
                "var(--weight-regular)",
                "var(--weight-medium)",
                "var(--weight-bold)",
            },
        )


class HtmlTests(unittest.TestCase):
    def test_templates_do_not_require_decorative_eyebrows(self):
        for document in (cover_document(), object_cover_document(), framework_document()):
            with self.subTest(template=document["template"]):
                validate_document(document)

    def test_html_autoescapes_user_copy(self):
        document = cover_document(title="UNIT <script>alert(1)</script>")
        html = render_html(document, Path("examples/cover-editorial.json"))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_both_covers_render_one_category(self):
        for document, path in (
            (
                cover_document(category="ONCHAIN & RESEARCH"),
                Path("examples/cover-editorial.json"),
            ),
            (
                object_cover_document(category="ONCHAIN & RESEARCH"),
                Path("examples/cover-object.json"),
            ),
        ):
            with self.subTest(template=document["template"]):
                html = render_html(document, path)
                self.assertEqual(html.count('class="cover-category"'), 1)
                self.assertIn("ONCHAIN &amp; RESEARCH", html)

    def test_line_chart_context_contains_svg_points_and_ticks(self):
        document = data_document()
        document["chart"]["labels"] = ["1Y", "2Y", "3Y", "4Y", "5Y", "6Y"]
        document["chart"]["series"][0]["values"] = [92, 83, 74, 66, 59, 51]

        context = build_context(document, Path("examples/figure-data.json"))

        self.assertEqual(len(context["chart"]["series"][0]["points"]), 6)
        self.assertEqual(len(context["chart"]["ticks"]), 5)
        self.assertIn(",", context["chart"]["series"][0]["polyline"])

    def test_close_line_series_place_labels_on_opposite_sides(self):
        document = data_document()
        document["chart"]["series"].append(
            {"name": "비교군", "values": [91.0, 77.0, 62.0]}
        )

        context = build_context(document, Path("examples/figure-data.json"))

        first = context["chart"]["series"][0]["points"]
        second = context["chart"]["series"][1]["points"]
        self.assertTrue(all(point["label_y"] < point["y"] for point in first))
        self.assertTrue(all(point["label_y"] > point["y"] for point in second))

    def test_bar_chart_context_contains_rectangles(self):
        document = data_document()
        document["chart"]["type"] = "bar"

        context = build_context(document, Path("examples/figure-data.json"))

        self.assertEqual(len(context["chart"]["series"][0]["bars"]), 3)
        self.assertTrue(all(bar["height"] >= 0 for bar in context["chart"]["series"][0]["bars"]))

    def test_explicit_axis_bounds_are_preserved(self):
        document = data_document()
        document["chart"]["series"][0]["values"] = [25, 50, 100]
        document["chart"].update({"y_min": 0, "y_max": 100})

        context = build_context(document, Path("examples/figure-data.json"))

        self.assertEqual(context["chart"]["y_min"], 0)
        self.assertEqual(context["chart"]["y_max"], 100)

    def test_dark_cover_uses_exact_logo_asset_with_dark_treatment(self):
        html = render_html(object_cover_document(), Path("examples/cover-object.json"))
        self.assertIn("unit-tx-logo.png", html)
        self.assertIn("logo-on-dark", html)

    def test_dark_cover_has_no_generated_graph_or_symbol(self):
        html = render_html(object_cover_document(), Path("examples/cover-object.json"))
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertNotIn("object-stage", html)
        self.assertNotIn("signal-map", html)
        self.assertNotIn("signal-route", html)
        self.assertNotIn("signal-node", html)
        self.assertNotIn("signal-core", html)
        self.assertNotIn(".signal-", styles)

    def test_dark_cover_uses_a_neutral_black_surface(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn("--dark-surface: #0a0a0a;", styles)
        self.assertRegex(
            styles,
            r"\.cover-object-canvas\s*\{[^}]*background: var\(--dark-surface\);",
        )
        self.assertNotIn("#071426", styles)

    def test_bright_templates_use_the_blue_accent(self):
        for document, path in (
            (cover_document(), Path("examples/cover-editorial.json")),
            (data_document(), Path("examples/figure-data.json")),
            (framework_document(), Path("examples/figure-framework.json")),
        ):
            with self.subTest(template=document["template"]):
                html = render_html(document, path)
                self.assertIn("--accent: #0064FF", html)

    def test_covers_do_not_repeat_the_brand_byline(self):
        for document, path in (
            (cover_document(), Path("examples/cover-editorial.json")),
            (object_cover_document(), Path("examples/cover-object.json")),
        ):
            with self.subTest(template=document["template"]):
                html = render_html(document, path)
                self.assertNotIn("UNIT TX Research", html)

    def test_framework_source_is_not_repeated_in_the_footer(self):
        html = render_html(framework_document(), Path("examples/figure-framework.json"))
        self.assertEqual(html.count("UNIT TX Research"), 1)

    def test_every_template_uses_one_fixed_bottom_date_and_logo(self):
        documents = (
            (cover_document(), Path("examples/cover-editorial.json")),
            (object_cover_document(), Path("examples/cover-object.json")),
            (data_document(), Path("examples/figure-data.json")),
            (framework_document(), Path("examples/figure-framework.json")),
        )
        for document, path in documents:
            with self.subTest(template=document["template"]):
                html = render_html(document, path)
                self.assertIn('class="fixed-footer', html)
                self.assertIn('class="fixed-date num"', html)
                self.assertEqual(html.count("unit-tx-logo.png"), 1)
                self.assertNotIn("date-chip", html)
                self.assertNotIn("object-date", html)

    def test_fixed_footer_has_no_center_copy(self):
        documents = (
            (cover_document(topic="DUPLICATE TOPIC"), Path("examples/cover-editorial.json")),
            (object_cover_document(topic="DUPLICATE TOPIC"), Path("examples/cover-object.json")),
            (data_document(note="DUPLICATE NOTE"), Path("examples/figure-data.json")),
            (framework_document(), Path("examples/figure-framework.json")),
        )
        for document, path in documents:
            with self.subTest(template=document["template"]):
                html = render_html(document, path)
                self.assertNotIn("footer-topic", html)
                self.assertNotIn("DUPLICATE TOPIC", html)
                self.assertNotIn("DUPLICATE NOTE", html)

    def test_templates_omit_decorative_and_fallback_copy(self):
        documents = (
            (
                cover_document(
                    eyebrow="ADOPTION BRIEF",
                    index_label="ONCHAIN / USE CASES",
                ),
                Path("examples/cover-editorial.json"),
            ),
            (
                object_cover_document(eyebrow="SYSTEM NOTE"),
                Path("examples/cover-object.json"),
            ),
            (
                framework_document(eyebrow="TRANSACTION FLOW"),
                Path("examples/figure-framework.json"),
            ),
        )
        forbidden = (
            "ADOPTION BRIEF",
            "ONCHAIN / USE CASES",
            "SYSTEM NOTE",
            "SIGNAL MAP",
            "FIELD 01",
            "ROUTING LAYER",
            "ACTIVE",
            "TRANSACTION FLOW",
            "Key read",
            "각 단계의 마찰을 줄일수록",
            "LOCAL IMAGE / INPUT",
        )
        for document, path in documents:
            html = render_html(document, path)
            with self.subTest(template=document["template"]):
                for copy in forbidden:
                    self.assertNotIn(copy, html)

    def test_all_dates_use_exact_black_text(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn("--date-on-light: #000000;", styles)
        self.assertNotIn("--date-on-dark", styles)
        self.assertRegex(
            styles,
            r"\.fixed-date\s*\{[^}]*color: var\(--date-on-light\);",
        )
        self.assertRegex(
            styles,
            r"\.object-footer \.fixed-date\s*\{[^}]*color: var\(--date-on-light\);[^}]*background: #ffffff;",
        )

    def test_information_cards_use_the_rounder_shared_radius(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn("--radius: 28px;", styles)

    def test_brand_lockup_uses_one_color_per_surface(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn("--brand-on-light: #0c1b33;", styles)
        self.assertIn("--brand-on-dark: #ffffff;", styles)
        self.assertRegex(
            styles,
            r"\.brand-lockup\s*\{[^}]*color: var\(--brand-on-light\);",
        )
        self.assertRegex(
            styles,
            r"\.object-footer \.brand-lockup\s*\{[^}]*color: var\(--brand-on-dark\);",
        )

    def test_fixed_footer_uses_the_six_percent_safe_area(self):
        styles = Path("assets/styles.css").read_text(encoding="utf-8")
        self.assertIn("left: 6%;", styles)
        self.assertIn("right: 6%;", styles)
        self.assertIn("bottom: 6%;", styles)

    def test_all_templates_include_the_shared_fixed_footer_partial(self):
        for template in ("cover-editorial", "cover-object", "figure-data", "figure-framework"):
            source = Path("templates", f"{template}.html").read_text(encoding="utf-8")
            with self.subTest(template=template):
                self.assertIn('{% include "partials/fixed-footer.html" %}', source)

    def test_framework_renders_nodes_and_connectors(self):
        html = render_html(framework_document(), Path("examples/figure-framework.json"))
        self.assertEqual(html.count('class="framework-node"'), 3)
        self.assertIn("flow-connector", html)
        self.assertIn("UNIT TX Research", html)

    def test_hero_image_cannot_escape_input_directory(self):
        document = object_cover_document(hero_image="../outside.png")
        with self.assertRaisesRegex(ValueError, "hero_image"):
            build_context(document, Path("examples/cover-object.json"))

    def test_html_uses_absolute_local_assets(self):
        html = render_html(cover_document(), Path("examples/cover-editorial.json"))
        self.assertIn("file:", html)
        self.assertNotIn("../assets", html)


class OutputTests(unittest.TestCase):
    def test_output_path_uses_slug_and_suffix(self):
        self.assertEqual(output_path(Path("out"), "sample", ".png"), Path("out/sample.png"))
        self.assertEqual(output_path(Path("out"), "sample", ".html"), Path("out/sample.html"))

    def test_manifest_update_preserves_unrelated_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "manifest.json").write_text(
                json.dumps({"cards": {"old": {"template": "cover-editorial"}}}),
                encoding="utf-8",
            )

            path = update_manifest(
                output,
                slug="new",
                template="figure-data",
                size=(1440, 1200),
                scale=1,
                source="figure-data.json",
            )

            cards = json.loads(path.read_text(encoding="utf-8"))["cards"]
            self.assertEqual(set(cards), {"old", "new"})
            self.assertEqual(cards["new"]["width"], 1440)
            self.assertEqual(cards["new"]["height"], 1200)

    def test_png_size_reads_ihdr_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.png"
            path.write_bytes(
                b"\x89PNG\r\n\x1a\n"
                + struct.pack(">I", 13)
                + b"IHDR"
                + struct.pack(">II", 1440, 756)
            )

            self.assertEqual(png_size(path), (1440, 756))

    def test_png_size_rejects_non_png(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.png"
            path.write_bytes(b"not a png")

            with self.assertRaisesRegex(ValueError, "PNG"):
                png_size(path)

    def test_render_document_writes_exact_viewport_outputs(self):
        class FakePage:
            def __init__(self):
                self.viewport = None
                self.url = None
                self.waits = []

            def set_viewport_size(self, size):
                self.viewport = size

            def goto(self, url, wait_until):
                self.url = url
                self.wait_until = wait_until

            def wait_for_function(self, expression):
                self.waits.append(expression)

            def screenshot(self, path):
                Path(path).write_bytes(
                    b"\x89PNG\r\n\x1a\n"
                    + struct.pack(">I", 13)
                    + b"IHDR"
                    + struct.pack(">II", self.viewport["width"], self.viewport["height"])
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "cover.json"
            source.write_text(json.dumps(cover_document()), encoding="utf-8")
            output = root / "out"
            page = FakePage()

            png = render_document(page, source, output, scale=1)

            self.assertEqual(page.viewport, {"width": 1440, "height": 756})
            self.assertEqual(page.wait_until, "load")
            self.assertTrue(page.url.startswith("file:"))
            self.assertEqual(len(page.waits), 2)
            self.assertEqual(png, output / "sample-cover.png")
            self.assertTrue((output / "sample-cover.html").is_file())
            self.assertTrue((output / "manifest.json").is_file())

    def test_render_document_rejects_wrong_png_dimensions(self):
        class WrongSizePage:
            def set_viewport_size(self, size):
                pass

            def goto(self, url, wait_until):
                pass

            def wait_for_function(self, expression):
                pass

            def screenshot(self, path):
                Path(path).write_bytes(
                    b"\x89PNG\r\n\x1a\n"
                    + struct.pack(">I", 13)
                    + b"IHDR"
                    + struct.pack(">II", 1, 1)
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "cover.json"
            source.write_text(json.dumps(cover_document()), encoding="utf-8")
            output = root / "out"
            output.mkdir()
            previous = output / "sample-cover.png"
            previous.write_bytes(b"previous image")

            with self.assertRaisesRegex(ValueError, "크기"):
                render_document(WrongSizePage(), source, output, scale=1)

            self.assertEqual(previous.read_bytes(), b"previous image")


class CliTests(unittest.TestCase):
    def test_select_sources_requires_exactly_one_mode(self):
        with self.assertRaisesRegex(ValueError, "하나"):
            select_sources(None, False, Path("examples"))
        with self.assertRaisesRegex(ValueError, "하나"):
            select_sources(Path("one.json"), True, Path("examples"))

    def test_select_sources_returns_sorted_json_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            examples = Path(directory)
            (examples / "z.json").write_text("{}", encoding="utf-8")
            (examples / "a.json").write_text("{}", encoding="utf-8")
            (examples / "ignore.txt").write_text("{}", encoding="utf-8")

            sources = select_sources(None, True, examples)

            self.assertEqual([path.name for path in sources], ["a.json", "z.json"])

    def test_select_sources_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "찾을 수"):
                select_sources(Path(directory) / "missing.json", False, Path(directory))

    def test_render_sources_reuses_one_browser_for_all_documents(self):
        class FakePage:
            def __init__(self, scale):
                self.scale = scale
                self.viewport = None
                self.screenshots = 0

            def set_viewport_size(self, size):
                self.viewport = size

            def goto(self, url, wait_until):
                pass

            def wait_for_function(self, expression):
                pass

            def screenshot(self, path):
                self.screenshots += 1
                Path(path).write_bytes(
                    b"\x89PNG\r\n\x1a\n"
                    + struct.pack(">I", 13)
                    + b"IHDR"
                    + struct.pack(
                        ">II",
                        self.viewport["width"] * self.scale,
                        self.viewport["height"] * self.scale,
                    )
                )

        class FakeBrowser:
            def __init__(self):
                self.new_page_calls = 0
                self.closed = False
                self.page = None

            def new_page(self, viewport, device_scale_factor):
                self.new_page_calls += 1
                self.page = FakePage(device_scale_factor)
                return self.page

            def close(self):
                self.closed = True

        class FakeChromium:
            def __init__(self):
                self.launch_calls = 0
                self.browser = FakeBrowser()

            def launch(self):
                self.launch_calls += 1
                return self.browser

        class FakePlaywright:
            def __init__(self):
                self.chromium = FakeChromium()

        class FakeManager:
            def __init__(self):
                self.playwright = FakePlaywright()

            def __enter__(self):
                return self.playwright

            def __exit__(self, exc_type, exc, traceback):
                pass

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cover = root / "cover.json"
            data = root / "data.json"
            cover.write_text(json.dumps(cover_document()), encoding="utf-8")
            data.write_text(json.dumps(data_document()), encoding="utf-8")
            manager = FakeManager()

            with contextlib.redirect_stdout(io.StringIO()):
                outputs = render_sources(
                    [cover, data],
                    root / "out",
                    scale=2,
                    playwright_factory=lambda: manager,
                )

            chromium = manager.playwright.chromium
            self.assertEqual(chromium.launch_calls, 1)
            self.assertEqual(chromium.browser.new_page_calls, 1)
            self.assertTrue(chromium.browser.closed)
            self.assertEqual(chromium.browser.page.screenshots, 2)
            self.assertEqual([png_size(path) for path in outputs], [(2880, 1512), (2880, 2400)])


class ExampleTests(unittest.TestCase):
    def test_logo_asset_matches_the_supplied_unit_tx_mark(self):
        logo = Path(__file__).parents[1] / "assets" / "unit-tx-logo.png"

        self.assertEqual(
            hashlib.sha256(logo.read_bytes()).hexdigest(),
            "57718cc67c3b14bd92b1caf8253873612cac9a975e132d5c57b7aa948cd228e1",
        )

    def test_example_set_covers_all_templates(self):
        examples = Path(__file__).parents[1] / "examples"
        documents = [load_document(path) for path in sorted(examples.glob("*.json"))]

        self.assertEqual({document["template"] for document in documents}, set(TEMPLATES))
        for document in documents:
            validate_document(document)

    def test_visible_example_copy_has_no_em_or_en_dash(self):
        examples = Path(__file__).parents[1] / "examples"
        for path in sorted(examples.glob("*.json")):
            with self.subTest(path=path.name):
                document = load_document(path)
                html = render_html(document, path)
                self.assertNotIn("—", html)
                self.assertNotIn("–", html)


if __name__ == "__main__":
    unittest.main()
