# UNIT TX Research Image Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic HTML-to-PNG renderer with four UNIT TX research templates, structured example inputs, and authoritative image rules.

**Architecture:** A single Python entry point validates JSON, enriches chart data, renders allowlisted Jinja templates, and captures fixed viewports with Playwright. Shared CSS and the unmodified UNIT TX mark keep all formats consistent; examples run fully offline and generated artifacts stay outside version control.

**Tech Stack:** Python 3.9+, Jinja2 3.1.6, Playwright 1.60/1.61, HTML/CSS/SVG, `unittest`

## Global Constraints

- Canonical outputs are exactly 1440×756 (`cover`), 1440×810 (`wide`), and 1440×1200 (`data`).
- The supplied 738×694 UNIT TX symbol must remain unaltered.
- Bright templates use a white `#FFFFFF` field with UNIT TX Blue `#0064FF` (Toss Blue reference) as the default signal color.
- The dark cover uses a deep navy blueprint grid and connected signal map, not a decorative 3D object.
- Standard example rendering must not require a network request.
- Quantitative figures require a source and as-of date.
- Cover titles may occupy at most two intentional lines.
- No essential content may enter the outer 6% safe margin.
- Color may not be the only carrier of meaning.
- Generated HTML, PNG, and manifest files live in `out/` and are ignored.
- Use only Jinja2 and Playwright as runtime dependencies; use `unittest` for tests.

---

### Task 1: Authoring rules and validation core

**Files:**
- Create: `AGENTS.md`
- Create: `docs/IMAGE_SYSTEM.md`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `render.py`
- Create: `tests/test_render.py`

**Interfaces:**
- Consumes: UTF-8 JSON objects with `template`, `slug`, and template-specific fields.
- Produces: `TemplateSpec`, `load_document(path: Path) -> dict[str, Any]`, `validate_document(document: dict[str, Any]) -> TemplateSpec`, and `safe_slug(value: str) -> str`.

- [ ] **Step 1: Write failing validation tests**

```python
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
        with self.assertRaisesRegex(ValueError, "slug"):
            safe_slug("../escape")

    def test_quantitative_figure_requires_source_and_date(self):
        document = {"template": "figure-data", "slug": "sample", "title": "제목"}
        with self.assertRaisesRegex(ValueError, "source"):
            validate_document(document)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python3 -m unittest tests.test_render.ValidationTests -v`

Expected: import failure because `render.py` does not yet expose the required interfaces.

- [ ] **Step 3: Implement the allowlist and validation boundary**

```python
@dataclass(frozen=True)
class TemplateSpec:
    filename: str
    size: tuple[int, int]
    required: tuple[str, ...]


TEMPLATES = {
    "cover-editorial": TemplateSpec("cover-editorial.html", (1440, 756), ("eyebrow", "title", "subtitle", "date")),
    "cover-object": TemplateSpec("cover-object.html", (1440, 756), ("eyebrow", "title", "subtitle", "date")),
    "figure-framework": TemplateSpec("figure-framework.html", (1440, 810), ("eyebrow", "title", "nodes", "source", "date")),
    "figure-data": TemplateSpec("figure-data.html", (1440, 1200), ("title", "source", "date", "chart", "takeaways")),
}


def safe_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("slug는 영문 소문자, 숫자, 하이픈만 사용할 수 있습니다")
    return value
```

`validate_document` must reject absent required keys, titles containing more than one newline, framework node counts outside 3–5, chart series with unequal label/value counts, chart types outside `line` and `bar`, and accent values outside six-digit hex colors.

- [ ] **Step 4: Write the concise agent rules and complete human guide**

`AGENTS.md` must identify `docs/IMAGE_SYSTEM.md` as authoritative and include the canonical dimensions, source/date requirements, title limits, local-asset rule, safe margin, accessibility rule, render commands, and visual QA checklist. `docs/IMAGE_SYSTEM.md` must document JSON fields and one complete invocation for each template family.

- [ ] **Step 5: Run tests and documentation checks**

Run: `python3 -m unittest tests.test_render.ValidationTests -v`

Expected: all validation tests pass.

Run: `grep -R -nE 'T[B]D|T[O]DO|PLACE[H]OLDER' AGENTS.md docs/IMAGE_SYSTEM.md render.py tests || true`

Expected: no output.

- [ ] **Step 6: Commit the validation boundary and rules**

```bash
git add AGENTS.md docs/IMAGE_SYSTEM.md requirements.txt .gitignore render.py tests/test_render.py
git commit -m "Add UNIT TX image authoring rules"
```

### Task 2: Brand assets and deterministic HTML templates

**Files:**
- Create: `assets/unit-tx-logo.png`
- Create: `assets/PretendardVariable.woff2`
- Create: `assets/styles.css`
- Create: `templates/base.html`
- Create: `templates/cover-editorial.html`
- Create: `templates/cover-object.html`
- Create: `templates/figure-data.html`
- Create: `templates/figure-framework.html`
- Modify: `render.py`
- Modify: `tests/test_render.py`

