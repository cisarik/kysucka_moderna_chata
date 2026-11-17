# Agent Instructions

<!-- BEGIN MANAGED AP INTEGRATION -->
## Analytic Programming

This project uses Analytic Programming through the pinned Git submodule at `.ap/`.
The exact AP version is the commit recorded by this repository's `.ap` gitlink.

Required reading:
- All participants read `.ap/AP.md`.
- Orchestrators also read `.ap/AP_ORCHESTRATOR.md`.
- Workers also read `.ap/AP_WORKER.md`.
- Prompt structures are in `.ap/PROMPT_CONTRACTS.md`.

Project-specific rules outside this managed block remain authoritative within
their scope. Task authority comes only from the current authoritative
Orchestrator prompt.

Treat `.ap/` as read-only during ordinary project work. Protocol updates require
a separate explicit AP update task.
<!-- END MANAGED AP INTEGRATION -->

## Project rules

### Roles, communication, and scope

Michal is the COOPERATOR. Master Orchestrator and Fresh Orchestrator are
instances of ORCHESTRATOR: Master coordinates the development run; the whole's
Orchestrator coordinates its selected logical whole. WORKER performs only the
bounded task in the current complete grant. Workers never close a logical whole.

Communicate with Michal in Slovak, addressing him in masculine forms.
The Orchestrator uses feminine self-reference. Worker prompts and formal
reports are English. Every standard Worker report begins exactly:
`### Report for ORCHESTRATOR_CHAT`.

Human-facing project documentation is Slovak. Agent rules, code, identifiers,
formal reports, and existing English technical documentation may be English.

The project develops a visualization against
`reference/kysucka_chata_moderna.png`. Architectural review is deferred until
Michal accepts the visualization. No construction certification, structural,
permit, energy, or real-site design claim is implied.

The 14.4 × 8.4 m footprint, 45-degree roof, floor +0.450 m, wall plate
+3.250 m, nominal ridge +7.450 m, room arrangement, unseen elevations, and
camera remain hypotheses, not accepted dimensioning or visual calibration.

### Current sources and preservation

`model/parameters.json` owns shared main numbers, camera, and material targets.
`scripts/design.py` owns drawing geometry and shared geometry helpers.
`scripts/build_scene.py` owns detailed procedural scene construction.
The reference is the preserved visual target; the seed is the preserved S00
scene checkpoint. Generated PDF/CAD and old renders do not own current 3D behavior.

Manual Blender edits do not flow back into JSON or generators. A later grant
must identify accepted scene/source versions before regeneration.

The preserved v04 predecessor is `blender/kysucka_chata_mcp_v04.blend`, saved
through live MCP from preserved v03. Its camera remains locked at
[21.5, -10.0, 1.25], target [8.5, 2.5, 1.25], 35 mm and shift_y 0.105.
Dedicated PBR materials/metric UVs refine 89 exterior timber objects; 26 rustic
foreground posts and two rails replace only the former fence. Shared original
wood materials remain unchanged on 77 excluded objects. Reference, S00, v01, v02 and
v03 remain preserved; overall visual acceptance remains pending.
`model/parameters.json` owns timber/fence targets and `scripts/timber_fence_v03.py`
is the explicit shared refinement used by live MCP and the source builder.

The v04 environment uses `scripts/landscape_v04.py::apply_v04(scene, P, ROOT)`
and `model/parameters.json::landscape_v04`: 1,200 linked forest placements
(780 Picea mariana and 420 Picea abies), four young spruces, one static orchard
tree with 28 attached fruit instances, 51 planted clump groups and 104 edge-grass
groups. The 263 superseded proxies remain hidden and retained. Existing site and
bed vertex coordinates are unchanged; dedicated shaders replace only their slots.
Sixteen off-scene master collections and the two original ground materials carry
fake users so they survive saving. Native render output and source replay use
the locked camera, preserved world/lights and v03 comparison profile.

Protected initialization SHA-256 values:

