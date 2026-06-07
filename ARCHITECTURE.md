# Architecture

## Product Shape

`/astory` is a Codex-native agentic creative-production system. The skill provides the operating instructions, and this workspace stores references, runs, evals, traces, and reports.

## Runtime Agents

- Main Orchestrator: owns run state, artifacts, HITL, imagegen, final decisions.
- Idea Room: Relatability Ethnographer, Shareability Strategist, Visual Story Director.
- Story Room: Story Director, Pacing Editor, Swipe Retention Critic.
- Prompt QA Room: Identity Guardian, Style Guardian, Scene Logic Critic.
- Image QA Room: Face Match Reviewer, Style Fidelity Reviewer, Publishing QA Reviewer.

## State Machine

`INIT_RUN -> PARSE_CREATIVE_INPUT -> DETERMINE_IDEA_MODE -> REFERENCE_PREFLIGHT -> GENERATE_OR_REFINE_IDEAS -> SCORE_IDEAS -> SELECT_BEST_IDEA -> HITL_IDEA_LOCK -> GENERATE_STORY_CONCEPT -> DECIDE_SLIDE_COUNT -> GENERATE_SLIDE_BEATS -> SELECT_AND_ORDER_SLIDES -> CREATE_CHARACTER_BIBLE -> CREATE_STYLE_BIBLE -> CREATE_PROMPT_PACK -> PRE_GENERATION_EVAL -> HITL_PROMPT_LOCK -> LOAD_REFERENCE_IMAGES_IN_CONTEXT -> GENERATE_IMAGES_WITH_IMAGEGEN -> IMAGE_QUALITY_EVAL -> RETRY_OR_REVISE_IF_NEEDED -> FINAL_QA -> EXPORT_AND_PACKAGE -> WRITE_REPORTS -> COMPLETE_OR_BLOCKED`

## Data Flow

Input becomes a creative brief. The idea room creates and debates candidates. The story room turns the locked idea into a slide count and beat map. The prompt room validates the prompts. Imagegen creates candidates. The image QA room accepts, retries, or blocks. Reports package the run for production and portfolio review.

## Reference Gates

Identity references are not optional for final generation. If actual Aachu/Zuv references are missing or cannot be made visible to Codex, the run is blocked before imagegen.
