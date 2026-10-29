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
(standard library only, Python 3). In production a weekly GitHub Action runs it; locally you can
run it yourself to try it out.

The script needs one variable, `LETTERBOXD_USER` (your Letterboxd username). It is not hardcoded
anywhere. On GitHub it is the repository variable of the same name (Settings → Secrets and
variables → Actions → Variables); locally, pass it inline from the repo root:

```sh
LETTERBOXD_USER=<your username> python3 scripts/update_films.py   # e.g. "2 new, 0 updated, 48 unchanged"
git diff _data/films.json    # review what changed; git checkout _data/films.json undoes it
```

Good to know: running it twice changes nothing the second time; it only adds and updates
entries (a film deleted on Letterboxd must be removed from the JSON by hand); and the feed only
holds about 50 recent items, so the full history came from a one-time CSV export
(`scripts/import_csv.py`).

## Deploy

Push to `main` — GitHub Pages builds Jekyll natively (its own ``_site` version).

```sh
git add . && git commit -m "…" && git push
```