| File | SHA-256 |
|---|---|
| blender/kysucka_chata_seed.blend | 9fcea3fc25eeaec1e791b772c4d4ae4f825f103a139154ab45c2c420718226e0 |
| reference/kysucka_chata_moderna.png | 05bc3e72161e5945379c86da80450ffdf82ddce6dbdd9b9e77071aa79cdecc96 |
| model/parameters.json | 00b97dd1adc1b82a19685454d4ab40dfb60332c90c7ad2ad165eb9e73e39a162 |
| scripts/build_scene.py | 4310a6ed69e577157c2a605b5c2a7b0128ca62ab667f69ea72aece47563884c2 |

Current MCP v01 SHA-256 values (the initialization values above remain historical):

| File | SHA-256 |
|---|---|
| model/parameters.json | 90a3bf95c9c51ea407ae1d749b481795733e88c083c07415ed0f58f916c6cc7a |
| blender/kysucka_chata_mcp_v01.blend | 227edd9356a0e2917486351bce6e6fdbb62c58eacbfbb96101c1872d5235e4a8 |

Current MCP v02 SHA-256 values (the initialization and v01 values above remain historical):

| File | SHA-256 |
|---|---|
| model/parameters.json | 2d441b08d658e4aa4c8fccc5e71c76eb16666deeb4401cdd0b973c379901cada |
| blender/kysucka_chata_mcp_v02.blend | 010f47a81a4fde2e936f401e87b8bc11af76a8e72d71811d68dd910da0b27249 |

Current MCP v03 SHA-256 values (all earlier tables remain historical):

| File | SHA-256 |
|---|---|
| model/parameters.json | 153437c4a574243240011bb12a34b3597f199b5c18d36b54a8f3e8bcde45ad34 |
| scripts/build_scene.py | baee0b204b17b5e696933ed97a9c915191b6c5b873320651da9cdf59f30288c0 |
| scripts/timber_fence_v03.py | f94dce1b2da5c07d4064f8ac800304ce3e4c04372447eb737ac2a51aa73fcf98 |
| blender/kysucka_chata_mcp_v03.blend | 360c99a107f9bd819e273274e3cd449a5b7666a27fc69c6ee3a51dfa7e120248 |

Current MCP v04 SHA-256 values (all earlier tables remain historical):

| File | SHA-256 |
|---|---|
| model/parameters.json | a2239cd2ef6b75545e9f0a8ca750c11553678674c8ee1fde11818cb77d40ba77 |
| scripts/build_scene.py | 8dfe65695ad99e25fad53d465fd8d79e4f6f5a7f7e8f1ef780ad9385ac08ce15 |
| scripts/landscape_v04.py | 950d23c79bc50b26a1c606cff36605923a1c172b660f15945f58faf9beceb723 |
| blender/kysucka_chata_mcp_v04.blend | c19b37cf75037969d2608677d276880d46e9ae7afc31aa11a78c340241fa3d43 |

