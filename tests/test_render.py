from __future__ import annotations

import unittest

from render import TEMPLATES, safe_slug, validate_document


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


if __name__ == "__main__":
    unittest.main()
