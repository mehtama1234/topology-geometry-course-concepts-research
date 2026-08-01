# Goal: Topology & Geometry Course Companion

## Objective

Build a robotics-quality, first-principles companion for Tadashi Tokieda's Topology & Geometry course.

The reader should be able to understand the course without prior math vocabulary. Each page should start from the human problem, name the mathematical object, explain the operation performed on that object, and say why that operation works.

## Scope

- Recover all individual playlist links and caption coverage.
- Group the playlist into lectures.
- Build lecture explainers, concept pages, theme pages, subtheme pages, and method-family pages.
- Add whole-course synthesis surfaces.
- Add an interactive playground for the core mathematical moves.
- Keep source caveats explicit.
- Validate the generated site end to end.

## Writing Standard

- Plain everyday language.
- First principles before terminology.
- No vague praise or filler.
- No unexplained jargon.
- No assumptions about math, machine learning, benchmark, causal-inference, optimization, or systems background.
- Every important concept should answer:
  - what problem it solves;
  - what detail matters;
  - what mathematical principle is behind it;
  - where it reappears in the course.

## Current Completion Shape

- 35 playlist videos indexed.
- 15 lecture groups.
- 34 recovered caption files.
- 1 explicit missing-caption caveat: `nx1XOlezuvk`.
- 24 concepts.
- 6 themes.
- 10 subthemes.
- 5 method families.
- 92 generated HTML pages.
- 15 lecture-spine entries.
- 8 concept dependency paths.
- 5 proof-move recipes.
- 45 lecture-grounded examples.
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
- 8 theorem-use contracts.
- 1,271 theorem-contract words.
- 10 concept contrast pairs.
- 1,355 concept-contrast words.
- 8 transfer-lab cases.
- 1,187 transfer-lab words.
- 8 repair-clinic cases.
- 1,136 repair-clinic words.
- 7 oral-exam prompts.
- 875 oral-exam words.
- 10 change-ledger cases.
- 1,275 change-ledger words.
- 7,732 concept essay words.
- 2,746 concept workup words.
- 1,965 concept anchor words.
- 8,582 concept self-check words.
- 803 theme lens words.
- 2,353 theme answer-guide words.
- 1,110 subtheme routine words.
- 985 subtheme bridge words.
- 3,584 subtheme answer-guide words.
- 727 method-contract words.
- 711 method-playbook words.
- 2,258 method-family answer-guide words.
- 16 term translations.
- 1,850 term-translation words.
- 7 paper/source reader cards.
- 1,095 source-reader words.
- 7 paper-family ledger rows.
- 1,005 paper-family words.
- 15 source-nuance repair notes.
- 7 references across course sources, primary papers, and standard texts.
- 6 quality-rubric tests.
- 6 rubric-coverage layer maps.
- Four playground widgets.
- Course synthesis, transfer-lab, repair-clinic, oral-exam, change-ledger, reader-checks, term-translator, theorem-use-contracts, concept-contrasts, paper-source-reader, paper-family-ledger, lecture-source-bridges, lecture-reconstruction-drills, source-nuance-repairs, references, quality-rubric, and rubric-coverage pages.

## Required Gates

Run:

```bash
python3 scripts/build_course.py
python3 scripts/validate_all.py
```

The validator must pass before claiming readiness.

## Remaining Human Risk

The main remaining risk is not structure. The repo now has lecture-specific source-repair notes, but auto-captions can still mishear mathematics and one video lacks recovered captions. Future improvement should be a human-read pass against the original lectures, especially around lecture 9's missing middle caption.
