# Topology & Geometry Course Concepts Research

This repo is a source-backed companion for Tadashi Tokieda's AIMS South Africa course, **Topology & Geometry**.

Playlist: https://www.youtube.com/playlist?list=PLTBqohhFNBE_09L0i-lf3fYXF5woAbrzJ

## Goal

Build a deep, plain-language treatment of the course across lectures, themes, subthemes, concepts, and method families. The writing starts from first principles: what problem the idea solves, what detail matters, why the mathematical principle is important, and how the ideas connect. It avoids assuming prior knowledge of mathematics, machine learning, benchmark language, causal inference, optimization, or systems language.

## Current State

- 35 playlist videos discovered.
- 15 lecture groups recovered from titles.
- 34 English auto-caption files recovered.
- 1 video currently reports no captions through `yt-dlp`: `nx1XOlezuvk`.
- Raw captions live in `raw-material/youtube/captions/`.
- Cleaned transcripts live in `raw-material/youtube/transcripts/`.
- 75 generated HTML pages in `site/`.
- 45 lecture-grounded examples, exactly three per lecture.
- 1,090 lecture source-lens words explaining how transcript anchors should be read as evidence.
- Long-form first-principles essays for lectures, 24 concepts, themes, subthemes, and method families.
- A course-level synthesis page, a reader-checks page, a quality audit, and a four-widget interactive math playground.

## Reader Surfaces

- `site/index.html` — starting point and source state.
- `site/lectures.html` and `site/lecture-*.html` — 15 lecture explainers.
- `site/concepts.html` and `site/concept-*.html` — concept atlas with reverse lecture links.
- `site/themes.html`, `site/subthemes.html`, `site/families.html` — cross-course idea maps.
- `site/the-math-why.html` — first-principles mathematical synthesis.
- `site/course-synthesis.html` — dependency spine across the whole course.
- `site/concept-dependencies.html` — eight prerequisite paths from early concepts to later theorem-level ideas.
- `site/formula-reader.html` — plain readings of the course's central formulas and theorem statements.
- `site/math-playground.html` — interactive widgets for Euler characteristic, signed cancellation, fixed points, and vector-field index.
- `site/reader-checks.html` — eleven common reasoning failure checks.
- `site/quality-audit.html` and `site/source-audit.html` — current validation evidence and source caveats.

## Readiness Docs

- `GOAL.md` — the long-term writing and build standard.
- `HANDOFF.md` — current state, commands, gotchas, and next work.
- `PARITY_AUDIT.md` — comparison against the robotics-quality companion shape, with evidence and remaining caveats.

## Commands

```bash
python3 scripts/build_course.py
python3 scripts/validate_all.py
python3 -m http.server 8790 --directory site
```

Then open:

```text
http://127.0.0.1:8790/
```

## Important Caveat

One playlist item still has no recovered captions: `nx1XOlezuvk`. The site preserves that caveat instead of pretending complete transcript coverage. Auto-captions should not be treated as exact mathematical text; they can mishear names, symbols, and short technical words.

## Readiness Gates

`scripts/validate_all.py` enforces the current quality shape:

- 35 videos, 15 lectures, at least 34 captioned videos.
- Required generated pages, including synthesis, concept dependencies, formula reader, reader checks, playground, audits, lectures, concepts, themes, subthemes, and families.
- Minimum essay depth for lecture, source-lens, concept, theme, subtheme, method-family, and math-why layers.
- Source-lens sections on every lecture page.
- At least three concrete lecture examples per lecture.
- Concept/theme/subtheme/family id integrity.
- No broken local links.
- No banned vague phrases in generated HTML.
