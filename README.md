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
- 77 generated HTML pages in `site/`.
- 45 lecture-grounded examples, exactly three per lecture.
- 15 lecture-spine entries that name the object, question, legal move, surviving fact, and later use for every lecture.
- 1,986 lecture walkthrough words that slow each lecture down from starting object to mathematical payoff to reader check.
- 979 caption-nuance words explaining risky auto-caption terms and safe mathematical readings by lecture.
- 1,090 lecture source-lens words explaining how transcript anchors should be read as evidence.
- Long-form first-principles essays for lectures, 24 concepts, themes, subthemes, and method families.
- 1,781 concept workup words across object, operation, protected fact, and failure tests.
- 858 subtheme routine words across look-for, ask, use, and mistake fields.
- A course-level synthesis page, a reader-checks page, a quality audit, and a four-widget interactive math playground.

## Reader Surfaces

- `site/index.html` — starting point and source state.
- `site/lectures.html` and `site/lecture-*.html` — 15 lecture explainers with slow walkthroughs and caption nuance.
- `site/lecture-spine.html` — one reasoning path through all lectures from object to later use.
- `site/concepts.html` and `site/concept-*.html` — concept atlas with reverse lecture links and work-from-scratch blocks.
- `site/themes.html`, `site/subthemes.html`, `site/families.html` — cross-course idea maps, with subtheme reading routines.
- `site/the-math-why.html` — first-principles mathematical synthesis.
- `site/course-synthesis.html` — dependency spine across the whole course.
- `site/concept-dependencies.html` — eight prerequisite paths from early concepts to later theorem-level ideas.
- `site/proof-moves.html` — five reusable first-principles proof recipes with steps, failure modes, and course examples.
- `site/formula-reader.html` — plain readings of the course's central formulas and theorem statements.
- `site/math-playground.html` — interactive widgets for Euler characteristic, signed cancellation, fixed points, and vector-field index.
- `site/reader-checks.html` — eleven common reasoning failure checks.
- `site/quality-audit.html` and `site/source-audit.html` — current validation evidence, source caveats, and per-lecture caption nuance.

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
- Required generated pages, including lecture spine, synthesis, concept dependencies, proof moves, formula reader, reader checks, playground, audits, lectures, concepts, themes, subthemes, and families.
- Minimum essay depth for lecture, lecture-walkthrough, caption-nuance, source-lens, concept, concept-workup, theme, subtheme, subtheme-routine, method-family, and math-why layers.
- Source-lens sections on every lecture page.
- Slow Walkthrough sections on every lecture page.
- Caption Nuance sections on every lecture page and source-audit cards for every lecture.
- Work It From Scratch sections on every concept page.
- Reading Routine sections on every subtheme page.
- Lecture-spine entries for all 15 lectures.
- Proof-move recipes with enough steps, explanations, failure modes, and examples.
- At least three concrete lecture examples per lecture.
- Concept/theme/subtheme/family id integrity.
- No broken local links.
- No banned vague phrases in generated HTML.
