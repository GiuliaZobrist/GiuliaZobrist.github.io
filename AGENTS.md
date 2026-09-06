# AGENTS.md

Working notes for AI agents (and humans) editing this repo.

## Stack

Jekyll static site, deployed via GitHub Pages. No build step beyond `jekyll`.
Local preview: `bundle exec jekyll serve`. Generated output lives in `_site/`
— never edit it, it is overwritten on every build.

- `index.html` — the homepage, front-matter + inline HTML, uses the `default` layout.
- `_layouts/default.html` — the only layout. **All CSS lives here**, inline in a
  single `<style>` block. There is no separate stylesheet.
- `_posts/` — blog entries.
- `_data/` — YAML data files exposed to Liquid as `site.data.<name>`.

## Where the rules live

- **`CONTEXT.md`** — the design system: type scale, spacing tokens, palette,
  typographic principles, and what must be preserved. **Read it before touching
  any styling or markup that affects layout.** New UI should visually match
  existing components (the `.project-card` block is the reference pattern for
  expandable, thumbnailed cards).
- **`README.md`** — setup, local preview, adding a post, deploy.
- **`TODO.md`** — open tasks and parked ideas.

## "On the run" — Strava activities

The homepage shows a collapsed card (`<details id="statues">`, opened only via
an `a[href="#statues"]` link) containing a horizontally sliding, scroll-snapped
strip of Strava activity embeds.

**To add or change an activity, edit `_data/runs.yml` only.** Each entry:

```yaml
- id: "19972522066"        # the number in the Strava activity URL
  token: "…"               # embed token from Strava's Share > Embed dialog
  place: "Zürichberg"      # free text, shown in the caption
  description: "…"         # one line, written by Giulia
```

Agents cannot obtain `token`, `place`, or `description` — the embed token is
only visible to the logged-in activity owner. Leave `TODO` placeholders and ask
Giulia to fill them.

Implementation notes (all in `index.html` + `_layouts/default.html`):

- `index.html` loops over `site.data.runs`, emitting one
  `.strava-embed-placeholder` per entry.
- `https://strava-embeds.com/embed.js` is loaded lazily the first time the card
  opens — running it while the card is `display:none` renders the iframes at
  zero width, and it never re-runs.
- Classes: `.strava-embed-wrap` (card shell), `.strava-carousel` (flex row:
  arrow / strip / arrow), `.strava-strip` (scroll container, scrollbar hidden),
  `.strava-slide` (one activity + `figcaption`), `.strava-nav` (round arrow
  buttons — removed when fewer than 2 activities).
- An inline script tracks the slide index, scrolls the strip on arrow clicks,
  and disables each arrow at its end of the range.
