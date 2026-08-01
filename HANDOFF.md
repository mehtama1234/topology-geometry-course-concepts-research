# Handoff: Topology & Geometry Course Concepts Research

This repo is the source and generated static site for a first-principles companion to Tadashi Tokieda's AIMS South Africa course, Topology & Geometry.

## Where To Start

1. Read `README.md`.
2. Read `GOAL.md`.
3. Read `PARITY_AUDIT.md`.
4. Run `python3 scripts/validate_all.py`.
5. Serve the site with `python3 -m http.server 8790 --directory site`.
6. Open `http://127.0.0.1:8790/quality-audit.html`.

## Current State

- Branch: `main`.
- Remote: none configured in this local repo.
- Site directory: `site/`.
- Main generator: `scripts/build_course.py`.
- Validator: `scripts/validate_all.py`.
- Playlist: `https://www.youtube.com/playlist?list=PLTBqohhFNBE_09L0i-lf3fYXF5woAbrzJ`.
- Videos indexed: 35.
- Lecture groups: 15.
- Captioned videos: 34.
- Missing caption id: `nx1XOlezuvk`.
- HTML pages: 77.

## Main Reader Surfaces

- `index.html` — entry point and source state.
- `videos.html` — all individual YouTube links.
- `lectures.html`, `lecture-*.html` — lecture explainers with slow walkthroughs and caption nuance.
- `lecture-spine.html` — one reasoning path through all 15 lectures from object to later use.
- `concepts.html`, `concept-*.html` — concept atlas, reverse lecture appearances, and work-from-scratch blocks.
- `themes.html`, `subthemes.html`, `families.html` — recurring ideas, subtheme routines, and proof families.
- `the-math-why.html` — core mathematical reason the course works.
- `course-synthesis.html` — dependency spine and proof-family synthesis.
- `concept-dependencies.html` — prerequisite paths from early concepts to later theorem-level ideas.
- `proof-moves.html` — five reusable first-principles proof recipes with steps, failure modes, and examples.
- `formula-reader.html` — plain readings of central formulas and theorem statements.
- `math-playground.html` — four interactive canvas widgets.
- `reader-checks.html` — eleven common reasoning failure checks.
- `quality-audit.html` — generated readiness evidence.
- `source-audit.html` — caption/source caveats and per-lecture caption nuance.

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
- lecture, lecture-walkthrough, caption-nuance, source-lens, concept, concept-workup, theme, subtheme, subtheme-routine, family, and math-why depth floors;
- at least three concrete examples per lecture;
- lecture-spine structure for all 15 lectures;
- referential integrity across concepts, themes, subthemes, and families;
- playground page and four widget renderers;
- course synthesis structure;
- concept dependency structure;
- proof-move structure and length;
- source-lens sections on every lecture page;
- slow-walkthrough sections on every lecture page;
- caption-nuance sections on every lecture page and source-audit cards for every lecture;
- work-from-scratch sections on every concept page;
- reading-routine sections on every subtheme page;
- reader checks structure;
- broken local links;
- banned vague phrases in generated HTML.

## Current Quality Metrics

As of the current generated audit:

- 45 lecture examples.
- 15 lecture-spine entries.
- 3,855 lecture essay words.
- 1,986 lecture walkthrough words.
- 979 caption-nuance words.
- 1,090 lecture source-lens words.
- 4,830 concept essay words.
- 1,781 concept workup words.
- 1,278 theme essay words.
- 1,500 subtheme essay words.
- 858 subtheme routine words.
- 824 method-family essay words.
- 4 playground widgets.
- 8 synthesis sections.
- 8 concept dependency paths.
- 5 proof-move recipes.
- 11 reader checks.

## Local Readiness Evidence

- `python3 scripts/validate_all.py` passes.
- The local HTTP server has been checked at `http://127.0.0.1:8790/`.
- Desktop and mobile Chromium screenshots were checked for `math-playground.html`, `course-synthesis.html`, and `reader-checks.html`.
- The repo is clean on `main` after each committed pass.

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
