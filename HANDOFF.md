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
- HTML pages: 88.

## Main Reader Surfaces

- `index.html` — entry point and source state.
- `videos.html` — all individual YouTube links.
- `lectures.html`, `lecture-*.html` — lecture explainers with lecture deepening, slow walkthroughs, reader tests, answer guides, source checkpoints, source-faithfulness audits, and caption nuance.
- `lecture-spine.html` — one reasoning path through all 15 lectures from object to later use.
- `concepts.html`, `concept-*.html` — concept atlas, reverse lecture appearances, anchor examples, work-from-scratch blocks, and self-check answer guides.
- `themes.html`, `subthemes.html`, `families.html` — recurring ideas, theme lenses and answer guides, subtheme bridges, routines and answer guides, proof families, method playbooks, method contracts, and method answer guides.
- `the-math-why.html` — core mathematical reason the course works.
- `course-synthesis.html` — dependency spine and proof-family synthesis.
- `concept-dependencies.html` — prerequisite paths from early concepts to later theorem-level ideas.
- `transfer-lab.html` — eight everyday transfer cases that test object, allowed move, protected fact, wrong transfer, and course bridge.
- `proof-moves.html` — five reusable first-principles proof recipes with steps, failure modes, and examples.
- `formula-reader.html` — plain readings of central formulas and theorem statements.
- `theorem-use-contracts.html` — eight use contracts for central results and methods, with required object, allowed move, protected evidence, conclusion, break condition, and everyday test.
- `concept-contrasts.html` — ten contrast pairs that separate neighboring ideas readers often blur.
- `math-playground.html` — four interactive canvas widgets.
- `reader-checks.html` — eleven common reasoning failure checks.
- `term-translator.html` — 16 formal course words translated into everyday sentences, argument jobs, non-definition warnings, failure tests, reader questions, and concept links.
- `paper-source-reader.html` — seven course/paper/text sources explained as first-principles source families with reading questions and overread warnings.
- `lecture-source-bridges.html` — 15 lecture-level bridges from concrete demonstrations to source families, with overread warnings and reader questions.
- `lecture-reconstruction-drills.html` — 15 lecture rebuild drills with six steps each, self-checks, common failures, source checks, and concept links.
- `source-nuance-repairs.html` — 15 lecture-specific repair notes for caption hazards, safe claims, repair moves, do-not-claim guards, reviewer questions, and concept links.
- `references.html` — course, primary-paper, and standard-text links with source caveats and lecture/concept coverage.
- `quality-rubric.html` — six first-principles prose tests for object, legal move, protected fact, failure condition, course anchor, and everyday-language replacement.
- `rubric-coverage.html` — maps the six prose tests across lectures, concepts, themes, subthemes, method families, and source/quality pages.
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
- lecture, lecture-deepening, lecture-walkthrough, lecture-reader-test, lecture-answer-guide, caption-nuance, source-lens, source-checkpoint, source-faithfulness, concept, concept-workup, concept-anchor, concept-self-check, theme, theme-lens, theme-answer-guide, subtheme, subtheme-routine, subtheme-bridge, subtheme-answer-guide, family, method-contract, method-playbook, method-family-answer-guide, and math-why depth floors;
- at least three concrete examples per lecture;
- lecture-spine structure for all 15 lectures;
- referential integrity across concepts, themes, subthemes, and families;
- playground page and four widget renderers;
- course synthesis structure;
- concept dependency structure;
- transfer-lab structure, required case set, field depth, and concept-link integrity;
- proof-move structure and length;
- theorem-use-contract structure, required result set, field depth, and concept-link integrity;
- concept-contrast structure, required contrast set, field depth, and concept-link integrity;
- source-lens sections on every lecture page;
- lecture-deepening sections on every lecture page;
- source-checkpoint sections on every lecture page;
- source-faithfulness audit sections on every lecture page;
- lecture-source-bridges structure, field depth, reference integrity, and concept-link integrity;
- lecture-reconstruction-drills structure, six-step coverage, field depth, and concept-link integrity;
- source-nuance-repairs structure, field depth, and concept-link integrity;
- slow-walkthrough sections on every lecture page;
- can-you-explain-it reader-test sections on every lecture page;
- answer-guide sections on every lecture page;
- caption-nuance sections on every lecture page and source-audit cards for every lecture, including caption support, course inference, and caveat fields;
- anchor-example sections on every concept page;
- work-from-scratch sections on every concept page;
- can-you-use-it self-check sections on every concept page;
- theme-lens sections on every theme page;
- can-you-carry-the-theme answer-guide sections on every theme page;
- first-principles-bridge sections on every subtheme page;
- reading-routine sections on every subtheme page;
- can-you-apply-the-routine answer-guide sections on every subtheme page;
- method-playbook sections on every family page;
- method-contract sections on every family page;
- can-you-use-this-method answer-guide sections on every family page;
- reader checks structure;
- term-translator structure, field depth, required term set, and concept-link integrity;
- paper-source-reader structure, field depth, full reference coverage, and concept-link integrity;
- references layer structure and page content;
- quality-rubric structure and page content;
- rubric-coverage structure and page content;
- broken local links;
- banned vague phrases in generated HTML.

## Current Quality Metrics

As of the current generated audit:

- 45 lecture examples.
- 15 lecture-spine entries.
- 5,333 lecture essay words.
- 1,594 lecture deepening words.
- 1,986 lecture walkthrough words.
- 2,805 lecture reader-test words.
- 2,657 lecture answer-guide words.
- 1,492 caption-nuance words.
- 1,645 lecture source-lens words.
- 1,532 lecture source-checkpoint words.
- 2,109 lecture source-faithfulness words.
- 1,734 source-nuance repair words.
- 4,206 lecture-source bridge words.
- 6,460 lecture reconstruction words.
- 7,732 concept essay words.
- 2,746 concept workup words.
- 1,965 concept anchor words.
- 8,582 concept self-check words.
- 1,963 theme essay words.
- 803 theme lens words.
- 2,353 theme answer-guide words.
- 2,761 subtheme essay words.
- 1,110 subtheme routine words.
- 985 subtheme bridge words.
- 3,584 subtheme answer-guide words.
- 1,523 method-family essay words.
- 727 method-contract words.
- 711 method-playbook words.
- 2,258 method-family answer-guide words.
- 4 playground widgets.
- 8 synthesis sections.
- 8 concept dependency paths.
- 8 transfer-lab cases.
- 1,187 transfer-lab words.
- 5 proof-move recipes.
- 8 theorem-use contracts.
- 1,271 theorem-contract words.
- 10 concept contrast pairs.
- 1,355 concept-contrast words.
- 11 reader checks.
- 16 term translations.
- 1,850 term-translation words.
- 7 paper/source reader cards.
- 1,095 source-reader words.
- 15 source-nuance repair notes.
- 7 references.
- 6 quality-rubric tests.
- 6 rubric-coverage layer maps.

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

The structure is now strong and includes source-repair notes. The highest-value future work is still a human source pass against original lecture videos, especially any point where auto-captions may have garbled mathematical terminology.
