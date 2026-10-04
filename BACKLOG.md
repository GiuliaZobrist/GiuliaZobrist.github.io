# Backlog

## Content

- [ ] Add links under the LaTeX and Genealogy tags in "Where my roots are" once relevant projects are public (e.g. genealogy tree repo, LaTeX templates). Tags are currently commented out in `index.html`.

## Learning / infra

- [ ] **optional (learning)**: Understand the `JEKYLL_ENV` difference between local and deploy. GitHub Pages' classic build sets `JEKYLL_ENV=production`; locally it defaults to `development`. Templates commonly guard analytics/tracking snippets with `{% if jekyll.environment == "production" %}` so they only load on the live site, not during local dev. Consequence: such snippets never render in a plain local `jekyll serve`, so to preview them run `JEKYLL_ENV=production bundle exec jekyll serve`. Worth checking whether this site adds any production-only snippets later (e.g. analytics).

## Strava

- [ ] **low priority**: Custom card to embed Strava iframe. How it works: at build time, a scheduled GitHub Action calls the API, writes `_data/runs.json`, a Liquid template renders it in the site's own type/palette. One-time: register a Strava app, run the OAuth handshake once, add repo secrets; the workflow must write Strava's rotating refresh token back to a secret each run. ~60 lines total. Only worth it if the design becomes annoying.

## GitHub projects

- [ ] **idea**: Automate listing my public GitHub projects instead of hand-writing them in `index.html`. 
(!) I tried to solve this issue already in my-skills with presentable-readme.
Approach (as in [Expedia Group's open source site](https://medium.com/expedia-group-tech/building-the-expedia-group-open-source-site-fbdb8764dfe9)): a scheduled GitHub Action queries the GitHub GraphQL API for repository info (name, description, topics, language, stars, last push), writes `_data/repos.json`, and a Liquid template renders it in the site's own style (reuse the `.project-card` pattern). Same fetch-commit-rebuild flow as the Letterboxd Action, so reuse its workflow shape. Decide first: which repos to include (e.g. an opt-in topic like `showcase`, or an allowlist in `_data/`), and exclude forks and archived repos. The built-in `GITHUB_TOKEN` is enough for public data, so no secrets to set up. 
