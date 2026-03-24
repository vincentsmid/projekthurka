# Projekt Hůrka

Website for the indie band **Projekt Hůrka**.

## Adding concerts

Edit `concerts.md` in the root of this repo. Each concert is a block of key-value pairs separated by `---`.

### Format

```
date: YYYY-MM-DD
title: Concert name
venue: Venue name
city: City
time: HH:MM
price: e.g. 250 Kč or TBD
bands: Comma-separated list of bands
link: Optional URL for tickets
---
```

- `date` and `title` are required, everything else is optional.
- Concerts are automatically sorted by date.
- Past concerts are filtered out on the homepage; the nearest upcoming one is shown.

## Deployment

The site is deployed via GitHub Pages. On every push to `main`, a GitHub Actions workflow runs `build.py` which reads `concerts.md` and injects the concert data into the HTML files, then deploys to Pages.

To test the build locally:

```
python3 build.py
```
