# Handoff: Topology & Geometry Course Concepts Research

This repo is the source and generated static site for a first-principles companion to Tadashi Tokieda's AIMS South Africa course, Topology & Geometry.

## Where To Start

1. Read `README.md`.
2. Read `GOAL.md`.
3. Run `python3 scripts/validate_all.py`.
4. Serve the site with `python3 -m http.server 8790 --directory site`.
5. Open `http://127.0.0.1:8790/quality-audit.html`.

## Current State

- Branch: `main`.
- Site directory: `site/`.
- Main generator: `scripts/build_course.py`.
- Validator: `scripts/validate_all.py`.
- Playlist: `https://www.youtube.com/playlist?list=PLTBqohhFNBE_09L0i-lf3fYXF5woAbrzJ`.
- Videos indexed: 35.
- Lecture groups: 15.
- Captioned videos: 34.
- Missing caption id: `nx1XOlezuvk`.
- HTML pages: 65.

## Main Reader Surfaces

- `index.html` — entry point and source state.
- `videos.html` — all individual YouTube links.
- `lectures.html`, `lecture-*.html` — lecture explainers.
- `concepts.html`, `concept-*.html` — concept atlas and reverse lecture appearances.
- `themes.html`, `subthemes.html`, `families.html` — recurring ideas and proof families.
- `the-math-why.html` — core mathematical reason the course works.
- `course-synthesis.html` — dependency spine and proof-family synthesis.
- `math-playground.html` — four interactive canvas widgets.
- `reader-checks.html` — common reasoning failure checks.
- `quality-audit.html` — generated readiness evidence.
- `source-audit.html` — caption/source caveats.

## Build And Validation

Use:

```bash
python3 scripts/build_course.py
python3 scripts/validate_all.py
```

The build regenerates JSON analysis files, markdown audits, CSS, JS, and all HTML pages. Do not hand-edit generated files unless you intend to port the change back into `scripts/build_course.py`.

## Validation Gates

`scripts/validate_all.py` checks:

- exact expected video and lecture counts;
- caption coverage and missing-caption caveat;
- required page existence;
- lecture, concept, theme, subtheme, family, and math-why depth floors;
- at least three concrete examples per lecture;
- referential integrity across concepts, themes, subthemes, and families;
- playground page and four widget renderers;
- course synthesis structure;
- reader checks structure;
- broken local links;
- banned vague phrases in generated HTML.

## Current Quality Metrics

As of the current generated audit:

- 45 lecture examples.
- 3,855 lecture essay words.
- 3,207 concept essay words.
- 1,278 theme essay words.
- 1,500 subtheme essay words.
- 824 method-family essay words.
- 4 playground widgets.
- 8 synthesis sections.
- 10 reader checks.

## Source Caveats

`nx1XOlezuvk` currently has no recovered captions. Lecture 9 preserves this caveat visibly. Auto-captions are source material, not exact mathematical text.

## Common Gotchas

- Do not weaken validation to pass a shallow page. Improve the generated content instead.
- Do not add prose only to `site/*.html`; edits will be overwritten by `scripts/build_course.py`.
- Avoid banned vague phrases. The validator scans generated HTML.
- Keep links local and valid; the validator checks them.
- If adding a new page, add it to nav, homepage if appropriate, quality/readiness audits, and validation.
- If changing ids, update every concept/theme/subtheme/family reference and rerun validation.

## Suggested Next Work

The structure is now strong. The highest-value future work is a source-nuance pass against original lecture videos, especially any point where auto-captions may have garbled mathematical terminology.
