from __future__ import annotations

import unittest
from pathlib import Path

from render import TEMPLATES, build_context, render_html, safe_slug, validate_document


def cover_document(**overrides):
    document = {
        "template": "cover-editorial",
        "slug": "sample-cover",
        "eyebrow": "UNIT TX RESEARCH",
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
        "eyebrow": "TRANSACTION FLOW",
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

    def test_cover_rejects_more_than_two_title_lines(self):
        document = cover_document(title="첫째 줄\n둘째 줄\n셋째 줄")
        with self.assertRaisesRegex(ValueError, "두 줄"):
            validate_document(document)

    def test_invalid_accent_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "accent"):
            validate_document(cover_document(accent="orange"))

    def test_framework_accepts_only_three_to_five_nodes(self):
        document = {
            "template": "figure-framework",
            "slug": "framework",
            "eyebrow": "TRANSACTION FLOW",
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


class HtmlTests(unittest.TestCase):
    def test_html_autoescapes_user_copy(self):
        document = cover_document(title="UNIT <script>alert(1)</script>")
        html = render_html(document, Path("examples/cover-editorial.json"))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_line_chart_context_contains_svg_points_and_ticks(self):
        document = data_document()
        document["chart"]["labels"] = ["1Y", "2Y", "3Y", "4Y", "5Y", "6Y"]
        document["chart"]["series"][0]["values"] = [92, 83, 74, 66, 59, 51]

        context = build_context(document, Path("examples/figure-data.json"))

        self.assertEqual(len(context["chart"]["series"][0]["points"]), 6)
        self.assertEqual(len(context["chart"]["ticks"]), 5)
        self.assertIn(",", context["chart"]["series"][0]["polyline"])

    def test_bar_chart_context_contains_rectangles(self):
        document = data_document()
        document["chart"]["type"] = "bar"

        context = build_context(document, Path("examples/figure-data.json"))

        self.assertEqual(len(context["chart"]["series"][0]["bars"]), 3)
        self.assertTrue(all(bar["height"] >= 0 for bar in context["chart"]["series"][0]["bars"]))

    def test_dark_cover_uses_exact_logo_asset_with_dark_treatment(self):
        html = render_html(object_cover_document(), Path("examples/cover-object.json"))
        self.assertIn("unit-tx-logo.png", html)
        self.assertIn("logo-on-dark", html)

    def test_framework_renders_nodes_and_connectors(self):
        html = render_html(framework_document(), Path("examples/figure-framework.json"))
        self.assertEqual(html.count('class="framework-node"'), 3)
        self.assertIn("flow-connector", html)
        self.assertIn("UNIT TX Research", html)

    def test_hero_image_cannot_escape_input_directory(self):
        document = object_cover_document(hero_image="../outside.png")
        with self.assertRaisesRegex(ValueError, "hero_image"):
            build_context(document, Path("examples/cover-object.json"))


if __name__ == "__main__":
    unittest.main()
