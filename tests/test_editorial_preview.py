from copy import deepcopy
from pathlib import Path
import unittest

from render import build_context, load_document, render_html, validate_document


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class EditorialPreviewTests(unittest.TestCase):
    def sample(self, kind="figure-data", **fields):
        sample = load_document(EXAMPLES / f"{kind}.json")
        return {**sample, "variant": "editorial", **fields}

    def test_only_explicit_series_is_blue_and_data_is_not_modified(self):
        sample = self.sample(focus_index=1)
        original = deepcopy(sample)
        context = build_context(sample, EXAMPLES / "figure-data.json")
        self.assertEqual(context["chart"]["series"][1]["color"], "#0064FF")
        self.assertEqual(context["chart"]["series"][0]["color"], "#8B95A1")
        self.assertEqual(sample, original)
        for actual, expected in zip(context["chart"]["series"], original["chart"]["series"]):
            self.assertEqual(actual["values"], expected["values"])

    def test_omitted_focus_does_not_select_the_first_item(self):
        context = build_context(self.sample(), EXAMPLES / "figure-data.json")
        self.assertTrue(all(series["color"] == "#8B95A1" for series in context["chart"]["series"]))
        html = render_html(self.sample("figure-metrics"), EXAMPLES / "figure-metrics.json")
        self.assertNotIn('class="metric-card is-focus"', html)

    def test_selected_metric_is_marked_once_without_extra_copy(self):
        html = render_html(self.sample("figure-metrics", focus_index=2), EXAMPLES / "figure-metrics.json")
        self.assertEqual(html.count('class="metric-card is-focus"'), 1)
        self.assertEqual(html.count('class="editorial-rule"'), 1)
        self.assertEqual(html.count("unit-tx-logo.png"), 1)
        self.assertEqual(html.count('class="fixed-date num"'), 1)
        self.assertEqual(html.count("46.3"), 1)
        self.assertNotIn("KEY READ", html)

    def test_invalid_focus_indices_fail_instead_of_silently_selecting(self):
        for kind, invalid in (("figure-data", 2), ("figure-metrics", 4), ("figure-data", -1), ("figure-metrics", True), ("figure-data", "0")):
            with self.subTest(kind=kind, invalid=invalid), self.assertRaisesRegex(ValueError, "focus_index"):
                validate_document(self.sample(kind, focus_index=invalid))

    def test_variant_is_limited_to_the_two_approved_previews(self):
        for kind in ("cover-editorial", "cover-object", "figure-ranking", "figure-composition", "figure-comparison"):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "variant"):
                validate_document(self.sample(kind))
        with self.assertRaisesRegex(ValueError, "variant"):
            validate_document(self.sample(variant="unknown"))
        sample = self.sample()
        sample["chart"]["type"] = "bar"
        sample["chart"]["labels"] = sample["chart"]["labels"][:3]
        for series in sample["chart"]["series"]:
            series["values"] = series["values"][:3]
        with self.assertRaisesRegex(ValueError, "line"):
            validate_document(sample)

    def test_focus_requires_the_opt_in_variant(self):
        sample = self.sample(focus_index=0)
        sample.pop("variant")
        with self.assertRaisesRegex(ValueError, "variant"):
            validate_document(sample)

    def test_standard_example_does_not_render_the_new_rule(self):
        for kind in ("figure-data", "figure-metrics"):
            sample = load_document(EXAMPLES / f"{kind}.json")
            html = render_html(sample, EXAMPLES / f"{kind}.json")
            self.assertNotIn("editorial-rule", html)
            self.assertNotIn("editorial-figure", html)


if __name__ == "__main__":
    unittest.main()
