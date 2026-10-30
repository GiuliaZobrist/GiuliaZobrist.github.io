# Backlog

## Open

- [ ] Add links under the LaTeX and Genealogy tags in "Where my roots are" once relevant projects are public (e.g. genealogy tree repo, LaTeX templates).

## Depolyment

- [ ] **optional (learning)**: Understand the `JEKYLL_ENV` difference between local and deploy. GitHub Pages' classic build sets `JEKYLL_ENV=production`; locally it defaults to `development`. Templates commonly guard analytics/tracking snippets with `{% if jekyll.environment == "production" %}` so they only load on the live site, not during local dev. Consequence: such snippets never render in a plain local `jekyll serve`, so to preview them run `JEKYLL_ENV=production bundle exec jekyll serve`. Worth checking whether this site adds any production-only snippets later (e.g. analytics).
Another option is to try to create a Docker file and run it "as if" on Github Pages but locally.
## Strava

- [ ] **low priority**: Custom card to embed Strava iframe. How it works: at build time, a scheduled GitHub Action calls the API, writes `_data/runs.json`, a Liquid template renders it in the site's own type/palette. One-time: register a Strava app, run the OAuth handshake once, add repo secrets; the workflow must write Strava's rotating refresh token back to a secret each run. ~60 lines total. Only worth it if the design becomes annoying.

## GitHub projects

- [ ] **idea**: Automate listing my public GitHub projects instead of hand-writing them in `index.html`. 
(!) I tried to solve this issue already in my-skills with presentable-readme.
Approach (as in [Expedia Group's open source site](https://medium.com/expedia-group-tech/building-the-expedia-group-open-source-site-fbdb8764dfe9)): a scheduled GitHub Action queries the GitHub GraphQL API for repository info (name, description, topics, language, stars, last push), writes `_data/repos.json`, and a Liquid template renders it in the site's own style (reuse the `.project-card` pattern). Same fetch-commit-rebuild flow as the Letterboxd Action, so reuse its workflow shape. Decide first: which repos to include (e.g. an opt-in topic like `showcase`, or an allowlist in `_data/`), and exclude forks and archived repos. The built-in `GITHUB_TOKEN` is enough for public data, so no secrets to set up. 

## Project cards (follow-up to `_data/projects.yml`)

Cards now render from `_data/projects.yml` via `_includes/project-card.html` (content only in YAML, markup once). Two follow-ups:

- [ ] **Scheduled Action for repo metadata**: a workflow (cron + manual dispatch, same fetch-commit shape as the Letterboxd one) queries the GitHub GraphQL API with the built-in `GITHUB_TOKEN` for the repos listed in `projects.yml` (match on `repo`), writes `_data/repos.json` (stars, primary language, last push, archived flag, topics), and commits only if it changed. `project-card.html` then looks up the matching entry and shows e.g. language and last-updated next to the link. `projects.yml` stays the curated source (images, bullets, wording); `repos.json` is script-owned and never hand-edited. Decide first: show stars or not, and what to do if a repo is private or deleted (skip metadata, keep the card). This supersedes the "Automate listing my public GitHub projects" idea above.
