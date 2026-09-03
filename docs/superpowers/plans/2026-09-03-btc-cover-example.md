# BTC Cover Example Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render light and dark 1440x756 UNIT TX cover examples with the original orange Bitcoin logo, while keeping the UNIT TX footer lockup unchanged.

**Architecture:** Reuse the renderer's existing validated `hero_uri` context for both Jinja cover templates. Add one local, provenance-recorded Bitcoin PNG that both example JSON files reference, then use one shared CSS image class with theme-specific positioning and no media card.

**Tech Stack:** Python 3, unittest, Jinja2, HTML, CSS, Playwright, local PNG assets

## Global Constraints

- Main covers remain 1440x756px.
- Core text, the article visual, the date, and the UNIT TX lockup remain inside the 6% safe area.
- The date stays at the bottom left in `#000000`; the dark cover keeps its white date backing.
- The official UNIT TX logo stays at the bottom right exactly once and is not modified.
- Both covers show `category` exactly once at the top left.
- The font remains local SUIT Variable with weights 500, 600, and 800 only.
- The light cover remains white with UNIT TX Blue `#0064FF` as its template accent.
- The dark cover retains its charcoal, smoke, and deep-blue layered gradient.
- The Bitcoin logo keeps its source color, proportions, orientation, and transparency with no tint, crop, shadow, card, caption, or generated decoration.
- Rendering does not request remote URLs.
- Visible cover copy contains no em dash or en dash.

---

### Task 1: Shared Unframed Cover Image

**Files:**
- Modify: `tests/test_render.py`
- Modify: `templates/cover-editorial.html`
- Modify: `templates/cover-object.html`
- Modify: `assets/styles.css`

**Interfaces:**
- Consumes: `build_context(document: dict[str, Any], source_path: Path) -> dict[str, Any]`, which already exposes validated `hero_uri: str | None`.
- Produces: optional `<img class="cover-hero-image">` markup in both covers, with `editorial-visual has-hero` on the light image wrapper and `object-stage` on the dark image wrapper.

- [ ] **Step 1: Write failing template tests**

Add tests that create a local placeholder `art/bitcoin-logo.png`, render both cover documents with `hero_image`, and assert that each HTML result contains one `cover-hero-image`, the local file URI, and no `atlas-media-frame`. Add a light fallback assertion proving that `editorial-visual` remains and no hero image is emitted when `hero_image` is absent. Add a stylesheet assertion for `object-fit: contain` and absence of `.atlas-media-frame`.

```python
def test_both_covers_render_a_local_hero_as_an_unframed_object(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        art = root / "art"
        art.mkdir()
        hero = art / "bitcoin-logo.png"
        hero.write_bytes(b"local png placeholder")

        for document in (
            cover_document(hero_image="art/bitcoin-logo.png"),
            object_cover_document(hero_image="art/bitcoin-logo.png"),
        ):
            with self.subTest(template=document["template"]):
                html = render_html(document, root / "cover.json")
                self.assertEqual(html.count('class="cover-hero-image"'), 1)
                self.assertIn(hero.resolve().as_uri(), html)
                self.assertNotIn("atlas-media-frame", html)

def test_light_cover_keeps_its_blue_fallback_without_a_hero(self):
    html = render_html(cover_document(), Path("examples/cover-editorial.json"))
    self.assertIn('class="editorial-visual"', html)
    self.assertNotIn("cover-hero-image", html)

def test_cover_hero_css_contains_without_a_media_card(self):
    styles = Path("assets/styles.css").read_text(encoding="utf-8")
    self.assertRegex(
        styles,
        r"\.cover-hero-image\s*\{[^}]*object-fit: contain;",
    )
    self.assertNotIn(".atlas-media-frame", styles)
```

- [ ] **Step 2: Run the focused tests and confirm the expected failure**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_render.HtmlTests.test_both_covers_render_a_local_hero_as_an_unframed_object \
  tests.test_render.HtmlTests.test_light_cover_keeps_its_blue_fallback_without_a_hero \
  tests.test_render.HtmlTests.test_cover_hero_css_contains_without_a_media_card -v
