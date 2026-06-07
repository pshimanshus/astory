# Imagegen Contract

Use built-in Codex `imagegen` only. Do not ask for an OpenAI API key. Do not create a local image provider.

## Required Before Final Generation

1. Select identity references.
2. Make local reference images visible in context when needed using `view_image`.
3. Select style references or load the locked style rules.
4. Confirm exact on-image text.
5. Confirm native surface: 4:5 post or 9:16 story/reel.
6. Confirm prompt passed pre-generation QA.
7. Ask for HITL prompt approval.

## Generation Rhythm

- Generate one slide at a time.
- Save each candidate in `runs/<run_id>/images/`.
- Save accepted finals in `runs/<run_id>/exports/`.
- Log each generation attempt and decision.

## Retry Rule

Use targeted prompt repair. Do not rewrite the whole prompt randomly.

Retry up to 2 times per failure type. If identity cannot be preserved, mark blocked.
