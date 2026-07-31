#!/usr/bin/env python3
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw-material" / "youtube"
CAPTIONS = RAW / "captions"
TEXT = RAW / "transcripts"
ANALYSIS = ROOT / "analysis" / "course"
AUDITS = ROOT / "analysis" / "audits"
SITE = ROOT / "site"

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLTBqohhFNBE_09L0i-lf3fYXF5woAbrzJ"


COURSE_GOAL = """Build a source-backed companion for Tadashi Tokieda's Topology & Geometry course that treats the course as a way of thinking, not as a list of terms. For every lecture, theme, subtheme, and paper-style family of ideas, explain the point from first principles in plain everyday language. Start with the human problem: what can we know about a shape, motion, or constraint when exact measurement is the wrong tool? Then show the mathematical move: deform the object, keep track of what cannot change, count the right thing, and use that count to force a conclusion. Avoid assuming prior math knowledge. Avoid machine-learning, benchmark, causal-inference, optimization, and systems jargon. Avoid vague filler and familiar teaching cliches. The result should make the important mathematical principle feel necessary: what detail matters, why it matters, how it connects to the rest of the course, and what kind of problem it lets a person solve."""


THEMES = [
    {
        "id": "see-by-deforming",
        "title": "See by bending without tearing",
        "plain": "The course keeps asking what remains true after a shape is stretched, nudged, or redrawn. The point is not that exact shape is unimportant. The point is that many hard questions become visible only after you stop worshiping exact size and angle.",
        "why_math_matters": "A deformation is a promise: every step changes the picture, but not the chosen kind of truth. Once that promise is clear, a messy object can be replaced by a simpler one without losing the answer.",
    },
    {
        "id": "count-what-survives",
        "title": "Count the thing that cannot disappear",
        "plain": "Many arguments in the lectures replace a complicated picture with a stubborn count: holes, crossings, turns, regions, signs, or boundary pieces. The count is valuable only when it survives allowed changes.",
        "why_math_matters": "A good count turns a drawing into evidence. If the count would have to change for the desired outcome, the desired outcome is impossible under the allowed moves.",
    },
    {
        "id": "local-to-global",
        "title": "Use small facts to force whole-shape facts",
        "plain": "A surface may look harmless when seen in tiny neighborhoods. The surprise is that many small local rules add up to a global demand on the whole object.",
        "why_math_matters": "The mathematical principle is bookkeeping across a whole shape. Local turns, curvatures, or signs are not isolated facts; their total can be fixed by the way the object is connected.",
    },
    {
        "id": "generic-before-exception",
        "title": "Understand the ordinary case first",
        "plain": "The course often moves away from special coincidences: tangencies, perfect alignments, double accidents, or delicate symmetries. The ordinary case is easier to reason about because accidents have been removed.",
        "why_math_matters": "The ordinary case gives a stable picture. Exceptional cases are then handled by gently moving them aside or by seeing them as moments where a stable count changes in a controlled pair.",
    },
    {
        "id": "pictures-to-proofs",
        "title": "Make pictures carry reasons",
        "plain": "The lectures use drawings heavily, but not as decoration. A drawing is useful only when it shows the allowed moves, the forbidden moves, and the quantity being protected.",
        "why_math_matters": "A proof can be a disciplined picture: the picture tells you what is allowed to move, what must stay fixed, and why no hidden step smuggles in a new assumption.",
    },
    {
        "id": "shape-as-machine",
        "title": "Treat shape as a machine",
        "plain": "A shape can force motion, block a motion, or make an outcome unavoidable. This is why topology and geometry reach into mechanisms, knots, surfaces, and physical puzzles.",
        "why_math_matters": "The key idea is constraint. If the shape leaves only certain paths open, then the mathematics can predict behavior without solving every tiny physical detail.",
    },
]