```

Expected: the shared-hero and CSS tests fail because the light template has no image markup, the dark template still has `atlas-media-frame`, and the current image CSS uses `object-fit: cover`.

- [ ] **Step 3: Implement the minimum shared image markup**

Change the light visual to conditionally contain the supplied image while keeping the no-image fallback:

```html
<div class="editorial-visual{% if hero_uri %} has-hero{% endif %}" aria-hidden="true">
  {% if hero_uri %}<img class="cover-hero-image" src="{{ hero_uri }}" alt="">{% endif %}
</div>
```

Change the dark visual to remove the nested frame:

```html
{% if hero_uri %}
  <div class="object-stage" aria-hidden="true">
    <img class="cover-hero-image" src="{{ hero_uri }}" alt="">
  </div>
{% endif %}
```

Keep the existing `.editorial-visual` fallback rules, add `.editorial-visual.has-hero` rules that remove its background and pseudo-elements, replace `.hero-image` with `.cover-hero-image`, set `object-fit: contain`, and delete `.atlas-media-frame`. Position the dark object within the safe area with a transparent wrapper and no border or background.

- [ ] **Step 4: Run the focused tests and confirm they pass**

Run the Step 2 command.

Expected: 3 tests pass.

- [ ] **Step 5: Run the full suite**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Expected: all tests pass with 0 failures and 0 errors.

---

### Task 2: Original Bitcoin Asset and Example Inputs

**Files:**
- Create: `examples/art/bitcoin-logo.png`
- Create: `examples/art/README.md`
- Modify: `examples/cover-editorial.json`
- Modify: `examples/cover-object.json`
- Modify: `tests/test_render.py`

**Interfaces:**
- Consumes: the shared `hero_image` input contract and `cover-hero-image` markup from Task 1.
- Produces: two runnable Bitcoin cover example JSON files that both reference `art/bitcoin-logo.png`.

- [ ] **Step 1: Write failing asset and example tests**

Add an example test that checks the downloaded asset's exact SHA-256 hash and 1000x1000 dimensions, confirms both cover examples reference the same local file, and confirms the provenance note includes the source and raw download URLs.

```python
def test_bitcoin_cover_examples_share_the_original_local_logo(self):
    examples = Path(__file__).parents[1] / "examples"
    asset = examples / "art" / "bitcoin-logo.png"
    provenance = (examples / "art" / "README.md").read_text(encoding="utf-8")
    covers = [
        load_document(examples / "cover-editorial.json"),
        load_document(examples / "cover-object.json"),
    ]

    self.assertEqual(
        hashlib.sha256(asset.read_bytes()).hexdigest(),
        "b0231779b54f52e4352fa4300cb5353351bee8261f5d84b6e6ad8f6a2d24a1a4",
    )
    self.assertEqual(png_size(asset), (1000, 1000))
    self.assertTrue(all(cover["hero_image"] == "art/bitcoin-logo.png" for cover in covers))
    self.assertIn("https://github.com/bitpay/bitcoin-brand", provenance)
    self.assertIn(
        "https://raw.githubusercontent.com/bitpay/bitcoin-brand/master/bitcoin.png",
        provenance,
    )
```

- [ ] **Step 2: Run the focused test and confirm the expected failure**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_render.ExampleTests.test_bitcoin_cover_examples_share_the_original_local_logo -v
```

Expected: error because `examples/art/bitcoin-logo.png` and its provenance note do not exist.

- [ ] **Step 3: Add the source asset and provenance note**

Download the 1000x1000 RGBA PNG from the Bitcoin Brand repository and verify its digest before use:

```bash
mkdir -p examples/art
curl -L --fail --silent --show-error \
  https://raw.githubusercontent.com/bitpay/bitcoin-brand/master/bitcoin.png \
  -o examples/art/bitcoin-logo.png
shasum -a 256 examples/art/bitcoin-logo.png
```

Write `examples/art/README.md` with the asset filename, source repository URL, exact raw download URL, SHA-256 digest, 1000x1000 size, RGBA format, and public-domain dedication stated by the source repository.

- [ ] **Step 4: Replace both example inputs with Bitcoin research content**

Use this light example:

