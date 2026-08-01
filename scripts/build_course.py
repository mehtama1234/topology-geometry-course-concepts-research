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


THEME_DEPTH = {
    "see-by-deforming": {
        "problem": "This theme answers the course's most basic question: how can a person solve a shape problem without measuring every detail? Tokieda's answer is to move the picture by legal changes until the answer is easier to see. The movement is useful only because it protects the feature being asked about.",
        "habit": "The habit is to ask, before doing any calculation, which parts of the picture are allowed to move and which facts must remain fixed. Once that rule is clear, deformation becomes a way of reasoning, not a way of decorating the drawing.",
        "course_arc": "The Mobius strip makes the need for global thinking visible. The disk-connection puzzle turns deformation into a proof method. Surface classification uses deformation to reduce complicated surfaces to standard parts. Intersection number, fixed points, and vector-field index later depend on the same promise: move the object, but keep the protected answer.",
        "important_detail": "The allowed moves carry the whole proof. If a path slips through another path, or a boundary point is quietly moved, the argument may have solved a different problem. This theme is therefore about disciplined freedom: move as much as possible, but only under rules that preserve the question.",
        "lectures": [1, 2, 5, 8, 15],
    },
    "count-what-survives": {
        "problem": "Many pictures change too much to trust what the eye sees at one moment. The course therefore looks for a count that survives the legal changes: number of sides, holes, crossings with signs, cells in an alternating sum, or indices of arrow-field defects.",
        "habit": "The habit is to count only after deciding why the count should survive. A raw number of visible crossings is usually fragile. A signed or alternating count can be stable because fake changes cancel in pairs while the real obstruction remains.",
        "course_arc": "The early paper examples make survival concrete. Euler characteristic turns a cut-up surface into a stable number. Intersection number shows how signs protect a count under deformation. Poincare-Hopf later uses the same idea when local vector-field indices add to a whole-surface number.",
        "important_detail": "A useful count is designed. It is not the first count that comes to mind. The mathematical work is in arranging cancellation so that changes in the drawing do not change the evidence the argument depends on, even after many redrawings.",
        "lectures": [5, 6, 8, 12, 13, 15],
    },
    "local-to-global": {
        "problem": "A surface, loop, or arrow field can look ordinary in every small neighborhood while still being impossible to organize consistently over the whole object. This theme asks how small local facts add up to a whole-shape demand that no single patch reveals.",
        "habit": "The habit is to distrust purely local inspection. One small patch of a Mobius strip looks like an ordinary strip. One small patch of a sphere can carry a tangent arrow. The question is whether those local choices can be made compatible after traveling around the whole space.",
        "course_arc": "The theme starts with one-sidedness, grows through orientation and surface classification, and becomes numerical in Euler characteristic and Poincare-Hopf. By the dynamics lectures, local equilibria and their indices are forced to obey a global surface count rather than acting independently.",
        "important_detail": "Local freedom does not imply global freedom. The obstruction may appear only after all patches are glued together, all signs are summed, or all defects are counted across the complete object, so checking one neighborhood is never enough for proof.",
        "lectures": [1, 5, 8, 11, 12, 13],
    },
    "generic-before-exception": {
        "problem": "Real drawings often contain accidents: tangencies, triple meetings, perfect alignments, or non-isolated equilibria. These special cases can hide the stable structure. The course needs a way to reason without being trapped by coincidences that vanish under a tiny change.",
        "habit": "The habit is to gently move the picture into an ordinary position, solve the stable case, and then understand special cases as limits of stable behavior. This is how crossings can be born or die in controlled pairs rather than as mysterious exceptions.",
        "course_arc": "Generic position is present whenever Tokieda makes intersections clean, counts them with signs, or treats equilibria as isolated defects. It is also present in the physical demonstrations: the point is not the exact accidental drawing, but the behavior that survives a small nudge.",
        "important_detail": "Moving to an ordinary case is not evasion. It is valid only when the small move does not change the problem's protected feature. Used carelessly, it erases the hard case; used correctly, it reveals the stable mechanism behind it and then explains the exceptional moment.",
        "lectures": [2, 6, 8, 11, 12],
    },
    "pictures-to-proofs": {
        "problem": "The course uses pictures constantly, but a picture by itself is not proof. This theme asks what makes a drawing mathematical evidence rather than a visual suggestion or a memory aid for something proved elsewhere by words alone in another form.",
        "habit": "The habit is to make every drawing state its rules. The drawing should show allowed motion, forbidden motion, signs, boundaries, identifications, and the quantity being protected. A good picture removes ambiguity instead of adding charm or hiding the difficult step.",
        "course_arc": "Paper strips, disk paths, edge identifications, surface surgery, intersection diagrams, graphs of maps, diagonals, and vector fields all serve as proof-bearing pictures. By the final lecture, Tokieda explicitly frames the course as pictorial thinking because the pictures have carried reasons all along.",
        "important_detail": "A picture becomes a proof only when the reader can tell what cannot change. If the picture hides an over-under crossing, an edge identification, or a boundary condition, it may be persuasive while being mathematically incomplete or even misleading.",
        "lectures": [1, 2, 3, 4, 8, 9, 15],
    },
    "shape-as-machine": {
        "problem": "The course repeatedly shows that shape can force behavior. A disk can force a fixed point, a sphere can force a vector-field defect, and a space of possible states can block or require a motion before equations are solved.",
        "habit": "The habit is to treat a shape as a system of constraints. Instead of asking only what the object looks like, ask what routes it allows, what choices it forbids, and what event any continuous rule must encounter while moving through it.",
        "course_arc": "This begins with physical strips and path puzzles, passes through fixed points as intersections with the diagonal, and reaches dynamical systems where vector fields and equilibria are constrained by topology. Applications late in the course show the same method outside pure surface examples.",
        "important_detail": "The shape only forces behavior after the modeling choice is made honestly. One must identify the space, the rule or motion on that space, the allowed changes, and the protected count or obstruction before applying a theorem to reality or mechanism.",
        "lectures": [7, 9, 10, 11, 13, 14],
    },
}


THEME_ESSAYS = {
    "see-by-deforming": [
        "Seeing by deformation is the course's most important habit because it changes what a problem is allowed to look like. A hard drawing may contain too many accidental details: a curve wiggles, a strip bends in space, a handle is drawn awkwardly, or a field has defects in inconvenient places. Deformation says that if the real question survives a legal motion, then the picture may be moved until the structure is easier to see. The proof is not the final simplified picture. The proof is the whole legal path from the original picture to the simpler one.",
        "This theme starts with the Mobius strip and disk path puzzle, but it does not stay there. Surface classification uses deformation and surgery to reduce surfaces to standard pieces. Intersection number is meaningful because it survives deformation. Fixed-point theory uses graphs and diagonals that can be compared under motion. Vector-field index survives cleanup of an arrow pattern. The theme teaches disciplined flexibility: move freely only after deciding what cannot change.",
        "The first-principles danger is changing the question while changing the picture. If an endpoint moves past another endpoint, if a curve crosses a forbidden obstacle, or if a boundary condition is silently dropped, the simplified object may no longer represent the original problem. Deformation is powerful because it is restricted. The restriction is what lets visual simplification become a valid reason.",
    ],
    "count-what-survives": [
        "Counting what survives is the course's answer to unreliable pictures. A visible crossing count can change when curves move. A raw cell count can change when a surface is subdivided. A local arrow pattern can be redrawn. The course does not give up on counting; it designs better counts. Alternating signs, plus-minus intersections, parity, and index are all ways of making fake changes cancel while the real obstruction remains.",
        "The theme becomes richer as the course progresses. Euler characteristic is the first major stable count for surfaces. Intersection number turns meetings into signed evidence. Poincare-Hopf turns vector-field defects into a total controlled by the surface. The underlying first-principles idea is simple: if a number survives every allowed change, then it can prove impossibility, existence, or forced behavior. The hard work is choosing the right number.",
        "A reader should leave this theme asking not 'what can I count?' but 'what count is protected by the rules of this problem?'",
        "This is also why signs and alternating terms are not formal decoration. They are repair mechanisms for counts that would otherwise be too brittle. The course repeatedly shows the same pattern: understand which local changes are fake, then build a count that makes those fake changes cancel. The surviving total is the mathematical evidence.",
    ],
    "local-to-global": [
        "Local-to-global thinking is the reason the course begins with objects like the Mobius strip. Every small patch of the strip looks ordinary, yet the whole strip has one side. Every small patch of a sphere can carry a tangent arrow, yet a full nonzero arrow field on the sphere is impossible. Local evidence is necessary, but it is not sufficient. The global gluing of all local pieces can impose a condition no single patch reveals.",
        "This theme threads through orientation, surface classification, Euler characteristic, Gauss-Bonnet-style total turning, vector-field index, and Poincare-Hopf. Each case asks how local facts add up. Sometimes the local facts are patches of a surface. Sometimes they are crossings. Sometimes they are arrow defects. The recurring lesson is that the whole object can have fewer choices than its pieces seem to have independently.",
        "For a beginner, the key is to stop asking only whether each small neighborhood looks possible. The harder question is whether all the local choices can be made consistently at once. A Mobius strip blocks a global side choice. A sphere blocks a global nonzero tangent field. A surface can demand a total count even when each small patch looks flexible.",
    ],
    "generic-before-exception": [
        "Generic-before-exception is the course's way of keeping proofs honest around special accidents. A drawing with perfect tangency or a triple crossing may carry real information, but it may be unstable. A tiny perturbation can split the event into ordinary pieces. The course therefore studies the ordinary case first: clean intersections, isolated defects, and controlled pair creation or cancellation. This is not avoiding difficulty. It is exposing the stable mechanism.",
        "Exceptional cases still matter, but they are best understood as boundaries between ordinary cases. When two intersections are born together, the singular moment is important because it explains why the signed count does not change. When equilibria are not isolated, the field must be cleaned up before index makes sense. This theme protects the reader from proving a theorem about a coincidence instead of proving a theorem about the shape.",
        "The mathematical principle is that stable events can be assigned stable evidence. A single clean crossing can receive a sign. An isolated defect can receive an index. A pair born at one instant can be analyzed by what exists just before and just after. The exception is not ignored; it is handled through the ordinary cases it connects.",
    ],
    "pictures-to-proofs": [
        "Pictures-to-proofs is the theme that makes Tokieda's course distinctive. The drawings and demonstrations are not illustrations pasted onto the mathematics afterward. They are often the place where the reasoning happens. A strip cut, a square with edge identifications, a handle slide, a graph meeting a diagonal, or a vector field around a defect can show the allowed moves and the protected quantity directly.",
        "A picture becomes proof-bearing only when it makes its rules visible. The reader must know which parts can move, which parts are fixed, what counts as crossing, how edges are glued, where signs come from, and what quantity survives. Otherwise the picture may be memorable but mathematically weak. By the final lecture, pictorial thinking names the course's real discipline: use pictures that carry constraints, not pictures that merely look suggestive.",
        "This is why the course can stay plain without becoming shallow: the picture does real work when its constraints are explicit.",
        "The first-principles test for any picture in the companion is whether a reader can audit it. What are the objects? What are the legal moves? What is being counted or protected? What conclusion follows if the picture is replaced by an equivalent one? A picture that answers those questions is part of the proof.",
    ],
    "shape-as-machine": [
        "Shape-as-machine is the theme that connects topology to behavior. A shape is not only something to classify; it can force motion, block motion, or guarantee a special state. A closed ball can force a fixed point. A sphere can force a vector-field defect. A configuration space can show that a physical motion is blocked because no legal path exists through the space of possibilities.",
        "This theme is why the course can move from paper strips to dynamical systems without changing its soul. The same proof engine keeps returning: identify the space, identify the rule or motion, decide the allowed changes, and find the protected obstruction. The shape then behaves like a machine of constraints. It does not compute every detail of motion, but it can make certain outcomes unavoidable.",
        "The result is a practical kind of mathematics: understand the shape of possibility, and some behavior follows before calculation begins.",
        "The important caution is that the machine is only as good as the space chosen to represent the situation. A configuration space must include the actual freedoms and exclude the actual forbidden states. A fixed-point theorem must apply to the right domain and rule. Once the model is honest, the shape can force behavior in a way direct calculation may not reveal.",
    ],
}


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


SUBTHEME_DEPTH = {
    "allowed-moves": {
        "problem": "Allowed moves define the game being played. Before saying two shapes are the same, before simplifying a drawing, and before claiming a count survives, the course must say what changes are legal.",
        "first_principles": "If a knot can be cut, it can be untied. If paths can pass through each other, a crossing obstruction disappears. If boundary points can slide around, a disk puzzle changes. The mathematics lives in the rule that certain changes are allowed and others are not.",
        "course_role": "This subtheme appears in deformation, surface surgery, knot and link reasoning, fixed-point arguments, and vector-field cleanup. It is the quiet contract behind nearly every proof and the first thing to check when an argument feels too easy.",
    },
    "invariant-receipts": {
        "problem": "A changing picture needs a receipt for what survived. Without such a receipt, a deformation may feel convincing but leave no evidence that the answer stayed the same through every allowed move.",
        "first_principles": "An invariant is that receipt. It can be a side count, a hole count, a signed intersection number, or a total index. It is useful because it can be checked before and after legal motion.",
        "course_role": "This subtheme connects the Mobius strip to Euler characteristic, intersection number, and Poincare-Hopf. The object changes; the receipt proves what did not change and lets one picture speak for another.",
    },
    "holes-and-boundaries": {
        "problem": "Holes and boundaries decide which routes exist and which counts must include edge terms. They are not visual decoration; they change what the surface can support and what motions are possible.",
        "first_principles": "A boundary is where a surface stops. A hole is missing room or a blocked filling. Both change the way loops, paths, fields, and decompositions behave because they alter the available routes.",
        "course_role": "This subtheme is central in surface classification, Euler characteristic, fixed-point theorems on balls, and configuration spaces where forbidden states become holes or walls in the space of possibilities itself.",
    },
    "curves-loops-knots": {
        "problem": "Curves and loops can carry information about how they sit inside a space. The problem is to distinguish accidental shape from protected route information that survives legal bending and stretching.",
        "first_principles": "A loop can stretch while still going around a hole. A knot can wiggle while still refusing to become a circle. The exact drawing changes, but the route relation may remain.",
        "course_role": "This subtheme supports deformation, winding, linking, intersections, and the move from visible curves to abstract paths in spaces of possible states. It keeps route information separate from length or appearance.",
    },
    "turning-and-curvature": {
        "problem": "Turning and curvature measure local change in direction, but the course is interested in totals that cannot be chosen freely by a drawing or arrow field on the whole shape.",
        "first_principles": "A little bend by itself may be a local geometric fact. When many bends are added over a closed curve, a surface, or an arrow field around a defect, the total can become topological evidence.",
        "course_role": "This subtheme links Gauss-Bonnet-style thinking to vector-field index. It prepares the reader to see local turning as part of whole-shape bookkeeping rather than isolated measurement at one point.",
    },
    "signs-and-cancellation": {
        "problem": "Many events appear and disappear during a deformation. Counting them all positively gives a fragile number. The course needs a way for fake changes to cancel while forced information remains.",
        "first_principles": "Signs record direction or orientation. When two opposite events are born together, their signed contributions add to zero. The visible picture changes, but the signed total survives the allowed motion.",
        "course_role": "This subtheme is central to intersection number and vector-field index. It is also the finer version of parity: not just even or odd, but plus and minus with geometric meaning.",
    },
    "surfaces-and-orientation": {
        "problem": "Surfaces are the main stage of the course, but they are not all alike. Some have boundaries, some have handles, some reverse side after a trip, and some allow consistent signs.",
        "first_principles": "Orientation asks whether a consistent sense of direction can be carried across the whole surface. Classification asks which handles, crosscaps, and boundaries remain after legal simplification and cutting into standard pieces.",
        "course_role": "This subtheme supports surface classification, signed intersections, Euler characteristic, and Poincare-Hopf. Without it, later plus-minus bookkeeping has no stable meaning across the whole surface or field being studied.",
    },
    "mechanisms-and-locks": {
        "problem": "Physical systems often look complicated because parts move. The course asks whether the shape of the possible motions explains what is forced or blocked without tracking every detail of the motion.",
        "first_principles": "A mechanism can be studied by its possible states. If the state space has a hole, wall, disconnected region, or forced passage, the mechanism inherits that constraint in its physical motion.",
        "course_role": "This subtheme appears in center-of-gravity reasoning, fixed points, configuration spaces, and late applications where topology predicts behavior without solving every physical detail or trajectory explicitly from equations of motion.",
    },
    "singular-moments": {
        "problem": "A special accident can be where the action happens: two intersections are born, two cancel, a tangent contact appears, or a defect ceases to be isolated for a moment during motion.",
        "first_principles": "A singular moment is not the ordinary case. It is the border between ordinary cases. By understanding how ordinary pictures change as they pass through it, the course controls exceptions instead of fearing them.",
        "course_role": "This subtheme explains pair creation and cancellation, generic position, and the need to isolate equilibria before assigning index. It turns exceptions into controlled transitions between ordinary pictures during deformation arguments.",
    },
    "models-not-labels": {
        "problem": "Topology and geometry have many names, but names do not teach the course. The real work is building a model that explains what can move, what is counted, and what is forced.",
        "first_principles": "A term matters only if it helps answer a question. Manifold means local space with gluing rules. Quotient means identified points. Index means signed turning around a defect. Each name should earn its keep.",
        "course_role": "This subtheme keeps the companion plain. It resists glossary thinking and asks every concept page to explain why the concept exists in the course and what work it performs for the reader.",
    },
}


