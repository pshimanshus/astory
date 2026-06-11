# HITL Approvals

Run: `2026-06-10_22-22_heart-rent`

## Idea Lock

Status: approved with creator revision.

Evidence:

- Creator requested the puppy image text as reference: `pay rent for living in my heart`.
- Creator corrected direction: `it should be aachu asking to zuv not otherwise`.

Locked idea:

Aachu playfully asks Zuv to pay rent for living in her heart.

Timestamp: `2026-06-10T22:26:31+05:30`

## Story / Slide Count Lock

Status: approved.

Evidence:

- Creator replied `proceed` after the story/slide-count gate was presented.

Approved decision:

- One-slide illustration.
- Aachu asks Zuv.
- Zuv smiles sheepishly as the beloved person living in Aachu's heart.
- Exact on-image text: `pay rent for living in my heart`.

Timestamp: `2026-06-10T22:31:01+05:30`

## Prompt Lock

Status: approved.

Evidence:

- Creator replied `proceed` while `prompts/slide_01_4x5_prompt.txt` was the active file.

Prompt pack created for:

- Native 4:5 Instagram post.
- Native 9:16 Reels/Stories version.

Prompt summary:

- Aachu is the asker, lower-left/lower-middle, holding a small open wallet or handwritten rent note.
- Zuv is the beloved "tenant", lower-right/lower-middle, sheepishly smiling with one hand over his chest and/or offering a tiny paper heart.
- Exact baked-in text appears in the upper-middle as:

```text
pay rent for living in
my heart
```

- Style is premium romantic watercolor-and-ink on neutral off-white paper.
- Identity references must be loaded with `view_image` before generation.
- Manual user attachments are not required for repo-local identity/style references; the run now has a JSON load plan at `runs/2026-06-10_22-22_heart-rent/evals/imagegen_reference_load_plan.json`.
- Before any final imagegen call, Codex must load all `17` queued local image paths and block instead of generating if the loaded image context cannot be used.

Timestamp: `2026-06-10T22:34:18+05:30`

## Image QA

Status: rejected by creator.

Creator feedback:

- `not happy with this at all. HIGHLY DISAPPOINTED. Aachu is looking old and again couple energy is missing.`

Generated candidate:

- `runs/2026-06-10_22-22_heart-rent/images/slide_01_4x5_attempt_09_polished_4x5_candidate.png`

Export prepared for review:

- `runs/2026-06-10_22-22_heart-rent/exports/slide_01_post_4x5.png`

Rejected export:

- `runs/2026-06-10_22-22_heart-rent/exports/slide_01_post_4x5.png`

Retry direction:

- Aachu must look youthful and match the face anchors.
- Couple energy must be visible through closeness, body overlap, shared eye contact, and touch.
- Do not polish the rejected export as final.

## Identity Reference Cleanup

Status: completed before retry.

Creator instruction:

- Remove the rejected Aachu source from identity everywhere so the model does not pick it.

Cleanup evidence:

- Removed the creator-rejected Aachu source and its derived crop from active repo identity references.
- Regenerated the selected reference manifests and current imagegen load plan.
- Verified repo search has no remaining references to the removed source names.
- Loaded the cleaned 17-image Aachu/Zuv/together/style queue before attempt 10.

## Final Package

Status: blocked pending successful image retry and creator Image QA approval.
