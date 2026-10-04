# Plan: Letterboxd films on a GitHub Pages site

**How to use this file (Claude Code):** read `AGENTS.md` and `CONTEXT.md` first (this is a Jekyll site, all CSS inline in `_layouts/default.html`). Work through the tasks in order and tick them off. Don't change the **Decisions** section without asking.

**Status (2026-10-04):** UI is done (Task 5). History imported (Task 6): `_data/films.json` has 129 entries, rebuilt from a fresh export after the duplicate and sensitive tags were fixed on Letterboxd. Task 0 done (fixture saved, not committed). Open: Tasks 1 to 4 (weekly RSS update, tests, Action), plus the tag decision below. See **Git plan** at the end for what is committed when.

## Decisions (already made by the human)

- **No Pillow.** Posters are stored as downloaded. No image processing, standard library only.
- **Always sort by `watchedDate` descending**, never by feed order.
- **Weekly delta load**, and the **whole diary scrollable** on the site.
- **Full history comes from a one-time manual Letterboxd CSV export** (Task 6). The RSS feed alone cannot provide it.

## Adaptations to this repo (made 2026-10-04)

The original plan assumed a plain static site with client-side `fetch`. This repo is Jekyll, so:

- **Data lives in `_data/films.json`**, not `data/diary.json`. Jekyll exposes it as `site.data.films` and Liquid renders the list **at build time**. This replaces `films.js`, the `fetch`, the chunked `IntersectionObserver` rendering, the error state and the `<noscript>` fallback: 130 text rows are plain HTML, the whole list is simply the page, and it works without JS. Revisit only if it passes a few thousand rows.
- **No separate stylesheet.** All CSS lives in the single `<style>` block of `_layouts/default.html` (see AGENTS.md). Film styles are the `.films-*` block there, on top of the shared `.expander` card shell.
- **No dark mode.** The site has a single warm palette (`CONTEXT.md`); the films card uses `--bg --ink --muted --sage --rule` only.
- **Text-first, no posters in the UI.** The CSV export has no poster URLs, so 80+ of 130 entries could never have one. A mixed poster/no-poster grid would look broken, so the diary is a typographic table (date, title and year, stars, ♥ liked, ↺ rewatch), in the spirit of the site. Poster caching (Task 2) is now optional and only worth doing if a poster is wanted in the collapsed card.
- **Tags are stored but never rendered.** The export's `Tags` column holds festival tags (`zff2026`, `locarno film festival 2026`, `live_music`) but also `w-<name>` tags naming people Giulia watched with. **Decision (2026-10-04, Giulia): all tags stay in `_data/films.json`, including `w-*` (currently `w-gold`). This is a risk she knowingly owns; do not filter, strip or rewrite git history for them, and do not raise it again.** The only rule that remains: never render tags in the UI. `update_films.py` must keep stored tags on update (the RSS feed carries none).
- **Site type is a user site** (`giuliazobrist.github.io`), and the site already uses root-absolute paths (`/assets/...`, `/blog/`), so the films card does too.
- **Private data stays out.** The export folder (email, watchlist, profile) sits in `tmp/`, which is now in `.gitignore` and in `_config.yml` `exclude` (otherwise Jekyll would publish the CSVs). `scripts/`, `tests/` and `PLAN.md` are excluded from the build too.

## Goal

