# TODO

## Content

- [ ] Add links under the LaTeX and Genealogy tags in "Where my roots are" once relevant projects are public (e.g. genealogy tree repo, LaTeX templates). Tags are currently commented out in `index.html`.

## Strava

- [ ] **low priority**: Custom card to embed Strava iframe. How it works: at build time, a scheduled GitHub Action calls the API, writes `_data/runs.json`, a Liquid template renders it in the site's own type/palette. One-time: register a Strava app, run the OAuth handshake once, add repo secrets; the workflow must write Strava's rotating refresh token back to a secret each run. ~60 lines total. Only worth it if the design becomes annoying.
