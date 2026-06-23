# Style Guardian Audit - Reza

run_id: 2026-06-15_23-25_silence-house-walks
prompt: runs/2026-06-15_23-25_silence-house-walks/prompts/slide_01_prompt.txt
status: pass

## Evidence Basis

- Checked the active slide prompt, selected scene, and imagegen visibility proof.
- Checked the house style contract, imagegen contract, master prompt, brand rules, and text-style rules.
- Viewed the three loaded best-illustration style references listed in the visibility proof: `encoded-check-000.png`, `road-trip-best-reduced-tan-50-4x5.png`, and `slide-01.png`.
- Reference visibility proof records 4 Aachu face anchors, 4 Zuv face anchors, 3 style references, and `visible_reference_context_ready`.
- Anti-slop lock: this is one single illustration using the supplied copy as-is. No alternate concept or copy is being proposed.

## Style Strengths

- Native `1080x1350 px` is explicit in the generation priority and hard gate.
- Prompt gives raw Aachu/Zuv face anchors priority over descriptions, which protects against generic pretty-couple drift.
- Style language is aligned with the house lock: hand-drawn watercolor-and-ink, fine pencil/ink linework, transparent muted washes, visible paper grain, tactile clothing and prop detail, soft faded edges.
- Paper safety is stated directly: neutral white/off-white only, with no yellow, mustard, sepia, beige/tan dominance, parchment, coffee-stained, or heavy cream cast.
- Text is instructed as warm charcoal handwriting baked into the paper, with upper-middle negative space and no digital overlay.
- Scene is not a poster around a quote. The lifted sock foot, two-hand cup hold, half-open door, still curtain, and angled chair all make the line visually provable even if the text is covered.
- Brandmark is explicitly required as tiny, low-contrast, handwritten `@a.storyof.two` at the top-right.
- Hard negatives name the right failure modes: quote-card/poster design, generic sad couple, anime, doll faces, glossy render, wrong Devanagari, missing brandmark, yellow/parchment cast, role reversal, and face merge.

## Style Risks

- The loaded style references include warm/tan visual temptations and bottom-right brandmark examples. The active prompt correctly overrides this with neutral white/off-white paper and top-right brandmark, but image QA must reject if the model follows the references instead of the written contract.
- Bilingual text raises a real `TEXT_UNREADABLE` watchpoint. The prompt says exact text and no wrong Devanagari, but generation may still deform glyphs or line breaks.
- "Warm" appears in text and light language. It is currently controlled because the prompt says any warm light must stay local to faces/props and must not tint the paper.
- The scene has multiple quiet environment details. If over-rendered, it could become decorative mood illustration instead of the clean lower-half/lower-two-thirds A Story composition.

## Prompt Fixes

- No blocking prompt fixes required before imagegen.
- Do not alter the supplied copy, line order, scene concept, or single-illustration scope.
- If a targeted repair becomes necessary after generation, tighten only these guards: preserve bilingual glyphs and line breaks exactly; ignore bottom-right brandmark placement in style references and keep the brandmark top-right; keep all warm light local so the paper remains neutral white/off-white.

## Scores

- house_style_fidelity: 5/5
- paper_tone_safety: 4/5
- typography_integration: 4/5
- texture_detail: 5/5
- palette_control: 4/5
- brandmark_clarity: 4/5

## Failure Codes

failure_codes: []

watchlist_codes:
- YELLOW_PAPER_CAST
- TEXT_UNREADABLE
- STYLE_DRIFT
- BRANDMARK_MISSING
