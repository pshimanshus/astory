# Image Quality Report

Run: `2026-06-15_23-25_silence-house-walks`

Status: `failed_after_allowed_text_retries`

Accepted final: `false`

## Candidate Review

- `images/candidate_01_text_not_exact.png`: rejected. Visual direction works, but Hindi text is not exact and the file is `1122x1402`, not native `1080x1350 px`.
- `images/candidate_02_text_retry_01.png`: rejected. Text improved but still not exact; canvas remains `1122x1402`.
- `images/candidate_03_text_retry_02.png`: rejected. Best visual candidate, but Hindi line wrapping/punctuation is still not exact and canvas remains `1122x1402`.

## Final Gate

Blocked on:

- `TEXT_NOT_EXACT`
- `WRONG_CANVAS_SIZE`

No image was copied into `exports/`.