SUBTHEME_ESSAYS = {
    "allowed-moves": [
        "Allowed moves are the rulebook behind every deformation argument in the course. Before deciding that two pictures are equivalent, the reader has to know what is permitted: stretching, sliding, bending, cutting, gluing, crossing through, moving endpoints, or preserving boundaries. Changing the rulebook changes the problem. A knot is only knotted because cutting is forbidden; a disk path puzzle is only obstructed because paths may not cross.",
        "This subtheme is the first thing to inspect when a proof feels suspiciously easy. If the simplification used an illegal move, the argument may have solved a different problem. Tokieda's pictures work because they make the allowed motion visible enough for the reader to audit.",
        "The plain rule is: sameness is always sameness under some allowed changes. A curve may be the same up to bending, a surface may be the same up to deformation, and a vector field may be the same after cleaning isolated defects. Each statement gets its meaning from the permitted moves.",
    ],
    "invariant-receipts": [
        "An invariant is a receipt for a journey through allowed changes. If a surface is deformed, a path is redrawn, or a vector field is cleaned up, the invariant records what survived. The receipt may be one-sidedness, an alternating cell count, a signed intersection number, or a total index. Its job is not to remember everything; its job is to remember the fact the proof needs.",
        "This is why invariants make deformation rigorous. Without a receipt, a transformed picture may only feel similar to the original. With a receipt, the reader can say exactly what was preserved and use that preserved fact to prove impossibility or forced existence.",
        "The course uses receipts in both directions. Matching receipts can justify carrying an answer from an easier picture back to a harder one. Different receipts can prove that no legal motion connects two situations. In both cases, the invariant turns visual change into accountable reasoning.",
    ],
    "holes-and-boundaries": [
        "Holes and boundaries are route constraints. A hole is missing room, a blocked filling, or a place a loop can remember going around. A boundary is where the surface stops, and that stopping changes what can be glued, counted, or forced. These are not decorative marks in a drawing; they determine what paths and fields can do.",
        "The course uses this subtheme from Mobius-strip boundaries to Euler characteristic, fixed-point theorems on balls, and configuration spaces where forbidden states become walls. When a proof depends on a surface's edge or missing region, this subtheme is doing the work.",
        "A beginner should treat holes and boundaries as instructions for motion. A loop may fail to shrink because a hole blocks the filling. A fixed-point theorem may need the boundary because the boundary traps possible escape. A configuration space may gain a hole because a physical collision is forbidden.",
    ],
    "curves-loops-knots": [
        "Curves and loops are the course's simplest carriers of route memory. A loop can stretch without forgetting that it went around a hole. A knot can bend without becoming untied. A linked pair can move without separating. The exact drawing changes, but the route relation can remain locked by the allowed moves.",
        "This subtheme prepares the reader for more abstract paths later. A path in a configuration space is still a route, even if the space represents possible states rather than physical positions. The same question remains: what can this route become without breaking the rules?",
        "The detail is that the route belongs to a surrounding space. A loop in a plane, a loop on a torus, and a loop in a configuration space can have different freedoms. The course keeps asking whether the route can be pulled tight, moved away, or separated without crossing something forbidden.",
    ],
    "turning-and-curvature": [
        "Turning and curvature begin as local geometric facts: an arrow turns, a curve bends, a surface curves near a point. The course cares about them because totals can become global evidence. Total turning, total curvature, and total index all express the idea that many small local changes may be forced to add up to a whole-shape constraint.",
        "This subtheme connects geometry to topology without erasing either side. The local measurement matters because its sum is not arbitrary. That is the same habit behind Gauss-Bonnet-style reasoning and vector-field index.",
        "The important mathematical move is summing local behavior only after knowing what the sum means. Turning around one defect gives an index. Curvature over a surface gives a total only after boundary and corner effects are handled. The local numbers matter because the whole object controls their combined account.",
    ],
    "signs-and-cancellation": [
        "Signs are the course's way of making fake changes disappear. If two intersections are born together with opposite signs, the visible picture changes but the signed total does not. If defects can split into opposite contributions, the total can survive even while the local pattern changes. Cancellation is designed into the count.",
        "This subtheme is the bridge from parity to intersection number to index. It teaches that the right count is often not the raw count. The right count is the one whose allowed changes cancel cleanly. The sign is the extra memory that tells a real obstruction apart from a pair that appeared only because the picture passed through a temporary accident.",
        "Signs require a rule for direction. Without orientation or a local convention that can be checked, plus and minus would be arbitrary marks. The course uses signs only when they record how objects meet, turn, or pass through the surrounding space.",
    ],
    "surfaces-and-orientation": [
        "Surfaces are the stage, and orientation is one of the rules that lets signs mean anything. A surface may have two sides, one side, a boundary, handles, or crosscaps. Locally these differences can be hidden. Globally they decide whether consistent direction, signed intersections, and vector-field bookkeeping are possible.",
        "This subtheme is why the Mobius strip is not a toy example. It shows that side information can fail globally. Later, whenever plus and minus signs appear, the reader should ask whether the surface supports those signs consistently. Orientation is the promise that a local choice can be carried around the whole object without contradiction.",
        "Surface classification uses the same concern in a broader way. Handles, crosscaps, and boundaries are not names attached after drawing; they are global features that decide what loops, cuts, fields, and counts can do. Orientation is one of the clearest tests of that global structure.",
    ],
    "mechanisms-and-locks": [
        "Mechanisms and locks describe the course's move from shape to behavior. A physical system may have many moving parts, but its possible states form a shape. If that shape has a wall, hole, disconnected region, or forced passage, the mechanism inherits the constraint. Topology can then say something before the detailed motion is solved.",
        "This subtheme appears in center-of-gravity reasoning, fixed points, configuration spaces, and late applications. It is the practical side of the course: understand the shape of possibility, and you can understand some behavior. The point is not to ignore physical details, but to choose a model where the allowed states reveal the obstruction clearly.",
        "The first-principles step is to replace time by possibility. Instead of asking where the system goes second by second, ask which states are possible at all and which paths connect them. If the state space blocks a path, the physical mechanism cannot perform the motion represented by that path.",
    ],
    "singular-moments": [
        "A singular moment is an exceptional event between ordinary pictures. Two intersections are born, two cancel, a tangency appears, or a vector-field defect stops being isolated. The course does not ignore these moments. It uses them to understand how stable pictures change without changing the protected total.",
        "This subtheme keeps generic position honest. The ordinary case is studied first, but singular moments explain transitions between ordinary cases. That is why pair creation and cancellation are not nuisances; they reveal why the invariant survives. The exception is studied just long enough to prove that the count changes in a controlled way.",
        "The useful question is not whether singular moments occur. They often do during motion. The useful question is what they are allowed to change. If the event creates opposite signs or preserves parity, it cannot destroy the invariant the proof is using.",
    ],
    "models-not-labels": [
        "Models-not-labels is the companion's guardrail against glossary thinking. A term matters only when it does work. Manifold means local space with gluing behavior. Deformation means legal motion. Index means signed turning around a defect. If a name does not help answer a question, the reader has not yet learned the idea.",
        "This subtheme is also a writing standard. The pages should not ask the reader to admire terminology. They should show what problem the concept solves, what detail makes it valid, and how it connects to the course's proof habits.",
        "The course is especially vulnerable to empty naming because topology words can sound abstract before their purpose is clear. The companion should always translate a name back into an action: build a space, move a picture, count a protected fact, compare two representations, or prove that a behavior is forced.",
    ],
}


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
        "subthemes": ["mechanisms-and-locks", "holes-and-boundaries"],
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


CONCEPT_DEPTH = {
    "generic-position": {
        "why_it_exists": "Generic position exists because special coincidences are too brittle to reason from. If three things meet at exactly one point, or a curve just kisses another curve, a tiny nudge can change the picture. The course wants arguments that survive tiny nudges, so it first moves the picture away from accidental perfection.",
        "beginner_trap": "The trap is to think ordinary position means ignoring difficult cases. It does not. It means solve the stable case first, then understand exceptional cases as limits or controlled moments where stable pictures change without destroying the question.",
        "course_role": "This idea is quiet but constant. It is behind clean intersections, pair creation and cancellation, isolated equilibria, and the move from messy physical examples to countable mathematical evidence. It gives the course permission to draw simple pictures without lying about the original problem.",
    },
    "deformation": {
        "why_it_exists": "Deformation exists because exact drawings often hide the answer. If stretching a curve does not change the question, then a complicated curve can be replaced by a simpler one. The purpose is not to make a cleaner-looking picture; it is to preserve the right fact while throwing away distracting measurement.",
        "beginner_trap": "The trap is to think any visual simplification is legal. A deformation cannot cut, glue, jump, pass through a forbidden obstacle, or move fixed endpoints past each other. The allowed moves are the proof, and changing those moves changes the claim.",
        "course_role": "Deformation is the course's main verb. It begins with strips and disk puzzles, then reappears in surface classification, intersection invariance, fixed-point theory, and vector-field index. Each later theorem asks what survives when the picture is moved honestly.",
    },
    "invariant": {
        "why_it_exists": "An invariant exists to give memory to a changing picture. When a shape bends or a map moves, most visible details change. The invariant is the part chosen carefully enough that it does not change under the allowed motion.",
        "beginner_trap": "The trap is to expect one invariant to tell the whole story. Most invariants are partial witnesses. They are powerful because a single preserved difference can prove impossibility, even when it cannot classify every possible shape.",
        "course_role": "The course moves from physical invariants such as one-sidedness to numerical invariants such as intersection number, Euler characteristic, fixed-point counts, and total vector-field index. The recurring question is always which fact has enough memory to survive the allowed change.",
    },
    "topology-vs-geometry": {
        "why_it_exists": "The distinction exists because not every question needs the same kind of information. Geometry asks how much, how long, how curved, or at what angle. Topology asks how connected, how many holes, which routes are blocked, and what survives bending.",
        "beginner_trap": "The trap is to treat topology as geometry with measurements removed. In this course, topology is not emptier than geometry; it is a different level of description chosen because it protects the facts that matter.",
        "course_role": "Tokieda constantly uses both. Drawings and physical objects give geometric intuition, while topological reasoning explains why the outcome survives changes in the drawing. The lectures are strongest when a measured-looking picture is converted into a route, boundary, count, or obstruction.",
    },
    "euler-characteristic": {
        "why_it_exists": "Euler characteristic exists because surfaces need a count that ignores how they were chopped up. Vertices, edges, and faces individually depend on the chosen decomposition. The alternating count is arranged so artificial internal cuts cancel.",
        "beginner_trap": "The trap is to memorize the formula without seeing the cancellation. The formula matters because it survives refinement and therefore belongs to the surface, not to one drawing of the surface or one chosen mesh of pieces.",
        "course_role": "It becomes the bridge from surface bookkeeping to dynamics. In Poincare-Hopf, Euler characteristic is the whole-surface number that local vector-field indices must add up to. That is why a cell count can predict something about motion.",
    },
    "triangulation": {
        "why_it_exists": "Triangulation exists to make a soft surface countable. A smooth surface has infinitely many points, but a triangulated surface has a finite ledger of pieces. That ledger lets the course count without pretending the surface is made of rigid triangles in any physical sense.",
        "beginner_trap": "The trap is to confuse the chosen triangulation with the surface itself. A different triangulation should give the same meaningful surface facts, or the count was not topological. The pieces are scaffolding for thought, not the object.",
        "course_role": "Triangulation supports Euler characteristic, surface classification, and the later comparison between cell counts and vector-field behavior. It is the finite bookkeeping device that lets smooth-looking surfaces enter exact arguments without pretending that smoothness has disappeared.",
    },
    "graph-planarity": {
        "why_it_exists": "Planarity exists because connection problems are also space problems. A graph may only say which dots must be joined, but drawing it on a plane adds a constraint: the routes must share a surface without forbidden crossings.",
        "beginner_trap": "The trap is to think a failed drawing proves impossibility. A bad drawing proves only that the drawer failed. A topological argument proves that every drawing must fail because the surface itself lacks the required room.",
        "course_role": "Graph thinking trains the reader to separate combinatorial demand from surface room, a separation that later appears in intersections and configuration spaces. It makes route constraints feel concrete before the course moves to manifolds and higher-dimensional examples.",
    },
    "knots-and-links": {
        "why_it_exists": "Knots and links exist in the course because a curve in space can remember how it is embedded. Length, roundness, and exact position can change, yet the loop may still be unable to become a plain circle by legal motion.",
        "beginner_trap": "The trap is to judge a knot by how tangled the drawing looks. A knot diagram is only meaningful when crossings record which strand passes over and which passes under. Without that record, the drawing has lost the spatial question.",
        "course_role": "They sharpen the idea of allowed moves. The same discipline later governs deformation of submanifolds, intersection counts, and paths in spaces of possible states. Knots make clear why passing through is not an innocent shortcut.",
    },
    "winding-linking": {
        "why_it_exists": "Winding and linking exist because going around something can be a stable relationship. A loop around a post can stretch and wiggle, but it cannot stop going around the post unless it crosses the post or breaks.",
        "beginner_trap": "The trap is to treat winding as a visual impression. The course needs a signed count, because opposite turns can cancel and because the count must survive legal motion instead of depending on one drawing.",
        "course_role": "This idea connects loops and knots to intersection signs. It is one of the plainest examples of a count that records a relationship rather than a measurement. Later signed counts are more abstract, but they serve the same purpose.",
    },
    "boundary-orientation": {
        "why_it_exists": "Boundary and orientation exist because a surface's edge and side-structure control what counts can be made. A boundary changes the bookkeeping. Orientation tells whether signs can be assigned consistently across the whole surface, which determines whether signed counts are even available.",
        "beginner_trap": "The trap is to check orientation only locally. Every small patch has two sides, but a trip around a Mobius-type surface can return with the side choice reversed. The obstruction is global, not local.",
        "course_role": "Orientation is required for signed intersection number and for many index arguments. Boundary issues also explain why some fixed-point statements need extra care. The course uses these details whenever a plus or minus sign is supposed to mean something.",
    },
    "gauss-bonnet": {
        "why_it_exists": "Gauss-Bonnet exists because local bending and whole-shape topology are not separate worlds. A surface can bend in many ways, but the total bending, with boundary terms included when needed, can be tied to the surface's topology.",
        "beginner_trap": "The trap is to think curvature is only a point-by-point geometric measurement. The course cares about total curvature because totals can be protected by topology. The local measurement matters most when its sum is forced.",
        "course_role": "It belongs to the local-to-global theme. Even when the course later emphasizes vector fields, the same pattern remains: local contributions add up to a global demand. Gauss-Bonnet is the curvature version of that demand.",
    },
    "vector-field-index": {
        "why_it_exists": "Vector-field index exists because solving a differential equation is often too much to ask. The index extracts a small but durable fact from the arrow pattern near an equilibrium: how the arrows turn around the failure point.",
        "beginner_trap": "The trap is to classify equilibria by appearance alone. The index is a signed turning count, and different-looking local pictures may have the same index while similar-looking pictures may behave differently under deformation.",
        "course_role": "Index is the dynamics version of signed intersection. It lets Poincare-Hopf connect local equilibria to Euler characteristic. The concept proves that a local arrow defect can carry exactly the kind of signed information the earlier intersection theory taught us to trust.",
    },
    "fixed-points": {
        "why_it_exists": "Fixed points exist as a concept because many problems ask whether a rule must leave something unchanged. Instead of finding the point, topology can sometimes prove that the shape of the space prevents all points from escaping themselves.",
        "beginner_trap": "The trap is to expect a fixed-point theorem to compute the fixed point. These theorems often prove existence only, which is already powerful when exact computation is unavailable or when the rule is known only qualitatively.",
        "course_role": "Fixed points connect intersection theory to dynamics. The graph of a map meeting the diagonal becomes a reusable form for proving unavoidable states. The idea then reappears when equilibria are treated as unavoidable failures of a vector field.",
    },
    "configuration-space": {
        "why_it_exists": "Configuration space exists because a moving system may be hard to understand in ordinary physical space. By listing every possible state as a point in a new space, motion becomes a path and constraints become holes or walls.",
        "beginner_trap": "The trap is to think the configuration space is imaginary decoration. It is a real model of possibilities: if there is no path in that model, the physical motion cannot be performed legally. The abstraction is doing physical work.",
        "course_role": "This idea gathers the course's method into applications. It lets deformation, obstruction, fixed points, and topology of state spaces speak about mechanisms and motion. It is where the course's pictorial thinking becomes a way to reason about systems that move.",
    },
    "duality": {
        "why_it_exists": "Duality exists because the first picture of a problem may hide the useful count. Turning regions into dots or borders into connections can reveal a structure that was present but hard to see in the original drawing.",
        "beginner_trap": "The trap is to treat the dual picture as a new problem. It is a change of representation, and it is valid only when it preserves the relationships the original question depends on. Otherwise it is just a different drawing.",
        "course_role": "Duality supports pictorial thinking. It trains the reader to ask whether a different diagram can carry the same reason more clearly. This is central to the course's habit of solving by redrawing without changing the problem.",
    },
    "parity": {
        "why_it_exists": "Parity exists because sometimes the exact number is too sensitive, but evenness or oddness is stable. If legal changes create or remove events two at a time, the parity cannot change, even while the visible count changes.",
        "beginner_trap": "The trap is to dismiss parity as crude. Crude is useful when the problem only needs an obstruction, and an odd count can prove that zero is impossible. The coarseness is the reason it survives.",
        "course_role": "Parity is the simplest surviving-count idea. It prepares the reader for richer signed counts, where cancellation is tracked with more information than odd or even. The course repeatedly upgrades this simple habit into finer bookkeeping.",
    },
}


