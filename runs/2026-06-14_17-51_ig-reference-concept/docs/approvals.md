# Approvals

Run: `2026-06-14_17-51_ig-reference-concept`

## HITL_IDEA_LOCK

Status: approved.

Timestamp: `2026-06-14T12:40:39Z`

Creator decision: proceed to slide content for the selected idea.

Evidence: creator asked, `share the content for all slides`, after the selected idea and scene-landing preview were presented.

Approved idea: `The Hair Clip He Started Carrying`

Approval scope: proceed through Story Room / slide-content drafting only. Prompt lock, imagegen, image QA, and final package remain unapproved.

## HITL_STORY_LOCK

Status: revision requested.

Draft generated: `2026-06-14T12:49:04Z`

Recommended slide count: `5`

Recommended sequence:

1. `why do you have my clip?`
2. `wait. my old one?`
3. `it lives in my pocket now.`
4. `for first-bite emergencies.`
5. `fine. keep it there.`

Artifact paths:

- `runs/2026-06-14_17-51_ig-reference-concept/planning/story_concept.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/slide_count_decision.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/slide_beat_map.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/scene_options.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/selected_scenes.json`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/story_room/story_debate.md`

Creator rejected this draft on `2026-06-14T13:06:24Z`.

Reason: the draft over-invented a new hair-clip premise instead of preserving the source post's copy/structure with small A Story changes.

Repaired draft generated: `2026-06-14T13:06:24Z`

Repaired slide count: `6`

Repaired sequence:

1. `"can i ask you something?"` / `~sure`
2. `"you remembered?"` / `~of course i did.`
3. `"no coriander?"` / `~extra chutney too.`
4. `"that's the thing."` / `~what thing?`
5. `the intimacy of "you remembered?" "of course i did."`
6. `the intimacy was important. so was the chutney.`

Repaired artifact paths:

- `runs/2026-06-14_17-51_ig-reference-concept/planning/source_preserving_repair.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/repaired_slide_content.json`

Creator rejected this repair on `2026-06-14T13:10:38Z`.

Reason: it still followed a template from another post instead of using the
same line from `DUtQzmaj9Rw?img_index=3`.

Same-line visual repair generated: `2026-06-14T13:10:38Z`

Same-line repaired sequence:

1. `The intimacy of "You remembered?" "Of course I did."`
2. `The intimacy of "You noticed?" "Of course I did."`
3. `The intimacy of "You saved it?" "Of course I did."`
4. `The intimacy of "You still know?" "Of course I do."`
5. `The intimacy of "You remembered?" "I always do."`

Same-line repair artifact paths:

- `runs/2026-06-14_17-51_ig-reference-concept/planning/same_line_visual_repair.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/same_line_slide_content.json`

Decision to approve or revise the slide content will be recorded here before continuing to character/style bibles, prompt writing, or image generation.

## HITL_PROMPT_LOCK

Status: approved by direct continuation request.

Timestamp: `2026-06-16T18:35:10Z`

Creator decision: `share rest of the illustrations for the caraousel`

Approval scope: generate the remaining carousel illustrations from the existing
same-line artifact, slides 2-5, in `1080 x 1350 px` portrait format. Do not
invent fresh slide copy beyond the recorded same-line slide texts.

Prompt paths:

- `runs/2026-06-14_17-51_ig-reference-concept/prompts/slide-02-you-noticed-1080x1350.md`
- `runs/2026-06-14_17-51_ig-reference-concept/prompts/slide-03-you-saved-it-1080x1350.md`
- `runs/2026-06-14_17-51_ig-reference-concept/prompts/slide-04-you-still-know-1080x1350.md`
- `runs/2026-06-14_17-51_ig-reference-concept/prompts/slide-05-i-always-do-1080x1350.md`
