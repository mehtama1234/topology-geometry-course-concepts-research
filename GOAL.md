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
- 77 generated HTML pages.
- 15 lecture-spine entries.
- 8 concept dependency paths.
- 5 proof-move recipes.
- 45 lecture-grounded examples.
- 1,090 lecture source-lens words.
- Four playground widgets.
- Course synthesis and reader-checks pages.

## Required Gates

Run:

```bash
python3 scripts/build_course.py
python3 scripts/validate_all.py
```

The validator must pass before claiming readiness.

## Remaining Human Risk

The main remaining risk is not structure. It is source nuance: auto-captions can mishear mathematics, and one video lacks recovered captions. Future improvement should be a human-read pass against the original lectures, especially around lecture 9's missing middle caption.