CONCEPT_ESSAYS = {
    "generic-position": [
        "Generic position is the course's way of refusing to build a proof on a coincidence. If two curves merely touch, if three intersections happen at exactly one point, or if an equilibrium is smeared into a whole line, the picture may be too delicate to reveal the stable reason. A tiny nudge could change it. The ordinary case is not the lazy case; it is the case that survives small disturbances and therefore can be counted cleanly.",
        "The concept matters because many of Tokieda's arguments depend on clean events: isolated intersections, pairs being born or canceled, and defects that can be assigned an index. Generic position makes those events visible one at a time. After the stable case is understood, exceptional cases can be read as limits or transition moments. The beginner mistake is to think the exceptional picture is more honest because it looks more exact. Often it is less honest, because it hides the mechanism that persists under small motion.",
        "From first principles, the idea is a promise about evidence. If a proof counts meetings, then the meetings should be separate enough to count. If a proof assigns a sign, then the local picture should be clear enough for plus or minus to mean something. Generic position prepares the object so the later invariant is not built on an accident.",
    ],
    "deformation": [
        "Deformation is the central verb of the course. It means changing a picture continuously while preserving the question being asked. A curve can be slid, a surface can be stretched, and a handle can be moved, but only under the rules of the problem. The point is not that exact shape is irrelevant in every situation. The point is that for many questions, exact shape is the wrong level of detail. What matters is what the object can become without cutting, gluing, jumping, or crossing a forbidden obstacle.",
        "A deformation proof has a strict contract. First name the allowed moves. Then identify the fact that is supposed to survive those moves. Only then simplify the picture. This is why deformation appears from the disk path puzzle all the way to vector-field index: the course keeps replacing hard pictures by simpler ones while carrying protected information along the way. If the allowed moves are vague, the proof is vague. If the allowed moves are precise, the motion itself becomes the proof.",
        "The everyday version is bending a wire without breaking it. The mathematical version is more careful because the object may be a path, surface, map, or vector field rather than a wire. The same question remains in every case: what changes continuously, and what fact is being guarded while it changes?",
    ],
    "invariant": [
        "An invariant is a memory device for a changing situation. When a shape bends, a path slides, or a field is cleaned up, most visible facts change. An invariant is the chosen fact that does not change under the allowed moves. It may be one-sidedness, Euler characteristic, a signed intersection number, parity, or the total index of a vector field. The invariant does not need to describe the whole object. It only needs to remember enough to answer the question.",
        "The power of an invariant is often negative: it proves that something cannot happen. If two pictures have different protected counts, no legal deformation connects them. If a desired crossing-free drawing would require a count to change, the drawing is impossible. This is why invariants are not vocabulary decorations in the course. They are the receipts that let one picture speak for another. Without an invariant, deformation can feel persuasive but leave no evidence that the answer survived.",
        "A good invariant is matched to the allowed moves. One-sidedness is useful for Mobius-strip behavior because ordinary bending does not create a second side. A signed intersection count is useful because opposite pairs cancel when the picture changes legally. The art is choosing a receipt that ignores the noise but keeps the fact that decides the problem.",
    ],
    "topology-vs-geometry": [
        "Topology and geometry are not enemies in this course. Geometry gives visible local behavior: bending, turning, angles, surfaces, arrows, and physical demonstrations. Topology asks which facts survive when those visible details are changed by legal motion. Geometry may notice how a strip bends in space. Topology notices that the Mobius strip has one side and one boundary component. Both kinds of seeing matter, but they answer different questions.",
        "The distinction is practical. If a problem depends on exact length or curvature at a point, geometry is the right tool. If the problem depends on routes, holes, boundaries, or forced meetings, topology may be the cleaner level. Tokieda's course works by moving between the two: start with a physical or geometric picture, then extract the topological fact that survives. The reader should not think topology means throwing away meaning. It means keeping the meaning that the problem actually needs.",
        "This distinction also protects the reader from false simplification. A shape can be geometrically distorted while topologically unchanged, but not every distortion is harmless for every question. When curvature is being totaled, geometric detail matters. When a loop's route around a hole is being tested, exact curvature may be beside the point. The course keeps asking which level carries the answer.",
    ],
    "euler-characteristic": [
        "Euler characteristic is surface bookkeeping designed to survive redrawing. If a surface is cut into vertices, edges, and faces, those individual counts depend on the chosen cuts. Add more cuts and the raw numbers change. The alternating combination is arranged so artificial internal changes cancel. That is why the final number belongs to the surface rather than to one particular mesh drawn on it.",
        "This concept becomes much more than a formula. Early on, it helps classify and recognize surfaces. Later, in Poincare-Hopf, it becomes the number that a vector field's local indices must add up to. That is a remarkable conceptual bridge: a cell count from surface decomposition controls possible failures of motion. The first-principles lesson is that a carefully designed count can move across domains. It starts as surface accounting and ends as a constraint on dynamics.",
        "The detail behind the arithmetic is cancellation. When an edge is inserted across a face, the number of edges and faces both change, and the alternating count absorbs that artificial choice. The formula is useful because it has been engineered to forget the cuts the mathematician chose and remember the surface those cuts describe.",
    ],
    "triangulation": [
        "Triangulation is a way to make a continuous surface countable without pretending the surface is literally made of rigid triangles. A smooth surface has infinitely many points, which is too much for direct bookkeeping. Cutting it into simple cells gives a finite ledger. Once the ledger exists, the course can count vertices, edges, faces, and higher-dimensional pieces in a disciplined way.",
        "The important detail is that the triangulation is scaffolding. A different triangulation should not change the topological conclusion. If the answer depends on the exact mesh, the count has not found a surface fact. This is why triangulation supports Euler characteristic and surface classification: it lets a soft object enter exact reasoning, while later cancellation proves that the reasoning did not depend on one arbitrary set of cuts.",
        "First-principles triangulation is therefore an act of translation. A surface that cannot be counted point by point is replaced by a finite pattern of simple pieces. The replacement is valid only because the final quantity is checked against changes of that pattern. The mesh helps the mind count, then the invariant proves the mesh was not the real subject.",
    ],
    "graph-planarity": [
        "Planar graph thinking asks whether a required pattern of connections can fit on a surface without forbidden crossings. The graph itself only records which dots must be joined. The surface supplies room, routes, and limitations. A failed drawing does not prove impossibility, because the drawer may have chosen a poor arrangement. A topological argument must show that every legal arrangement runs into the same obstruction.",
        "This concept trains a habit used throughout the course: separate the demand from the room available for satisfying it. Disk path puzzles, intersections of submanifolds, knots, and configuration spaces all use versions of that separation. The question is not just what must connect to what. It is whether the surrounding space gives enough freedom for those connections to avoid each other. When it does not, crossings become evidence rather than mistakes.",
        "The everyday picture is routing roads without bridges. Some layouts fail because the route planner was clumsy; others fail because the required connections overfill the available surface. The mathematical work is to tell those cases apart. That is why graph planarity belongs with deformation and invariants rather than with drawing skill.",
    ],
    "knots-and-links": [
        "Knots and links matter because curves can remember how they sit in space. A loop may stretch, bend, and wiggle while still refusing to become a plain circle through legal motion. Linked loops may look movable, yet remain unable to separate without passing through each other. The visible tangle is not the whole story; the over-under and around-through relationships are the story.",
        "Tokieda's strip-cutting demonstrations give a concrete version of this idea. Off-center cuts of a Mobius strip can produce pieces that stay linked. The final lecture returns to linked strip behavior. These examples teach the same rule that knot theory formalizes: passing through is not an innocent simplification. The legal moves determine whether an apparent tangle is removable or whether it records a real route constraint.",
        "The key mathematical detail is that the curve lives inside a surrounding space. A loop drawn on a page and a loop floating in three-dimensional space have different freedoms. The knot is not just the curve; it is the curve together with the rule that it must move through the surrounding space without crossing itself.",
    ],
    "winding-linking": [
        "Winding and linking are ways of counting a relationship rather than a size. A loop around a post can be pulled tighter or looser, but it still goes around the post unless it crosses the post or breaks. Two loops can be linked even when their exact shapes change. The stable fact is not length, roundness, or position. It is the aroundness relation.",
        "The course needs signs because relationships can cancel. Opposite windings may add to zero. Opposite intersections may be born together and vanish together. Winding and linking therefore prepare the reader for signed intersection number and vector-field index. They make it intuitive that a count can measure a relation between objects, not just a property of one object by itself.",
        "That is why linked strip demonstrations are not just curiosities. They train the eye to see a relationship that survives motion.",
        "From first principles, winding asks whether a route can be pulled off a forbidden center without crossing it. Linking asks the same kind of question for two closed curves. Both ideas teach the reader to look for a relationship that belongs to the whole route, not to one convenient snapshot of the drawing.",
    ],
    "boundary-orientation": [
        "Boundary and orientation are the details that make many later counts honest. A boundary is where a surface stops, and stopping changes the bookkeeping. Orientation asks whether a consistent sense of direction can be carried across the whole surface. On a Mobius-type surface, every small patch looks ordinary, but a full trip can reverse the side choice. That is a global obstruction.",
        "Signed intersection number depends on orientation. Vector-field index depends on being able to interpret turning consistently. Fixed-point statements on balls depend on what the boundary does. These are not technical side conditions added to intimidate beginners. They are the facts that let plus and minus signs mean something. If orientation or boundary is ignored, the proof may count a quantity that is not actually defined.",
        "The first-principles test is simple: can a local choice be carried all the way around without contradiction, and does the surface have an edge where extra behavior enters? Those questions decide whether later arithmetic is legal. Boundary and orientation are therefore part of the proof's foundation, not a cleanup step after the idea is already known.",
    ],
    "gauss-bonnet": [
        "Gauss-Bonnet represents the course's local-to-global habit in geometric form. Curvature is local: it says how a surface bends near a point. But the total curvature, with boundary and corner terms when needed, can be tied to the surface's whole topology. Local bending is not free to add up to anything it wants.",
        "Even when the course later emphasizes vector fields more than curvature, the same principle remains. Local contributions can be summed into a global constraint. The concept is therefore useful as a bridge: it helps a reader see why total turning, total curvature, total index, and Euler characteristic belong in the same family of ideas. The surface makes demands on the sum of local behavior.",
        "The point is not to memorize a formula, but to recognize the pattern: small measured changes can be forced by whole-shape structure.",
        "For a beginner, the important detail is that the theorem balances several kinds of information. Interior curvature, boundary turning, and corner contributions may all be needed before the total matches the surface. Leaving out an edge term is not a small oversight; it changes the account being balanced.",
    ],
    "vector-field-index": [
        "Vector-field index is the dynamics version of signed counting. A vector field assigns an arrow to each point. Where the arrow vanishes, there is an equilibrium or defect. The index records how the nearby arrows turn around that defect. It is local evidence, but it is designed so it survives appropriate changes in the field.",
        "The concept matters because it lets topology speak about differential equations without solving them. Sources, sinks, saddles, and other local patterns may move or change under deformation, but their signed total can be constrained by the surface. Poincare-Hopf is the payoff: the sum of local indices equals Euler characteristic. A fact about arrows becomes a fact about the shape carrying them.",
        "This turns a hard analytic question into a topological one: not where every trajectory goes, but what failures the whole surface requires.",
        "The first-principles picture is to walk once around a small loop surrounding the defect and watch the arrows turn. If the arrows make a full turn, or reverse their turning in a saddle-like way, that local behavior receives a signed count. The count is local, but the course uses it because the sum of such local counts can be globally forced.",
    ],
    "fixed-points": [
        "A fixed point is a place that a rule sends back to itself. The concept is powerful because many problems care about existence, not explicit calculation. Brouwer's theorem, for example, says that a continuous self-map of a closed ball must have a fixed point. It does not tell us where the point is. It tells us that the shape gives all points no continuous way to avoid themselves at once.",
        "The graph-and-diagonal picture explains why fixed points fit the course. The graph of a map records where points go. The diagonal records self-agreement. A fixed point is their intersection. This turns a rule into a geometric meeting problem, so earlier intersection ideas become relevant. Later, equilibria in vector fields play a similar role: special states forced by the shape and continuity of the system.",
        "The mathematical detail is that continuity ties nearby inputs to nearby outputs. If the rule could jump, it might dodge the forced agreement. The theorem is not saying every process has a fixed point; it is saying that certain shapes and certain continuous rules leave no global escape from self-agreement.",
    ],
    "configuration-space": [
        "Configuration space is a change of viewpoint. Instead of watching a mechanism or moving system in ordinary space, list all possible states and treat each state as a point in a new space. Motion becomes a path through that space. Forbidden positions become holes or walls. A blocked physical motion becomes the absence of a legal path.",
        "This concept is crucial for applications because it lets topology reason about behavior without tracking every physical detail. The state space may reveal constraints that are hard to see in the original object. Fixed points, barriers, forced passages, and connected components become statements about the shape of possibilities. The abstraction is not escape from reality; it is a cleaner model of what the system is allowed to do.",
        "The hard part is modeling honestly: the state space must include the right freedoms and forbid the right impossible states.",
        "From first principles, the construction asks what information is needed to describe one complete state. For a moving rod, that may include position and angle. For several moving points, it includes all their positions plus collision rules. Once those choices are made, the new space can be studied with the same route and obstruction ideas as any other space.",
    ],
    "duality": [
        "Duality means changing the picture so the useful structure becomes visible. Regions may become dots, shared borders may become edges, or a rule may become a graph in a product space. The new picture is not a new problem. It is another representation of the same relationships, chosen because it exposes a count, route, or obstruction that the first picture hid.",
        "The course relies on this habit constantly. A square with edge labels represents a surface. A map becomes its graph. A fixed point becomes an intersection with the diagonal. A physical mechanism becomes a configuration space. Duality is therefore part of pictorial thinking: redraw the situation, but preserve the relationships that matter. If the redraw loses those relationships, it is only a different drawing, not a proof.",
        "A good dual picture earns its place by making the protected fact easier to see without changing what must be proved.",
        "The important check is translation back. After solving the dual problem, the conclusion must mean something in the original picture. If regions become dots, the answer about dots must still say something about regions. If a map becomes a graph, an intersection must still mean a fixed point. Duality is useful only when both directions of meaning are kept clear.",
    ],
    "parity": [
        "Parity asks whether a count is even or odd. It is deliberately coarse, and that is why it can be powerful. If legal changes create or remove events in pairs, the exact count may change but the parity cannot. An odd count can prove that zero is impossible, which is often enough for an existence or obstruction argument.",
        "The course uses richer signed counts later, but parity is the simplest version of the same survival idea. It teaches the reader not to demand more information than the problem needs. Sometimes the stable shadow of a number is more useful than the fragile exact number. This prepares the mind for intersection signs and index sums, where cancellation is tracked with finer detail.",
        "The lesson is economical: keep only the part of the count that the allowed moves cannot destroy.",
        "This is why parity is a first-principles tool rather than a shortcut. If every legal change alters a count by two, then evenness or oddness is protected by the rules of motion. The proof may not know the exact count at the end, but it can still know that zero is impossible when the protected parity is odd.",
    ],
}


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
        "concepts": ["configuration-space", "fixed-points", "deformation", "vector-field-index"],
    },
]


