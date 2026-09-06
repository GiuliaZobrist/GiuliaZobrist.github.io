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

## Deploy

Push to `main` — GitHub Pages builds Jekyll natively (its own ``_site` version).

```sh
git add . && git commit -m "…" && git push
```