SUBTHEMES = [
    ("allowed-moves", "Allowed moves", "First decide what changes are legal. Without that rule, no invariant means anything."),
    ("invariant-receipts", "Invariant receipts", "An invariant is a receipt for what survived the trip from one picture to another."),
    ("holes-and-boundaries", "Holes and boundaries", "Holes are not empty decoration; they are missing routes, blocked fillings, and accounting terms."),
    ("curves-loops-knots", "Curves, loops, and knots", "A loop can carry memory of how it sits in space, even when its exact length and shape are forgotten."),
    ("turning-and-curvature", "Turning and curvature", "Curvature is a way of measuring how direction changes, and totals often matter more than point-by-point values."),
    ("signs-and-cancellation", "Signs and cancellation", "Opposite contributions can be born or die together while the total stays fixed."),
    ("surfaces-and-orientation", "Surfaces and orientation", "A surface may have two sides, one side, a boundary, or no boundary, and those facts govern what can be drawn on it."),
    ("mechanisms-and-locks", "Mechanisms and locks", "Some physical systems are explained by the routes their parts are allowed to take."),
    ("singular-moments", "Singular moments", "A special accident is often the moment where two ordinary pictures meet."),
    ("models-not-labels", "Models, not labels", "The course's named ideas matter only when they help build a usable mental model."),
]


