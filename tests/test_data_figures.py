from copy import deepcopy
from pathlib import Path
import unittest

from figure_models import figure_context
from render import DATA_TEMPLATES, build_context, load_document, render_html, validate_document


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def document(kind):
    return load_document(EXAMPLES / f"{kind}.json")


class DataFigureTests(unittest.TestCase):
    def test_five_data_templates_share_dimensions_and_required_metadata(self):
        self.assertEqual(len(DATA_TEMPLATES), 5)
        for kind in DATA_TEMPLATES:
            sample = document(kind)
            with self.subTest(kind=kind):
                self.assertEqual(validate_document(sample).size, (1440, 1200))
                for field in ("source", "date", "title"):
                    invalid = deepcopy(sample)
                    invalid.pop(field)
                    with self.assertRaisesRegex(ValueError, field):
                        validate_document(invalid)

    def test_trend_does_not_add_kpis_or_decorative_copy(self):
        sample = document("figure-data")
        sample["highlight"] = "SHOULD NOT APPEAR"
        html = render_html(sample, EXAMPLES / "figure-data.json")
        self.assertNotIn("takeaway-grid", html)
        self.assertNotIn("SHOULD NOT APPEAR", html)
        self.assertEqual(html.count("Example data · replace before publishing"), 1)

    def test_daily_trend_retains_all_data_and_both_end_tick_labels(self):
        sample = document("figure-data")
        sample["chart"] = {
            "type": "line", "unit": "달러", "labels": [f"D{i:03}" for i in range(366)],
            "series": [{"name": "시리즈", "values": list(range(366))}],
        }
        chart = build_context(sample, EXAMPLES / "figure-data.json")["chart"]
        self.assertEqual(len(chart["series"][0]["points"]), 366)
        self.assertEqual(len(chart["series"][0]["polyline"].split()), 366)
        self.assertLessEqual(len(chart["x_labels"]), 6)
        self.assertEqual(chart["x_labels"][0]["label"], "D000")
        self.assertEqual(chart["x_labels"][-1]["label"], "D365")
        sample["chart"]["labels"].append("D366")
        sample["chart"]["series"][0]["values"].append(366)
        with self.assertRaisesRegex(ValueError, "366"):
            validate_document(sample)

    def test_three_identical_end_values_have_separated_labels(self):
        sample = document("figure-data")
        sample["chart"]["series"] = [
            {"name": str(index), "values": [0] * 24} for index in range(3)
        ]
        chart = build_context(sample, EXAMPLES / "figure-data.json")["chart"]
        ends = sorted(series["points"][-1]["end_label_y"] for series in chart["series"])
        self.assertTrue(all(b - a >= 34 for a, b in zip(ends, ends[1:])))
        self.assertGreaterEqual(ends[0], 24)
        self.assertLessEqual(ends[-1], chart["height"] - 64)

    def test_legacy_bar_keeps_every_category_instead_of_sampling_them(self):
        sample = document("figure-data")
        sample["chart"] = {
            "type": "bar", "unit": "개", "labels": [f"항목 {i}" for i in range(12)],
            "series": [{"name": "수량", "values": list(range(12))}],
        }
        chart = build_context(sample, EXAMPLES / "figure-data.json")["chart"]
        self.assertEqual([label["label"] for label in chart["x_labels"]], sample["chart"]["labels"])
        self.assertEqual(chart["series"][0]["bars"][0]["height"], 0)

    def test_trend_rejects_numbers_that_would_clip_axis_labels(self):
        sample = document("figure-data")
        sample["chart"].pop("y_min")
        sample["chart"].pop("y_max")
        sample["chart"]["series"][0]["values"][0] = 123456789
        with self.assertRaisesRegex(ValueError, "단위"):
            validate_document(sample)

    def test_trend_rejects_generated_ticks_that_exceed_label_width(self):
        sample = document("figure-data")
        for chart_type in ("line", "bar"):
            sample["chart"] = {
                "type": chart_type, "unit": "개", "labels": ["2025", "2026"],
                "series": [{"name": "변화", "values": [-99999, 99999]}],
                "y_min": -99999, "y_max": 99999,
            }
            with self.subTest(chart_type=chart_type), self.assertRaisesRegex(ValueError, "단위"):
                validate_document(sample)

    def test_ranking_sorts_without_mutating_and_preserves_signed_lengths(self):
        sample = document("figure-ranking")
        sample["items"] = [{"label": "음수", "value": -5}, {"label": "영", "value": 0}, {"label": "양수", "value": 10}]
        original = deepcopy(sample)
        context = figure_context(sample)
        self.assertEqual(sample, original)
        items = context["ranked_items"]
        self.assertEqual([item["value"] for item in items], [10, 0, -5])
        self.assertEqual(items[1]["width"], 0)
        self.assertAlmostEqual(items[0]["width"], items[2]["width"] * 2)
        self.assertEqual(items[0]["x"], context["ranking_zero"])
        self.assertAlmostEqual(items[2]["x"] + items[2]["width"], context["ranking_zero"])
        self.assertEqual(items[2]["formatted"], "-5")

    def test_zero_only_ranking_is_not_drawn_as_nonzero_bars(self):
        sample = document("figure-ranking")
        for item in sample["items"]:
            item["value"] = 0
        self.assertTrue(all(item["width"] == 0 for item in figure_context(sample)["ranked_items"]))

    def test_composition_rejects_invalid_totals_instead_of_normalizing(self):
        for values in ([50, 20, 10, 10], [101, -1, 0, 0], [25, 25, 50]):
            sample = document("figure-composition")
            sample["groups"][0]["values"] = values
            with self.subTest(values=values), self.assertRaises(ValueError):
                validate_document(sample)

    def test_zero_and_small_composition_shares_keep_explicit_labels(self):
        sample = document("figure-composition")
        sample["groups"] = [{"label": "2026", "values": [99.9, 0.1, 0, 0]}]
        html = render_html(sample, EXAMPLES / "figure-composition.json")
        for value in ("99.9%", "0.1%", "0%"):
            self.assertIn(value, html)
        for name in sample["categories"]:
            self.assertIn(name, html)

    def test_composition_requires_percent_units_and_unique_categories(self):
        sample = document("figure-composition")
        sample["unit"] = "달러"
        with self.assertRaisesRegex(ValueError, "unit"):
            validate_document(sample)
        sample["unit"] = "%"
        sample["categories"][1] = sample["categories"][0]
        with self.assertRaisesRegex(ValueError, "중복"):
            validate_document(sample)

    def test_four_metrics_require_units_and_change_comparison_period(self):
        sample = document("figure-metrics")
        for missing in ("unit", "label", "value"):
            invalid = deepcopy(sample)
            invalid["metrics"][0].pop(missing)
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, missing):
                validate_document(invalid)
        sample["metrics"][0]["change"].pop("period")
        with self.assertRaisesRegex(ValueError, "period"):
            validate_document(sample)

    def test_metric_change_is_optional_and_signed_not_just_color_coded(self):
        sample = document("figure-metrics")
        context = figure_context(sample)
        self.assertEqual(context["metrics"][0]["change"]["formatted"], "+3.9")
        self.assertEqual(context["metrics"][-1]["change"]["formatted"], "-2.4")
        for metric in sample["metrics"]:
            metric.pop("change")
        html = render_html(sample, EXAMPLES / "figure-metrics.json")
        self.assertNotIn("metric-change", html)
        self.assertNotIn("전월 대비", html)

    def test_comparison_requires_one_value_for_each_column(self):
        sample = document("figure-comparison")
        sample["rows"][0]["values"].pop()
        with self.assertRaisesRegex(ValueError, "columns"):
            validate_document(sample)

    def test_comparison_escapes_user_supplied_cell_content(self):
        sample = document("figure-comparison")
        sample["rows"][0]["values"][0] = "<b>데이터</b>"
        html = render_html(sample, EXAMPLES / "figure-comparison.json")
        self.assertIn("&lt;b&gt;데이터&lt;/b&gt;", html)
        self.assertNotIn("<b>", html)

    def test_numeric_figures_reject_nonfinite_and_boolean_inputs(self):
        for kind, field in (("figure-ranking", "items"), ("figure-metrics", "metrics")):
            for value in (True, float("nan"), float("inf"), "42"):
                sample = document(kind)
                sample[field][0]["value"] = value
                with self.subTest(kind=kind, value=value), self.assertRaisesRegex(ValueError, "숫자"):
                    validate_document(sample)

    def test_long_copy_is_rejected_instead_of_shrinking_the_font(self):
        sample = document("figure-comparison")
        sample["rows"][0]["values"][0] = "가" * 13
        with self.assertRaisesRegex(ValueError, "24"):
            validate_document(sample)
        sample = document("figure-data")
        sample["title"] = "가" * 23
        with self.assertRaisesRegex(ValueError, "44"):
            validate_document(sample)


if __name__ == "__main__":
    unittest.main()
