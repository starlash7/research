# UNIT TX Cover Visual Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable top-left article category to both cover templates and replace the flat dark cover with a restrained charcoal, smoke, and deep-blue gradient.

**Architecture:** Keep the existing JSON to Jinja to Playwright pipeline. Extend the existing cover document contract with one required `category` string, render it through one shared CSS class, and create the dark atmosphere entirely with local CSS pseudo-elements. No new renderer abstraction, dependency, remote asset, graph, or generated symbol is added.

**Tech Stack:** Python 3.9, Jinja2, HTML, native CSS gradients, Playwright, unittest

## Global Constraints

- Cover outputs remain exactly 1440×756px.
- Both cover templates require one non-empty `category` with display width at most 24.
- Category, title, subtitle, date, and UNIT TX wordmark are the only default visible cover text.
- Date remains bottom-left and exact black; the dark cover keeps a small white backing.
- Official UNIT TX logo remains bottom-right and is not redrawn.
- Typography remains SUIT Variable with only weights 500, 600, and 800.
- Dark styling uses low-saturation charcoal, smoke grey, and deep UNIT TX blue with no graph, grid, generated symbol, or remote asset.
- Existing figure templates and their JSON contracts do not change.

---

### Task 1: Cover category data contract

**Files:**
- Modify: `tests/test_render.py`
- Modify: `render.py`
- Modify: `templates/cover-editorial.html`
- Modify: `templates/cover-object.html`
- Modify: `examples/cover-editorial.json`
- Modify: `examples/cover-object.json`

**Interfaces:**
- Consumes: existing `validate_document(document)`, `render_html(document, source_path)`, and Jinja cover contexts.
- Produces: required cover field `category: str`, rendered as one `.cover-category` element.

- [ ] **Step 1: Write failing category tests**

Add tests that remove `category` from both cover helper documents and expect `ValueError`, reject `category="A" * 25`, and assert both rendered covers contain exactly one `.cover-category` with escaped user text. Update test helper documents to include `"category": "ONCHAIN RESEARCH"`.

```python
def test_both_covers_require_category(self):
    for document in (cover_document(), object_cover_document()):
        document.pop("category")
        with self.subTest(template=document["template"]), self.assertRaisesRegex(ValueError, "category"):
            validate_document(document)

def test_cover_category_has_a_fixed_display_width_limit(self):
    with self.assertRaisesRegex(ValueError, "category"):
        validate_document(cover_document(category="A" * 25))

def test_both_covers_render_one_category(self):
    for document in (cover_document(), object_cover_document()):
        html = render_html(document, Path("examples/cover.json"))
        self.assertEqual(html.count('class="cover-category"'), 1)
        self.assertIn("ONCHAIN RESEARCH", html)
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_render.ValidationTests.test_both_covers_require_category tests.test_render.ValidationTests.test_cover_category_has_a_fixed_display_width_limit tests.test_render.HtmlTests.test_both_covers_render_one_category -v
```

Expected: FAIL because `category` is not required, limited, or rendered.

- [ ] **Step 3: Implement the minimum category contract**

Add `category` to both cover `required` and `TEXT_FIELDS` tuples. In `validate_document`, reject cover categories whose `_display_width` exceeds 24.

```python
if template_name.startswith("cover-") and _display_width(text["category"]) > 24:
    raise ValueError("cover category는 영문 24자 폭 이하여야 합니다")
```

Render the same element at the start of each cover canvas:

```html
<p class="cover-category">{{ category }}</p>
```

Add `"category": "ONCHAIN RESEARCH"` and `"category": "STABLECOINS"` to the two example JSON files.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the same focused command. Expected: all three tests PASS.

- [ ] **Step 5: Commit the category contract**

```bash
git add tests/test_render.py render.py templates/cover-editorial.html templates/cover-object.html examples/cover-editorial.json examples/cover-object.json
git commit -m "Add cover article categories"
```

### Task 2: Restore premium dark depth and style categories

**Files:**
- Modify: `tests/test_render.py`
- Modify: `assets/styles.css`

**Interfaces:**
- Consumes: `.cover-category`, `.cover-editorial-canvas`, `.cover-object-canvas`, and the existing `.object-footer` contract.
- Produces: stable top-left category styling and a layered dark background with no additional DOM.

- [ ] **Step 1: Write failing visual-contract tests**

Replace the flat-dark assertion with tests requiring a non-black dark base, at least three gradient layers, a dark vignette pseudo-element, category colors on both cover surfaces, and no return of forbidden signal-map markup.

