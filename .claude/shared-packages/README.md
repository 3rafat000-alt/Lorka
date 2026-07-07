# 📦 shared-packages — reusable code, never duplicated

Doctrine (Teaching III · Radical Isolation): a project never copies code from
another project. Anything two projects share lives **here** and is imported, not
duplicated. Each `projects/<PRJ-XXXX>/` symlinks `shared/ → ../../.claude/shared-packages`.

**What belongs here:** cross-project libraries, shared UI components, common
utilities, design-token packages — code with a clear owner and a versioned contract.

**What does NOT:** project-specific logic, secrets, or anything that ties two
projects' fates together beyond a stable published interface.

Promotion of a package into this dir is an ADR-worthy decision (it creates a
cross-project dependency) — record it in the owning project's `DECISIONS.md`.
