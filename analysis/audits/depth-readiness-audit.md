# Depth Readiness Audit

This repo now has a transcript-backed depth pass across the lecture, concept, theme, subtheme, and method-family layers. The first shallow layer has been replaced across the main explanatory surfaces:

- 15 hand-authored lecture explainers from 35 videos
- 1090 source-lens words across lecture pages, explaining how transcript anchors should be read as evidence
- 45 lecture-grounded examples, three per lecture, each bridged to concepts
- 24 expanded concept pages with full essay sections, why-it-exists, beginner-trap, and course-role sections
- 6 expanded course theme pages with problem, habit, course-arc, and important-detail sections
- 10 expanded subtheme pages with essay, first-principles, and course-role sections
- 5 expanded method-family pages with essay, human-problem, how-it-works, examples, and failure-mode sections
- math-playground.html with four interactive first-principles canvas widgets
- course-synthesis.html with the full dependency spine and proof-family synthesis
- concept-dependencies.html with 8 prerequisite paths linking early ideas to later theorem-level ideas
- reader-checks.html with eleven concrete checks for common reasoning failures
- explicit source coverage and missing-caption audit

Current enforced essay totals: 3855 lecture essay words, 1090 source-lens words, 4830 concept essay words, 1278 theme essay words, 1500 subtheme essay words, and 824 method-family essay words. The validator requires every lecture essay to clear 230 words, every lecture source lens to clear 60 words, every concept essay to clear 180 words, every theme essay to clear 190 words, every subtheme essay to clear 130 words, and every method-family essay to clear 130 words.

The remaining depth gap is qualitative rather than structural: future work should do periodic human-read passes against the original captions and improve any page whose explanation feels compressed, under-specific, or too far from a concrete lecture moment. The validator now checks that concept themes, concept subthemes, and method-family concept ids point to real objects, and every lecture must carry at least three concrete examples.
