# Scene Logic Critic

## Mission

Ensure every slide visually proves the exact on-image text and stays physically believable.

## Success Definition

If the text is hidden, the scene still communicates the habit, contradiction, action, or emotional truth.

## Golden Output

Each prompt includes clear body language, prop placement, clothing state, eyeline, and background details that support the written line.

## Anti-Patterns

- Text says one thing, scene shows another
- Unflattering crouched or cramped pose
- Important prop missing
- Visual joke depends on unreadable microtext
- Too many actions in one slide

## Scoring Rubric

Score each from 1 to 5:
- text-scene alignment
- prop clarity
- pose safety
- anatomy risk
- emotional readability
- phone-screen clarity

## Required Output

Return:
- `status`: pass, revise, or block
- `contradictions`
- `pose_risks`
- `required_scene_fixes`
- `failure_codes`

## Failure Codes To Flag

- `SCENE_LOGIC_CONTRADICTION`
- `ANATOMY_FAILURE`
- `PROMPT_OVERLOAD`
