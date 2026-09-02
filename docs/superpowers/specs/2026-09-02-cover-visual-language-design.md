# UNIT TX Cover Visual Language Revision

## Scope

Revise the two 1440×756 cover templates only. The change restores a premium dark visual language and adds an explicit article category to both cover types. Figure templates, chart behavior, footer positions, logo treatment, SUIT typography, and fixed canvas sizes remain unchanged.

## Design Read

This is an editorial research-cover system for crypto and finance readers. The light family should feel clear and product-like, using white space and UNIT TX Blue. The dark family should feel premium and atmospheric, using restrained depth similar to the supplied dark research references without copying their logos, graphics, or composition.

Design settings:

- Design variance: 6. Asymmetric editorial composition with stable reusable positions.
- Motion intensity: 1. The output is a static PNG.
- Visual density: 3. Category, title, subtitle, date, and one UNIT TX lockup only.

## Considered Approaches

### 1. Layered editorial gradient, selected

Build the dark atmosphere with native CSS layers: charcoal base, a cool smoke field, one deep-blue directional wash, and a subtle edge vignette. Keep the right side as atmospheric negative space unless a real `hero_image` is supplied.

This approach is deterministic, local, and reusable for every article. It creates depth without inventing a graph, protocol symbol, or decorative data visualization.

### 2. Tinted photography

Use a darkened full-bleed article image under a gradient scrim. This can look more distinctive per article, but it requires a suitable image for every publication and weakens the clone-and-edit workflow when no image exists.

### 3. Generated abstract object

Place a different abstract 3D object on each dark cover. This resembles some references but adds an asset-generation dependency and risks unrelated filler imagery. It is not suitable as the default template.

The system selects approach 1. A supplied local image remains an optional enhancement, not a requirement.

## Shared Cover Information Hierarchy

Both cover templates require a `category` JSON field. It appears once in the top-left safe area as plain editorial metadata, not as a sentence or decorative index.

Visible text is limited to:

1. category;
2. title;
3. subtitle;
4. date;
5. UNIT TX wordmark.

No author fallback, use-case label, template name, index number, center-footer copy, or generated caption is added.

Example categories include `ONCHAIN RESEARCH`, `MARKET`, and `PROTOCOL`. The renderer accepts one non-empty text value and autoescapes it. Category copy should be short enough to remain on one line.

## Light Cover

The light cover uses a pure white surface, UNIT TX Blue `#0064FF`, and deep navy text. The category sits at the top-left as a compact blue label with no pill or oversized container. The title and subtitle remain left-aligned below it. The existing blue circular visual stays on the right as the single brand-colored composition element.

The category establishes article context, while the title remains the dominant element. Date stays bottom-left and the official UNIT TX lockup stays bottom-right.

## Dark Cover

The dark cover must not use a flat black fill. Its background uses four restrained layers:

- charcoal base around `#111318`;
- smoke-grey illumination from the upper-right;
- deep UNIT TX blue wash from the lower-left or right edge;
- soft vignette that preserves strong text contrast.

The gradient is low saturation and has no neon glow. It should read as light passing across a dark material rather than an AI-style purple mesh.

The category sits top-left in a muted off-white. Title and subtitle remain left-aligned. If `hero_image` is absent, the gradient and negative space are the complete composition. If present, the existing local image frame is retained with a subtle dark border and scrim so it belongs to the same palette.

The date remains exact black text as already requested. On the dark cover it stays on a small white backing for contrast. The official logo and UNIT TX wordmark remain white at bottom-right.

## Data Contract

`category` becomes required for both `cover-editorial` and `cover-object`. It is not used by figure templates. Existing cover JSON files must add the field.

The input flow remains unchanged:

1. clone an example JSON;
2. replace category, title, subtitle, date, and optional image;
3. run `render.py`;
4. receive a deterministic PNG.

No new dependency or remote asset is introduced.

## Validation and Error Handling

- Missing or blank `category` fails before rendering.
- A category wider than 24 display-width units fails rather than wrapping.
- Existing title, slug, local-image, and canvas validation remains unchanged.
- User-provided category text is HTML-escaped through the existing Jinja environment.

## Test and Visual Verification

Tests must first fail for the missing behavior, then pass after implementation. They cover:

- both cover templates requiring `category`;
- both templates rendering category exactly once;
- category width validation;
- the dark cover using layered gradients instead of a flat `#0A0A0A` background;
- no generated graph, protocol symbol, or filler copy returning;
- unchanged footer, logo, font, and dimensions.

Final verification renders all four examples, checks PNG dimensions, inspects computed styles, and reviews both cover PNGs at original size for clipping, contrast, line wrapping, and visual hierarchy.

## Success Criteria

- The light cover visibly includes an article category at top-left.
- The dark cover has restrained charcoal, smoke, and deep-blue gradient depth rather than a flat black field.
- Both covers remain recognizably one UNIT TX system through typography, footer, spacing, and category placement.
- A new cover still requires JSON edits only.
- No unnecessary phrase, duplicated metadata, generated graph, or unrelated symbol appears.
