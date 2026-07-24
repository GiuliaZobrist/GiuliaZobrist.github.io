# Jekyll setup — run this on the new machine

The site was converted from plain static HTML to Jekyll so blog posts can be
written as markdown files. Everything is already committed; this doc is just
the local setup + how to verify it before pushing.

## What changed, in one paragraph

`index.html` and `blog.html` now have YAML front matter and share one
template, `_layouts/default.html` (nav/CSS/footer/scripts extracted from the
old `index.html`, byte-for-byte). Blog posts live in `_posts/` as markdown
files with `title`/`date` front matter; `blog.html` loops over `site.posts`
and renders each as an expandable `<details>` row (click title → full text
opens in place). Each post also gets an auto-generated permalink page at
`/blog/<slug>/` via `_layouts/post.html`, for future sharing — not linked
from anywhere yet, just there if you want it.

## 1. Install a real Ruby via Homebrew

The system Ruby on macOS is old (2.6) and too old for current Jekyll's
dependencies. Homebrew's Ruby fixes that:

```sh
brew install ruby
```

Add Homebrew's Ruby to your `PATH` *ahead of* the system one. Add this to
your `~/.zshrc` (adjust for Intel vs Apple Silicon — check `brew --prefix ruby`):

```sh
# Apple Silicon:
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
# Intel:
export PATH="/usr/local/opt/ruby/bin:$PATH"
```

Then open a new terminal and confirm:

```sh
which ruby        # should print the homebrew path, not /usr/bin/ruby
ruby -v            # should be 3.x
```

## 2. Install the site's gems

From the repo root:

```sh
cd /path/to/personal-website
bundle install
```

This reads the `Gemfile` (just `jekyll` + `webrick`) and installs into your
gem environment. No pinned versions needed on a modern Ruby — that was only
required to work around the old system Ruby.

## 3. Run it locally

```sh
bundle exec jekyll serve
```

Open `http://localhost:4000`. Check:

- `/` — homepage looks identical to before, nav now reads
  **About · Projects · Blog · Contact**, and the "Otherwise" paragraph ends
  with a "writing here" link.
- `/blog.html` — one entry ("Starting somewhere"), open by default, with two
  placeholder-free paragraphs. Click the title to collapse/expand it.
- Clicking "writing here" on `/` lands on `/blog.html`.
- Floating crab/triggerfish images and the (invisible, that's expected)
  sankey script still load without console errors.

`jekyll serve` watches files and rebuilds automatically — leave it running
while you edit.

## 4. Add a new post

Create a new file in `_posts/`, named `YYYY-MM-DD-slug.md`:

```markdown
---
layout: post
title: "Your title here"
date: 2026-08-02
---

Body text in plain markdown.
```

Save it, `blog.html` picks it up automatically (newest post sorts first,
open by default; older ones collapsed). No build step to remember beyond
having `jekyll serve` running while you check it, or `bundle exec jekyll
build` once before committing if you just want to double check the output
in `_site/`.

## 5. Deploy

This repo is `GiuliaZobrist.github.io`, so GitHub Pages already builds
Jekyll natively on every push to `main` — there's no GitHub Action to add
and no custom build step. GitHub Pages does **not** read the `Gemfile`; it
uses its own pinned Jekyll (the `github-pages` gem) server-side. Nothing
here uses a plugin outside Jekyll core, so there's no compatibility risk.

```sh
git add .
git commit -m "Add Jekyll setup and blog"
git push
```

Then check the repo's **Settings → Pages** section for the build status, or
just wait ~a minute and reload the live URL.

## Known gaps / things to revisit

- The first post's text is still a placeholder — replace the content in
  `_posts/2026-07-24-starting-somewhere.md` with the real entry.
- Per-post permalink pages (`/blog/<slug>/`) exist but aren't linked from
  the UI. Fine to leave as-is, or add a subtle permalink link in the
  `entry-meta` row in `blog.html` later if you want shareable post URLs.
- `Gemfile.lock` is gitignored (versions will differ once resolved on a
  modern Ruby vs. this machine's constrained one) — that's intentional, not
  an oversight.

Delete this file once you've run through it — it's a one-time setup note,
not ongoing documentation.