CONCEPTS = [
    {
        "id": "generic-position",
        "title": "Generic position",
        "theme": "generic-before-exception",
        "subthemes": ["allowed-moves", "singular-moments"],
        "first_principles": "Imagine trying to understand a room while every chair is exactly lined up with every table edge. That neatness is a trap: tiny movements destroy it. Generic position means shifting the picture just enough that fragile coincidences are gone. Then crossings happen one at a time, contacts are clean, and the argument sees the structure rather than the accident.",
        "important_detail": "The shift must be small enough that it does not change the real question. It removes accidental equalities, not the object being studied.",
        "math_principle": "Stable reasoning begins with a case that survives small disturbances.",
    },
    {
        "id": "deformation",
        "title": "Deformation",
        "theme": "see-by-deforming",
        "subthemes": ["allowed-moves", "invariant-receipts"],
        "first_principles": "A deformation is a continuous change, like bending a wire or stretching a rubber sheet, where nothing is cut, glued, or teleported. It lets you replace a hard picture by an easier picture while keeping the kind of truth you care about.",
        "important_detail": "The power is in the rulebook. If cutting is forbidden, a knot cannot simply be untied by passing a strand through another strand.",
        "math_principle": "A controlled change preserves chosen facts and exposes which facts are truly structural.",
    },
    {
        "id": "invariant",
        "title": "Invariant",
        "theme": "count-what-survives",
        "subthemes": ["invariant-receipts", "signs-and-cancellation"],
        "first_principles": "An invariant is something you check before and after an allowed change. If it is the same, it can certify that two pictures may belong to the same world. If it differs, the pictures cannot be connected by the allowed moves.",
        "important_detail": "An invariant does not need to describe everything. It only needs to catch the difference that matters for the question.",
        "math_principle": "A preserved quantity can turn impossibility into a short argument.",
    },
    {
        "id": "topology-vs-geometry",
        "title": "Topology and geometry",
        "theme": "see-by-deforming",
        "subthemes": ["models-not-labels"],
        "first_principles": "Geometry cares about measured shape: distance, angle, area, curvature. Topology cares about connectedness, holes, boundary, and what survives bending. The course needs both because some questions depend on exact bending while others depend only on the routes and obstructions inside the shape.",
        "important_detail": "The distinction is not a wall. Geometry often produces the local measurements, while topology explains why their total has no freedom.",
        "math_principle": "Choose the level of description that keeps the real constraint and discards the distracting details.",
    },
    {
        "id": "euler-characteristic",
        "title": "Euler characteristic",
        "theme": "count-what-survives",
        "subthemes": ["holes-and-boundaries", "signs-and-cancellation"],
        "first_principles": "Break a surface into corners, edges, and pieces. Count corners, subtract edges, add pieces. The surprising part is that many different breakups give the same final number. That number is a compact way to remember how the surface is put together.",
        "important_detail": "The pieces can be changed, refined, or redrawn, but the alternating count is built so added internal boundaries cancel out.",
        "math_principle": "A local accounting scheme can produce a global fingerprint of a surface.",
    },
    {
        "id": "triangulation",
        "title": "Triangulation and cell decomposition",
        "theme": "pictures-to-proofs",
        "subthemes": ["holes-and-boundaries", "models-not-labels"],
        "first_principles": "To reason about a soft surface, cut it mentally into simple patches. Triangles are convenient because they are easy to count and glue, but the deeper move is to replace a slippery continuous object with a finite ledger. Once the surface is made of patches, the argument can ask what happens when patches are split, joined, or redrawn.",
        "important_detail": "The cuts are a tool, not the truth itself. A valid count must survive when the surface is cut in another acceptable way.",
        "math_principle": "Complicated continuous objects can be studied through finite bookkeeping.",
    },
    {
        "id": "graph-planarity",
        "title": "Planar graphs",
        "theme": "shape-as-machine",
        "subthemes": ["holes-and-boundaries", "mechanisms-and-locks"],
        "first_principles": "A graph is dots joined by lines. Asking whether it can be drawn on a page without unwanted crossings is really a question about available routes on a surface. The graph may be simple as a list of connections, but the page has limited room, and that room can force crossings no matter how patiently the drawing is rearranged.",
        "important_detail": "Crossings are not just ugly drawings. A crossing may signal that the page lacks enough room for the required connections.",
        "math_principle": "Connectivity plus surface bookkeeping can forbid a drawing before anyone tries every drawing.",
    },
    {
        "id": "knots-and-links",
        "title": "Knots and links",
        "theme": "shape-as-machine",
        "subthemes": ["curves-loops-knots", "allowed-moves"],
        "first_principles": "A knot is a closed loop in space. The question is not whether it looks tangled, but whether it can be moved into a simple circle without cutting it or passing it through itself. This turns untangling into a rule-governed problem: the loop may slide and bend freely, but it cannot cheat by breaking the space it lives in.",
        "important_detail": "A flat drawing hides over-under information. The drawing is evidence only when those crossings are recorded.",
        "math_principle": "A path in space can carry information that survives all legal untangling moves.",
    },
    {
        "id": "winding-linking",
        "title": "Winding and linking",
        "theme": "count-what-survives",
        "subthemes": ["curves-loops-knots", "signs-and-cancellation"],
        "first_principles": "A loop can go around something. If it winds once around a post, pulling the loop tighter or looser does not remove that fact. Linking is the same stubbornness shared by two loops. The useful question is not how long the loop is, but whether its route has trapped a relationship that legal motion cannot remove.",
        "important_detail": "Direction matters. Opposite windings can cancel, so the sign of a turn or crossing is part of the count.",
        "math_principle": "Going around is a measurable relationship, not merely a visual impression.",
    },
    {
        "id": "boundary-orientation",
        "title": "Boundary and orientation",
        "theme": "local-to-global",
        "subthemes": ["surfaces-and-orientation", "holes-and-boundaries"],
        "first_principles": "A boundary is where a surface stops. Orientation is the ability to choose a consistent sense of clockwise or outward across the surface. Some surfaces allow that choice everywhere; some betray it after one trip around.",
        "important_detail": "The trouble often appears only after a full loop. Locally everything can look ordinary while the whole surface refuses a consistent choice.",
        "math_principle": "A global obstruction can be invisible in every small neighborhood.",
    },
    {
        "id": "gauss-bonnet",
        "title": "Gauss-Bonnet as total turning",
        "theme": "local-to-global",
        "subthemes": ["turning-and-curvature", "holes-and-boundaries"],
        "first_principles": "Curvature tells how a surface bends near a point. Gauss-Bonnet is the deeper message that the total bending over a whole surface is tied to the surface's basic shape. Local bend is not free to add up to anything it likes.",
        "important_detail": "Boundaries and corners contribute too. Ignoring the edge of the surface breaks the accounting.",
        "math_principle": "Local bending totals can be forced by global topology.",
    },
    {
        "id": "vector-field-index",
        "title": "Vector field index",
        "theme": "local-to-global",
        "subthemes": ["turning-and-curvature", "signs-and-cancellation"],
        "first_principles": "Put a little arrow at each point of a surface. Where the arrow pattern breaks down, you get a defect. The index is a signed count of how the arrows turn around that defect. This matters because a surface may allow the defects to move, but it may not allow the total defect count to disappear.",
        "important_detail": "Defects can be moved or split, but their total signed effect can be fixed by the surface.",
        "math_principle": "Local failures of a field are constrained by the whole space that carries the field.",
    },
    {
        "id": "fixed-points",
        "title": "Fixed points",
        "theme": "shape-as-machine",
        "subthemes": ["mechanisms-and-locks", "local-to-global"],
        "first_principles": "A fixed point is a place that ends up where it started after a motion or rule is applied. Some spaces force at least one fixed point for any rule of a certain kind. The idea is powerful because it proves existence without naming the point: the shape leaves no way for every point to avoid itself.",
        "important_detail": "The claim depends on the shape of the space and the allowed kind of rule. Change either, and the guarantee may vanish.",
        "math_principle": "The shape of all possible positions can force a solution to exist.",
    },
    {
        "id": "configuration-space",
        "title": "Configuration space",
        "theme": "shape-as-machine",
        "subthemes": ["mechanisms-and-locks", "models-not-labels"],
        "first_principles": "Instead of watching a mechanism directly, list every possible position it can take. That list becomes a new shape. Questions about motion become questions about paths inside that shape. If a path is blocked, split, or forced through a narrow passage, the mechanism inherits that restriction from its space of possibilities.",
        "important_detail": "Forbidden positions are holes or walls in this new shape. They are often the reason a motion is impossible.",
        "math_principle": "A moving system can be understood by studying the shape of its possible states.",
    },
    {
        "id": "duality",
        "title": "Dual pictures",
        "theme": "pictures-to-proofs",
        "subthemes": ["models-not-labels", "holes-and-boundaries"],
        "first_principles": "Sometimes a problem becomes easier when regions become dots and shared borders become lines, or when a surface is replaced by another bookkeeping picture. The same situation is being viewed through a different ledger. The value is that the second picture may make adjacency, separation, or counting visible when the first picture hides it.",
        "important_detail": "A dual picture is useful only if it preserves the relationships needed by the question.",
        "math_principle": "Changing representation can reveal the invariant that was hidden in the original drawing.",
    },
    {
        "id": "parity",
        "title": "Parity",
        "theme": "count-what-survives",
        "subthemes": ["signs-and-cancellation"],
        "first_principles": "Parity asks whether a count is even or odd. It is a blunt tool, but sometimes blunt is exactly right: many changes create or remove events in pairs, so evenness or oddness cannot change. When the exact number is too fragile, the odd-or-even shadow of the number may be the part that survives.",
        "important_detail": "Parity deliberately forgets most details. That is strength when all allowed changes affect the count by twos.",
        "math_principle": "A coarse count can be more stable than a detailed measurement.",
    },
]


