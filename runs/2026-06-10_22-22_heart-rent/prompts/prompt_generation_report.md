# Prompt Generation Report

Status: ready for creator prompt approval.

Created prompts:

- `prompts/slide_01_4x5_prompt.txt`
- `prompts/slide_01_9x16_prompt.txt`
- `prompts/negative_prompt.txt`

Prompt lock summary:

- Aachu is the asker.
- Zuv is the one living in Aachu's heart.
- Exact text is two lines:

```text
pay rent for living in
my heart
```

- Native 4:5 and native 9:16 prompts are separate.
- Identity references must be loaded in context with `view_image` before imagegen.
- Built-in Codex `imagegen` will be used after prompt approval.

Primary risk controls:

- Role reversal is explicitly forbidden.
- Face merge is explicitly forbidden.
- Yellow/parchment paper is explicitly forbidden.
- Quote-card output is explicitly forbidden.