```json
{
  "template": "cover-editorial",
  "slug": "bitcoin-use-cover",
  "category": "BITCOIN RESEARCH",
  "title": "비트코인은\n어디에서 쓰이는가",
  "subtitle": "보유 자산을 넘어 결제와 준비자산으로 확장되는 흐름을 추적한다.",
  "date": "2026.09.03",
  "hero_image": "art/bitcoin-logo.png"
}
```

Use this dark example:

```json
{
  "template": "cover-object",
  "slug": "bitcoin-reserve-cover",
  "category": "BITCOIN OUTLOOK",
  "title": "비트코인은\n준비자산이 되는가",
  "subtitle": "수요 구조와 유동성 변화를 통해 장기 채택 조건을 살펴본다.",
  "date": "2026.09.03",
  "hero_image": "art/bitcoin-logo.png"
}
```

- [ ] **Step 5: Run the focused and full tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_render.ExampleTests.test_bitcoin_cover_examples_share_the_original_local_logo -v
.venv/bin/python -m unittest discover -s tests -v
```

Expected: the focused test passes, followed by the complete suite with 0 failures and 0 errors.

---

### Task 3: Documentation, Rendering, and Visual QA

**Files:**
- Modify: `docs/IMAGE_SYSTEM.md`
- Generate but do not commit: `out/bitcoin-use-cover.html`
- Generate but do not commit: `out/bitcoin-use-cover.png`
- Generate but do not commit: `out/bitcoin-reserve-cover.html`
- Generate but do not commit: `out/bitcoin-reserve-cover.png`
- Generate but do not commit: `.context/previews/btc-cover-light.png`
- Generate but do not commit: `.context/previews/btc-cover-dark.png`

**Interfaces:**
- Consumes: the two finished example JSON files and local Bitcoin logo.
- Produces: documented reusable `hero_image` behavior plus visually inspected preview PNGs for user review.

- [ ] **Step 1: Update the image-system documentation**

State that both covers accept the same optional local `hero_image`. Document each fallback: light uses its UNIT TX Blue editorial circle when absent, dark leaves negative space. Update the cover JSON examples to include `hero_image` and the Bitcoin example copy. Keep the path-safety rules unchanged.

- [ ] **Step 2: Validate text and source changes**

Run:

```bash
git diff --check
grep -RInE '—|–' examples/cover-editorial.json examples/cover-object.json templates/cover-editorial.html templates/cover-object.html || true
.venv/bin/python -m unittest discover -s tests -v
```

Expected: no whitespace errors, no em dash or en dash in visible cover inputs or templates, and all tests pass.

- [ ] **Step 3: Render all examples**

Run:

```bash
.venv/bin/python render.py --all
```

Expected: four `[ok]` lines and `[done] 4 images`.

- [ ] **Step 4: Verify cover dimensions and asset fidelity**

Run:

```bash
sips -g pixelWidth -g pixelHeight out/bitcoin-use-cover.png out/bitcoin-reserve-cover.png
sips -g pixelWidth -g pixelHeight -g hasAlpha -g space examples/art/bitcoin-logo.png
shasum -a 256 examples/art/bitcoin-logo.png
```

Expected: both covers are 1440x756, the source asset is 1000x1000 with alpha, and its SHA-256 is `b0231779b54f52e4352fa4300cb5353351bee8261f5d84b6e6ad8f6a2d24a1a4`.

- [ ] **Step 5: Inspect both covers at original size**

Open both rendered PNGs at original resolution. Check title line breaks, category placement, untouched orange Bitcoin mark, clear negative space, no card or glow, black date at bottom left, one correctly treated UNIT TX lockup at bottom right, and no clipping or overlap. Adjust only the theme-specific image position or size if the visual balance fails, then repeat Steps 2 through 5.

- [ ] **Step 6: Save stable review previews**

Copy the verified covers to `.context/previews/btc-cover-light.png` and `.context/previews/btc-cover-dark.png` for the user's visual review.

- [ ] **Step 7: Commit the verified implementation**

```bash
git add \
  assets/styles.css \
  docs/IMAGE_SYSTEM.md \
  examples/art/README.md \
  examples/art/bitcoin-logo.png \
  examples/cover-editorial.json \
  examples/cover-object.json \
  templates/cover-editorial.html \
  templates/cover-object.html \
  tests/test_render.py
git commit -m "Add original Bitcoin cover examples"
```