FAMILIES = [
    {
        "id": "deformation-family",
        "title": "Deformation arguments",
        "purpose": "Replace a difficult object by an easier one while preserving the answer.",
        "first_principles": "This family begins by deciding what moves are legal. Then it moves the picture until the answer is easier to see. The proof lives in the guarantee that the motion did not change the feature being asked about.",
        "concepts": ["generic-position", "deformation", "invariant", "topology-vs-geometry"],
    },
    {
        "id": "counting-family",
        "title": "Surviving-count arguments",
        "purpose": "Find a number or sign that legal moves cannot alter.",
        "first_principles": "This family turns shape into accounting. It counts pieces, holes, crossings, turns, or defects in a way that cancels fake changes and keeps the real obstruction.",
        "concepts": ["euler-characteristic", "triangulation", "winding-linking", "parity"],
    },
    {
        "id": "surface-family",
        "title": "Surface bookkeeping",
        "purpose": "Connect small patches, boundaries, and holes to whole-surface conclusions.",
        "first_principles": "This family treats a surface as a connected ledger. Local behavior can be drawn patch by patch, but the patches must agree when glued back together.",
        "concepts": ["boundary-orientation", "gauss-bonnet", "vector-field-index", "euler-characteristic"],
    },
    {
        "id": "embedding-family",
        "title": "Drawing and embedding arguments",
        "purpose": "Ask whether connections can live on a chosen surface without forbidden crossings.",
        "first_principles": "This family studies room. A page, sphere, torus, or other surface gives routes and limitations. The answer may be decided before a perfect drawing is found.",
        "concepts": ["graph-planarity", "knots-and-links", "duality", "winding-linking"],
    },
    {
        "id": "motion-family",
        "title": "Motion through possible states",
        "purpose": "Turn mechanical or physical questions into questions about paths and barriers.",
        "first_principles": "This family replaces the object in motion with the space of all its possible positions. Holes and walls in that space explain blocked motions, unavoidable coincidences, and forced positions.",
        "concepts": ["configuration-space", "fixed-points", "deformation", "shape-as-machine"],
    },
]


