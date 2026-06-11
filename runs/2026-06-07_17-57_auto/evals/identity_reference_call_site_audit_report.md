# Identity Reference Full Repo Audit

Run: `2026-06-07_17-57_auto`

Status: `pass`

## Scope

- Files seen: `72912`
- Non-vendor text files scanned line-by-line: `163`
- Files with identity/reference mentions: `87`
- Excluded from line scan: `.git`, run-local `local-tools` vendor/cache tree, binary image/model/cache files, and this audit's own output files.

## Result

- Active findings: `0`
- Legacy/vague flat-reference pattern matches in scanned text: `0`
- Required folders missing: `0`
- Contact sheets missing: `0`
- Selected manifest missing paths: `0`
- Dossier role errors: `0`
- Dossier SHA errors: `0`
- Prompt reference-block errors: `0`
- Local workflow reference errors: `0`
- Local proof mismatches: `0`
- Discovery audit errors: `0`

## Sources Of Truth

- Dossier: `references/identity/_dossier/identity-dossier.json`
- Preflight: `references/identity/_dossier/identity-generation-preflight.md`
- Active manifest: `runs/2026-06-07_17-57_auto/references-used/selected_references.json`
- Local proof: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Local workflow: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`

## Role Library

- Aachu face anchors: `11`
- Zuv face anchors: `8`
- Indexed dossier references: `53`
- Deprecated duplicate role aliases: `14`
- Active cross-role duplicate image hashes: `0`
- Selected manifest paths checked: `71`
- Slide prompts checked: `10`

## Local Stack State

- Proof status: `dry_run_pass_pending_creator_execution_approval`
- Discovery status: `blocked`
- Discovery failure codes: `COMFYUI_DEPS_MISSING`

## Notes

Historical failed context-generation evidence is superseded/redacted and is not an active source. The current active path requires actual local image inputs selected from the role folders and validated by the dossier/preflight. Local model execution remains gated by discovery status.
