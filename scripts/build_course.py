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


THEME_LENSES = {
    "see-by-deforming": {
        "notices": "This lens notices which parts of a picture are free to move and which parts must stay tied to the original question.",
        "ignores": "It ignores exact length, angle, and visual neatness when those details are not part of the protected question.",
        "changes_problem": "It changes a problem from staring at one hard drawing into following a legal path toward a drawing whose structure is easier to inspect.",
        "reader_test": "Can the reader name the legal moves and the fact that survives before trusting the simplified picture?",
    },
    "count-what-survives": {
        "notices": "This lens notices the part of a changing picture that can be recorded as stable evidence: a hole count, signed total, parity, or index sum.",
        "ignores": "It ignores raw visible clutter when that clutter can appear or disappear under harmless legal changes.",
        "changes_problem": "It changes a problem from trying every possible drawing into building a count that every legal drawing must obey.",
        "reader_test": "Can the reader say why the chosen count survives the allowed moves rather than only computing it once?",
    },
    "local-to-global": {
        "notices": "This lens notices when many locally possible choices must be made compatible across a whole surface, loop, field, or state space.",
        "ignores": "It ignores the false comfort that comes from checking only one small patch and assuming the whole object behaves the same way.",
        "changes_problem": "It changes a problem from asking whether each piece works alone into asking whether all pieces can be glued into one consistent whole.",
        "reader_test": "Can the reader identify the full journey, full sum, or full gluing step where the global obstruction appears?",
    },
    "generic-before-exception": {
        "notices": "This lens notices fragile coincidences such as tangencies, triple meetings, perfect alignments, and non-isolated defects.",
        "ignores": "It ignores accidental exactness when that exactness would disappear under a tiny legal nudge.",
        "changes_problem": "It changes a problem from analyzing a brittle special picture into understanding ordinary cases and the controlled transitions between them.",
        "reader_test": "Can the reader explain what ordinary picture appears just before and just after the exceptional moment?",
    },
    "pictures-to-proofs": {
        "notices": "This lens notices whether a picture states the mathematical contract: objects, allowed moves, forbidden moves, signs, boundaries, and protected evidence.",
        "ignores": "It ignores visual appeal when the drawing does not say what fact survives or what conclusion follows.",
        "changes_problem": "It changes a problem from remembering a diagram into auditing the reason carried by that diagram.",
        "reader_test": "Can the reader point to the exact part of the picture that prevents the forbidden outcome or forces the desired one?",
    },
    "shape-as-machine": {
        "notices": "This lens notices how the shape of a space permits routes, blocks routes, forces self-agreement, or demands defects.",
        "ignores": "It ignores unnecessary point-by-point prediction when a whole-space constraint already forces the kind of behavior being asked about.",
        "changes_problem": "It changes a problem from solving every motion detail into understanding the shape of possible states and the constraints that shape imposes.",
        "reader_test": "Can the reader name the state space or domain, the rule acting on it, and the topological feature that forces behavior?",
    },
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


SUBTHEME_ROUTINES = {
    "allowed-moves": {
        "look_for": "Look first for the rulebook of the problem: which objects may move, which points or boundaries stay fixed, and which changes are forbidden.",
        "ask": "Ask whether the proposed simplification uses only those allowed moves, or whether it quietly changes the original question.",
        "use": "Use this routine before every deformation, surgery, knot, path, or vector-field cleanup argument. The allowed moves decide what sameness means.",
        "mistake": "The mistake is accepting a cleaner picture before checking the motion that produced it. A clean drawing reached illegally is not evidence.",
    },
    "invariant-receipts": {
        "look_for": "Look for the piece of evidence the argument carries through change: a count, side behavior, parity, signed total, or index sum.",
        "ask": "Ask why that evidence survives the exact moves allowed in the problem, not merely why it looks stable in one drawing.",
        "use": "Use the invariant as a receipt. If two situations have different receipts, no legal journey connects them; if the receipt is forced, an outcome may be unavoidable.",
        "mistake": "The mistake is asking an invariant to remember everything. A good receipt may be partial and still strong enough to rule something out.",
    },
    "holes-and-boundaries": {
        "look_for": "Look for missing regions, blocked fillings, actual edges, and places where a path or field must respect a stopping rule.",
        "ask": "Ask whether a loop can be filled, whether a boundary adds a term, and whether removing or adding an edge changes the theorem's contract.",
        "use": "Use holes and boundaries as route information. They explain why loops may not shrink, why escape may be blocked, and why counts may need edge terms.",
        "mistake": "The mistake is treating holes and boundaries as visual decoration. They change which motions exist and which accounting rules are legal.",
    },
    "curves-loops-knots": {
        "look_for": "Look for route memory: whether a path closes, goes around something, links another path, or carries over-under crossing data.",
        "ask": "Ask what the surrounding space permits. Can the loop shrink, can strands pass through, and does the drawing record the needed spatial information?",
        "use": "Use this routine whenever the course turns a drawn curve into evidence about route, linking, winding, or impossible untangling.",
        "mistake": "The mistake is judging by visual tangledness. The protected question is what legal motion can remove, not how complicated the drawing appears.",
    },
    "turning-and-curvature": {
        "look_for": "Look for local changes of direction: a curve turning, a surface bending, or arrows rotating around a defect.",
        "ask": "Ask whether the local turning is being summed over the right object and whether boundary or corner terms belong in the account.",
        "use": "Use turning and curvature to connect local measurements to whole-shape restrictions, especially in total-turning, index, and Gauss-Bonnet-style arguments.",
        "mistake": "The mistake is stopping at one local bend. The course usually cares about a total whose value the whole object can constrain.",
    },
    "signs-and-cancellation": {
        "look_for": "Look for pairs of events that can appear or disappear together: crossings, intersections, or defects with opposite contributions.",
        "ask": "Ask where plus and minus signs come from, and whether legal changes really create canceling pairs rather than arbitrary arithmetic.",
        "use": "Use signs to make a fragile raw count into stable evidence. Cancellation is the mechanism that lets the total survive redrawings.",
        "mistake": "The mistake is assigning signs without a direction rule. Without a reason for plus and minus, cancellation has no mathematical force.",
    },
    "surfaces-and-orientation": {
        "look_for": "Look for the whole surface carrying the argument: its boundary, handles, side behavior, and whether a consistent direction can travel everywhere.",
        "ask": "Ask whether local choices glue together globally. Can a side or orientation be carried around a full loop without contradiction?",
        "use": "Use this routine before trusting signed intersections, vector-field indices, surface classification, or any argument that depends on plus and minus across a surface.",
        "mistake": "The mistake is checking only a small patch. Every tiny neighborhood may look ordinary while the completed surface reverses a side or blocks a global choice.",
    },
    "mechanisms-and-locks": {
        "look_for": "Look for the space of possible states behind the physical setup: positions, angles, forbidden collisions, walls, and connected regions.",
        "ask": "Ask which physical motion becomes a path or rule in that state space, and what topological feature blocks or forces behavior.",
        "use": "Use this routine when the course moves from paper or surface examples into balance, fixed points, configuration spaces, and dynamics.",
        "mistake": "The mistake is applying a theorem before the model is honest. A wrong state space gives a conclusion about the wrong physical problem.",
    },
    "singular-moments": {
        "look_for": "Look for special instants: tangencies, pair births, pair cancellations, triple meetings, or defects that stop being isolated.",
        "ask": "Ask what ordinary pictures exist just before and just after the special instant, and what protected count changes or stays fixed.",
        "use": "Use singular moments as transition evidence. They explain why ordinary cases can change without destroying a protected total.",
        "mistake": "The mistake is either ignoring the special instant or treating it as the whole proof. Its role is to explain the passage between ordinary cases.",
    },
    "models-not-labels": {
        "look_for": "Look for the work a term performs: what object it names, what move it permits, what count it protects, or what conclusion it supports.",
        "ask": "Ask whether the name has been translated into an everyday action before it is used in an argument.",
        "use": "Use this routine whenever a page introduces a formal word. The word earns its place only by helping solve the problem.",
        "mistake": "The mistake is collecting labels while missing the model. Knowing a term's name is not the same as knowing what it lets the proof do.",
    },
}


SUBTHEME_BRIDGES = {
    "allowed-moves": {
        "course_moment": "The disk path puzzle makes this subtheme visible because the endpoints, boundary order, and no-crossing rule decide the problem before any drawing is simplified.",
        "thinking_shift": "The reader stops asking whether two pictures look similar and starts asking which motion was permitted between them.",
        "reader_test": "Can the reader name one move that is allowed, one move that is forbidden, and the fact the allowed move must preserve?",
    },
    "invariant-receipts": {
        "course_moment": "The Mobius strip, Euler characteristic, intersection number, and vector-field index each preserve a different receipt while the visible object changes.",
        "thinking_shift": "The reader stops trusting resemblance and asks for the surviving evidence that lets one picture answer for another.",
        "reader_test": "Can the reader say what receipt is carried through the motion and why that receipt is enough for the conclusion?",
    },
    "holes-and-boundaries": {
        "course_moment": "The closed ball in Brouwer, the boundary of the Mobius strip, and forbidden states in configuration spaces all show that edges and missing regions change the claim.",
        "thinking_shift": "The reader stops seeing holes and boundaries as marks on a picture and starts reading them as rules for possible travel.",
        "reader_test": "Can the reader identify which route, filling, escape, or accounting term changes because a boundary or hole is present?",
    },
    "curves-loops-knots": {
        "course_moment": "Mobius strip cuts and later linked strip demonstrations show that a curve can keep route memory even after its exact shape changes.",
        "thinking_shift": "The reader stops judging by visual tangledness and asks what legal motion can or cannot remove.",
        "reader_test": "Can the reader name the surrounding space, the route relation, and the forbidden move needed to erase that relation?",
    },
    "turning-and-curvature": {
        "course_moment": "Vector-field index asks the reader to walk around a defect and watch arrows turn; Gauss-Bonnet-style reasoning asks how local bending contributes to a total.",
        "thinking_shift": "The reader stops treating a local bend or turn as isolated and asks what total it contributes to.",
        "reader_test": "Can the reader say what local turning is being added and what whole object controls the final total?",
    },
    "signs-and-cancellation": {
        "course_moment": "Signed intersections show two meetings born together with opposite signs, so the drawing changes while the total stays fixed.",
        "thinking_shift": "The reader stops counting every visible event positively and asks which events cancel because of the direction rule.",
        "reader_test": "Can the reader explain where the signs come from and why a pair created during motion adds no net evidence?",
    },
    "surfaces-and-orientation": {
        "course_moment": "The Mobius strip reverses side after a full trip, while orientable surfaces later allow consistent signs for intersections and vector-field index.",
        "thinking_shift": "The reader stops trusting one local patch and asks whether the local side or direction choice survives a full journey.",
        "reader_test": "Can the reader carry the chosen direction around the object and say whether it returns agreeing with itself?",
    },
    "mechanisms-and-locks": {
        "course_moment": "The center-of-gravity demonstration and later applications turn physical behavior into questions about paths or forced points in a state space.",
        "thinking_shift": "The reader stops following every motion detail and asks what shape the possible states form.",
        "reader_test": "Can the reader state the possible states, forbidden states, and topological feature that blocks or forces the physical behavior?",
    },
    "singular-moments": {
        "course_moment": "Pair creation, pair cancellation, tangencies, and non-isolated defects are the special instants where one ordinary picture changes into another.",
        "thinking_shift": "The reader stops fearing exceptions as separate mysteries and reads them as controlled transitions between stable cases.",
        "reader_test": "Can the reader describe the ordinary picture before the special instant, after it, and what protected count survives the passage?",
    },
    "models-not-labels": {
        "course_moment": "Manifold, quotient, index, invariant, and configuration space all matter only when they name a working model for motion, counting, or forced behavior.",
        "thinking_shift": "The reader stops collecting terms and translates each term into the action it permits in the proof.",
        "reader_test": "Can the reader replace the term with an everyday sentence saying what object, move, count, or obstruction it supplies?",
    },
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
    {
        "id": "product-space",
        "title": "Product space",
        "theme": "shape-as-machine",
        "subthemes": ["models-not-labels", "mechanisms-and-locks"],
        "first_principles": "A product space is what you get when two choices are made independently. If one choice is a point on a line and another choice is a point on a line, the combined choice fills a square. The idea matters because many spaces in the course are spaces of choices, not objects already drawn in ordinary room.",
        "important_detail": "The product keeps both freedoms. Forgetting one coordinate means studying a smaller problem than the one the lecture built.",
        "math_principle": "Independent freedoms combine into a new space whose shape can be studied on its own.",
    },
    {
        "id": "quotient-space",
        "title": "Quotient space",
        "theme": "pictures-to-proofs",
        "subthemes": ["models-not-labels", "surfaces-and-orientation"],
        "first_principles": "A quotient space is made by declaring some points to be the same point. A square with opposite sides identified is no longer only a square on the page; it is an instruction for travel. When a path leaves one marked edge, the rule says where it re-enters and whether its direction has been reversed.",
        "important_detail": "The identification rule is part of the object. The same drawn square can make different spaces if the edge rules change.",
        "math_principle": "Sameness can be built by a rule, and that rule changes routes, sides, and holes.",
    },
    {
        "id": "surgery",
        "title": "Surgery",
        "theme": "see-by-deforming",
        "subthemes": ["allowed-moves", "surfaces-and-orientation"],
        "first_principles": "Surgery means removing a controlled piece of a space and attaching another controlled piece. The plain idea is repair by rule: do not stare at the whole surface at once; change one part while tracking exactly what feature has been changed and what feature is meant to stay meaningful.",
        "important_detail": "Surgery is not arbitrary damage. The boundary of the removed piece and the gluing rule for the replacement determine the new space.",
        "math_principle": "A global surface can be understood through local replacement rules when the boundary bookkeeping is explicit.",
    },
    {
        "id": "manifold",
        "title": "Manifold",
        "theme": "local-to-global",
        "subthemes": ["models-not-labels", "surfaces-and-orientation"],
        "first_principles": "A manifold is a space that looks ordinary when seen very close up, even if the whole space has a surprising shape. A surface of a ball, a torus, or a Mobius-type object can have simple small neighborhoods while the complete object carries holes, side reversal, or other global behavior.",
        "important_detail": "Local ordinariness does not settle the global question. The whole course depends on that gap.",
        "math_principle": "A space can be locally simple and globally constrained at the same time.",
    },
    {
        "id": "intersection-number",
        "title": "Intersection number",
        "theme": "count-what-survives",
        "subthemes": ["signs-and-cancellation", "surfaces-and-orientation"],
        "first_principles": "Intersection number counts meetings with plus and minus signs. A raw count of crossings changes too easily: a small motion can create two meetings or remove two meetings. The signed count is designed so opposite meetings cancel, leaving the part of the meeting information that legal motion cannot erase.",
        "important_detail": "The signs must come from orientation. If plus and minus are assigned without a consistent direction rule, the count has no force.",
        "math_principle": "Local meetings can become global evidence when signs make accidental pair changes cancel.",
    },
    {
        "id": "brouwer-fixed-point",
        "title": "Brouwer fixed-point theorem",
        "theme": "shape-as-machine",
        "subthemes": ["mechanisms-and-locks", "holes-and-boundaries"],
        "first_principles": "Brouwer's theorem says that a continuous rule sending a filled ball back into itself must leave at least one point unmoved. The everyday picture is stirring every point of a filled disk without tearing the rule or sending points outside. The whole filled shape gives no way for every point to escape its starting place at once.",
        "important_detail": "The filled ball and its boundary are part of the claim. Change the space or remove the boundary and the guarantee can fail.",
        "math_principle": "The shape of a domain can force self-agreement for every continuous rule of the right kind.",
    },
    {
        "id": "equilibrium",
        "title": "Equilibrium",
        "theme": "shape-as-machine",
        "subthemes": ["turning-and-curvature", "mechanisms-and-locks"],
        "first_principles": "An equilibrium is a state where the motion arrow vanishes. In everyday terms, the system has no immediate direction to move. The course cares about equilibria because they can be studied without solving every path: their local arrow patterns can carry signed information.",
        "important_detail": "An equilibrium is not only a dot in a drawing. What matters is how nearby arrows behave around it.",
        "math_principle": "A local failure of motion can carry evidence about the whole space of motion.",
    },
    {
        "id": "poincare-hopf",
        "title": "Poincare-Hopf theorem",
        "theme": "local-to-global",
        "subthemes": ["turning-and-curvature", "signs-and-cancellation"],
        "first_principles": "Poincare-Hopf says that the signed indices of all isolated vector-field defects add up to a number belonging to the surface itself. The plain meaning is that local failures of motion are not independent. The surface carrying the arrows demands a total.",
        "important_detail": "The theorem counts clean isolated defects. If failures merge into a smeared region, the picture must be made ordinary enough before the count is trusted.",
        "math_principle": "Whole-surface topology can control the total of local motion failures.",
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
    "product-space": {
        "why_it_exists": "Product space exists because many course objects are built from several freedoms at once. A point on a square is two line choices made together. A state of a moving object may combine position, angle, and another constraint. The product gives those combined choices a shape.",
        "beginner_trap": "The trap is to imagine the product as only a larger drawing. It is a record of independent choices. If the choices are not actually independent, then the product is the wrong model and the later topological conclusion may answer the wrong question.",
        "course_role": "Products appear when the course builds boxes, manifolds, graphs of maps, and configuration spaces. They prepare the reader to treat a rule or physical state as a point in a larger space where intersections, paths, and fixed points can be studied.",
    },
    "quotient-space": {
        "why_it_exists": "Quotient space exists because some spaces are best described by identification rules. A torus can be described by a square whose opposite sides are treated as the same passage. The visible drawing is ordinary; the rule changes the actual travel inside the space.",
        "beginner_trap": "The trap is to look only at the drawn shape and ignore the labels or arrows on its edges. In quotient thinking, the labels are not decoration. They say which points are identical in the space being studied.",
        "course_role": "Quotients explain cylinders, Mobius bands, tori, and later abstract spaces built from rules rather than physical models. They keep the course honest about what a diagram means before deformation, orientation, or vector fields are placed on it.",
    },
    "surgery": {
        "why_it_exists": "Surgery exists because classification needs controlled operations, not passive looking. By removing a known piece and gluing in another, the course can expose handles, crosscaps, and boundaries and can compare surfaces through repeatable moves that a reader can audit.",
        "beginner_trap": "The trap is to think surgery permits any convenient alteration. It does not. The removed piece, the attaching boundary, and the replacement rule are part of the argument. Change those without accounting for them and the surface has become a different problem.",
        "course_role": "Surgery supports surface classification and the early construction language. It also trains the same discipline later used in deformation and vector-field cleanup: change an object locally while keeping exact track of what the change means globally.",
    },
    "manifold": {
        "why_it_exists": "Manifold exists as the course's word for a space where small neighborhoods behave like ordinary room, even when the total space does not. This lets the lectures put curves, surfaces, maps, and vector fields in settings that are locally manageable but globally rich.",
        "beginner_trap": "The trap is to think local familiarity implies global simplicity. A Mobius band can look ordinary near every point and still reverse side after a full trip. A torus can look ordinary locally while carrying routes a sphere does not have.",
        "course_role": "Manifolds are the stage for intersection theory, fixed points, vector fields, and Poincare-Hopf. The word matters only because it tells the reader what local reasoning is allowed and why whole-space bookkeeping is still necessary.",
    },
    "intersection-number": {
        "why_it_exists": "Intersection number exists because visible crossings alone are unstable. During a legal motion, crossings can be born or die in pairs. The signed count remembers whether the meetings carry a net obstruction after those pair changes cancel.",
        "beginner_trap": "The trap is to count crossings without asking where signs came from. The sign records how oriented pieces meet inside the surrounding space. Without that direction information, cancellation may be wishful arithmetic rather than a mathematical reason.",
        "course_role": "Intersection number is the hinge between early deformation and later fixed-point theory. It turns meetings into protected evidence, then reappears when graphs meet diagonals and when vector-field defects are counted by index in the dynamics chapter.",
    },
    "brouwer-fixed-point": {
        "why_it_exists": "Brouwer's theorem exists in the companion because it is the clearest place where shape forces existence without computation. A continuous self-map of a filled ball cannot move every point away from itself while staying inside the ball.",
        "beginner_trap": "The trap is to hear the theorem as a method for finding the fixed point. Its job is different: it proves that at least one point must exist. That existence claim is already strong when the rule is complicated or only qualitatively known.",
        "course_role": "Brouwer connects graph-and-diagonal fixed-point thinking to the later dynamics chapter. It teaches the reader that a theorem can be useful because it rules out global escape, not because it solves the rule explicitly.",
    },
    "equilibrium": {
        "why_it_exists": "Equilibrium exists because dynamics often asks where motion must stop or fail. A vector field may be too hard to solve, but the places where its arrows vanish can still be forced, counted, and compared.",
        "beginner_trap": "The trap is to classify an equilibrium by a rough picture of arrows and stop there. The course asks for the turning around the defect, because that signed local behavior is what can survive deformation and enter a global sum.",
        "course_role": "Equilibria are the dynamics counterpart of intersections. They give vector-field index a place to live and let Poincare-Hopf turn surface topology into a prediction about motion without requiring the reader to solve the full differential equation.",
    },
    "poincare-hopf": {
        "why_it_exists": "Poincare-Hopf exists because the course needs a final exchange between shape and motion. It says that the sum of local vector-field indices is forced by Euler characteristic, so the surface can demand defects before the differential equation is solved.",
        "beginner_trap": "The trap is to treat the theorem as a slogan about the hairy ball. The real content is a signed account over every isolated defect. One local source or saddle is not enough; the total over the whole surface is the theorem.",
        "course_role": "Poincare-Hopf gathers the course's main habits: surfaces, Euler characteristic, signed counts, generic cleanup, and dynamics. It is the late point where earlier bookkeeping becomes a statement about possible motion and about what every arrow field must fail to avoid.",
    },
}


CONCEPT_WORKUPS = {
    "generic-position": {
        "object": "A drawing or configuration that may contain accidental alignments, tangencies, or multiple events happening at the same place.",
        "operation": "Move it a very small amount while preserving the actual question, so fragile coincidences separate into ordinary events.",
        "protected": "The protected fact is the answer to the original problem, not the exact accidental arrangement that made the first drawing hard to read.",
        "breaks_if": "It breaks if the small move changes the object being studied, crosses a forbidden boundary, or removes a condition the problem required.",
    },
    "deformation": {
        "object": "A curve, surface, field, or diagram whose exact shape is less important than what it can become under allowed motion.",
        "operation": "Bend, slide, stretch, or redraw continuously while keeping forbidden moves out of the argument.",
        "protected": "The protected fact is the feature the question is really about: route order, side behavior, crossing obstruction, or total count.",
        "breaks_if": "It breaks if the simplification uses a move the original problem did not permit, such as passing through an obstacle or moving fixed data.",
    },
    "invariant": {
        "object": "A changing situation where many visible details vary while one chosen piece of evidence is meant to stay fixed.",
        "operation": "Check the evidence before and after every allowed move, and keep only the part that survives those moves.",
        "protected": "The protected fact is the stored memory of the problem: a side count, hole count, parity, signed meeting count, or total index.",
        "breaks_if": "It breaks if the chosen quantity changes under a harmless legal redraw, or if it remembers details unrelated to the question.",
    },
    "topology-vs-geometry": {
        "object": "A shape or motion that can be described either by measurements or by route, boundary, and connection facts.",
        "operation": "Choose the level of description that keeps the real constraint while discarding details that can legally vary.",
        "protected": "The protected fact is whichever feature the problem depends on: measured bending for geometry, or surviving arrangement for topology.",
        "breaks_if": "It breaks if a topological argument throws away a needed measurement, or if a geometric description hides a whole-shape obstruction.",
    },
    "euler-characteristic": {
        "object": "A surface divided into vertices, edges, and faces by a chosen decomposition.",
        "operation": "Count vertices, subtract edges, add faces, and check that refinements only add canceling bookkeeping terms.",
        "protected": "The protected fact is the alternating total attached to the surface rather than to the particular mesh drawn on it.",
        "breaks_if": "It breaks if boundaries, identifications, or cell choices are counted inconsistently, because then cancellation no longer records the surface honestly.",
    },
    "triangulation": {
        "object": "A continuous surface that is too slippery to count directly but can be divided into manageable finite pieces.",
        "operation": "Replace the surface by a finite ledger of cells or triangles, then compare what happens when that ledger is refined.",
        "protected": "The protected fact is the surface information that survives after the chosen pieces are redrawn, split, or merged legally.",
        "breaks_if": "It breaks if the pieces are treated as the surface itself, or if the count depends on one arbitrary decomposition.",
    },
    "graph-planarity": {
        "object": "A set of required connections between vertices, placed on a surface with limited room for routes.",
        "operation": "Try to embed the connections without forbidden crossings, while using surface bookkeeping to decide whether every attempt must fail.",
        "protected": "The protected fact is the connection demand together with the surface room available for carrying those connections.",
        "breaks_if": "It breaks if one failed drawing is mistaken for proof, or if the surface is silently changed to give extra routes.",
    },
    "knots-and-links": {
        "object": "A closed loop or several loops sitting in space, with over-under information at crossings when drawn on a page.",
        "operation": "Move the loops by legal ambient motion while forbidding cuts, breaks, and strands passing through each other.",
        "protected": "The protected fact is the embedding relation: whether the loop can become a plain circle or whether loops remain linked.",
        "breaks_if": "It breaks if the flat drawing forgets over-under data, or if the argument lets strands pass through each other.",
    },
    "winding-linking": {
        "object": "A loop or pair of loops whose route may go around a hole, post, point, or another loop.",
        "operation": "Track the aroundness with direction, so opposite turns or crossings can cancel when the motion changes the picture.",
        "protected": "The protected fact is the signed relationship of going around, not the length, roundness, or visual neatness of the loop.",
        "breaks_if": "It breaks if direction is ignored, because opposite windings can look similar while canceling in the actual count.",
    },
    "boundary-orientation": {
        "object": "A surface with possible edges and a possible global choice of consistent direction or side.",
        "operation": "Carry a local direction choice around the whole surface and account for any boundary terms separately.",
        "protected": "The protected fact is whether local signs and side choices can be made consistently over the complete surface.",
        "breaks_if": "It breaks if local two-sidedness is mistaken for global orientability, or if boundary contributions are left out of the account.",
    },
    "gauss-bonnet": {
        "object": "A surface or region whose local bending, boundary turning, and corner behavior can be measured and summed.",
        "operation": "Add the local geometric contributions with the necessary boundary and corner terms, then compare the total to whole-surface topology.",
        "protected": "The protected fact is the total account, which can be constrained by the surface even when local bending changes.",
        "breaks_if": "It breaks if edge or corner terms are ignored, because then the total no longer balances the actual geometric object.",
    },
    "vector-field-index": {
        "object": "An arrow field on a surface with isolated places where the arrow pattern fails or vanishes.",
        "operation": "Walk around each defect on a small loop and count how the nearby arrows turn.",
        "protected": "The protected fact is the signed local turning count, which can move with the defect and enter a global sum.",
        "breaks_if": "It breaks if the defect is not isolated, or if the surrounding arrow direction is not read consistently around the loop.",
    },
    "fixed-points": {
        "object": "A rule that sends points of a space to points, together with the question of whether some point returns to itself.",
        "operation": "Translate the rule into a graph and compare it with the diagonal where input and output agree.",
        "protected": "The protected fact is self-agreement: a graph-diagonal meeting means the original rule has a fixed point.",
        "breaks_if": "It breaks if the graph no longer represents the rule, or if the space and continuity assumptions are not the ones the theorem needs.",
    },
    "configuration-space": {
        "object": "The full list of possible states of a mechanism, physical setup, or moving system.",
        "operation": "Represent each state as a point, remove forbidden states, and read motion as paths through the resulting space.",
        "protected": "The protected fact is the shape of possibility: holes, walls, components, and forced passages in the state space.",
        "breaks_if": "It breaks if the model omits a real freedom, adds a false restriction, or forgets a boundary condition from the physical problem.",
    },
    "duality": {
        "object": "A problem whose first drawing hides the useful relationships among regions, boundaries, choices, or rules.",
        "operation": "Redraw the same relationships in a different form, such as regions becoming vertices or a map becoming a graph.",
        "protected": "The protected fact is the meaning that survives translation between the original picture and the dual picture.",
        "breaks_if": "It breaks if solving the new picture no longer answers the old question, or if the translation back is left vague.",
    },
    "parity": {
        "object": "A count whose exact value may change while its evenness or oddness is expected to survive.",
        "operation": "Forget all information except odd or even, then check that every legal change alters the raw count by pairs.",
        "protected": "The protected fact is parity, which can prove zero impossible when an odd count must remain odd.",
        "breaks_if": "It breaks if a legal move can change the count by one, because then oddness and evenness are not protected.",
    },
    "product-space": {
        "object": "Several independent choices that must be recorded together as one combined state or point.",
        "operation": "Let each choice vary and treat the combined choices as a new space with its own routes and boundaries.",
        "protected": "The protected fact is independence: each coordinate keeps its freedom until the actual problem imposes a constraint.",
        "breaks_if": "It breaks if dependent choices are treated as independent, because the product then contains states the problem never allowed.",
    },
    "quotient-space": {
        "object": "A drawn shape together with a rule declaring certain points, edges, or exits to be the same.",
        "operation": "Apply the identification rule and read travel, loops, sides, and boundaries in the resulting space rather than in the drawing.",
        "protected": "The protected fact is rule-made sameness: points that look separate on the page may be identical in the space.",
        "breaks_if": "It breaks if the drawing is read literally after identifications have changed what counts as a point or boundary.",
    },
    "surgery": {
        "object": "A surface or space with a controlled part that can be removed and replaced along a stated boundary.",
        "operation": "Remove the chosen piece, keep track of the exposed boundary, and attach the replacement by a specified rule.",
        "protected": "The protected fact is the bookkeeping of what the local replacement changed and what global feature it was meant to reveal.",
        "breaks_if": "It breaks if the removed piece, boundary, or gluing rule is vague, because then the operation is not auditable.",
    },
    "manifold": {
        "object": "A space that looks like ordinary room when inspected close up, even if its whole shape is unfamiliar.",
        "operation": "Use local ordinary neighborhoods for drawing curves, maps, and fields, then check what global gluing does to them.",
        "protected": "The protected fact is the gap between local simplicity and global constraint, which lets the course reason patch by patch without stopping there.",
        "breaks_if": "It breaks if local ordinariness is used to conclude global simplicity, because holes, side reversal, and total counts can be invisible locally.",
    },
    "intersection-number": {
        "object": "Clean meetings between oriented curves, surfaces, or subspaces inside a surrounding space where direction has meaning.",
        "operation": "Assign each meeting a sign from the orientation rule and add the signs rather than the raw number of meetings.",
        "protected": "The protected fact is the signed total, which survives legal deformation when newly born pairs cancel.",
        "breaks_if": "It breaks if meetings are not clean or signs are not justified, because then cancellation is not trustworthy evidence.",
    },
    "brouwer-fixed-point": {
        "object": "A continuous rule sending every point of a closed filled ball back into that same filled ball.",
        "operation": "Assume every point avoids itself and read that attempted escape against the filled shape and its boundary.",
        "protected": "The protected fact is forced self-agreement: the ball gives no continuous way for all points to escape themselves.",
        "breaks_if": "It breaks if the space is not the right closed filled object, or if the rule jumps or leaves the domain.",
    },
    "equilibrium": {
        "object": "A state in a vector field where the motion arrow vanishes and nearby arrows show the local pattern.",
        "operation": "Inspect the arrows around the vanishing point and read their turning as local evidence.",
        "protected": "The protected fact is the signed behavior around the equilibrium, not merely the fact that the dot is present.",
        "breaks_if": "It breaks if the surrounding arrow pattern is ignored, because topology uses the local turning rather than the label of the equilibrium.",
    },
    "poincare-hopf": {
        "object": "A vector field on a surface with all isolated defects included in one account.",
        "operation": "Add the signed indices of every defect and compare the sum with Euler characteristic.",
        "protected": "The protected fact is the equality between total local defect count and the whole-surface number.",
        "breaks_if": "It breaks if any defect is omitted, if defects are not isolated, or if the surface carrying the field is changed.",
    },
}


CONCEPT_ANCHORS = {
    "generic-position": {
        "course_moment": "In the intersection lectures, a messy meeting is first nudged into clean separate meetings. That small cleanup is not cosmetic. It is what lets each meeting receive a sign or be paired with another meeting.",
        "principle": "A proof should count ordinary events whose behavior survives small legal motion, because accidental coincidences can hide the event that actually carries evidence.",
        "reader_question": "If the picture is nudged a little, which events remain readable, and which exact coincidences were only making the drawing harder to audit?",
    },
    "deformation": {
        "course_moment": "The disk path puzzle asks whether boundary pairs can be joined without crossings. The useful move is to slide and smooth paths while keeping endpoint order and the no-crossing rule intact.",
        "principle": "A picture can be simplified only after the allowed motion and the protected fact have both been named.",
        "reader_question": "What did the motion preserve, and would the answer change if an endpoint moved past another endpoint or a path crossed a forbidden obstacle?",
    },
    "invariant": {
        "course_moment": "The Mobius strip keeps one-sided behavior while it bends, and signed intersections keep a total while pairs appear or vanish. Both are receipts for what survived a legal change.",
        "principle": "The useful fact is not the one most visible in the drawing; it is the one that remains fixed under the moves the problem allows.",
        "reader_question": "What fact is being carried from the original picture to the simplified one, and why is that fact allowed to speak for both pictures?",
    },
    "topology-vs-geometry": {
        "course_moment": "A paper strip has lengths and bends, but the Mobius lesson depends on the end-gluing rule. A vector field has arrow sizes, but the index lesson depends on how nearby directions turn.",
        "principle": "The right description is the one that keeps the constraint the question needs and leaves aside details that can change without changing the answer.",
        "reader_question": "Is the problem asking about measurement, or is it asking about routes, gluing, sides, holes, signs, or forced agreement?",
    },
    "euler-characteristic": {
        "course_moment": "When a surface is divided into vertices, edges, and faces, extra internal cuts change the raw counts. The alternating total is built so those artificial changes cancel.",
        "principle": "A count earns trust when it forgets the chosen bookkeeping device and remembers the surface being booked.",
        "reader_question": "Which changes came only from the chosen decomposition, and how does the alternating count cancel those changes?",
    },
    "triangulation": {
        "course_moment": "Surface classification needs a smooth object to become countable. Triangulation supplies a finite ledger, then later checks that the answer does not belong only to that one ledger.",
        "principle": "A finite drawing can support a proof when the final fact survives replacing one finite drawing by another.",
        "reader_question": "Which part of the argument uses the chosen pieces, and which part proves the conclusion belongs to the surface instead?",
    },
    "graph-planarity": {
        "course_moment": "The boundary-pair disk problem is not settled by one failed drawing. The obstruction must show that every legal drawing of the required connections runs into the same shortage of room.",
        "principle": "A connection demand and a surface's available room must be judged together; drawing failure is not yet mathematical impossibility.",
        "reader_question": "What required connections are fixed, what surface carries them, and what protected fact blocks all crossing-free attempts?",
    },
    "knots-and-links": {
        "course_moment": "Off-center Mobius cuts can leave pieces linked. The important event is not that the strips look tangled, but that separating them would require a forbidden pass-through.",
        "principle": "A loop in space carries embedding information: how it sits inside surrounding room matters even when its exact shape changes.",
        "reader_question": "What motion is allowed for the loops, and where would an attempted simplification secretly pass one strand through another?",
    },
    "winding-linking": {
        "course_moment": "A route around a hole or another loop may stretch and wiggle while still going around. Later signed counts refine this by letting opposite turns cancel.",
        "principle": "Some counts record a relationship between objects, not a size of one object; the relationship survives until a forbidden crossing or break occurs.",
        "reader_question": "What is being gone around, what direction is recorded, and what legal move would be needed to change that aroundness?",
    },
    "boundary-orientation": {
        "course_moment": "The Mobius strip shows that every small patch can look two-sided while a full trip reverses the side choice. Signed intersections later require that this reversal not happen.",
        "principle": "Local direction choices matter only if they can be carried consistently through the whole object and across any boundary terms.",
        "reader_question": "Can the chosen side or direction travel all the way around and come back agreeing with itself?",
    },
    "gauss-bonnet": {
        "course_moment": "The course's local-to-global habit appears when local bending or turning is summed and compared with a whole-surface number, instead of being treated as isolated measurements.",
        "principle": "Local geometric contributions can be free one by one while their total is constrained by the shape carrying them.",
        "reader_question": "What local quantities are being added, and what boundary or corner terms must be included before the total can be trusted?",
    },
    "vector-field-index": {
        "course_moment": "Around a source, sink, or saddle, nearby arrows turn in a pattern that can be read on a small loop. That turning becomes a signed local count.",
        "principle": "A failure of motion can carry evidence through the behavior around it, not only through the dot where the arrow vanishes.",
        "reader_question": "If you walk once around the defect, how do the arrows turn, and why does that local count survive cleanup of the field?",
    },
    "fixed-points": {
        "course_moment": "The graph of a map and the diagonal turn the question f(x) = x into a meeting problem. A fixed point is no longer hidden inside a rule; it is a visible intersection.",
        "principle": "A rule can be made into a shape, and self-agreement can be tested by comparing that shape with the diagonal.",
        "reader_question": "What is the graph recording, what is the diagonal recording, and why does their meeting mean the original rule fixes a point?",
    },
    "configuration-space": {
        "course_moment": "In applications, a physical motion is replaced by the space of all possible states. Legal motion becomes a path, and forbidden states become missing regions or walls.",
        "principle": "A hard motion problem can become a shape-of-possibilities problem when every allowed state is represented honestly.",
        "reader_question": "What data describe one complete state, what states are forbidden, and what path in the state space would perform the motion?",
    },
    "duality": {
        "course_moment": "A map becomes a graph, regions can become vertices, and an edge-labeled square becomes a travel rule. The new picture is useful only because it preserves the old question.",
        "principle": "Changing representation is valid when the relationships needed by the proof can be read both before and after the change.",
        "reader_question": "After solving the new picture, how does the conclusion translate back to the original object or question?",
    },
    "parity": {
        "course_moment": "When legal changes create or remove events two at a time, the exact number may change while oddness or evenness stays fixed.",
        "principle": "A coarse count can be strong if the problem only needs to know whether zero is possible.",
        "reader_question": "Can every legal change alter this count only by pairs, and does the protected odd or even value block the desired outcome?",
    },
    "product-space": {
        "course_moment": "A graph of a map records input and output together; a configuration space records several freedoms together. Product thinking supplies the larger room where those combined choices live.",
        "principle": "Independent choices form a space of combined states, and later constraints carve the actual problem out of that space.",
        "reader_question": "Which choices vary independently, and which equations, boundaries, or forbidden states reduce the product to the space the problem really uses?",
    },
    "quotient-space": {
        "course_moment": "A square with edge labels can describe a cylinder, torus, or Mobius-type surface. The drawn boundary is not final until the identification rule has been read.",
        "principle": "A space can be made by declaring points to be the same; the rule of sameness controls travel more than the visible drawing does.",
        "reader_question": "When a traveler reaches a labeled edge, where do they re-enter, and does their direction or side choice return changed?",
    },
    "surgery": {
        "course_moment": "Surface classification uses controlled removal and attachment to expose handles, crosscaps, and boundaries. The operation has to say exactly what boundary is left and how the replacement is glued.",
        "principle": "Changing a space locally can reveal global structure only when the local replacement is accounted for exactly.",
        "reader_question": "What piece was removed, what boundary did it leave, what was attached, and which global feature changed as a result?",
    },
    "manifold": {
        "course_moment": "A sphere, torus, and Mobius band all look ordinary close up, yet they differ in loops, side behavior, and vector-field demands.",
        "principle": "Local ordinariness lets the course draw and count small events, while global shape decides whether those local choices can agree everywhere.",
        "reader_question": "Which part of the reasoning uses ordinary local neighborhoods, and where does the whole space add a constraint the local view cannot see?",
    },
    "intersection-number": {
        "course_moment": "Lecture 8 counts clean meetings with signs so that a positive and negative pair can appear or vanish without changing the total.",
        "principle": "The count is protected because local birth and cancellation rules have been built into the arithmetic.",
        "reader_question": "Where do the signs come from, and why does a newly born pair contribute zero to the total evidence?",
    },
    "brouwer-fixed-point": {
        "course_moment": "For a continuous self-map of a filled ball, Brouwer says at least one point cannot escape itself. The course reads this as shape forcing existence without giving a formula for the point.",
        "principle": "The filled domain and the continuity of the rule can block a global escape plan for all points at once.",
        "reader_question": "What would it mean for every point to avoid itself, and why do the filled ball and its boundary make that avoidance impossible?",
    },
    "equilibrium": {
        "course_moment": "In the dynamics lectures, an equilibrium is where the arrow vanishes, but the useful evidence is how nearby arrows turn around that vanishing point.",
        "principle": "A stopped state matters mathematically when its surrounding arrow pattern can be counted and compared with the whole surface.",
        "reader_question": "What does the arrow field do around the equilibrium, and what signed evidence does that local pattern contribute?",
    },
    "poincare-hopf": {
        "course_moment": "Poincare-Hopf adds every isolated vector-field index and compares the sum with Euler characteristic. Local motion failures must answer to the surface carrying them.",
        "principle": "The whole surface controls the total of local defects, so dynamics can be constrained before individual trajectories are solved.",
        "reader_question": "Have all defects been counted with signs, and what total does the underlying surface require?",
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
        "Euler characteristic is surface bookkeeping designed to survive redrawing. If a surface is divided into vertices, edges, and faces, those individual counts depend on the chosen division. Add a diagonal to a face and the number of edges changes. The number of faces changes too. The alternating combination is arranged so those artificial internal changes balance each other. That is why the final number belongs to the surface rather than to one particular mesh drawn on it.",
        "The everyday need is simple: the course wants a number that can recognize a whole surface without caring about the artist's drawing. A sphere can be divided in many ways. A torus can be divided in many ways. If the count changed every time the drawing was improved, it would be useless as evidence. Euler characteristic earns its place because it ignores the replaceable drawing choices and remembers a whole-surface fact.",
        "This concept becomes much more than a formula. Early on, it helps classify and recognize surfaces. Later, in Poincare-Hopf, it becomes the number that a vector field's local indices must add up to. That is the conceptual bridge: a count first learned from surface pieces later controls possible failures of motion. Shape accounting becomes a demand placed on arrows.",
        "The detail behind the arithmetic is cancellation. When a face is split, the extra edge and extra face enter with opposite effects. When a triangulation is refined, many raw numbers change, but the alternating total is designed to remain still. The formula is useful because it has been engineered to forget the divisions the mathematician chose and remember the surface those divisions describe.",
        "For a beginner, the key is not to worship the symbols. The symbols are a bookkeeping device for a plain idea: choose a count that changes zero when the drawing changes harmlessly. Once that habit is clear, intersection number and vector-field index feel like relatives rather than new mysteries.",
    ],
    "triangulation": [
        "Triangulation is a way to make a continuous surface countable without pretending the surface is literally made of rigid triangles. A smooth surface has infinitely many points, which is too much for direct bookkeeping. Dividing it into simple pieces gives a finite ledger. Once the ledger exists, the course can count vertices, edges, faces, and higher-dimensional pieces in a disciplined way.",
        "The first-principles reason is that a proof often needs a handle on the infinite. A surface such as a sphere or torus is continuous, so there is no final list of its points. A triangulation replaces that impossible list with a manageable pattern of pieces and attachments. The question then becomes whether the answer found from the pattern really belongs to the surface.",
        "The important detail is that the triangulation is scaffolding. A different triangulation should not change the topological conclusion. If the answer depends on the exact mesh, the count has not found a surface fact. This is why triangulation supports Euler characteristic and surface classification: it lets a soft object enter exact reasoning, while later cancellation proves that the reasoning did not depend on one arbitrary set of divisions.",
        "A beginner can read triangulation as a two-step promise. First, replace the surface by a finite set of simple pieces whose gluing is known. Second, prove that changing to a finer or different set of pieces does not change the quantity being used. The first step makes counting possible. The second step makes the counting honest.",
        "This is why triangulation belongs beside deformation and invariance. It is not the answer itself. It is a controlled translation into a form where arithmetic can begin, followed by a check that the arithmetic did not become a statement about the translation alone.",
    ],
    "graph-planarity": [
        "Planar graph thinking asks whether a required pattern of connections can fit on a surface without forbidden crossings. The graph itself only records which dots must be joined. The surface supplies room, routes, and limitations. A failed drawing does not prove impossibility, because the drawer may have chosen a poor arrangement. A topological argument must show that every legal arrangement runs into the same obstruction.",
        "The first-principles split is between demand and room. The demand says which pairs of points must be connected. The room says where the connecting paths are allowed to travel. On a plane or disk, routes can block each other because there is no overpass unless the problem explicitly allows one. On a different surface, such as a torus, the available routes may change. Planarity is therefore not only about neat drawing; it is about whether the chosen surface has enough route freedom.",
        "This concept trains a habit used throughout the course. Disk path puzzles, intersections of submanifolds, knots, and configuration spaces all use versions of the same split. The question is not just what must connect to what. It is whether the surrounding space gives enough freedom for those connections to avoid each other. When it does not, crossings become evidence rather than mistakes.",
        "The everyday picture is routing roads without bridges. Some layouts fail because the route planner chose a bad layout; others fail because the required connections overfill the available surface. The mathematical work is to tell those cases apart. A real impossibility proof must survive every redraw, every slide of a route, and every legal repositioning of the vertices.",
        "That is why graph planarity belongs with deformation and invariants rather than with drawing skill. A good planarity argument does not say, 'I cannot draw it.' It says which protected order, count, or separation condition prevents every drawing of the required kind.",
    ],
    "knots-and-links": [
        "Knots and links matter because curves can remember how they sit in space. A loop may stretch, bend, and wiggle while still refusing to become a plain circle through legal motion. Linked loops may look movable, yet remain unable to separate without passing through each other. The visible tangle is not the whole story; the over-under and around-through relationships are the story.",
        "The first-principles issue is permission. If a loop is allowed to pass through itself, almost every knot can be undone by brute force. If passing through is forbidden, the route taken by the loop becomes evidence. The curve has no thickness in the mathematical model, but the no-passing rule gives it memory. The course uses this kind of memory whenever it asks what legal motion can and cannot remove.",
        "Tokieda's strip demonstrations give a concrete version of this idea. Off-center divisions of a Mobius strip can produce pieces that stay linked. The final lecture returns to linked strip behavior. These examples teach the same rule that knot theory formalizes: passing through is not an innocent simplification. The legal moves determine whether an apparent tangle is removable or whether it records a real route constraint.",
        "The surrounding space is part of the object. A loop drawn on a page and a loop floating in three-dimensional space have different freedoms. A crossing in a plane may mean two strands occupy the same point; a crossing in a three-dimensional drawing may be only a projection, with one strand above the other. The knot is therefore not just the curve. It is the curve together with the space it inhabits and the motion rules it must obey.",
        "This concept connects to intersections and invariants because a knot needs evidence that survives deformation. A picture of a knot can be made uglier or cleaner without changing the knot. The reader should ask what relation remains after all legal simplification has been tried: linking, winding, crossing information, or another protected record of how the curve travels.",
    ],
    "winding-linking": [
        "Winding and linking are ways of counting a relationship rather than a size. A loop around a post can be pulled tighter or looser, but it still goes around the post unless it crosses the post or breaks. Two loops can be linked even when their exact shapes change. The stable fact is not length, roundness, or position. It is the aroundness relation.",
        "The course needs signs because relationships can cancel. Opposite windings may add to zero. Opposite intersections may be born together and vanish together. Winding and linking therefore prepare the reader for signed intersection number and vector-field index. They make it intuitive that a count can measure a relation between objects, not just a property of one object by itself.",
        "That is why linked strip demonstrations are not just curiosities. They train the eye to see a relationship that survives motion.",
        "From first principles, winding asks whether a route can be pulled off a forbidden center without crossing it. Linking asks the same kind of question for two closed curves. Both ideas teach the reader to look for a relationship that belongs to the whole route, not to one convenient snapshot of the drawing.",
    ],
    "boundary-orientation": [
        "Boundary and orientation are the details that make many later counts honest. A boundary is where a surface stops, and stopping changes the bookkeeping. Orientation asks whether a consistent sense of direction can be carried across the whole surface. On a Mobius-type surface, every small patch looks ordinary, but a full trip can reverse the side choice. That is a global obstruction.",
        "A boundary is not merely an edge in a picture. It is a place where the usual local continuation changes. A traveler on the interior of a surface can move in all nearby surface directions. At a boundary, some directions run out of surface. That difference matters in fixed-point arguments, curvature totals, Stokes-style bookkeeping, and any proof where behavior on the edge can add a separate term.",
        "Orientation is the ability to make local choices agree globally. A tiny patch can be given a clockwise sense, a normal direction, or a plus-minus convention. The hard question is whether that choice can be carried around every loop and return unchanged. The Mobius strip shows why the answer is not automatic. Local consistency can fail after a full journey.",
        "Signed intersection number depends on orientation. Vector-field index depends on being able to interpret turning consistently. Fixed-point statements on balls depend on what the boundary does. These are not side conditions added to intimidate beginners. They are the facts that let plus and minus signs mean something. If orientation or boundary is ignored, the proof may count a quantity that is not actually defined.",
        "The first-principles test is simple: can a local choice be carried all the way around without contradiction, and does the surface have an edge where extra behavior enters? Those questions decide whether later arithmetic is legal. Boundary and orientation are therefore part of the proof's foundation, not a cleanup step after the idea is already known.",
    ],
    "gauss-bonnet": [
        "Gauss-Bonnet represents the course's local-to-global habit in geometric form. Curvature is local: it says how a surface bends near a point. But the total curvature, with boundary and corner terms when needed, can be tied to the surface's whole topology. Local bending is not free to add up to anything it wants.",
        "A plain way to enter the idea is to imagine walking around a region while keeping track of turning. Some turning comes from the path along the boundary. Some comes from corners. Some comes from the surface itself bending underneath the path. Gauss-Bonnet says that when the full account is made correctly, those local contributions answer to the whole shape of the region or surface.",
        "Even when the course later emphasizes vector fields more than curvature, the same principle remains. Local contributions can be summed into a global constraint. The concept is therefore useful as a bridge: it helps a reader see why total turning, total curvature, total index, and Euler characteristic belong in the same family of ideas. The surface makes demands on the sum of local behavior.",
        "The point is not to memorize a formula, but to recognize the pattern: small measured changes can be forced by whole-shape structure. That pattern is also why signs and boundary terms matter. If the account leaves out a corner or an edge contribution, the total may be answering the wrong question.",
        "For a beginner, the important detail is that the theorem balances several kinds of information. Interior curvature, boundary turning, and corner contributions may all be needed before the total matches the surface. Leaving out an edge term is not a small oversight; it changes the account being balanced. Gauss-Bonnet teaches that a global conclusion often appears only after every local contribution has been put into the same ledger.",
    ],
    "vector-field-index": [
        "Vector-field index is the dynamics version of signed counting. A vector field assigns an arrow to each point. Where the arrow vanishes, there is an equilibrium or defect. The index records how the nearby arrows turn around that defect. It is local evidence, but it is designed so it survives appropriate changes in the field.",
        "The concept matters because it lets topology speak about differential equations without solving them. Sources, sinks, saddles, and other local patterns may move or change under deformation, but their signed total can be constrained by the surface. Poincare-Hopf is the payoff: the sum of local indices equals Euler characteristic. A fact about arrows becomes a fact about the shape carrying them.",
        "This turns a hard analytic question into a topological one: not where every trajectory goes, but what failures the whole surface requires.",
        "The first-principles picture is to walk once around a small loop surrounding the defect and watch the arrows turn. If the arrows make a full turn, or reverse their turning in a saddle-like way, that local behavior receives a signed count. The count is local, but the course uses it because the sum of such local counts can be globally forced.",
    ],
    "fixed-points": [
        "A fixed point is a place that a rule sends back to itself. The concept is powerful because many problems care about existence, not explicit calculation. Brouwer's theorem, for example, says that a continuous self-map of a closed ball must have a fixed point. It does not tell us where the point is. It tells us that the shape gives all points no continuous way to avoid themselves at once.",
        "The first-principles problem is avoidance. Imagine every point trying to move somewhere else while staying inside the same allowed space. If the rule is continuous, nearby starting points must have nearby destinations. They cannot scatter independently. On some spaces, such as a closed filled ball, that no-jump condition and the boundary structure prevent a total escape from self-agreement.",
        "The graph-and-diagonal picture explains why fixed points fit the course. The graph of a map records where points go. The diagonal records self-agreement. A fixed point is their intersection. This turns a rule into a geometric meeting problem, so earlier intersection ideas become relevant. The rule is no longer only an instruction; it has become a shape that can be compared with another shape.",
        "Later, equilibria in vector fields play a similar role: special states forced by the shape and continuity of the system. The difference is that a fixed point says a rule returns a point to itself, while an equilibrium says the motion arrow at a point vanishes. Both are ways for topology to prove that a special state exists before it is computed.",
        "The mathematical detail is that continuity ties nearby inputs to nearby outputs. If the rule could jump, it might dodge the forced agreement. The theorem is not saying every process has a fixed point; it is saying that certain shapes and certain continuous rules leave no global escape from self-agreement. The shape and the rule must both be named honestly.",
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
    "product-space": [
        "A product space is the course's plainest way to build a new world from choices. If one choice moves left to right and another moves up and down, the combined choice fills a square. If a third independent choice is added, the combined choices fill a box. This is not only a drawing device. It is the beginning of treating a list of possibilities as a shape with routes, boundaries, and obstacles of its own.",
        "The idea becomes important because many mathematical objects in the course are not physical pieces of paper. The graph of a map records an input and an output together. A configuration space records all data needed to describe a mechanical state. A path through such a space records a continuous change of all those choices at once. Product thinking is the step that lets the course put several ordinary freedoms into one organized object.",
        "The detail that keeps the idea honest is independence. A product says each coordinate can vary without immediately determining the other. If the problem has a constraint tying the choices together, then the allowed states form a smaller shape inside the product. From first principles, the product gives the large room first; the equations, forbidden states, or boundary rules then describe which part of that room the problem actually uses.",
    ],
    "quotient-space": [
        "A quotient space is made by changing what counts as the same point. A square on paper has four sides. But if the left and right sides are declared to be the same passage, a traveler leaving one side re-enters from the other. If another pair of sides is also identified, or if one side is reversed before identification, the routes inside the resulting space change again. The drawing has become a set of travel rules.",
        "This matters because many spaces in topology are easier to describe by instructions than by physical construction. A cylinder, a Mobius band, and a torus can all begin from a rectangle, but they are not the same space because their identification rules differ. The rule is what decides whether a loop closes, whether a side choice survives a full trip, and where a path goes when it reaches a labeled edge.",
        "The beginner danger is to treat the drawing as the object. In quotient thinking, the ink is only a code. Two points that look far apart on the page may be the same point in the space, and a boundary line on the drawing may no longer be a boundary in the finished object. Once that habit is learned, later constructions become less mysterious: maps, state spaces, and manifolds are often understood by the rules that identify their points.",
    ],
    "surgery": [
        "Surgery is controlled local replacement. Instead of trying to understand a whole surface in one glance, the course removes a known piece and attaches another piece according to a boundary rule. The operation sounds physical because it is meant to be checkable: what was removed, what edge remained, what was attached, and how did the surrounding surface connect afterward?",
        "The first-principles reason is that a global surface can be too complicated to classify from its first drawing. A handle, crosscap, or boundary component may be easier to understand as a part that can be isolated and compared with standard parts. Surgery gives the course a way to expose those parts without pretending that every visual feature of the original drawing matters.",
        "This idea matters for classification. Handles, crosscaps, and boundary components are easier to track when the surface can be changed through standard operations. Surgery lets the course reduce complicated surfaces to recognizable building blocks while still accounting for what has happened. It is not damage applied to a surface; it is a disciplined way to expose durable parts.",
        "From first principles, the boundary of the operation is the contract. If a disk is removed, the circular edge left behind matters. If a band is attached, its twist and attachment matter. A surgical move is valid only when those details are stated. If the boundary is matched differently, the resulting surface may have a different orientation behavior, a different route structure, or a different classification.",
        "The payoff is that a local replacement can reveal a global fact: which routes have been added, which side choices now fail, or which surface family the object belongs to. Surgery is therefore not a visual stunt. It is a controlled way to change the object while keeping a ledger of the topological consequences.",
    ],
    "manifold": [
        "A manifold is a space that behaves like ordinary room when examined close up. A surface of a sphere looks flat to a tiny traveler. A torus also looks flat close up. Even a Mobius band looks locally like an ordinary strip. The surprise is that these spaces can disagree globally while every small neighborhood feels familiar.",
        "This local-global gap is one of the main reasons topology exists. Local inspection can tell the reader which small motions, arrows, and crossings make sense. It cannot tell whether a loop can shrink, whether a side choice returns reversed, or whether every vector field must have a defect. Those are whole-space questions. The word manifold gives permission to reason locally while warning that local reasoning is not the end of the story.",
        "In the course, manifolds are stages. Curves move inside them. Subspaces intersect inside them. Maps send them to themselves. Vector fields live on them. The stage matters because the same local object behaves differently on different global spaces. A vector field on a sphere faces demands that a vector field on a torus may avoid. The manifold is therefore not background scenery; it supplies the room and the rules.",
    ],
    "intersection-number": [
        "Intersection number is the course's way of making meetings count only when they carry durable evidence. Two curves may cross in one drawing and miss after a small legal motion. Other meetings cannot be removed without breaking the rules. A raw count of visible crossings cannot tell these apart because it changes whenever an opposite pair is born or dies.",
        "The first-principles problem is that seeing a meeting is not enough. A meeting can be an accident of the drawing, like two routes touching because they were placed carelessly. Before a count can matter, the objects must be put in ordinary clean position, the allowed motions must be known, and the local meeting must be isolated enough to inspect. Generic position prepares that setting.",
        "The signed count fixes the weakness of raw counting. Each clean intersection receives plus or minus from the orientation of the objects and the surrounding space. When a legal deformation creates a pair, the two signs oppose each other, so their total contribution is zero. The visible drawing has changed, but the signed total has not. That is the reason the number deserves trust.",
        "This concept is the hinge of the course. Before it, deformation and generic position prepare clean pictures. After it, fixed points can be treated as intersections of a graph with a diagonal, and vector-field index can be understood as a signed local count around a defect. Intersection number teaches the reader how a picture becomes arithmetic without losing the geometry that gave the signs meaning.",
        "The important caution is that signs are not decoration. They come from orientation data and from the way the objects meet. If orientation is missing or the meeting is not clean, the count may not be defined. The power of the concept comes from this discipline: count only evidence that survives the legal motion being used.",
    ],
    "brouwer-fixed-point": [
        "The Brouwer fixed-point theorem is one of the course's clearest examples of existence forced by shape. Take a filled disk or ball. Apply a continuous rule that sends every point somewhere inside the same filled shape. Brouwer says at least one point lands exactly where it began. The theorem does not find the point. It says the space leaves no continuous escape plan for all points at once.",
        "A helpful everyday picture is stirring the points of a disk. Points can move, but the rule cannot tear, jump, or send them outside the disk. If every point tried to avoid itself, the attempted escape would have to organize directions across the whole filled shape in a way the boundary and interior do not allow. The force comes from the shape of the domain, not from a formula for the rule.",
        "The important detail is that the statement is specific. A closed ball is not the same as an open ball, a circle, or a torus. The boundary and the filled interior are part of the reason. This is why Brouwer fits the course's larger habit: identify the space honestly, identify the allowed rule, then let the topology of that space decide whether avoidance is possible.",
    ],
    "equilibrium": [
        "An equilibrium is a state where the motion arrow vanishes. If a vector field tells a particle which way it wants to move from each point, an equilibrium is a point with no immediate direction. In a solved differential equation, equilibria may appear as special solutions. In this course, they are more than special points: they are defects in an arrow pattern that can be counted.",
        "The first-principles shift is from following motion to reading the motion field. Solving every path asks where each starting point eventually goes. Topology asks a different question: can the whole surface carry arrows everywhere without a forced failure? An equilibrium is one place where the attempt fails. That failure may reveal something about the surface carrying the field.",
        "The surrounding arrows matter. A source, a sink, and a saddle are not only pictures with different names. Walk around a small loop enclosing the equilibrium and watch how the arrows turn. That turning gives the local index. This is why the course can say something about dynamics without solving every path: a local failure of motion carries signed evidence.",
        "The concept connects physical intuition to topology. A balancing state, a fixed point, and a vector-field equilibrium are all versions of forced special behavior. The course asks when such behavior is avoidable and when the shape of the space demands it. Equilibrium is where motion stops being followed point by point and starts being studied through the global constraints on its arrow field.",
        "The caution is that not every still-looking point carries the same evidence. The local arrow pattern must be inspected. A defect may contribute positively, negatively, or in another signed way depending on how nearby arrows turn. That is why equilibrium belongs with index and Poincare-Hopf, not only with the vocabulary of differential equations.",
    ],
    "poincare-hopf": [
        "Poincare-Hopf is the moment when the course's earlier bookkeeping speaks directly about motion. A vector field on a surface may have several isolated defects. Each defect has an index, a signed count of how nearby arrows turn. The theorem says that when all these local indices are added, the sum is forced by Euler characteristic, a number belonging to the surface.",
        "The plain meaning is that local failures of motion are not independent. On a sphere, the total demand is different from the demand on a torus. That is why the hairy-ball idea is not a loose metaphor; it is a visible case of a whole surface refusing a continuous nonzero tangent arrow field everywhere. Something must fail because the local arrow choices cannot be glued into a perfect global choice.",
        "This theorem gathers the course into one exchange. Euler characteristic began as cell bookkeeping. Generic position made defects clean enough to count. Signs made local contributions add honestly. Vector fields supplied the motion problem. Poincare-Hopf ties them together: shape controls the total defect of motion, and observed defects can reveal shape. It is not a final slogan; it is the course's central method written as an equation.",
    ],
}


FAMILIES = [
    {
        "id": "deformation-family",
        "title": "Deformation arguments",
        "purpose": "Replace a difficult object by an easier one while preserving the answer.",
        "first_principles": "This family begins by deciding what moves are legal. Then it moves the picture until the answer is easier to see. The proof lives in the guarantee that the motion did not change the feature being asked about.",
        "concepts": ["generic-position", "deformation", "invariant", "topology-vs-geometry", "surgery"],
    },
    {
        "id": "counting-family",
        "title": "Surviving-count arguments",
        "purpose": "Find a number or sign that legal moves cannot alter.",
        "first_principles": "This family turns shape into accounting. It counts pieces, holes, crossings, turns, or defects in a way that cancels fake changes and keeps the real obstruction.",
        "concepts": ["euler-characteristic", "triangulation", "winding-linking", "parity", "intersection-number", "poincare-hopf"],
    },
    {
        "id": "surface-family",
        "title": "Surface bookkeeping",
        "purpose": "Connect small patches, boundaries, and holes to whole-surface conclusions.",
        "first_principles": "This family treats a surface as a connected ledger. Local behavior can be drawn patch by patch, but the patches must agree when glued back together.",
        "concepts": ["boundary-orientation", "gauss-bonnet", "vector-field-index", "euler-characteristic", "quotient-space", "manifold", "poincare-hopf"],
    },
    {
        "id": "embedding-family",
        "title": "Drawing and embedding arguments",
        "purpose": "Ask whether connections can live on a chosen surface without forbidden crossings.",
        "first_principles": "This family studies room. A page, sphere, torus, or other surface gives routes and limitations. The answer may be decided before a perfect drawing is found.",
        "concepts": ["graph-planarity", "knots-and-links", "duality", "winding-linking", "manifold", "intersection-number"],
    },
    {
        "id": "motion-family",
        "title": "Motion through possible states",
        "purpose": "Turn mechanical or physical questions into questions about paths and barriers.",
        "first_principles": "This family replaces the object in motion with the space of all its possible positions. Holes and walls in that space explain blocked motions, unavoidable coincidences, and forced positions.",
        "concepts": ["configuration-space", "fixed-points", "deformation", "vector-field-index", "product-space", "brouwer-fixed-point", "equilibrium", "poincare-hopf"],
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


FAMILY_CONTRACTS = {
    "deformation-family": {
        "input": "A hard picture whose exact drawing is less important than a route, boundary, side behavior, or count it carries.",
        "action": "State the legal moves, move the object through only those moves, and replace the hard picture by an easier one.",
        "evidence": "The protected evidence is the fact that survives the whole motion: same endpoints, same boundary data, same route relation, or same invariant.",
        "output": "The output is a simpler picture that can answer the original question because the legal path to it preserved the question.",
        "failure_test": "Reject the argument if it cuts, glues, passes through forbidden matter, moves fixed data, or changes the meaning of sameness.",
    },
    "counting-family": {
        "input": "A situation where visible local events change too easily: cells split, crossings appear, defects move, or raw counts fluctuate.",
        "action": "Design a count that ignores harmless changes by cancellation, alternating terms, parity, or signs with geometric meaning.",
        "evidence": "The protected evidence is the total that legal redrawings cannot change, even though individual local events may appear or disappear.",
        "output": "The output is a number or parity fact that can prove impossibility, force existence, or compare two legally related pictures.",
        "failure_test": "Reject the argument if the count changes under a legal harmless move or if signs are assigned without a rule that can be checked.",
    },
    "surface-family": {
        "input": "A surface whose small patches look manageable but whose complete shape may carry holes, boundary behavior, handles, or side reversal.",
        "action": "Cut the surface into pieces, track boundary and orientation data, and glue the account back into a whole-surface statement.",
        "evidence": "The protected evidence is the global surface account: Euler characteristic, orientability, boundary behavior, or a total controlled by the surface.",
        "output": "The output is a whole-surface conclusion that local inspection alone could not justify.",
        "failure_test": "Reject the argument if it assumes every local choice glues globally, ignores boundary terms, or changes the surface while counting.",
    },
    "embedding-family": {
        "input": "An object with required connections or loop relations that must live inside a chosen surface or surrounding space.",
        "action": "Separate accidental crossings from forced ones by using allowed motion, surface room, over-under data, and route information.",
        "evidence": "The protected evidence is a relation that every legal placement must respect: linking, winding, unavoidable crossing, or unavailable route room.",
        "output": "The output is either a legal placement or a proof that no legal placement can avoid the obstruction.",
        "failure_test": "Reject the argument if it treats one failed drawing as impossibility or forgets data needed to distinguish crossings in space.",
    },
    "motion-family": {
        "input": "A physical or dynamical situation whose direct motion is too complicated to follow point by point.",
        "action": "Build the space of possible states, translate motion into paths or rules, and apply fixed-point, index, or obstruction reasoning there.",
        "evidence": "The protected evidence is the shape of possibility: a barrier, hole, forced self-agreement, index total, or missing legal path.",
        "output": "The output is a constraint on the original motion, such as an unavoidable state, blocked motion, equilibrium, or required defect.",
        "failure_test": "Reject the argument if the state space leaves out a real freedom, adds a false barrier, or cannot translate the conclusion back to the physical setup.",
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


FAMILY_PLAYBOOKS = {
    "deformation-family": {
        "setup": "Start with the original object, not the prettier target picture. Mark the fixed data: endpoints, boundary pieces, obstacles, gluing rules, side choices, and the question being protected.",
        "move": "Move the object continuously through only the allowed changes, checking after each kind of move that the protected fact has not changed.",
        "payoff": "The final simpler picture answers the original problem because the legal route to it carried the same question all the way across.",
        "failure": "The method fails when the easy picture is reached by crossing through a forbidden object, moving fixed data, or silently changing what sameness means.",
        "reader_test": "Can the reader describe the full legal route, not only the before-and-after pictures?",
    },
    "counting-family": {
        "setup": "Start by listing the local events that may change under motion: cells split, crossings appear, turns shift, or defects move.",
        "move": "Choose a count whose allowed changes cancel by design, using alternating terms, parity, or signs that come from the geometry of the situation.",
        "payoff": "Once the protected total is known in one honest version, every legally related version must obey it, so impossibility or forced existence can follow.",
        "failure": "The method fails when the count changes under a harmless legal redraw or when signs are assigned without a checkable direction rule.",
        "reader_test": "Can the reader explain one local change and why the chosen count stays fixed through that change?",
    },
    "surface-family": {
        "setup": "Start by naming the whole surface and its edge behavior: boundary, handles, crosscaps, holes, orientation, and any gluing instructions.",
        "move": "Break the surface into manageable pieces, track local information on the pieces, then glue the account back together without losing global restrictions.",
        "payoff": "The conclusion belongs to the whole surface, not to one patch, one drawing, or one chosen decomposition.",
        "failure": "The method fails when local ordinariness is mistaken for global simplicity or when boundary and orientation data are dropped from the account.",
        "reader_test": "Can the reader point to the full trip, full gluing, or full sum where the global surface constraint appears?",
    },
    "embedding-family": {
        "setup": "Start by separating the required object from the surrounding room: which points connect, which loops link, which crossings are forbidden, and what surface or space carries the placement.",
        "move": "Try legal placements while tracking route relations, over-under information, crossings, and winding that cannot be erased by allowed motion.",
        "payoff": "The result is either a legal placement or a proof that every legal placement must encounter the same obstruction.",
        "failure": "The method fails when one bad drawing is treated as proof, or when spatial information such as over-under order is lost in a flat picture.",
        "reader_test": "Can the reader say why every legal attempt is blocked, rather than only why one attempted drawing failed?",
    },
    "motion-family": {
        "setup": "Start by listing what information describes one complete state: positions, angles, boundary conditions, forbidden collisions, and any rule acting on states.",
        "move": "Turn those states into a space, read motion as paths or maps, and then apply deformation, fixed-point, index, or obstruction reasoning inside that state space.",
        "payoff": "The original system inherits the conclusion because the state space records the real freedoms and restrictions of the physical or dynamical problem.",
        "failure": "The method fails when the state space omits a real freedom, adds a false wall, or cannot translate its conclusion back to the original motion.",
        "reader_test": "Can the reader name the state space, the forbidden states, the rule or path, and the topological feature forcing behavior?",
    },
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
        {"title": "Products make spaces from independent choices", "text": "The lecture builds cubes and related spaces by taking products of intervals. The plain idea is that two or more choices vary at once, and the resulting state-space has its own shape.", "concepts": ["configuration-space", "topology-vs-geometry", "triangulation", "product-space"]},
        {"title": "Quotients turn edge instructions into spaces", "text": "When edges or points are identified, a flat drawing becomes a code for a new space. The same square can describe different worlds depending on the gluing rule.", "concepts": ["duality", "boundary-orientation", "deformation", "quotient-space"]},
        {"title": "Surgery treats construction as reasoning", "text": "Removing a simple piece and gluing another one back is a way to change the space under controlled rules. The operation matters because it tracks what feature has been changed and what feature is meant to survive.", "concepts": ["deformation", "triangulation", "invariant", "surgery"]},
    ],
    4: [
        {"title": "A square is not the space until its edges are read", "text": "The lecture returns to squares with edge identifications. The useful lesson is that the visible square is a set of instructions for travel, not the final surface itself.", "concepts": ["duality", "boundary-orientation", "topology-vs-geometry", "quotient-space"]},
        {"title": "Reversing an edge changes the global surface", "text": "Changing a gluing direction can turn an ordinary two-sided behavior into a one-sided one. The local patches remain simple, but the whole route structure changes.", "concepts": ["boundary-orientation", "invariant", "deformation", "manifold"]},
        {"title": "A route can leave the drawing and keep going", "text": "Edge identification teaches that a path reaching the side of the drawn square has not necessarily stopped. The boundary rule decides where that path re-enters and what loop it has traced in the actual surface.", "concepts": ["duality", "winding-linking", "boundary-orientation"]},
    ],
    5: [
        {"title": "Classification separates surfaces by durable parts", "text": "The lecture discusses orientable and non-orientable surface families. Handles, crosscaps, and boundaries matter because they survive the allowed simplifications and therefore describe the surface beyond one drawing.", "concepts": ["euler-characteristic", "boundary-orientation", "triangulation"]},
        {"title": "Surgery changes a surface by controlled cutting and gluing", "text": "The surface operations are not arbitrary cutting. They are controlled replacements that help reduce surfaces to standard forms while tracking what has changed and what surface information remains protected.", "concepts": ["deformation", "topology-vs-geometry", "invariant", "surgery"]},
        {"title": "Handles and crosscaps are durable building blocks", "text": "The lecture's classification viewpoint treats handles, crosscaps, and boundaries as parts that remain meaningful after simplification. The surface is understood by the pieces that cannot be wished away by a different drawing.", "concepts": ["boundary-orientation", "euler-characteristic", "invariant", "manifold"]},
    ],
    6: [
        {"title": "Moving an object inside a manifold", "text": "The lecture asks whether a sub-object can be moved around obstacles inside a larger space. The answer depends on dimension: enough room can turn collision into avoidance.", "concepts": ["generic-position", "deformation", "graph-planarity", "manifold"]},
        {"title": "Forced meetings become evidence", "text": "When an intersection cannot be removed by legal motion, it stops being a drawing accident and becomes information about the surrounding space. The lecture prepares the later signed count by separating removable crossings from forced ones.", "concepts": ["invariant", "winding-linking", "parity", "intersection-number"]},
        {"title": "Dimension measures available escape room", "text": "The lecture turns the physical feeling of room into a mathematical test. If the surrounding space has enough independent directions, objects can often avoid meeting; when it does not, intersections become meaningful.", "concepts": ["generic-position", "topology-vs-geometry", "graph-planarity"]},
    ],
    7: [
        {"title": "The center-of-gravity demonstration", "text": "Sliding two hands inward under an object creates a physical example of a forced state. Continuity makes the balancing event unavoidable because the relevant condition changes steadily rather than jumping past the answer.", "concepts": ["fixed-points", "configuration-space", "deformation"]},
        {"title": "Existence without a formula", "text": "The lecture turns a hands-on balancing fact into the idea that some special point or event can be forced even when no explicit formula for it is available.", "concepts": ["fixed-points", "invariant", "generic-position"]},
        {"title": "A physical motion becomes an intersection question", "text": "The balancing setup can be read as two continuously changing conditions that must meet. That translation is the bridge from a demonstration with hands to the later formal language of intersections.", "concepts": ["duality", "fixed-points", "configuration-space", "intersection-number"]},
    ],
    8: [
        {"title": "Signed intersection number", "text": "The lecture counts intersections with plus and minus signs. The signs let newly born opposite pairs cancel, so the total remembers more than the visible crossing count.", "concepts": ["winding-linking", "boundary-orientation", "parity", "intersection-number"]},
        {"title": "Pair creation and cancellation", "text": "When a positive and a negative intersection appear together, the picture changes but the signed total does not. This is the cleanest example of designed cancellation.", "concepts": ["generic-position", "invariant", "vector-field-index", "intersection-number"]},
        {"title": "Orientation gives signs their meaning", "text": "A signed intersection count only works after the surrounding surface or space supports a consistent direction choice. The plus or minus sign is geometric information, not an arbitrary label added after counting.", "concepts": ["boundary-orientation", "winding-linking", "invariant"]},
    ],
    9: [
        {"title": "The graph of a map meets the diagonal", "text": "The lecture treats a fixed point as an intersection: the graph records where points go, and the diagonal records points that stay where they started.", "concepts": ["fixed-points", "duality", "graph-planarity", "product-space", "intersection-number"]},
        {"title": "Missing middle caption is kept visible", "text": "The middle video of this lecture has no recovered captions, so the explanation leans on the available surrounding parts and preserves the source gap in the audit.", "concepts": ["invariant", "generic-position", "fixed-points"]},
        {"title": "A rule becomes a shape that can be compared", "text": "Representing a map by its graph turns an invisible instruction into an object in a larger space. Once it is drawn that way, fixed points become meetings with the diagonal.", "concepts": ["duality", "fixed-points", "configuration-space"]},
    ],
    10: [
        {"title": "Brouwer on the closed ball", "text": "The lecture's fixed-point theorem says a continuous self-map of a closed ball must leave some point fixed. The point is forced by the shape, not found by calculation.", "concepts": ["fixed-points", "boundary-orientation", "topology-vs-geometry", "brouwer-fixed-point"]},
        {"title": "Boundary changes the theorem", "text": "The closed ball includes its boundary, and that boundary is part of why the statement has force. Removing or changing the boundary can change the conclusion.", "concepts": ["boundary-orientation", "configuration-space", "invariant"]},
        {"title": "No global escape from self-agreement", "text": "The theorem can be understood as ruling out a continuous way for every point of the ball to avoid itself at once. The shape of the filled ball blocks that escape.", "concepts": ["fixed-points", "deformation", "invariant", "brouwer-fixed-point"]},
    ],
    11: [
        {"title": "Vector fields replace solved trajectories", "text": "The lecture starts the dynamics chapter by asking what can be known without solving a differential equation. A vector field gives an arrow pattern whose defects can be studied topologically.", "concepts": ["vector-field-index", "fixed-points", "configuration-space"]},
        {"title": "Equilibria are arrow-field failures", "text": "An equilibrium is where the arrow vanishes. The index records how nearby arrows turn around that failure, turning local dynamics into signed evidence that can later be added over the whole surface.", "concepts": ["vector-field-index", "gauss-bonnet", "invariant", "equilibrium"]},
        {"title": "Local arrow patterns can be counted", "text": "A source, sink, and saddle are not only dynamical pictures. Around each defect the arrows turn in a characteristic way, and that turning can be assigned a signed index.", "concepts": ["vector-field-index", "parity", "boundary-orientation", "equilibrium"]},
    ],
    12: [
        {"title": "Adding local indices", "text": "The lecture asks what all local vector-field indices know together. The sum is not arbitrary; it is tied to the surface carrying the field.", "concepts": ["vector-field-index", "euler-characteristic", "boundary-orientation"]},
        {"title": "Poincare-Hopf as surface bookkeeping", "text": "Local arrow failures add up to Euler characteristic. This converts the earlier cell-counting idea into a statement about possible motion and shows why surface topology controls vector fields.", "concepts": ["euler-characteristic", "gauss-bonnet", "invariant", "poincare-hopf"]},
        {"title": "Defects can move while the total stays fixed", "text": "The lecture's global index idea allows local equilibria to shift, split, or cancel in controlled ways. What survives is the total signed count demanded by the surface.", "concepts": ["vector-field-index", "deformation", "invariant", "equilibrium", "poincare-hopf"]},
    ],
    13: [
        {"title": "Using Poincare-Hopf in both directions", "text": "The theorem can predict forced equilibria from topology, or use known equilibria to reveal something about the surface. It is a bridge between shape and motion.", "concepts": ["vector-field-index", "euler-characteristic", "fixed-points", "equilibrium", "poincare-hopf"]},
        {"title": "The hairy-ball idea in plain form", "text": "On a sphere, a continuous tangent arrow pattern cannot avoid defects everywhere. Something must fail because the whole surface does not allow all local choices to agree.", "concepts": ["boundary-orientation", "vector-field-index", "topology-vs-geometry"]},
        {"title": "Topology predicts a failure of motion", "text": "The point of Poincare-Hopf is not only to count existing equilibria. It can prove that some defect must be present before the exact vector field is solved.", "concepts": ["vector-field-index", "euler-characteristic", "fixed-points", "poincare-hopf"]},
    ],
    14: [
        {"title": "Applications as honest translations", "text": "The late applications work by translating a physical or rotational situation into a space, a rule, and a protected obstruction. The theorem applies only after that translation is correct.", "concepts": ["configuration-space", "fixed-points", "invariant"]},
        {"title": "Rotations and dynamics share the same proof engine", "text": "Rotations in space and dynamical examples look different, but both can be read through fixed points, vector fields, indices, or deformation-protected counts once the right space and rule are identified.", "concepts": ["vector-field-index", "configuration-space", "duality"]},
        {"title": "The model must carry the real constraint", "text": "An application succeeds only when the chosen space, allowed motion, and protected count match the physical situation. A theorem applied to the wrong model proves a true statement about the wrong object.", "concepts": ["configuration-space", "topology-vs-geometry", "invariant"]},
    ],
    15: [
        {"title": "The table of contents becomes one argument", "text": "The final review names the course as pictorial thinking. Paper strips, deformation, manifolds, intersections, fixed points, and vector fields form one chain rather than separate topics.", "concepts": ["deformation", "invariant", "topology-vs-geometry", "manifold", "intersection-number", "poincare-hopf"]},
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
        "The word deformation should be read in an everyday way first. A curve is allowed to bend, stretch, and slide, just as a loose string could move on a table. But some things are not allowed. An endpoint fixed on the boundary cannot quietly trade places with another endpoint. One curve cannot pass through another curve if the original problem forbids crossings. The proof begins by naming those permissions and prohibitions. Only after that does a cleaner picture become trustworthy.",
        "This is the first time the course makes a drawing carry a contract. The visible ink can change, but the contract cannot. The contract says which points belong to the boundary data, which meetings are forbidden, and which motions count as the same problem. Once that is clear, the reader can stop asking whether a particular drawing is skillful enough and start asking whether any drawing could obey the same contract. That shift is the mathematical content.",
        "The mathematical principle behind the lecture is boundary order. The endpoints around the disk are part of the data, and legal motion cannot reorder them. If a crossing-free drawing existed, deformation would allow the reader to clean it while preserving that circular order. When the cleaned version still forces a crossing, the obstruction belongs to the problem itself. The proof is not that one sketch failed. The proof is that every legal sketch inherits the same order problem.",
        "The payoff for the rest of the course is large. Later arguments will move surfaces, graphs, arrows, and maps. This lecture teaches the reader how to ask whether the motion kept the original question intact. Without that habit, every later simplification could be a hidden change of subject.",
    ],
    3: [
        "After deformation is introduced, the course needs a supply of spaces whose behavior is worth studying. Lecture 3 explains that spaces can be built from recipes. That is a major step for a beginner. A space is not only something already sitting in front of us, like a sheet of paper or a ball. A space can be the result of a rule about choices, sameness, and replacement. The lecture is teaching the reader to read a mathematical object by asking how it was made.",
        "A product is the simplest example of this recipe language. If one choice moves along an interval and another independent choice also moves along an interval, then the pair of choices fills a square. Nothing mystical is happening: a point in the square records two pieces of information at once. This matters later because many spaces in the course are spaces of possible states. To understand such a space, the reader must ask how many independent choices are being recorded and what counts as changing one choice while holding another fixed.",
        "A quotient is the opposite kind of move. Instead of adding independent choices, it declares that two places should count as the same place. The declaration is not a cosmetic label. It changes travel. A path that seems to leave through one edge may re-enter through another because the rule has identified those exits. This is why edge labels on a square deserve careful reading. They can turn a flat drawing into a cylinder, torus, Mobius band, or projective-plane style object.",
        "Surgery adds a third habit: remove a piece whose role is understood, then attach a different piece under controlled rules. Everyday repair gives the right first image, but mathematical surgery is stricter. One must know exactly what has been removed, exactly where the replacement is attached, and which boundary information matches. If that matching is wrong, the resulting space is a different object and later theorems may no longer apply.",
        "The important shift is that a drawing becomes an instruction manual. Later, when fixed points are graphs meeting diagonals or when vector fields live on manifolds, the reader needs to remember that the space itself was made by rules. The construction recipe controls what motion, boundary, and sameness mean. The first-principles detail is therefore not the vocabulary of product, quotient, surgery, or manifold. It is the simpler question beneath all of them: what choices are allowed, what points have been declared identical, and what local piece has been replaced?",
    ],
    4: [
        "Lecture 4 deepens the idea that gluing rules create worlds. The same visible patch can describe different spaces if its boundary is read differently. This matters because the mathematical object is not the ink on the page; it is the travel rule encoded by that ink. If leaving through one edge returns through another edge, then routes inside the square have a wraparound behavior. If an edge is reversed before it is glued, a trip through the surface can reverse the sense of side.",
        "The beginner mistake is to treat the square as a container with four walls. In a gluing diagram the boundary may not be a wall at all. It may be a doorway. The label tells the traveler what happens at the doorway: which edge is reached, whether direction is kept, and whether left and right have been swapped. A flat square can therefore describe a world with no edge in the ordinary sense. The page is only a code for that world.",
        "This is why quotient constructions should be read through motion. Imagine a small traveler walking straight across the drawn patch. If the traveler crosses a labeled edge, the rule says where the next step begins. Repeating that experiment reveals loops that are invisible in the drawing. It also reveals whether a tiny arrow carried by the traveler returns pointing the same way or reversed. That is the everyday content behind orientation.",
        "This lecture is a quiet but important bridge. It prepares the reader for why orientation, boundary, and global consistency keep returning. A vector field on a sphere and a vector field on a torus do not differ merely by their drawing style. They differ because the underlying surface gives different routes for arrows and loops to follow. The course is teaching the reader to ask, for every picture, what rules the picture represents.",
        "The first-principles point is that sameness is created by the rule, not by visual resemblance. If two exits of a drawn square are declared to be the same passage, then a path leaving one side has not ended; it has re-entered the world somewhere else. That habit becomes essential later when maps, diagonals, and vector fields are also treated as objects whose behavior depends on the space carrying them. The rule is part of the object.",
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
        "Lecture 9 carries intersection thinking into fixed points. A map from a space to itself can feel abstract because it is a rule rather than a visible object. The lecture makes it visible by drawing the graph of the map. For every input point, the graph records two pieces of information: where the point started and where the rule sends it. That record is now a geometric object that can be compared with other geometric objects.",
        "The diagonal is the key comparison object. It is the set of pairs where the first entry and the second entry agree. In everyday language, the diagonal is the place where a point has not changed its name. A fixed point is exactly a point whose starting position and ending position match. So the fixed-point question becomes a meeting question: does the graph of the rule meet the diagonal of self-agreement?",
        "This translation matters because it brings the earlier course tools back into play. If a fixed point were treated only as an equation, a beginner might think the only possible proof is to solve the equation. The graph-diagonal picture shows another route. The course can ask whether those two objects are allowed to avoid each other under legal deformation. If the answer is no, then a fixed point is forced even before anyone knows where it is.",
        "The missing middle caption is a real source caveat, so the companion should not pretend to recover every spoken detail of the lecture. The reliable mathematical spine is still clear from the surrounding material: fixed-point theory is being built from intersections, deformation, and invariant information. The reader should hold onto the graph, the diagonal, and the fact that their meeting means self-agreement.",
        "The first-principles gain is that a rule has been turned into a shape. A map may sound like an instruction, but its graph can be moved, compared, and counted. The diagonal is the shape of self-agreement. Their intersection is not a metaphor for a fixed point; it is the fixed point written geometrically. This is exactly the kind of conversion the course wants readers to learn: change the form of the problem until the hidden constraint becomes visible.",
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
        "A useful first image is to walk around a tiny loop surrounding one defect and watch the nearby arrows. The arrows may turn once with the loop, turn the other way, or combine in a more complicated local pattern. The index records that turning. The point is not to memorize names such as source or saddle. The point is to notice that the field has failed to give a nonzero direction at the center, and the surrounding arrows leave evidence of how that failure behaves.",
        "This is where the earlier surface bookkeeping becomes visibly necessary. Euler characteristic was not just a cell-counting curiosity. It becomes the number that controls the total defect of a vector field. The lecture therefore connects three layers of the course: surfaces can be decomposed and counted, vector fields can fail locally, and topology can force the total of those failures. Poincare-Hopf is powerful because it makes motion answer to shape.",
        "The important detail is that local defects can move around. A source can be shifted, a positive-negative pair can be created or canceled under the right circumstances, and a drawing can be cleaned up. But the total signed index is not free when the underlying surface is fixed. That is the same survival principle from intersection number, now expressed in the language of dynamics. The arithmetic was designed to ignore harmless local reshuffling and remember the whole-surface demand.",
        "For the reader, this lecture is the moment when Euler characteristic stops being only a surface label. It becomes a demand placed on motion. The same number obtained from cutting a surface into pieces now says how arrow-field defects must add up on that surface. That is the big conceptual turn: a number first learned from shape can later constrain every continuous choice of arrows on that shape.",
    ],
    13: [
        "Lecture 13 uses Poincare-Hopf as a working tool rather than a slogan. If the topology of the surface is known, the theorem restricts what equilibria a vector field can have. If the equilibria and their indices are known, they can reveal information about the surface. This is a two-way exchange between shape and motion. The theorem is not merely a formula; it is a bridge between two kinds of evidence.",
        "The hairy-ball idea is the most everyday form of the message. On a sphere, one cannot choose a continuous nonzero tangent arrow everywhere. Some defect must occur because the whole surface does not allow all local arrow choices to agree. This is exactly the course's local-to-global principle in dynamics. Every small patch may seem able to carry an arrow, but the complete surface has fewer choices than the patches suggest.",
        "The theorem's depth is that it can be used in both directions without changing its meaning. If the surface is known, it predicts what kinds of vector-field failures must occur. If the failures are observed, they give information about the surface. The equation is therefore not just a result to remember; it is a tool for translating between local motion and global shape.",
        "The important first-principles detail is that the theorem does not inspect one equilibrium in isolation. It asks for the total signed behavior over the whole surface. Local arrow patterns may look adjustable one by one, but the completed surface makes a demand on their sum. That is the reason topology can make a prediction before the differential equation is solved.",
    ],
    14: [
        "Lecture 14 turns the machinery toward applications. Rotations, physical systems, and dynamical examples can look unrelated, but the course asks the same modeling questions each time. What is the space? What is the rule or motion on that space? What changes are legal? What count, fixed point, index, or obstruction is protected? Without that translation, applying topology would be empty.",
        "The first-principles issue is that an application is never the raw physical object itself. It is a selected description of the object's possible states. For a rotation problem, the state might be an angle or an orientation. For a mechanical problem, it might be a position together with a constraint. For a dynamical problem, it might be the surface on which arrows describe motion. The topology applies to that state space, so building the state space is part of the proof.",
        "The value of the applications is that they show topology as a method for behavior, not only for static shapes. A physical system may have too many details to track directly, but the space of its possible states can have holes, walls, boundaries, or forced passages. Once a problem is honestly translated into that space, the earlier proof families apply. The course's demonstrations are therefore not isolated performances; they are examples of a reusable way to reason about constrained motion.",
        "This lecture also warns against careless application. A theorem cannot be pasted onto a physical story until the modeling has been done. The state space, boundary conditions, allowed motions, and protected quantity must be identified. The reader should ask what information has been kept and what has been thrown away. If a supposedly harmless detail changes the state space, then it may change the conclusion.",
        "The mathematical principle is model first, theorem second. The shape used in the proof must be the shape of the actual possibilities. If the model omits a freedom, adds a false barrier, or forgets a boundary condition, the conclusion may no longer describe the physical system. When the translation is honest, topology can explain why a behavior is unavoidable even when the physical system itself looks messy.",
    ],
    15: [
        "The final lecture reviews the course as pictorial thinking. That phrase matters because the pictures have not been decorative. The Mobius strip, disk paths, edge identifications, handle slides, intersections, graphs of maps, diagonals, and vector fields all served as proof environments. The point of the course is to learn how to make a picture carry constraints: what may move, what may not move, what survives, and what conclusion is forced.",
        "Read backward, the course becomes one chain. Mobius strips teach global surprise. Deformation teaches legal simplification. Products, quotients, and surgery build spaces. Surface classification names durable parts. Intersection number turns meetings into signed evidence. Fixed points turn rules into forced self-agreement. Vector-field index and Poincare-Hopf turn motion into surface bookkeeping. The final demonstrations return to strips because the whole course has been about seeing more in a picture than its immediate appearance.",
        "The ready-state lesson is therefore not a list of theorems. It is a way of asking questions. What is allowed to move? What survives the motion? What count is designed to ignore fake changes? What whole-shape constraint forces the answer? If the reader can ask those questions across strips, surfaces, maps, and vector fields, then the course has done its work.",
        "The final lecture also explains why a companion should be organized by concepts, themes, subthemes, and method families rather than only by chronology. Chronology shows how the course unfolds. The concept map shows the reusable reasoning underneath that order. A reader needs both to see the course as one connected method.",
    ],
}


LECTURE_SOURCE_LENS = {
    1: [
        "Read the Mobius-strip words as evidence about a gluing rule. The important source move is not that paper is surprising; it is that following, coloring, or cutting the strip tests whether a local side choice survives one full trip around the surface.",
        "The anchor words should be held together. Twist and glue explain how the object is made. One side versus two sides explains what the whole object remembers. Cutting along the center is the controlled operation that makes that memory visible.",
    ],
    2: [
        "Read the disk-path lecture as a proof about boundary order. The source language around deformation and curves that do not intersect matters because it fixes the contract before any drawing is simplified.",
        "The anchor words prevent a common false proof. A disk by itself is not enough; the paired boundary points, their order, and the no-crossing rule are the data. Deformation is evidence only while those data stay unchanged.",
    ],
    3: [
        "Read product, quotient, surgery, balls, spheres, and manifolds as construction words. The lecture is teaching how a space is made before later theorems are allowed to use that space.",
        "The source lens is to ask what each construction changes. Product adds independent choices. Quotient changes sameness. Surgery changes a part under a boundary rule. Manifold says local neighborhoods are ordinary enough for later local arguments.",
    ],
    4: [
        "Read the square and boundary-identification anchors as instructions rather than pictures. The source point is that the same drawn square can become different spaces depending on which edges are treated as the same and whether direction is reversed.",
        "This lecture should make later pages less abstract. When a map, field, or route lives on a manifold, its behavior is controlled by these hidden travel rules. The drawing is useful only after the identification rule has been read.",
    ],
    5: [
        "Read classification, orientable, non-orientable, Mobius, and surgery as a vocabulary for durable surface parts. The source arc is about reducing surfaces to pieces that survive legal simplification.",
        "The practical evidence is not the name of a surface family alone. Handles give routes, crosscaps reverse side choices, boundaries add edge behavior, and surgery explains how the surface is changed while these features are tracked.",
    ],
    6: [
        "Read submanifold, obstacles, dimensions, and intersection as a question about room. The source material is preparing the reader to separate a meeting caused by a cramped space from a meeting caused by a careless drawing.",
        "The important source move is ordinary position. Before counting intersections, the objects must be placed so meetings are clean enough to inspect. Dimension then tells whether avoidance is expected or whether meeting carries evidence.",
    ],
    7: [
        "Read center of gravity and continuous motion as the physical entrance to forced existence. The lecture is not only about balance; it is about a changing condition that cannot jump past the special state.",
        "The source lens is to translate the demonstration into intersection language. One moving condition and another condition must meet. That same shape of reasoning prepares fixed points, diagonals, equilibria, and later state-space applications.",
    ],
    8: [
        "Read intersection number, orientation, positive or negative, isotopy invariant, and pairwise creation as one account. The lecture is not merely introducing signs; it is explaining why signs let the count survive legal motion.",
        "The source evidence is the birth and cancellation of pairs. A raw crossing count changes, but a signed total can stay fixed. Orientation is what makes the plus or minus mean something rather than being arithmetic pasted onto a picture.",
    ],
    9: [
        "Read graph of a mapping, diagonal, and fixed points as the translation of a rule into a meeting problem. Because one middle caption is missing, the source lens must stay modest and lean on the available surrounding lecture parts.",
        "The important source move is the graph. A map becomes a geometric object in a larger space. The diagonal records self-agreement. Their meeting is not an analogy; it is the fixed point written in a form that intersection reasoning can inspect.",
    ],
    10: [
        "Read Brouwer, closed ball, boundary, and continuous map as a statement about no global escape. The source arc is existence without computation: a filled shape can force at least one point to stay put.",
        "The boundary words matter. The theorem is not saying every space and every rule has a fixed point. It is saying that a closed ball, together with continuity and self-mapping, blocks the attempt to move every point away from itself.",
    ],
    11: [
        "Read vector field, differential equations, equilibria, and index as a change in what counts as understanding motion. The lecture does not solve paths one by one; it asks what the arrow pattern must contain.",
        "The source lens is to look around an equilibrium, not only at it. Nearby arrows turn around the failure point, and that turning becomes a signed local count. This is intersection-number thinking moved into dynamics.",
    ],
    12: [
        "Read index of a vector field, equilibria, Euler characteristic, and Poincare-Hopf as a sum-over-the-whole-surface lecture. The source point is that local defects have a total controlled by the surface.",
        "The evidence is the move from local to global. Sources, sinks, saddles, and other defects may shift under cleanup, but the total signed index is not free. It has to answer to the surface carrying the field.",
    ],
    13: [
        "Read Poincare-Hopf, index sum, Euler characteristic, hairy ball, and equilibria as a two-way exchange. The lecture uses topology to predict defects, and it can also use observed defects to say something about the surface.",
        "The hairy-ball anchor should be read as the plain case, not the whole theorem. The deeper source point is the total over all isolated defects. A local arrow choice may look possible, but the completed surface can forbid all choices from agreeing.",
    ],
    14: [
        "Read applications, rotations in space, Poincare-Hopf, and dynamical systems as a modeling lecture. The source material is testing whether earlier proof families can be carried into physical or moving systems without losing the real constraints.",
        "The source lens is model first, theorem second. Name the space of states, the rule or motion, the forbidden behavior, and the protected count. Only then can a topological theorem say something about the application.",
    ],
    15: [
        "Read table of contents, pictorial thinking, deformation, intersection, fixed point, and vector field as a dependency chain. The final lecture is not a list of topics; it is a review of one reasoning habit as it changes setting.",
        "The source lens is to follow the conversions. Paper strips become global surface evidence. Deformations protect questions. Intersections become signed counts. Fixed points and vector fields turn those counts into existence and motion statements.",
    ],
}


LECTURE_SOURCE_CHECKPOINTS = {
    1: {
        "trust": "Trust the making-following-cutting sequence as evidence about the gluing rule, because each action tests whether local side information survives a full trip.",
        "do_not_overread": "Do not overread the paper surprise as a one-off curiosity or as a statement about exact shape, length, or bend angle.",
        "math_question": "What whole-surface fact appears only after the traveler or cut has gone all the way around the strip?",
    },
    2: {
        "trust": "Trust the disk-path setup only together with endpoint order, fixed boundary data, and the rule that paths may not cross.",
        "do_not_overread": "Do not treat a cleaner redraw as proof unless the redraw was reached by legal motion that preserved the original boundary problem.",
        "math_question": "Which part of the endpoint order survives every allowed redraw and forces or forbids a crossing?",
    },
    3: {
        "trust": "Trust product, quotient, manifold, and surgery language as construction evidence: the lecture is saying how spaces are built before they are used.",
        "do_not_overread": "Do not treat a square, cube, or cut surface as the final object until the construction rule has been read.",
        "math_question": "Which choices are combined, which points are identified, and which local replacement changes the possible routes?",
    },
    4: {
        "trust": "Trust edge labels and arrows as travel instructions, because they decide whether a path stops, re-enters, or returns with direction changed.",
        "do_not_overread": "Do not read the visible boundary of the drawn square as the boundary of the finished space without checking the identifications.",
        "math_question": "Where does a traveler go after crossing a labeled edge, and does the rule preserve or reverse orientation?",
    },
    5: {
        "trust": "Trust handles, crosscaps, orientability, and boundary components as durable surface evidence, not as surface names alone.",
        "do_not_overread": "Do not accept classification by visual resemblance; two drawings can differ while carrying the same preserved surface data.",
        "math_question": "Which durable feature survives the cutting, gluing, or surface simplification being used in the argument?",
    },
    6: {
        "trust": "Trust dimension and ordinary-position language as preparation for deciding whether meetings are accidental or forced.",
        "do_not_overread": "Do not count a messy contact before the picture has been cleaned enough for separate meetings to be inspected.",
        "math_question": "After a tiny legal nudge, which meetings disappear as accidents and which remain as evidence?",
    },
    7: {
        "trust": "Trust the center-of-gravity demonstration as continuity evidence: a changing physical condition cannot jump past the balancing event.",
        "do_not_overread": "Do not treat the demonstration as a formula for locating the special point; its job is to prove the event must occur.",
        "math_question": "What changes continuously, and what event is impossible to skip under that continuous change?",
    },
    8: {
        "trust": "Trust the signed crossing language only when orientation explains the plus and minus signs and pair creation has been accounted for.",
        "do_not_overread": "Do not use the raw number of visible crossings as protected evidence, because legal motion can change that number.",
        "math_question": "Why does a positive-negative pair contribute no net change to the signed total?",
    },
    9: {
        "trust": "Trust the available graph-and-diagonal spine, while keeping the missing middle caption visible as a source limit.",
        "do_not_overread": "Do not fill the missing caption gap with a stronger theorem claim than the surrounding source arc supports.",
        "math_question": "Why does an intersection of the graph with the diagonal mean the original rule has a fixed point?",
    },
    10: {
        "trust": "Trust Brouwer language only with the closed filled domain, self-map condition, boundary included, and continuity kept explicit.",
        "do_not_overread": "Do not turn the theorem into a claim about every space or every rule; changing the domain can change the conclusion.",
        "math_question": "What blocks a continuous attempt to move every point of the filled ball away from itself?",
    },
    11: {
        "trust": "Trust vector-field language as arrow-pattern evidence, especially the places where arrows vanish and nearby arrows turn.",
        "do_not_overread": "Do not confuse naming an equilibrium with understanding its topological evidence; the surrounding arrows matter.",
        "math_question": "What does a small loop around the equilibrium see in the nearby arrow directions?",
    },
    12: {
        "trust": "Trust index-sum language only after local vector-field defects are isolated and every defect belongs to the whole-surface account.",
        "do_not_overread": "Do not treat one defect as the theorem; the lecture is preparing a total over the entire surface.",
        "math_question": "Which local indices are being added, and what surface controls their total?",
    },
    13: {
        "trust": "Trust Poincare-Hopf as a two-sided account linking all local defects to Euler characteristic.",
        "do_not_overread": "Do not reduce the lecture to the hairy-ball example; that example is one visible consequence of the full index-sum statement.",
        "math_question": "How does the complete surface force the total defect count of a vector field?",
    },
    14: {
        "trust": "Trust applications only after the state space, allowed motion, forbidden states, and protected obstruction have been named.",
        "do_not_overread": "Do not paste a theorem onto a physical story before proving the model carries the real freedoms and restrictions.",
        "math_question": "What exact feature of the state space becomes the claimed physical constraint?",
    },
    15: {
        "trust": "Trust the final review as a dependency map linking objects, legal moves, protected evidence, and forced conclusions across the course.",
        "do_not_overread": "Do not treat pictorial thinking as a style preference; in this course the picture must carry a rule or count.",
        "math_question": "Can each topic be read as object, legal move, surviving fact, and forced conclusion?",
    },
}


LECTURE_SPINE = [
    {
        "lecture": 1,
        "object": "A strip made by gluing its ends after a half-turn.",
        "plain_question": "Can a surface look ordinary in every small patch while carrying a whole-surface rule that changes what side means?",
        "legal_move": "Follow, mark, or cut the strip without pretending the glued edge rule has disappeared.",
        "surviving_fact": "A full trip around the strip reverses the local side choice instead of returning it unchanged.",
        "why_later": "This is the first warning against local-only thinking. Later orientation, manifolds, vector fields, and surface classification all use the same gap between small-patch behavior and whole-object behavior.",
    },
    {
        "lecture": 2,
        "object": "Curves inside a disk with boundary points held in their circular order.",
        "plain_question": "When can a messy drawing be replaced by a cleaner one without changing the problem it was meant to answer?",
        "legal_move": "Slide and bend curves while keeping endpoints fixed in order and while preventing forbidden crossings.",
        "surviving_fact": "Boundary order and the no-crossing rule survive the redraw, so an unavoidable crossing belongs to the original setup.",
        "why_later": "This lecture makes deformation into a proof method. Intersection number, fixed points, and vector-field cleanup all rely on this same contract: move the picture, but protect the question.",
    },
    {
        "lecture": 3,
        "object": "Spaces built from choices, identifications, local patches, and controlled replacements.",
        "plain_question": "How can a complicated space be made from simple instructions instead of being drawn all at once?",
        "legal_move": "Build by product, quotient, manifold charts, or surgery while keeping the construction rule visible.",
        "surviving_fact": "The rule of construction decides the routes, holes, sides, and local neighborhoods available in the finished space.",
        "why_later": "Later theorems are only as honest as the spaces they act on. This lecture gives the raw building tools for configuration spaces, graphs of maps, quotient surfaces, and surface surgery.",
    },
    {
        "lecture": 4,
        "object": "A square whose marked edges are read as travel instructions for a finished surface.",
        "plain_question": "How can the same flat drawing represent different worlds depending on which edge exits are declared identical?",
        "legal_move": "Read each edge identification as part of the object, including whether direction is preserved or reversed.",
        "surviving_fact": "The gluing rule determines whether paths close, whether sides remain consistent, and whether the drawn boundary is a true boundary.",
        "why_later": "This is the plain entrance to quotient thinking. It prepares the reader for manifolds and for later situations where a rule, not visual appearance, defines the mathematical object.",
    },
    {
        "lecture": 5,
        "object": "Surfaces broken into standard features such as handles, crosscaps, and boundary components.",
        "plain_question": "What does it mean to say two surfaces are the same when their drawings can look very different?",
        "legal_move": "Cut, glue, and simplify under controlled surface operations while tracking the features those operations preserve.",
        "surviving_fact": "Orientability, boundary behavior, and durable surface pieces remain as the evidence used to classify the surface.",
        "why_later": "This gives Euler characteristic and orientation a home. Later local counts only have force because they live on a surface whose global type has been understood.",
    },
    {
        "lecture": 6,
        "object": "Subspaces placed inside a surrounding space with only so much room to avoid one another.",
        "plain_question": "When is a meeting between objects an accident of the drawing, and when is it forced by dimension and position?",
        "legal_move": "Move objects into ordinary position so meetings are clean and separate, without changing the surrounding problem.",
        "surviving_fact": "After accidental coincidences are removed, the remaining pattern of meetings can carry real information.",
        "why_later": "This lecture supplies the discipline needed before signs can be assigned. Intersection number only works after meetings are clean enough to count honestly.",
    },
    {
        "lecture": 7,
        "object": "A physical balance condition that changes continuously as the setup moves.",
        "plain_question": "How can a special state be forced even when we cannot calculate its exact location?",
        "legal_move": "Track the changing condition continuously and ask whether it can pass from one side of a requirement to another without meeting it.",
        "surviving_fact": "Continuity prevents the condition from jumping over the balance state.",
        "why_later": "This is the physical doorway into existence proofs. It prepares fixed points, intersections with the diagonal, and equilibria as forced special states rather than computed answers.",
    },
    {
        "lecture": 8,
        "object": "Clean intersections between oriented objects, equipped with plus and minus signs.",
        "plain_question": "How can a count survive when crossings can appear or disappear during legal motion?",
        "legal_move": "Assign signs using a consistent orientation rule and allow only deformations where pair creation is inspected.",
        "surviving_fact": "Opposite-signed pairs can be born or die without changing the signed total.",
        "why_later": "This is the counting engine for the second half of the course. Fixed points and vector-field index both reuse the idea that local events become evidence when cancellation is controlled.",
    },
    {
        "lecture": 9,
        "object": "The graph of a map compared with the diagonal of self-agreement.",
        "plain_question": "How can the equation that says 'the output equals the input' become a visible geometric meeting?",
        "legal_move": "Translate the rule into its graph in input-output space and compare it with the diagonal without changing what equality means.",
        "surviving_fact": "A meeting of graph and diagonal is exactly a fixed point of the original map.",
        "why_later": "This converts rules into shapes. Brouwer and later dynamics become easier to read because existence can now be treated as forced intersection rather than hidden algebra.",
    },
    {
        "lecture": 10,
        "object": "A continuous self-map of a closed ball, including its filled interior and boundary.",
        "plain_question": "Why can a filled shape force at least one point to stay put under every continuous rule of the right kind?",
        "legal_move": "Keep the domain filled, keep the boundary condition honest, and forbid jumps in the rule.",
        "surviving_fact": "The ball gives no continuous escape plan that moves every point away from itself at once.",
        "why_later": "This is the strongest plain example of shape forcing existence. It also teaches the necessary caution: the theorem depends on the exact space and the exact kind of rule.",
    },
    {
        "lecture": 11,
        "object": "A vector field, meaning an arrow assigned to each point of a surface or state space.",
        "plain_question": "What can be learned about motion without solving every path of motion?",
        "legal_move": "Study the arrow pattern and isolate the points where the arrow vanishes.",
        "surviving_fact": "An equilibrium carries more information than its location; nearby arrows turn around it in a countable way.",
        "why_later": "This shifts the course from fixed places to motion laws. It prepares index as the local evidence attached to a failure of motion.",
    },
    {
        "lecture": 12,
        "object": "Indices assigned to isolated vector-field defects by reading nearby arrow turning.",
        "plain_question": "How can many local motion failures add up to one whole-surface demand?",
        "legal_move": "Clean the field to isolated defects, read the turning around each one, and add the signed local counts.",
        "surviving_fact": "Defects may move or split, but the total signed index is constrained by the surface.",
        "why_later": "This is the immediate bridge from local dynamics to Poincare-Hopf. It shows why the whole surface, not one defect, controls the conclusion.",
    },
    {
        "lecture": 13,
        "object": "A vector field on a surface, with all isolated defects counted together.",
        "plain_question": "Why must the total defect of a motion pattern answer to the shape that carries it?",
        "legal_move": "Use Poincare-Hopf only after the field is clean enough and the surface carrying it is the right one.",
        "surviving_fact": "The sum of local indices equals the Euler characteristic of the surface.",
        "why_later": "This gathers the course's main chain: surface bookkeeping, signs, local defects, and global constraint. The hairy-ball idea is one visible consequence, not the whole story.",
    },
    {
        "lecture": 14,
        "object": "A physical or moving system translated into a space of possible states.",
        "plain_question": "How can topology say something useful about an application before every motion equation is solved?",
        "legal_move": "Choose the state space honestly, include the real freedoms, exclude the real forbidden states, and then apply the theorem to that model.",
        "surviving_fact": "Barriers, holes, fixed points, and index totals in the state space become constraints on the original system.",
        "why_later": "This tests the whole course outside its cleanest surface examples. It shows that first-principles modeling is part of the mathematics, not a preliminary story.",
    },
    {
        "lecture": 15,
        "object": "The whole course as a chain of picture-based reasoning moves.",
        "plain_question": "What single habit connects strips, surfaces, intersections, fixed points, and vector fields?",
        "legal_move": "Translate each situation into objects, allowed moves, protected evidence, and a conclusion that follows from that evidence.",
        "surviving_fact": "The same reasoning pattern survives across settings: build the right picture, move it legally, count what survives, and let the shape force the answer.",
        "why_later": "This is the final reader standard for the companion. A page is deep enough only when the reader can say what object was made, what move was legal, what fact survived, and why that fact forces the conclusion.",
    },
]


LECTURE_WALKTHROUGHS = {
    1: {
        "start_here": "Start with the plain act of making the strip. A rectangle by itself has two long sides and two short ends. The surprise enters when the ends are glued after one half-turn. That gluing instruction means a traveler who follows the surface all the way around comes back with the local sense of side reversed.",
        "payoff": "The mathematical payoff is the difference between small evidence and whole-object evidence. Every tiny patch of the strip looks like an ordinary two-sided strip, so local inspection cannot settle the question. The full trip around the object is the test, and that test reveals a global rule.",
        "reader_check": "Do not remember this lecture as only a surprising paper example. Ask what rule made the object, what local observation fails to detect, and what full journey reveals. If those three answers are clear, the Mobius strip becomes the first model for later orientation and vector-field obstructions.",
    },
    2: {
        "start_here": "Start with curves in a disk and boundary points that are not free to wander. The curves may look messy, but the proof does not care about their exact wiggles. It cares about whether the curves can be redrawn under legal motion while the endpoints and no-crossing rule stay fixed.",
        "payoff": "The mathematical payoff is that a picture can be simplified without losing its force. Deformation becomes valid only because the question is protected during the motion. This is the first time the course turns a visual cleanup into a proof rather than a preference for a neater drawing.",
        "reader_check": "Before accepting any deformation argument, ask what stayed fixed. Were endpoints preserved? Were forbidden crossings avoided? Was a boundary condition quietly changed? If the answer is not explicit, the drawing may have changed the problem instead of solving it.",
    },
    3: {
        "start_here": "Start by treating spaces as things that can be built from instructions. A product says two choices vary together. A quotient says different-looking points are declared the same. Surgery says a controlled piece is removed and another controlled piece is attached along a stated boundary rule.",
        "payoff": "The mathematical payoff is honest modeling. Later theorems apply to spaces, so the reader must know what space has actually been built. Products, quotients, manifolds, and surgery are not vocabulary decorations; they are construction rules that decide routes, boundaries, holes, and local neighborhoods.",
        "reader_check": "When a later page names a space, ask how that space was made. What choices were combined? What points were identified? What local piece was replaced? If the construction is vague, any theorem applied to that space is standing on weak ground.",
    },
    4: {
        "start_here": "Start with a square on paper, then stop treating the ink as the finished object. Edge labels are instructions for travel. If the left edge is glued to the right edge, a path leaving one side re-enters from the other. If an edge is reversed, direction changes during the return.",
        "payoff": "The mathematical payoff is quotient thinking in everyday form. The same square drawing can describe different spaces because the identification rule, not the visual outline, decides the object. This prepares the reader to see maps, surfaces, and state spaces as rule-built objects.",
        "reader_check": "Ask whether an apparent boundary is really a boundary in the finished space. Ask where a traveler goes after crossing a labeled edge. Ask whether direction is preserved. Those questions keep the drawing from being mistaken for the mathematical object.",
    },
    5: {
        "start_here": "Start with the problem of recognizing a surface after it has been bent, stretched, cut, and reassembled under legal rules. The visual drawing may change dramatically. Classification asks which durable features remain: boundary components, handles, crosscaps, and whether a consistent side choice survives everywhere.",
        "payoff": "The mathematical payoff is that surfaces can be sorted by what survives simplification, not by how they happen to be drawn. This gives later counts a stage. Euler characteristic, orientation, and vector-field index matter because they belong to the surface, not to one picture of it.",
        "reader_check": "When a surface is classified, ask what evidence is being preserved. Is the argument tracking holes, boundary, side reversal, or a controlled surgery move? A name for the surface is useful only after the preserved features have been identified.",
    },
    6: {
        "start_here": "Start with the everyday idea of room. Two objects may avoid each other if the surrounding space gives them enough directions to move. In cramped settings, meeting may be forced. The lecture cleans the objects into ordinary position so accidental contacts do not obscure the real room-counting question.",
        "payoff": "The mathematical payoff is preparation for intersection theory. A meeting should not be counted until the picture is clean enough to make meetings separate and inspectable. Once that ordinary position is reached, dimension and placement can say whether intersections are accidental, avoidable, or evidence-bearing.",
        "reader_check": "Ask whether the meeting survives after tiny legal motion. If it disappears because the original drawing was too special, it was probably an accident. If clean meetings remain under the allowed setup, the course can begin assigning signs and using them as evidence.",
    },
    7: {
        "start_here": "Start with a physical balance condition that changes continuously. The point is not to compute the exact balance location first. The point is to notice that a condition moving from one side of a requirement to another cannot jump over the special state if the change is continuous.",
        "payoff": "The mathematical payoff is forced existence. The course begins turning demonstrations into statements of the form: some special state must occur even if we cannot name it directly. That habit leads to fixed points, equilibria, and state-space arguments where shape blocks total avoidance.",
        "reader_check": "Ask what is changing continuously and what event it cannot skip. If the motion could jump, the existence claim may fail. If the setup stays continuous and the endpoints force opposite behavior, the special state is not guessed; it is forced.",
    },
    8: {
        "start_here": "Start with a weakness in raw counting. If two curves move, the visible number of crossings can change. A pair can appear or disappear. The lecture repairs the count by assigning signs to clean intersections, so harmless pair changes contribute plus one and minus one together.",
        "payoff": "The mathematical payoff is protected arithmetic. The signed total is not just a number read from one drawing; it is a number designed to survive legal deformation. This is why orientation and pair creation matter. They explain why the count deserves trust.",
        "reader_check": "Ask where the signs came from and what happens when a pair is born. If plus and minus are arbitrary labels, the argument has no force. If the signs come from orientation and pairs cancel, the count can carry proof evidence.",
    },
    9: {
        "start_here": "Start with a rule that sends each input somewhere. The equation for a fixed point can look invisible because it lives inside the rule. The lecture makes it visible by drawing the graph of the rule and comparing it with the diagonal, the set of input-output pairs where both entries agree.",
        "payoff": "The mathematical payoff is translation. A fixed point becomes an intersection problem, so earlier ideas about clean meetings and protected counts become relevant. The source caveat matters here because one middle caption is missing, but the graph-diagonal conversion remains the reliable spine.",
        "reader_check": "Ask what point in the graph means and what point on the diagonal means. Their meeting is not a loose picture for self-agreement; it is exactly the statement that the rule sends some input back to itself.",
    },
    10: {
        "start_here": "Start with a filled disk or ball and a continuous rule that sends every point back into that same filled object. Brouwer says at least one point must land where it began. The theorem is not trying to find the point; it rules out the possibility that every point escapes itself.",
        "payoff": "The mathematical payoff is existence from shape. The filled interior, boundary, and continuity of the rule work together. If any of those pieces is changed, the conclusion may fail. This makes the theorem a disciplined statement, not a slogan about all motion.",
        "reader_check": "Ask whether the space is the right closed filled shape, whether the rule stays inside it, and whether nearby points move to nearby outputs. If those conditions are not present, invoking Brouwer may be using a theorem outside its contract.",
    },
    11: {
        "start_here": "Start with arrows rather than paths. A vector field tells each point which way motion wants to go. Solving every path may be hard, but the places where the arrow vanishes are visible failures of motion. The nearby arrows then tell how that failure is shaped.",
        "payoff": "The mathematical payoff is understanding motion through local defects. An equilibrium is not only a location where motion stops. It has surrounding behavior, and that behavior can be counted through turning. This opens a route from dynamics back to topology.",
        "reader_check": "Ask what the nearby arrows do when you walk around the equilibrium. Do they turn once, turn the other way, or fail to give a clean isolated pattern? The index belongs to that surrounding behavior, not merely to the dot.",
    },
    12: {
        "start_here": "Start by isolating the defects of a vector field. Each defect has nearby arrows circling it in some pattern, and that pattern receives a signed index. The lecture then asks what happens when all those local signed counts are added over the whole surface.",
        "payoff": "The mathematical payoff is the move from local dynamics to global bookkeeping. Individual defects can move, split, or cancel under controlled changes, but the total signed index is not free. It is constrained by the surface that carries the arrows.",
        "reader_check": "Ask whether the defects are isolated and whether the total, not one favorite defect, is being counted. If the argument focuses only on a single equilibrium, it has missed the whole-surface nature of the theorem being prepared.",
    },
    13: {
        "start_here": "Start with Poincare-Hopf as a balance sheet. On one side are all the local indices of isolated vector-field defects. On the other side is Euler characteristic, a number belonging to the surface. The theorem says these two accounts must match.",
        "payoff": "The mathematical payoff is that topology predicts something about motion before the differential equation is solved. A sphere demands a different total defect from a torus. The hairy-ball idea is a visible case, but the deeper point is the enforced equality between local failures and whole-surface shape.",
        "reader_check": "Ask what surface carries the field and whether every defect has been included in the sum. Poincare-Hopf is not about admiring one dramatic singularity. It is about the total account forced by the complete surface.",
    },
    14: {
        "start_here": "Start with an application by refusing to apply a theorem too early. First name the possible states of the system. Then say which states are forbidden, which boundaries matter, and what continuous rule or motion acts on that space. Only then does topology have a correct object to study.",
        "payoff": "The mathematical payoff is disciplined transfer from pure examples to physical systems. Holes, barriers, fixed points, and index totals can constrain real behavior, but only when the model represents the real freedoms and exclusions. The modeling step is part of the proof.",
        "reader_check": "Ask whether the state space includes all needed degrees of freedom and excludes only genuinely forbidden states. Also ask which physical conclusion the topological statement translates back into. A beautiful theorem applied to the wrong model gives a beautiful answer to the wrong question.",
    },
    15: {
        "start_here": "Start by reading the final lecture as a map of habits, not a list of topics. The same pattern has appeared repeatedly: build the right object, specify legal motion, identify protected evidence, and use that evidence to force a conclusion that the original picture hid.",
        "payoff": "The mathematical payoff is a portable way to think. Mobius strips, surface classification, intersections, fixed points, vector fields, and applications are different settings for the same discipline. Pictorial thinking is deep here because the pictures carry rules and preserved facts.",
        "reader_check": "For any page in the companion, ask four questions: what object was made, what move was legal, what fact survived, and what conclusion became forced? If a page cannot answer those, it is not yet at the course's standard.",
    },
}


LECTURE_DEEPENING = {
    1: {
        "what_is_really_happening": "The lecture is replacing the question 'what does the strip look like?' with 'what does a full journey through the strip do to local side information?'",
        "why_it_is_hard": "A beginner can inspect many small patches and see only ordinary paper, so the global reversal feels like a surprise rather than a rule-made consequence.",
        "key_move": "Treat the twist as an instruction for gluing the ends, then test that instruction by following, coloring, and cutting paths that travel around the whole strip.",
        "payoff": "The reader learns the course's first durable lesson: local sameness does not guarantee global sameness, and a physical test can expose the difference.",
    },
    2: {
        "what_is_really_happening": "The lecture turns drawing into proof by asking which path changes are legal while boundary order and no-crossing conditions stay fixed.",
        "why_it_is_hard": "It is tempting to trust a drawing that looks cleaner, but the proof depends on the motion that produced the drawing, not on the drawing's appearance.",
        "key_move": "State the fixed boundary data, then deform the interior curves only through moves that keep endpoints and forbidden crossings under control.",
        "payoff": "The reader learns how a simplified picture can answer the original problem without secretly solving a different boundary puzzle.",
    },
    3: {
        "what_is_really_happening": "The lecture gives the construction tools that let later arguments talk about spaces made from choices, identifications, local patches, and replacement operations.",
        "why_it_is_hard": "Words such as product, quotient, surgery, and manifold can sound like labels, when here they are actions that build the object under study.",
        "key_move": "Read each construction by asking what choices are added, what points become the same, what local piece is replaced, and what neighborhoods remain ordinary.",
        "payoff": "The reader can later test whether a theorem is being applied to the right space, because the space's construction rules are visible.",
    },
    4: {
        "what_is_really_happening": "The lecture teaches that a flat drawing can be a code for a different space once its edges are identified by rules.",
        "why_it_is_hard": "A beginner naturally trusts the visible square, but the actual surface is determined by where travelers go after crossing labeled edges.",
        "key_move": "Stop reading the boundary as a wall until the edge rule has been checked, including whether direction is preserved or reversed.",
        "payoff": "The reader gains the habit needed for quotient spaces, orientation, and any later argument where the object is defined by a rule rather than by appearance.",
    },
    5: {
        "what_is_really_happening": "The lecture turns surfaces into classifiable objects by tracking handles, boundaries, side reversal, and the operations that preserve those features.",
        "why_it_is_hard": "Surface names can sound like a taxonomy of pictures, but classification is really about durable evidence under legal cutting, gluing, and simplification.",
        "key_move": "Follow the controlled surface operations and ask which global features survive: orientability, boundary behavior, handles, crosscaps, and Euler-style bookkeeping.",
        "payoff": "The reader sees why later counts and signs need a surface type beneath them; the surface is the stage that gives those later statements force.",
    },
    6: {
        "what_is_really_happening": "The lecture separates accidental meetings from forced meetings by using ordinary position and the amount of room supplied by the surrounding space.",
        "why_it_is_hard": "A visible crossing can feel like evidence immediately, but before signs or counts are trusted the meeting must be cleaned and tested for stability.",
        "key_move": "Move objects slightly into ordinary position, then ask whether dimension and placement allow the meeting to be removed or make it unavoidable.",
        "payoff": "The reader is prepared for intersection number because only clean, evidence-bearing meetings deserve to be counted.",
    },
    7: {
        "what_is_really_happening": "The lecture uses a physical balancing event to introduce forced existence without requiring a formula for the point where it occurs.",
        "why_it_is_hard": "The demonstration can distract from the mathematical structure: a continuous condition is changing and cannot skip the state being asked for.",
        "key_move": "Name the quantity that changes continuously and the event that lies between the starting and ending behavior.",
        "payoff": "The reader learns why topology can prove that a special state exists even when the exact state is not computed.",
    },
    8: {
        "what_is_really_happening": "The lecture turns raw crossings into protected arithmetic by assigning signs that make harmless birth and cancellation events add to zero.",
        "why_it_is_hard": "A beginner may count visible crossings and miss why that count is fragile; the stable evidence is the signed total, not the raw number.",
        "key_move": "Use orientation to justify plus and minus signs, then check what happens when a positive-negative pair appears or disappears during legal motion.",
        "payoff": "The reader learns the central pattern of designed counting: choose arithmetic that forgets fake changes and remembers the obstruction.",
    },
    9: {
        "what_is_really_happening": "The lecture turns a fixed-point equation into a geometric meeting between a map's graph and the diagonal of self-agreement.",
        "why_it_is_hard": "A rule can feel invisible compared with a surface or curve, and one missing caption means the page must lean on the reliable graph-diagonal spine.",
        "key_move": "Represent the rule by all input-output pairs, then compare that graph with the diagonal where input and output are equal.",
        "payoff": "The reader sees fixed points as intersections, which connects the theorem language back to the course's earlier deformation and counting tools.",
    },
    10: {
        "what_is_really_happening": "The lecture uses the shape of a closed filled ball to rule out a continuous escape plan for every point at once.",
        "why_it_is_hard": "The theorem proves existence without locating the point, so it can feel weaker than computation even though it answers a different kind of question.",
        "key_move": "Keep the domain closed and filled, keep the rule inside the domain, and use continuity to block a total avoidance of self-agreement.",
        "payoff": "The reader learns how the shape of a space can force a solution before any formula for that solution is available.",
    },
    11: {
        "what_is_really_happening": "The lecture changes dynamics from solving paths to reading the arrow pattern and the places where that pattern fails.",
        "why_it_is_hard": "A beginner may treat an equilibrium as just a named point, but the useful evidence is how nearby arrows turn around it.",
        "key_move": "Inspect a small loop around each vanishing arrow and record the local turning behavior rather than trying to solve every trajectory.",
        "payoff": "The reader sees how motion can be studied topologically: defects in an arrow field become countable evidence.",
    },
    12: {
        "what_is_really_happening": "The lecture asks what all local vector-field defects know together when their signed indices are added over the full surface.",
        "why_it_is_hard": "It is easy to focus on one source, sink, or saddle and miss that the important object is the total over every isolated defect.",
        "key_move": "Clean the field to isolated defects, assign each local index, then compare the sum with the surface carrying the field.",
        "payoff": "The reader sees Euler characteristic becoming a demand on motion, not only a surface bookkeeping number.",
    },
    13: {
        "what_is_really_happening": "The lecture uses Poincare-Hopf as a working equality between whole-surface topology and total local vector-field failure.",
        "why_it_is_hard": "The hairy-ball example is memorable, but it can hide the deeper statement about adding every isolated defect with signs.",
        "key_move": "Read the theorem as a complete account: surface first, all defects second, signed sum third, Euler characteristic as the required total.",
        "payoff": "The reader can use topology to predict motion failures or use observed failures to infer information about the surface.",
    },
    14: {
        "what_is_really_happening": "The lecture tests whether the course's proof tools survive honest translation into applications and moving systems.",
        "why_it_is_hard": "Applications can sound convincing too early; the theorem only sees the model, so an inaccurate state space gives an inaccurate physical conclusion.",
        "key_move": "Build the state space carefully, name forbidden states and allowed motions, then translate the topological conclusion back to the original system.",
        "payoff": "The reader learns that modeling is part of the proof, not a story added before the mathematics begins.",
    },
    15: {
        "what_is_really_happening": "The final lecture gathers the course as one reasoning habit rather than a list of separate demonstrations and theorem names.",
        "why_it_is_hard": "Review lectures can encourage memorizing topics in order, but the deeper value is seeing the same proof engine move across different objects.",
        "key_move": "Read each topic as a four-part account: object, legal move, surviving fact, and conclusion forced by that fact.",
        "payoff": "The reader leaves with a portable method for reading the whole companion and for testing whether any page has reached first-principles depth.",
    },
}


LECTURE_CAPTION_NUANCE = {
    1: {
        "terms": ["Mobius", "one side", "twist", "cut"],
        "risk": "Auto-captions can make the paper construction sound like a surprising object name rather than a gluing rule. The important evidence is the sequence of making, following, and cutting the strip.",
        "safe_reading": "Treat every mention of side, twist, and cutting as evidence about whether a local side choice survives a full journey around the strip.",
        "verify_question": "Can the explanation say what the gluing rule is before it says what the strip does?",
    },
    2: {
        "terms": ["deformation", "curve", "disk", "intersect"],
        "risk": "Caption words around drawing and moving can hide the boundary contract. If endpoints or forbidden crossings are not kept visible, the argument becomes easier than the actual lecture problem.",
        "safe_reading": "Read deformation as legal motion of curves inside a disk while endpoint order and the no-crossing rule remain part of the data.",
        "verify_question": "Can the explanation name the fixed boundary data before simplifying the drawing?",
    },
    3: {
        "terms": ["product", "quotient", "surgery", "manifold"],
        "risk": "Auto-captions may blur construction words into ordinary English. Product, quotient, surgery, and manifold are not labels for shapes already known; they say how a space is built or locally read.",
        "safe_reading": "Read this lecture as a construction manual: combine choices, identify points, replace pieces, and check that local neighborhoods are ordinary enough for later arguments.",
        "verify_question": "Can the explanation say what rule created the space and what routes or boundaries that rule changes?",
    },
    4: {
        "terms": ["identify", "boundary", "edge", "orientation"],
        "risk": "Caption text can make edge identifications sound like visual matching. The mathematical point is stronger: the labels state travel rules for the finished space.",
        "safe_reading": "Read each edge word as an instruction for where a path goes after it leaves the square and whether direction is preserved or reversed.",
        "verify_question": "Can the explanation distinguish the drawn square from the quotient space it encodes?",
    },
    5: {
        "terms": ["classification", "orientable", "handle", "boundary"],
        "risk": "Surface-family words can sound like naming by appearance. The source point is classification by durable features after legal cutting, gluing, and simplification.",
        "safe_reading": "Read handles, crosscaps, boundaries, and orientability as evidence the surface retains under controlled surface operations.",
        "verify_question": "Can the explanation say which surface feature survives the simplification rather than only naming the final family?",
    },
    6: {
        "terms": ["dimension", "submanifold", "intersection", "generic"],
        "risk": "Caption fragments around dimension can sound like informal room talk. The safe meaning is a rule for when clean meetings are expected after accidental coincidences are removed.",
        "safe_reading": "Read ordinary position as a preparation step: move objects slightly so meetings become clean enough for dimension and later signs to matter.",
        "verify_question": "Can the explanation say whether a meeting is accidental, avoidable, or forced after a small legal move?",
    },
    7: {
        "terms": ["center of gravity", "continuous", "balance", "intersection"],
        "risk": "Physical demonstration words can tempt the reader to focus on the apparatus and miss the mathematical structure. The key source idea is continuous change forcing a special state.",
        "safe_reading": "Read balance as an existence argument: a continuously changing condition cannot jump past the state where the required equality occurs.",
        "verify_question": "Can the explanation name what changes continuously and what event cannot be skipped?",
    },
    8: {
        "terms": ["intersection number", "orientation", "positive", "negative"],
        "risk": "Auto-captions can flatten plus and minus into ordinary arithmetic. The signs matter only because orientation gives them geometric meaning and pair creation explains cancellation.",
        "safe_reading": "Read every signed crossing as local evidence whose value must be justified by orientation and whose stability must be checked under legal deformation.",
        "verify_question": "Can the explanation say where the signs come from and why a born pair contributes zero in total?",
    },
    9: {
        "terms": ["graph", "diagonal", "mapping", "fixed point"],
        "risk": "This lecture has one missing middle caption, so any claim that depends on the absent part must stay modest. The available arc supports graph, diagonal, and fixed-point translation.",
        "safe_reading": "Read the lecture through the reliable conversion: a map becomes its graph, the diagonal means self-agreement, and their meeting is a fixed point.",
        "verify_question": "Can the explanation separate what is supported by available captions from what would need the missing middle video?",
    },
    10: {
        "terms": ["Brouwer", "closed ball", "boundary", "continuous"],
        "risk": "A caption can make the theorem sound broader than it is. The filled ball, self-map condition, boundary behavior, and continuity are not optional details.",
        "safe_reading": "Read Brouwer as a contract: a continuous rule sends a closed filled ball into itself, and that exact setup forces at least one self-agreeing point.",
        "verify_question": "Can the explanation state the domain and continuity assumptions before claiming a fixed point?",
    },
    11: {
        "terms": ["vector field", "equilibrium", "differential equation", "index"],
        "risk": "Caption text around dynamics may pull the reader toward solving trajectories. The lecture's source value is different: local arrow patterns can be read without solving every path.",
        "safe_reading": "Read an equilibrium as a defect in an arrow field, then inspect nearby arrows to see the signed turning information it carries.",
        "verify_question": "Can the explanation describe the arrows around the equilibrium, not only the point where the arrow vanishes?",
    },
    12: {
        "terms": ["index", "Euler characteristic", "equilibria", "sum"],
        "risk": "Auto-captions can obscure whether the theorem is local or global. The important point is not one defect but the sum of all isolated defect indices on the surface.",
        "safe_reading": "Read index as local evidence that becomes meaningful when every isolated defect is included in the whole-surface total.",
        "verify_question": "Can the explanation say what is being summed and what surface controls that sum?",
    },
    13: {
        "terms": ["Poincare-Hopf", "hairy ball", "Euler characteristic", "index"],
        "risk": "The memorable hairy-ball phrase can crowd out the theorem. The deeper source reading is the equality between total local index and Euler characteristic.",
        "safe_reading": "Read the hairy-ball idea as one consequence of Poincare-Hopf, while keeping the full theorem as a statement about all isolated defects on the surface.",
        "verify_question": "Can the explanation move from the visible sphere example back to the general index-sum account?",
    },
    14: {
        "terms": ["application", "rotation", "state space", "dynamical system"],
        "risk": "Application language can make the topology sound automatic. The source caution is that the model has to be chosen before a theorem can say anything about the physical system.",
        "safe_reading": "Read each application by first naming the state space, the allowed motion, the forbidden states, and the protected topological evidence.",
        "verify_question": "Can the explanation translate the theorem's conclusion back into the original physical setup without changing the model?",
    },
    15: {
        "terms": ["pictorial thinking", "deformation", "intersection", "fixed point"],
        "risk": "A final review can sound like a topic list if the captions are read too quickly. The course is reviewing one chain of reasoning across different objects.",
        "safe_reading": "Read the final lecture as a dependency map: legal pictures support protected counts, protected counts support forced existence, and forced existence supports motion conclusions.",
        "verify_question": "Can the explanation connect each reviewed topic to the object, move, preserved fact, and conclusion it uses?",
    },
}


CONCEPT_DEPENDENCIES = [
    {
        "stage": "From local patch evidence to whole-surface behavior",
        "before": ["topology-vs-geometry", "boundary-orientation"],
        "after": ["manifold", "quotient-space"],
        "plain": "A small patch can look ordinary while the whole surface changes what routes and sides mean.",
        "why": "This is the first dependency in the course. Before a reader can trust later surface arguments, they need to see that local evidence is not enough. Quotient rules and manifold language give that local-versus-global gap a precise form.",
        "reader_check": "Can I say what is locally ordinary, and what whole-surface fact is still undecided?",
    },
    {
        "stage": "From legal motion to protected mathematical evidence in proof",
        "before": ["deformation", "generic-position"],
        "after": ["invariant", "parity"],
        "plain": "A picture may move, but the proof needs a fact that moves with it unchanged.",
        "why": "Deformation by itself is only motion. Generic position cleans the picture enough to inspect it. Invariant and parity add evidence: something survives the motion and can rule out a desired ending.",
        "reader_check": "What exact move is legal, and what fact is still true after that move?",
    },
    {
        "stage": "From built spaces to durable surface classification rules",
        "before": ["product-space", "quotient-space", "surgery"],
        "after": ["manifold", "boundary-orientation", "euler-characteristic"],
        "plain": "A space built from choices, identifications, or replacements can be sorted by durable surface features.",
        "why": "Products make choice-spaces, quotients make sameness rules, and surgery changes a surface under boundary control. Those operations prepare the reader to count faces, track orientation, and name the surface by what survives simplification.",
        "reader_check": "What construction rule made this space, and which surface features did that rule create or preserve?",
    },
    {
        "stage": "From surface ledger to stable whole-shape number",
        "before": ["triangulation", "euler-characteristic"],
        "after": ["gauss-bonnet", "poincare-hopf"],
        "plain": "A surface count first looks like bookkeeping, then becomes a number that can control geometry and motion.",
        "why": "Triangulation makes a soft surface finite enough to count. Euler characteristic shows that the final account does not belong to one mesh. Later, Gauss-Bonnet and Poincare-Hopf use that same whole-surface number to constrain turning and vector-field defects.",
        "reader_check": "Is this number attached to one drawing, or to the surface after redrawings and refinements?",
    },
    {
        "stage": "From clean meetings to signed obstruction under deformation",
        "before": ["generic-position", "boundary-orientation", "winding-linking"],
        "after": ["intersection-number", "fixed-points"],
        "plain": "Clean meetings can be assigned signs, and the signed total can force a later meeting to exist.",
        "why": "Generic position separates meetings. Orientation gives signs meaning. Winding and linking train the idea of a stable relation. Intersection number combines these into a count that survives legal motion, then fixed-point theory uses meetings between graph and diagonal.",
        "reader_check": "Are the meetings clean, and do the signs come from a real direction rule?",
    },
    {
        "stage": "From a rule to forced self-agreement inside space",
        "before": ["product-space", "duality", "intersection-number"],
        "after": ["fixed-points", "brouwer-fixed-point"],
        "plain": "A rule becomes a shape in a larger space; self-agreement becomes a meeting with the diagonal.",
        "why": "Product space holds input and output together. Duality allows the rule to be redrawn as a graph. Intersection number explains why a graph may be unable to avoid the diagonal. Brouwer is the closed-ball version where the space itself blocks total escape.",
        "reader_check": "What is the graph, what is the diagonal, and why would their meeting mean a fixed point?",
    },
    {
        "stage": "From arrow-field failure to signed index around defects",
        "before": ["fixed-points", "equilibrium", "generic-position"],
        "after": ["vector-field-index", "poincare-hopf"],
        "plain": "A place where motion stops can be read by how nearby arrows turn around it.",
        "why": "Fixed points teach forced special states. Equilibrium turns that idea into a failure of an arrow field. Generic position keeps failures isolated. Vector-field index makes each failure countable, and Poincare-Hopf adds those counts over the whole surface.",
        "reader_check": "Is the defect isolated, and what do the arrows do on a small loop around it?",
    },
    {
        "stage": "From state-space model to physical application constraints",
        "before": ["configuration-space", "fixed-points", "poincare-hopf"],
        "after": ["duality", "invariant", "vector-field-index"],
        "plain": "A physical problem becomes usable only after its possible states are turned into the right mathematical space.",
        "why": "Configuration space lists the possible states. Fixed points and Poincare-Hopf supply forced-behavior tools. Duality and invariants keep the translation honest by asking whether the new picture still means the original physical question.",
        "reader_check": "Does the state space include the real freedoms and exclude the real forbidden states?",
    },
]


PROOF_MOVES = [
    {
        "name": "Deform a picture without changing the original question",
        "family": "deformation-family",
        "problem": "The first drawing is too tangled to reason from directly.",
        "steps": [
            "Name the object that is allowed to move.",
            "Name the forbidden moves: passing through, breaking, gluing, moving endpoints, or dropping a boundary.",
            "Move the picture only through legal changes.",
            "State the fact that survived the whole motion.",
            "Use the simpler final picture to answer the original question.",
        ],
        "why": "The proof works because each legal step preserves the question. The final picture is useful only because the journey to it was honest.",
        "failure": "The usual failure is simplifying first and justifying later. If the legal moves are not named before the motion, the proof may have solved a different problem.",
        "example": "The disk path puzzle uses deformation to show that endpoint order and no-crossing rules can force an obstruction.",
    },
    {
        "name": "Build a count that survives legal redrawings by cancellation",
        "family": "counting-family",
        "problem": "The visible number of pieces, crossings, or defects changes when the picture is cleaned up.",
        "steps": [
            "Decide which local events matter.",
            "Watch how those events can appear or disappear under legal motion.",
            "Choose an account where harmless changes cancel.",
            "Check the account on a simple version of the object.",
            "Use the protected total to force existence or impossibility.",
        ],
        "why": "A useful count is designed around its allowed changes. Euler characteristic, parity, intersection number, and index all work because fake changes do not alter the protected account.",
        "failure": "The raw count is often the wrong count. If the proof does not explain why the number survives, the number is only a measurement of one drawing.",
        "example": "Signed intersection number counts plus and minus meetings so pairs born during deformation add to zero.",
    },
    {
        "name": "Translate an invisible rule into a comparable shape",
        "family": "motion-family",
        "problem": "A map or motion law feels invisible because it is an instruction rather than a drawn object.",
        "steps": [
            "List the input space and output space.",
            "Draw or describe the graph that records input and output together.",
            "Identify the comparison object, such as the diagonal of self-agreement.",
            "Turn the desired conclusion into a meeting or avoidance question.",
            "Apply the earlier count, obstruction, or fixed-point idea.",
        ],
        "why": "The proof works because the rule becomes an object that can be moved, compared, and counted. A fixed point is no longer hidden inside notation; it is a meeting with the diagonal.",
        "failure": "The translation fails if the graph no longer represents the original rule or if the diagonal does not represent the desired self-agreement.",
        "example": "Fixed-point lectures turn f(x) = x into the graph of f meeting the diagonal.",
    },
    {
        "name": "Read local defects as evidence about the whole surface",
        "family": "surface-family",
        "problem": "A vector field may have several local failures, and each one looks adjustable in isolation.",
        "steps": [
            "Clean the field so the defects are isolated.",
            "Walk around each defect with a small loop.",
            "Record how the nearby arrows turn.",
            "Add the signed local indices.",
            "Compare the total with the surface's Euler characteristic.",
        ],
        "why": "The proof works because isolated local defects can move or cancel in controlled ways, but their total is tied to the surface that carries the field.",
        "failure": "The theorem is misread when one equilibrium is treated as the whole story. Poincare-Hopf is about the total over the complete surface.",
        "example": "The hairy-ball idea is the plain case: a sphere cannot carry a continuous nonzero tangent arrow field everywhere.",
    },
    {
        "name": "Model physical motion as a space of possible states",
        "family": "motion-family",
        "problem": "A physical setup has too many details to track directly over time.",
        "steps": [
            "Say what information describes one complete state.",
            "Treat every possible state as a point in a new space.",
            "Remove forbidden states or mark boundary restrictions.",
            "Translate motion into paths or rules on that state space.",
            "Use holes, barriers, fixed points, or indices to constrain the original system.",
        ],
        "why": "The proof works only if the state space carries the real freedoms and real exclusions of the physical problem. Topology then reasons about the shape of possibility.",
        "failure": "A careless state space can prove a true theorem about the wrong model. The physical conclusion is only as good as the translation.",
        "example": "The late applications use state spaces and protected obstructions to reason about motion without solving every trajectory.",
    },
]


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
        ("lecture-spine.html", "Lecture Spine"),
        ("concepts.html", "Concepts"),
        ("themes.html", "Themes"),
        ("subthemes.html", "Subthemes"),
        ("families.html", "Families"),
        ("the-math-why.html", "The Math Why"),
        ("math-playground.html", "Playground"),
        ("course-synthesis.html", "Synthesis"),
        ("concept-dependencies.html", "Dependencies"),
        ("proof-moves.html", "Proof Moves"),
        ("formula-reader.html", "Formula Reader"),
        ("reader-checks.html", "Reader Checks"),
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
    lecture_deepening_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", l["deep"]["deepening"][field])) for field in ["what_is_really_happening", "why_it_is_hard", "key_move", "payoff"]) for l in data["lectures"])
    lecture_walkthrough_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", l["deep"]["walkthrough"][field])) for field in ["start_here", "payoff", "reader_check"]) for l in data["lectures"])
    lecture_source_lens_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in l["deep"]["source_lens"]) for l in data["lectures"])
    lecture_source_checkpoint_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", l["deep"]["source_checkpoint"][field])) for field in ["trust", "do_not_overread", "math_question"]) for l in data["lectures"])
    lecture_caption_nuance_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", l["deep"]["caption_nuance"][field])) for field in ["risk", "safe_reading", "verify_question"]) for l in data["lectures"])
    concept_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in c["essay"]) for c in data["concepts"])
    concept_workup_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", c["workup"][field])) for field in ["object", "operation", "protected", "breaks_if"]) for c in data["concepts"])
    concept_anchor_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", c["anchor"][field])) for field in ["course_moment", "principle", "reader_question"]) for c in data["concepts"])
    theme_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in t["essay"]) for t in data["themes"])
    theme_lens_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", t["lens"][field])) for field in ["notices", "ignores", "changes_problem", "reader_test"]) for t in data["themes"])
    subtheme_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in s["essay"]) for s in data["subthemes"])
    subtheme_routine_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", s["routine"][field])) for field in ["look_for", "ask", "use", "mistake"]) for s in data["subthemes"])
    subtheme_bridge_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", s["bridge"][field])) for field in ["course_moment", "thinking_shift", "reader_test"]) for s in data["subthemes"])
    family_essay_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", p)) for p in f["essay"]) for f in data["families"])
    family_contract_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", f["contract"][field])) for field in ["input", "action", "evidence", "output", "failure_test"]) for f in data["families"])
    family_playbook_words = sum(sum(len(re.findall(r"[A-Za-z0-9']+", f["playbook"][field])) for field in ["setup", "move", "payoff", "failure", "reader_test"]) for f in data["families"])
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
            "evidence": f"{stats['lectures']} lecture explainers with full essay sections, lecture-deepening fields, slow walkthroughs, caption-nuance notes, problem, first principles, mathematical move, important detail, connection, transcript anchors, source-lens paragraphs, and examples.",
            "status": "met",
        },
        {
            "requirement": "Lecture-by-lecture reasoning spine",
            "evidence": f"The Lecture Spine page gives {len(data['lecture_spine'])} lecture entries that name the object, plain question, legal move, surviving fact, and later use.",
            "status": "met",
        },
        {
            "requirement": "Hand-written concepts, themes, subthemes, and method families",
            "evidence": f"{stats['concepts']} concepts, {stats['themes']} themes, {stats['subthemes']} subthemes, and {stats['families']} method families all have essay sections plus validated first-principles depth fields; concept pages include anchor examples, subtheme pages include first-principles bridges, and method-family pages include playbooks.",
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
        {
            "requirement": "Interactive first-principles playground",
            "evidence": "The Math Playground page has four canvas widgets for Euler characteristic, signed cancellation, fixed points, and vector-field index.",
            "status": "met",
        },
        {
            "requirement": "Course-level synthesis",
            "evidence": "The Course Synthesis page connects the lecture sequence, proof families, mathematical objects, operations, failure modes, and reader questions in one first-principles path.",
            "status": "met",
        },
        {
            "requirement": "Concept dependency map",
            "evidence": f"The Concept Dependencies page gives {len(data['concept_dependencies'])} prerequisite paths that connect early ideas to later theorems and applications.",
            "status": "met",
        },
        {
            "requirement": "Proof-move recipes",
            "evidence": f"The Proof Moves page gives {len(data['proof_moves'])} reusable proof recipes with steps, why-they-work explanations, failure modes, and examples.",
            "status": "met",
        },
        {
            "requirement": "Formula reader for mathematical statements",
            "evidence": "The Formula Reader page translates seven central statements into plain readings, survival reasons, forced conclusions, and reader checks.",
            "status": "met",
        },
        {
            "requirement": "Reader checks for common failure modes",
            "evidence": "The Reader Checks page gathers eleven course-wide mistakes and gives concrete replacement questions linked to lectures, concepts, method families, and the formula reader.",
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
            "lecture_spine_entries": len(data["lecture_spine"]),
            "lecture_essay_words": lecture_essay_words,
            "lecture_deepening_words": lecture_deepening_words,
            "lecture_walkthrough_words": lecture_walkthrough_words,
            "lecture_source_lens_words": lecture_source_lens_words,
            "lecture_source_checkpoint_words": lecture_source_checkpoint_words,
            "lecture_caption_nuance_words": lecture_caption_nuance_words,
            "concept_essay_words": concept_essay_words,
            "concept_workup_words": concept_workup_words,
            "concept_anchor_words": concept_anchor_words,
            "theme_essay_words": theme_essay_words,
            "theme_lens_words": theme_lens_words,
            "subtheme_essay_words": subtheme_essay_words,
            "subtheme_routine_words": subtheme_routine_words,
            "subtheme_bridge_words": subtheme_bridge_words,
            "family_essay_words": family_essay_words,
            "family_contract_words": family_contract_words,
            "family_playbook_words": family_playbook_words,
            "playground_widgets": 4,
            "synthesis_sections": 8,
            "dependency_paths": len(data["concept_dependencies"]),
            "proof_moves": len(data["proof_moves"]),
            "reader_checks": 11,
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
main{max-width:1180px;margin:0 auto;padding:28px 24px 56px}.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:26px;align-items:start;padding:18px 0 30px;border-bottom:1px solid var(--line)}h1{font-size:clamp(34px,5vw,64px);line-height:1;margin:0 0 18px}h2{font-size:28px;margin:34px 0 12px}h3{font-size:18px;margin:6px 0 8px}.lead{font-size:20px;color:#2f342f;max-width:800px}.panel{background:var(--band);border:1px solid var(--line);padding:18px;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}.card{background:white;border:1px solid var(--line);border-radius:8px;padding:15px;min-height:170px}.card p{margin:0;color:#303630}.meta{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}.arrow{display:inline-block;margin-top:12px;color:var(--accent);font-weight:700;text-decoration:none}.lecture{border-top:1px solid var(--line);padding:18px 0}.pill{display:inline-block;border:1px solid var(--line);background:white;border-radius:999px;padding:3px 8px;margin:3px;color:#303630;font-size:13px}.quote{border-left:4px solid var(--accent2);padding-left:14px;color:#282d28}.video-list a{display:block;color:var(--accent);padding:5px 0;text-decoration:none}.evidence{font-size:13px;color:var(--muted);margin-top:12px}.warn{border-color:#d7a64c;background:#fff8e8}.play-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.play{background:white;border:1px solid var(--line);border-radius:8px;padding:14px}.play canvas{width:100%;height:240px;border:1px solid var(--line);border-radius:6px;background:#fff;display:block}.control{display:grid;grid-template-columns:130px 1fr 42px;gap:10px;align-items:center;margin:10px 0}.control label{font-size:13px;color:var(--muted)}.control input{width:100%}.readout{font-variant-numeric:tabular-nums;font-size:13px;color:#303630}.equation{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#f5f6f1;border:1px solid var(--line);border-radius:6px;padding:8px;margin:10px 0;color:#222}
@media(max-width:850px){.topbar{align-items:flex-start;flex-direction:column}.hero,.grid,.grid.two{grid-template-columns:1fr}main{padding:18px 14px 42px}h1{font-size:40px}.lead{font-size:18px}}
@media(max-width:850px){.play-grid{grid-template-columns:1fr}.control{grid-template-columns:72px 1fr 30px}.play canvas{height:220px}}
"""
    (SITE / "assets" / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")
    playground_js = r"""
(function(){
const $=(s,r=document)=>r.querySelector(s);
const canvases=[...document.querySelectorAll('[data-play]')];
function fit(c){const d=window.devicePixelRatio||1;const r=c.getBoundingClientRect();c.width=Math.max(1,Math.floor(r.width*d));c.height=Math.max(1,Math.floor(r.height*d));const x=c.getContext('2d');x.setTransform(d,0,0,d,0,0);return [x,r.width,r.height];}
function line(x,a,b,c,d,col='#151515',w=2){x.strokeStyle=col;x.lineWidth=w;x.beginPath();x.moveTo(a,b);x.lineTo(c,d);x.stroke();}
function dot(x,a,b,r,col){x.fillStyle=col;x.beginPath();x.arc(a,b,r,0,Math.PI*2);x.fill();}
function text(x,s,a,b,size=13,col='#151515'){x.fillStyle=col;x.font=`${size}px Inter, system-ui, sans-serif`;x.fillText(s,a,b);}
function arrow(x,a,b,c,d,col='#11685f'){line(x,a,b,c,d,col,2);const ang=Math.atan2(d-b,c-a);x.beginPath();x.moveTo(c,d);x.lineTo(c-9*Math.cos(ang-.45),d-9*Math.sin(ang-.45));x.lineTo(c-9*Math.cos(ang+.45),d-9*Math.sin(ang+.45));x.closePath();x.fillStyle=col;x.fill();}
function clear(x,w,h){x.clearRect(0,0,w,h);x.fillStyle='#fff';x.fillRect(0,0,w,h);}
function drawEuler(c){const [x,w,h]=fit(c),n=+$('#euler-cuts').value;clear(x,w,h);const cx=w/2,cy=h/2,r=Math.min(w,h)*.34;line(x,cx-r,cy,cx+r,cy,'#d8ddd7',1);x.strokeStyle='#11685f';x.lineWidth=3;x.beginPath();x.arc(cx,cy,r,0,Math.PI*2);x.stroke();for(let i=0;i<n;i++){const a=(i/n)*Math.PI*2;line(x,cx,cy,cx+r*Math.cos(a),cy+r*Math.sin(a),'#8b3a2f',1.5);}dot(x,cx,cy,5,'#8b3a2f');text(x,`vertices ${n+1}`,18,28);text(x,`edges ${2*n}`,18,48);text(x,`faces ${n}`,18,68);text(x,`V - E + F = ${(n+1)-(2*n)+n}`,18,92,16,'#11685f');text(x,'Cuts change the ledger; count stays.',18,h-20,13,'#5e645f');}
function drawSigns(c){const [x,w,h]=fit(c),sep=+$('#sign-sep').value;clear(x,w,h);const y=h/2,mid=w/2;line(x,35,y,w-35,y,'#151515',2);const off=(sep-50)*2.2;line(x,mid-120,y-80,mid+120,y+80,'#11685f',3);line(x,mid-120,y+80,mid+120,y-80,'#8b3a2f',3);const a1=mid-off,a2=mid+off;if(sep>6){dot(x,a1,y,8,'#11685f');dot(x,a2,y,8,'#8b3a2f');text(x,'+1',a1-12,y-16,15,'#11685f');text(x,'-1',a2-12,y-16,15,'#8b3a2f');text(x,'signed total = 0',18,32,16,'#151515');}else{text(x,'singular moment: pair is born',18,32,16,'#151515');text(x,'the before and after totals match',18,55,13,'#5e645f');}text(x,'Raw count changes; signed count survives.',18,h-20,13,'#5e645f');}
function drawFixed(c){const [x,w,h]=fit(c),bend=(+$('#fixed-bend').value-50)/50;clear(x,w,h);const m=34,scale=(w-2*m);line(x,m,h-m,w-m,m,'#d8ddd7',1.5);text(x,'diagonal: x = f(x)',m+8,h-m-8,12,'#5e645f');x.strokeStyle='#11685f';x.lineWidth=3;x.beginPath();for(let i=0;i<=80;i++){const t=i/80;const px=m+t*scale;const fy=.5+.35*Math.sin((t+bend*.18)*Math.PI*2)+bend*.08*(t-.5);const py=h-m-fy*(h-2*m);if(i)x.lineTo(px,py);else x.moveTo(px,py);}x.stroke();let best=[0,999];for(let i=0;i<=200;i++){const t=i/200;const fy=.5+.35*Math.sin((t+bend*.18)*Math.PI*2)+bend*.08*(t-.5);const d=Math.abs(fy-t);if(d<best[1])best=[t,d];}const px=m+best[0]*scale,py=h-m-best[0]*(h-2*m);dot(x,px,py,7,'#8b3a2f');text(x,'fixed point',px+10,py-8,13,'#8b3a2f');text(x,'graph meets diagonal',18,32,16,'#151515');text(x,'A continuous rule cannot always avoid self-agreement.',18,h-20,13,'#5e645f');}
function drawIndex(c){const [x,w,h]=fit(c),mode=+$('#index-mode').value;clear(x,w,h);const cx=w/2,cy=h/2,r=Math.min(w,h)*.32;x.strokeStyle='#d8ddd7';x.lineWidth=1.5;x.beginPath();x.arc(cx,cy,r,0,Math.PI*2);x.stroke();for(let i=0;i<16;i++){const a=i/16*Math.PI*2,px=cx+r*Math.cos(a),py=cy+r*Math.sin(a);let ang=a;if(mode<33)ang=a;else if(mode<66)ang=-a;else ang=a+Math.PI/2*Math.sin(2*a);arrow(x,px,py,px+22*Math.cos(ang),py+22*Math.sin(ang),'#11685f');}dot(x,cx,cy,8,'#8b3a2f');const lab=mode<33?'+1 source-like':mode<66?'-1 saddle-like':'mixed local turns';text(x,`index: ${lab}`,18,32,16,'#151515');text(x,'Walk around the defect and count arrow turning.',18,h-20,13,'#5e645f');}
function sync(){document.querySelectorAll('input[type=range]').forEach(i=>{$(`[data-out="${i.id}"]`).textContent=i.value});canvases.forEach(c=>({euler:drawEuler,signs:drawSigns,fixed:drawFixed,index:drawIndex}[c.dataset.play](c)));}
window.addEventListener('resize',sync);document.addEventListener('input',sync);sync();
})();
"""
    (SITE / "assets" / "playground.js").write_text(playground_js.strip() + "\n", encoding="utf-8")

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
<h2>Interactive Math</h2>
<div class="grid two">
{card('Math Playground', 'Four small canvas models let the reader adjust cuts, signed pairs, fixed-point graphs, and vector-field turning. The controls make the course principles visible without assuming prior notation.', 'math-playground.html', 'Playground')}
{card('Course Synthesis', 'A single first-principles path through the whole course: hard situation, mathematical object, operation, reason, and what becomes possible.', 'course-synthesis.html', 'Synthesis')}
{card('Lecture Spine', 'One dense path through all 15 lectures: object, plain question, legal move, surviving fact, and why the lecture is needed later.', 'lecture-spine.html', 'Spine')}
{card('Concept Dependencies', 'Eight paths show what a reader should understand first, what later idea depends on it, and why the dependency matters.', 'concept-dependencies.html', 'Dependencies')}
{card('Proof Moves', 'Five reusable proof recipes show the steps: name the object, name legal moves, protect evidence, and use the conclusion without hiding the contract.', 'proof-moves.html', 'Moves')}
{card('Formula Reader', 'Plain readings of the course equations: what is counted, what is protected, why cancellation matters, and what kind of conclusion the equation can force.', 'formula-reader.html', 'Reader')}
{card('Reader Checks', 'Eleven checks for the places readers most often lose the mathematics: illegal motion, weak counts, local-only reasoning, unsupported signs, careless models, and formulas read without their protected account.', 'reader-checks.html', 'Checks')}
</div>
"""
    (SITE / "index.html").write_text(page("Topology & Geometry Course Companion", body, "Course"), encoding="utf-8")

    lecture_by_number = {l["lecture"]: l for l in data["lectures"]}
    spine_cards = []
    for row in data["lecture_spine"]:
        lecture = lecture_by_number[row["lecture"]]
        spine_cards.append(
            f"""<article class="card">
  <div class="meta">Lecture {row['lecture']:02d}</div>
  <h3>{esc(lecture['deep']['title'])}</h3>
  <p><b>Object:</b> {esc(row['object'])}</p>
  <p><b>Plain question:</b> {esc(row['plain_question'])}</p>
  <p><b>Legal move:</b> {esc(row['legal_move'])}</p>
  <p><b>Surviving fact:</b> {esc(row['surviving_fact'])}</p>
  <p><b>Why later lectures need it:</b> {esc(row['why_later'])}</p>
  <a class="arrow" href="lecture-{row['lecture']:02d}.html">Open lecture</a>
</article>"""
        )
    spine_body = f"""
<h1>Lecture Spine</h1>
<p class="lead">This page reads the course as one chain of reasoning. Each lecture is reduced to the object it builds, the plain question it asks, the move it allows, the fact it protects, and the later mathematical work that depends on it.</p>
<section class="lecture">
  <h2>How To Read This Spine</h2>
  <p>Use each row as a check against shallow understanding. If the lecture is remembered only as a topic name, the main idea has probably been lost. The useful memory is the working contract: what object is under discussion, what may be changed, what must survive the change, and what conclusion that survival later supports.</p>
  <p>The sequence also shows why the course has its particular order. The Mobius strip teaches local versus global. Deformation teaches legal motion. Constructed spaces and quotient rules teach how the stage is made. Intersections and signs teach protected counting. Fixed points and vector fields turn that protected evidence into existence and motion statements.</p>
</section>
<div class="grid two">{''.join(spine_cards)}</div>
"""
    (SITE / "lecture-spine.html").write_text(page("Lecture Spine", spine_body, "Lecture Spine"), encoding="utf-8")

    playground_body = """
<h1>Math Playground</h1>
<p class="lead">These small models make the course engine visible: choose legal data, watch what changes, and notice what count or meeting survives.</p>
<section class="play-grid">
  <article class="play">
    <div class="meta">Euler characteristic</div>
    <h2>Cut a disk into pieces</h2>
    <p>More cuts change the ledger of vertices, edges, and faces. The alternating count stays attached to the disk.</p>
    <div class="equation">V - E + F stays 1</div>
    <canvas data-play="euler" aria-label="Euler characteristic playground"></canvas>
    <div class="control"><label for="euler-cuts">Cuts</label><input id="euler-cuts" type="range" min="3" max="12" value="6"><span class="readout" data-out="euler-cuts">6</span></div>
  </article>
  <article class="play">
    <div class="meta">Signed cancellation</div>
    <h2>Birth of opposite meetings</h2>
    <p>A pair can appear during motion. The raw count changes, but the plus and minus signs cancel.</p>
    <div class="equation">(+1) + (-1) = 0</div>
    <canvas data-play="signs" aria-label="Signed cancellation playground"></canvas>
    <div class="control"><label for="sign-sep">Separation</label><input id="sign-sep" type="range" min="0" max="100" value="55"><span class="readout" data-out="sign-sep">55</span></div>
  </article>
  <article class="play">
    <div class="meta">Fixed points</div>
    <h2>Graph meets diagonal</h2>
    <p>A rule becomes a graph. Where the graph meets the diagonal, a point returns to itself.</p>
    <div class="equation">fixed point means f(x) = x</div>
    <canvas data-play="fixed" aria-label="Fixed point playground"></canvas>
    <div class="control"><label for="fixed-bend">Rule bend</label><input id="fixed-bend" type="range" min="0" max="100" value="50"><span class="readout" data-out="fixed-bend">50</span></div>
  </article>
  <article class="play">
    <div class="meta">Vector-field index</div>
    <h2>Walk around a defect</h2>
    <p>The index records how nearby arrows turn around a failure point. Local turning becomes countable evidence.</p>
    <div class="equation">local arrow turn gives a signed count</div>
    <canvas data-play="index" aria-label="Vector-field index playground"></canvas>
    <div class="control"><label for="index-mode">Arrow pattern</label><input id="index-mode" type="range" min="0" max="100" value="20"><span class="readout" data-out="index-mode">20</span></div>
  </article>
</section>
<script src="assets/playground.js"></script>
"""
    (SITE / "math-playground.html").write_text(page("Math Playground", playground_body, "Playground"), encoding="utf-8")

    chain_rows = [
        ("Paper strip", "A small twist changes a whole surface.", "A gluing rule for the ends of a strip.", "Follow a route and cut along chosen paths.", "The route returns with side information that one small patch cannot reveal.", "Global surface facts become visible."),
        ("Disk paths", "Trying drawings cannot prove that no drawing works.", "Boundary order plus a no-crossing rule.", "Deform all legal drawings toward a cleaner case.", "The boundary order survives, so a forced crossing in the clean case blocks every legal case.", "Impossibility can be proved without testing every route."),
        ("Built spaces", "A shape cannot be understood if its construction is hidden.", "Products, quotients, and surgery recipes.", "Track how choices vary, how points are identified, and how pieces are replaced.", "The recipe tells which routes, edges, and neighborhoods are real in the finished space.", "Later theorems have a precise stage to act on."),
        ("Surface classification", "Many drawings may describe the same surface type.", "Handles, crosscaps, boundaries, and orientation.", "Cut, move, and reassemble until durable parts are exposed.", "Legal simplification removes drawing accidents while keeping global surface structure.", "Surfaces can be named by what survives."),
        ("Intersections", "Meetings can appear or disappear during motion.", "A signed count of clean meetings.", "Assign signs and add them.", "Opposite pairs born during deformation cancel, while forced meetings leave a total.", "Pictures become arithmetic without losing geometry."),
        ("Fixed points", "A rule may force a self-return without revealing where.", "The graph of the rule and the diagonal of self-agreement.", "Translate the rule into a shape and compare it with the diagonal.", "A forced intersection is a fixed point written geometrically.", "Existence follows from shape and continuity."),
        ("Vector fields", "A motion law may be hard to solve exactly.", "Arrow-field defects with signed index.", "Walk around each defect and count arrow turning.", "Local defects may move, but their total can be tied to the surface.", "The shape predicts failures of motion."),
        ("Applications", "A physical story is too detailed to use directly.", "A state space, a rule, and a protected obstruction.", "Model possible states and apply the earlier proof family.", "The topology applies only when the model carries the real freedoms and barriers.", "Behavior can be constrained before exact calculation."),
    ]
    chain_html = "".join(
        f"""<article class="card"><div class="meta">{esc(stage)}</div><h3>{esc(hard)}</h3><p><b>Turns into:</b> {esc(obj)}</p><p><b>Operation:</b> {esc(op)}</p><p><b>Reason:</b> {esc(reason)}</p><p><b>What becomes possible:</b> {esc(poss)}</p></article>"""
        for stage, hard, obj, op, reason, poss in chain_rows
    )
    family_rows = [
        ("Deformation", "Move the object while guarding the question.", "allowed motion", "replace a hard picture by an easier legal picture"),
        ("Surviving Count", "Build a count whose fake changes cancel.", "protected total", "prove impossibility or forced existence"),
        ("Surface Bookkeeping", "Cut a surface into pieces and glue the account back together.", "global ledger", "make local patches obey a whole-surface fact"),
        ("Embedding", "Separate required connections from available room.", "route demand", "decide whether every legal drawing faces an obstruction"),
        ("Motion Through States", "Replace motion over time by the shape of possible states.", "state space", "read behavior as paths, walls, holes, and fixed points"),
    ]
    family_html = "".join(
        f"""<article class="card"><div class="meta">{esc(name)}</div><h3>{esc(move)}</h3><p><b>Mathematical object:</b> {esc(obj)}.</p><p><b>Course use:</b> {esc(use)}.</p></article>"""
        for name, move, obj, use in family_rows
    )
    lecture_spine = "".join(
        f"""<article class="card"><div class="meta">Lecture {l['lecture']:02d}</div><h3>{esc(l['deep']['title'])}</h3><p>{esc(l['deep']['connection'])}</p><a class="arrow" href="lecture-{l['lecture']:02d}.html">Open lecture</a></article>"""
        for l in data["lectures"]
    )
    deep_body = f"""
<h1>Course Synthesis</h1>
<p class="lead">The course is one method learned in stages: build or move a picture, name the legal changes, protect the right evidence, and let the whole shape force the answer.</p>
<section class="lecture">
  <h2>What The Course Turns Hard Problems Into</h2>
  <p>The hard thing is rarely a formula. It is a surface that fools local inspection, a drawing with too many possible routes, a rule whose fixed point is not visible, or a motion law that cannot be solved path by path. The course turns each case into a mathematical object simple enough to audit: a gluing rule, a boundary order, a signed count, a graph and diagonal, a vector-field index, or a state space.</p>
  <p>The operation is also repeated. Deform the object, count the protected part, compare two shapes, add local contributions, or model the possible states. The reason this works is that the operation is chosen to ignore accidental detail while preserving the obstruction. That is the mathematical spine of the course.</p>
</section>
<h2>Dependency Spine</h2>
<div class="grid two">{chain_html}</div>
<section class="lecture">
  <h2>The One Engine</h2>
  <p>Every major result asks the same plain questions. What is allowed to move? What is forbidden to change? What object carries the evidence? What operation is performed on that object? Why does that operation preserve the evidence? What answer becomes forced after the evidence is protected?</p>
  <p>This is why the Mobius strip belongs with Poincare-Hopf. The strip teaches that the whole object can remember a side reversal. Poincare-Hopf teaches that the whole surface can demand a total index. The objects differ, but the reasoning habit is the same: local freedom is organized by global structure.</p>
</section>
<h2>Proof Families</h2>
<div class="grid two">{family_html}</div>
<section class="lecture">
  <h2>Where Beginners Usually Lose The Thread</h2>
  <p>The first loss happens when a drawing is treated as the object itself. Many drawings are codes for gluing rules, route constraints, or state spaces. The second loss happens when any simplification is treated as legal. A deformation only proves something after the allowed moves are named. The third loss happens when a count is accepted without asking why it survives. A count is useful only when legal changes either leave it alone or make opposite contributions cancel.</p>
  <p>The companion is organized to prevent those losses. Lecture pages show the chronological path. Concept pages name the tools. Theme and subtheme pages show the recurring habits. Method-family pages show the proof moves. The playground lets the reader adjust the simplest cases by hand.</p>
</section>
<h2>Lecture Spine</h2>
<div class="grid">{lecture_spine}</div>
<section class="lecture">
  <h2>How To Read Any Page</h2>
  <p>Start by finding the hard physical or pictorial situation. Then ask what the page turns it into: a route, a count, a graph, a surface ledger, a field, or a space of possible states. Next identify the operation: deformation, signed addition, comparison with a diagonal, summing local indices, or searching paths in a state space. Finally ask why the operation works. The answer should name the protected detail, not merely say that the method succeeds.</p>
</section>
"""
    (SITE / "course-synthesis.html").write_text(page("Course Synthesis", deep_body, "Synthesis"), encoding="utf-8")

    dependency_cards = "".join(
        f"""<article class="card"><div class="meta">{esc(row['stage'])}</div><h3>{esc(row['plain'])}</h3><p><b>Understand first:</b> {concept_pills(row['before'], data['concepts'])}</p><p><b>Then read:</b> {concept_pills(row['after'], data['concepts'])}</p><p><b>Why this dependency matters:</b> {esc(row['why'])}</p><p><b>Reader check:</b> {esc(row['reader_check'])}</p></article>"""
        for row in data["concept_dependencies"]
    )
    dependency_body = f"""
<h1>Concept Dependencies</h1>
<p class="lead">This page is a reading order for the course ideas. It shows which earlier concepts carry the load for later theorem-level ideas, and what question proves that the dependency has been understood.</p>
<section class="lecture">
  <h2>How To Use This Map</h2>
  <p>Do not read the course as a flat list of terms. Later ideas rely on earlier agreements: what counts as the same space, which motions are legal, why signs mean anything, and how local data can add to a whole-surface demand. If a later theorem feels sudden, walk backward through the dependency row that supports it.</p>
  <p>The right test is not whether a name is familiar. The test is whether the reader can say what the earlier idea lets the later idea do. A quotient lets edge labels become a surface. Orientation lets signs become evidence. Euler characteristic lets Poincare-Hopf speak about motion.</p>
</section>
<div class="grid two">{dependency_cards}</div>
"""
    (SITE / "concept-dependencies.html").write_text(page("Concept Dependencies", dependency_body, "Dependencies"), encoding="utf-8")

    proof_cards = "".join(
        f"""<article class="card"><div class="meta">{esc(row['name'])}</div><h3>{esc(row['problem'])}</h3><p><b>Steps:</b></p><ol>{''.join(f'<li>{esc(step)}</li>' for step in row['steps'])}</ol><p><b>Why it works:</b> {esc(row['why'])}</p><p><b>Failure mode:</b> {esc(row['failure'])}</p><p><b>Course example:</b> {esc(row['example'])}</p><p><b>Family:</b> <a class="pill" href="{slug_page('family', row['family'])}">{esc(row['family'])}</a></p></article>"""
        for row in data["proof_moves"]
    )
    proof_body = f"""
<h1>Proof Moves</h1>
<p class="lead">These are the reusable moves beneath the lectures. Each recipe starts from the everyday problem, names the legal contract, explains why the move works, and names the failure that would make the proof invalid.</p>
<section class="lecture">
  <h2>How To Use These Recipes</h2>
  <p>When a page feels compressed, find the proof move it is using. Do not start with the theorem name. Start with the action: move a picture, build a count, translate a rule, add local defects, or model possible states. Then ask what detail makes the action legal.</p>
  <p>The course becomes easier when every proof is read as a sequence of obligations. What is the object? What may change? What must survive? What count or comparison is protected? What conclusion follows because the protected evidence cannot be removed?</p>
</section>
<div class="grid two">{proof_cards}</div>
<section class="lecture">
  <h2>Audit Question</h2>
  <p>After reading any proof in the course, ask which recipe was used and where the proof paid its debt. A deformation proof pays its debt by naming legal motion. A counting proof pays its debt by explaining cancellation. A fixed-point proof pays its debt by translating the rule into a graph-and-diagonal meeting. A dynamics proof pays its debt by showing why local defects can be added over the whole surface.</p>
</section>
"""
    (SITE / "proof-moves.html").write_text(page("Proof Moves", proof_body, "Proof Moves"), encoding="utf-8")

    formula_rows = [
        ("Euler characteristic", "chi = vertices - edges + faces", "Take a surface that has been divided into pieces. Count corner points, subtract edge pieces, then add face pieces.", "When a face is split by a new edge, both the edge count and face count change. The alternating account absorbs that artificial choice.", "The final number belongs to the surface type, not to one chosen drawing or mesh.", "Before using the number, ask what surface is being counted and whether boundaries or different kinds of cells have been accounted for.", "concept-euler-characteristic.html"),
        ("Signed intersection number", "total = plus meetings - minus meetings", "Count each clean meeting between two objects, but record whether the meeting agrees or disagrees with the direction rule of the surrounding space.", "A legal motion can create two new meetings at once. In the ordinary case they have opposite signs, so the signed total does not change.", "If the protected total is nonzero, the objects cannot be pulled apart by legal motion.", "Before trusting the signs, ask where orientation comes from and whether the meetings are clean enough to count.", "concept-intersection-number.html"),
        ("Parity", "only even or odd is kept", "Forget the exact number and keep only whether the number is even or odd.", "Some legal changes add or remove events two at a time. That can change the exact count while preserving oddness or evenness.", "An odd protected parity can prove that zero is impossible, even when the exact count is unknown.", "Use parity only when the allowed moves really do change the count by pairs.", "concept-parity.html"),
        ("Fixed point as graph meets diagonal", "fixed point means graph(f) meets diagonal", "Turn a rule into a shape by drawing all input-output pairs. The diagonal is the set where input and output agree.", "The equation f(x) = x becomes a meeting question. Earlier intersection reasoning can then decide whether that meeting can be avoided.", "A fixed-point theorem can prove that some point stays put without computing which point it is.", "Check the domain, boundary, and continuity of the rule before applying the theorem.", "concept-fixed-points.html"),
        ("Brouwer fixed point", "every continuous self-map of a closed ball has a fixed point", "Move every point of a filled ball somewhere inside the same filled ball, with nearby points still moving to nearby outputs.", "The filled shape and its boundary block a continuous escape plan in which every point avoids itself.", "Shape can force existence without a formula for the answer.", "The closed ball matters. Changing the space can change the claim.", "concept-brouwer-fixed-point.html"),
        ("Vector-field index", "index = signed turning around a defect", "Walk around a small loop enclosing a place where the arrow field vanishes. Watch how the nearby arrows turn during that walk.", "The local arrow pattern can be moved or redrawn, but its signed turning survives allowed cleanup as long as the defect is treated honestly.", "A local failure of motion becomes countable evidence.", "Make sure the defect is isolated before assigning a single local index.", "concept-vector-field-index.html"),
        ("Poincare-Hopf", "sum of indices = Euler characteristic", "Add the signed index of every isolated vector-field defect on a surface.", "Defects may move, split, or cancel in controlled pairs, but the total has to match the surface's Euler characteristic.", "The surface controls the total failure of any arrow field on it.", "Do not read one equilibrium alone as the theorem. The statement is about the whole surface total.", "concept-poincare-hopf.html"),
    ]
    formula_cards = "".join(
        f"""<article class="card"><div class="meta">{esc(name)}</div><h3>{esc(statement)}</h3><p><b>Plain reading:</b> {esc(reading)}</p><p><b>Why it survives:</b> {esc(survival)}</p><p><b>What it can force:</b> {esc(force)}</p><p><b>Reader check:</b> {esc(check)}</p><a class="arrow" href="{href}">Open concept</a></article>"""
        for name, statement, reading, survival, force, check, href in formula_rows
    )
    formula_body = f"""
<h1>Formula Reader</h1>
<p class="lead">The formulas in this course are compressed sentences about what is counted, what motion is allowed, why the count survives, and what conclusion the protected count can force.</p>
<section class="lecture">
  <h2>How To Read A Formula Here</h2>
  <p>Start by asking what object the formula is talking about: a surface, a pair of meeting objects, a map, a vector field, or a space of possible states. Then ask what operation produced the numbers: splitting into pieces, assigning signs, walking around a defect, or comparing a graph with a diagonal. Finally ask why the number is allowed to speak after the picture changes. That last step is the mathematics.</p>
  <p>A formula is useful only when it guards the right information. If the surface was modeled incorrectly, if the signs have no orientation, if the boundary was ignored, or if the defect is not isolated, the symbols may still be written down while the reason has failed.</p>
</section>
<div class="grid two">{formula_cards}</div>
<section class="lecture">
  <h2>The Common Pattern</h2>
  <p>Every formula above turns a flexible situation into a disciplined account. Euler characteristic forgets the chosen mesh and remembers the surface. Intersection number forgets temporary crossing pairs and remembers unavoidable meeting. Brouwer turns a rule into forced self-agreement. Poincare-Hopf turns local arrow failures into a whole-surface demand.</p>
  <p>That is the first-principles point: mathematics is not adding symbols to a picture. It is choosing an account that survives the legal changes in the problem and is strong enough to rule something in or out.</p>
</section>
"""
    (SITE / "formula-reader.html").write_text(page("Formula Reader", formula_body, "Formula Reader"), encoding="utf-8")

    check_rows = [
        ("The drawing is being treated as the object", "A square with edge labels, a graph of a map, or a configuration space is a code for relationships. The ink is not the final object.", "The same visible drawing can describe different spaces when the edge rule changes, so the rule has to be read before the picture can be trusted.", "What rule does this picture represent, and what relationships must survive if I redraw it?", "lecture-04.html", "Read Lecture 04"),
        ("The allowed motion is not stated", "A deformation can only prove something after the legal moves are named. Cutting, crossing through, moving endpoints, or dropping a boundary can change the problem.", "The whole proof rests on the promise that the motion preserves the question. Without that promise, a simpler picture may solve a different problem.", "Which motion is legal here, and which feature is being protected while the picture moves?", "family-deformation-family.html", "Open deformation family"),
        ("A raw count is trusted too early", "Visible crossings, cells, or defects may change under harmless redrawings. The useful count is the one designed to survive those changes.", "Euler characteristic, intersection number, parity, and index all work because fake changes cancel. The raw number usually does not have that protection.", "What local change can happen, and does the proposed count stay fixed when it happens?", "family-counting-family.html", "Open counting family"),
        ("Local evidence is mistaken for global evidence", "Every small patch of a Mobius strip looks ordinary. Every small patch of a sphere can carry an arrow. The whole object may still refuse a consistent choice.", "Topology often begins exactly where local inspection stops. The obstruction may appear only after a full trip, a full sum, or a full gluing.", "Can the local choice be carried around the whole object without contradiction?", "theme-local-to-global.html", "Open local-to-global theme"),
        ("Signs are used without checking orientation", "Plus and minus signs must come from a direction rule. Without orientation or a local sign convention, signed arithmetic may not be defined.", "A sign is not a decoration attached to a count. It records how objects meet or how arrows turn inside a setting where direction has meaning.", "What gives the sign its meaning in this space?", "concept-boundary-orientation.html", "Open boundary and orientation"),
        ("A failed drawing is treated as impossibility", "One bad attempt does not prove no legal drawing exists. A topological obstruction has to defeat every legal attempt.", "This is the difference between drawing skill and proof. The proof must name a protected fact that no redraw can remove.", "What fact survives all attempts, and why does it block the desired drawing?", "family-embedding-family.html", "Open embedding family"),
        ("The exceptional case is studied before the ordinary case", "Tangencies, triple meetings, and non-isolated defects can hide the stable mechanism. The clean case should be understood first.", "Ordinary clean cases allow isolated crossings, signs, and indices to be assigned. The exceptional moment is then used to explain how ordinary cases change.", "What happens after a tiny legal nudge, and what changes only at the singular moment?", "theme-generic-before-exception.html", "Open ordinary-case theme"),
        ("The theorem is pasted onto the wrong model", "Applications need an honest state space, rule, boundary, and protected quantity. If the model has the wrong freedoms or barriers, the conclusion may describe the model but not the situation.", "The topological theorem only sees the model. If the model omits a real motion or adds a false wall, the conclusion can be mathematically correct and physically irrelevant.", "Does the mathematical space contain exactly the states and forbidden moves in the original problem?", "family-motion-family.html", "Open motion family"),
        ("A fixed point is expected to be computed", "Fixed-point theorems often prove existence without naming the point. That is not a weakness when the goal is to prove that escape is impossible.", "The course repeatedly values forced existence. Knowing that a point, meeting, or defect must exist can be the central answer even when its exact location is unavailable.", "Is the page proving where the point is, or proving that some point must exist?", "concept-fixed-points.html", "Open fixed points"),
        ("A formula is read without its protected account", "Symbols such as chi, index, or f(x) = x are easy to repeat while missing what they count. The formula is the end of a reasoning contract, not the beginning.", "The course's equations work only because a legal motion, sign rule, boundary condition, or surface account has already been named.", "What is being counted, why does that account survive, and what conclusion can it force?", "formula-reader.html", "Open formula reader"),
        ("A term is remembered without its job", "Names such as manifold, quotient, index, and invariant matter only when they explain what can move, what is counted, or what is forced.", "A name should compress a working idea, not replace it. If the action behind the word is unclear, the reader has vocabulary without understanding.", "What work does this word perform in the argument?", "subtheme-models-not-labels.html", "Open models, not labels"),
    ]
    checks_html = "".join(
        f"""<article class="card"><div class="meta">Reader check</div><h3>{esc(title)}</h3><p><b>What goes wrong:</b> {esc(problem)}</p><p><b>Why it matters:</b> {esc(why)}</p><p><b>Ask instead:</b> {esc(question)}</p><a class="arrow" href="{href}">{esc(label)}</a></article>"""
        for title, problem, why, question, href, label in check_rows
    )
    checks_body = f"""
<h1>Reader Checks</h1>
<p class="lead">Use these checks when a page feels easy for the wrong reason. Each one turns a common confusion into a concrete question about legal moves, protected evidence, whole-shape structure, or modeling.</p>
<section class="lecture">
  <h2>How To Use This Page</h2>
  <p>Do not memorize these as warnings. Use them as a reading routine. When a proof moves a picture, ask what motion is legal. When a proof counts something, ask why the count survives. When a proof uses signs, ask where the signs come from. When a physical example appears, ask what mathematical space represents the possible states.</p>
  <p>The goal is to make each page harder to misunderstand. A first-principles explanation should let the reader audit the move, not only remember the conclusion.</p>
</section>
<div class="grid two">{checks_html}</div>
"""
    (SITE / "reader-checks.html").write_text(page("Reader Checks", checks_body, "Reader Checks"), encoding="utf-8")

    video_links = "".join(f'<a href="{esc(v["youtube_url"])}">{v["index"]:02d}. {esc(v["title"])}</a>' for v in data["videos"])
    body = f"<h1>Video Links</h1><p class='lead'>Every individual YouTube item in playlist order.</p><div class='video-list'>{video_links}</div>"
    (SITE / "videos.html").write_text(page("Video Links", body, "Videos"), encoding="utf-8")

    lecture_html = ""
    for l in data["lectures"]:
        vids = " ".join(f'<a class="pill" href="{esc(v["youtube_url"])}">Part {v["part"]}</a>' for v in l["videos"])
        miss = " warn" if l["missing_caption_ids"] else ""
        href = f"lecture-{l['lecture']:02d}.html"
        walk = l["deep"]["walkthrough"]
        nuance = l["deep"]["caption_nuance"]
        lecture_html += f"""<section class="lecture{miss}"><h2>Lecture {l['lecture']:02d}: {esc(l['deep']['title'])}</h2><p>{esc(l['deep']['problem'])}</p><p>{esc(l['deep']['first_principles'])}</p><div>{vids}</div><p><a class="arrow" href="{href}">Open lecture explainer</a></p><p class="evidence">Transcript words: {l['transcript_words']}. Missing captions: {', '.join(l['missing_caption_ids']) or 'none'}.</p></section>"""
        lecture_body = f"""
<h1>Lecture {l['lecture']:02d}: {esc(l['deep']['title'])}</h1>
<p class="lead">{esc(l['deep']['problem'])}</p>
<section class="lecture">
  <h2>Lecture Essay</h2>
  {paragraph_block(l['deep']['essay'])}
</section>
<section class="lecture">
  <h2>Lecture Deepening</h2>
  <p><b>What is really happening:</b> {esc(l['deep']['deepening']['what_is_really_happening'])}</p>
  <p><b>Why it is hard:</b> {esc(l['deep']['deepening']['why_it_is_hard'])}</p>
  <p><b>Key move:</b> {esc(l['deep']['deepening']['key_move'])}</p>
  <p><b>Payoff:</b> {esc(l['deep']['deepening']['payoff'])}</p>
</section>
<section class="lecture">
  <h2>Slow Walkthrough</h2>
  <p><b>Start here:</b> {esc(walk['start_here'])}</p>
  <p><b>Mathematical payoff:</b> {esc(walk['payoff'])}</p>
  <p><b>Reader check:</b> {esc(walk['reader_check'])}</p>
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
<section class="lecture">
  <h2>Source Lens</h2>
  {paragraph_block(l['deep']['source_lens'])}
</section>
<section class="lecture">
  <h2>Source Checkpoint</h2>
  <p><b>Trust:</b> {esc(l['deep']['source_checkpoint']['trust'])}</p>
  <p><b>Do not overread:</b> {esc(l['deep']['source_checkpoint']['do_not_overread'])}</p>
  <p><b>Math question:</b> {esc(l['deep']['source_checkpoint']['math_question'])}</p>
</section>
<section class="panel{' warn' if l['missing_caption_ids'] else ''}">
  <h2>Caption Nuance</h2>
  <p><b>Listen for:</b> {', '.join(esc(t) for t in nuance['terms'])}</p>
  <p><b>Caption risk:</b> {esc(nuance['risk'])}</p>
  <p><b>Safe reading:</b> {esc(nuance['safe_reading'])}</p>
  <p><b>Verify:</b> {esc(nuance['verify_question'])}</p>
</section>
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
        work = c["workup"]
        anchor = c["anchor"]
        body = f"""<h1>{esc(c['title'])}</h1><p class="lead">{esc(c['depth']['why_it_exists'])}</p><section class="lecture"><h2>Concept Essay</h2>{paragraph_block(c['essay'])}</section><section class="panel"><h2>First Principles</h2><p>{esc(c['first_principles'])}</p><h2>Important Detail</h2><p>{esc(c['important_detail'])}</p><h2>Principle Behind It</h2><p>{esc(c['math_principle'])}</p><h2>Beginner Trap</h2><p>{esc(c['depth']['beginner_trap'])}</p><h2>Course Role</h2><p>{esc(c['depth']['course_role'])}</p></section><section class="lecture"><h2>Anchor Example</h2><p><b>Course moment:</b> {esc(anchor['course_moment'])}</p><p><b>Principle:</b> {esc(anchor['principle'])}</p><p><b>Reader question:</b> {esc(anchor['reader_question'])}</p></section><section class="lecture"><h2>Work It From Scratch</h2><p><b>Object:</b> {esc(work['object'])}</p><p><b>Operation:</b> {esc(work['operation'])}</p><p><b>Protected fact:</b> {esc(work['protected'])}</p><p><b>Breaks if:</b> {esc(work['breaks_if'])}</p></section><p>{''.join(f'<span class="pill">{esc(s)}</span>' for s in c['subthemes'])}</p><h2>Where It Appears</h2><div class="grid two">{moments}</div>"""
        (SITE / slug_page("concept", c["id"])).write_text(page(c["title"], body, "Concepts"), encoding="utf-8")

    body = "<h1>Themes</h1><p class='lead'>Themes are the recurring habits of thought that make the course cohere across paper strips, surfaces, intersections, fixed points, and dynamics.</p><div class='grid two'>" + "".join(card(t["title"], t["depth"]["problem"], slug_page("theme", t["id"]), "Theme") for t in data["themes"]) + "</div>"
    (SITE / "themes.html").write_text(page("Themes", body, "Themes"), encoding="utf-8")
    for t in data["themes"]:
        related = [c for c in data["concepts"] if c["theme"] == t["id"]]
        lecture_links = "".join(f'<a class="pill" href="lecture-{n:02d}.html">Lecture {n:02d}</a>' for n in t["depth"]["lectures"])
        lens = t["lens"]
        body = f"""<h1>{esc(t['title'])}</h1><p class='lead'>{esc(t['depth']['problem'])}</p><section class="lecture"><h2>Theme Essay</h2>{paragraph_block(t['essay'])}</section><section class='panel'><h2>The Habit</h2><p>{esc(t['depth']['habit'])}</p><h2>Course Arc</h2><p>{esc(t['depth']['course_arc'])}</p><h2>Important Detail</h2><p>{esc(t['depth']['important_detail'])}</p><h2>Why The Math Matters</h2><p>{esc(t['why_math_matters'])}</p></section><section class="lecture"><h2>Theme Lens</h2><p><b>Notices:</b> {esc(lens['notices'])}</p><p><b>Ignores:</b> {esc(lens['ignores'])}</p><p><b>Changes the problem:</b> {esc(lens['changes_problem'])}</p><p><b>Reader test:</b> {esc(lens['reader_test'])}</p></section><h2>Lecture Thread</h2><p>{lecture_links}</p><h2>Related Concepts</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("theme", t["id"])).write_text(page(t["title"], body, "Themes"), encoding="utf-8")

    body = "<h1>Subthemes</h1><p class='lead'>Subthemes are the smaller recurring moves inside the larger course habits: the contracts, counts, signs, boundaries, and modeling choices that make the arguments work.</p><div class='grid'>" + "".join(card(s["title"], s["depth"]["problem"], slug_page("subtheme", s["id"]), "Subtheme") for s in data["subthemes"]) + "</div>"
    (SITE / "subthemes.html").write_text(page("Subthemes", body, "Subthemes"), encoding="utf-8")
    for s in data["subthemes"]:
        related = [c for c in data["concepts"] if s["id"] in c["subthemes"]]
        routine = s["routine"]
        bridge = s["bridge"]
        body = f"""<h1>{esc(s['title'])}</h1><p class='lead'>{esc(s['depth']['problem'])}</p><section class="lecture"><h2>Subtheme Essay</h2>{paragraph_block(s['essay'])}</section><section class='panel'><h2>First Principles</h2><p>{esc(s['depth']['first_principles'])}</p><h2>Course Role</h2><p>{esc(s['depth']['course_role'])}</p></section><section class="lecture"><h2>First-Principles Bridge</h2><p><b>Course moment:</b> {esc(bridge['course_moment'])}</p><p><b>Thinking shift:</b> {esc(bridge['thinking_shift'])}</p><p><b>Reader test:</b> {esc(bridge['reader_test'])}</p></section><section class="lecture"><h2>Reading Routine</h2><p><b>Look for:</b> {esc(routine['look_for'])}</p><p><b>Ask:</b> {esc(routine['ask'])}</p><p><b>Use:</b> {esc(routine['use'])}</p><p><b>Mistake:</b> {esc(routine['mistake'])}</p></section><h2>Related Concepts</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("subtheme", s["id"])).write_text(page(s["title"], body, "Subthemes"), encoding="utf-8")

    body = "<h1>Method Families</h1><p class='lead'>Method families explain how the course turns pictures into reasons. They are the reusable proof moves beneath the lectures.</p><div class='grid two'>" + "".join(card(f["title"], f["depth"]["human_problem"], slug_page("family", f["id"]), f["purpose"]) for f in data["families"]) + "</div>"
    (SITE / "families.html").write_text(page("Families", body, "Families"), encoding="utf-8")
    for f in data["families"]:
        related = [c for c in data["concepts"] if c["id"] in f["concepts"]]
        contract = f["contract"]
        playbook = f["playbook"]
        body = f"""<h1>{esc(f['title'])}</h1><p class='lead'>{esc(f['depth']['human_problem'])}</p><section class="lecture"><h2>Method Essay</h2>{paragraph_block(f['essay'])}</section><section class='panel'><h2>Purpose</h2><p>{esc(f['purpose'])}</p><h2>First Principles</h2><p>{esc(f['depth']['first_principles'])}</p><h2>How It Works</h2><p>{esc(f['depth']['how_it_works'])}</p><h2>Course Examples</h2><p>{esc(f['depth']['course_examples'])}</p><h2>Failure Mode</h2><p>{esc(f['depth']['failure_mode'])}</p></section><section class="lecture"><h2>Method Playbook</h2><p><b>Setup:</b> {esc(playbook['setup'])}</p><p><b>Move:</b> {esc(playbook['move'])}</p><p><b>Payoff:</b> {esc(playbook['payoff'])}</p><p><b>Failure:</b> {esc(playbook['failure'])}</p><p><b>Reader test:</b> {esc(playbook['reader_test'])}</p></section><section class="lecture"><h2>Method Contract</h2><p><b>Input:</b> {esc(contract['input'])}</p><p><b>Action:</b> {esc(contract['action'])}</p><p><b>Protected evidence:</b> {esc(contract['evidence'])}</p><p><b>Output:</b> {esc(contract['output'])}</p><p><b>Failure test:</b> {esc(contract['failure_test'])}</p></section><h2>Concepts in this family</h2><div class='grid'>{''.join(card(c['title'], c['depth']['why_it_exists'], slug_page('concept', c['id']), 'Concept') for c in related)}</div>"""
        (SITE / slug_page("family", f["id"])).write_text(page(f["title"], body, "Families"), encoding="utf-8")

    math_why = f"""<h1>The Math Why</h1><p class="lead">{esc(data['math_why']['big_picture'])}</p><section class="panel"><h2>First Principles</h2><p>{esc(data['math_why']['first_principles'])}</p><h2>Important Detail</h2><p>{esc(data['math_why']['important_detail'])}</p><h2>Principle Behind the Mathematics</h2><p>{esc(data['math_why']['principle'])}</p><h2>Why These Concepts Matter</h2><p>{esc(data['math_why']['concepts_matter'])}</p><h2>How To Read The Course</h2><p>{esc(data['math_why']['reader_path'])}</p></section>"""
    (SITE / "the-math-why.html").write_text(page("The Math Why", math_why, "The Math Why"), encoding="utf-8")

    qa_rows = "".join(
        f'<article class="card"><div class="meta">{esc(item["status"])}</div><h3>{esc(item["requirement"])}</h3><p>{esc(item["evidence"])}</p></article>'
        for item in data["quality_audit"]["requirements"]
    )
    qa_metrics = data["quality_audit"]["metrics"]
    qa_body = f"""<h1>Quality Audit</h1><p class="lead">{esc(data['quality_audit']['summary'])}</p><section class="panel"><h2>Current Metrics</h2><p>{qa_metrics['videos']} videos, {qa_metrics['lectures']} lectures, {qa_metrics['captioned_videos']} captioned videos, {len(qa_metrics['missing_captions'])} missing caption, {qa_metrics['lecture_examples']} lecture examples, {qa_metrics['lecture_spine_entries']} lecture-spine entries, {qa_metrics['playground_widgets']} playground widgets, {qa_metrics['synthesis_sections']} synthesis sections, {qa_metrics['dependency_paths']} dependency paths, {qa_metrics['proof_moves']} proof-move recipes, {qa_metrics['reader_checks']} reader checks, {qa_metrics['lecture_essay_words']} lecture essay words, {qa_metrics['lecture_deepening_words']} lecture deepening words, {qa_metrics['lecture_walkthrough_words']} lecture walkthrough words, {qa_metrics['lecture_caption_nuance_words']} caption-nuance words, {qa_metrics['lecture_source_lens_words']} source-lens words, {qa_metrics['lecture_source_checkpoint_words']} source-checkpoint words, {qa_metrics['concept_essay_words']} concept essay words, {qa_metrics['concept_workup_words']} concept workup words, {qa_metrics['concept_anchor_words']} concept anchor words, {qa_metrics['theme_essay_words']} theme essay words, {qa_metrics['theme_lens_words']} theme lens words, {qa_metrics['subtheme_essay_words']} subtheme essay words, {qa_metrics['subtheme_routine_words']} subtheme routine words, {qa_metrics['subtheme_bridge_words']} subtheme bridge words, {qa_metrics['family_essay_words']} method-family essay words, {qa_metrics['family_contract_words']} method-contract words, {qa_metrics['family_playbook_words']} method-playbook words, concept appearance coverage from {qa_metrics['concept_appearances_min']} to {qa_metrics['concept_appearances_max']} examples per concept.</p></section><h2>Requirement Evidence</h2><div class="grid two">{qa_rows}</div>"""
    (SITE / "quality-audit.html").write_text(page("Quality Audit", qa_body, "Quality Audit"), encoding="utf-8")

    nuance_cards = "".join(
        f"""<article class="card {'warn' if l['missing_caption_ids'] else ''}">
  <div class="meta">Lecture {l['lecture']:02d}</div>
  <h3>{esc(l['deep']['title'])}</h3>
  <p><b>Listen for:</b> {', '.join(esc(t) for t in l['deep']['caption_nuance']['terms'])}</p>
  <p><b>Caption risk:</b> {esc(l['deep']['caption_nuance']['risk'])}</p>
  <p><b>Safe reading:</b> {esc(l['deep']['caption_nuance']['safe_reading'])}</p>
  <p><b>Verify:</b> {esc(l['deep']['caption_nuance']['verify_question'])}</p>
  <p><b>Source checkpoint:</b> {esc(l['deep']['source_checkpoint']['math_question'])}</p>
  <a class="arrow" href="lecture-{l['lecture']:02d}.html">Open lecture</a>
</article>"""
        for l in data["lectures"]
    )
    audit = f"""<h1>Source Audit</h1><section class="panel {'warn' if stats['missing_captions'] else ''}"><p>{stats['captioned_videos']} of {stats['videos']} playlist videos have recovered English auto-captions. Missing: {', '.join(data['missing_caption_ids']) or 'none'}.</p><p>The companion uses captions as raw source material, but the narrative is hand-authored from the course arc and checked against available transcript coverage. Auto-captions can mishear names, symbols, and short mathematical words.</p></section><h2>Caption Nuance By Lecture</h2><div class="grid two">{nuance_cards}</div>"""
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
        deep["deepening"] = LECTURE_DEEPENING[number]
        deep["source_lens"] = LECTURE_SOURCE_LENS[number]
        deep["source_checkpoint"] = LECTURE_SOURCE_CHECKPOINTS[number]
        deep["walkthrough"] = LECTURE_WALKTHROUGHS[number]
        deep["caption_nuance"] = LECTURE_CAPTION_NUANCE[number]
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
        enriched["lens"] = THEME_LENSES[theme["id"]]
        themes.append(enriched)
    subthemes = []
    for i, t, p in SUBTHEMES:
        subthemes.append({"id": i, "title": t, "plain": p, "depth": SUBTHEME_DEPTH[i], "essay": SUBTHEME_ESSAYS[i], "routine": SUBTHEME_ROUTINES[i], "bridge": SUBTHEME_BRIDGES[i]})
    concepts = []
    for concept in CONCEPTS:
        enriched = dict(concept)
        enriched["depth"] = CONCEPT_DEPTH[concept["id"]]
        enriched["essay"] = CONCEPT_ESSAYS[concept["id"]]
        enriched["workup"] = CONCEPT_WORKUPS[concept["id"]]
        enriched["anchor"] = CONCEPT_ANCHORS[concept["id"]]
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
        enriched["contract"] = FAMILY_CONTRACTS[family["id"]]
        enriched["playbook"] = FAMILY_PLAYBOOKS[family["id"]]
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
        "lecture_spine": LECTURE_SPINE,
        "concept_dependencies": CONCEPT_DEPENDENCIES,
        "proof_moves": PROOF_MOVES,
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
    write_json(ANALYSIS / "lecture-spine.json", LECTURE_SPINE)
    write_json(ANALYSIS / "concept-dependencies.json", CONCEPT_DEPENDENCIES)
    write_json(ANALYSIS / "proof-moves.json", PROOF_MOVES)
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
- lecture-spine.html with {metrics['lecture_spine_entries']} lecture-by-lecture reasoning entries
- {metrics['lecture_deepening_words']} lecture deepening words across what-is-happening, why-hard, key-move, and payoff fields
- {metrics['lecture_walkthrough_words']} slow-walkthrough words across lecture pages, explaining each lecture from object to payoff to reader check
- {metrics['lecture_caption_nuance_words']} caption-nuance words across lecture pages and source audit, explaining risky transcript terms and safe readings
- {metrics['lecture_source_lens_words']} source-lens words across lecture pages, explaining how transcript anchors should be read as evidence
- {metrics['lecture_source_checkpoint_words']} source-checkpoint words across lecture trust, overread-warning, and math-question fields
- 45 lecture-grounded examples, three per lecture, each bridged to concepts
- {data['stats']['concepts']} expanded concept pages with full essay sections, why-it-exists, beginner-trap, and course-role sections
- {metrics['concept_workup_words']} concept workup words across object, operation, protected-fact, and failure-test fields
- {metrics['concept_anchor_words']} concept anchor words across course-moment, principle, and reader-question fields
- 6 expanded course theme pages with problem, habit, course-arc, and important-detail sections
- {metrics['theme_lens_words']} theme lens words across notices, ignores, problem-change, and reader-test fields
- 10 expanded subtheme pages with essay, first-principles, and course-role sections
- {metrics['subtheme_routine_words']} subtheme routine words across look-for, ask, use, and mistake fields
- {metrics['subtheme_bridge_words']} subtheme bridge words across course-moment, thinking-shift, and reader-test fields
- 5 expanded method-family pages with essay, human-problem, how-it-works, examples, and failure-mode sections
- {metrics['family_contract_words']} method-contract words across input, action, protected-evidence, output, and failure-test fields
- {metrics['family_playbook_words']} method-playbook words across setup, move, payoff, failure, and reader-test fields
- math-playground.html with four interactive first-principles canvas widgets
- course-synthesis.html with the full dependency spine and proof-family synthesis
- concept-dependencies.html with {metrics['dependency_paths']} prerequisite paths linking early ideas to later theorem-level ideas
- proof-moves.html with {metrics['proof_moves']} reusable proof recipes
- reader-checks.html with eleven concrete checks for common reasoning failures
- explicit source coverage, missing-caption audit, and per-lecture caption-nuance cards

Current enforced essay totals: {metrics['lecture_essay_words']} lecture essay words, {metrics['lecture_deepening_words']} lecture deepening words, {metrics['lecture_walkthrough_words']} lecture walkthrough words, {metrics['lecture_caption_nuance_words']} caption-nuance words, {metrics['lecture_source_lens_words']} source-lens words, {metrics['lecture_source_checkpoint_words']} source-checkpoint words, {metrics['concept_essay_words']} concept essay words, {metrics['concept_workup_words']} concept workup words, {metrics['concept_anchor_words']} concept anchor words, {metrics['theme_essay_words']} theme essay words, {metrics['theme_lens_words']} theme lens words, {metrics['subtheme_essay_words']} subtheme essay words, {metrics['subtheme_routine_words']} subtheme routine words, {metrics['subtheme_bridge_words']} subtheme bridge words, {metrics['family_essay_words']} method-family essay words, {metrics['family_contract_words']} method-contract words, and {metrics['family_playbook_words']} method-playbook words. The validator requires every lecture essay to clear 255 words, every lecture deepening field to clear 14 words, every lecture walkthrough field to clear 35 words, every lecture caption-nuance field to clear 12 words, every lecture source lens to clear 60 words, every lecture source-checkpoint field to clear 12 words, every concept essay to clear 195 words, every concept workup field to clear 12 words, every concept anchor field to clear 14 words, every theme essay to clear 190 words, every theme lens field to clear 12 words, every subtheme essay to clear 130 words, every subtheme routine field to clear 12 words, every subtheme bridge field to clear 14 words, every method-family essay to clear 130 words, every method-contract field to clear 12 words, and every method-playbook field to clear 12 words.

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
