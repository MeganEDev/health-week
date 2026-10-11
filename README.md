# Week

A Monday–Sunday page showing the day's meals and training. Mobile-first, works offline,
installs to the iPhone home screen with its own icon.

```
data/plan.json      ← all content lives here. This is the file you edit.
src/template.html   ← the UI. Layout, styling, behaviour.
tools/make_icon.py  ← generates the app icon
build.py            ← inlines the data + icon into one self-contained file
docs/index.html     ← the built page. Don't edit; it's overwritten.
dev.sh              ← rebuild and serve on localhost
```

## Changing the plan

Edit `data/plan.json`, then:

```sh
python3 build.py
```

That's the whole loop. The build fails loudly with a line and column number if the JSON
is malformed, so a stray comma can't silently break the page.

Nothing about the content is hard-coded in the UI — days, meals, recipes, workouts,
shopping and the week's cook pattern are all read from the JSON. Add a seventh superset
or a tenth meal and it renders.

### Structure

- `mealKey` — every meal by id. Add a `recipe` block and the meal gets a chevron
  through to its own page. Leave it out and it's assembly-only.
- `week` — the seven days. `lunchFrom` marks a lunch as leftovers; `cookTonight`
  marks the dinner that gets batch-cooked for four.
- `workouts` — supersets, reps, loads. `swap` on an exercise records what it replaced
  and why; `note` on a workout explains a change at the top of the day.
- `shopping` — grouped list, one week.

## Running it on the laptop

```sh
./dev.sh          # rebuild, serve on :8000, open the browser
```

Or just `open docs/index.html` — the page is entirely self-contained, so a `file://`
URL works for everything except the service worker.

## Getting it on the iPhone

**The Files app route does not work.** Tapping an HTML file in Files opens it in Quick Look,
which renders CSS but does not execute JavaScript — you'd get an empty page. This was tested,
not assumed. The same applies to a Shortcut that Quick Looks the file.

What works is a URL plus Safari's **Add to Home Screen**. The page declares
`apple-mobile-web-app-capable`, an `apple-touch-icon`, and a service worker, so once installed
it launches fullscreen with no Safari chrome and works with no signal.

### This site is on GitHub Pages

The repo serves the `docs/` folder from `main`. That's why the build writes there rather than
to `dist/` — Pages can only serve from the repo root or `/docs`, not an arbitrary folder.

To install on the phone: open the Pages URL in **Safari** (not Chrome — only Safari can add to
the home screen), tap Share, scroll to **Add to Home Screen**.

Open it from the icon afterwards, not from Safari. A home-screen web app gets its own storage
container on iOS, so shopping-list ticks made in Safari won't appear in the installed app and
vice versa.

### Publishing a change

```sh
python3 build.py
git add -A && git commit -m "update plan" && git push
```

Pages redeploys in under a minute. The service worker cache name is a hash of the build, so
the new version replaces the old one cleanly instead of a stale copy getting stuck.