Preserve reference/, blender/, model/, scripts/, cad/, docs/*.pdf, previews/,
manifest/*.sha256, requirements-docs.txt, and tools/ during initialization.
No scene resave, rebuild, camera/material/shader/geometry change, PDF/CAD
regeneration, asset download, or preview replacement without a specific grant.
Historical inventories are retained evidence, not current repository gates.
`work/` holds temporary output, never authoritative sources; cleanup needs a grant.

### Blender capability route

The canonical local inspection route is `blender-local-v1` in docs/OPERATIONS.md.
The observed executable is /Applications/Blender.app/Contents/MacOS/Blender,
observed as 5.2.3 LTS. Seed-authoring provenance remains Blender 4.3.2.

For `kysucka-moderna-chata-blender-mcp-first-reference-render`, the explicit
implementation grant activates the task-specific `blender-mcp-live-v1` route:
existing MCP tools control the live GUI for reads, owner checkpoints, working-copy
saves, the camera shift, renders, readback, and camera/scene-world display.
The active working file is `blender/kysucka_chata_mcp_v01.blend`; the seed remains
preserved. This bounded deviation grants no future mutations or installations.

For `kysucka-moderna-chata-reference-camera-perspective`, its explicit
implementation grant reactivates `blender-mcp-live-v1` for the three-candidate
camera comparison and v02 save. The current working file is
`blender/kysucka_chata_mcp_v02.blend`; seed and v01 remain preserved. Only camera
perspective changed; non-camera geometry, materials, glass, world, lights and
landscape remain unchanged. This task-specific route grants no future mutations
or installations.

For `kysucka-moderna-chata-realistic-timber-and-foreground-fence`, the explicit
implementation grant reactivates `blender-mcp-live-v1` for timber materials,
metric UVs, foreground fence, checkpoint, matched renders, packing and v03 save.
The selected camera and all excluded content remain unchanged. Official CC0
wood maps are listed in `assets/ASSET_MANIFEST.md` and packed with relative paths.
CLI cold verification and replay use separate processes; `work/mcp-v03-before.blend`
and `work/v03_source_replay.blend` are disposable evidence, never source authority.
This task-specific route grants no future mutations or installations.

For `kysucka-moderna-chata-kysuce-forest-and-natural-garden`, the explicit
implementation grant activates `blender-mcp-live-v1` for normalized CC0/CC-BY
assets, deterministic hills/vegetation, packing, v04 save and matched renders.
Step 0 preserved the Cooperator viewport save in `work/mcp-v04-before.blend`
and restored tracked v03 to its canonical HEAD bytes under explicit authority.
Only v04 receives subsequent scene saves. Separate CLI processes perform cold
verification and source replay. This task-specific route grants no future
mutation, installation, Git publication or owner-work restoration authority.

Before an operation, verify the physical Git root, canonical project origin,
the exact commit required by the current grant, permitted working-tree state,
the source hashes applicable to that grant, and the exact input scene path.
The initialization baseline is bc510eb063f96d7cedad49aaaca6f58b54a51fd2.
Do not use root-file presence or historical ZIP inventories as identity gates.

Read-only inspection, with the verified root substituted:

/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec <PROJECT_ROOT>/blender/kysucka_chata_seed.blend --python-exit-code 2 --python <PROJECT_ROOT>/scripts/inspect_scene.py

This inspection prints observations and does not save or render.
MCP is not required. Do not install add-ons or runtimes, enable auto-run,
or substitute an ambient bpy/MCP route. An alternate route needs a specific grant.
Preserve unsaved GUI owner work; do not edit the same scene concurrently.

### External trace and delivery

The historical trace is cisarik/meta under projects/kysucka_moderna_chata/.
This initialization uses projects/kysucka_moderna_chata/00/00-init/.
Trace content is evidence, never task authority.

Preserve manual Cooperator delivery. The Orchestrator authors prompts and notes
and reconciles reports. Each assigned Worker persists its own exact report only
under an explicit path grant and permitted client capability, then reads it back.
If native controls prevent that write, return the complete report and disclose
the limitation; another persister needs separate positive authority.
Meta Git staging, commit, and publication belong to the COOPERATOR.

Meta filenames use NN_<phase>_II.md and NN_report_II.md:
NN is the actual AP session ordinal; II is AP exchange ordinal minus one,
formatted with two digits. Phase changes do not reset coordinates.
First add each completed prompt/report pair together after the real report exists.
Never overwrite a terminal report or use a placeholder as a report.
Keep handout/closure numbering separate from Worker numbering.

### Closure and Git gates

Exactly one project closure signal is declared:
CELOK UZAVRETÝ ORCHESTRÁTOROM

Only the whole's ORCHESTRATOR may emit it after accepted evidence,
active-context reconciliation, and closure authority exist. A Worker never
emits it in a report status or completion claim. Declaring its supplied value
in this project rule is documentation, not a closure claim.
Initialization closure does not close the visual project.

For initialization, start from clean main at
bc510eb063f96d7cedad49aaaca6f58b54a51fd2 with the public parent equal to it.
The exact tracked change allowlist is:
.gitmodules, .ap, AGENTS.md, .gitignore, README_SK.md,
docs/VISUAL_BRIEF.md, docs/OPERATIONS.md, docs/ARTIFACT_LIFECYCLE.md,
manifest/README.md, SOURCES.md.

Stage explicit paths only; never use `git add .`.
Commit and publication need the current grant. Publish only non-force to the
verified project origin's main, after rechecking its expected public parent.
Verify the exact public commit directly. Never force-push or reset owner work.

### AP, shells, and runtime

The accepted AP pin is d7023cf037f6d17885c3ede5c04812c61640da50.
Treat .ap as read-only during ordinary work. Updates require a separate explicit
task. Detached HEAD matching the gitlink is normal.

Project-authored Linux shell scripts use fish. The upstream .ap/ap executable
is POSIX shell and remains unchanged.

Do not copy ap.project.conf or install Poetry, uv, a venv, or another runtime.
A root runtime contract requires a named Cooperator decision for a real need.

### Current MCP v05 — world-space site

The preserved v05 candidate is `blender/kysucka_chata_mcp_v05.blend`, created
from preserved v04 under the explicit implementation grant for
`kysucka-moderna-chata-spatial-site-valley-and-grass`. The task-specific
`blender-mcp-live-v1` route uses the existing Linux Blender 5.3.0 GUI; isolated
`/home/agile/Applications/Blender/blender` processes verify cold reopen and replay.
This record grants no future mutation, installation or Git publication.

`model/parameters.json::site_v05` owns the terrain, garden, masks, populations and
review poses. `scripts/site_v05.py::apply_v05(scene, P, ROOT)` follows v03/v04 in
the builder and uses isolated RNG 13705. The protected terrace
`[-15,19] × [-10,11.5] m` retains all 126 original vertices exactly. Protected
building/interior/bed/path/orchard/timber/fence witness data remain unchanged.
The four v04 hill ribbons are hidden and retained; 1,200 existing forest trees
and young spruces 02/03 are vertically re-grounded on the common surface.

The continuous closed terrain spans `[-260,320] × [-220,260] m` with a descending
+X valley. The convex garden is 810.910 m², 34.70 × 25.12 m, with a closed gate
and four additional approach slabs. Original 26 fence stakes/two rails remain
intact. V05 adds 286 stakes (including gate posts) and 100 rails (including gate
rails), plus gate palings/brace/hinges/latch. No fruit tree is added.

V05 adds 1,200 linked spruces, 5,332 short-lawn patches and 8 232 meadow
groups. 489 groups use 6 726 independently grounded linked constituents
where support variation exceeds 10 mm. Far meadow density is halved after
capping. Original v04 libraries/materials remain unchanged; interior edge tufts
are hidden. Nineteen off-scene V04/V05 master collections and the original
terrain snapshot carry fake users. Three Grass005 1K JPG maps are packed.

C1 remains `[21.5,-10,1.25] → [8.5,2.5,1.25]`, 35 mm, sensor 36 mm, shifts
0/0.105, clip_end 500 m. It is active in the saved scene with the established
1448 × 1086 / 96-sample CPU OIDN comparison profile. `work/` checkpoints and
`work/v05_source_replay.blend` are temporary evidence, never source authority.
The visual candidate awaits Cooperator acceptance; no architectural/site
calibration is asserted.

Current MCP v05 SHA-256 values (earlier tables remain historical):

| File | SHA-256 |
|---|---|
| `model/parameters.json` | `66ed4d7246ca211a55d3067a4b14f50e8af706efc669c4dd4911c7c0c1d2d664` |
| `scripts/build_scene.py` | `9c7863c125c74f2894529ad247f8d5eb8f9b756f3f1af26dd8be094ebd7a8c6b` |
| `scripts/site_v05.py` | `f6f122dbacb293bb8a90f748583555516c8d57344112c47a62eba172afb821aa` |
| `blender/kysucka_chata_mcp_v05.blend` | `c3bd3d5e847c52d33a60f3f89cf4392da85a24df96fe7774a25a37bd39d8fafe` |

### CachyOS workstation and forward visual criteria

The exclusive development workstation is CachyOS Linux at
`/home/agile/Projects/kysucka_moderna_chata`. Michal reports 32 GiB system RAM,
with approximately 20 GiB still available while normal development tools,
Blender and the browser are running. Direct inspection also observed an
`NVIDIA GeForce RTX 3080` with 10,240 MiB VRAM and the existing Blender 5.3.0
Cycles `CUDA` and `OPTIX` devices enabled. Actual device use and VRAM/system RAM
must be measured per render rather than inferred merely from preferences.

The legacy 3 GiB render-RSS target was a bounded planning assumption, not a
workstation requirement. It led to Grass005 1K selection, halved far-meadow
population and 32 m meadow chunks in saved v05. It is not a standing reason
to cap later candidates. Future refinements should choose quality from visual 1:1
A/B evidence and measured CPU/GPU/RAM/VRAM behavior, while retaining existing
CPU/OIDN comparisons where needed.

The v05 candidate is technically replayable, but it is not an accepted final
photorealistic visualization. The whole's closure carries an explicit visual
gap register into Master. In particular, the far valley ridge and several
slopes still need dense, varied forest; the meadow needs continuous cover rather
than isolated dark clumps; and the lawn needs more naturally curved/thicker 3D
blade sections, thatch and spatial variation. Glass roughness 0.07 blurs the
inside view. The original fireplace's gable reflection is disclosed, not an
unidentified exterior tree. A subsequent gate-approach landing must close the
remaining approximately 18–22 cm route gap to the gate. Review-camera NW/SZ
needs an unobstructed review pose without hiding forest. Additional fruit and
architectural/interior/lighting work remain separate accepted future objectives,
not permission to mutate the v05 scene.

### Pre-meadow MCP v06 — compressed exterior and dense vegetation candidate

The pre-meadow saved candidate was `blender/kysucka_chata_mcp_v06.blend`, produced
under V06-RESOURCE-BOUNDED-COMPLETION and Michal's explicit amendment to halve
exterior landscape and trees while retaining the cottage, enclosed garden,
path and cameras. This record grants no future mutation or Git publication.
`model/parameters.json::vegetation_v06` and
`scripts/vegetation_v06.py::apply_v06(scene, P, ROOT)` own the deterministic
seed-13706 treatment, called after the unchanged v03/v04/v05 builder steps.
All 17 older parameter sections and previous modules remain unchanged.

V06 copies the original terrain into owned derived meshes, contracts X/Y
outside the fixed core `[-15.5,19.2] x [-10,16.5]` by 0.5, and blends terrain
height to the same factor over an 8 m join from datum -0.055 m. Active extent
is about `[-137.75,169.60] x [-115,138.25]`. Original terrain geometry, topology,
UVs and normals remain retained hidden; two ground slots use owned materials.
The exterior young spruce 03 is retained hidden and replaced by a linked
half-size instance. Cottage, garden, C1, old cameras, timber, enclosure/gate,
paving, orchard, interior, glass, world/lights and source libraries are preserved.

The full candidate has 12,833 linked tree placements, 6,793 lawn patches and
1,134,737 meadow patches. Meadow is resampled at natural blade/stem sizes.
Support uses actual terrain triangles, small linked subpatches and bounded
root envelopes; 2,973 tiny cells (11.6133 square metres) are rejected and
reported. Full idempotence, actual supports/masks, source replay and cold
semantic checks pass. Geometry remains instanced. Existing Grass005 1K maps
and original asset credits remain; no asset was downloaded or introduced.

Official matched renders use P0 CPU/OIDN Accurate/High, 8 threads, 96 samples,
1448 x 1086 for C1, frame/seed 0 and AgX/None, exposure 0/gamma 1. Full OPTIX
completed but left only 159 MiB VRAM, below the declared approximately 1 GiB
guard; the earlier P1 bridge did not fail. Following a reported system reset,
CPU jobs and heavy validation were serialized with a SOLID viewport. No
further GPU attempt, driver change or saved preferences occurred.

V06 is a technically saved/replayable PARTIAL visual result. Canopy overlaps
more and covers more of the distant ridge, but meadow bands/stepped bare
patches, overly uniform narrow lawn blades and some needle-like silhouettes
and an unforested central crest remain. Original roughness-0.07 glass still blurs the inside view. The sharp
outside-glass diagnostic is not an interior repair. No professional visual,
architectural/site acceptance or publication is asserted. Evidence and the
terminal Worker report belong to Meta `00/06-dense-forest-and-continuous-meadow/`;
`work/v06/final/` and replay/checkpoint files are temporary evidence only.

Pre-meadow MCP v06 SHA-256 values (all earlier tables remain historical):

| File | SHA-256 |
|---|---|
| `model/parameters.json` | `58a6886c917e59d233d2cd5abcf711f334f73a9ef3f340f4a5c8bde7983d507a` |
| `scripts/build_scene.py` | `2abb505c6665eb7e215557a1681f6fc7bc72e4d2949493c275cd16c261473f6a` |
| `scripts/vegetation_v06.py` | `4bfce5ea56de33fdc737e31c1cfafe8cb82cc460d998c98711d234c7860e3ea9` |
| `blender/kysucka_chata_mcp_v06.blend` | `fff6f16e373aa94c20902f9cd9880f62a2569981ce5b68d2396222258626cc63` |

### MCP v06 — meadow correction before steep-slope treatment

The current file remains `blender/kysucka_chata_mcp_v06.blend`; its pre-meadow
bytes are preserved in `work/v06/final/pre_meadow_correction.blend` (fff6f16e…).
V06-MEADOW-ONLY-CORRECTION introduced shared `apply_meadow_v06`, used by normal
`apply_v06` and live meadow-only application. All older JSON sections, other
V06 settings, forest/lawn/terrain/cameras, shared materials and original assets
remain unchanged. Only the builder's first-save image rebasing changed for the
mandated deep replay path; the v03/v04/v05/v06 build hook order is unchanged.

The corrected meadow has 3,869,907 linked patches and 12 reusable
masters: staggered overlapping 0.5 m cells, 0.125/0.0625 m support/boundary
refinement, smooth ecological mixing, arching lower leaves, atlas middle forms
and varied tall stems. Binary 2 m omissions and screen-tier density/width jumps
are removed. Nominal support rejection is 31.0664 m²;
this sum may overlap and is not unique terrain loss. Full and meadow-only
idempotence, protected semantics, actual roots/masks, replay and cold C1 passed.

The bounded visual result is PARTIAL; see Meta `01_report_03.md` and
`work/v06/final/meadow/`. Remaining limits: Large rectangular omissions are repaired and low-eye continuity improves, but fine directional bands/clumped texture and a broad bare steep slope remain; frozen short lawn and central crest also remain open.
The accepted 0.5 exterior, fixed core, P0 CPU/OIDN/96 and all deferred optical,
short-lawn, crest and architectural limits remain. GUI uses IMAGE_EDITOR for
native renders after recovery; no scene visibility or machine preferences were
changed. No whole acceptance, publication or continuing mutation grant follows.

Pre-steep-slope meadow-correction hashes (historical):

| File | SHA-256 |
|---|---|
| `model/parameters.json` | `4064dc0757f4fc89c3907b8469047986e8f16f2a99fe629b62da48f31624c711` |
| `scripts/vegetation_v06.py` | `237aecb0fe2521d7ab0beaa8adbbccd926758217150fa7197b27336a4b1b480f` |
| `scripts/build_scene.py` | `b3754b119311cd242d2872a9b40cdc3fdfcd0349a436964e5949775e7e063154` |
| `blender/kysucka_chata_mcp_v06.blend` | `9f97bc9cd33739e0e104d9d003aab5f773d4b2069768c6dd453ff7860cbc6a96` |

### Current MCP v06 — steep-slope meadow support correction

V06-STEEP-SLOPE-SUPPORT-CORRECTION retains the current v06 path. Exact former
9f97bc… bytes are in `work/v06/final/meadow/pre_steep_slope_correction.blend`;
complete former trace pixels/metadata are inventoried under
`work/v06/final/meadow/steep_slope/before/`. The measured 64.214° SW and
63.107° exterior-left slopes exceeded the former 60° meadow threshold.
`vegetation_v06.meadow.steep_slope` now permits only the (60°,68°] class,
with full projected-footprint triangle normals and 0.4 local-height low forms.
The shared meadow-only/full path preserves all 3,869,907 old
placements and 12 old masters exactly; 15,194 new linked
patches use 12 additional owned low-cover masters. Forest/lawn, every terrain,
camera, shared shader/asset and all other source settings remain unchanged.

Meadow-only/full fixed points, normal source replay, exhaustive actual support,
masks, stored frames and separate cold C1 passed. Product is 159,992,657
bytes (152.58 MiB). Bounded result: PASS.
Both measured steep bare faces visibly carry low cover. Fine directional/speckled meadow, uniform short lawn, central unforested crest and optical/architectural limits remain unaccepted.
Evidence: `work/v06/final/meadow/steep_slope/`, Meta `01_report_04.md`.
P0 CPU/OIDN/96 and safe idle IMAGE_EDITOR remain; no preferences, Git
publication, visual/architectural acceptance or continuing authority follows.

Current steep-slope correction hashes (all earlier tables remain historical):

| File | SHA-256 |
|---|---|
| `model/parameters.json` | `383bef95d3ec08f439756557bf10250f645b3c00511f3d16a47fb69fe48754d7` |
| `scripts/vegetation_v06.py` | `6515cd6e8ffdeb31fb55cfe7802e9968364cb71771ed557c367b4507cb0361ae` |
| `scripts/build_scene.py` | `b3754b119311cd242d2872a9b40cdc3fdfcd0349a436964e5949775e7e063154` |
| `blender/kysucka_chata_mcp_v06.blend` | `059eaa947d64ecb1a0e3b15c2a380f800b827c54d4a1a7dd877bbb6e686f5a0b` |


### MCP v07 — forest age variation and connected gravel trail

The current saved candidate is `blender/kysucka_chata_mcp_v07.blend`
(194,344,710 bytes), derived from preserved v06 under
FOREST-TRAIL-V07-IMPL. The explicit `blender-mcp-live-v1` grant used existing
Linux Blender 5.3.0; separate canonical CLI processes verified source replay,
forced V07 idempotence and actual-product cold portability. This record grants
no continuing mutation, installation, Git publication or visual acceptance.

`model/parameters.json::forest_trail_v07` and
`scripts/forest_trail_v07.py::apply_v07(scene, P, ROOT, *, components=None)`
own the seed-13707 treatment after unchanged v03/v04/v05/v06 builder steps.
All 18 older JSON sections and prior modules remain unchanged. The active
forest has 12,977 placements, including 144 crest additions, exactly 649
uniform baseline-scale × 0.5 replacements and 378 legacy young placements at
factor 1. The eleven declared route-clearance XY moves and 337 edge prototype
swaps are explicit; original tree meshes/materials and predecessor layers remain.

The 198.180813 m XY / 200.616798 m graded trail reaches the actual north
boundary at [42,138.25], with a supported closed gravel layer and the disclosed
27.55–35.13° short gate bevel / 5 mm leaf clearance. Its 1,105 samples have
maximum spacing 0.199972 m. Owned terrain derivatives preserve original meshes
and exterior coordinates/UVs/normals; native free float-vector corner normals
avoid legacy INT16 encoding drift. Actual support masks remove 41,215 old
meadow patches; 60,552 local cover placements include 3,297 boundary repairs.
There are 300 stone / 600 litter instances and 85 packed file images, including
three 2K CC0 gravel maps. The original 82 image bytes remain unchanged.

C1/P0 and safe idle IMAGE_EDITOR remain selected. Low branches in the walking
witness, finite-world edges in the fixed overview, original meadow/lawn and
glass/fireplace/architectural limits remain open to visual review. Source replay
and checkpoints under `work/v07/` are temporary evidence, never source authority.
The protected v06 and `work/baselines/v06-pre-v07/` recovery packet remain intact.
The earlier candidate records above are historical.

V07 SHA-256 values:

| File | SHA-256 |
|---|---|
| `model/parameters.json` | `1b429d72ed9db1a07fde7c19e1575b01948cb4e6a62e29e970898f810fb382c4` |
| `scripts/build_scene.py` | `50f3d248a03470b8d392202fa06c56278500321fa62b0bed88a627df3950a7a8` |
| `scripts/forest_trail_v07.py` | `54f93c5abe0814faa12ffbc544ca3f731d4315a97f27621e1122d7031baa045c` |
| `blender/kysucka_chata_mcp_v07.blend` | `99c4f239040e880d0d8c5e9fc761954690b707c84ce746a33ac356a86d72e384` |

V07 implementation status is PARTIAL at final audit: `route.shoulder_width_m`
contains [0.45,0.75] m but is not explicitly consumed by the module. The current
owned soil-shader test uses 0.85 m and local cover restoration uses 1.15 m plus
boundary repair footprints. A separately controlled irregular shoulder-width
zone is unverified. The single correction is exhausted; a new Orchestrator
disposition is required before further product/source mutation.


### MCP v08 — usable vegetation candidate

The explicit direct Cooperator decision in the current session authorizes the
V08 optimization, superseding the earlier V07-only scope for this task.
`blender/kysucka_chata_mcp_v08.blend` is the new candidate; V07 remains preserved.
`model/parameters.json::vegetation_v08` and `scripts/vegetation_v08.py::apply_v08`
own seed-13708 thinning to 9,733 forest trees, bounded 1–9 m height variation,
owned simplified render masters and a separate linked lightweight viewport branch.
All 19 prior parameter sections and prior modules remain unchanged.
Measured final vegetation cost is 51.73% of V07 expanded triangle accounting;
the full Solid orbit measures 42.9 FPS at 2840×1208. Native renders remain CPU P0.
Protected cottage/interior/orchard/beds/fence/gate/paving/world/lights/cameras remain.
V07's irregular shoulder-width gap is explicitly deferred, not accepted as fixed.
The old full-vegetation Material Preview attempt preceded a hardware reset; recovery
and bounded lightweight-view tests are documented in `docs/V08_VEGETATION.md`.
No driver, backend, preferences, Git publication or architectural acceptance changed.
This historical record grants no continuing mutation authority.

V08 scene SHA-256: `1ba638c7335319c84558e4f779befe9f6a0f7a1ed255d29097359f816d2e6662`.
V08 module SHA-256: `b4b15f3bedce142616112b49c516c1bc6a829d1b39784bdf0eda290261b52d1c`.

### V08 optional working-view refinement

`blender/kysucka_chata_mcp_v08_view.blend` preserves original V08 and replaces
only its five coarse working tree meshes with source-derived branch/alpha-foliage
LODs. Render meshes, placements, grass, masks, cottage and cameras are unchanged;
the native V08 images remain their original evidence. The current V08 source
selects `forest.viewport_model = source_branches`, ratio 0.3 of existing LOD1.
Solid measured 41.8 FPS and staged Material Preview 16.7 FPS at 2840×1208 before
a subsequently observed new system boot of unconfirmed cause. No further GPU
stress test followed reconnection; GUI shows the saved C1 in IMAGE_EDITOR.
See `docs/V08_VEGETATION.md` and temporary `work/v08/viewport_review/` evidence.
This record is not visual acceptance or continuing mutation authority.

Working-view scene SHA-256: `07146b03e7e74a54c6368fb51e2affa695d8edec58045953a6fc5d62c084104e`.
Current V08 module SHA-256: `cd3137ed08c09726a29a06ba08452f1840a4981e09267de6c94d965dd492fc73`.
