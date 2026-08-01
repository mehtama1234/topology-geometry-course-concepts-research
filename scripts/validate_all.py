#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "analysis" / "course" / "course-companion.json"

FORBIDDEN = [
    "cutting-edge",
    "game-changing",
    "deep dive",
    "unlock",
    "leverage",
    "robust",
    "seamless",
    "paradigm",
    "state-of-the-art",
    "template",
    "hand-wave",
    "magic",
    "clever",
    "trick",
    "interesting",
    "pretty",
    "zoo",
]


def words(s):
    return re.findall(r"[A-Za-z0-9']+", s or "")


def fail(msg):
    raise SystemExit(f"validation failed: {msg}")


def main():
    if not DATA.exists():
        fail("course-companion.json missing; run scripts/build_course.py")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    stats = data["stats"]
    if stats["videos"] != 35:
        fail(f"expected 35 videos, got {stats['videos']}")
    if stats["lectures"] != 15:
        fail(f"expected 15 lectures, got {stats['lectures']}")
    if stats["captioned_videos"] < 34:
        fail(f"expected at least 34 captioned videos, got {stats['captioned_videos']}")
    if stats["concepts"] < 16:
        fail("concept map too small")
    if stats["themes"] < 6 or stats["subthemes"] < 10 or stats["families"] < 5:
        fail("theme/subtheme/family coverage too small")

    quality_rubric = data.get("quality_rubric") or []
    expected_rubric_ids = {
        "object-before-name",
        "legal-move",
        "protected-fact",
        "failure-condition",
        "course-anchor",
        "plain-language-replacement",
    }
    if {item.get("id") for item in quality_rubric} != expected_rubric_ids:
        fail("quality rubric ids do not match required first-principles tests")
    for item in quality_rubric:
        if len(words(item.get("title"))) < 3:
            fail(f"quality rubric {item.get('id')} title too thin")
        for field in ["test", "strong_answer", "failure", "repair"]:
            if len(words(item.get(field))) < 8:
                fail(f"quality rubric {item.get('id')} {field} too thin")

    rubric_coverage = data.get("rubric_coverage") or []
    if len(rubric_coverage) < 6:
        fail("rubric coverage needs six layer maps")
    for row in rubric_coverage:
        coverage = row.get("coverage") or {}
        if set(coverage) != expected_rubric_ids:
            fail(f"rubric coverage {row.get('layer')} does not cover all rubric ids")
        if len(words(row.get("reader_test"))) < 20:
            fail(f"rubric coverage {row.get('layer')} reader test too thin")
        for rubric_id, evidence in coverage.items():
            if len(words(evidence)) < 5:
                fail(f"rubric coverage {row.get('layer')} {rubric_id} too thin")

    term_concept_ids = {concept["id"] for concept in data["concepts"]}
    term_translations = data.get("term_translations") or []
    if len(term_translations) < 16:
        fail("term translations layer needs at least sixteen terms")
    required_terms = {
        "Topology",
        "Geometry",
        "Invariant",
        "Deformation",
        "Quotient space",
        "Product space",
        "Manifold",
        "Generic position",
        "Orientation",
        "Euler characteristic",
        "Parity",
        "Intersection number",
        "Fixed point",
        "Configuration space",
        "Vector-field index",
        "Poincare-Hopf theorem",
    }
    if {row.get("term") for row in term_translations} != required_terms:
        fail("term translations do not match required first-principles term set")
    for row in term_translations:
        for field in ["everyday_sentence", "job_in_argument", "not_a_definition", "failure_if_misread"]:
            if len(words(row.get(field))) < 14:
                fail(f"term translation {row.get('term')} {field} too thin")
        if len(words(row.get("reader_question"))) < 8:
            fail(f"term translation {row.get('term')} reader question too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"term translation {row.get('term')} needs three concept links")
        missing = sorted(set(row.get("concepts") or []) - term_concept_ids)
        if missing:
            fail(f"term translation {row.get('term')} references unknown concept ids: {missing}")

    math_why = data.get("math_why") or {}
    for field in ["big_picture", "first_principles", "important_detail", "principle", "concepts_matter", "reader_path"]:
        if len(words(math_why.get(field))) < 45:
            fail(f"math_why {field} too thin")

    quality_audit = data.get("quality_audit") or {}
    if len(words(quality_audit.get("summary"))) < 20:
        fail("quality audit summary too thin")
    if len(quality_audit.get("requirements") or []) < 7:
        fail("quality audit needs requirement evidence")
    for item in quality_audit.get("requirements", []):
        if item.get("status") not in {"met", "met-with-caveat"}:
            fail(f"quality audit invalid status: {item.get('status')}")
        if len(words(item.get("evidence"))) < 10:
            fail(f"quality audit evidence too thin: {item.get('requirement')}")

    for theme in data["themes"]:
        depth = theme.get("depth") or {}
        for field in ["problem", "habit", "course_arc", "important_detail"]:
            if len(words(depth.get(field))) < 40:
                fail(f"theme {theme['id']} depth {field} too thin")
        if len(depth.get("lectures") or []) < 4:
            fail(f"theme {theme['id']} needs lecture thread")
        theme_essay_words = sum(len(words(p)) for p in theme.get("essay") or [])
        if theme_essay_words < 300:
            fail(f"theme {theme['id']} essay too thin")
        lens = theme.get("lens") or {}
        for field in ["notices", "ignores", "changes_problem", "reader_test"]:
            if len(words(lens.get(field))) < 25:
                fail(f"theme {theme['id']} lens {field} too thin")
        answer_guide = theme.get("answer_guide") or {}
        for field in ["notice_answer", "ignore_answer", "transfer_answer", "test_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"theme {theme['id']} answer guide {field} too thin")

    for subtheme in data["subthemes"]:
        depth = subtheme.get("depth") or {}
        for field in ["problem", "first_principles", "course_role"]:
            if len(words(depth.get(field))) < 30:
                fail(f"subtheme {subtheme['id']} depth {field} too thin")
        subtheme_essay_words = sum(len(words(p)) for p in subtheme.get("essay") or [])
        if subtheme_essay_words < 260:
            fail(f"subtheme {subtheme['id']} essay too thin")
        routine = subtheme.get("routine") or {}
        for field in ["look_for", "ask", "use", "mistake"]:
            if len(words(routine.get(field))) < 25:
                fail(f"subtheme {subtheme['id']} routine {field} too thin")
        bridge = subtheme.get("bridge") or {}
        for field in ["course_moment", "thinking_shift", "reader_test"]:
            if len(words(bridge.get(field))) < 25:
                fail(f"subtheme {subtheme['id']} bridge {field} too thin")
        answer_guide = subtheme.get("answer_guide") or {}
        for field in ["look_answer", "ask_answer", "use_answer", "mistake_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"subtheme {subtheme['id']} answer guide {field} too thin")

    for family in data["families"]:
        depth = family.get("depth") or {}
        for field in ["human_problem", "first_principles", "how_it_works", "course_examples", "failure_mode"]:
            if len(words(depth.get(field))) < 35:
                fail(f"family {family['id']} depth {field} too thin")
        family_essay_words = sum(len(words(p)) for p in family.get("essay") or [])
        if family_essay_words < 285:
            fail(f"family {family['id']} essay too thin")
        contract = family.get("contract") or {}
        for field in ["input", "action", "evidence", "output", "failure_test"]:
            if len(words(contract.get(field))) < 25:
                fail(f"family {family['id']} contract {field} too thin")
        playbook = family.get("playbook") or {}
        for field in ["setup", "move", "payoff", "failure", "reader_test"]:
            if len(words(playbook.get(field))) < 25:
                fail(f"family {family['id']} playbook {field} too thin")
        answer_guide = family.get("answer_guide") or {}
        for field in ["input_answer", "action_answer", "evidence_answer", "output_answer", "failure_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"family {family['id']} answer guide {field} too thin")

    theme_ids = {theme["id"] for theme in data["themes"]}
    subtheme_ids = {subtheme["id"] for subtheme in data["subthemes"]}
    concept_ids = {concept["id"] for concept in data["concepts"]}

    for concept in data["concepts"]:
        if concept.get("theme") not in theme_ids:
            fail(f"concept {concept['id']} references unknown theme: {concept.get('theme')}")
        unknown_subthemes = sorted(set(concept.get("subthemes") or []) - subtheme_ids)
        if unknown_subthemes:
            fail(f"concept {concept['id']} references unknown subthemes: {unknown_subthemes}")
        if len(words(concept["first_principles"])) < 35:
            fail(f"concept first_principles too thin: {concept['id']}")
        if len(words(concept["important_detail"])) < 12:
            fail(f"concept important_detail too thin: {concept['id']}")
        if len(words(concept["math_principle"])) < 8:
            fail(f"concept math_principle too thin: {concept['id']}")
        depth = concept.get("depth") or {}
        for field in ["why_it_exists", "beginner_trap", "course_role"]:
            if len(words(depth.get(field))) < 35:
                fail(f"concept {concept['id']} depth {field} too thin")
        concept_essay_words = sum(len(words(p)) for p in concept.get("essay") or [])
        if concept_essay_words < 290:
            fail(f"concept {concept['id']} essay too thin")
        workup = concept.get("workup") or {}
        for field in ["object", "operation", "protected", "breaks_if"]:
            if len(words(workup.get(field))) < 25:
                fail(f"concept {concept['id']} workup {field} too thin")
        anchor = concept.get("anchor") or {}
        for field in ["course_moment", "principle", "reader_question"]:
            if len(words(anchor.get(field))) < 25:
                fail(f"concept {concept['id']} anchor {field} too thin")
        self_check = concept.get("self_check") or {}
        for field in ["object_check", "operation_check", "protected_check", "failure_check"]:
            if len(words(self_check.get(field))) < 40:
                fail(f"concept {concept['id']} self check {field} too thin")
        appearances = concept.get("appearances") or []
        if len(appearances) < 2:
            fail(f"concept {concept['id']} needs at least two lecture appearances")
        lecture_numbers = {lecture["lecture"] for lecture in data["lectures"]}
        for appearance in appearances:
            if appearance.get("lecture") not in lecture_numbers:
                fail(f"concept {concept['id']} appearance references unknown lecture")
            if len(words(appearance.get("summary"))) < 25:
                fail(f"concept {concept['id']} appearance summary too thin")

    for lecture in data["lectures"]:
        if not lecture["missing_caption_ids"] and lecture["transcript_words"] < 1000:
            fail(f"lecture {lecture['lecture']} has suspiciously short transcript")
        if len(words(lecture["plain_reading"])) < 18:
            fail(f"lecture {lecture['lecture']} reading too thin")
        deep = lecture.get("deep") or {}
        for field in ["problem", "first_principles", "math_move", "detail", "connection"]:
            if len(words(deep.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} deep {field} too thin")
        deepening = deep.get("deepening") or {}
        for field in ["what_is_really_happening", "why_it_is_hard", "key_move", "payoff"]:
            if len(words(deepening.get(field))) < 25:
                fail(f"lecture {lecture['lecture']} deepening {field} too thin")
        if len(deep.get("anchors") or []) < 4:
            fail(f"lecture {lecture['lecture']} needs transcript anchors")
        source_lens = deep.get("source_lens") or []
        if len(source_lens) < 2:
            fail(f"lecture {lecture['lecture']} needs source lens paragraphs")
        if sum(len(words(p)) for p in source_lens) < 100:
            fail(f"lecture {lecture['lecture']} source lens too thin")
        source_checkpoint = deep.get("source_checkpoint") or {}
        for field in ["trust", "do_not_overread", "math_question"]:
            if len(words(source_checkpoint.get(field))) < 25:
                fail(f"lecture {lecture['lecture']} source checkpoint {field} too thin")
        source_faithfulness = deep.get("source_faithfulness") or {}
        for field in ["caption_support", "course_inference", "caveat"]:
            if len(words(source_faithfulness.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} source faithfulness {field} too thin")
        nuance = deep.get("caption_nuance") or {}
        if len(nuance.get("terms") or []) < 4:
            fail(f"lecture {lecture['lecture']} caption nuance needs four terms")
        for field in ["risk", "safe_reading", "verify_question"]:
            if len(words(nuance.get(field))) < 25:
                fail(f"lecture {lecture['lecture']} caption nuance {field} too thin")
        walkthrough = deep.get("walkthrough") or {}
        for field in ["start_here", "payoff", "reader_check"]:
            if len(words(walkthrough.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} walkthrough {field} too thin")
        reader_test = deep.get("reader_test") or {}
        for field in ["explain_object", "test_allowed_move", "protect_conclusion"]:
            if len(words(reader_test.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} reader test {field} too thin")
        answer_guide = deep.get("answer_guide") or {}
        for field in ["object_answer", "move_answer", "conclusion_answer"]:
            if len(words(answer_guide.get(field))) < 30:
                fail(f"lecture {lecture['lecture']} answer guide {field} too thin")
        essay_words = sum(len(words(p)) for p in deep.get("essay") or [])
        if essay_words < 300:
            fail(f"lecture {lecture['lecture']} essay too thin")
        examples = deep.get("examples") or []
        if len(examples) < 3:
            fail(f"lecture {lecture['lecture']} needs at least three concrete examples")
        concept_ids = {c["id"] for c in data["concepts"]}
        for example in examples:
            if len(words(example.get("text"))) < 25:
                fail(f"lecture {lecture['lecture']} example too thin: {example.get('title')}")
            if len(example.get("concepts") or []) < 3:
                fail(f"lecture {lecture['lecture']} example needs concept bridges: {example.get('title')}")
            missing = [cid for cid in example.get("concepts", []) if cid not in concept_ids]
            if missing:
                fail(f"lecture {lecture['lecture']} example has unknown concept ids: {missing}")

    for family in data["families"]:
        missing = sorted(set(family.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"family {family['id']} references unknown concept ids: {missing}")

    lecture_numbers = {lecture["lecture"] for lecture in data["lectures"]}
    lecture_spine = data.get("lecture_spine") or []
    if len(lecture_spine) != 15:
        fail(f"lecture spine needs exactly 15 entries, got {len(lecture_spine)}")
    if {row.get("lecture") for row in lecture_spine} != lecture_numbers:
        fail("lecture spine does not match lecture numbers")
    for row in lecture_spine:
        for field in ["object", "plain_question", "legal_move", "surviving_fact", "why_later"]:
            if len(words(row.get(field))) < 10:
                fail(f"lecture spine {row.get('lecture')} {field} too thin")

    dependencies = data.get("concept_dependencies") or []
    if len(dependencies) < 8:
        fail("concept dependencies too small")
    for row in dependencies:
        ids = set(row.get("before") or []) | set(row.get("after") or [])
        missing = sorted(ids - concept_ids)
        if missing:
            fail(f"concept dependency references unknown concept ids: {missing}")
        for field in ["stage", "plain", "why", "reader_check"]:
            if len(words(row.get(field))) < 8:
                fail(f"concept dependency {row.get('stage')} {field} too thin")

    family_ids = {family["id"] for family in data["families"]}
    proof_moves = data.get("proof_moves") or []
    if len(proof_moves) < 5:
        fail("proof moves too small")
    for row in proof_moves:
        if row.get("family") not in family_ids:
            fail(f"proof move references unknown family id: {row.get('family')}")
        if len(row.get("steps") or []) < 5:
            fail(f"proof move needs five steps: {row.get('name')}")
        for field in ["name", "problem", "why", "failure", "example"]:
            if len(words(row.get(field))) < 8:
                fail(f"proof move {row.get('name')} {field} too thin")

    references = data.get("references") or []
    if len(references) < 7:
        fail("references layer too small")
    reference_ids = {row.get("id") for row in references}
    referenced_concepts = set()
    for row in references:
        if not str(row.get("url", "")).startswith("https://"):
            fail(f"reference missing https url: {row.get('id')}")
        if len(words(row.get("why"))) < 25:
            fail(f"reference why too thin: {row.get('id')}")
        if len(words(row.get("use_carefully"))) < 20:
            fail(f"reference caveat too thin: {row.get('id')}")
        if len(row.get("lectures") or []) < 2:
            fail(f"reference needs lecture coverage: {row.get('id')}")
        if len(row.get("concepts") or []) < 3:
            fail(f"reference needs concept coverage: {row.get('id')}")
        unknown = sorted(set(row.get("concepts") or []) - concept_ids)
        if unknown:
            fail(f"reference {row.get('id')} has unknown concept ids: {unknown}")
        referenced_concepts.update(row.get("concepts") or [])
    uncovered_concepts = sorted(concept_ids - referenced_concepts)
    if uncovered_concepts:
        fail(f"concepts missing reference coverage: {uncovered_concepts}")

    source_readers = data.get("source_readers") or []
    if len(source_readers) != len(references):
        fail("source reader layer must cover every reference")
    if {row.get("reference") for row in source_readers} != reference_ids:
        fail("source reader references do not match reference ids")
    for row in source_readers:
        for field in ["reader_problem", "object_to_watch", "first_principles_bridge", "how_to_read", "do_not_overread", "reader_question"]:
            if len(words(row.get(field))) < 14:
                fail(f"source reader {row.get('reference')} {field} too thin")
        if len(words(row.get("family"))) < 2:
            fail(f"source reader {row.get('reference')} family too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"source reader {row.get('reference')} needs three concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"source reader {row.get('reference')} references unknown concept ids: {missing}")

    lecture_source_bridges = data.get("lecture_source_bridges") or []
    if len(lecture_source_bridges) != 15:
        fail("lecture source bridges need exactly fifteen lecture bridges")
    if {row.get("lecture") for row in lecture_source_bridges} != lecture_numbers:
        fail("lecture source bridges do not match lecture numbers")
    for row in lecture_source_bridges:
        if len(row.get("references") or []) < 1:
            fail(f"lecture source bridge {row.get('lecture')} needs references")
        unknown_refs = sorted(set(row.get("references") or []) - reference_ids)
        if unknown_refs:
            fail(f"lecture source bridge {row.get('lecture')} unknown references: {unknown_refs}")
        unknown_concepts = sorted(set(row.get("concepts") or []) - concept_ids)
        if unknown_concepts:
            fail(f"lecture source bridge {row.get('lecture')} unknown concepts: {unknown_concepts}")
        if len(row.get("concepts") or []) < 3:
            fail(f"lecture source bridge {row.get('lecture')} needs concept links")
        if len(words(row.get("source_family"))) < 2:
            fail(f"lecture source bridge {row.get('lecture')} source family too thin")
        for field in ["course_demonstration", "mathematical_bridge", "how_source_extends", "overread_warning", "reader_question"]:
            if len(words(row.get(field))) < 24:
                fail(f"lecture source bridge {row.get('lecture')} {field} too thin")

    html_files = sorted(SITE.glob("*.html"))
    if len(html_files) < 65:
        fail(f"expected at least 65 html pages after reader-checks pass, got {len(html_files)}")
    names = {p.name for p in html_files}
    for page in ["index.html", "videos.html", "lectures.html", "lecture-spine.html", "concepts.html", "themes.html", "subthemes.html", "families.html", "the-math-why.html", "math-playground.html", "course-synthesis.html", "concept-dependencies.html", "proof-moves.html", "formula-reader.html", "reader-checks.html", "term-translator.html", "paper-source-reader.html", "lecture-source-bridges.html", "references.html", "quality-rubric.html", "rubric-coverage.html", "quality-audit.html", "source-audit.html"]:
        if page not in names:
            fail(f"missing site page {page}")
    playground = SITE / "math-playground.html"
    playground_js = SITE / "assets" / "playground.js"
    if not playground_js.exists():
        fail("missing playground.js asset")
    play_html = playground.read_text(encoding="utf-8", errors="ignore")
    if play_html.count("data-play=") < 4:
        fail("math playground needs four canvas widgets")
    for widget in ["euler", "signs", "fixed", "index"]:
        if f'data-play="{widget}"' not in play_html:
            fail(f"math playground missing widget: {widget}")
        if f"{widget}:" not in playground_js.read_text(encoding="utf-8", errors="ignore"):
            fail(f"playground.js missing renderer: {widget}")
    deep_dive = (SITE / "course-synthesis.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Dependency Spine", "The One Engine", "Proof Families", "Lecture Spine", "How To Read Any Page"]:
        if phrase not in deep_dive:
            fail(f"course synthesis missing section: {phrase}")
    if deep_dive.count("<article") < 25:
        fail("course synthesis needs dependency, family, and lecture cards")
    if len(words(re.sub(r"<[^>]+>", " ", deep_dive))) < 900:
        fail("course synthesis too thin")
    dependency_page = (SITE / "concept-dependencies.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Concept Dependencies", "Understand first", "Then read", "Why this dependency matters", "Reader check"]:
        if phrase not in dependency_page:
            fail(f"concept dependencies page missing phrase: {phrase}")
    if dependency_page.count("<article") < 8:
        fail("concept dependencies page needs eight dependency cards")
    if len(words(re.sub(r"<[^>]+>", " ", dependency_page))) < 850:
        fail("concept dependencies page too thin")
    lecture_spine_page = (SITE / "lecture-spine.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Lecture Spine", "Object:", "Plain question:", "Legal move:", "Surviving fact:", "Why later lectures need it:"]:
        if phrase not in lecture_spine_page:
            fail(f"lecture spine page missing phrase: {phrase}")
    if lecture_spine_page.count("<article") < 15:
        fail("lecture spine page needs fifteen lecture cards")
    for number in range(1, 16):
        if f"lecture-{number:02d}.html" not in lecture_spine_page:
            fail(f"lecture spine missing lecture link: {number:02d}")
    if len(words(re.sub(r"<[^>]+>", " ", lecture_spine_page))) < 1400:
        fail("lecture spine page too thin")
    proof_page = (SITE / "proof-moves.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Proof Moves", "Steps", "Why it works", "Failure mode", "Course example"]:
        if phrase not in proof_page:
            fail(f"proof moves page missing phrase: {phrase}")
    if proof_page.count("<article") < 5:
        fail("proof moves page needs five proof cards")
    if proof_page.count("<li>") < 25:
        fail("proof moves page needs twenty-five proof steps")
    if len(words(re.sub(r"<[^>]+>", " ", proof_page))) < 900:
        fail("proof moves page too thin")
    formula_reader = (SITE / "formula-reader.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Formula Reader", "Plain reading", "Why it survives", "What it can force", "Reader check"]:
        if phrase not in formula_reader:
            fail(f"formula reader missing phrase: {phrase}")
    if formula_reader.count("<article") < 7:
        fail("formula reader needs seven formula cards")
    if len(words(re.sub(r"<[^>]+>", " ", formula_reader))) < 700:
        fail("formula reader too thin")
    reader_checks = (SITE / "reader-checks.html").read_text(encoding="utf-8", errors="ignore")
    if reader_checks.count("Reader check") < 11:
        fail("reader checks page needs eleven checks")
    for phrase in ["What goes wrong", "Ask instead", "legal moves", "protected evidence"]:
        if phrase not in reader_checks:
            fail(f"reader checks page missing phrase: {phrase}")
    if len(words(re.sub(r"<[^>]+>", " ", reader_checks))) < 700:
        fail("reader checks page too thin")
    term_translator = (SITE / "term-translator.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Term Translator", "Everyday sentence:", "Job in the argument:", "Not a definition:", "Failure if misread:", "Reader question:"]:
        if phrase not in term_translator:
            fail(f"term translator missing phrase: {phrase}")
    if term_translator.count("<article") < 16:
        fail("term translator needs sixteen term cards")
    if len(words(re.sub(r"<[^>]+>", " ", term_translator))) < 1200:
        fail("term translator too thin")
    paper_source_reader = (SITE / "paper-source-reader.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Paper Source Reader", "Reader problem:", "Object to watch:", "First-principles bridge:", "How to read:", "Do not overread:", "Reader question:", "Course-To-Paper Test"]:
        if phrase not in paper_source_reader:
            fail(f"paper source reader missing phrase: {phrase}")
    if paper_source_reader.count("<article") < 7:
        fail("paper source reader needs seven source cards")
    if len(words(re.sub(r"<[^>]+>", " ", paper_source_reader))) < 1200:
        fail("paper source reader too thin")
    lecture_source_bridges_page = (SITE / "lecture-source-bridges.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Lecture Source Bridges", "Course demonstration:", "Mathematical bridge:", "How the source extends it:", "Overread warning:", "Reader question:", "The Transfer Test"]:
        if phrase not in lecture_source_bridges_page:
            fail(f"lecture source bridges page missing phrase: {phrase}")
    if lecture_source_bridges_page.count("<article") < 15:
        fail("lecture source bridges page needs fifteen cards")
    if len(words(re.sub(r"<[^>]+>", " ", lecture_source_bridges_page))) < 2400:
        fail("lecture source bridges page too thin")
    references_page = (SITE / "references.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["References", "Source Caveat", "Why it belongs", "Use carefully", "Lecture coverage", "Concept coverage"]:
        if phrase not in references_page:
            fail(f"references page missing phrase: {phrase}")
    if references_page.count("<article") < 7:
        fail("references page needs seven reference cards")
    if len(words(re.sub(r"<[^>]+>", " ", references_page))) < 700:
        fail("references page too thin")
    quality_rubric_page = (SITE / "quality-rubric.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Quality Rubric", "How To Use The Rubric", "Completion Test", "Test:", "Strong answer:", "Failure:", "Repair:"]:
        if phrase not in quality_rubric_page:
            fail(f"quality rubric page missing phrase: {phrase}")
    if quality_rubric_page.count("<article") < 6:
        fail("quality rubric page needs six cards")
    if len(words(re.sub(r"<[^>]+>", " ", quality_rubric_page))) < 650:
        fail("quality rubric page too thin")
    rubric_coverage_page = (SITE / "rubric-coverage.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Rubric Coverage", "How To Read This Coverage", "Reviewer Rule", "Reader test:", "Name the object before the term", "Name the legal move", "Name what survives", "Say what would break the claim", "Tie the idea to a course moment", "Replace formal words with everyday sentences"]:
        if phrase not in rubric_coverage_page:
            fail(f"rubric coverage page missing phrase: {phrase}")
    if rubric_coverage_page.count("<article") < 6:
        fail("rubric coverage page needs six cards")
    if len(words(re.sub(r"<[^>]+>", " ", rubric_coverage_page))) < 950:
        fail("rubric coverage page too thin")
    source_audit = (SITE / "source-audit.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Caption Nuance By Lecture", "Caption risk:", "Safe reading:", "Verify:", "Source checkpoint:", "Caption support:", "Course inference:", "Caveat:"]:
        if phrase not in source_audit:
            fail(f"source audit missing caption nuance phrase: {phrase}")
    if source_audit.count("<article") < 15:
        fail("source audit needs fifteen caption nuance cards")
    if len(words(re.sub(r"<[^>]+>", " ", source_audit))) < 1400:
        fail("source audit caption nuance too thin")
    for concept in data["concepts"]:
        concept_name = f"concept-{concept['id']}.html"
        if concept_name not in names:
            fail(f"missing concept page {concept['id']}")
        concept_html = (SITE / concept_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Anchor Example", "Course moment:", "Principle:", "Reader question:", "Work It From Scratch", "Object:", "Operation:", "Protected fact:", "Breaks if:", "Can You Use It?", "Object check:", "Operation check:", "Protected fact check:", "Failure check:"]:
            if phrase not in concept_html:
                fail(f"concept page missing concept phrase {phrase}: {concept_name}")
        for phrase in ["Further Source Trail", "Why it belongs:", "Use carefully:"]:
            if phrase not in concept_html:
                fail(f"concept page missing reference phrase {phrase}: {concept_name}")
    for lecture in data["lectures"]:
        lecture_name = f"lecture-{lecture['lecture']:02d}.html"
        if lecture_name not in names:
            fail(f"missing lecture page {lecture['lecture']:02d}")
        lecture_html = (SITE / lecture_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Lecture Deepening", "What is really happening:", "Why it is hard:", "Key move:", "Payoff:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing deepening phrase {phrase}: {lecture_name}")
        if "Source Lens" not in lecture_html:
            fail(f"lecture page missing source lens: {lecture_name}")
        for phrase in ["Source Checkpoint", "Trust:", "Do not overread:", "Math question:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing source checkpoint phrase {phrase}: {lecture_name}")
        for phrase in ["Source-Faithfulness Audit", "Caption support:", "Course inference:", "Caveat:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing source faithfulness phrase {phrase}: {lecture_name}")
        for phrase in ["Caption Nuance", "Caption risk:", "Safe reading:", "Verify:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing caption nuance phrase {phrase}: {lecture_name}")
        for phrase in ["Slow Walkthrough", "Start here:", "Mathematical payoff:", "Reader check:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing walkthrough phrase {phrase}: {lecture_name}")
        for phrase in ["Can You Explain It?", "Explain the object:", "Check the allowed move:", "Protect the conclusion:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing reader test phrase {phrase}: {lecture_name}")
        for phrase in ["Answer Guide", "Object answer:", "Move answer:", "Conclusion answer:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing answer guide phrase {phrase}: {lecture_name}")
        for phrase in ["Further Source Trail", "Why it belongs:", "Use carefully:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing reference phrase {phrase}: {lecture_name}")
    for theme in data["themes"]:
        theme_name = f"theme-{theme['id']}.html"
        if theme_name not in names:
            fail(f"missing theme page {theme['id']}")
        theme_html = (SITE / theme_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Theme Lens", "Notices:", "Ignores:", "Changes the problem:", "Reader test:", "Can You Carry The Theme?", "Notice answer:", "Ignore answer:", "Transfer answer:", "Test answer:"]:
            if phrase not in theme_html:
                fail(f"theme page missing lens phrase {phrase}: {theme_name}")
    for subtheme in data["subthemes"]:
        subtheme_name = f"subtheme-{subtheme['id']}.html"
        if subtheme_name not in names:
            fail(f"missing subtheme page {subtheme['id']}")
        subtheme_html = (SITE / subtheme_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["First-Principles Bridge", "Course moment:", "Thinking shift:", "Reader test:", "Reading Routine", "Look for:", "Ask:", "Use:", "Mistake:", "Can You Apply The Routine?", "Look answer:", "Ask answer:", "Use answer:", "Mistake answer:"]:
            if phrase not in subtheme_html:
                fail(f"subtheme page missing subtheme phrase {phrase}: {subtheme_name}")
    for family in data["families"]:
        family_name = f"family-{family['id']}.html"
        if family_name not in names:
            fail(f"missing family page {family['id']}")
        family_html = (SITE / family_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Method Playbook", "Setup:", "Move:", "Payoff:", "Failure:", "Reader test:", "Method Contract", "Input:", "Action:", "Protected evidence:", "Output:", "Failure test:", "Can You Use This Method?", "Input answer:", "Action answer:", "Evidence answer:", "Output answer:", "Failure answer:"]:
            if phrase not in family_html:
                fail(f"family page missing family phrase {phrase}: {family_name}")

    corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore").lower() for p in html_files)
    for phrase in FORBIDDEN:
        if re.search(rf"\b{re.escape(phrase)}\b", corpus):
            fail(f"forbidden phrase found: {phrase}")
    if corpus.count("a strong answer") > 25:
        fail("generated prose repeats 'a strong answer' too often")

    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "#")):
                continue
            target = (path.parent / href).resolve()
            if "#" in href:
                target = (path.parent / href.split("#", 1)[0]).resolve()
            if not target.exists():
                fail(f"broken local link in {path.name}: {href}")

    print(json.dumps({
        "videos": stats["videos"],
        "lectures": stats["lectures"],
        "captioned_videos": stats["captioned_videos"],
        "missing_captions": data["missing_caption_ids"],
        "concepts": stats["concepts"],
        "themes": stats["themes"],
        "subthemes": stats["subthemes"],
        "families": stats["families"],
        "html_pages": len(html_files),
    }, indent=2))


if __name__ == "__main__":
    main()