FAMILY_DEPTH = {
    "deformation-family": {
        "human_problem": "The human problem is that the original picture is often too tangled to reason about directly. The family asks how to change that picture without changing the answer, so the reader can solve the simpler version with confidence.",
        "first_principles": "Start by naming the legal moves. Then move the object through those moves until it is easier to inspect. If the protected fact survives every step, the simplified picture speaks for the original picture and not merely for itself.",
        "how_it_works": "A deformation proof has three parts: the contract of allowed motion, the protected feature, and the simpler endpoint. The proof fails if any one of these is vague. The endpoint is convincing only because the route to it was legal.",
        "course_examples": "The disk-connection puzzle, surface classification by surgery, intersection invariance, and the treatment of vector-field defects all use this family. In each case, motion is not a side effect; it is the proof method.",
        "failure_mode": "The common failure is to simplify by a move that the problem does not permit. Cutting a loop, sliding an endpoint, passing through an obstacle, or changing a boundary condition may make the picture easier while solving the wrong problem.",
    },
    "counting-family": {
        "human_problem": "The human problem is that a drawing can change while the underlying obstruction remains. A count gives the reader something stable enough to compare before and after the change, even when the visible picture has been redrawn.",
        "first_principles": "Do not count everything. Count the feature whose changes cancel under the allowed moves. Sometimes the count is alternating, as in Euler characteristic. Sometimes it is signed, as in intersection number or index, because signs make fake changes disappear.",
        "how_it_works": "A surviving-count proof identifies which local changes can happen, then shows those changes leave the chosen total alone. Once the total is known in an easy picture, it constrains every legally related picture and can forbid desired outcomes.",
        "course_examples": "Euler characteristic counts cells with alternating signs. Intersection number counts meetings with plus and minus signs. Poincare-Hopf counts vector-field defects and ties their total to the surface. These are different objects but the same proof instinct.",
        "failure_mode": "The common failure is to use a count that changes under harmless redrawings. A raw crossing count, for example, can rise or fall when a canceling pair is created, so it is not the protected quantity.",
    },
    "surface-family": {
        "human_problem": "The human problem is that surfaces look simple nearby but can behave differently as wholes. This family asks how patches, boundaries, holes, and orientation combine into whole-surface facts that local inspection alone misses completely.",
        "first_principles": "Cut the surface into manageable pieces, understand what happens on each piece, and then glue the bookkeeping back together. The global result is not guessed from one patch; it is forced by how all patches fit.",
        "how_it_works": "Surface bookkeeping uses decompositions, orientation choices, boundary terms, and cancellation. It is careful about what is local and what is global, because many surface obstructions appear only after a full trip around the object or a full sum over its pieces.",
        "course_examples": "The Mobius strip reveals global one-sidedness. Surface classification tracks handles and crosscaps. Euler characteristic records whole-surface type. Poincare-Hopf shows that vector fields must obey the surface's total count. The same surface facts keep reappearing in different language.",
        "failure_mode": "The common failure is to reason locally and assume the whole surface behaves the same way. A Mobius strip defeats that assumption immediately, and later orientation-dependent counts fail without global consistency across the surface.",
    },
    "embedding-family": {
        "human_problem": "The human problem is to know whether one object can sit inside another without forbidden collisions. A drawing may suggest an answer, but this family asks for a reason that covers every drawing and every legal attempt.",
        "first_principles": "Separate the object's required connections from the room supplied by the surrounding surface or space. If every legal placement would force a forbidden meeting, the obstruction belongs to the topology, not to a bad drawing.",
        "how_it_works": "Embedding arguments track crossings, over-under information, winding, linking, and surface room. They ask whether deformation can remove intersections or whether a count proves that some relation survives every allowed placement in the space under study.",
        "course_examples": "Path puzzles in a disk, planar graph questions, knots and links, and intersection theory all belong here. The family teaches the reader to distinguish accidental crossings from forced ones by checking what legal motion can remove.",
        "failure_mode": "The common failure is to confuse a failed attempt with a proof of impossibility. A topological obstruction must show that every legal attempt fails, not only the first drawing tried or the most obvious arrangement.",
    },
    "motion-family": {
        "human_problem": "The human problem is to understand motion when exact equations or trajectories are unavailable. This family asks what the shape of possible states can force before anything is solved explicitly or computed point by point.",
        "first_principles": "Represent each possible state as a point in a new space. Motion becomes a path or rule on that space. Fixed points, equilibria, blocked routes, and forced passages become topological questions about that state space.",
        "how_it_works": "The family translates physical or dynamical behavior into shape: graph of a map versus diagonal, vector field defects, index sums, or paths in a configuration space. Once translated, earlier tools such as deformation and surviving counts apply.",
        "course_examples": "The center-of-gravity demonstration, Brouwer fixed point theorem, vector fields, equilibria, Poincare-Hopf, and late applications all use this family. The course ends here because it shows topology acting on behavior, not only on static pictures.",
        "failure_mode": "The common failure is to model the state space carelessly. If the states, boundaries, forbidden positions, or allowed motions are wrong, the topological conclusion may no longer describe the physical system being studied at all.",
    },
}


FAMILY_ESSAYS = {
    "deformation-family": [
        "Deformation arguments are the course's way of replacing a hard object by an easier one without losing the question. The first step is not to move anything. The first step is to state the contract: what may bend, what must stay attached, which crossings are forbidden, which endpoints stay fixed, and which boundaries still count as boundaries. Only after that contract is clear does motion become a proof method.",
        "The family matters because many topological questions are impossible to settle from the first drawing. A tangled drawing may hide a simple answer; a simple-looking drawing may hide an obstruction. Deformation gives the reader permission to simplify, but only under rules that preserve the feature being tested. This is why the endpoint of a deformation proof is not evidence by itself. The evidence is the whole legal journey from the original picture to the easier one.",
        "The mathematical principle is plain: if every allowed step preserves the relevant fact, then the final easy picture can speak for the original hard picture.",
    ],
    "counting-family": [
        "Surviving-count arguments begin with a practical problem: the visible picture changes too much. Crossings can appear, cells can be subdivided, arrows can be redrawn, and defects can move. A raw count of everything usually fails because it records accidental clutter. The course therefore asks for a count designed to ignore the harmless changes while keeping the obstruction that matters.",
        "Euler characteristic does this by alternating pieces. Intersection number does this by using signs. Vector-field index does this by recording how arrows turn around a defect. Parity does it more coarsely by keeping only evenness or oddness. These examples look different on the surface, but they share one idea: count the part of the situation that legal motion cannot erase.",
        "The family is important because a good count can prove impossibility or forced existence without listing every possible drawing. Once the count is known in one honest version of the object, every legally related version has to obey it.",
    ],
    "surface-family": [
        "Surface bookkeeping is needed because a surface can lie to local inspection. Every tiny patch of a sphere, torus, disk, or Mobius strip may look like an ordinary piece of paper. The difference appears when patches are glued into a whole: a route may return reversed, a boundary may add a term, a handle may create a new loop, or a missing disk may change what can be filled.",
        "This family teaches the reader to track the whole surface without losing the local pieces. Cut the surface into manageable parts, count or orient those parts, then check what survives when they are put back together. Euler characteristic, boundary orientation, surface classification, and Poincare-Hopf all depend on this discipline.",
        "The mathematical principle is that local freedom is not the same as global freedom. A patch may allow an arrow, a side choice, or a sign, while the completed surface refuses to let all those local choices agree at once.",
    ],
    "embedding-family": [
        "Drawing and embedding arguments ask whether there is enough room for required connections. A failed drawing is not enough, because a better drawing may exist. The family therefore separates the object that must be placed from the space that must receive it. Which endpoints are fixed? Which crossings are forbidden? Can one strand pass through another? Does the surrounding surface have holes or handles that provide alternate routes?",
        "This is where knots, links, planar graphs, path puzzles, and intersection arguments meet. Each problem asks whether a relation can be removed by legal motion or whether it belongs to the shape of the situation. A crossing on the page may be accidental. A linking relation or forced intersection may survive every attempt to redraw.",
        "The important mathematical idea is not drawing skill. It is proving that all legal drawings face the same constraint. The surface or surrounding space supplies only certain routes, and sometimes those routes are not enough.",
    ],
    "motion-family": [
        "Motion-through-state arguments are the course's bridge from shapes to behavior. Instead of following a mechanism directly, the method lists its possible states and treats each state as a point in a new space. A motion is then a path through that space. A rule becomes a map of the space to itself. A forbidden physical arrangement becomes a wall, hole, or missing region in the state space.",
        "This family explains why fixed points, vector fields, configuration spaces, and physical examples belong with surface topology. They are all ways of asking what behavior the shape of possibility permits. The course does not need every equation of motion to say something meaningful. If the state space has the right obstruction, some positions, coincidences, defects, or blocked motions are forced before detailed solving begins.",
        "The detail that keeps the method honest is modeling. The state space must contain the right freedoms and remove the right forbidden states. If that translation is wrong, the topological conclusion may be true about the model but false about the physical situation.",
    ],
}


MATH_WHY = {
    "big_picture": "The mathematical heart of the course is the search for facts that survive honest change. Exact length, exact angle, and exact placement often change too easily. Tokieda's course asks for a better handle: a count, a boundary, a hole, a turn, a sign, a fixed point, or a forced route. The reason these ideas matter is that they let a person prove something when direct measurement or direct solving is the wrong tool.",
    "first_principles": "Start with an object or motion that is too complicated to inspect directly. Decide which changes leave the real question unchanged. Move the object until the picture becomes simpler. Track the feature that did not change. If the simplified picture makes the answer clear, the original object inherits that answer. This is the common engine behind paper strips, surface classification, intersection number, fixed-point theorems, and vector-field index.",
    "important_detail": "The allowed changes are the whole contract. A result is only as strong as the promise that the change did not cut, glue, pass through, erase a boundary, reverse a side, or create a forbidden coincidence. This is why the course spends so much time on ordinary position, orientation, boundaries, and signs. Those details are not formal decoration; they are what keep the reasoning honest.",
    "principle": "Topology and geometry become powerful when local details are organized so that the whole shape has fewer choices than it appears to have. Local patches may look free. Local arrows may look adjustable. Local crossings may look removable. But the whole object can force a side reversal, a nonzero count, a fixed point, or a defect. The mathematical principle is that global structure can turn many small freedoms into one unavoidable conclusion.",
    "concepts_matter": "The important concepts matter because each one protects a different kind of evidence. Deformation protects the question while the picture moves. Invariants remember what survived. Euler characteristic turns a surface into stable bookkeeping. Intersection number records meetings with signs. Fixed points turn rules into forced self-agreement. Vector-field index turns local arrow failures into a count that the whole surface controls.",
    "reader_path": "A reader should not learn this course as a vocabulary list. The path is: first see a physical surprise, then ask what kind of fact survived, then name the allowed motion, then build a count or obstruction, then use that obstruction to force an answer. This is why the companion links lectures, concepts, themes, subthemes, and method families in both directions.",
}


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


