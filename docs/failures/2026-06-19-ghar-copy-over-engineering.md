# Ghar Copy Underperformed Context

Date: 2026-06-19

## Failure

The creator gave a direct emotional note for a two-slide Ghar carousel: first the
song-line, then a soft note about the real ache of one person being home. The
agent-heavy workflow produced a more elaborate A Story-style repair with an
object receipt and private scene.

The creator then compared it with a plain general-LM rendition of the same note
and strongly preferred the plain version.

The first retro misread the correction as "preserve the creator's note more."
That was too narrow. The creator's actual correction is broader: with all the
repo memory, agents, references, taste rules, and context, the generation layer
should produce materially better output than a general LM, regardless of whether
the incoming note is polished, messy, sparse, or already emotional.

## Root Cause

The workflow did not convert accumulated knowledge into better judgment at
generation time. It used evidence and agents as process scaffolding, but the
final creative choice was weaker than a plain model's direct emotional read.

This is not only an input-preservation issue. The failure can happen even when
the creator gives only a rough seed. The studio system must be capable of
generalizing from its learning into stronger copy, stronger emotional structure,
and stronger taste. More knowledge is a liability if it produces heavier,
less-felt output.

## Evidence

- `runs/2026-06-19_21-07_ghar-correction/planning/creator_direction_notes.md`
- `runs/2026-06-19_21-07_ghar-correction/planning/final_copy_voice_repair.md`
- `runs/2026-06-19_21-07_ghar-correction/logs/trace.jsonl`

## Durable Lesson

The bar is not "preserve the prompt." The bar is "outgenerate a plain general
LM using the studio's accumulated taste."

For any A Story creative generation:

- Always create a simple human baseline first. This is the control sample, not
  the final ceiling and not a preserve-only mode.
- Use the knowledge base to sharpen the output, not to burden it.
- Treat a plain general-LM answer as the minimum baseline, not the achievement.
- Agents, winner-bank evidence, and novelty models must improve the final words
  the viewer sees.
- Treat creator-provided terms such as winner-bank, hook, novelty, storytelling,
  and agents as architecture/style signals. They should make the final answer
  more nuanced and robust, not narrower or more procedural.
- If the final output is less moving, less clear, less sendable, or less
  postable than a simple baseline, the generation layer failed.
- Do not convert this lesson into a preservation-only rule. It applies
  irrespective of how complete the creator's input is.

## Regression Check

Before approving future creative copy, ask:

1. Would this beat a plain general-LM answer to the same brief?
2. Did the added context produce sharper taste, or only more machinery?
3. Is the final visible copy better, not just better explained?
4. Would the creator plausibly prefer this output without needing to hear the
   process behind it?
5. Did the studio layers deepen the baseline instead of narrowing the brief?

If any answer is no, stop. The system has not earned the extra context it used.
