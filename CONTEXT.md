# Design Context — giuliazobrist.com

## Character

A personal site in the spirit of a well-set LaTeX document: Computer Modern Sans,
generous leading, classical proportions, no ornament. The aesthetic is rooted in
the author's own history with LaTeX and printed type.

---

## Typographic Principles

These principles derive from 500 years of typographic practice, encoded by Knuth
in TeX and applied here to CSS.

### The Em as Unit of Measure

All spacing and sizing is expressed in `rem` (relative to the 17 px root size) so
every proportion stays consistent if the base changes. Never use `px` for spacing
or type sizes except at the system boundary (border widths, outline offsets).

### Measure (Line Length)

Optimal reading line: **45–75 characters**. Enforced via `max-width: 58ch` on body
paragraphs. The column (`--col: 720px`) is wider to allow headings and decorative
elements to breathe; body text is constrained inside it.

### Leading (Line Height)

`line-height: 1.8` on body text is intentionally generous — it echoes the airy
spacing of a lightly-leaded LaTeX document and suits the light (300) weight.
Headings and display text use tighter leading (1.3–1.4) because they are read in
a single fixation, not line by line.

### Tracking (Letter Spacing)

- Large display text (blockquote): slight negative tracking (`-0.015em`) — large
  glyphs naturally space too wide optically.
- Headings (h2): slight negative tracking (`-0.01em`).
- Small all-caps labels: positive tracking (`+0.12em`) — tight all-caps is
  illegible; open tracking compensates.
- Body text: no tracking override — the font's own spacing is correct at text size.

### Type Scale

Based on a **Major Third** ratio (×1.25):

| Token      | rem     | px@17px | Use                          |
|------------|---------|---------|------------------------------|
| `--t-xs`   | 0.694   | 11.8    | contact label (all-caps)     |
| `--t-sm`   | 0.8     | 13.6    | tags, footer, captions       |
| `--t-nav`  | 0.8125  | 13.8    | nav links, secondary links   |
| `--t-base` | 1       | 17      | body copy                    |
| `--t-md`   | 1.125   | 19.1    | h2                           |
| `--t-lg`   | 1.25    | 21.25   | contact email                |
| `--t-xl`   | 1.563   | 26.6    | blockquote min               |
| `--t-2xl`  | 2.25    | 38.25   | blockquote max               |

### Spacing Scale

Sections breathe on a consistent rhythm. The scale is em-based with a ×1.5–2
step between levels:

| Token    | rem  | px@17px | Use                                   |
|----------|------|---------|---------------------------------------|
| `--sp-1` | 0.5  | 8.5     | tag padding, tight gaps               |
| `--sp-2` | 1    | 17      | inline margins, figcaption            |
| `--sp-3` | 1.5  | 25.5    | label→content, h2→body, list gaps     |
| `--sp-4` | 2    | 34      | tags row, nav gap                     |
| `--sp-5` | 2.5  | 42.5    | nav/wrap padding, cite margin         |
| `--sp-6` | 4.5  | 76.5    | medium section padding (sankey)       |
| `--sp-7` | 5    | 85      | standard section padding (chapters)   |
| `--sp-8` | 6    | 102     | generous section padding (opening)    |

### Vertical Rhythm

All top-level sections use the same vertical spacing so the page scrolls with
a predictable pulse. Exceptions only for the opening (extra bottom padding to
make the hero feel set apart) and the footer (compressed, deliberately quiet).

### Optical Corrections

- `text-underline-offset: 3px` on body links — default underlines sit too close
  to the descenders.
- `-webkit-font-smoothing: antialiased` — Computer Modern renders better with
  subpixel smoothing suppressed on macOS.
- Horizontal rule separators use `--rule` (a warm off-white) not pure grey —
  hard rules fight the warm background.

---

## Colour Palette

| Token     | Value     | Role                                      |
|-----------|-----------|-------------------------------------------|
| `--bg`    | `#faf9f6` | Warm off-white — echoes uncoated paper    |
| `--ink`   | `#2c2c2c` | Near-black — softer than #000, less glare |
| `--muted` | `#8c8c8c` | Secondary text, metadata                 |
| `--sage`  | `#8a9e8a` | Accent — links, underlines, Sankey        |
| `--rule`  | `#e4e1da` | Borders — warm, not cool grey             |

The palette avoids pure black and pure white deliberately — both create harsh
contrast that tires the eye. The sage accent is the only non-neutral colour and
should stay so.

---

## Layout

- **Single column**, centred, max `--col` (720 px) for content.
- **Outer wrap** adds horizontal padding for smaller viewports.
- Floating margin images appear only when the viewport is wide enough to show
  true margins (> 900 px) — below that they would overlap content.
- Two-sided margin logic (inner > outer) does not apply here (no print target),
  so symmetric padding is correct.

---

## What to Preserve

- Computer Modern Sans — central to the identity.
- The warm background/ink palette.
- `line-height: 1.8` on body — the airiness is intentional.
- The `58ch` paragraph measure.
- Negative tracking on display text.
