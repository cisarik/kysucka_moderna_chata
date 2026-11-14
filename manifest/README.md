# Historical S00 integrity inventories

Both seed_files.sha256 and delivery_files.sha256 are retained inventories
of the original non-Git S00 package. They can name files absent from the
reduced Git repository and are not current task prerequisites.

seed_files.sha256 records the original source/deliverable selection.
delivery_files.sha256 additionally records the original delivery selection,
including its prepared bootstrap material.

Do not rewrite their hashes to describe a later tree. Current identity uses
the exact Git commit/tree and the protected source-byte hashes specified by
AGENTS.md and the current grant.

Format: SHA-256, two spaces, relative POSIX path. Read-only recounting is
historical analysis, not proof of current publication, delivery, or acceptance.
