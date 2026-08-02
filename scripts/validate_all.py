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
    "tricks",
    "interesting",
    "natural",
    "powerful",
    "pretty",
    "simply",
    "zoo",
    "big picture",
    "big-picture",
    "course habit",
    "course habits",
    "broad claim",
    "broad claims",
    "broad idea",
    "broad ideas",
    "broad theme",
    "broad themes",
    "decorative",
    "the idea matters",
    "why the idea matters",
    "the concept matters",
    "why the concept matters",
    "the theme matters",
    "why the theme matters",
    "the lecture matters",
    "why the lecture matters",
    "the method matters",
    "why the method matters",
    "useful because",
    "useful only",
    "useful when",
    "stays useful",
    "becomes useful",
]


def words(s):
    return re.findall(r"[A-Za-z0-9']+", s or "")


def sentence_starts(text, size=6):
    starts = []
    for sentence in re.split(r"(?<=[.!?])\s+", text or ""):
        start = words(sentence)[:size]
        if len(start) >= 4:
            starts.append(" ".join(start).lower())
    return starts


def fail_repeated_sentence_starts(layer, rows, max_allowed=3):
    counts = {}
    examples = {}
    for row_id, fields in rows:
        for field, text in fields.items():
            for start in sentence_starts(text):
                counts[start] = counts.get(start, 0) + 1
                examples.setdefault(start, f"{row_id}.{field}")
    repeated = sorted((count, start) for start, count in counts.items() if count > max_allowed)
    if repeated:
        count, start = repeated[-1]
        fail(f"{layer} answer guides repeat sentence start {count} times: {start} at {examples[start]}")


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
            if len(words(item.get(field))) < 30:
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
            if len(words(row.get(field))) < 65:
                fail(f"term translation {row.get('term')} {field} too thin")
        if len(words(row.get("reader_question"))) < 65:
            fail(f"term translation {row.get('term')} reader question too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"term translation {row.get('term')} needs three concept links")
        missing = sorted(set(row.get("concepts") or []) - term_concept_ids)
        if missing:
            fail(f"term translation {row.get('term')} references unknown concept ids: {missing}")

    math_why = data.get("math_why") or {}
    for field in ["big_picture", "first_principles", "important_detail", "principle", "concepts_matter", "reader_path"]:
        if len(words(math_why.get(field))) < 90:
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
        if len(words(theme.get("plain"))) < 85:
            fail(f"theme {theme['id']} plain summary too thin")
        depth = theme.get("depth") or {}
        for field in ["problem", "habit", "course_arc", "important_detail"]:
            if len(words(depth.get(field))) < 40:
                fail(f"theme {theme['id']} depth {field} too thin")
        if len(words(theme.get("why_math_matters"))) < 40:
            fail(f"theme {theme['id']} why_math_matters too thin")
        if len(depth.get("lectures") or []) < 4:
            fail(f"theme {theme['id']} needs lecture thread")
        theme_essay_words = sum(len(words(p)) for p in theme.get("essay") or [])
        if theme_essay_words < 300:
            fail(f"theme {theme['id']} essay too thin")
        first_principles_essay = theme.get("first_principles_essay") or {}
        for field in ["ordinary_problem", "object_on_page", "allowed_change", "protected_fact", "topology_payoff", "outside_use", "wrong_use"]:
            if len(words(first_principles_essay.get(field))) < 120:
                fail(f"theme {theme['id']} first-principles essay {field} too thin")
        lens = theme.get("lens") or {}
        for field in ["notices", "ignores", "changes_problem", "reader_test"]:
            if len(words(lens.get(field))) < 90:
                fail(f"theme {theme['id']} lens {field} too thin")
        application = theme.get("application") or {}
        for field in ["outside_problem", "course_habit", "where_it_matters", "honest_limit"]:
            if len(words(application.get(field))) < 105:
                fail(f"theme {theme['id']} application {field} too thin")
        answer_guide = theme.get("answer_guide") or {}
        for field in ["notice_answer", "ignore_answer", "transfer_answer", "test_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"theme {theme['id']} answer guide {field} too thin")
    fail_repeated_sentence_starts(
        "theme",
        [(theme["id"], theme.get("answer_guide") or {}) for theme in data["themes"]],
    )

    for subtheme in data["subthemes"]:
        if len(words(subtheme.get("plain"))) < 80:
            fail(f"subtheme {subtheme['id']} plain summary too thin")
        depth = subtheme.get("depth") or {}
        for field in ["problem", "first_principles", "course_role"]:
            if len(words(depth.get(field))) < 40:
                fail(f"subtheme {subtheme['id']} depth {field} too thin")
        subtheme_essay_words = sum(len(words(p)) for p in subtheme.get("essay") or [])
        if subtheme_essay_words < 260:
            fail(f"subtheme {subtheme['id']} essay too thin")
        first_principles_essay = subtheme.get("first_principles_essay") or {}
        for field in ["ordinary_problem", "object_on_page", "allowed_change", "protected_fact", "topology_payoff", "outside_use", "wrong_use"]:
            if len(words(first_principles_essay.get(field))) < 120:
                fail(f"subtheme {subtheme['id']} first-principles essay {field} too thin")
        routine = subtheme.get("routine") or {}
        for field in ["look_for", "ask", "use", "mistake"]:
            if len(words(routine.get(field))) < 90:
                fail(f"subtheme {subtheme['id']} routine {field} too thin")
        bridge = subtheme.get("bridge") or {}
        for field in ["course_moment", "thinking_shift", "reader_test"]:
            if len(words(bridge.get(field))) < 90:
                fail(f"subtheme {subtheme['id']} bridge {field} too thin")
        application = subtheme.get("application") or {}
        for field in ["outside_problem", "course_habit", "where_it_matters", "honest_limit"]:
            if len(words(application.get(field))) < 120:
                fail(f"subtheme {subtheme['id']} application {field} too thin")
        answer_guide = subtheme.get("answer_guide") or {}
        for field in ["look_answer", "ask_answer", "use_answer", "mistake_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"subtheme {subtheme['id']} answer guide {field} too thin")
    fail_repeated_sentence_starts(
        "subtheme",
        [(subtheme["id"], subtheme.get("answer_guide") or {}) for subtheme in data["subthemes"]],
    )

    for family in data["families"]:
        depth = family.get("depth") or {}
        if len(words(family.get("purpose"))) < 60:
            fail(f"family {family['id']} purpose too thin")
        for field in ["human_problem", "first_principles", "how_it_works", "course_examples", "failure_mode"]:
            if len(words(depth.get(field))) < 45:
                fail(f"family {family['id']} depth {field} too thin")
        family_essay_words = sum(len(words(p)) for p in family.get("essay") or [])
        if family_essay_words < 285:
            fail(f"family {family['id']} essay too thin")
        first_principles_essay = family.get("first_principles_essay") or {}
        for field in ["ordinary_problem", "object_on_page", "allowed_change", "protected_fact", "topology_payoff", "outside_use", "wrong_use"]:
            if len(words(first_principles_essay.get(field))) < 130:
                fail(f"family {family['id']} first-principles essay {field} too thin")
        contract = family.get("contract") or {}
        for field in ["input", "action", "evidence", "output", "failure_test"]:
            if len(words(contract.get(field))) < 100:
                fail(f"family {family['id']} contract {field} too thin")
        playbook = family.get("playbook") or {}
        for field in ["setup", "move", "payoff", "failure", "reader_test"]:
            if len(words(playbook.get(field))) < 100:
                fail(f"family {family['id']} playbook {field} too thin")
        application = family.get("application") or {}
        for field in ["outside_problem", "method_transfer", "where_it_matters", "honest_limit"]:
            if len(words(application.get(field))) < 125:
                fail(f"family {family['id']} application {field} too thin")
        answer_guide = family.get("answer_guide") or {}
        for field in ["input_answer", "action_answer", "evidence_answer", "output_answer", "failure_answer"]:
            if len(words(answer_guide.get(field))) < 40:
                fail(f"family {family['id']} answer guide {field} too thin")
    fail_repeated_sentence_starts(
        "family",
        [(family["id"], family.get("answer_guide") or {}) for family in data["families"]],
    )

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
        if len(words(concept["important_detail"])) < 20:
            fail(f"concept important_detail too thin: {concept['id']}")
        if len(words(concept["math_principle"])) < 18:
            fail(f"concept math_principle too thin: {concept['id']}")
        depth = concept.get("depth") or {}
        concept_depth_min_words = {
            "why_it_exists": 35,
            "beginner_trap": 35,
            "course_role": 45,
        }
        for field, minimum in concept_depth_min_words.items():
            if len(words(depth.get(field))) < minimum:
                fail(f"concept {concept['id']} depth {field} too thin")
        concept_essay_words = sum(len(words(p)) for p in concept.get("essay") or [])
        if concept_essay_words < 290:
            fail(f"concept {concept['id']} essay too thin")
        first_principles_essay = concept.get("first_principles_essay") or {}
        for field in ["ordinary_problem", "object_on_page", "allowed_change", "protected_fact", "topology_payoff", "outside_use", "wrong_use"]:
            if len(words(first_principles_essay.get(field))) < 120:
                fail(f"concept {concept['id']} first-principles essay {field} too thin")
        workup = concept.get("workup") or {}
        for field in ["object", "operation", "protected", "breaks_if"]:
            if len(words(workup.get(field))) < 75:
                fail(f"concept {concept['id']} workup {field} too thin")
        anchor = concept.get("anchor") or {}
        for field in ["course_moment", "principle", "reader_question"]:
            if len(words(anchor.get(field))) < 75:
                fail(f"concept {concept['id']} anchor {field} too thin")
        application = concept.get("application") or {}
        for field in ["outside_problem", "topology_application", "other_fields", "why_it_matters", "honest_limit"]:
            if len(words(application.get(field))) < 95:
                fail(f"concept {concept['id']} application {field} too thin")
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
    fail_repeated_sentence_starts(
        "concept",
        [(concept["id"], concept.get("self_check") or {}) for concept in data["concepts"]],
    )

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
            if len(words(deepening.get(field))) < 95:
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
            if len(words(source_checkpoint.get(field))) < 85:
                fail(f"lecture {lecture['lecture']} source checkpoint {field} too thin")
        source_faithfulness = deep.get("source_faithfulness") or {}
        for field in ["caption_support", "course_inference", "caveat"]:
            if len(words(source_faithfulness.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} source faithfulness {field} too thin")
        nuance = deep.get("caption_nuance") or {}
        if len(nuance.get("terms") or []) < 4:
            fail(f"lecture {lecture['lecture']} caption nuance needs four terms")
        for field in ["risk", "safe_reading", "verify_question"]:
            if len(words(nuance.get(field))) < 85:
                fail(f"lecture {lecture['lecture']} caption nuance {field} too thin")
        walkthrough = deep.get("walkthrough") or {}
        for field in ["start_here", "payoff", "reader_check"]:
            if len(words(walkthrough.get(field))) < 95:
                fail(f"lecture {lecture['lecture']} walkthrough {field} too thin")
        application_bridge = deep.get("application_bridge") or {}
        for field in ["outside_problem", "topology_bridge", "protected_fact", "where_it_matters", "honest_limit"]:
            if len(words(application_bridge.get(field))) < 105:
                fail(f"lecture {lecture['lecture']} application bridge {field} too thin")
        reader_test = deep.get("reader_test") or {}
        for field in ["explain_object", "test_allowed_move", "protect_conclusion"]:
            if len(words(reader_test.get(field))) < 95:
                fail(f"lecture {lecture['lecture']} reader test {field} too thin")
        answer_guide = deep.get("answer_guide") or {}
        for field in ["object_answer", "move_answer", "conclusion_answer"]:
            if len(words(answer_guide.get(field))) < 85:
                fail(f"lecture {lecture['lecture']} answer guide {field} too thin")
        essay_words = sum(len(words(p)) for p in deep.get("essay") or [])
        if essay_words < 300:
            fail(f"lecture {lecture['lecture']} essay too thin")
        first_principles_essay = deep.get("first_principles_essay") or {}
        for field in ["ordinary_problem", "object_on_page", "allowed_change", "protected_fact", "topology_payoff", "outside_use", "wrong_use"]:
            if len(words(first_principles_essay.get(field))) < 130:
                fail(f"lecture {lecture['lecture']} first-principles essay {field} too thin")
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
    fail_repeated_sentence_starts(
        "lecture",
        [(str(lecture["lecture"]), ((lecture.get("deep") or {}).get("answer_guide") or {})) for lecture in data["lectures"]],
    )

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
            if len(words(row.get(field))) < 85:
                fail(f"lecture spine {row.get('lecture')} {field} too thin")

    dependencies = data.get("concept_dependencies") or []
    if len(dependencies) < 8:
        fail("concept dependencies too small")
    for row in dependencies:
        ids = set(row.get("before") or []) | set(row.get("after") or [])
        missing = sorted(ids - concept_ids)
        if missing:
            fail(f"concept dependency references unknown concept ids: {missing}")
        if len(words(row.get("stage"))) < 8:
            fail(f"concept dependency {row.get('stage')} stage too thin")
        for field in ["plain", "why", "reader_check"]:
            if len(words(row.get(field))) < 30:
                fail(f"concept dependency {row.get('stage')} {field} too thin")

    application_spine_rows = data.get("application_spine_rows") or []
    required_application_domains = {
        "Physics and motion",
        "Robotics and mechanisms",
        "Engineering constraints",
        "Modeling choices",
        "Computing and networks",
        "Scientific measurement",
    }
    if {row.get("domain") for row in application_spine_rows} != required_application_domains:
        fail("application spine rows do not match required domain set")
    for row in application_spine_rows:
        for field in ["plain_problem", "topology_move", "outside_application", "why_it_matters", "wrong_reading", "reader_test"]:
            if len(words(row.get(field))) < 60:
                fail(f"application spine {row.get('domain')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"application spine {row.get('domain')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"application spine {row.get('domain')} unknown concepts: {missing}")

    transfer_lab_cases = data.get("transfer_lab_cases") or []
    required_transfer_titles = {
        "Rubber band around a mug handle",
        "Two walking routes around a fountain",
        "Matching arrows on a weather map",
        "Moving a sofa through a hallway",
        "Stirring coffee in a cup",
        "Drawing a map on a folded sheet",
        "Counting dents on a squeezed ball",
        "A robot arm avoiding a blocked zone",
    }
    if {row.get("title") for row in transfer_lab_cases} != required_transfer_titles:
        fail("transfer lab cases do not match required case set")
    for row in transfer_lab_cases:
        for field in ["situation", "object", "allowed_move", "protected_fact", "course_bridge", "wrong_transfer", "reader_task"]:
            if len(words(row.get(field))) < 60:
                fail(f"transfer lab {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"transfer lab {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"transfer lab {row.get('title')} unknown concepts: {missing}")

    repair_clinic_cases = data.get("repair_clinic_cases") or []
    required_repair_titles = {
        "Mobius strip as a visual surprise",
        "Invariant as any number that survives the allowed move",
        "Quotient space as a square with arrows",
        "Generic position as visual cleanup",
        "Fixed point as a point that does not move",
        "Index as the number of equilibria",
        "Configuration space as a diagram of the machine",
        "Poincare-Hopf as topology predicting motion",
    }
    if {row.get("title") for row in repair_clinic_cases} != required_repair_titles:
        fail("repair clinic cases do not match required case set")
    for row in repair_clinic_cases:
        for field in ["flawed_explanation", "why_it_fails", "repair_move", "strong_version", "reviewer_test"]:
            if len(words(row.get(field))) < 65:
                fail(f"repair clinic {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"repair clinic {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"repair clinic {row.get('title')} unknown concepts: {missing}")

    oral_exam_prompts = data.get("oral_exam_prompts") or []
    required_oral_titles = {
        "Explain the course in one chain",
        "Defend a deformation argument",
        "Turn a count into evidence",
        "Read a theorem contract",
        "Model a physical motion problem",
        "Separate fixed points and equilibria",
        "Audit a source-supported claim",
    }
    if {row.get("title") for row in oral_exam_prompts} != required_oral_titles:
        fail("oral exam prompts do not match required prompt set")
    for row in oral_exam_prompts:
        for field in ["prompt", "strong_answer", "must_include", "common_failure", "follow_up"]:
            if len(words(row.get(field))) < 65:
                fail(f"oral exam {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"oral exam {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"oral exam {row.get('title')} unknown concepts: {missing}")

    change_ledger_rows = data.get("change_ledger_rows") or []
    required_ledger_titles = {
        "Paper strip to global surface fact",
        "Messy route to legal deformation",
        "Visible crossings to signed evidence",
        "Cell drawing to Euler characteristic",
        "Square diagram to quotient surface",
        "Map rule to fixed-point evidence",
        "Arrow field to local index",
        "Local defects to Poincare-Hopf",
        "Machine motion to configuration space",
        "Source sentence to supported claim",
    }
    if {row.get("title") for row in change_ledger_rows} != required_ledger_titles:
        fail("change ledger rows do not match required case set")
    for row in change_ledger_rows:
        for field in ["object", "legal_change", "protected_fact", "why_matters", "false_move", "reader_test"]:
            if len(words(row.get(field))) < 65:
                fail(f"change ledger {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"change ledger {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"change ledger {row.get('title')} unknown concepts: {missing}")

    assumption_ledger_rows = data.get("assumption_ledger_rows") or []
    required_assumption_titles = {
        "Same object through a deformation",
        "Boundary data is fixed",
        "Continuity has not been lost",
        "The counted meetings are ordinary",
        "Signs have a shared direction rule",
        "All defects are included",
        "One point records one full state",
        "The rule maps the space to itself",
        "A cell count describes the same surface",
        "The source supports exactly this claim",
    }
    if {row.get("title") for row in assumption_ledger_rows} != required_assumption_titles:
        fail("assumption ledger rows do not match required case set")
    for row in assumption_ledger_rows:
        for field in ["claim", "assumption", "why_needed", "plain_check", "breaks_if", "course_place"]:
            if len(words(row.get(field))) < 65:
                fail(f"assumption ledger {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"assumption ledger {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"assumption ledger {row.get('title')} unknown concepts: {missing}")

    counterexample_gallery_rows = data.get("counterexample_gallery_rows") or []
    required_counterexample_titles = {
        "Flattening a twist loses the surface",
        "Moving an endpoint removes the obstruction",
        "Counting raw crossings overreads the picture",
        "Using signs without orientation",
        "Applying Brouwer outside its contract",
        "Leaving out one vector-field defect",
        "Modeling motion with missing forbidden states",
        "Changing the surface during a cell count",
        "Reading a source as stronger than it is",
        "Treating a theorem as a procedure",
    }
    if {row.get("title") for row in counterexample_gallery_rows} != required_counterexample_titles:
        fail("counterexample gallery rows do not match required case set")
    for row in counterexample_gallery_rows:
        for field in ["tempting_claim", "missing_condition", "failure_scene", "why_it_breaks", "repair"]:
            if len(words(row.get(field))) < 30:
                fail(f"counterexample gallery {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"counterexample gallery {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"counterexample gallery {row.get('title')} unknown concepts: {missing}")

    weak_claim_repair_rows = data.get("weak_claim_repair_rows") or []
    required_weak_claim_titles = {
        "Same shape means same answer",
        "The count is invariant",
        "The theorem applies",
        "The picture makes it clear",
        "The model captures the motion",
        "Signs cancel",
        "Local behavior determines the whole surface",
        "The source supports this",
        "This is just an example of the concept",
        "Topology is only about shape",
    }
    if {row.get("title") for row in weak_claim_repair_rows} != required_weak_claim_titles:
        fail("weak claim repair rows do not match required case set")
    for row in weak_claim_repair_rows:
        for field in ["weak_claim", "why_weak", "first_principles_repair", "detail_to_check", "where_to_use"]:
            if len(words(row.get(field))) < 65:
                fail(f"weak claim repair {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"weak claim repair {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"weak claim repair {row.get('title')} unknown concepts: {missing}")

    family_ids = {family["id"] for family in data["families"]}
    proof_moves = data.get("proof_moves") or []
    if len(proof_moves) < 5:
        fail("proof moves too small")
    for row in proof_moves:
        if row.get("family") not in family_ids:
            fail(f"proof move references unknown family id: {row.get('family')}")
        if len(row.get("steps") or []) < 5:
            fail(f"proof move needs five steps: {row.get('name')}")
        for field in ["problem", "why", "failure", "example"]:
            if len(words(row.get(field))) < 70:
                fail(f"proof move {row.get('name')} {field} too thin")

    theorem_contracts = data.get("theorem_use_contracts") or []
    if len(theorem_contracts) < 8:
        fail("theorem use contracts need eight contracts")
    required_contracts = {
        "Euler characteristic",
        "Generic position",
        "Signed intersection number",
        "Graph and diagonal fixed-point test",
        "Brouwer fixed-point theorem",
        "Vector-field index",
        "Poincare-Hopf theorem",
        "Configuration-space modeling",
    }
    if {row.get("name") for row in theorem_contracts} != required_contracts:
        fail("theorem use contracts do not match required contract set")
    for row in theorem_contracts:
        for field in ["use_when", "object_needed", "allowed_move", "protected_evidence", "conclusion_it_can_force", "breaks_if", "everyday_test"]:
            if len(words(row.get(field))) < 85:
                fail(f"theorem contract {row.get('name')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"theorem contract {row.get('name')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"theorem contract {row.get('name')} unknown concepts: {missing}")

    concept_contrasts = data.get("concept_contrasts") or []
    required_contrasts = {
        "Topology versus geometry",
        "Invariant versus raw count",
        "Deformation versus illegal shortcut",
        "Quotient space versus drawing",
        "Product space versus configuration space",
        "Generic position versus special accident",
        "Fixed point versus equilibrium",
        "Vector-field index versus Euler characteristic",
        "Boundary versus hole",
        "Source support versus source overclaim",
    }
    if {row.get("title") for row in concept_contrasts} != required_contrasts:
        fail("concept contrasts do not match required contrast set")
    for row in concept_contrasts:
        for field in ["confusion", "left_job", "right_job", "bridge", "failure_test", "reader_question"]:
            if len(words(row.get(field))) < 65:
                fail(f"concept contrast {row.get('title')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"concept contrast {row.get('title')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"concept contrast {row.get('title')} unknown concepts: {missing}")

    references = data.get("references") or []
    if len(references) < 7:
        fail("references layer too small")
    reference_ids = {row.get("id") for row in references}
    referenced_concepts = set()
    for row in references:
        if not str(row.get("url", "")).startswith("https://"):
            fail(f"reference missing https url: {row.get('id')}")
        if len(words(row.get("why"))) < 45:
            fail(f"reference why too thin: {row.get('id')}")
        if len(words(row.get("use_carefully"))) < 45:
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
            if len(words(row.get(field))) < 65:
                fail(f"source reader {row.get('reference')} {field} too thin")
        if len(words(row.get("family"))) < 2:
            fail(f"source reader {row.get('reference')} family too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"source reader {row.get('reference')} needs three concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"source reader {row.get('reference')} references unknown concept ids: {missing}")

    paper_family_ledger_rows = data.get("paper_family_ledger_rows") or []
    if len(paper_family_ledger_rows) != len(references):
        fail("paper family ledger must cover every reference")
    if {row.get("reference") for row in paper_family_ledger_rows} != reference_ids:
        fail("paper family ledger references do not match reference ids")
    for row in paper_family_ledger_rows:
        if len(words(row.get("family"))) < 2:
            fail(f"paper family ledger {row.get('reference')} family too thin")
        for field in ["problem", "object", "allowed_reading", "protected_idea", "course_bridge", "overclaim", "reader_test"]:
            if len(words(row.get(field))) < 40:
                fail(f"paper family ledger {row.get('reference')} {field} too thin")
        if len(row.get("concepts") or []) < 3:
            fail(f"paper family ledger {row.get('reference')} needs concept links")
        missing = sorted(set(row.get("concepts") or []) - concept_ids)
        if missing:
            fail(f"paper family ledger {row.get('reference')} unknown concepts: {missing}")

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

    lecture_reconstruction_drills = data.get("lecture_reconstruction_drills") or []
    if len(lecture_reconstruction_drills) != 15:
        fail("lecture reconstruction drills need exactly fifteen drills")
    if {row.get("lecture") for row in lecture_reconstruction_drills} != lecture_numbers:
        fail("lecture reconstruction drills do not match lecture numbers")
    for row in lecture_reconstruction_drills:
        if len(row.get("rebuild_steps") or []) < 6:
            fail(f"lecture reconstruction drill {row.get('lecture')} needs six rebuild steps")
        for step in row.get("rebuild_steps") or []:
            if len(words(step)) < 30:
                fail(f"lecture reconstruction drill {row.get('lecture')} step too thin")
        for field in ["start_from", "self_check", "common_failure", "source_check"]:
            if len(words(row.get(field))) < 70:
                fail(f"lecture reconstruction drill {row.get('lecture')} {field} too thin")
        unknown_concepts = sorted(set(row.get("concepts") or []) - concept_ids)
        if unknown_concepts:
            fail(f"lecture reconstruction drill {row.get('lecture')} unknown concepts: {unknown_concepts}")
        if len(row.get("concepts") or []) < 3:
            fail(f"lecture reconstruction drill {row.get('lecture')} needs concept links")

    source_nuance_repairs = data.get("source_nuance_repairs") or []
    if len(source_nuance_repairs) != 15:
        fail("source nuance repairs need exactly fifteen lecture notes")
    if {row.get("lecture") for row in source_nuance_repairs} != lecture_numbers:
        fail("source nuance repairs do not match lecture numbers")
    for row in source_nuance_repairs:
        for field in ["caption_hazard", "safe_claim", "repair_move", "do_not_claim", "reviewer_question"]:
            if len(words(row.get(field))) < 70:
                fail(f"source nuance repair {row.get('lecture')} {field} too thin")
        unknown_concepts = sorted(set(row.get("concepts") or []) - concept_ids)
        if unknown_concepts:
            fail(f"source nuance repair {row.get('lecture')} unknown concepts: {unknown_concepts}")
        if len(row.get("concepts") or []) < 3:
            fail(f"source nuance repair {row.get('lecture')} needs concept links")

    html_files = sorted(SITE.glob("*.html"))
    if len(html_files) < 65:
        fail(f"expected at least 65 html pages after reader-checks pass, got {len(html_files)}")
    names = {p.name for p in html_files}
    for page in ["index.html", "videos.html", "lectures.html", "lecture-spine.html", "concepts.html", "themes.html", "subthemes.html", "families.html", "the-math-why.html", "math-playground.html", "course-synthesis.html", "application-spine.html", "concept-dependencies.html", "transfer-lab.html", "repair-clinic.html", "oral-exam.html", "change-ledger.html", "assumption-ledger.html", "counterexample-gallery.html", "weak-claim-repairs.html", "proof-moves.html", "formula-reader.html", "theorem-use-contracts.html", "concept-contrasts.html", "reader-checks.html", "term-translator.html", "paper-source-reader.html", "paper-family-ledger.html", "lecture-source-bridges.html", "lecture-reconstruction-drills.html", "source-nuance-repairs.html", "references.html", "quality-rubric.html", "rubric-coverage.html", "quality-audit.html", "source-audit.html"]:
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
    for phrase in ["Dependency Spine", "The One Engine", "Proof Families", "Applications Beyond Topology", "Physics and motion", "Robotics and mechanisms", "Engineering constraints", "Modeling choices", "Computing and networks", "Lecture Spine", "How To Read Any Page"]:
        if phrase not in deep_dive:
            fail(f"course synthesis missing section: {phrase}")
    if deep_dive.count("<article") < 30:
        fail("course synthesis needs dependency, family, and lecture cards")
    if len(words(re.sub(r"<[^>]+>", " ", deep_dive))) < 1400:
        fail("course synthesis too thin")
    application_page = (SITE / "application-spine.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Application Spine", "How To Read An Application", "The Application Test", "Physics and motion", "Robotics and mechanisms", "Engineering constraints", "Modeling choices", "Computing and networks", "Scientific measurement"]:
        if phrase not in application_page:
            fail(f"application spine page missing phrase: {phrase}")
    if application_page.count("<article") < 6:
        fail("application spine page needs six application cards")
    if len(words(re.sub(r"<[^>]+>", " ", application_page))) < 1200:
        fail("application spine page too thin")
    dependency_page = (SITE / "concept-dependencies.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Concept Dependencies", "Understand first", "Then read", "Why this dependency matters", "Reader check"]:
        if phrase not in dependency_page:
            fail(f"concept dependencies page missing phrase: {phrase}")
    if dependency_page.count("<article") < 8:
        fail("concept dependencies page needs eight dependency cards")
    if len(words(re.sub(r"<[^>]+>", " ", dependency_page))) < 850:
        fail("concept dependencies page too thin")
    transfer_lab = (SITE / "transfer-lab.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Transfer Lab", "Situation:", "Object:", "Allowed move:", "Protected fact:", "Course bridge:", "Wrong transfer:", "Reader task:", "The Transfer Test"]:
        if phrase not in transfer_lab:
            fail(f"transfer lab page missing phrase: {phrase}")
    if transfer_lab.count("<article") < 8:
        fail("transfer lab page needs eight cards")
    if len(words(re.sub(r"<[^>]+>", " ", transfer_lab))) < 1700:
        fail("transfer lab page too thin")
    repair_clinic = (SITE / "repair-clinic.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Repair Clinic", "Flawed explanation:", "Why it fails:", "Repair move:", "Strong version:", "Evidence test:", "The Repair Test"]:
        if phrase not in repair_clinic:
            fail(f"repair clinic page missing phrase: {phrase}")
    if repair_clinic.count("<article") < 8:
        fail("repair clinic page needs eight cards")
    if len(words(re.sub(r"<[^>]+>", " ", repair_clinic))) < 1700:
        fail("repair clinic page too thin")
    oral_exam = (SITE / "oral-exam.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Oral Exam", "Prompt:", "Strong answer:", "Must include:", "Common failure:", "Follow-up:", "The Passing Standard"]:
        if phrase not in oral_exam:
            fail(f"oral exam page missing phrase: {phrase}")
    if oral_exam.count("<article") < 7:
        fail("oral exam page needs seven cards")
    if len(words(re.sub(r"<[^>]+>", " ", oral_exam))) < 1500:
        fail("oral exam page too thin")
    change_ledger = (SITE / "change-ledger.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Change Ledger", "Object:", "Legal change:", "Protected fact:", "Why it matters:", "False move:", "Reader test:", "The Ledger Test"]:
        if phrase not in change_ledger:
            fail(f"change ledger page missing phrase: {phrase}")
    if change_ledger.count("<article") < 10:
        fail("change ledger page needs ten cards")
    if len(words(re.sub(r"<[^>]+>", " ", change_ledger))) < 2100:
        fail("change ledger page too thin")
    assumption_ledger = (SITE / "assumption-ledger.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Assumption Ledger", "Claim:", "Assumption:", "Why needed:", "Plain check:", "Breaks if:", "Course place:", "The Assumption Test"]:
        if phrase not in assumption_ledger:
            fail(f"assumption ledger page missing phrase: {phrase}")
    if assumption_ledger.count("<article") < 10:
        fail("assumption ledger page needs ten cards")
    if len(words(re.sub(r"<[^>]+>", " ", assumption_ledger))) < 2200:
        fail("assumption ledger page too thin")
    counterexample_gallery = (SITE / "counterexample-gallery.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Counterexample Gallery", "Tempting claim:", "Missing condition:", "Failure scene:", "Why it breaks:", "Repair:", "The Counterexample Test"]:
        if phrase not in counterexample_gallery:
            fail(f"counterexample gallery page missing phrase: {phrase}")
    if counterexample_gallery.count("<article") < 10:
        fail("counterexample gallery page needs ten cards")
    if len(words(re.sub(r"<[^>]+>", " ", counterexample_gallery))) < 2000:
        fail("counterexample gallery page too thin")
    weak_claim_repairs = (SITE / "weak-claim-repairs.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Weak Claim Repairs", "Weak claim:", "Why weak:", "First-principles repair:", "Detail to check:", "Where to use:", "The Repair Standard"]:
        if phrase not in weak_claim_repairs:
            fail(f"weak claim repairs page missing phrase: {phrase}")
    if weak_claim_repairs.count("<article") < 10:
        fail("weak claim repairs page needs ten cards")
    if len(words(re.sub(r"<[^>]+>", " ", weak_claim_repairs))) < 2100:
        fail("weak claim repairs page too thin")
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
    theorem_contract_page = (SITE / "theorem-use-contracts.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Theorem Use Contracts", "Use when:", "Object needed:", "Allowed move:", "Protected evidence:", "Conclusion it can force:", "Breaks if:", "Everyday test:", "The Misuse Test"]:
        if phrase not in theorem_contract_page:
            fail(f"theorem use contracts page missing phrase: {phrase}")
    if theorem_contract_page.count("<article") < 8:
        fail("theorem use contracts page needs eight cards")
    if len(words(re.sub(r"<[^>]+>", " ", theorem_contract_page))) < 1500:
        fail("theorem use contracts page too thin")
    concept_contrasts_page = (SITE / "concept-contrasts.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Concept Contrasts", "Confusion:", "Left job:", "Right job:", "Bridge:", "Failure test:", "Reader question:", "The Separation Test"]:
        if phrase not in concept_contrasts_page:
            fail(f"concept contrasts page missing phrase: {phrase}")
    if concept_contrasts_page.count("<article") < 10:
        fail("concept contrasts page needs ten cards")
    if len(words(re.sub(r"<[^>]+>", " ", concept_contrasts_page))) < 1500:
        fail("concept contrasts page too thin")
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
    paper_family_ledger_page = (SITE / "paper-family-ledger.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Paper Family Ledger", "Problem:", "Object:", "Allowed reading:", "Protected idea:", "Course bridge:", "Overclaim boundary:", "Reader test:", "The Paper-Family Test"]:
        if phrase not in paper_family_ledger_page:
            fail(f"paper family ledger missing phrase: {phrase}")
    if paper_family_ledger_page.count("<article") < 7:
        fail("paper family ledger needs seven source cards")
    if len(words(re.sub(r"<[^>]+>", " ", paper_family_ledger_page))) < 1650:
        fail("paper family ledger too thin")
    lecture_source_bridges_page = (SITE / "lecture-source-bridges.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Lecture Source Bridges", "Course demonstration:", "Mathematical bridge:", "How the source extends it:", "Overread warning:", "Reader question:", "The Transfer Test"]:
        if phrase not in lecture_source_bridges_page:
            fail(f"lecture source bridges page missing phrase: {phrase}")
    if lecture_source_bridges_page.count("<article") < 15:
        fail("lecture source bridges page needs fifteen cards")
    if len(words(re.sub(r"<[^>]+>", " ", lecture_source_bridges_page))) < 2400:
        fail("lecture source bridges page too thin")
    lecture_reconstruction_page = (SITE / "lecture-reconstruction-drills.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Lecture Reconstruction Drills", "Start from:", "Rebuild steps:", "Self-check:", "Common failure:", "Source check:", "The Readiness Test"]:
        if phrase not in lecture_reconstruction_page:
            fail(f"lecture reconstruction drills page missing phrase: {phrase}")
    if lecture_reconstruction_page.count("<article") < 15:
        fail("lecture reconstruction drills page needs fifteen cards")
    if lecture_reconstruction_page.count("<li>") < 90:
        fail("lecture reconstruction drills page needs ninety rebuild steps")
    if len(words(re.sub(r"<[^>]+>", " ", lecture_reconstruction_page))) < 3600:
        fail("lecture reconstruction drills page too thin")
    source_nuance_repairs_page = (SITE / "source-nuance-repairs.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Source Nuance Repairs", "Caption hazard:", "Safe claim:", "Repair move:", "Do not claim:", "Evidence check:", "The Source Repair Test"]:
        if phrase not in source_nuance_repairs_page:
            fail(f"source nuance repairs page missing phrase: {phrase}")
    if source_nuance_repairs_page.count("<article") < 15:
        fail("source nuance repairs page needs fifteen cards")
    if len(words(re.sub(r"<[^>]+>", " ", source_nuance_repairs_page))) < 2400:
        fail("source nuance repairs page too thin")
    references_page = (SITE / "references.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["References", "Source Caveat", "Why it belongs", "Use carefully", "Lecture coverage", "Concept coverage"]:
        if phrase not in references_page:
            fail(f"references page missing phrase: {phrase}")
    if references_page.count("<article") < 7:
        fail("references page needs seven reference cards")
    if len(words(re.sub(r"<[^>]+>", " ", references_page))) < 700:
        fail("references page too thin")
    quality_rubric_page = (SITE / "quality-rubric.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Quality Rubric", "How To Use The Rubric", "Completion Test", "Test:", "Complete answer:", "Failure:", "Repair:"]:
        if phrase not in quality_rubric_page:
            fail(f"quality rubric page missing phrase: {phrase}")
    if quality_rubric_page.count("<article") < 6:
        fail("quality rubric page needs six cards")
    if len(words(re.sub(r"<[^>]+>", " ", quality_rubric_page))) < 650:
        fail("quality rubric page too thin")
    rubric_coverage_page = (SITE / "rubric-coverage.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Rubric Coverage", "How To Read This Coverage", "Evidence Rule", "Reader test:", "Name the object before the term", "Name the legal move", "Name what survives", "Say what would break the claim", "Tie the idea to a course moment", "Replace formal words with everyday sentences"]:
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
        for phrase in ["First-Principles Long Essay", "Ordinary problem:", "Object on the page:", "Allowed change:", "Protected fact:", "Topology payoff:", "Outside use:", "Wrong use:", "Anchor Example", "Course moment:", "Principle:", "Reader question:", "Work It From Scratch", "Object:", "Operation:", "Protected fact:", "Breaks if:", "Where This Matters Outside Topology", "Outside problem:", "Topological use:", "Other fields:", "Why it matters:", "Honest limit:", "Can You Use It?", "Object check:", "Operation check:", "Protected fact check:", "Failure check:"]:
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
        for phrase in ["First-Principles Long Essay", "Ordinary problem:", "Object on the page:", "Allowed change:", "Protected fact:", "Topology payoff:", "Outside use:", "Wrong use:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing first-principles essay phrase {phrase}: {lecture_name}")
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
        for phrase in ["Why This Matters Beyond The Lecture", "Outside problem:", "Topology bridge:", "Protected fact:", "Where it matters:", "Honest limit:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing application bridge phrase {phrase}: {lecture_name}")
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
        for phrase in ["First-Principles Long Essay", "Ordinary problem:", "Object on the page:", "Allowed change:", "Protected fact:", "Topology payoff:", "Outside use:", "Wrong use:"]:
            if phrase not in theme_html:
                fail(f"theme page missing first-principles essay phrase {phrase}: {theme_name}")
        for phrase in ["Theme Lens", "Notices:", "Ignores:", "Changes the problem:", "Reader test:", "Why This Theme Matters Beyond The Course", "Outside problem:", "Course reading rule:", "Where it matters:", "Honest limit:", "Can You Carry The Theme?", "Notice answer:", "Ignore answer:", "Transfer answer:", "Test answer:"]:
            if phrase not in theme_html:
                fail(f"theme page missing lens phrase {phrase}: {theme_name}")
    for subtheme in data["subthemes"]:
        subtheme_name = f"subtheme-{subtheme['id']}.html"
        if subtheme_name not in names:
            fail(f"missing subtheme page {subtheme['id']}")
        subtheme_html = (SITE / subtheme_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["First-Principles Long Essay", "Ordinary problem:", "Object on the page:", "Allowed change:", "Protected fact:", "Topology payoff:", "Outside use:", "Wrong use:"]:
            if phrase not in subtheme_html:
                fail(f"subtheme page missing first-principles essay phrase {phrase}: {subtheme_name}")
        for phrase in ["First-Principles Bridge", "Course moment:", "Thinking shift:", "Reader test:", "Reading Routine", "Look for:", "Ask:", "Use:", "Mistake:", "Why This Subtheme Matters Beyond The Course", "Outside problem:", "Course reading rule:", "Where it matters:", "Honest limit:", "Can You Apply The Routine?", "Look answer:", "Ask answer:", "Use answer:", "Mistake answer:"]:
            if phrase not in subtheme_html:
                fail(f"subtheme page missing subtheme phrase {phrase}: {subtheme_name}")
    for family in data["families"]:
        family_name = f"family-{family['id']}.html"
        if family_name not in names:
            fail(f"missing family page {family['id']}")
        family_html = (SITE / family_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["First-Principles Long Essay", "Ordinary problem:", "Object on the page:", "Allowed change:", "Protected fact:", "Topology payoff:", "Outside use:", "Wrong use:"]:
            if phrase not in family_html:
                fail(f"family page missing first-principles essay phrase {phrase}: {family_name}")
        for phrase in ["Method Playbook", "Setup:", "Move:", "Payoff:", "Failure:", "Reader test:", "Method Contract", "Input:", "Action:", "Protected evidence:", "Output:", "Failure test:", "Why This Method Matters Beyond The Course", "Outside problem:", "Method transfer:", "Where it matters:", "Honest limit:", "Can You Use This Method?", "Input answer:", "Action answer:", "Evidence answer:", "Output answer:", "Failure answer:"]:
            if phrase not in family_html:
                fail(f"family page missing family phrase {phrase}: {family_name}")

    corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore").lower() for p in html_files)
    for phrase in FORBIDDEN:
        if re.search(rf"\b{re.escape(phrase)}\b", corpus):
            fail(f"forbidden phrase found: {phrase}")
    stale_rubric_phrases = [
        "the answer should",
        "the reader should",
        "a good answer",
        "a strong answer",
        "in everyday language, explain",
        "name the allowed move",
        "the recovered captions support",
        "begin with the live feature the page must expose",
        "turn that feature into the question the proof has to answer",
        "make the false shortcut explicit before accepting the page's conclusion",
        "the correction names what the page must check",
        "that question turns the subtheme into an inspection",
        "apply this routine only when it changes what the reader checks",
        "begin with the kind of evidence this theme trains the reader to see",
        "name the distracting detail the theme refuses to let carry the proof",
        "connect early and late lectures through the same proof work",
        "make the theme earn its place on the page",
        "the method starts with the situation it is allowed to act on",
        "the method has to become a concrete operation before the title carries any weight",
        "the protected evidence is the reason the operation speaks for the starting problem",
        "the result has to return to the original problem",
        "the bad use shows exactly where the method stops applying",
        "start from its own carrier before the name does any work",
        "turn the idea into a permitted action on the course example",
        "keep the surviving evidence in front of the conclusion",
        "make the nearest bad use visible",
        "say what has to be pictured first",
        "put the allowed change in plain words",
        "the guide is not a longer list of topics",
        "name the fact that survives the legal move",
        "state the evidence that comes through unchanged",
        "say what remains available after the action",
    ]
    for phrase in stale_rubric_phrases:
        if phrase in corpus:
            fail(f"stale rubric phrase found: {phrase}")

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
