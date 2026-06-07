# Story-To-Carousel Agentic Workflow Dry Run

## Problem

A broad creative input like "husband helps in kitchen but creates more work" can easily become a generic spouse joke or one-shot prompt.

## Product Insight

The creator needs a system that debates the idea before production, preserves warmth, scores engagement, and refuses final image generation when identity references are missing.

## Agentic Workflow

This dry run tested the idea room only. Three specialist agents independently generated candidates, debated strengths and weaknesses, repaired the best direction, and produced a final scorecard.

## Multi-Agent Design

- Relatability Ethnographer protected lived-in emotional truth.
- Shareability Strategist optimized for comments and shares.
- Visual Story Director challenged visual feasibility and prompt risk.

## Evaluation

The selected idea scored `4.72 / 5`, clearing the `4.0` threshold.

## HITL Design

The run stops at idea lock. In production, the creator approves, revises, or chooses another idea before story and prompt planning.

## Failure Taxonomy

The system correctly classified missing identity references as `IDENTITY_REFERENCE_MISSING` and blocked final image generation.

## AI PM Skill Demonstrated

- multi-agent workflow design
- engagement scoring
- human-in-the-loop gating
- failure taxonomy
- traceable creative decision-making
- refusal to fake completion

## Next Iteration

Add identity and style references, rerun `/astory setup`, then continue through story room, prompt QA, and imagegen.
