# Process Failure Audit

Run: `2026-06-19_21-09_ghar-line`

## Verdict

You are right: those milestones should not have existed as approvals.

The generated slide was not a subtle miss. It was an obvious creative failure: Aachu was smiling in a missing-person ache beat, and the image copied the loaded cafe identity reference's smile, cup/table setup, jacket, and composition. That should have been caught before generation.

## What Actually Happened

The original run had real multi-agent work, but that was for the earlier domestic/sofa lane. Your later corrections invalidated that lane.

For iteration 2, the prompt-room review was not fresh independent agent work. It was recorded as `fallback_local_passes_with_limitation_recorded`. I then let that fallback pass behave like a real approval gate. That was the main process failure.

## Why The Agents / Reviewers Passed It

They did not meaningfully pass it.

The artifacts passed because I let checklists substitute for taste:

- raw references loaded: yes;
- prompt says `1080x1350 px`: yes;
- prompt says no Zuv: yes;
- prompt says do not copy anchors: yes;
- prompt has brandmark and exact text: yes.

But none of that answered the actual question:

> Does this image still feel like Aachu is lost in a full place, or did we just watercolor-copy a smiling cafe photo?

That question was not enforced as a hard gate. It should have been.

## Root Causes

- `EMOTIONAL_STATE_CONTRADICTION`: the prompt asked for a late smile when the scene needed an unsmiling ache.
- `IDENTITY_REFERENCE_POSE_COPY`: the active Aachu cafe reference overlapped with the desired scene, so the model copied its pose and emotional state.
- `FALLBACK_REVIEW_TREATED_AS_AGENT_PASS`: local fallback prompt notes were allowed to unlock generation.
- `CHECKLIST_OVER_JUDGMENT`: QA verified route artifacts but not the emotional/visual truth.
- `HUMAN_CREATOR_BECAME_QA`: you caught something the internal process should have blocked.

## New Blocking Rules

- No fallback local prompt-room pass may unlock imagegen after a major creator visual correction.
- Before imagegen, check identity-reference collision: if a loaded identity image shares the scene, prop, wardrobe, expression, or camera angle, it must be excluded/cropped or generation blocks.
- Before imagegen, check emotional-state contradiction. For this run, slide 1 cannot contain a smile.
- Prompt lock cannot be inferred from a broad "proceed" after the prompt has changed.
- Image QA must start with emotional truth and reference-copying, not with canvas size.

## Current State

No more imagegen from this prompt pack. The run is blocked until prompt review is rebuilt from the corrected premise and a safer identity-reference route.
