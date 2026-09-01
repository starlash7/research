# UNIT TX Research Image Templates Design

## Goal

Create a version-controlled image system for UNIT TX research posts on Substack. The first release produces polished cover images and reusable in-article figures from structured JSON without requiring Canva or Figma for routine edits.

## Reference Direction

The system combines three qualities from the supplied references:

- restrained editorial covers with large Korean typography and generous whitespace;
- object-led covers with a dark, atmospheric background;
- information-dense figures with a clear claim, source, as-of date, chart, and takeaway metrics.

The implementation follows the proven `kimch-index` card pipeline: Jinja templates render structured data into fixed-size HTML, and Playwright captures deterministic PNG output. This repository does not copy its collectors or product-specific card logic.

## Canonical Formats

| Format | Output size | Ratio | Use |
| --- | ---: | ---: | --- |
| `cover` | 1440×756 | 1.90:1 | Substack post cover and social preview |
| `wide` | 1440×810 | 16:9 | In-article frameworks, flows, and comparisons |
| `data` | 1440×1200 | 6:5 | Charts, KPI summaries, and dense evidence |

The renderer supports an optional 2× export for unusually high-resolution needs, but standard checked examples use the canonical sizes above. The cover ratio matches Substack's 1200×630 social-preview recommendation while providing more source pixels.

## Initial Template Set

### Editorial cover

`cover-editorial` uses a warm off-white field, black UNIT TX mark, compact category pill, left-aligned title and subtitle, and a restrained topic symbol on the right. It is the default research cover.

### Object cover

`cover-object` uses a near-black field, subtle technical grid and glow, white UNIT TX mark, left-aligned editorial copy, and an optional user-supplied hero image. When no hero image is supplied, a deterministic CSS object provides a complete fallback rather than leaving an empty region.

### Data figure

`figure-data` contains a claim-led heading, source line, as-of date, legend, line or bar chart, and up to three takeaway cards. It is designed for sourced quantitative evidence, not decoration.

### Framework figure

`figure-framework` presents three to five labeled nodes and their relationships. It is used for protocol architecture, transaction flow, system maps, and comparisons.

## Brand System

The supplied 738×694 UNIT TX symbol is the canonical logo asset. It remains unaltered. On light surfaces it is rendered black with multiply blending; on dark surfaces it is inverted and rendered white with screen blending. This removes the screenshot's white field visually without redrawing or approximating the logo.

The initial palette is intentionally restrained:

- paper: `#F3F1EC`
- white: `#FFFFFF`
- ink: `#0A0A0A`
- muted ink: `#6E6B65`
- signal orange: `#FF4D00`
- electric blue: `#2563EB`
- positive: `#07883F`
- negative: `#D92D3A`

Pretendard Variable is the primary Korean and Latin typeface. A local font asset is bundled so browser and machine differences cannot change line breaks. Monospace labels use the platform monospace fallback only for short metadata.

## Authoring Rules

The root `AGENTS.md` is the mandatory concise rule file for future agents. `docs/IMAGE_SYSTEM.md` is the human-facing detailed guide. Together they require:

- source and as-of date on every quantitative figure;
- no fabricated values, unsupported claims, or decorative precision;
- a maximum of two title lines on covers;
- no essential content inside the outer 6% safe margin;
- minimum readable type sizes per format;
- color never being the only carrier of meaning;
- explicit labels and units on charts;
- Korean word keeping and tabular numerals;
- deterministic filenames and committed example inputs;
- visual inspection for clipping, overflow, logo treatment, and source visibility.

## Architecture

The implementation stays deliberately small:

- `render.py` is the CLI and rendering entry point.
- `templates/` contains Jinja HTML templates and shared partials.
- `assets/` contains the canonical logo and local font.
- `examples/` contains one JSON input per template.
- `out/` contains generated HTML and PNG files and is ignored except for a placeholder.
- `tests/` verifies input validation, template rendering, dimensions, and output naming.

The renderer accepts either one JSON file or `--all` examples. A JSON document identifies its template and supplies only content fields. Template dimensions are fixed by the selected template and cannot be overridden by content.

## Data Flow

1. Load and validate UTF-8 JSON.
2. Resolve the named template from an allowlist.
3. Normalize common metadata such as date, source, and output slug.
4. Render Jinja HTML with autoescaping enabled.
5. Open the local HTML in Chromium and wait for fonts and images.
6. Capture the exact template viewport as PNG.
7. Verify the PNG dimensions and write a small manifest.

No external network request is required for mock rendering. Hero images must be local paths so old research can be reproduced later.

## Error Handling

- Unknown templates, missing required fields, invalid colors, unsupported chart types, and unsafe output slugs fail with a concise error before Chromium starts.
- Overlong titles fail validation rather than silently shrinking to unreadable text.
- Missing optional hero art uses the CSS fallback.
- Missing required local assets fail the run; they are not replaced with remote assets.
- Existing unrelated output files are never deleted. A render replaces only its own HTML, PNG, and manifest entry.

## Testing and Verification

Automated tests cover template allowlisting, required fields, safe slugs, title limits, chart-series shape, HTML escaping, output dimensions, and manifest contents. Rendering verification runs all example inputs and checks each PNG with the operating system image metadata tool.

Visual review checks:

- all text and footer content remains inside the canvas;
- the UNIT TX mark has no visible rectangular background;
- Korean titles wrap intentionally;
- sources, dates, units, and chart legends are readable;
- light and dark covers preserve sufficient contrast;
- the 6:5 data card remains understandable when scaled to mobile width.

## Success Criteria

- One command renders all four example templates without network access.
- Outputs exactly match 1440×756, 1440×810, or 1440×1200 as appropriate.
- Future research images can be created by editing JSON and optional local hero art only.
- The repository documents authoritative visual and data-integrity rules for every future contributor.
- The generated examples visibly form one UNIT TX family while preserving the distinct editorial, object, chart, and framework use cases.
