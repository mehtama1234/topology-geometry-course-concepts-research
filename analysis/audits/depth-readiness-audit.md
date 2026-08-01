# Depth Readiness Audit

This repo now has a transcript-backed depth pass across the lecture, concept, theme, subtheme, and method-family layers. The first shallow layer has been replaced across the main explanatory surfaces:

- 15 hand-authored lecture explainers from 35 videos
- lecture-spine.html with 15 lecture-by-lecture reasoning entries
- 1594 lecture deepening words across what-is-happening, why-hard, key-move, and payoff fields
- 1986 slow-walkthrough words across lecture pages, explaining each lecture from object to payoff to reader check
- 2805 lecture reader-test words asking the reader to explain the object, check the allowed move, and protect the conclusion
- 2657 lecture answer-guide words showing what a strong self-check answer must contain
- 1492 caption-nuance words across lecture pages and source audit, explaining risky transcript terms and safe readings
- 1645 source-lens words across lecture pages, explaining how transcript anchors should be read as evidence
- 1532 source-checkpoint words across lecture trust, overread-warning, and math-question fields
- 2338 source-faithfulness words separating caption support, course inference, and source caveats on lecture pages and source audit cards
- 1734 source-nuance repair words across 15 lecture-specific repair notes
- 45 lecture-grounded examples, three per lecture, each bridged to concepts
- 24 expanded concept pages with full essay sections, why-it-exists, beginner-trap, and course-role sections
- 2746 concept workup words across object, operation, protected-fact, and failure-test fields
- 1965 concept anchor words across course-moment, principle, and reader-question fields
- 8582 concept self-check words showing what a strong answer must include for the object, operation, protected fact, and failure condition
- 6 expanded course theme pages with problem, habit, course-arc, and important-detail sections
- 803 theme lens words across notices, ignores, problem-change, and reader-test fields
- 2353 theme answer-guide words showing how to carry a theme across lectures
- 10 expanded subtheme pages with essay, first-principles, and course-role sections
- 1110 subtheme routine words across look-for, ask, use, and mistake fields
- 985 subtheme bridge words across course-moment, thinking-shift, and reader-test fields
- 3628 subtheme answer-guide words showing how to apply the routine on a real page
- 5 expanded method-family pages with essay, human-problem, how-it-works, examples, and failure-mode sections
- 797 method-contract words across input, action, protected-evidence, output, and failure-test fields
- 738 method-playbook words across setup, move, payoff, failure, and reader-test fields
- 2385 method-family answer-guide words showing what a strong method explanation must include
- math-playground.html with four interactive first-principles canvas widgets
- course-synthesis.html with the full dependency spine and proof-family synthesis
- concept-dependencies.html with 8 prerequisite paths linking early ideas to later theorem-level ideas
- transfer-lab.html with 8 everyday transfer cases and 1187 transfer words
- repair-clinic.html with 8 flawed explanations repaired into first-principles versions and 1155 repair-clinic words
- oral-exam.html with 7 final readiness prompts and 899 oral-exam words
- change-ledger.html with 10 change-versus-survival cases and 1275 change-ledger words
- assumption-ledger.html with 10 hidden-assumption cases and 1363 assumption-ledger words
- counterexample-gallery.html with 10 failure scenes and 1053 counterexample words
- weak-claim-repairs.html with 10 shallow claims repaired into first-principles explanations and 1174 repair words
- proof-moves.html with 5 reusable proof recipes
- concept-contrasts.html with 10 contrast pairs and 1355 contrast words separating ideas readers often blur
- source-nuance-repairs.html with 15 lecture-specific source repair notes that state caption hazards, safe claims, repair moves, do-not-claim guards, and reviewer questions
- reader-checks.html with eleven concrete checks for common reasoning failures
- term-translator.html with 16 formal course words translated into everyday sentences, argument jobs, failure tests, reader questions, and concept links
- paper-family-ledger.html with 7 paper/source family contracts and 1180 paper-family words
- references.html with 7 course, primary-paper, and standard-text links, each with source caveats and lecture/concept coverage
- quality-rubric.html with 6 prose tests for object, legal move, protected fact, failure condition, course anchor, and plain-language replacement
- rubric-coverage.html with 6 layer maps showing where those tests are satisfied
- explicit source coverage, missing-caption audit, per-lecture caption-nuance cards, and source-faithfulness audits

Current enforced essay totals: 5333 lecture essay words, 1594 lecture deepening words, 1986 lecture walkthrough words, 2805 lecture reader-test words, 2657 lecture answer-guide words, 1492 caption-nuance words, 1645 source-lens words, 1532 source-checkpoint words, 2338 source-faithfulness words, 1734 source-nuance repair words, 1187 transfer-lab words, 1155 repair-clinic words, 899 oral-exam words, 1275 change-ledger words, 1363 assumption-ledger words, 1053 counterexample words, 1174 weak-claim repair words, 1180 paper-family words, 7732 concept essay words, 2746 concept workup words, 1965 concept anchor words, 8582 concept self-check words, 1355 concept-contrast words, 1963 theme essay words, 803 theme lens words, 2353 theme answer-guide words, 3009 subtheme essay words, 1110 subtheme routine words, 985 subtheme bridge words, 3628 subtheme answer-guide words, 1667 method-family essay words, 797 method-contract words, 738 method-playbook words, and 2385 method-family answer-guide words. The validator requires every lecture essay to clear 300 words, every lecture deepening field to clear 25 words, every lecture walkthrough field to clear 35 words, every lecture reader-test field to clear 35 words, every lecture answer-guide field to clear 30 words, every lecture caption-nuance field to clear 25 words, every lecture source lens to clear 100 words, every lecture source-checkpoint field to clear 25 words, every lecture source-faithfulness field to clear 35 words, every source-nuance repair field to clear 14 words, every transfer-lab field to clear 14 words, every repair-clinic field to clear 14 words, every oral-exam field to clear 14 words, every change-ledger field to clear 14 words, every assumption-ledger field to clear 14 words, every counterexample field to clear 14 words, every weak-claim repair field to clear 14 words, every paper-family field to clear 14 words, every concept essay to clear 290 words, every concept workup field to clear 25 words, every concept anchor field to clear 25 words, every concept self-check field to clear 40 words, every concept contrast field to clear 14 words, every theme essay to clear 300 words, every theme lens field to clear 25 words, every theme answer-guide field to clear 40 words, every subtheme essay to clear 260 words, every subtheme routine field to clear 25 words, every subtheme bridge field to clear 25 words, every subtheme answer-guide field to clear 40 words, every method-family essay to clear 285 words, every method-contract field to clear 25 words, every method-playbook field to clear 25 words, and every method-family answer-guide field to clear 40 words.

The remaining depth gap is qualitative rather than structural: future work should do periodic human-read passes against the original captions and improve any page whose explanation feels compressed, under-specific, or too far from a concrete lecture moment. The validator now checks that concept themes, concept subthemes, and method-family concept ids point to real objects, and every lecture must carry at least three concrete examples.
