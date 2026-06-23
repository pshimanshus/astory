# Image QA Debate

Run: `{{run_id}}`

## Face Match Reviewer

{{face_match_notes}}

## Style Fidelity Reviewer

{{style_fidelity_notes}}

## Publishing QA Reviewer

{{publishing_qa_notes}}

## First Hard Questions

- Emotional truth before canvas: `pass|block`
- Reference-copying before prettiness: `pass|block`
- What would the creator immediately reject: `{{creator_reject_frame}}`
- Which identity reference did the candidate copy too literally: `{{copied_identity_reference}}`

If emotional truth or reference-copying blocks, stop before canvas, brandmark,
or typography polish.

## Hard Gates

- Creative room checked image before passing: `yes|no`
- Actual canvas is native `1080x1350 px`: `yes|no`
- Tiny top-right `@a.storyof.two` brandmark is present: `yes|no`
- Visual setting, prop placement, eyeline, and body logic make sense: `yes|no`

## Arbiter Decision

`accept|retry|block`

## Required Retry Prompt Delta

{{retry_delta}}
