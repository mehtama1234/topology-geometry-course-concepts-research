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
            if len(words(lens.get(field))) < 12:
                fail(f"theme {theme['id']} lens {field} too thin")

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
            if len(words(routine.get(field))) < 12:
                fail(f"subtheme {subtheme['id']} routine {field} too thin")
        bridge = subtheme.get("bridge") or {}
        for field in ["course_moment", "thinking_shift", "reader_test"]:
            if len(words(bridge.get(field))) < 14:
                fail(f"subtheme {subtheme['id']} bridge {field} too thin")

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
            if len(words(contract.get(field))) < 12:
                fail(f"family {family['id']} contract {field} too thin")
        playbook = family.get("playbook") or {}
        for field in ["setup", "move", "payoff", "failure", "reader_test"]:
            if len(words(playbook.get(field))) < 12:
                fail(f"family {family['id']} playbook {field} too thin")

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
            if len(words(workup.get(field))) < 12:
                fail(f"concept {concept['id']} workup {field} too thin")
        anchor = concept.get("anchor") or {}
        for field in ["course_moment", "principle", "reader_question"]:
            if len(words(anchor.get(field))) < 14:
                fail(f"concept {concept['id']} anchor {field} too thin")
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
            if len(words(deepening.get(field))) < 14:
                fail(f"lecture {lecture['lecture']} deepening {field} too thin")
        if len(deep.get("anchors") or []) < 4:
            fail(f"lecture {lecture['lecture']} needs transcript anchors")
        source_lens = deep.get("source_lens") or []
        if len(source_lens) < 2:
            fail(f"lecture {lecture['lecture']} needs source lens paragraphs")
        if sum(len(words(p)) for p in source_lens) < 60:
            fail(f"lecture {lecture['lecture']} source lens too thin")
        source_checkpoint = deep.get("source_checkpoint") or {}
        for field in ["trust", "do_not_overread", "math_question"]:
            if len(words(source_checkpoint.get(field))) < 12:
                fail(f"lecture {lecture['lecture']} source checkpoint {field} too thin")
        nuance = deep.get("caption_nuance") or {}
        if len(nuance.get("terms") or []) < 4:
            fail(f"lecture {lecture['lecture']} caption nuance needs four terms")
        for field in ["risk", "safe_reading", "verify_question"]:
            if len(words(nuance.get(field))) < 12:
                fail(f"lecture {lecture['lecture']} caption nuance {field} too thin")
        walkthrough = deep.get("walkthrough") or {}
        for field in ["start_here", "payoff", "reader_check"]:
            if len(words(walkthrough.get(field))) < 35:
                fail(f"lecture {lecture['lecture']} walkthrough {field} too thin")
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

    html_files = sorted(SITE.glob("*.html"))
    if len(html_files) < 65:
        fail(f"expected at least 65 html pages after reader-checks pass, got {len(html_files)}")
    names = {p.name for p in html_files}
    for page in ["index.html", "videos.html", "lectures.html", "lecture-spine.html", "concepts.html", "themes.html", "subthemes.html", "families.html", "the-math-why.html", "math-playground.html", "course-synthesis.html", "concept-dependencies.html", "proof-moves.html", "formula-reader.html", "reader-checks.html", "quality-audit.html", "source-audit.html"]:
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
    source_audit = (SITE / "source-audit.html").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Caption Nuance By Lecture", "Caption risk:", "Safe reading:", "Verify:", "Source checkpoint:"]:
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
        for phrase in ["Anchor Example", "Course moment:", "Principle:", "Reader question:", "Work It From Scratch", "Object:", "Operation:", "Protected fact:", "Breaks if:"]:
            if phrase not in concept_html:
                fail(f"concept page missing concept phrase {phrase}: {concept_name}")
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
        for phrase in ["Caption Nuance", "Caption risk:", "Safe reading:", "Verify:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing caption nuance phrase {phrase}: {lecture_name}")
        for phrase in ["Slow Walkthrough", "Start here:", "Mathematical payoff:", "Reader check:"]:
            if phrase not in lecture_html:
                fail(f"lecture page missing walkthrough phrase {phrase}: {lecture_name}")
    for theme in data["themes"]:
        theme_name = f"theme-{theme['id']}.html"
        if theme_name not in names:
            fail(f"missing theme page {theme['id']}")
        theme_html = (SITE / theme_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Theme Lens", "Notices:", "Ignores:", "Changes the problem:", "Reader test:"]:
            if phrase not in theme_html:
                fail(f"theme page missing lens phrase {phrase}: {theme_name}")
    for subtheme in data["subthemes"]:
        subtheme_name = f"subtheme-{subtheme['id']}.html"
        if subtheme_name not in names:
            fail(f"missing subtheme page {subtheme['id']}")
        subtheme_html = (SITE / subtheme_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["First-Principles Bridge", "Course moment:", "Thinking shift:", "Reader test:", "Reading Routine", "Look for:", "Ask:", "Use:", "Mistake:"]:
            if phrase not in subtheme_html:
                fail(f"subtheme page missing subtheme phrase {phrase}: {subtheme_name}")
    for family in data["families"]:
        family_name = f"family-{family['id']}.html"
        if family_name not in names:
            fail(f"missing family page {family['id']}")
        family_html = (SITE / family_name).read_text(encoding="utf-8", errors="ignore")
        for phrase in ["Method Playbook", "Setup:", "Move:", "Payoff:", "Failure:", "Reader test:", "Method Contract", "Input:", "Action:", "Protected evidence:", "Output:", "Failure test:"]:
            if phrase not in family_html:
                fail(f"family page missing family phrase {phrase}: {family_name}")

    corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore").lower() for p in html_files)
    for phrase in FORBIDDEN:
        if re.search(rf"\b{re.escape(phrase)}\b", corpus):
            fail(f"forbidden phrase found: {phrase}")

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
