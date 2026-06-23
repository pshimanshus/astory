# Pre-Generation Eval Report

Run: `2026-06-19_21-09_ghar-line`

Status: `invalidated_process_failed_reapproval_required`

The previous pre-generation pass is invalidated. It allowed a fallback local prompt-room review to behave like a real gate after a major creator visual correction, and it missed the emotional contradiction / identity-reference pose-copying risk before imagegen.

The prompt pack has been patched after creator correction, but it is not approved for generation. It needs rebuilt prompt review and reapproval.

## Key Scores

- Overall: `4.54`
- Visual setting logic: `4.8`
- Prompt clarity: `4.6`
- Text readability potential: `4.1`
- Publishability: `4.1`

## Recorded Limitation

The original run used actual multi-agent rooms. The domestic prompt pack was later invalidated by creator corrections. The iteration 2 prompt refresh used local specialist passes with the limitation recorded because fresh subagent spawning is not allowed unless explicitly requested by the user.

## Hard Gates

- Native `1080x1350 px`: `pass`
- Tiny top-right `@a.storyof.two`: `pass`
- Exact text in prompt: `pass`
- Zuv absent in all slides: `pass`
- No comeback payoff: `pass`
- Identity-reference pose/expression copying blocked: `pass`
- Slide 1 smile removed: `pass`
- Process approval: `failed`
- Reference visibility: `pending`
