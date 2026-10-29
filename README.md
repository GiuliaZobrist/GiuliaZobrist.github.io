# Personal website

Source for [giuliazobrist.github.io](https://giuliazobrist.github.io), a Jekyll site on GitHub Pages.

## Structure

- `index.html`, `blog.html` — pages with YAML front matter; share `_layouts/default.html`.
- `_posts/` — posts as `YYYY-MM-DD-slug.md`; `blog.html` renders each as an expandable row.
- `_layouts/post.html` — permalink page at `/blog/<slug>/` per post.
- `assets/` — static files. `_config.yml` — config.
- `_site/` — build output, regenerated automatically by Jekyll on every build /
  save. Never edit it by hand; changes there are overwritten. It is not the
  source of truth and does not need to be committed.

## Local preview

Front matter + Liquid mean that opening `index.html` directly shows only unstyled content. You need to build with Jekyll instead (and Ruby 3.x installed via brew, since macOS system Ruby is too old).

```sh
brew install ruby
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"   # add to ~/.zshrc
```

Then from the repo root:

```sh
bundle install
bundle exec jekyll serve --livereload  # http://localhost:4000, rebuilds on save
```
Hides build erros with
```sh
bundle exec jekyll serve --livereload 2>/dev/null
```

## Add a post

Create `_posts/YYYY-MM-DD-slug.md`:

```markdown
---
layout: post
title: "Your title here"
date: 2026-08-02
---

Body in markdown.
```

Newest sorts first and opens by default; older ones collapse.

## Update the films list (Letterboxd)

`_data/films.json` is filled from the public Letterboxd RSS feed by `scripts/update_films.py`
(standard library only, Python 3). A GitHub Action (`.github/workflows/letterboxd.yml`) runs it
and can also be started by hand from the repo's Actions tab; locally you can run it yourself.

The scripts need one variable, `LETTERBOXD_USER` (your Letterboxd username). It is not hardcoded
anywhere. Both `update_films.py` and `import_csv.py` read it the same way (`filmslib.require_user()`)
and exit with "LETTERBOXD_USER is not set" if it is missing.

- **On GitHub:** a repository *variable* (not a secret: the name is public, and secrets are masked
  in logs) under Settings → Secrets and variables → Actions → Variables. The workflow passes it
  to the script through `env:`.
- **Locally:** put it in a `.env` file in the repo root (gitignored, and Jekyll skips dotfiles):

  ```sh
  echo 'LETTERBOXD_USER=<your username>' > .env
  ```

  Load it into the current terminal session, then run from the repo root:

  ```sh
  set -a; source .env; set +a                  # once per terminal
  python3 scripts/update_films.py              # e.g. "2 new, 0 updated, 48 unchanged"
  git diff _data/films.json                    # review; git checkout _data/films.json undoes it
  ```

  Without a file, inline works too: `LETTERBOXD_USER=<name> python3 scripts/update_films.py`.

Tests (offline, standard library only, use the trimmed feed in `tests/fixtures/rss.xml`):

```sh
python3 -m unittest discover -s tests -v
```

Good to know: running the script twice changes nothing the second time; it only adds and updates
entries (a film deleted on Letterboxd must be removed from the JSON by hand); a like is never
removed by the feed; and the feed only holds about 50 recent items, so the full history came from
a one-time CSV export (`scripts/import_csv.py`, same variable).

## Deploy

Push to `main` — GitHub Pages builds Jekyll natively (its own ``_site` version).

```sh
git add . && git commit -m "…" && git push
```