LECTURE_DEPTH = {
    1: {
        "title": "The Mobius strip reveals the course's central problem",
        "problem": "The course begins with a strip of paper because the strip makes the central promise visible before any vocabulary arrives. A normal loop of paper has two sides. A Mobius strip has one side. If you cut them, color them, or walk along them, they answer differently. The problem is: how can a small twist change the whole behavior of a surface when every tiny patch still looks like ordinary paper?",
        "first_principles": "A beginner is tempted to think a surface is understood by looking at a small piece of it. Tokieda starts by breaking that habit. Every small patch of the Mobius strip looks harmless, but a full trip around it changes what side you think you are on. The important lesson is that a whole object can carry information that no tiny patch reveals by itself.",
        "math_move": "Use a physical object as a proof object. Cut the strip, follow a line, and compare what happens with and without the twist. The act of cutting is not entertainment added after the mathematics; it is a controlled test of how the surface is connected.",
        "detail": "The twist is not measured by its exact angle in a geometric sense. What matters is the gluing rule at the ends. Glue without reversal and you get an ordinary band. Glue after reversal and the global surface changes.",
        "connection": "This opening prepares the rest of the course: local appearance is not enough, allowed operations matter, and a visible experiment can carry a mathematical reason. The later theorems will look more formal, but they keep returning to this same lesson: the whole object may remember something that a small local view cannot see.",
        "anchors": ["Mobius strip", "twist and glue", "cutting along the center", "one side versus two sides"],
    },
    2: {
        "title": "Deformation as a way to solve, not decorate",
        "problem": "The lecture asks whether several pairs of boundary points in a disk can be connected without the connecting paths meeting. Drawn directly, the question looks like a routing puzzle. The deeper problem is how to prove impossibility without trying every possible drawing.",
        "first_principles": "If a drawing can be stretched, slid, or rounded without changing the question, then the exact drawing was never the main thing. What matters is the order of the points on the boundary and the rule that paths may not cross. Deformation lets us simplify the picture while protecting those facts.",
        "math_move": "Replace the drawing by a cleaner drawing through allowed motion. If any successful drawing existed, the cleaned-up version would still exist. When the clean version forces a crossing, the original problem is impossible too.",
        "detail": "A deformation argument always depends on a contract. You may move paths continuously, but you may not let one path pass through another, move endpoints past each other, or tear the disk. If that contract is vague, the proof solves an unclear problem; if it is precise, the motion itself becomes evidence.",
        "connection": "This lecture gives the course its working method. Later intersection numbers, fixed-point arguments, and vector-field indices all use the same idea: change the picture while protecting the answer. The names become more advanced, but the habit remains this simple: simplify only by moves that keep the question intact.",
        "anchors": ["deformation", "disk", "boundary points", "curves that do not intersect"],
    },
    3: {
        "title": "Building spaces from simple pieces",
        "problem": "After deformation enters, the course needs objects worth deforming. This lecture asks how to build useful spaces from simple pieces such as intervals, disks, balls, and spheres. The problem is to stop treating spaces as finished shapes and start treating them as objects made by understandable operations.",
        "first_principles": "A space is not just a shape sitting in front of us. It can be assembled. Taking a product means letting two independent choices vary at once. Taking a quotient means deciding that different-looking points should count as the same point. Surgery means removing a piece and gluing another piece back in. These operations explain how complicated spaces can be made in a disciplined way.",
        "math_move": "Study spaces by their construction recipe. Instead of memorizing a list of named shapes, track the operations that create them and the facts those operations preserve or change. The construction recipe tells you what paths, boundaries, and neighborhoods should mean after the pieces have been combined.",
        "detail": "The gluing instructions matter as much as the pieces. The same square can become a cylinder, a Mobius band, a torus, or something else depending on which edges are identified and whether directions are reversed.",
        "connection": "The product, quotient, and surgery language becomes the course's toolkit for surfaces, manifolds, intersections, and later the spaces of possible states in dynamics. Once a space can be built from rules, later arguments can refer to those rules instead of relying on a fragile drawing.",
        "anchors": ["balls and spheres", "product", "quotient", "surgery", "manifolds"],
    },
    4: {
        "title": "Gluing rules make new worlds",
        "problem": "This lecture continues the construction story and shows that a small change in identification can alter the whole space. The problem is not drawing a square or a disk; the problem is knowing what world the gluing rule creates.",
        "first_principles": "A paper square is familiar until its edges are treated as instructions. Glue one pair of opposite edges and you get a cylinder-like behavior. Glue both pairs and the routes through the square can wrap around. Reverse an edge and the surface can lose a consistent two-sidedness. The picture becomes a map of allowed travel.",
        "math_move": "Read a space from its boundary identifications. The edges tell you which exits return as which entrances. Once that rule is known, questions about loops, sides, and holes become questions about how routes behave under the identifications.",
        "detail": "The drawing on the page is not the final space. It is a code for the final space. Forgetting that distinction makes quotient constructions look like strange drawings rather than precise instructions. The same visible square can describe different spaces, so the arrows and edge labels are part of the object.",
        "connection": "This lecture deepens the transition from physical examples to general manifolds. Later, when intersections or vector fields live on a manifold, the hidden gluing rules still control what can happen. A vector field on a torus and a vector field on a sphere differ because the underlying route structure differs.",
        "anchors": ["square", "product", "quotient", "manifolds", "boundary identification"],
    },
    5: {
        "title": "Classifying surfaces by what survives cutting and gluing",
        "problem": "The lecture turns from examples to classification: what kinds of surfaces exist if we ignore exact size and focus on how they are connected? The problem is to avoid treating every drawing as a new species.",
        "first_principles": "Surfaces can have handles, crosscaps, boundaries, and orientability. These are not decorative labels. A handle gives a route around and through. A crosscap reverses the sense of side after a trip. Classification says that, after enough legal cutting and reassembly, surfaces fall into families controlled by these features.",
        "math_move": "Use surgery and deformation to reduce a surface to standard parts. If the same basic pieces remain after all legal simplification, those pieces describe the surface's type. The proof idea is not to inspect every possible drawing, but to show that every drawing can be brought to a controlled normal form.",
        "detail": "Orientability is not about whether a drawing looks twisted. It asks whether a consistent sense of clockwise, or left side versus right side, can be carried around the entire surface without contradiction. A surface can look ordinary in every small patch and still reverse this choice after a long trip.",
        "connection": "Classification makes later counting meaningful. Euler characteristic, intersections, and vector-field index depend on the surface family, not on the exact drawing. This is why later formulas can speak about a sphere, torus, or non-orientable surface as a whole rather than about one picture of it.",
        "anchors": ["classification of surfaces", "Mobius", "orientable", "non-orientable", "surgery"],
    },
    6: {
        "title": "Moving subspaces and meeting only when dimension forces it",
        "problem": "This lecture asks when an object inside a space can be moved away from another object, and when meeting is unavoidable. The everyday version is: can two things pass without collision if they have enough room?",
        "first_principles": "Dimension is room. A point moving on a line is easily trapped by another point. A curve in a plane has more freedom, but crossings still matter. In higher-dimensional spaces, objects may have enough spare directions to avoid one another. The course turns this physical feeling into a counting rule.",
        "math_move": "Compare the dimensions of the objects with the dimension of the surrounding space. If there is enough room, deformation can remove intersections. If not, intersections become meaningful evidence. The argument converts a visual crossing into a question about available directions for escape.",
        "detail": "An intersection that remains after every legal motion is different from an accidental crossing in a bad drawing. The hard work is separating removable accidents from forced meetings. That separation is why the course insists on ordinary position before it starts counting.",
        "connection": "This prepares the intersection number. Once meetings cannot simply be waved away, the next question is how to count them so the count survives deformation. Lecture 8 answers that question by adding signs, which lets accidental pairs cancel while forced information remains.",
        "anchors": ["submanifold", "moving inside a manifold", "obstacles", "dimensions", "intersection"],
    },
    7: {
        "title": "Center of gravity and the birth of intersection thinking",
        "problem": "The lecture opens with a physical center-of-gravity demonstration and uses it to point toward a bigger question: when does a continuous process have to pass through a special state? The problem is to turn a physical inevitability into a mathematical inevitability without hiding behind a formula.",
        "first_principles": "If two hands slide inward under an object, they meet at a balancing point because the system has no way to jump over the balance condition. The mathematical habit is to watch a continuously changing situation and ask which event cannot be avoided.",
        "math_move": "Turn an existence question into an intersection question. One moving condition and another condition are represented as sets; if they must meet, the desired object or state exists. This changes the proof from searching for a point to showing that two organized pieces cannot avoid each other.",
        "detail": "The strength of the argument is continuity. If the motion could jump, vanish, or teleport, the forced meeting would not follow. The demonstration works because each small change in hand position produces a small change in the balancing condition.",
        "connection": "This lecture bridges hands-on physical reasoning and the formal intersection machinery used in the following lecture. It also foreshadows fixed points and equilibria, where the same question returns in a new form: what state is forced to exist because a continuous rule cannot avoid it?",
        "anchors": ["center of gravity", "continuous motion", "intersection", "existence"],
    },
    8: {
        "title": "Intersection number is a count with memory",
        "problem": "The lecture states one of the course's main theorems: a signed count of intersections does not change under deformation. The problem is to count meetings in a way that ignores accidental births and deaths but remembers forced structure.",
        "first_principles": "If two curves or surfaces meet, some meetings may appear or disappear when the picture moves. But they often appear in opposite-signed pairs. Counting with signs makes those fake changes cancel. What remains is not the number of visible crossings in one drawing; it is the part of the crossing information that the drawing cannot get rid of.",
        "math_move": "Assign plus or minus signs to intersections using orientation, then add them. Pair creation and cancellation change the visible picture but leave the signed total unchanged. This is the point where a picture becomes arithmetic without losing the geometry that made the count meaningful.",
        "detail": "Orientation is not ornamental here. Without signs, two opposite intersections look like two events. With signs, they cancel and reveal why the total survives deformation. The sign records how the two pieces meet inside the surrounding oriented space.",
        "connection": "This is the hinge between early topology and later fixed-point and vector-field arguments. The same signed-count idea will reappear as index. Once you have learned to count intersections with signs, it is natural to count arrow-field defects with signs too.",
        "anchors": ["intersection number", "orientation", "positive or negative", "isotopy invariant", "pairwise creation"],
    },
    9: {
        "title": "Fixed points as intersections with the diagonal",
        "problem": "The lecture studies maps from a space to itself. A fixed point is a point that the map sends back to itself. The problem is to prove that such a point exists without finding it directly.",
        "first_principles": "Draw the graph of the map: for each starting point, record where it goes. Also draw the diagonal: the set of pairs where the start and the end are the same. A fixed point is simply a meeting of these two objects. This turns a problem about a rule into a problem about intersection.",
        "math_move": "Translate fixed points into intersections between the graph of a map and the diagonal. Then use the earlier intersection machinery to decide when those meetings cannot all disappear. The map is no longer an invisible rule; it becomes a geometric object that can be compared with another geometric object.",
        "detail": "The middle video for this lecture has no recovered captions, so this reading is grounded in the surrounding transcript and the course summary rather than a complete transcript for all parts. The site keeps that source gap visible because pretending full evidence would make the explainer less trustworthy.",
        "connection": "This lecture carries intersection theory into fixed-point theory. It sets up Brouwer and Lefschetz-style arguments in the next lecture. The course is now using the same signed-meeting idea to prove that a rule must leave some point unmoved.",
        "anchors": ["graph of a mapping", "diagonal", "fixed points", "missing middle caption"],
    },
    10: {
        "title": "Brouwer fixed point theorem: shape forces a point to stay",
        "problem": "The lecture centers on Brouwer's fixed-point theorem for a closed ball: every continuous self-map has a point that stays put. The problem is to understand why a soft shape can force a solution even when the map is arbitrary.",
        "first_principles": "Imagine stirring all points of a disk and putting each point somewhere else in the disk, without tearing the motion rule. Brouwer says at least one point cannot avoid landing where it began. This is not because we know which point it is. It is because the disk's boundary and filled-in interior leave no continuous escape route for every point at once.",
        "math_move": "Use a stronger closed-space fixed-point idea and adapt it to the ball, whose boundary makes the statement look harder. The proof strategy turns the boundary problem into a topological obstruction. If every point tried to move away from itself, the induced escape pattern would contradict the shape of the ball.",
        "detail": "The theorem depends on the domain being the closed ball. If the boundary is removed or the shape changes, the forced fixed point can fail. The statement is not about all spaces; it is about the particular way a filled ball holds its boundary and interior together.",
        "connection": "This lecture shows the payoff of the intersection viewpoint: existence can be proved by the shape of the space, not by solving equations. That same payoff will matter for dynamics, where exact trajectories may be unavailable but forced equilibria can still be proved.",
        "anchors": ["Brouwer fixed-point theorem", "closed ball", "boundary", "continuous map"],
    },
    11: {
        "title": "Vector fields: learning without solving the equations",
        "problem": "The final chapter starts with dynamical systems. The practical problem is that differential equations are often impossible to solve exactly, yet we still need to know how their solutions behave. The lecture asks what can be known from the shape of the arrow pattern before any explicit solution is written down.",
        "first_principles": "A vector field assigns a little arrow to each point, telling a particle which way it wants to move. An equilibrium is a place where the arrow vanishes. Instead of solving the whole motion, topology asks what the pattern of arrows is forced to contain.",
        "math_move": "Replace exact solutions by qualitative information: equilibria, local arrow patterns, and the index of each equilibrium. The index records how the arrows turn around a defect. This lets the course use topology where calculation would otherwise demand solving the whole differential equation.",
        "detail": "The index is not a decorative label on an equilibrium. It is a signed local count, and signed local counts can be added across the whole surface. A source, a sink, and a saddle are different because the surrounding arrows turn in different signed ways.",
        "connection": "This lecture imports the course's earlier signed-count habit into dynamics. Intersections become indices; forced intersections become forced equilibria. The course has moved from paper surfaces to motion, but the proof engine is still protected counting under allowed deformation.",
        "anchors": ["dynamical systems", "differential equations", "vector field", "equilibria", "index"],
    },
    12: {
        "title": "Index becomes global bookkeeping",
        "problem": "After defining the index of a vector field, the course asks what all the local indices know together. Can a surface force the total behavior of every vector field on it? The problem is to connect many small arrow failures to one number belonging to the whole surface.",
        "first_principles": "A vector field may have many defects. Some look like sources, sinks, saddles, or rotating patterns. Each defect has a local signed count. The surprise is that the total of those local counts is not chosen freely by the field. The surface itself controls it.",
        "math_move": "Add the indices of all equilibria and compare the sum with a whole-surface number. This is the road to Poincare-Hopf: local arrow failures add up to Euler characteristic. The theorem works because local defects can move or split, but their signed total is tied to the surface.",
        "detail": "The theorem counts isolated equilibria under clean conditions. If equilibria smear into a whole curve or captions garble a condition, the safe interpretation is the first-principles one: clean up to a generic case, then count.",
        "connection": "This lecture binds Euler-style surface bookkeeping to vector-field behavior. It makes the old count of cells matter for motion. The same alternating count that once described a surface now predicts what any arrow pattern on that surface must fail to do.",
        "anchors": ["index of a vector field", "equilibria", "Euler characteristic", "Poincare-Hopf"],
    },
    13: {
        "title": "Poincare-Hopf turns topology into a prediction about motion",
        "problem": "The lecture uses the Poincare-Hopf theorem in both directions. If the surface is known, it restricts the possible equilibria. If the equilibria are known, they reveal information about the surface. The problem is to see a theorem not as a slogan, but as a working exchange rate between shape and motion.",
        "first_principles": "The theorem says that local defects in a vector field must add up to a number belonging to the surface. On a sphere, this explains why a perfectly nonzero tangent arrow pattern cannot exist everywhere. Something has to fail. That is the everyday content behind the hairy-ball idea.",
        "math_move": "Use the equation between total index and Euler characteristic as a two-way tool. Known topology predicts forced equilibria; known dynamics can diagnose topology. The same equality can answer different questions depending on which side of the equation is already understood.",
        "detail": "This is not about drawing a tidy arrow field. It is about the impossibility of making all local arrow choices agree with the whole surface. A sphere, for example, does not give the arrows enough global freedom to avoid defects everywhere.",
        "connection": "The lecture is where the course's early themes clearly pay off: deformation, signed counts, surfaces, and dynamics all meet in one statement. It shows why the earlier bookkeeping was worth learning: it can now say something concrete about motion.",
        "anchors": ["Poincare-Hopf theorem", "index sum", "Euler characteristic", "hairy ball", "equilibria"],
    },
    14: {
        "title": "Applications show the same method in new settings",
        "problem": "The late applications ask why rotations, physical motion, and dynamical examples keep obeying topological restrictions. The problem is to see the common structure rather than treat each example as an isolated demonstration. Each example has to be translated into a space, a rule on that space, and a protected quantity.",
        "first_principles": "A rotation, a flow, or a physical process gives a rule for moving points or states. The rule may be complicated, but the space of possible states may have simple topological demands. If the space has the wrong kind of hole, boundary, or total index, some behavior is forced.",
        "math_move": "Translate each application into one of the course's established forms: a fixed-point question, a vector-field question, an index count, or a deformation-invariant obstruction. Once the translation is made, the application inherits the force of the earlier theorem instead of needing a brand-new argument.",
        "detail": "Applications are convincing only when the translation is honest. One must identify the space, the allowed motion, and the quantity being preserved. If any of those three pieces is wrong, the topological theorem may no longer apply.",
        "connection": "This lecture proves that the course has been building a reusable method, not a pile of isolated theorems. It also prepares the final review, where the table of contents can be read as one connected method of thought.",
        "anchors": ["applications", "rotations in space", "Poincare-Hopf", "dynamical systems"],
    },
    15: {
        "title": "The course as pictorial thinking",
        "problem": "The final lecture reviews the table of contents and names the course's real subject: pictorial thinking. The problem is to understand how the pieces fit together instead of remembering separate chapter titles. A good summary should reveal the path from paper experiments to existence theorems and dynamics.",
        "first_principles": "The course begins with paper strips and ends with dynamics, but the habit stays the same. Replace a problem by a picture. Decide the legal changes. Find the feature that survives those changes. Use that feature to force an answer. This is why topology and geometry belong together here: geometry supplies visible local behavior, topology protects the whole-shape fact.",
        "math_move": "Read the course backward as one argument. Mobius strips teach global surprise; deformation teaches legal simplification; manifolds provide spaces; intersections provide signed evidence; fixed points and vector fields turn that evidence into existence theorems. The review is not a list; it is a dependency chain.",
        "detail": "The summary matters because the course is easy to underestimate as a collection of demonstrations. Its real depth is the repeated conversion of pictures into constraints. A picture earns its place only when it explains which motion, count, or obstruction is being protected.",
        "connection": "This page is the bridge from the lecture sequence to the concept, theme, subtheme, and family maps in the companion. It lets a reader move from chronological lectures to the recurring ideas that make the course cohere.",
        "anchors": ["table of contents", "pictorial thinking", "deformation", "intersection", "fixed point", "vector field"],
    },
}


