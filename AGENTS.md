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

The current working candidate is `blender/kysucka_chata_mcp_v03.blend`, saved
through live MCP from preserved v02. Its camera remains locked at
[21.5, -10.0, 1.25], target [8.5, 2.5, 1.25], 35 mm and shift_y 0.105.
Dedicated PBR materials/metric UVs refine 89 exterior timber objects; 26 rustic
foreground posts and two rails replace only the former fence. Shared original
wood materials remain unchanged on 77 excluded objects. Reference, S00, v01 and
v02 remain preserved; overall visual acceptance remains pending.
`model/parameters.json` owns timber/fence targets and `scripts/timber_fence_v03.py`
is the explicit shared refinement used by live MCP and the source builder.

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