**Interfaces:**
- Consumes: validated documents and `TemplateSpec.filename`.
- Produces: `build_context(document: dict[str, Any], source_path: Path) -> dict[str, Any]` and `render_html(document: dict[str, Any], source_path: Path) -> str`.

- [ ] **Step 1: Copy canonical assets without transforming them**

Copy the exact supplied logo to `assets/unit-tx-logo.png`. Copy the locally available Pretendard Variable WOFF2 from the inspected `kimch-index` workspace to `assets/PretendardVariable.woff2`. Record Pretendard's SIL Open Font License attribution in `docs/IMAGE_SYSTEM.md`.

- [ ] **Step 2: Write failing HTML and chart-context tests**

```python
def test_html_autoescapes_user_copy(self):
    document = valid_cover_document(title="UNIT <script>alert(1)</script>")
    html = render_html(document, Path("examples/cover-editorial.json"))
    self.assertNotIn("<script>", html)
    self.assertIn("&lt;script&gt;", html)

def test_line_chart_context_contains_svg_points_and_ticks(self):
    context = build_context(valid_data_document(), Path("examples/figure-data.json"))
    self.assertEqual(len(context["chart"]["series"][0]["points"]), 6)
    self.assertEqual(len(context["chart"]["ticks"]), 5)

def test_dark_cover_uses_exact_logo_asset_with_dark_treatment(self):
    html = render_html(valid_object_cover_document(), Path("examples/cover-object.json"))
    self.assertIn("unit-tx-logo.png", html)
    self.assertIn("logo-on-dark", html)
```

- [ ] **Step 3: Run focused tests and verify RED**

Run: `python3 -m unittest tests.test_render.HtmlTests -v`

Expected: failures because context building and templates are absent.

- [ ] **Step 4: Implement shared styles and base template**

`assets/styles.css` must define the palette from the spec, local `@font-face`, exact canvas sizing through CSS variables, 6% safe-area helpers, black-on-light and white-on-dark logo blend treatments, tabular numerals, and reduced-motion-safe static rendering. `templates/base.html` must load only local assets and expose `style`, `content`, and `footer` blocks.

- [ ] **Step 5: Implement four focused child templates**

The templates must meet these concrete content contracts:

- `cover-editorial`: category pill, maximum two-line title, subtitle, date, author, topic index, exact logo, and CSS topic glyph.
- `cover-object`: eyebrow, title, subtitle, date, exact logo, optional resolved local `hero_uri`, and complete CSS signal-map fallback.
- `figure-data`: claim, source, date, legend, SVG line or bar chart, y-axis tick labels, x labels, units, and one to three takeaway cards.
- `figure-framework`: eyebrow, title, source, date, three to five numbered nodes, visible directional connectors, and a summary statement.

- [ ] **Step 6: Implement chart enrichment and local hero resolution**

`build_context` must calculate evenly spaced x positions, normalized y positions, five y-axis ticks, SVG polyline strings, line-point labels, and bar rectangles. Optional `hero_image` paths resolve relative to the JSON file and must remain inside the JSON file's directory tree; missing or escaping paths raise `ValueError`.

- [ ] **Step 7: Run focused and full unit tests**

Run: `python3 -m unittest tests.test_render.HtmlTests -v`

Expected: all HTML tests pass.

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 8: Commit the template layer**

```bash
git add assets templates render.py tests/test_render.py docs/IMAGE_SYSTEM.md
git commit -m "Build UNIT TX research image templates"
```

### Task 3: Playwright PNG renderer and manifest

**Files:**
- Modify: `render.py`
- Modify: `tests/test_render.py`
- Create: `out/.gitkeep`

**Interfaces:**
- Consumes: `render_html`, `TemplateSpec.size`, source JSON path, output directory, and scale.
- Produces: `render_png(source_path: Path, output_dir: Path, scale: int = 1) -> Path`, `update_manifest(...) -> Path`, and CLI commands `python3 render.py <json>` and `python3 render.py --all`.

- [ ] **Step 1: Write failing output and manifest tests**

```python
def test_output_path_is_slug_png(self):
    self.assertEqual(output_path(Path("out"), "sample"), Path("out/sample.png"))

def test_manifest_update_preserves_unrelated_entries(self):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        (output / "manifest.json").write_text('{"cards":{"old":{"template":"cover-editorial"}}}')
        update_manifest(output, "new", "figure-data", (1440, 1200), 1)
        cards = json.loads((output / "manifest.json").read_text())["cards"]
        self.assertEqual(set(cards), {"old", "new"})
```

- [ ] **Step 2: Run output tests and verify RED**

Run: `python3 -m unittest tests.test_render.OutputTests -v`

Expected: failures because output and manifest helpers are absent.

- [ ] **Step 3: Implement atomic HTML, screenshot, and manifest writes**

The renderer must create only `<slug>.html`, `<slug>.png`, and `manifest.json`. It must launch Chromium once per CLI invocation, set the viewport to the exact template size, apply `device_scale_factor=scale`, wait for `document.fonts.ready` and all images, capture without full-page expansion, verify the PNG dimensions, and atomically replace the manifest through a sibling temporary file.

