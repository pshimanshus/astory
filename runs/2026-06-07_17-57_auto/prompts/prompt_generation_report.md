# Prompt Generation Report

Run: `2026-06-07_17-57_auto`

## Inputs Used

- Selected idea: `runs/2026-06-07_17-57_auto/planning/selected_idea.json`
- Story concept: `runs/2026-06-07_17-57_auto/planning/story_concept.json`
- Slide beat map: `runs/2026-06-07_17-57_auto/planning/slide_beat_map.json`
- Selected scenes: `runs/2026-06-07_17-57_auto/planning/selected_scenes.json`
- Character bible: `runs/2026-06-07_17-57_auto/planning/character_bible.json`
- Style bible: `runs/2026-06-07_17-57_auto/planning/style_bible.json`
- Reference manifest: `runs/2026-06-07_17-57_auto/references-used/selected_references.json`

## Prompt Decisions

- Built separate native prompts for `4:5` Instagram posts and `9:16` story/reel surfaces.
- Kept exact on-image text from the approved story lock.
- Repeated identity and style reference roles inside every prompt so later generation stays anchored.
- Kept slide 3 as an offered folded shawl, not a wrapped shawl, to reduce `ANATOMY_FAILURE`.
- Kept slide 4 concrete by anchoring the line to Aachu physically wearing or resting with the shawl.
- Applied Prompt QA revisions: slide 2 hides the shawl completely, slide 4 locks one seated pose, brandmark/paper palette are tighter, slide 3 text block has stronger spacing guidance, and repeated avoid lists are shorter.

## Risks

- `IDENTITY_REFERENCE_MISSING`: prompts are not approved for imagegen until selected local references are loaded visibly in context after prompt approval.
- `TEXT_UNREADABLE`: every prompt reserves upper-middle negative space, but final QA must still inspect text.
- `ANATOMY_FAILURE`: shawl handling is deliberately simple; image QA must reject tangled fabric, crossed arms, warped hands, or broken wrists.
- `GENERIC_IDEA`: Zuv must remain quiet and ordinary, not heroic or smug.

## Prompt QA Status

`passed`
