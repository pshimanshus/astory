# A Story of Two V2

Codex-native agentic creative production for `@a.storyof.two`.

This project is the clean source of truth for the `/astory` workflow: a multi-agent creative system that turns a rough idea, theme, or auto-idea request into an evaluated, reference-gated, image-ready or image-generated A Story of Two carousel package.

## What `/astory` Is

`/astory` is not a terminal app, npm script, API client, or one-shot prompt chain. It is a Codex skill plus a structured project workspace. When invoked inside Codex, it runs a hybrid agentic workflow:

- a main orchestrator manages state, files, HITL checkpoints, and built-in `imagegen`
- specialist agents debate ideas, story pacing, prompts, and image QA
- every major decision leaves artifacts, traces, evals, and reports

## Commands

```text
/astory setup
/astory husband helps in kitchen but creates more work
/astory theme: daily husband wife moments
/astory auto
/astory resume <run_id>
/astory audit <run_id>
```

## Setup Flow

1. Add identity photos:
   - `references/identity/aachu/`
   - `references/identity/zuv/`
   - `references/identity/together/`

2. Add style references:
   - `references/style/`

3. Add or keep text-style and brand rules:
   - `references/text-style/`
   - `references/brand/`

4. Run:

```text
/astory setup
```

Final image generation is blocked until real identity references are available and visible to Codex.

## Run Flow

For a normal creative request, `/astory` creates a run folder:

```text
runs/YYYY-MM-DD_HH-MM_slug/
  input/
  planning/
  debates/
  prompts/
  references-used/
  images/
  exports/
  evals/
  logs/
  docs/
```

The workflow then moves through:

1. input interpretation
2. reference preflight
3. multi-agent idea room
4. idea scoring and selection
5. HITL idea lock
6. story room and slide-count debate
7. HITL story lock
8. character and style bibles
9. prompt pack
10. prompt QA room
11. HITL prompt lock
12. built-in Codex `imagegen`
13. image QA room
14. retry, accept, or block
15. final reports and portfolio package

## HITL Gates

The system pauses before:

- idea lock
- story and slide-count lock
- final prompt/image generation
- accepting generated images
- final package closeout

The creator can approve, revise, or choose another direction.

## Image Generation

Use built-in Codex `imagegen` only.

Rules:

- no OpenAI API key
- no external provider
- no local image-generation app
- one slide at a time
- native 4:5 for Instagram posts
- separate native 9:16 for Reels/Stories
- no resizing one surface into another
- actual identity references must drive faces

## What Blocked Means

Blocked means the system refused to pretend the run is done. Common blockers:

- missing identity references
- face drift
- wrong or unreadable on-image text
- missing `@a.storyof.two`
- yellow/parchment paper cast
- generic AI watercolor or quote-card look
- scene contradicts the text

Blocked runs still produce reports and failure analysis.

## Example

```text
/astory husband helps in kitchen but creates more work
```

Expected behavior:

- spawn idea-room agents
- generate and debate improved angles
- score candidates
- ask for idea approval
- decide story-led slide count
- create prompt pack
- ask before imagegen
- generate, evaluate, retry if needed
- save final package and portfolio report

## Installed Skill

The source skill lives at:

```text
codex-skill/astory/
```

The installed Codex skill lives at:

```text
~/.codex/skills/astory/
```

When the source changes, reinstall the skill by copying the source folder to the Codex skills directory.
