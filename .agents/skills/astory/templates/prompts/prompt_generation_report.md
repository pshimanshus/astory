# Prompt Generation Report

Run: `{{run_id}}`

## Inputs Used

- Selected idea: `{{selected_idea_id}}`
- Story concept: `{{story_concept_path}}`
- Slide beat map: `{{slide_beat_map_path}}`
- Character bible: `{{character_bible_path}}`
- Style bible: `{{style_bible_path}}`

## Prompt Decisions

{{prompt_decisions}}

## Hard Gates

- Native canvas: every prompt says `1080x1350 px`
- Identity references: actual Aachu/Zuv face anchors must be visible before imagegen
- Brandmark: every prompt requires tiny top-right `@a.storyof.two`
- Visual setting: prompt matches the locked scene and makes physical sense

## Risks

- {{risk}}

## Prompt QA Status

`pending|passed|revision_required|blocked`
