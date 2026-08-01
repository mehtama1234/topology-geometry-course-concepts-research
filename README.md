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
- 78 generated HTML pages in `site/`.
- 45 lecture-grounded examples, exactly three per lecture.
- 15 lecture-spine entries that name the object, question, legal move, surviving fact, and later use for every lecture.
- 5,333 lecture essay words, with every lecture essay now clearing the 300-word validator floor.
- 1,594 lecture deepening words across what-is-happening, why-hard, key-move, and payoff fields, with every field now clearing the 25-word validator floor.
- 1,986 lecture walkthrough words that slow each lecture down from starting object to mathematical payoff to reader check.
- 2,805 lecture reader-test words asking readers to explain the object, check the allowed move, and protect the conclusion.
- 2,860 lecture answer-guide words showing what strong self-check answers must contain.
- 1,492 caption-nuance words explaining risky auto-caption terms and safe mathematical readings by lecture.
- 1,645 lecture source-lens words explaining how transcript anchors should be read as evidence.
- 1,532 lecture source-checkpoint words across trust, overread warning, and math-question fields.
- 2,109 lecture source-faithfulness words separating caption support, course inference, and source caveats.
- Long-form first-principles essays for lectures, 24 concepts, themes, subthemes, and method families.
- 7,732 concept essay words, with every concept essay now clearing the 290-word validator floor.
- 2,746 concept workup words across object, operation, protected fact, and failure tests.
- 1,965 concept anchor words tying every concept to a concrete course moment, principle, and reader question.
- 9,387 concept self-check words showing what strong answers must include for the object, operation, protected fact, and failure condition.
- 1,963 theme essay words, with every theme essay now clearing the 300-word validator floor.
- 803 theme lens words across notices, ignored distractions, problem changes, and reader tests.
- 2,481 theme answer-guide words showing how to carry each theme across lectures.
- 2,761 subtheme essay words, with every subtheme essay now clearing the 260-word validator floor.
- 1,110 subtheme routine words across look-for, ask, use, and mistake fields.
- 985 subtheme bridge words tying recurring moves to course moments, thinking shifts, and reader tests.
- 3,784 subtheme answer-guide words showing how to apply each routine on a real page.
- 1,523 method-family essay words, with every method-family essay now clearing the 285-word validator floor.
- 727 method-contract words across input, action, protected evidence, output, and failure tests.
- 711 method-playbook words across setup, move, payoff, failure, and reader-test fields.
- 2,339 method-family answer-guide words showing what strong method explanations must include.
- A course-level synthesis page, a reader-checks page, a references page with 7 course/paper/text links, a quality audit, and a four-widget interactive math playground.

## Reader Surfaces

- `site/index.html` — starting point and source state.
- `site/lectures.html` and `site/lecture-*.html` — 15 lecture explainers with lecture deepening, slow walkthroughs, reader tests, answer guides, source checkpoints, source-faithfulness audits, and caption nuance.
- `site/lecture-spine.html` — one reasoning path through all lectures from object to later use.
- `site/concepts.html` and `site/concept-*.html` — concept atlas with reverse lecture links, anchor examples, work-from-scratch blocks, and self-check answer guides.
- `site/themes.html`, `site/subthemes.html`, `site/families.html` — cross-course idea maps, with theme lenses and answer guides, subtheme bridges, reading routines and answer guides, plus method playbooks, contracts, and answer guides.
- `site/the-math-why.html` — first-principles mathematical synthesis.
- `site/course-synthesis.html` — dependency spine across the whole course.
- `site/concept-dependencies.html` — eight prerequisite paths from early concepts to later theorem-level ideas.
- `site/proof-moves.html` — five reusable first-principles proof recipes with steps, failure modes, and course examples.
- `site/formula-reader.html` — plain readings of the course's central formulas and theorem statements.
- `site/math-playground.html` — interactive widgets for Euler characteristic, signed cancellation, fixed points, and vector-field index.
- `site/reader-checks.html` — eleven common reasoning failure checks.
- `site/references.html` — course, primary-paper, and standard-text links with lecture coverage, concept coverage, and source caveats.
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
- Required generated pages, including lecture spine, synthesis, concept dependencies, proof moves, formula reader, reader checks, references, playground, audits, lectures, concepts, themes, subthemes, and families.
- Minimum essay depth for lecture, lecture-deepening, lecture-walkthrough, lecture-reader-test, lecture-answer-guide, caption-nuance, source-lens, source-checkpoint, source-faithfulness, concept, concept-workup, concept-anchor, concept-self-check, theme, theme-lens, theme-answer-guide, subtheme, subtheme-routine, subtheme-bridge, subtheme-answer-guide, method-family, method-contract, method-playbook, method-family-answer-guide, and math-why layers.
- Lecture Deepening sections on every lecture page.
- Source-lens sections on every lecture page.
- Source Checkpoint sections on every lecture page.
- Source-Faithfulness Audit sections on every lecture page.
- Slow Walkthrough sections on every lecture page.
- Can You Explain It sections on every lecture page.
- Answer Guide sections on every lecture page.
- Caption Nuance sections on every lecture page and source-audit cards for every lecture, including caption support, course inference, and caveat fields.
- Anchor Example sections on every concept page.
- Work It From Scratch sections on every concept page.
- Can You Use It? self-check sections on every concept page.
- Theme Lens sections on every theme page.
- Can You Carry The Theme? answer-guide sections on every theme page.
- First-Principles Bridge sections on every subtheme page.
- Reading Routine sections on every subtheme page.
- Can You Apply The Routine? answer-guide sections on every subtheme page.
- Method Playbook sections on every method-family page.
- Method Contract sections on every method-family page.
- Can You Use This Method? answer-guide sections on every method-family page.
- Lecture-spine entries for all 15 lectures.
- Proof-move recipes with enough steps, explanations, failure modes, and examples.
- References layer with course, primary-paper, and standard-text links plus source caveats.
- At least three concrete lecture examples per lecture.
- Concept/theme/subtheme/family id integrity.
- No broken local links.
- No banned vague phrases in generated HTML.
