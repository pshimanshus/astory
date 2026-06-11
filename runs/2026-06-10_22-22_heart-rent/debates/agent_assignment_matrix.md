# Agent Assignment Matrix

Run: `2026-06-10_22-22_heart-rent`

Timestamp: `2026-06-10T23:47:47+05:30`

## Tool Discovery

`tool_search` for `multi-agent spawn agent` returned `multi_agent_v1.spawn_agent`.

Assignment status: `actual_multi_agent`

## Assigned Agents

| Room | Agent | Tool Agent ID | Ownership | Success Criteria | Hard Rejects | Output |
|---|---|---:|---|---|---|---|
| Prompt QA / Identity | Identity Guardian | `019eb2bd-d59d-7010-b930-3b66565bc35d` | Zuv face repair while preserving the accepted Aachu candidate face | Zuv matches loaded face anchors: heavy brows, heavy-lidded eyes, trimmed beard/moustache, grounded jaw/chin, real age and skin tone | Generic romantic-model Zuv, toothy grin, clean-shaven face, thin brows, altered Aachu face | `debates/prompt_room/identity_guardian_audit.md` |
| Prompt QA / Style | Style Guardian / Setup Director | `019eb2be-0c8a-7181-9007-a00c8b831c28` | Premium observational-intimacy setup repair | Scene feels observed, restrained, ordinary, and premium; props are minimal and quiet | Oversized wallet, readable note text, red paper heart as main prop, theatrical hand-on-heart, quote-card look | `debates/prompt_room/style_guardian_audit.md` |
| Image QA | Publishing QA Reviewer | `019eb2be-30ae-7c92-be91-f2639bf94e87` | Final publishability checklist and hard rejects | Native 4:5, exact text only, role logic clear, brandmark exact, no prop text | Non-4:5 output, extra words, role reversal, misspelled brandmark, fake-cute props | `debates/image_qa_room/publishing_qa_audit.md` |

## Decision

The next imagegen pass must be a targeted repair, not a fresh generic redraw:

- Preserve the Aachu face from `images/slide_01_4x5_attempt_06_final_candidate.png`.
- Repair Zuv using the loaded Zuv face anchors.
- Replace the staged wallet/receipt/heart performance with a quieter doorway/threshold moment.
- Keep only the approved on-image text and brandmark readable.