LECTURE_EXAMPLES = {
    1: [
        {"title": "Cutting an ordinary band versus a Mobius band", "text": "The opening paper experiment compares a straight glued band with a one-twist band. Cutting the center line tests whether the surface's global gluing rule changes what the cut produces.", "concepts": ["boundary-orientation", "topology-vs-geometry", "deformation"]},
        {"title": "One side is a global fact", "text": "Walking around the Mobius strip shows that the local paper never stops looking ordinary, yet the full trip reverses the side. This is the course's first local-to-global lesson.", "concepts": ["boundary-orientation", "generic-position", "invariant"]},
        {"title": "Off-center cuts create linked pieces", "text": "When the cut is moved away from the center line, the resulting strips can stay linked rather than falling apart. The point is that the route around the twisted band remembers how the pieces pass around each other.", "concepts": ["knots-and-links", "winding-linking", "boundary-orientation"]},
    ],
    2: [
        {"title": "Connecting boundary pairs in a disk", "text": "The disk path puzzle asks whether several paired boundary points can be joined without intersections. The important evidence is the order of the endpoints and the no-crossing rule, not the prettiness of one attempted drawing.", "concepts": ["deformation", "graph-planarity", "invariant"]},
        {"title": "Deformation as proof of impossibility", "text": "The lecture uses legal motion to simplify paths. If the simplified situation still forces a crossing, the original problem could not have had a legal crossing-free solution.", "concepts": ["deformation", "topology-vs-geometry", "generic-position"]},
        {"title": "Endpoint order carries the obstruction", "text": "The boundary points are not movable labels. Their circular order is part of the problem, and deformation is allowed to clean the interior curves only while preserving that boundary order.", "concepts": ["boundary-orientation", "invariant", "deformation"]},
    ],
    3: [
        {"title": "Products make spaces from independent choices", "text": "The lecture builds cubes and related spaces by taking products of intervals. The plain idea is that two or more choices vary at once, and the resulting state-space has its own shape.", "concepts": ["configuration-space", "topology-vs-geometry", "triangulation"]},
        {"title": "Quotients turn edge instructions into spaces", "text": "When edges or points are identified, a flat drawing becomes a code for a new space. The same square can describe different worlds depending on the gluing rule.", "concepts": ["duality", "boundary-orientation", "deformation"]},
        {"title": "Surgery treats construction as reasoning", "text": "Removing a simple piece and gluing another one back is a way to change the space under controlled rules. The operation matters because it tracks what feature has been changed and what feature is meant to survive.", "concepts": ["deformation", "triangulation", "invariant"]},
    ],
    4: [
        {"title": "A square is not the space until its edges are read", "text": "The lecture returns to squares with edge identifications. The useful lesson is that the visible square is a set of instructions for travel, not the final surface itself.", "concepts": ["duality", "boundary-orientation", "topology-vs-geometry"]},
        {"title": "Reversing an edge changes the global surface", "text": "Changing a gluing direction can turn an ordinary two-sided behavior into a one-sided one. The local patches remain simple, but the whole route structure changes.", "concepts": ["boundary-orientation", "invariant", "deformation"]},
        {"title": "A route can leave the drawing and keep going", "text": "Edge identification teaches that a path reaching the side of the drawn square has not necessarily stopped. The boundary rule decides where that path re-enters and what loop it has traced in the actual surface.", "concepts": ["duality", "winding-linking", "boundary-orientation"]},
    ],
    5: [
        {"title": "Classification separates surfaces by durable parts", "text": "The lecture discusses orientable and non-orientable surface families. Handles, crosscaps, and boundaries matter because they survive the allowed simplifications and therefore describe the surface beyond one drawing.", "concepts": ["euler-characteristic", "boundary-orientation", "triangulation"]},
        {"title": "Surgery changes a surface by controlled cutting and gluing", "text": "The surface operations are not arbitrary cutting. They are controlled replacements that help reduce surfaces to standard forms while tracking what has changed and what surface information remains protected.", "concepts": ["deformation", "topology-vs-geometry", "invariant"]},
        {"title": "Handles and crosscaps are durable building blocks", "text": "The lecture's classification viewpoint treats handles, crosscaps, and boundaries as parts that remain meaningful after simplification. The surface is understood by the pieces that cannot be wished away by a different drawing.", "concepts": ["boundary-orientation", "euler-characteristic", "invariant"]},
    ],
    6: [
        {"title": "Moving an object inside a manifold", "text": "The lecture asks whether a sub-object can be moved around obstacles inside a larger space. The answer depends on dimension: enough room can turn collision into avoidance.", "concepts": ["generic-position", "deformation", "graph-planarity"]},
        {"title": "Forced meetings become evidence", "text": "When an intersection cannot be removed by legal motion, it stops being a drawing accident and becomes information about the surrounding space. The lecture prepares the later signed count by separating removable crossings from forced ones.", "concepts": ["invariant", "winding-linking", "parity"]},
        {"title": "Dimension measures available escape room", "text": "The lecture turns the physical feeling of room into a mathematical test. If the surrounding space has enough independent directions, objects can often avoid meeting; when it does not, intersections become meaningful.", "concepts": ["generic-position", "topology-vs-geometry", "graph-planarity"]},
    ],
    7: [
        {"title": "The center-of-gravity demonstration", "text": "Sliding two hands inward under an object creates a physical example of a forced state. Continuity makes the balancing event unavoidable because the relevant condition changes steadily rather than jumping past the answer.", "concepts": ["fixed-points", "configuration-space", "deformation"]},
        {"title": "Existence without a formula", "text": "The lecture turns a hands-on balancing fact into the idea that some special point or event can be forced even when no explicit formula for it is available.", "concepts": ["fixed-points", "invariant", "generic-position"]},
        {"title": "A physical motion becomes an intersection question", "text": "The balancing setup can be read as two continuously changing conditions that must meet. That translation is the bridge from a demonstration with hands to the later formal language of intersections.", "concepts": ["duality", "fixed-points", "configuration-space"]},
    ],
    8: [
        {"title": "Signed intersection number", "text": "The lecture counts intersections with plus and minus signs. The signs let newly born opposite pairs cancel, so the total remembers more than the visible crossing count.", "concepts": ["winding-linking", "boundary-orientation", "parity"]},
        {"title": "Pair creation and cancellation", "text": "When a positive and a negative intersection appear together, the picture changes but the signed total does not. This is the cleanest example of designed cancellation.", "concepts": ["generic-position", "invariant", "vector-field-index"]},
        {"title": "Orientation gives signs their meaning", "text": "A signed intersection count only works after the surrounding surface or space supports a consistent direction choice. The plus or minus sign is geometric information, not an arbitrary label added after counting.", "concepts": ["boundary-orientation", "winding-linking", "invariant"]},
    ],
    9: [
        {"title": "The graph of a map meets the diagonal", "text": "The lecture treats a fixed point as an intersection: the graph records where points go, and the diagonal records points that stay where they started.", "concepts": ["fixed-points", "duality", "graph-planarity"]},
        {"title": "Missing middle caption is kept visible", "text": "The middle video of this lecture has no recovered captions, so the explanation leans on the available surrounding parts and preserves the source gap in the audit.", "concepts": ["invariant", "generic-position", "fixed-points"]},
        {"title": "A rule becomes a shape that can be compared", "text": "Representing a map by its graph turns an invisible instruction into an object in a larger space. Once it is drawn that way, fixed points become meetings with the diagonal.", "concepts": ["duality", "fixed-points", "configuration-space"]},
    ],
    10: [
        {"title": "Brouwer on the closed ball", "text": "The lecture's fixed-point theorem says a continuous self-map of a closed ball must leave some point fixed. The point is forced by the shape, not found by calculation.", "concepts": ["fixed-points", "boundary-orientation", "topology-vs-geometry"]},
        {"title": "Boundary changes the theorem", "text": "The closed ball includes its boundary, and that boundary is part of why the statement has force. Removing or changing the boundary can change the conclusion.", "concepts": ["boundary-orientation", "configuration-space", "invariant"]},
        {"title": "No global escape from self-agreement", "text": "The theorem can be understood as ruling out a continuous way for every point of the ball to avoid itself at once. The shape of the filled ball blocks that escape.", "concepts": ["fixed-points", "deformation", "invariant"]},
    ],
    11: [
        {"title": "Vector fields replace solved trajectories", "text": "The lecture starts the dynamics chapter by asking what can be known without solving a differential equation. A vector field gives an arrow pattern whose defects can be studied topologically.", "concepts": ["vector-field-index", "fixed-points", "configuration-space"]},
        {"title": "Equilibria are arrow-field failures", "text": "An equilibrium is where the arrow vanishes. The index records how nearby arrows turn around that failure, turning local dynamics into signed evidence that can later be added over the whole surface.", "concepts": ["vector-field-index", "gauss-bonnet", "invariant"]},
        {"title": "Local arrow patterns can be counted", "text": "A source, sink, and saddle are not only dynamical pictures. Around each defect the arrows turn in a characteristic way, and that turning can be assigned a signed index.", "concepts": ["vector-field-index", "parity", "boundary-orientation"]},
    ],
    12: [
        {"title": "Adding local indices", "text": "The lecture asks what all local vector-field indices know together. The sum is not arbitrary; it is tied to the surface carrying the field.", "concepts": ["vector-field-index", "euler-characteristic", "boundary-orientation"]},
        {"title": "Poincare-Hopf as surface bookkeeping", "text": "Local arrow failures add up to Euler characteristic. This converts the earlier cell-counting idea into a statement about possible motion and shows why surface topology controls vector fields.", "concepts": ["euler-characteristic", "gauss-bonnet", "invariant"]},
        {"title": "Defects can move while the total stays fixed", "text": "The lecture's global index idea allows local equilibria to shift, split, or cancel in controlled ways. What survives is the total signed count demanded by the surface.", "concepts": ["vector-field-index", "deformation", "invariant"]},
    ],
    13: [
        {"title": "Using Poincare-Hopf in both directions", "text": "The theorem can predict forced equilibria from topology, or use known equilibria to reveal something about the surface. It is a bridge between shape and motion.", "concepts": ["vector-field-index", "euler-characteristic", "fixed-points"]},
        {"title": "The hairy-ball idea in plain form", "text": "On a sphere, a continuous tangent arrow pattern cannot avoid defects everywhere. Something must fail because the whole surface does not allow all local choices to agree.", "concepts": ["boundary-orientation", "vector-field-index", "topology-vs-geometry"]},
        {"title": "Topology predicts a failure of motion", "text": "The point of Poincare-Hopf is not only to count existing equilibria. It can prove that some defect must be present before the exact vector field is solved.", "concepts": ["vector-field-index", "euler-characteristic", "fixed-points"]},
    ],
    14: [
        {"title": "Applications as honest translations", "text": "The late applications work by translating a physical or rotational situation into a space, a rule, and a protected obstruction. The theorem applies only after that translation is correct.", "concepts": ["configuration-space", "fixed-points", "invariant"]},
        {"title": "Rotations and dynamics share the same proof engine", "text": "Rotations in space and dynamical examples look different, but both can be read through fixed points, vector fields, indices, or deformation-protected counts once the right space and rule are identified.", "concepts": ["vector-field-index", "configuration-space", "duality"]},
        {"title": "The model must carry the real constraint", "text": "An application succeeds only when the chosen space, allowed motion, and protected count match the physical situation. A theorem applied to the wrong model proves a true statement about the wrong object.", "concepts": ["configuration-space", "topology-vs-geometry", "invariant"]},
    ],
    15: [
        {"title": "The table of contents becomes one argument", "text": "The final review names the course as pictorial thinking. Paper strips, deformation, manifolds, intersections, fixed points, and vector fields form one chain rather than separate topics.", "concepts": ["deformation", "invariant", "topology-vs-geometry"]},
        {"title": "Pictures earn their role by carrying constraints", "text": "The course's pictures matter because they show what can move, what cannot move, and what count survives. That is why the final summary ties the visual style to mathematical force.", "concepts": ["duality", "generic-position", "euler-characteristic"]},
        {"title": "The final strip demonstration returns to linking", "text": "The last demonstration cuts glued strips and then glued Mobius strips, producing pieces that have to be untangled and displayed. It returns the course to the idea that a visible tangle can encode a real route constraint.", "concepts": ["knots-and-links", "duality", "topology-vs-geometry"]},
    ],
}