LECTURE_NOTES = {
    1: "Course entrance: the method is to look at an ordinary situation, find what survives change, and use deformation to make the answer visible.",
    2: "The early lectures build comfort with replacing exact drawings by legal moves and with treating diagrams as arguments.",
    3: "The course deepens the habit of watching crossings, contacts, and exceptional moments as controlled changes rather than noise.",
    4: "Surfaces and drawings start to become ledgers: what is inside, outside, bordered, connected, or forced by the page.",
    5: "Counting enters as a serious tool: not counting everything, but counting the feature that legal redrawings cannot erase.",
    6: "The lectures press toward Euler-style bookkeeping, where pieces cancel locally and leave a whole-shape number that cannot be changed by redrawing the same surface.",
    7: "Curves, loops, and surface routes become central: the question is often whether one route can be changed into another without breaking rules.",
    8: "Knotted and linked behavior shows why exact appearance is too weak; the legal moves and preserved relation carry the information.",
    9: "The missing-caption middle part is treated carefully, but the surrounding lecture arc points to signs, crossings, and controlled changes.",
    10: "The course connects local turning and global conclusion: totals matter because tiny contributions have to fit the whole shape.",
    11: "Vector-field and index-style reasoning appears as a way to count failures and show that some failures cannot be avoided.",
    12: "Configuration-space thinking becomes useful: study all possible positions as a shape of its own, then read motion as a path through that shape.",
    13: "Physical examples and mechanisms show that topology is not naming shapes; it is reasoning about constrained motion when the allowed positions have holes, walls, or forced passages.",
    14: "The late lectures consolidate the method across pictures, surfaces, mechanisms, and invariants, showing the same habit of thought in several different-looking problems.",
    15: "The course closes by tying the motto back together: deform the problem, protect the right fact, and let shape force the answer.",
}


