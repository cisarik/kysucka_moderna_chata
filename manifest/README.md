# Integrity inventories

`seed_files.sha256` identifies exact non-Git S00 source/deliverable bytes.
It excludes manifest/, handoff/, work/, caches and backup files to avoid
self-reference and allow the separately granted first report to be written.
The first Planner binds the SHA-256 of this inventory itself and the .blend.

`delivery_files.sha256` additionally covers the prepared first prompt and
seed inventory. It excludes only itself, temporary work, caches and backups.

Format: SHA-256, two spaces, relative POSIX path. Compute file hashes with
Python's standard library or a suitable local SHA-256 tool, without writing
into the project. These inventories prove bytes, not Git commit identity,
public branch state, delivery to a Worker or owner acceptance.