```python
def test_dark_cover_uses_layered_charcoal_gradient(self):
    styles = Path("assets/styles.css").read_text(encoding="utf-8")
    self.assertIn("--dark-surface: #111318;", styles)
    self.assertRegex(styles, r"\.cover-object-canvas::before\s*\{[^}]*radial-gradient[^}]*radial-gradient[^}]*linear-gradient")
    self.assertRegex(styles, r"\.cover-object-canvas::after\s*\{[^}]*radial-gradient")

def test_cover_categories_have_surface_specific_colors(self):
    styles = Path("assets/styles.css").read_text(encoding="utf-8")
    self.assertRegex(styles, r"\.cover-category\s*\{[^}]*color: var\(--accent\);")
    self.assertRegex(styles, r"\.cover-object-canvas \.cover-category\s*\{[^}]*color: #e3e6ed;")
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_render.HtmlTests.test_dark_cover_uses_layered_charcoal_gradient tests.test_render.HtmlTests.test_cover_categories_have_surface_specific_colors -v
```

Expected: FAIL because the current background is flat `#0A0A0A` and no category styles exist.

- [ ] **Step 3: Implement native CSS styling**

Set `--dark-surface: #111318`. Position `.cover-category` at `top: 58px; left: 74px`, use SUIT weight 600, 19px type, and UNIT TX Blue on light. Use muted off-white on dark.

Build the dark background with two radial fields and one linear base in `::before`, then apply a restrained vignette in `::after`. Use the blue field at low opacity so the result remains charcoal-led rather than a blue canvas.

```css
.cover-object-canvas::before {
  content: "";
  position: absolute;
  z-index: -2;
  inset: 0;
  background:
    radial-gradient(ellipse 62% 92% at 88% 10%, rgba(171, 179, 194, 0.30), transparent 66%),
    radial-gradient(ellipse 70% 82% at 78% 112%, rgba(0, 100, 255, 0.12), transparent 68%),
    linear-gradient(118deg, #0e1014 0%, #171a21 52%, #303541 100%);
}

.cover-object-canvas::after {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  background:
    radial-gradient(ellipse at center, transparent 34%, rgba(4, 6, 10, 0.36) 100%),
    linear-gradient(90deg, rgba(5, 7, 10, 0.36), transparent 56%);
}
```

- [ ] **Step 4: Run focused and full tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_render.HtmlTests.test_dark_cover_uses_layered_charcoal_gradient tests.test_render.HtmlTests.test_cover_categories_have_surface_specific_colors -v
.venv/bin/python -m unittest discover -s tests -v
```

Expected: focused tests and full suite PASS.

- [ ] **Step 5: Commit visual styling**

```bash
git add tests/test_render.py assets/styles.css
git commit -m "Restore layered dark cover depth"
```

### Task 3: Align rules, examples, and rendered proof

**Files:**
- Modify: `AGENTS.md`
- Modify: `goal.md`
- Modify: `README.md`
- Modify: `docs/IMAGE_SYSTEM.md`
- Test: `tests/test_render.py`

**Interfaces:**
- Consumes: the implemented `category` field and dark gradient contract.
- Produces: clone-ready authoring documentation and verified PNG examples.

- [ ] **Step 1: Write a failing documentation test**

Require the detailed guide and goal to state that both covers use `category` and the dark cover uses a layered charcoal, smoke, and deep-blue gradient.

```python
def test_docs_define_category_and_dark_gradient(self):
    docs = Path("docs/IMAGE_SYSTEM.md").read_text(encoding="utf-8")
    goal = Path("goal.md").read_text(encoding="utf-8")
    for phrase in ("category", "차콜", "스모크", "딥블루"):
        self.assertIn(phrase, docs)
        self.assertIn(phrase, goal)
```

- [ ] **Step 2: Run the documentation test and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_render.DocumentationTests.test_docs_define_category_and_dark_gradient -v
```

Expected: FAIL because current documentation still specifies a neutral-black typography cover with no category.

- [ ] **Step 3: Update authoring rules and examples**

Document `category` as required for both covers with a 24-unit limit. Replace references to the flat neutral-black cover with the selected charcoal, smoke, and deep-blue layered gradient. Keep the no-filler and optional-local-image rules intact.

- [ ] **Step 4: Run full automated and render verification**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python render.py --all
sips -g pixelWidth -g pixelHeight out/*.png
git diff --check
```

Expected: all tests PASS; covers are 1440×756, framework is 1440×810, and data figure is 1440×1200.

- [ ] **Step 5: Inspect both covers at original size**

Open `out/onchain-adoption-cover.png` and `out/stablecoin-payment-cover.png`. Confirm category placement, intentional title wrapping, footer positions, logo transparency, dark gradient depth, and absence of clipping or filler graphics.

- [ ] **Step 6: Commit documentation and tests**

```bash
git add AGENTS.md goal.md README.md docs/IMAGE_SYSTEM.md tests/test_render.py
git commit -m "Document revised cover system"
```