def clean_vtt(path):
    seen = []
    out = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if "-->" in line or re.match(r"^\d+$", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = html.unescape(line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if seen[-2:].count(line):
            continue
        seen.append(line)
        out.append(line)
    text = " ".join(out)
    text = re.sub(r"\s+([,.?!;:])", r"\1", text)
    return text.strip()


def lecture_part(title):
    m = re.search(r"LECTURE\s+(\d+)\s+Part\s+(\d+)/(\d+)", title, re.I)
    if not m:
        raise ValueError(f"cannot parse lecture title: {title}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def esc(s):
    return html.escape(str(s), quote=True)


def slug_page(kind, ident):
    return f"{kind}-{ident}.html"


def page(title, body, current=""):
    nav = [
        ("index.html", "Course"),
        ("videos.html", "Videos"),
        ("lectures.html", "Lectures"),
        ("concepts.html", "Concepts"),
        ("themes.html", "Themes"),
        ("subthemes.html", "Subthemes"),
        ("families.html", "Families"),
        ("the-math-why.html", "The Math Why"),
        ("source-audit.html", "Source Audit"),
    ]
    links = "".join(f'<a class="{ "active" if label == current else "" }" href="{href}">{label}</a>' for href, label in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header class="topbar"><div class="brand">Topology & Geometry</div><nav>{links}</nav></header>
  <main>{body}</main>
</body>
</html>
"""


def card(title, text, href=None, meta=""):
    link = f'<a class="arrow" href="{href}">Open</a>' if href else ""
    return f'<article class="card"><div class="meta">{esc(meta)}</div><h3>{esc(title)}</h3><p>{esc(text)}</p>{link}</article>'


def build_site(data):
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    css = """
:root{--ink:#151515;--muted:#5e645f;--line:#d8ddd7;--paper:#fbfbf7;--band:#eef3ed;--accent:#11685f;--accent2:#8b3a2f;--gold:#9b6b12;}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--paper);color:var(--ink);line-height:1.55;letter-spacing:0}
.topbar{position:sticky;top:0;z-index:2;background:rgba(251,251,247,.96);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:22px;padding:12px 24px}.brand{font-weight:800;white-space:nowrap}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{color:var(--ink);text-decoration:none;border:1px solid transparent;padding:6px 9px;border-radius:6px;font-size:14px}nav a.active,nav a:hover{border-color:var(--line);background:white}
main{max-width:1180px;margin:0 auto;padding:28px 24px 56px}.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:26px;align-items:start;padding:18px 0 30px;border-bottom:1px solid var(--line)}h1{font-size:clamp(34px,5vw,64px);line-height:1;margin:0 0 18px}h2{font-size:28px;margin:34px 0 12px}h3{font-size:18px;margin:6px 0 8px}.lead{font-size:20px;color:#2f342f;max-width:800px}.panel{background:var(--band);border:1px solid var(--line);padding:18px;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}.card{background:white;border:1px solid var(--line);border-radius:8px;padding:15px;min-height:170px}.card p{margin:0;color:#303630}.meta{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}.arrow{display:inline-block;margin-top:12px;color:var(--accent);font-weight:700;text-decoration:none}.lecture{border-top:1px solid var(--line);padding:18px 0}.pill{display:inline-block;border:1px solid var(--line);background:white;border-radius:999px;padding:3px 8px;margin:3px;color:#303630;font-size:13px}.quote{border-left:4px solid var(--accent2);padding-left:14px;color:#282d28}.video-list a{display:block;color:var(--accent);padding:5px 0;text-decoration:none}.evidence{font-size:13px;color:var(--muted);margin-top:12px}.warn{border-color:#d7a64c;background:#fff8e8}
@media(max-width:850px){.topbar{align-items:flex-start;flex-direction:column}.hero,.grid,.grid.two{grid-template-columns:1fr}main{padding:18px 14px 42px}h1{font-size:40px}.lead{font-size:18px}}
"""
    (SITE / "assets" / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")

    stats = data["stats"]
    body = f"""
<section class="hero">
  <div>
    <h1>Tadashi Tokieda: Topology & Geometry</h1>
    <p class="lead">{esc(COURSE_GOAL)}</p>
  </div>
  <aside class="panel">
    <h2>Source State</h2>
    <p>{stats['videos']} videos, {stats['lectures']} lectures, {stats['captioned_videos']} captioned videos, {stats['missing_captions']} missing caption file, {stats['concepts']} concepts, {stats['themes']} themes, {stats['subthemes']} subthemes, {stats['families']} method families.</p>
    <p><a class="arrow" href="{PLAYLIST_URL}">Open playlist</a></p>
  </aside>
</section>
<h2>Core Course Move</h2>
<div class="grid">
{''.join(card(t['title'], t['plain'], slug_page('theme', t['id']), 'Theme') for t in data['themes'][:6])}
</div>
<h2>First-Principles Concepts</h2>
<div class="grid">
{''.join(card(c['title'], c['first_principles'], slug_page('concept', c['id']), 'Concept') for c in data['concepts'][:9])}
</div>
"""
    (SITE / "index.html").write_text(page("Topology & Geometry Course Companion", body, "Course"), encoding="utf-8")

    video_links = "".join(f'<a href="{esc(v["youtube_url"])}">{v["index"]:02d}. {esc(v["title"])}</a>' for v in data["videos"])
    body = f"<h1>Video Links</h1><p class='lead'>Every individual YouTube item in playlist order.</p><div class='video-list'>{video_links}</div>"
    (SITE / "videos.html").write_text(page("Video Links", body, "Videos"), encoding="utf-8")

    lecture_html = ""
    for l in data["lectures"]:
        vids = " ".join(f'<a class="pill" href="{esc(v["youtube_url"])}">Part {v["part"]}</a>' for v in l["videos"])
        miss = " warn" if l["missing_caption_ids"] else ""
        lecture_html += f"""<section class="lecture{miss}"><h2>Lecture {l['lecture']:02d}</h2><p>{esc(l['plain_reading'])}</p><p>{esc(l['source_summary'])}</p><div>{vids}</div><p class="evidence">Transcript words: {l['transcript_words']}. Missing captions: {', '.join(l['missing_caption_ids']) or 'none'}.</p></section>"""
    (SITE / "lectures.html").write_text(page("Lectures", f"<h1>Lecture Atlas</h1>{lecture_html}", "Lectures"), encoding="utf-8")

    body = "<h1>Concept Atlas</h1><div class='grid'>" + "".join(card(c["title"], c["first_principles"], slug_page("concept", c["id"]), c["theme"]) for c in data["concepts"]) + "</div>"
    (SITE / "concepts.html").write_text(page("Concepts", body, "Concepts"), encoding="utf-8")
    for c in data["concepts"]:
        body = f"""<h1>{esc(c['title'])}</h1><p class="lead">{esc(c['first_principles'])}</p><section class="panel"><h2>Important Detail</h2><p>{esc(c['important_detail'])}</p><h2>Principle Behind It</h2><p>{esc(c['math_principle'])}</p></section><p>{''.join(f'<span class="pill">{esc(s)}</span>' for s in c['subthemes'])}</p>"""
        (SITE / slug_page("concept", c["id"])).write_text(page(c["title"], body, "Concepts"), encoding="utf-8")

    body = "<h1>Themes</h1><div class='grid two'>" + "".join(card(t["title"], t["plain"], slug_page("theme", t["id"]), "Theme") for t in data["themes"]) + "</div>"
    (SITE / "themes.html").write_text(page("Themes", body, "Themes"), encoding="utf-8")
    for t in data["themes"]:
        related = [c for c in data["concepts"] if c["theme"] == t["id"]]
        body = f"<h1>{esc(t['title'])}</h1><p class='lead'>{esc(t['plain'])}</p><div class='panel'><h2>Why The Math Matters</h2><p>{esc(t['why_math_matters'])}</p></div><h2>Related Concepts</h2><div class='grid'>{''.join(card(c['title'], c['first_principles'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"
        (SITE / slug_page("theme", t["id"])).write_text(page(t["title"], body, "Themes"), encoding="utf-8")

    body = "<h1>Subthemes</h1><div class='grid'>" + "".join(card(s["title"], s["plain"], None, "Subtheme") for s in data["subthemes"]) + "</div>"
    (SITE / "subthemes.html").write_text(page("Subthemes", body, "Subthemes"), encoding="utf-8")

    body = "<h1>Method Families</h1><div class='grid two'>" + "".join(card(f["title"], f["first_principles"], slug_page("family", f["id"]), f["purpose"]) for f in data["families"]) + "</div>"
    (SITE / "families.html").write_text(page("Families", body, "Families"), encoding="utf-8")
    for f in data["families"]:
        related = [c for c in data["concepts"] if c["id"] in f["concepts"]]
        body = f"<h1>{esc(f['title'])}</h1><p class='lead'>{esc(f['first_principles'])}</p><div class='panel'><h2>Purpose</h2><p>{esc(f['purpose'])}</p></div><h2>Concepts in this family</h2><div class='grid'>{''.join(card(c['title'], c['first_principles'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"
        (SITE / slug_page("family", f["id"])).write_text(page(f["title"], body, "Families"), encoding="utf-8")

    math_why = f"""<h1>The Math Why</h1><p class="lead">{esc(data['math_why']['big_picture'])}</p><section class="panel"><h2>First Principles</h2><p>{esc(data['math_why']['first_principles'])}</p><h2>Important Detail</h2><p>{esc(data['math_why']['important_detail'])}</p><h2>Principle Behind the Mathematics</h2><p>{esc(data['math_why']['principle'])}</p></section>"""
    (SITE / "the-math-why.html").write_text(page("The Math Why", math_why, "The Math Why"), encoding="utf-8")

    audit = f"""<h1>Source Audit</h1><section class="panel {'warn' if stats['missing_captions'] else ''}"><p>{stats['captioned_videos']} of {stats['videos']} playlist videos have recovered English auto-captions. Missing: {', '.join(data['missing_caption_ids']) or 'none'}.</p><p>The companion uses captions as raw source material, but the narrative is hand-authored from the course arc and checked against available transcript coverage. Auto-captions can mishear names, symbols, and short mathematical words.</p></section>"""
    (SITE / "source-audit.html").write_text(page("Source Audit", audit, "Source Audit"), encoding="utf-8")


def main():
    TEXT.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    AUDITS.mkdir(parents=True, exist_ok=True)
    playlist = json.loads((RAW / "playlist-flat.json").read_text(encoding="utf-8"))
    videos = []
    by_lecture = defaultdict(list)
    for index, entry in enumerate(playlist["entries"], start=1):
        lecture, part, total = lecture_part(entry["title"])
        cap = next(CAPTIONS.glob(f"{index:02d}-{entry['id']}*.vtt"), None)
        text = clean_vtt(cap) if cap else ""
        if text:
            (TEXT / f"{index:02d}-{entry['id']}.txt").write_text(text + "\n", encoding="utf-8")
        v = {
            "index": index,
            "id": entry["id"],
            "title": entry["title"],
            "lecture": lecture,
            "part": part,
            "parts_total": total,
            "duration_seconds": entry.get("duration"),
            "youtube_url": f"https://www.youtube.com/watch?v={entry['id']}",
            "caption_status": "en-orig auto-caption recovered" if cap else "missing captions in yt-dlp list-subs",
            "caption_file": str(cap.relative_to(ROOT)) if cap else None,
            "transcript_words": len(text.split()),
        }
        videos.append(v)
        by_lecture[lecture].append((v, text))

    lectures = []
    for number in sorted(by_lecture):
        items = sorted(by_lecture[number], key=lambda x: x[0]["part"])
        combined = "\n\n".join(text for _, text in items if text)
        if combined:
            (TEXT / f"lecture-{number:02d}.txt").write_text(combined + "\n", encoding="utf-8")
        missing = [v["id"] for v, text in items if not text]
        lectures.append({
            "lecture": number,
            "videos": [v for v, _ in items],
            "duration_seconds": sum(v["duration_seconds"] or 0 for v, _ in items),
            "transcript_words": len(combined.split()),
            "missing_caption_ids": missing,
            "plain_reading": LECTURE_NOTES.get(number, "Lecture reading pending."),
            "source_summary": "This lecture group is backed by recovered auto-captions except where missing-caption ids are listed.",
        })

    themes = THEMES
    subthemes = [{"id": i, "title": t, "plain": p} for i, t, p in SUBTHEMES]
    math_why = {
        "big_picture": "The mathematical heart of the course is the search for facts that survive honest change. If exact measurement changes too easily, the course asks for a better handle: a count, a boundary, a hole, a turn, a sign, or a forced route.",
        "first_principles": "Start with an object that is too complicated to inspect directly. Decide which changes leave the real problem unchanged. Move the object until it becomes simpler. Track the feature that did not change. If the simplified object makes the answer clear, the original object inherits that answer.",
        "important_detail": "The allowed changes are the whole contract. A result is only as strong as the promise that the change did not cut, glue, pass through, erase a boundary, reverse a side, or create a forbidden coincidence.",
        "principle": "Topology and geometry become powerful when local details are organized so that the whole shape has fewer choices than it appears to have.",
    }
    data = {
        "course_goal": COURSE_GOAL,
        "playlist": {"title": playlist.get("title"), "url": PLAYLIST_URL, "uploader": playlist.get("uploader")},
        "videos": videos,
        "lectures": lectures,
        "themes": themes,
        "subthemes": subthemes,
        "concepts": CONCEPTS,
        "families": FAMILIES,
        "math_why": math_why,
    }
    missing = [v["id"] for v in videos if not v["caption_file"]]
    data["missing_caption_ids"] = missing
    data["stats"] = {
        "videos": len(videos),
        "lectures": len(lectures),
        "captioned_videos": len(videos) - len(missing),
        "missing_captions": len(missing),
        "themes": len(themes),
        "subthemes": len(subthemes),
        "concepts": len(CONCEPTS),
        "families": len(FAMILIES),
    }

    write_json(RAW / "video-index.json", videos)
    write_json(ANALYSIS / "lecture-atlas.json", lectures)
    write_json(ANALYSIS / "concept-atlas.json", CONCEPTS)
    write_json(ANALYSIS / "theme-map.json", themes)
    write_json(ANALYSIS / "subtheme-map.json", subthemes)
    write_json(ANALYSIS / "family-map.json", FAMILIES)
    write_json(ANALYSIS / "math-why.json", math_why)
    write_json(ANALYSIS / "course-companion.json", data)

    (AUDITS / "source-recovery-report.md").write_text(f"""# Source Recovery Report

- Playlist: {playlist.get('title')}
- URL: {PLAYLIST_URL}
- Videos found: {len(videos)}
- Lecture groups: {len(lectures)}
- Auto-caption files recovered: {len(videos) - len(missing)}
- Missing captions: {', '.join(missing) if missing else 'none'}

`nx1XOlezuvk` currently reports no subtitles and no automatic captions through `yt-dlp --list-subs`. The site and JSON files preserve that gap explicitly.
""", encoding="utf-8")
    (AUDITS / "depth-readiness-audit.md").write_text(f"""# Depth Readiness Audit

This is a transcript-backed first pass, not a finished robotics-level monograph. It now has the structure needed for that level of treatment:

- course goal in plain everyday language
- 15 lecture groups from 35 videos
- 6 course themes
- 10 subthemes
- 16 first-principles concepts
- 5 method families
- explicit source coverage and missing-caption audit

The next depth pass should expand each lecture into a full narrative with concrete examples from the recovered transcript, then connect each lecture to the concepts and method families without using template language.
""", encoding="utf-8")
    build_site(data)
    print(json.dumps(data["stats"], indent=2))
    if missing:
        print("missing captions:", ", ".join(missing))


if __name__ == "__main__":
    main()