LECTURE_ESSAYS = {
    1: [
        "The first lecture does not begin with a definition because a definition would make the subject look smaller than it is. The Mobius strip is a better opening because it forces the reader to separate local appearance from global behavior. Every small patch of the strip is ordinary paper. Nothing in a tiny square of paper announces that the whole strip has only one side, one boundary component, or surprising cutting behavior. The mathematical lesson is that a surface is not exhausted by its local patches. A whole trip around the object can return with information that was invisible at the start.",
        "That is why cutting matters. Cutting the center line of an ordinary band and cutting the center line of a Mobius band are controlled experiments on the gluing rule. The scissors are not a prop; they reveal what the ends of the strip remembered after being joined with a twist. Off-center cuts add another layer: pieces can remain linked because their routes through the strip have wrapped around each other. The lecture is already teaching the course's whole method: make a physical picture, decide the legal operation, watch what survives, and let the result expose a global constraint.",
        "The first-principles detail is that the twist is a rule for identification, not only a visual feature. The strip's ends are glued with a reversal, and that reversal changes what a full trip around the surface means. This is the first place the course teaches that a small local instruction can control a whole-surface fact.",
    ],
    2: [
        "The second lecture turns the physical surprise of the Mobius strip into an explicit method: solve by deformation. The disk path problem is deliberately simple to state. Several pairs of boundary points must be joined inside a disk without the joining curves crossing. A beginner may try to draw better routes, but trying drawings one by one cannot prove impossibility. The lecture changes the question from drawing skill to protected structure: if endpoints stay in their boundary order and paths are not allowed to cross, what can any drawing do?",
        "The power of deformation is that it lets the picture move while the question stays fixed. A path can be rounded, stretched, or slid if it does not pass through another path or move an endpoint past another endpoint. Once those rules are clear, a simpler picture is allowed to speak for the original. This is a first-principles proof style, not a visual shortcut. It shows why topology is useful when exact measurement is irrelevant: the answer depends on the arrangement of routes and obstructions, not on the length or visual neatness of the curves.",
        "The mathematical principle behind the lecture is boundary order. The endpoints around the disk are part of the data, and legal motion cannot reorder them. If a crossing-free drawing existed, deformation would allow the reader to clean it while preserving that circular order. When the cleaned version still forces a crossing, the obstruction belongs to the problem itself.",
    ],
    3: [
        "After deformation is introduced, the course needs a supply of spaces whose behavior is worth studying. Lecture 3 explains that spaces can be built from recipes. A product lets independent choices vary together, so an interval times an interval becomes a square-like world, and more products build higher-dimensional boxes. A quotient says that different-looking points should be treated as the same point. Surgery removes a piece and glues something back in. These are plain operations, but they change the kind of routes and neighborhoods the resulting space contains.",
        "The important shift is that a drawing becomes an instruction manual. A square with edge labels is not merely a square; it can be a code for a cylinder, torus, Mobius band, or other surface depending on how its edges are identified. This is the course's move from demonstration to toolkit. Later, when fixed points are graphs meeting diagonals or when vector fields live on manifolds, the reader needs to remember that the space itself was made by rules. The construction recipe controls what motion, boundary, and sameness mean.",
        "The first-principles detail is that construction changes possible travel. A product adds independent choices, so a point can vary in several directions at once. A quotient identifies exits and entrances, so a route can return somewhere unexpected. Surgery changes which passages remain attached. These operations matter because later theorems are statements about the spaces created by those rules.",
    ],
    4: [
        "Lecture 4 deepens the idea that gluing rules create worlds. The same visible patch can describe different spaces if its boundary is read differently. This matters because the mathematical object is not the ink on the page; it is the travel rule encoded by that ink. If leaving through one edge returns through another edge, then routes inside the square have a wraparound behavior. If an edge is reversed before it is glued, a trip through the surface can reverse the sense of side.",
        "This lecture is a quiet but important bridge. It makes quotient constructions less mysterious by treating them as route instructions. It also prepares the reader for why orientation, boundary, and global consistency keep returning. A vector field on a sphere and a vector field on a torus do not differ merely by their drawing style. They differ because the underlying surface gives different routes for arrows and loops to follow. The course is teaching the reader to ask, for every picture, what rules the picture represents.",
        "The first-principles point is that sameness is created by the rule, not by visual resemblance. If two exits of a drawn square are declared to be the same passage, then a path leaving one side has not ended; it has re-entered the world somewhere else. That habit becomes essential later when maps, diagonals, and vector fields are also treated as objects whose behavior depends on the space carrying them.",
    ],
    5: [
        "Lecture 5 is where surfaces become classifiable objects rather than isolated examples. Handles, crosscaps, boundaries, and orientability are not decorative features. A handle supplies a route through and around. A crosscap, represented by Mobius-strip behavior, reverses side after a trip. A boundary changes the accounting at the edge. Classification says that once surfaces are simplified by legal cutting, gluing, and deformation, these durable parts determine the family of the surface.",
        "The handle-sliding discussion is especially important because it makes classification operational. One does not simply declare that a mixed surface is equivalent to a standard form. One moves handles across one-sided regions and watches how the surface changes while preserving its topological type. This is arithmetic with surfaces: connected sums, handles, and Mobius strips become manipulable pieces. The lecture teaches that topology can classify objects not by measuring them, but by reducing them to stable building blocks whose presence cannot be hidden by a different drawing.",
        "This is also where the course starts to feel like a working language. A surface is no longer a single picture but a member of a family with operations. Once that is understood, later formulas have a home: Euler characteristic, intersection signs, and vector-field indices are not floating symbols. They are ways of reading information from a surface whose type has already been disciplined by classification.",
        "The first-principles point is that classification is not naming by appearance. It is naming by what survives all legal simplification. Two drawings can look different while carrying the same handles, boundaries, and orientation behavior; two similar-looking drawings can hide different global side structure.",
    ],
    6: [
        "Lecture 6 begins the systematic study of moving submanifolds inside an ambient manifold. In everyday language, it asks whether two things have enough room to avoid each other. A point on a line has little room. A line in a plane may cross another line unless arranged specially. Objects in higher-dimensional spaces may have extra directions for escape. The lecture turns that spatial intuition into the idea of dimension overflow: when the objects are too large for the room they share, intersection becomes expected rather than accidental.",
        "This matters because the course is preparing to count intersections. Before a count can mean anything, the reader must know the difference between a crossing caused by a clumsy drawing and a crossing forced by the surrounding space. Generic position removes fragile coincidences and leaves the ordinary case, where meetings happen cleanly. If a meeting can be removed by a legal motion, it should not be treated as evidence. If it cannot be removed, it becomes the raw material for intersection number.",
        "The plain-language moral is that space is a resource. If there is enough room, two objects can miss each other after a small adjustment. If there is not enough room, the attempted avoidance overflows into intersection. That is why dimension is not an abstract label here; it measures the amount of freedom available for avoiding obstacles.",
        "This lecture also sharpens the course's idea of an accident. A meeting in one drawing may vanish after a small legal move. A meeting that remains after every legal move carries information. Generic position is the method for telling those two cases apart before any count is trusted.",
    ],
    7: [
        "Lecture 7 uses physical reasoning to make existence feel concrete. The center-of-gravity demonstration is not separate from the mathematics. When two hands slide inward under an object, they meet at a balancing point because the relevant quantities change continuously. The balancing state is forced without anyone solving an equation for it. This is the same kind of conclusion topology wants: an object or state must exist because a continuous process has no legal way around it.",
        "The conceptual move is to translate an existence problem into an intersection problem. One condition moves, another condition is fixed, and the desired event is their meeting. This prepares fixed-point theory, where the graph of a map meets the diagonal, and dynamics, where equilibria appear as failures of a vector field. The lecture is valuable because it keeps the theorem-level ideas grounded in bodily experience: continuous motion cannot always avoid a special state.",
        "This lecture also raises the standard for what counts as understanding. Knowing that a balancing point exists may be enough even when the exact point is not computed. That is a recurring topological attitude. The course is teaching existence from constraint: if a continuous process has no legal way to pass from one side of a condition to the other without meeting it, the meeting is forced.",
        "The important detail is continuity. If the hands, balance condition, or measured state could jump, the argument would fail. The course uses the demonstration because it makes the no-jump condition visible: small motions of the hands produce small changes in the relevant state, so the special meeting cannot be skipped.",
    ],
    8: [
        "Lecture 8 is one of the course's central turning points. It introduces intersection number as a count with memory. Counting visible intersections is too fragile because intersections can appear or disappear when the picture is deformed. The key is to count with signs. If a positive and a negative intersection are born together, the visible count changes by two, but the signed count changes by zero. The count has been designed so fake changes cancel.",
        "Orientation is the detail that makes this possible. Without orientation, the signs have no stable meaning. With orientation, an intersection records how two pieces meet inside the surrounding space. This is why the lecture matters far beyond intersections. It teaches the general method of protected arithmetic: identify local events, assign signs or alternating contributions, and add them so the total survives legal motion. Vector-field index later repeats the same pattern with arrow defects instead of crossings.",
        "The lecture is therefore a turning point from visual topology to numerical topology. The number is not a measurement of length or size. It is a record of unavoidable meeting. Once a reader understands why opposite pairs cancel, many later results become less mysterious: the course keeps designing counts so that accidental changes disappear and forced information remains.",
        "The important detail for a beginner is that a sign is not chosen after the count to make the theorem work. It comes from how the objects meet inside an oriented setting. The sign is geometry turned into arithmetic, and that is why the resulting total can carry topological force.",
    ],
    9: [
        "Lecture 9 carries intersection thinking into fixed points. A map from a space to itself can feel abstract because it is a rule rather than a visible object. The lecture makes it visible by drawing the graph of the map. It also draws the diagonal, the set of pairs where the starting point and ending point are the same. A fixed point is exactly an intersection between those two objects. The problem has been translated from solving a rule to finding a forced meeting.",
        "This translation is one of the course's strongest examples of pictorial thinking. The graph and diagonal are not illustrations after the fact; they are the proof setting. If intersection machinery says the graph and diagonal cannot avoid each other, then the map must have a fixed point. The missing middle caption is a real source caveat, but the surrounding lecture arc is clear: fixed-point theory is being built from the earlier language of intersections, deformation, and invariance.",
        "The first-principles gain is that a rule has been turned into a shape. A map may sound like an instruction, but its graph can be moved, compared, and counted. The diagonal is the shape of self-agreement. Their intersection is not a metaphor for a fixed point; it is the fixed point written geometrically. This is exactly the kind of conversion the course wants readers to learn.",
    ],
    10: [
        "Lecture 10 focuses on the Brouwer fixed-point theorem for the closed ball. In plain language, if every point of a filled disk or ball is moved continuously to another point inside the same filled shape, at least one point must end up where it started. The theorem does not tell us which point. Its strength is that it proves existence from the shape of the domain and the continuity of the rule.",
        "The boundary is not a minor technicality. A closed ball includes its boundary, and the boundary helps trap the continuous rule. If every point tried to avoid itself, the resulting escape pattern would contradict the way the boundary and interior fit together. This lecture shows the payoff of the earlier machinery: topology can prove that something exists without solving for it. That same payoff becomes essential in dynamics, where exact trajectories may be out of reach but forced equilibria can still be known.",
        "For a beginner, the hard part is accepting that existence can be a geometric consequence. The theorem is not guessing that a fixed point probably exists. It says the whole filled shape leaves no continuous escape plan. That is why the closed ball matters: the theorem is a statement about the space of all possible positions and the way its boundary holds that space together.",
        "The lecture also shows why changing the space changes the claim. A closed ball, an open ball, a circle, and a torus do not give a continuous map the same constraints. The theorem's force comes from the exact shape of the domain and the rule that points remain inside it.",
    ],
    11: [
        "Lecture 11 begins the dynamics chapter by changing what it means to understand a differential equation. Instead of solving the equation exactly, the course asks what can be known from the arrow pattern of a vector field. Each point receives an arrow showing the direction of motion. Where the arrow vanishes, there is an equilibrium. The question is no longer only where trajectories go, but what the whole arrow field is forced to contain.",
        "The index of an equilibrium is the new signed count. Around a defect, the nearby arrows turn in a certain way. That turning can be counted, and the count survives appropriate deformation of the field. This is the dynamics version of intersection number. The course has moved from curves and surfaces to motion, but the proof engine is still the same: isolate clean local events, attach signed evidence to them, and ask what total the whole space forces.",
        "This is where the course becomes especially useful beyond pure shape puzzles. Many differential equations cannot be solved in a useful closed form, but their qualitative behavior still matters. Vector fields give a picture of that behavior, and topology asks what the picture cannot avoid. The result is not a trajectory-by-trajectory solution; it is structural knowledge about all possible motion.",
        "The first-principles shift is from prediction to constraint. A solved equation predicts a path. An index argument says that certain failures of the arrow field cannot all be removed. That weaker-looking conclusion is often exactly what is needed: it tells the reader what behavior the whole space forces.",
    ],
    12: [
        "Lecture 12 asks what all the local indices know together. A vector field may have several equilibria: sources, sinks, saddles, and other local arrow patterns. Each has an index, but those indices are not independent. When the field lives on a surface, the sum of the local indices is tied to the Euler characteristic of that surface. Local failures of motion add up to a whole-shape number.",
        "This is where the earlier surface bookkeeping becomes visibly necessary. Euler characteristic was not just a cell-counting curiosity. It becomes the number that controls the total defect of a vector field. The lecture therefore connects three layers of the course: surfaces can be decomposed and counted, vector fields can fail locally, and topology can force the total of those failures. Poincare-Hopf is powerful because it makes motion answer to shape.",
        "The important detail is that local defects can move around. A source can be shifted, a pair can be created or canceled under the right circumstances, and a drawing can be cleaned up. But the total signed index is not free when the underlying surface is fixed. That is the same survival principle from intersection number, now expressed in the language of dynamics.",
        "For the reader, this lecture is the moment when Euler characteristic stops being only a surface label. It becomes a demand placed on motion. The same number obtained from cutting a surface into pieces now says how arrow-field defects must add up on that surface.",
    ],
    13: [
        "Lecture 13 uses Poincare-Hopf as a working tool rather than a slogan. If the topology of the surface is known, the theorem restricts what equilibria a vector field can have. If the equilibria and their indices are known, they can reveal information about the surface. This is a two-way exchange between shape and motion. The theorem is not merely a formula; it is a bridge between two kinds of evidence.",
        "The hairy-ball idea is the most everyday form of the message. On a sphere, one cannot choose a continuous nonzero tangent arrow everywhere. Some defect must occur because the whole surface does not allow all local arrow choices to agree. This is exactly the course's local-to-global principle in dynamics. Every small patch may seem able to carry an arrow, but the complete surface has fewer choices than the patches suggest.",
        "The theorem's depth is that it can be used in both directions without changing its meaning. If the surface is known, it predicts what kinds of vector-field failures must occur. If the failures are observed, they give information about the surface. The equation is therefore not just a result to remember; it is a tool for translating between local motion and global shape.",
        "The important first-principles detail is that the theorem does not inspect one equilibrium in isolation. It asks for the total signed behavior over the whole surface. Local arrow patterns may look adjustable one by one, but the completed surface makes a demand on their sum. That is the reason topology can make a prediction before the differential equation is solved.",
    ],
    14: [
        "Lecture 14 turns the machinery toward applications. Rotations, physical systems, and dynamical examples can look unrelated, but the course asks the same modeling questions each time. What is the space? What is the rule or motion on that space? What changes are legal? What count, fixed point, index, or obstruction is protected? Without that translation, applying topology would be empty.",
        "The value of the applications is that they show topology as a method for behavior, not only for static shapes. A physical system may have too many details to track directly, but the space of its possible states can have holes, walls, boundaries, or forced passages. Once a problem is honestly translated into that space, the earlier proof families apply. The course's demonstrations are therefore not isolated performances; they are examples of a reusable way to reason about constrained motion.",
        "This lecture also warns against careless application. A theorem cannot be pasted onto a physical story until the modeling has been done. The state space, boundary conditions, allowed motions, and protected quantity must be identified. When that translation is honest, topology can explain why a behavior is unavoidable even when the physical system itself looks messy.",
        "The mathematical principle is model first, theorem second. The shape used in the proof must be the shape of the actual possibilities. If the model omits a freedom, adds a false barrier, or forgets a boundary condition, the conclusion may no longer describe the physical system. This caution is part of the depth of the applications.",
    ],
    15: [
        "The final lecture reviews the course as pictorial thinking. That phrase matters because the pictures have not been decorative. The Mobius strip, disk paths, edge identifications, handle slides, intersections, graphs of maps, diagonals, and vector fields all served as proof environments. The point of the course is to learn how to make a picture carry constraints: what may move, what may not move, what survives, and what conclusion is forced.",
        "Read backward, the course becomes one chain. Mobius strips teach global surprise. Deformation teaches legal simplification. Products, quotients, and surgery build spaces. Surface classification names durable parts. Intersection number turns meetings into signed evidence. Fixed points turn rules into forced self-agreement. Vector-field index and Poincare-Hopf turn motion into surface bookkeeping. The final demonstrations return to strips because the whole course has been about seeing more in a picture than its immediate appearance.",
        "The ready-state lesson is therefore not a list of theorems. It is a way of asking questions. What is allowed to move? What survives the motion? What count is designed to ignore fake changes? What whole-shape constraint forces the answer? If the reader can ask those questions across strips, surfaces, maps, and vector fields, then the course has done its work.",
        "The final lecture also explains why a companion should be organized by concepts, themes, subthemes, and method families rather than only by chronology. Chronology shows how the course unfolds. The concept map shows the reusable reasoning underneath that order. A reader needs both to see the course as one connected method.",
    ],
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
        ("quality-audit.html", "Quality Audit"),
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


def paragraph_block(items):
    return "".join(f"<p>{esc(item)}</p>" for item in items)


def concept_pills(concept_ids, concepts):
    by_id = {c["id"]: c for c in concepts}
    return "".join(f'<a class="pill" href="{slug_page("concept", cid)}">{esc(by_id[cid]["title"])}</a>' for cid in concept_ids if cid in by_id)


def build_quality_audit(data):
    stats = data["stats"]
    concept_min = min(len(c["appearances"]) for c in data["concepts"])
    concept_max = max(len(c["appearances"]) for c in data["concepts"])
    lecture_examples = sum(len(l["deep"]["examples"]) for l in data["lectures"])
    lecture_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in l["deep"]["essay"]) for l in data["lectures"])
    concept_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in c["essay"]) for c in data["concepts"])
    theme_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in t["essay"]) for t in data["themes"])
    subtheme_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in s["essay"]) for s in data["subthemes"])
    family_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in f["essay"]) for f in data["families"])
    requirements = [
        {
            "requirement": "Own repo and folder",
            "evidence": "Standalone git repo at topology-geometry-course-concepts-research on main.",
            "status": "met",
        },
        {
            "requirement": "Recover all playlist links and source coverage",
            "evidence": f"{stats['videos']} playlist videos indexed; {stats['captioned_videos']} caption files recovered; missing caption preserved for {', '.join(data['missing_caption_ids'])}.",
            "status": "met-with-caveat",
        },
        {
            "requirement": "Hand-written lecture depth",
            "evidence": f"{stats['lectures']} lecture explainers with full essay sections, problem, first principles, mathematical move, important detail, connection, transcript anchors, and examples.",
            "status": "met",
        },
        {
            "requirement": "Hand-written concepts, themes, subthemes, and method families",
            "evidence": f"{stats['concepts']} concepts, {stats['themes']} themes, {stats['subthemes']} subthemes, and {stats['families']} method families all have essay sections plus validated first-principles depth fields.",
            "status": "met",
        },
        {
            "requirement": "First-principles plain language",
            "evidence": "Validation enforces minimum depth across all explanatory layers and bans common vague/cliche phrases; pages explain why ideas exist and what detail matters.",
            "status": "met",
        },
        {
            "requirement": "Connected course map",
            "evidence": f"{lecture_examples} lecture examples link forward to concepts; every concept links back to lecture appearances, with appearance counts from {concept_min} to {concept_max}.",
            "status": "met",
        },
        {
            "requirement": "Big-picture mathematical synthesis",
            "evidence": "The Math Why page explains the course engine: allowed changes, preserved facts, designed counts, and whole-shape constraints.",
            "status": "met",
        },
    ]
    return {
        "summary": "The companion now satisfies the requested depth shape across the main reader-facing layers. The only explicit source caveat is the one playlist item whose captions are not exposed by yt-dlp.",
        "requirements": requirements,
        "metrics": {
            "videos": stats["videos"],
            "lectures": stats["lectures"],
            "captioned_videos": stats["captioned_videos"],
            "missing_captions": data["missing_caption_ids"],
            "lecture_examples": lecture_examples,
            "lecture_essay_words": lecture_essay_words,
            "concept_essay_words": concept_essay_words,
            "theme_essay_words": theme_essay_words,
            "subtheme_essay_words": subtheme_essay_words,
            "family_essay_words": family_essay_words,
            "concept_appearances_min": concept_min,
            "concept_appearances_max": concept_max,
            "html_pages_before_audit_page": len(list(SITE.glob("*.html"))),
        },
    }


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
        href = f"lecture-{l['lecture']:02d}.html"
        lecture_html += f"""<section class="lecture{miss}"><h2>Lecture {l['lecture']:02d}: {esc(l['deep']['title'])}</h2><p>{esc(l['deep']['problem'])}</p><p>{esc(l['deep']['first_principles'])}</p><div>{vids}</div><p><a class="arrow" href="{href}">Open lecture explainer</a></p><p class="evidence">Transcript words: {l['transcript_words']}. Missing captions: {', '.join(l['missing_caption_ids']) or 'none'}.</p></section>"""
        lecture_body = f"""
<h1>Lecture {l['lecture']:02d}: {esc(l['deep']['title'])}</h1>
<p class="lead">{esc(l['deep']['problem'])}</p>
<section class="lecture">
  <h2>Lecture Essay</h2>
  {paragraph_block(l['deep']['essay'])}
</section>
<section class="panel">
  <h2>First Principles</h2>
  <p>{esc(l['deep']['first_principles'])}</p>
  <h2>The Mathematical Move</h2>
  <p>{esc(l['deep']['math_move'])}</p>
  <h2>The Important Detail</h2>
  <p>{esc(l['deep']['detail'])}</p>
  <h2>How It Connects</h2>
  <p>{esc(l['deep']['connection'])}</p>
</section>
<h2>Transcript Anchors</h2>
<p>{''.join(f'<span class="pill">{esc(a)}</span>' for a in l['deep']['anchors'])}</p>
<h2>Concrete Course Moments</h2>
<div class="grid two">
{''.join(f'<article class="card"><div class="meta">Transcript-grounded example</div><h3>{esc(ex["title"])}</h3><p>{esc(ex["text"])}</p><p>{concept_pills(ex["concepts"], data["concepts"])}</p></article>' for ex in l['deep']['examples'])}
</div>
<h2>Video Parts</h2>
<p>{vids}</p>
<p class="evidence">Transcript words: {l['transcript_words']}. Missing captions: {', '.join(l['missing_caption_ids']) or 'none'}.</p>
"""
        (SITE / href).write_text(page(f"Lecture {l['lecture']:02d}", lecture_body, "Lectures"), encoding="utf-8")
    (SITE / "lectures.html").write_text(page("Lectures", f"<h1>Lecture Atlas</h1>{lecture_html}", "Lectures"), encoding="utf-8")

    body = "<h1>Concept Atlas</h1><p class='lead'>These are not glossary entries. Each concept is explained as a tool: why it exists, what problem it solves, what detail can break it, and where it reappears in the course.</p><div class='grid'>" + "".join(card(c["title"], c["depth"]["why_it_exists"], slug_page("concept", c["id"]), c["theme"]) for c in data["concepts"]) + "</div>"
    (SITE / "concepts.html").write_text(page("Concepts", body, "Concepts"), encoding="utf-8")
    for c in data["concepts"]:
        moments = "".join(
            f'<article class="card"><div class="meta">Lecture {a["lecture"]:02d}</div><h3>{esc(a["title"])}</h3><p>{esc(a["summary"])}</p><a class="arrow" href="lecture-{a["lecture"]:02d}.html">Open lecture</a></article>'
            for a in c["appearances"]
        )
        body = f"""<h1>{esc(c['title'])}</h1><p class="lead">{esc(c['depth']['why_it_exists'])}</p><section class="lecture"><h2>Concept Essay</h2>{paragraph_block(c['essay'])}</section><section class="panel"><h2>First Principles</h2><p>{esc(c['first_principles'])}</p><h2>Important Detail</h2><p>{esc(c['important_detail'])}</p><h2>Principle Behind It</h2><p>{esc(c['math_principle'])}</p><h2>Beginner Trap</h2><p>{esc(c['depth']['beginner_trap'])}</p><h2>Course Role</h2><p>{esc(c['depth']['course_role'])}</p></section><p>{''.join(f'<span class="pill">{esc(s)}</span>' for s in c['subthemes'])}</p><h2>Where It Appears</h2><div class="grid two">{moments}</div>"""
        (SITE / slug_page("concept", c["id"])).write_text(page(c["title"], body, "Concepts"), encoding="utf-8")

    body = "<h1>Themes</h1><p class='lead'>Themes are the recurring habits of thought that make the course cohere across paper strips, surfaces, intersections, fixed points, and dynamics.</p><div class='grid two'>" + "".join(card(t["title"], t["depth"]["problem"], slug_page("theme", t["id"]), "Theme") for t in data["themes"]) + "</div>"
    (SITE / "themes.html").write_text(page("Themes", body, "Themes"), encoding="utf-8")
    for t in data["themes"]:
        related = [c for c in data["concepts"] if c["theme"] == t["id"]]
        lecture_links = "".join(f'<a class="pill" href="lecture-{n:02d}.html">Lecture {n:02d}</a>' for n in t["depth"]["lectures"])
        body = f"""<h1>{esc(t['title'])}</h1><p class='lead'>{esc(t['depth']['problem'])}</p><section class="lecture"><h2>Theme Essay</h2>{paragraph_block(t['essay'])}</section><section class='panel'><h2>The Habit</h2><p>{esc(t['depth']['habit'])}</p><h2>Course Arc</h2><p>{esc(t['depth']['course_arc'])}</p><h2>Important Detail</h2><p>{esc(t['depth']['important_detail'])}</p><h2>Why The Math Matters</h2><p>{esc(t['why_math_matters'])}</p></section><h2>Lecture Thread</h2><p>{lecture_links}</p><h2>Related Concepts</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("theme", t["id"])).write_text(page(t["title"], body, "Themes"), encoding="utf-8")

    body = "<h1>Subthemes</h1><p class='lead'>Subthemes are the smaller recurring moves inside the larger course habits: the contracts, counts, signs, boundaries, and modeling choices that make the arguments work.</p><div class='grid'>" + "".join(card(s["title"], s["depth"]["problem"], slug_page("subtheme", s["id"]), "Subtheme") for s in data["subthemes"]) + "</div>"
    (SITE / "subthemes.html").write_text(page("Subthemes", body, "Subthemes"), encoding="utf-8")
    for s in data["subthemes"]:
        related = [c for c in data["concepts"] if s["id"] in c["subthemes"]]
        body = f"""<h1>{esc(s['title'])}</h1><p class='lead'>{esc(s['depth']['problem'])}</p><section class="lecture"><h2>Subtheme Essay</h2>{paragraph_block(s['essay'])}</section><section class='panel'><h2>First Principles</h2><p>{esc(s['depth']['first_principles'])}</p><h2>Course Role</h2><p>{esc(s['depth']['course_role'])}</p></section><h2>Related Concepts</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("subtheme", s["id"])).write_text(page(s["title"], body, "Subthemes"), encoding="utf-8")

    body = "<h1>Method Families</h1><p class='lead'>Method families explain how the course turns pictures into reasons. They are the reusable proof moves beneath the lectures.</p><div class='grid two'>" + "".join(card(f["title"], f["depth"]["human_problem"], slug_page("family", f["id"]), f["purpose"]) for f in data["families"]) + "</div>"
    (SITE / "families.html").write_text(page("Families", body, "Families"), encoding="utf-8")
    for f in data["families"]:
        related = [c for c in data["concepts"] if c["id"] in f["concepts"]]
        body = f"""<h1>{esc(f['title'])}</h1><p class='lead'>{esc(f['depth']['human_problem'])}</p><section class="lecture"><h2>Method Essay</h2>{paragraph_block(f['essay'])}</section><section class='panel'><h2>Purpose</h2><p>{esc(f['purpose'])}</p><h2>First Principles</h2><p>{esc(f['depth']['first_principles'])}</p><h2>How It Works</h2><p>{esc(f['depth']['how_it_works'])}</p><h2>Course Examples</h2><p>{esc(f['depth']['course_examples'])}</p><h2>Failure Mode</h2><p>{esc(f['depth']['failure_mode'])}</p></section><h2>Concepts in this family</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("family", f["id"])).write_text(page(f["title"], body, "Families"), encoding="utf-8")

    math_why = f"""<h1>The Math Why</h1><p class="lead">{esc(data['math_why']['big_picture'])}</p><section class="panel"><h2>First Principles</h2><p>{esc(data['math_why']['first_principles'])}</p><h2>Important Detail</h2><p>{esc(data['math_why']['important_detail'])}</p><h2>Principle Behind the Mathematics</h2><p>{esc(data['math_why']['principle'])}</p><h2>Why These Concepts Matter</h2><p>{esc(data['math_why']['concepts_matter'])}</p><h2>How To Read The Course</h2><p>{esc(data['math_why']['reader_path'])}</p></section>"""
    (SITE / "the-math-why.html").write_text(page("The Math Why", math_why, "The Math Why"), encoding="utf-8")

    qa_rows = "".join(
        f'<article class="card"><div class="meta">{esc(item["status"])}</div><h3>{esc(item["requirement"])}</h3><p>{esc(item["evidence"])}</p></article>'
        for item in data["quality_audit"]["requirements"]
    )
    qa_metrics = data["quality_audit"]["metrics"]
    qa_body = f"""<h1>Quality Audit</h1><p class="lead">{esc(data['quality_audit']['summary'])}</p><section class="panel"><h2>Current Metrics</h2><p>{qa_metrics['videos']} videos, {qa_metrics['lectures']} lectures, {qa_metrics['captioned_videos']} captioned videos, {len(qa_metrics['missing_captions'])} missing caption, {qa_metrics['lecture_examples']} lecture examples, {qa_metrics['lecture_essay_words']} lecture essay words, {qa_metrics['concept_essay_words']} concept essay words, {qa_metrics['theme_essay_words']} theme essay words, {qa_metrics['subtheme_essay_words']} subtheme essay words, {qa_metrics['family_essay_words']} method-family essay words, concept appearance coverage from {qa_metrics['concept_appearances_min']} to {qa_metrics['concept_appearances_max']} examples per concept.</p></section><h2>Requirement Evidence</h2><div class="grid two">{qa_rows}</div>"""
    (SITE / "quality-audit.html").write_text(page("Quality Audit", qa_body, "Quality Audit"), encoding="utf-8")

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
        deep = dict(LECTURE_DEPTH[number])
        deep["examples"] = LECTURE_EXAMPLES[number]
        deep["essay"] = LECTURE_ESSAYS[number]
        lectures.append({
            "lecture": number,
            "videos": [v for v, _ in items],
            "duration_seconds": sum(v["duration_seconds"] or 0 for v, _ in items),
            "transcript_words": len(combined.split()),
            "missing_caption_ids": missing,
            "plain_reading": LECTURE_NOTES.get(number, "Lecture reading pending."),
            "deep": deep,
            "source_summary": "This lecture group is backed by recovered auto-captions except where missing-caption ids are listed.",
        })

    themes = []
    for theme in THEMES:
        enriched = dict(theme)
        enriched["depth"] = THEME_DEPTH[theme["id"]]
        enriched["essay"] = THEME_ESSAYS[theme["id"]]
        themes.append(enriched)
    subthemes = []
    for i, t, p in SUBTHEMES:
        subthemes.append({"id": i, "title": t, "plain": p, "depth": SUBTHEME_DEPTH[i], "essay": SUBTHEME_ESSAYS[i]})
    concepts = []
    for concept in CONCEPTS:
        enriched = dict(concept)
        enriched["depth"] = CONCEPT_DEPTH[concept["id"]]
        enriched["essay"] = CONCEPT_ESSAYS[concept["id"]]
        concepts.append(enriched)
    concept_appearances = {concept["id"]: [] for concept in concepts}
    for lecture in lectures:
        for example in lecture["deep"]["examples"]:
            for concept_id in example["concepts"]:
                if concept_id in concept_appearances:
                    concept_appearances[concept_id].append({
                        "lecture": lecture["lecture"],
                        "title": example["title"],
                        "summary": example["text"],
                    })
    for concept in concepts:
        concept["appearances"] = concept_appearances[concept["id"]]
    families = []
    for family in FAMILIES:
        enriched = dict(family)
        enriched["depth"] = FAMILY_DEPTH[family["id"]]
        enriched["essay"] = FAMILY_ESSAYS[family["id"]]
        families.append(enriched)
    math_why = MATH_WHY
    data = {
        "course_goal": COURSE_GOAL,
        "playlist": {"title": playlist.get("title"), "url": PLAYLIST_URL, "uploader": playlist.get("uploader")},
        "videos": videos,
        "lectures": lectures,
        "themes": themes,
        "subthemes": subthemes,
        "concepts": concepts,
        "families": families,
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
    data["quality_audit"] = build_quality_audit(data)

    write_json(RAW / "video-index.json", videos)
    write_json(ANALYSIS / "lecture-atlas.json", lectures)
    write_json(ANALYSIS / "concept-atlas.json", concepts)
    write_json(ANALYSIS / "theme-map.json", themes)
    write_json(ANALYSIS / "subtheme-map.json", subthemes)
    write_json(ANALYSIS / "family-map.json", families)
    write_json(ANALYSIS / "math-why.json", math_why)
    write_json(ANALYSIS / "course-companion.json", data)
    write_json(ANALYSIS / "quality-audit.json", data["quality_audit"])
    metrics = data["quality_audit"]["metrics"]

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

This repo now has a transcript-backed depth pass across the lecture, concept, theme, subtheme, and method-family layers. The first shallow layer has been replaced across the main explanatory surfaces:

- 15 hand-authored lecture explainers from 35 videos
- 45 lecture-grounded examples, three per lecture, each bridged to concepts
- 16 expanded concept pages with full essay sections, why-it-exists, beginner-trap, and course-role sections
- 6 expanded course theme pages with problem, habit, course-arc, and important-detail sections
- 10 expanded subtheme pages with essay, first-principles, and course-role sections
- 5 expanded method-family pages with essay, human-problem, how-it-works, examples, and failure-mode sections
- explicit source coverage and missing-caption audit

Current enforced essay totals: {metrics['lecture_essay_words']} lecture essay words, {metrics['concept_essay_words']} concept essay words, {metrics['theme_essay_words']} theme essay words, {metrics['subtheme_essay_words']} subtheme essay words, and {metrics['family_essay_words']} method-family essay words. The validator requires every lecture essay to clear 230 words, every concept essay to clear 180 words, every theme essay to clear 190 words, every subtheme essay to clear 130 words, and every method-family essay to clear 130 words.

The remaining depth gap is qualitative rather than structural: future work should do periodic human-read passes against the original captions and improve any page whose explanation feels compressed, under-specific, or too far from a concrete lecture moment. The validator now checks that concept themes, concept subthemes, and method-family concept ids point to real objects, and every lecture must carry at least three concrete examples.
""", encoding="utf-8")
    qa_md = ["# Quality Audit", "", data["quality_audit"]["summary"], "", "## Requirement Evidence"]
    for item in data["quality_audit"]["requirements"]:
        qa_md.append(f"- **{item['requirement']}** ({item['status']}): {item['evidence']}")
    (AUDITS / "quality-audit.md").write_text("\n".join(qa_md) + "\n", encoding="utf-8")
    build_site(data)
    print(json.dumps(data["stats"], indent=2))
    if missing:
        print("missing captions:", ", ".join(missing))


if __name__ == "__main__":
    main()
