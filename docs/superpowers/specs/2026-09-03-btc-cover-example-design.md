# BTC Cover Example Design

## Goal

Create one light and one dark UNIT TX cover example that use the original orange Bitcoin logo as the article visual. The examples must demonstrate the reusable workflow: a user clones the repository, replaces local content and `hero_image`, and receives covers that preserve the UNIT TX layout and brand rules.

## Scope

- Add local `hero_image` support to `cover-editorial`.
- Keep the existing local `hero_image` support in `cover-object`, but remove the card-like media frame from the rendered composition.
- Add one original-color Bitcoin logo file under the example assets and reference the same file from both cover JSON examples.
- Change both example covers to Bitcoin-related categories and copy so the visual and article subject agree.
- Update tests and image-system documentation for the shared cover behavior.
- Do not change canvas sizes, footer structure, UNIT TX logo treatment, date treatment, font family, or font weights.

## Asset Rules

- Use the established orange Bitcoin roundel with its white Bitcoin glyph from a Bitcoin project distribution source.
- Preserve the source asset's color, proportions, orientation, and transparent background. Do not redraw, recolor, tint, crop, distort, add a shadow, or place it inside a new decorative shape.
- Store the asset locally and render without remote requests.
- Record its source page and download URL beside the example asset so future maintainers can verify provenance.
- `assets/unit-tx-logo.png` remains the only UNIT TX brand symbol and stays unchanged at the bottom right.

## Shared Input Contract

Both cover templates accept an optional `hero_image` string. It must resolve to a PNG, JPG, JPEG, or WebP file inside the JSON file's directory or one of its descendants. Existing path validation continues to reject remote URLs, absolute paths, and parent-directory traversal.

The example JSON files both use the same relative input:

```json
"hero_image": "art/bitcoin-logo.png"
```

When a cover has no `hero_image`:

- `cover-editorial` keeps its existing UNIT TX Blue circular editorial visual.
- `cover-object` keeps the right side empty and shows only the layered dark gradient.

## Light Cover Composition

- Keep the white background, top-left category, left-aligned title and subtitle, bottom-left black date, and bottom-right dark UNIT TX lockup.
- When `hero_image` is present, replace the existing blue circular visual with the supplied image in the same right-side visual zone.
- Render the image with `object-fit: contain` and a transparent surrounding area.
- Do not add a card, ring, caption, asset name, ticker, glow, or extra label around the Bitcoin logo.
- Keep the logo within the 6% safe area and subordinate to the title.

## Dark Cover Composition

- Keep the low-saturation charcoal, smoke, and deep-blue gradient, top-left category, left-aligned title and subtitle, bottom-left black date on white, and bottom-right white UNIT TX lockup.
- Render the supplied image as an independent right-side object directly on the gradient.
- Remove the existing rounded media card around `hero_image`.
- Use `object-fit: contain`; do not crop the Bitcoin logo or add a glow, graph, grid, generated symbol, or decorative 3D object.
- Keep sufficient negative space around the logo so the dark cover remains editorial rather than promotional.

## Example Copy

The examples use concrete Bitcoin research copy without decorative labels or repeated statements.

Light cover:

- Category: `BITCOIN RESEARCH`
- Title: `비트코인은\n어디에서 쓰이는가`
- Subtitle: `보유 자산을 넘어 결제와 준비자산으로 확장되는 흐름을 추적한다.`

Dark cover:

- Category: `BITCOIN OUTLOOK`
- Title: `비트코인은\n준비자산이 되는가`
- Subtitle: `수요 구조와 유동성 변화를 통해 장기 채택 조건을 살펴본다.`

The existing date format remains unchanged and appears only in the footer.

## Template Structure

Use one image class for both covers so containment behavior is consistent. Theme-specific wrappers control only position and size. The image element is conditional and receives an empty `alt` because the cover title already communicates the subject and the rendered PNG is the final artifact.

The light wrapper retains its current fallback decoration only when no image exists. The dark wrapper exists only when an image exists and has no background, border, or frame.

## Verification

- Unit tests confirm that both cover templates render a local `hero_image` and still reject unsafe paths through the existing renderer validation.
- Unit tests confirm that the dark cover has no media-card wrapper and that the light fallback remains available without an image.
- Render both example PNGs at 1440×756.
- Check dimensions with `sips`.
- Inspect both PNGs at original size for clipping, unintended line breaks, altered Bitcoin logo colors or proportions, duplicate labels, footer placement, and logo backgrounds.
- Run the full unit-test suite before completion.