Show the films logged by Letterboxd user `lemongiu_cinema` (https://letterboxd.com/lemongiu_cinema/) on an existing static HTML site hosted on GitHub Pages. No server, no secrets, no framework. Python is available for tooling (stdlib preferred).

Requirements (confirmed by the human):
- `_data/films.json` is updated by a **weekly delta load**: each run only adds new or changed entries on top of what is already stored. It never rebuilds from scratch.
- The **entire list** (all 129 entries, not just recent ones) is browsable by scrolling on the site.

Two UI pieces:
1. **Homepage card** (`<details id="films">` in `index.html`): the latest 8 films, collapsed by default, opened by the "cinema" link in the paragraph above it, same shell as the Strava card.
2. **Full history inside the same card:** the whole list (all years) is a vertical scroll area, grouped by year with sticky year labels. No separate page.

## Constraints

- GitHub Pages is static, and browsers can't fetch Letterboxd directly (CORS). Data must be fetched ahead of the Jekyll build and committed as JSON.
- The official Letterboxd API is not available for personal projects, so the **public RSS feed** is the data source.
- Python script uses the standard library only (`urllib`, `xml.etree`, `json`, `csv`, `re`, `html`). No third-party packages (no Pillow).
- Frontend: Liquid + inline CSS, matching `CONTEXT.md`. No JS needed for the list itself. No build step beyond Jekyll.

## Verified facts about the feed

Checked against the live feed `https://letterboxd.com/lemongiu_cinema/rss/`. Re-verify with the fixture in Task 0.

- Namespaces: `letterboxd` = `https://letterboxd.com`, `tmdb` = `https://themoviedb.org`, `dc` = `http://purl.org/dc/elements/1.1/`.
- Per-film fields: `letterboxd:filmTitle`, `filmYear`, `watchedDate` (YYYY-MM-DD), `memberRating` (0.5 to 5.0, may be absent), `memberLike` (Yes/No), `rewatch` (Yes/No), `tmdb:movieId`, `link`, `guid`, `pubDate`.
- The feed has about **50 items**, while the profile diary has 130 entries. The feed alone can't give the full history.
- **Feed order is by log time (`pubDate`), not watch date.** This account backfilled many old films in one session (e.g. `watchedDate` 2012 to 2024, all with `pubDate` Dec 2025). The first N items in feed order are therefore NOT the most recently watched. **Always sort by `watchedDate` descending.**
- Lists appear as `<item>` entries with no `filmTitle` (guid prefix `letterboxd-list-`). Skip them.
- Some items are TV, using `tmdb:tvId` instead of `tmdb:movieId` (e.g. The Queen's Gambit).
- `guid` prefix is `letterboxd-watch-` for plain logs and `letterboxd-review-` for entries with a review.
- `<description>` is CDATA HTML: a `<p><img src="...poster..."/></p>` followed by a `<p>`. That paragraph is either `Watched on <Weekday> <Month> <D>, <YYYY>.` (no review) or the **review text**. Treat the "Watched on ..." pattern as "no review".
- Titles contain XML entities (`&#039;`) and non-ASCII characters (`Zürrer`, `Lätscht`). Use a real XML parser and write JSON with `ensure_ascii=False`.
- Poster URLs are on `a.ltrbxd.com` at 600x900.

## Data contract (`_data/films.json`)

This is the only interface between backend and frontend. Keep it stable.

```json
{
  "user": "lemongiu_cinema",
  "last_logged_at": "2026-10-04",
  "entries": [
    {
      "id": "violette-2026-2026-10-01",
      "title": "Violette",
      "year": 2026,
      "watched": "2026-10-01",
      "rating": 4.5,
      "liked": true,
      "rewatch": false,
      "review": null,
      "tags": ["zff2026", "w-gold"],
      "url": "https://boxd.it/gAKk1n",
      "media": "movie",
      "tmdb_id": null,
      "poster": null,
      "logged_at": "2026-10-03"
    }
  ]
}
```

- `id` = `slugify("<title> <year> <watched>")` from `scripts/filmslib.py` (ASCII-folded, lowercase, hyphenated). Both importers use it. This is the dedupe key (it also lets the CSV backfill merge cleanly).
- `rating` is `null` when unrated. `review` is `null` when absent. `tags` is a list (possibly empty), data only, never rendered.
- `logged_at` is a bare date (`YYYY-MM-DD`) for CSV entries and a full timestamp for RSS entries. Both sort correctly as strings.
- `url` is the `boxd.it` short link for CSV entries and the full film URL for RSS entries (RSS wins on merge only if the CSV value is missing, so the short link stays; both resolve to the same film).
- There is no `generated_at` field: it would dirty the file (and git history) on every run.
- `entries` is sorted by `watched` desc, then `logged_at` desc.
- The store is **accumulating**: each run merges new feed items into the existing file and never truncates. This is how history grows beyond the feed's 50-item window.
- `last_logged_at` is the delta cursor: the newest `logged_at` seen so far (`filmslib.save` computes it). It is informational and used for logging ("N new, M updated since <cursor>"). Correctness relies on the `id` merge, not on the cursor, so edits to older entries still propagate while they remain inside the feed's window.
- Weekly cadence caveat: the feed window is about 50 items. If more than about 50 entries are logged or edited between two runs (e.g. a big backfill session), the oldest would fall out of the window. The script should warn when **all** feed items are new (no overlap with the stored data), since that signals possible loss. The fix is a manual `workflow_dispatch` run or a CSV import.

## Repo layout

```
index.html                     # homepage; films card (done)
_includes/films-row.html       # one row, shared by both (done)
_layouts/default.html          # + .films-* CSS block (done)
_data/films.json               # the store (130 entries imported)
scripts/filmslib.py            # slugify, load, deterministic save (done)
scripts/import_csv.py          # one-time history backfill (done)
scripts/update_films.py        # weekly RSS delta (Task 1)
assets/posters/                # only if Task 2 is done
tests/fixtures/rss.xml         # live feed snapshot, 2026-10-04 (done)
tests/test_films.py            # Task 3
.github/workflows/letterboxd.yml
```

## Tasks

### Task 0: Fixture and exploration — DONE
- `curl -A "Mozilla/5.0" https://letterboxd.com/lemongiu_cinema/rss/ -o tests/fixtures/rss.xml`.
- Confirm the facts above still hold. Note any difference in a short comment at the top of the script.

**Done when:** fixture committed and facts confirmed. *Fixture saved (46 KB, 50 items). Not yet committed.*

### Task 1: `scripts/update_films.py`
- Config via env: `LETTERBOXD_USER` (default `lemongiu_cinema`), `--rss-file` (offline/test mode), `--out _data/films.json`. Reuse `filmslib` for ids, merge and save. RSS item fields map to the existing entry shape (`tags: []` for new entries; keep existing tags on update).
- Merge rule for entries already in the store (from the CSV): RSS wins for `rating`, `liked`, `rewatch`, `review`, `url`, `tmdb_id`, `poster`, `media`, `logged_at`; keep CSV `tags` (the feed has none).
- Fetch with a descriptive User-Agent, a 30s timeout, and one retry with backoff.
- Parse items. Skip anything without `filmTitle`. Map TV vs movie. Parse rating as float or `None`. Extract the review per the rule above (strip tags, unescape, collapse whitespace).
- **Delta load:** merge into the existing JSON by `id`. Classify each feed item as new, changed (any field differs), or unchanged. Only new and changed entries are written. Print a one-line summary (`3 new, 1 updated, 46 unchanged`) so the Action log shows what the weekly run did. Editing a review or rating on Letterboxd propagates; deleting an entry on Letterboxd does not remove it locally (document this).
- Update `last_logged_at` to the newest `logged_at` seen. Warn (don't fail) if zero feed items overlap with stored entries while stored entries exist.
- Sort and write deterministically (stable key order, `indent=2`, trailing newline) so git diffs stay clean. Don't rewrite the file if nothing changed (`filmslib.save` already does this).
- **Safety:** if the fetch fails or parses 0 films, exit non-zero and leave the existing file untouched.

**Done when:** running it twice on the fixture produces an identical file the second time.

### Task 2 (optional now): Poster caching
- For each entry without a local poster, download the feed's poster URL to `assets/posters/<tmdb_id>.jpg` (or `<id>.jpg` if there is no TMDB id).
- Skip existing files. Sleep about 0.5s between downloads. Never fail the whole run on one bad poster, and leave `poster: null` instead.
- Rationale: avoids hotlinking Letterboxd's CDN and avoids poster URL rot. Posters are saved as downloaded (no resizing). Expect roughly 10 MB or more for about 130 posters; mention this to the human and let them choose hotlinking instead if the repo size matters (open question 4). Since the UI is text-first, skip this unless posters are wanted.
- Entries imported from CSV have no poster URL, so `poster` stays `null` for them.

**Done when:** all RSS entries have a poster file or an explicit `null`.

### Task 3: Tests (`pytest`)
Using the fixture and a small CSV fixture (a trimmed copy of the export, no personal files), cover:
- Lists are skipped.
- TV item (`tvId`) is parsed as `media: "tv"`.
- Entities and non-ASCII titles decode correctly.
- Sorting is by `watched`, not feed order (e.g. Violette 2026-10-01 must come before The Zürrer Bakery 2023-07-01 even though the bakery appears earlier in the feed than many other entries).
- Review extraction: "Watched on ..." means `null`; the We Live in Time item yields its review text.
- Merge idempotency and update-in-place, and that an RSS item merging onto a CSV entry keeps the CSV `tags`.
- `import_csv.py`: idempotent, liked and review joins (We Live in Time is liked, rewatch and reviewed).
- 0 parsed items causes a non-zero exit and an untouched file.

**Done when:** `pytest` is green with no network access.

### Task 4: GitHub Action (`.github/workflows/letterboxd.yml`)
- Triggers: `schedule` **once a week** (e.g. Monday 06:17 UTC: `17 6 * * 1`; GitHub cron is UTC and may run a few minutes late) plus `workflow_dispatch` for on-demand runs.
- `permissions: contents: write`. Add `concurrency` so runs don't overlap.
- Steps: checkout, setup-python, run tests, run the script, commit `_data/films.json` (and `assets/posters/` if Task 2) only if changed (`git diff --staged --quiet ||` pattern), then push. Pushing to `main` triggers the Pages build, so there is no extra deploy step.
- Env: `LETTERBOXD_USER` from a repo variable or the workflow default.
- Prerequisite: the current branch is `feature/letterboxd-rss`. The workflow only runs on the default branch, so it takes effect after merging to `main`.
- Note: GitHub may disable scheduled workflows after about 60 days without repo activity. A weekly run that finds nothing new makes no commit, so a quiet stretch could trigger this. Mention it in the README, keep `workflow_dispatch`, and optionally add a small keepalive step (e.g. an empty commit when the last commit is older than 50 days).

**Done when:** a manual run produces a commit once, and a second run produces none.

### Task 5: Frontend — DONE
Server-side Liquid, no `films.js`, no separate page.

- **Placement:** two expanders in "What I do as well", each directly after the sentence that introduces it. The Strava card ("Statues while running · Logged on Strava") follows the paragraph about runs and statues. The Films card ("Films · Logged on Letterboxd") follows "Since summer 2025 I've been logging the films I watch, more or less consistently." The word "cinema" is an `a[href="#films"]` link that opens and scrolls to the card. Nothing opens on page load (same rule as `#statues`).
- **Card** (`index.html`, `<details id="films" class="films-card">`): same shell as `.project-card` / `.strava-embed-wrap`, round thumbnail, `h3`, muted subline, chevron.
- **List:** a `max-height: 26rem` vertical scroll area (keyboard focusable) with every entry, newest first, grouped by year with sticky year labels (`group_by_exp`; relies on the store being sorted by `watched` desc). A sticky header row reads *Watch date · Film title (year) · Personal review*. Dates are `DD.MM.`.
- **Row** (`_includes/films-row.html`): date, title (links to Letterboxd) and year, ♥ liked, ↺ rewatch, stars (`4.5` as `★★★★½`, with `role="img"` and an `aria-label`). **Review text is never shown**: films with a written review get a small speech-bubble icon next to the stars. Tags are not shown.
- **Hero:** `assets/films/hero.svg`, an original yellow and black leopard-style pattern (the Locarno poster is copyrighted, so it is not used). A small footnote under the list says it is an own illustration inspired by the festival's 2021 look.
- No posters in the UI, no filters, no jump-to-year, no stats. Add only if the list feels long.
- Not verified in a browser by Claude (no Chrome available). Check with `bundle exec jekyll serve`.

### Task 6: One-time history backfill — DONE

**Why manual:** the RSS feed exposes only about 50 items and Letterboxd's API is closed to personal projects. The official export is the supported way to get the complete history, and it only needs to be done once. After that, the weekly delta keeps everything current.

**Human steps (about 2 minutes):**
1. On Letterboxd: Settings, then Import & Export, then "Export your data". Download the zip.
2. Unzip into a gitignored folder (`tmp/` or `import/`, both in `.gitignore` now; the export contains private data such as your email and watchlist, so never commit it).
3. Files needed: `diary.csv`, plus optionally `reviews.csv` (review text) and `likes/films.csv` (liked flag).

**Result:** `python3 scripts/import_csv.py tmp/letterboxd-…/` gave `129 rows, 129 new` from the export taken 2026-10-04 11:30 UTC; a second run is a no-op. 21 liked, 3 reviews, 9 rewatches, 0 unrated, oldest entry Mamma Mia! (watched 2009-07-30). `diary.csv` headers matched the expected ones, plus a `Tags` column that is stored. Rebuild rule: the importer only *fills missing* fields, so to pick up edits made on Letterboxd, delete `_data/films.json` and re-import (safe only while no RSS data has been merged in).

**Claude Code steps (as built):** `scripts/import_csv.py`.
- Verify the real column headers first. Expected for `diary.csv`: Date, Name, Year, Letterboxd URI, Rating, Rewatch, Tags, Watched Date. Don't hard-code assumptions that the files contradict.
- Map each diary row to an entry: `title`, `year`, `watched` (from Watched Date), `rating` (float or `null`), `rewatch` (Yes means true), `logged_at` (from Date), `media: "movie"`, `url` (the Letterboxd URI, or build the film URL if it is a short link), `poster: null`, `tmdb_id: null`.
- Join `reviews.csv` on title, year and watched date to fill `review`. Join the likes file on title and year to fill `liked`. Leave `review: null` and `liked: false` when there is no match.
- Use the same `id` scheme as the RSS importer so entries present in both sources merge instead of duplicating. **RSS data wins** for entries in both, because it has posters and TMDB ids; fill only missing fields from CSV.
- Idempotent: running it twice changes nothing the second time.
- Print a summary (`130 rows, 82 new, 0 filled, 48 already present`).
- Posters: CSV-only entries stay `poster: null` and show the placeholder card. Poster enrichment is optional (see below).

**Done when:** `_data/films.json` holds all logged entries (129, matching the profile) and the list reaches the oldest one. ✔

**Optional poster enrichment (ask the human first):** use the TMDB API to find a poster by title and year, with `TMDB_API_KEY` stored as a GitHub Actions secret and never in client code. It needs a free TMDB account. Not needed while the UI is text-first.

### Task 7 (optional): Stats strip
Films this year, average rating, rating distribution, computed client-side from the accumulated JSON.

## Edge cases to handle

- Unrated films (`memberRating` missing).
- Same film logged twice on different dates (distinct `id`s, both kept).
- Very long reviews and reviews with line breaks or quotes.
- Entries whose `watchedDate` is far in the past (backfill), so group by watch date, never by log date.
- Letterboxd temporarily down, so the Action fails and the site keeps serving the last good JSON.

## Data oddities to surface to the human

- *The Six Billion Dollar Man* was logged twice. Resolved on Letterboxd: the 2025-10-05 duplicate was deleted, the 2025-10-04 entry (logged 2026-10-04) remains. The importer never removes entries, so a deletion on Letterboxd needs a manual removal from `_data/films.json` (or a rebuild, see Task 6).
- The export also has `deleted/` and `orphaned/` folders. They are ignored on purpose.
- The `likes` file is per film, not per log, so a film logged twice shows ♥ on both rows.

## Open questions

Answered:
1. Site type: user site, `giuliazobrist.github.io`.
2. Placement: inside the text, each card after its sentence (see Task 5). No nav link.
3. Reviews: text hidden, icon only.
4. Posters: none, text-first.
6. CSV backfill: done.
7. Design references: `CONTEXT.md` and the `.project-card` pattern.

Answered:
9. `w-*` tags: kept in the data, risk owned by Giulia (see Decisions section above).

Still open:
5. Weekly run time (default Monday 06:17 UTC).
8. Letterboxd links: entries link to `boxd.it` short URLs. Fine, or resolve to full film URLs?

## Git plan

Branch: `feature/letterboxd-with-actions`. The UI, data and housekeeping (formerly steps 1 to 3) are already in `main` via PR #3.

Commits so far, one purpose each:
1. **Tooling:** `scripts/filmslib.py`, `scripts/import_csv.py`.
2. **Fixture:** `tests/fixtures/rss.xml` (snapshot of the live feed, 2026-10-04).
3. **Plan:** `PLAN.md`, `AGENTS.md` (tag decision).

Still to build, in this order, each as its own commit:
1. `scripts/update_films.py`: RSS delta merge (Task 1), including `guid` matching if approved.
2. `tests/test_films.py` (Task 3), offline, using the fixture.
3. `.github/workflows/letterboxd.yml` as a skeleton with `workflow_dispatch` only (runs tests and the script, no commit step).
4. Add the weekly `schedule` and the commit-and-push step (Task 4).

Then open the PR to `main`. The schedule only runs from the default branch, so after merging, trigger one manual run and confirm that it commits once, a second run commits nothing, and the live site rebuilds.

Never commit: `tmp/` (the Letterboxd export holds email, watchlist, profile) and `.vscode/` (both gitignored).

## Out of scope

Login or private data, writing back to Letterboxd, the official API, scraping HTML pages.