- [ ] **Step 4: Implement the CLI**

```text
python3 render.py examples/cover-editorial.json
python3 render.py --all
python3 render.py --all --scale 2 --output-dir out-2x
```

The parser must reject using a positional JSON path with `--all`, reject scale values outside 1 and 2, process `examples/*.json` in filename order, reuse one browser, print one `[ok]` line per card, and return exit code 1 with `[error]` on validation or browser failures.

- [ ] **Step 5: Run unit tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass without starting Chromium; browser calls are mocked in unit tests.

- [ ] **Step 6: Commit the renderer**

```bash
git add render.py tests/test_render.py out/.gitkeep
git commit -m "Add deterministic PNG rendering"
```

### Task 4: Example content, complete rendering, and visual QA

**Files:**
- Create: `examples/cover-editorial.json`
- Create: `examples/cover-object.json`
- Create: `examples/figure-data.json`
- Create: `examples/figure-framework.json`
- Modify: `README.md`
- Modify: `docs/IMAGE_SYSTEM.md`
- Modify: `tests/test_render.py`

**Interfaces:**
- Consumes: the public CLI from Task 3.
- Produces: four reproducible PNG examples and a complete quick-start guide.

- [ ] **Step 1: Write the example-set regression test**

```python
def test_example_set_covers_all_templates(self):
    documents = [load_document(path) for path in sorted(EXAMPLES.glob("*.json"))]
    self.assertEqual({doc["template"] for doc in documents}, set(TEMPLATES))
    for document in documents:
        validate_document(document)
```

- [ ] **Step 2: Run the regression test and verify RED**

Run: `python3 -m unittest tests.test_render.ExampleTests -v`

Expected: failure because the four JSON examples do not exist.

- [ ] **Step 3: Add realistic UNIT TX example inputs**

Use Korean mock research copy covering stablecoin payments, institutional onchain adoption, token survival data, and an onchain transaction flow. Every value must be clearly example data, every quantitative figure must include `source: "Example data · replace before publishing"`, and dates must use `2026.09.01`.

- [ ] **Step 4: Complete README and author guide**

README must include setup, `playwright install chromium`, one-card and all-card commands, output sizes, directory map, and links to `AGENTS.md` and `docs/IMAGE_SYSTEM.md`. The author guide must include copy-length limits, a complete JSON example for each schema, local hero-image instructions, and a pre-publish checklist.

- [ ] **Step 5: Install dependencies in a repository-local virtual environment**

Run: `python3 -m venv .venv`

Run: `.venv/bin/pip install -r requirements.txt`

Run: `.venv/bin/playwright install chromium`

Expected: Jinja2 and the Python-version-compatible Playwright release install successfully, followed by Chromium.

- [ ] **Step 6: Run the complete verification suite**

Run: `.venv/bin/python -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `.venv/bin/python render.py --all`

Expected: four `[ok]` lines and `[done] 4 images`.

Run: `sips -g pixelWidth -g pixelHeight out/*.png`

Expected: both covers are 1440×756, the framework is 1440×810, and the data figure is 1440×1200.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 7: Inspect all four PNG files visually**

Open each PNG at original detail and verify no clipping, intentional Korean line wrapping, visible source/date metadata, correct logo treatment without a rectangle, clear chart labels and units, directional framework connectors, and coherent UNIT TX family resemblance.

- [ ] **Step 8: Commit examples and documentation**

```bash
git add examples README.md docs/IMAGE_SYSTEM.md tests/test_render.py
git commit -m "Add UNIT TX research image examples"
```

### Task 5: Final review and handoff

**Files:**
- Modify only files required by concrete review findings.

**Interfaces:**
- Consumes: complete branch diff against `origin/main`.
- Produces: reviewed, reproducible implementation with no unresolved findings.

- [ ] **Step 1: Review the complete diff for requirement coverage**

Run: `git diff --stat origin/main...HEAD`

Run: `git diff --check origin/main...HEAD`

Expected: only the design, rules, renderer, templates, assets, examples, tests, and documentation are changed; whitespace check is clean.

- [ ] **Step 2: Run final tests and rendering from a clean output directory**

Move existing generated files to a temporary backup, retain `out/.gitkeep`, then rerun the full tests and `render.py --all`. Confirm manifest entries match the four PNG files and every recorded dimension.

- [ ] **Step 3: Resolve every correctness or visual review finding**

For each concrete finding, add or update the smallest relevant regression test, apply the focused fix, rerun that test, and rerender only the affected example before the final full run.

- [ ] **Step 4: Commit review fixes if any**

```bash
git add <only-files-changed-for-reviewed-fixes>
git commit -m "Polish UNIT TX template rendering"
```

- [ ] **Step 5: Record final evidence**

Report the exact test count, four output dimensions, commit list, and clickable paths to `AGENTS.md`, `docs/IMAGE_SYSTEM.md`, and the four PNG examples.
