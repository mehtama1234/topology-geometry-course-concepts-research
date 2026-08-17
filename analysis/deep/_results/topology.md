# Topology & Geometry — verified measured results (small programs that COMPUTE invariants)

Every number below is computed by a short program we ran. The recurring magic: a DISCRETE count
equals a CONTINUOUS invariant that does not change when you bend or re-cut the shape. Script:
scripts/experiments/topology_run.py. Cite numbers verbatim.

## EXP1 — Euler characteristic V - E + F, invariant under re-triangulation (concepts: euler-characteristic, triangulation, invariant, manifold)
- Count vertices (V), edges (E), faces (F) of each shape and take V - E + F:
  tetrahedron (4,6,4)=2; cube (8,12,6)=2; octahedron (6,12,8)=2; dodecahedron (20,30,12)=2;
  icosahedron (12,30,20)=2. All five are sphere-shaped -> all give **2**.
- A torus triangulation (7 vertices, 21 edges, 14 triangles) gives V - E + F = **0**.
- Insight: however you cut up a sphere the alternating count is always 2; a torus is always 0.
  The number depends only on the shape, not the mesh — that is what "topological invariant" means.

## EXP2 — genus and surgery: each handle lowers the count by 2 (concept: surgery)
- Surface with g handles (genus g): Euler characteristic = 2 - 2g. Computed: genus 0 -> 2,
  1 -> 0, 2 -> -2, 3 -> -4, 4 -> -6.
- Insight: adding a handle (a "surgery") subtracts exactly 2 every time, so the count secretly
  tells you how many holes a surface has.

## EXP3 — product spaces multiply (concept: product-space)
- The Euler characteristic of a product is the product of the parts: chi(A x B) = chi(A) x chi(B).
  Using chi(circle)=0, chi(interval)=1, chi(sphere)=2: circle x circle (a torus) = 0 x 0 = **0**;
  circle x interval (a cylinder) = 0; sphere x circle = 2 x 0 = **0**.
- Insight: build a bigger space by pairing two shapes, and this one number just multiplies.

## EXP4 — Poincare-Hopf: you can't comb a hairy ball (concepts: poincare-hopf, vector-field-index)
- The "index" of a zero of a flow = how many times the arrows spin as you circle it. Computed:
  a source (arrows point outward) has index **+1**; a saddle has index **-1**.
- On a sphere the indices of any smooth flow must sum to the Euler characteristic, **2** (e.g. a source
  at each pole, +1 and +1 = 2). A flow with NO zeros would sum to 0 — impossible on the sphere.
- Insight: therefore every smooth flow on a sphere has at least one stagnation point — you cannot
  comb a hairy ball flat. The topology forces a swirl.

## EXP5 — Gauss-Bonnet: bend the sphere, curvature moves but its total is fixed (concepts: gauss-bonnet, topology-vs-geometry, deformation)
- Numerically integrating the curvature over the whole surface: a round sphere gives total
  curvature **3.99 x pi**, a stretched egg **3.99 x pi**, a squashed ellipsoid **3.99 x pi**
  (the theoretical value is exactly 4 x pi = 2 x pi x Euler characteristic 2).
- Insight: squash or stretch and curvature piles up in some places and thins in others, but the TOTAL
  always returns to 4 x pi. Geometry (where the curvature sits) is free; topology (the total) is locked.

## EXP6 — winding and linking numbers are integers (concepts: winding-linking, intersection-number, deformation)
- Winding number (how many times a loop wraps the origin), computed by tracking the angle:
  the loop e^(i t) winds **1** time; e^(3 i t) winds **3** times; a loop that misses the origin
  winds **0** times.
- Linking number of two loops: two circles hooked through each other (a Hopf link) link **1**;
  two separate circles link **0**.
- Insight: these are whole numbers you cannot change by wiggling the curves — only by cutting. A
  count that survives all deformation is exactly a topological invariant.

## EXP7 — knots: a coloring count tells a trefoil from a plain loop (concept: knots-and-links)
- Counting the valid 3-colorings of each knot diagram (a computable rule at every crossing):
  a plain loop (unknot) has **3**; the trefoil has **9**; the figure-eight has **3**.
- Insight: the trefoil's 9 versus the loop's 3 is a computed PROOF they are different knots — no
  amount of wiggling turns one into the other, because a wiggle can't change the count.

## EXP8 — Brouwer fixed point: something always stays put (concept: brouwer-fixed-point)
- Iterating x -> cos(x) converges to **x = 0.739085**, where cos(0.739085) = 0.739085 — a point the
  map leaves unmoved.
- Insight: any continuous map of a disk (or interval) into itself must fix at least one point. Stir
  your coffee and some speck ends up exactly where it started; a map of the world onto itself pins a spot.

## EXP9 — planar graphs obey V - E + F = 2, which forbids some graphs (concept: graph-planarity)
- For any connected graph drawn in the plane, V - E + F = 2. For K5 (5 nodes, all connected: V=5,
  E=10), a planar drawing would need F = 2 - 5 + 10 = **7** faces; but each face needs at least 3
  edges and each edge borders 2 faces, forcing E >= 3F/2 = 10.5 — impossible for E=10.
- Insight: so K5 simply cannot be drawn without a crossing — a hard impossibility proved by counting,
  the reason some circuit boards need a second layer.

## EXP10 — Betti numbers: counting holes, and duality (concept: duality)
- Betti numbers (b0 = pieces, b1 = loops around holes, b2 = enclosed voids) and their alternating
  sum: sphere (1,0,1) -> chi = **2**; torus (1,2,1) -> chi = **0**; two-holed torus (1,4,1) -> chi = **-2**.
- Insight: the alternating sum b0 - b1 + b2 is the SAME Euler characteristic, and the numbers read the
  same forwards and backwards (b_k = b_(n-k), Poincare duality) — a hidden mirror symmetry in shapes.
