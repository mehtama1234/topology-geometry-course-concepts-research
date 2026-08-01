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
        if theme_essay_words < 190:
            fail(f"theme {theme['id']} essay too thin")

    for subtheme in data["subthemes"]:
        depth = subtheme.get("depth") or {}
        for field in ["problem", "first_principles", "course_role"]:
            if len(words(depth.get(field))) < 30:
                fail(f"subtheme {subtheme['id']} depth {field} too thin")
        subtheme_essay_words = sum(len(words(p)) for p in subtheme.get("essay") or [])
        if subtheme_essay_words < 130:
            fail(f"subtheme {subtheme['id']} essay too thin")

    for family in data["families"]:
        depth = family.get("depth") or {}
        for field in ["human_problem", "first_principles", "how_it_works", "course_examples", "failure_mode"]:
            if len(words(depth.get(field))) < 35:
                fail(f"family {family['id']} depth {field} too thin")
        family_essay_words = sum(len(words(p)) for p in family.get("essay") or [])
        if family_essay_words < 130:
            fail(f"family {family['id']} essay too thin")

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
        if concept_essay_words < 180:
            fail(f"concept {concept['id']} essay too thin")
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
        if len(deep.get("anchors") or []) < 4:
            fail(f"lecture {lecture['lecture']} needs transcript anchors")
        source_lens = deep.get("source_lens") or []
        if len(source_lens) < 2:
            fail(f"lecture {lecture['lecture']} needs source lens paragraphs")
        if sum(len(words(p)) for p in source_lens) < 60:
            fail(f"lecture {lecture['lecture']} source lens too thin")
        essay_words = sum(len(words(p)) for p in deep.get("essay") or [])
        if essay_words < 230:
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

    html_files = sorted(SITE.glob("*.html"))
    if len(html_files) < 65:
        fail(f"expected at least 65 html pages after reader-checks pass, got {len(html_files)}")
    names = {p.name for p in html_files}
    for page in ["index.html", "videos.html", "lectures.html", "concepts.html", "themes.html", "subthemes.html", "families.html", "the-math-why.html", "math-playground.html", "course-synthesis.html", "formula-reader.html", "reader-checks.html", "quality-audit.html", "source-audit.html"]:
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
    for concept in data["concepts"]:
        if f"concept-{concept['id']}.html" not in names:
            fail(f"missing concept page {concept['id']}")
    for lecture in data["lectures"]:
        lecture_name = f"lecture-{lecture['lecture']:02d}.html"
        if lecture_name not in names:
            fail(f"missing lecture page {lecture['lecture']:02d}")
        lecture_html = (SITE / lecture_name).read_text(encoding="utf-8", errors="ignore")
        if "Source Lens" not in lecture_html:
            fail(f"lecture page missing source lens: {lecture_name}")
    for theme in data["themes"]:
        if f"theme-{theme['id']}.html" not in names:
            fail(f"missing theme page {theme['id']}")
    for subtheme in data["subthemes"]:
        if f"subtheme-{subtheme['id']}.html" not in names:
            fail(f"missing subtheme page {subtheme['id']}")
    for family in data["families"]:
        if f"family-{family['id']}.html" not in names:
            fail(f"missing family page {family['id']}")

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
