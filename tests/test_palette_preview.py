from copy import deepcopy
from pathlib import Path
import unittest

from render import PALETTE_PREVIEWS, build_context, load_document, render_html, select_sources, validate_document


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
EXPECTED = {
    "vermillion": ("#E4492D", "#E4492D", "#B93822"),
    "lime": ("#C7F542", "#526B16", "#526B16"),
    "violet": ("#7546E8", "#7546E8", "#7546E8"),
    "teal": ("#008F86", "#008F86", "#006E67"),
    "magenta": ("#D62F8A", "#D62F8A", "#D62F8A"),
    "amber": ("#F2B233", "#A86B08", "#8C5800"),
    "burgundy": ("#8C2545", "#8C2545", "#8C2545"),
    "forest": ("#1D684F", "#1D684F", "#1D684F"),
    "coral": ("#F47568", "#CC5045", "#B64037"),
    "copper": ("#B76E3C", "#B76E3C", "#925327"),
    "indigo": ("#4338CA", "#4338CA", "#4338CA"),
    "cyan": ("#00A6C8", "#00809B", "#006E85"),
    "red": ("#D7263D", "#D7263D", "#D7263D"),
    "orange": ("#F0781E", "#C85C10", "#AF4B08"),
    "yellow": ("#EBCB20", "#8D7900", "#796700"),
    "olive": ("#718044", "#718044", "#5B6833"),
    "mint": ("#21B889", "#008763", "#007354"),
    "blue": ("#0064FF", "#0064FF", "#0064FF"),
    "navy": ("#183153", "#183153", "#183153"),
    "slate": ("#64748B", "#64748B", "#64748B"),
}


class PalettePreviewTests(unittest.TestCase):
    def sample(self, palette="vermillion"):
        document = load_document(EXAMPLES / "previews/figure-data-editorial.json")
        return {**document, "palette_preview": palette}

    def test_palette_controls_selected_series_without_changing_data(self):
        for name, (accent, data, text) in EXPECTED.items():
            with self.subTest(name=name):
                self.assertIn(name, PALETTE_PREVIEWS)
                document = self.sample(name)
                document["focus_index"] = 1
                original = deepcopy(document)
                context = build_context(document, EXAMPLES / "figure-data.json")
                self.assertEqual(context["accent"], accent)
                self.assertEqual(context["chart"]["series"][1]["color"], data)
                self.assertEqual(context["chart"]["series"][0]["color"], "#8B95A1")
                self.assertEqual(document, original)
                html = render_html(document, EXAMPLES / "figure-data.json")
                self.assertIn('class="palette-preview"', html)
                self.assertIn(f"--preview-data: {data}", html)
                self.assertIn(f"--preview-text: {text}", html)
                self.assertEqual(html.count("unit-tx-logo.png"), 1)
                self.assertEqual(html.count('class="fixed-date num"'), 1)

    def test_missing_focus_does_not_automatically_highlight(self):
        document = self.sample("lime")
        document.pop("focus_index")
        context = build_context(document, EXAMPLES / "figure-data.json")
        self.assertTrue(all(series["color"] == "#8B95A1" for series in context["chart"]["series"]))

    def test_rejects_unknown_names_and_conflicting_accent(self):
        for value in ("unknown", "", None, [], {}, True, 1):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "palette_preview"):
                validate_document(self.sample(value))
        document = self.sample()
        document["accent"] = "#0064FF"
        with self.assertRaisesRegex(ValueError, "accent"):
            validate_document(document)

    def test_rejects_unapproved_template_combinations(self):
        for kind in ("cover-object", "figure-framework", "figure-ranking", "figure-composition", "figure-metrics", "figure-comparison", "figure-data"):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "palette_preview"):
                document = load_document(EXAMPLES / f"{kind}.json")
                validate_document({**document, "palette_preview": "lime"})

    def test_existing_inputs_do_not_get_palette_styles(self):
        paths = list(EXAMPLES.glob("*.json")) + list((EXAMPLES / "previews").glob("*.json"))
        for path in paths:
            with self.subTest(path=path.name):
                html = render_html(load_document(path), path)
                self.assertNotIn('class="palette-preview"', html)
                self.assertNotIn("--preview-data", html)

    def test_each_palette_has_two_examples_with_identical_copy_and_data(self):
        paths = sorted((EXAMPLES / "previews/palettes").glob("*.json"))
        self.assertEqual(len(paths), len(EXPECTED) * 2)
        self.assertEqual({path.name for path in paths}, {
            f"{name}-{kind}.json" for name in EXPECTED for kind in ("cover", "trend")
        })
        baseline = {}
        for path in paths:
            document = load_document(path)
            validate_document(document)
            html = render_html(document, path)
            name = document.pop("palette_preview")
            self.assertIn(name, EXPECTED)
            self.assertNotIn(name, document["title"])
            self.assertNotIn("—", html)
            self.assertNotIn("–", html)
            document.pop("slug")
            kind = document["template"]
            if kind in baseline:
                self.assertEqual(document, baseline[kind])
            baseline[kind] = document
        self.assertEqual(set(baseline), {"cover-editorial", "figure-data"})
        self.assertEqual(baseline["figure-data"]["chart"], load_document(EXAMPLES / "figure-data.json")["chart"])
        self.assertTrue(all(path.parent == EXAMPLES for path in select_sources(None, True, EXAMPLES)))

    def test_data_and_small_text_colors_have_white_background_contrast(self):
        self.assertEqual(set(PALETTE_PREVIEWS), set(EXPECTED))
        for name, palette in PALETTE_PREVIEWS.items():
            for role, minimum in (("data", 3), ("text", 4.5)):
                with self.subTest(name=name, role=role):
                    channels = [int(palette[role][i:i + 2], 16) / 255 for i in (1, 3, 5)]
                    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
                    luminance = sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))
                    self.assertGreaterEqual(1.05 / (luminance + .05), minimum)

    def test_invalid_palette_error_lists_all_candidates(self):
        with self.assertRaises(ValueError) as error:
            validate_document(self.sample("unknown"))
        for name in EXPECTED:
            self.assertIn(name, str(error.exception))


if __name__ == "__main__":
    unittest.main()
