# Story Engine Agent Synthesis

Run: `2026-06-19_09-17_story-engine-agents`

## Decision

Do not create another novelty doc. Do not add a new orchestrator state.

Build the missing evidence-and-matching layer that makes the existing novelty
doc, winner-bank dump, and A Story gates usable without agent improvisation.

The system contract should be:

`winner evidence -> source winner story engine -> novelty model -> scene landing -> story beats -> QA`

## Agent Consensus

All four agents converged on the same point from different angles:

- Meera: novelty is fake unless it is tied to a human behavior receipt.
- Kabir: winner matching must prove travel before it proves topic/story fit.
- Tara: novelty must become a first-frame visual hook and payoff frame, not a
  clever sentence.
- Idris: the existing gates are mostly present; the missing implementation is
  backend evidence shaping and matcher output.

## Recommended Artifact Shape

Use `source_winner_story_engine` as the structured layer. In run artifacts it
can live inside `planning/novelty_candidate_ledger.json` under
`source_bank_search.matches[*].story_engine`, feeding the existing
`planning/source_winner_novelty_model.json`.

Fields:

```json
{
  "source": {
    "source_url": "",
    "source_account": "",
    "source_shortcode": "",
    "source_format": "",
    "evidence_paths": []
  },
  "metrics": {
    "metric_source": "owned_first_party|third_party_public",
    "shares_per_1k": null,
    "saves_per_1k": null,
    "comments": 0,
    "views": null,
    "likes": null,
    "winner_score": null,
    "metric_gaps": []
  },
  "source_engine_preservation": {
    "copy_status": "exact|lightly_edited|caption_preserved|premise_only|mechanic_only",
    "what_stays": [],
    "what_must_not_be_improved": []
  },
  "travel_mechanism": {
    "viewer_outcome": "send|save|tag|comment|soften|laugh|feel_seen",
    "sender": "",
    "recipient": "",
    "social_cover": "",
    "send_motive": "",
    "comment_trigger": ""
  },
  "story_engine": {
    "stale_obvious_version": "",
    "new_reveal": "",
    "contrast_frame": "",
    "visual_hook": "",
    "last_line_payoff": "",
    "behavior_receipts": [],
    "story_dance_beats": [
      {
        "beat": 1,
        "transition": "context|but|therefore|payoff",
        "what_changes": "",
        "proof_receipt": ""
      }
    ],
    "anti_explanation_blacklist": []
  },
  "a_story_transformability": {
    "wrapper_scale": "small|medium|too_large",
    "lived_scene_wrapper": "",
    "photographable_without_caption": "pass|revise|block",
    "partner_would_send_it": "pass|revise|block",
    "imagegen_feasibility": {
      "face_proximity_risk": "",
      "text_load_risk": "",
      "microtext_risk": "",
      "anatomy_risk": "",
      "style_fit_risk": ""
    }
  },
  "match": {
    "winner_story_score": 0,
    "score_breakdown": {
      "performance_signal": 0,
      "story_engine_fit": 0,
      "a_story_transformability": 0,
      "novelty_preservation": 0,
      "format_fit": 0,
      "risk_caps": []
    },
    "evidence_gaps": [],
    "failure_codes": []
  }
}
```

## Gates To Add Or Strengthen

Hard block or revise when:

- source URL or `what_stays` is missing;
- third-party public source pretends to have shares/saves/reach;
- source is ranked by likes or `winnerScore` without a risk cap;
- `send_motive` is generic;
- `behavior_receipts` is empty;
- beat map is only `and_then`;
- `visual_hook` is mood words;
- `lived_scene_wrapper` is just Aachu/Zuv beside source copy;
- final payoff explains the lesson;
- evidence gaps are hidden.

Failure codes to add later where missing:

- `BEHAVIOR_RECEIPT_MISSING`
- `SOURCE_ENGINE_DRIFT`
- `SHARE_TRIGGER_MISSING`
- `GENERIC_NOVELTY_LABEL`
- `ONE_SIDED_JOKE`
- `EXPLAINS_THE_LESSON`
- `VISIBLE_RECEIPT_MISSING`
- `BUT_THEREFORE_CHAIN_MISSING`
- `DECORATIVE_WRAPPER_ONLY`
- `QUOTE_CARD_STAGING`
- `PAYOFF_FRAME_EXPLAINS_LESSON`

## Implementation Recommendation

First coding slice:

1. Keep existing `/astory` gates and orchestrator states unchanged.
2. Expand `backend/app/data_refs.py` with pure evidence functions:
   - `load_winner_evidence(...)`
   - `match_winner_evidence(brief_text, records, limit=5, rank_by=...)`
3. Return structured `WinnerEvidenceMatch` dictionaries that can populate
   `novelty_candidate_ledger.source_bank_search.matches`.
4. Add narrow backend tests proving:
   - source identity and evidence paths are preserved;
   - owned first-party metrics are used when present;
   - third-party public records emit metric gaps instead of invented shares;
   - likes-only/public-only records receive a confidence cap;
   - output has enough fields to feed the novelty model and remix contract.
5. Only after this matcher exists, strengthen repo QA around behavior receipts,
   `but/therefore` beats, and visual receipts.

## Why This Order

If QA is strengthened before evidence matching, agents will still improvise
source choice and then fill stricter forms with prettier guesses. If the
matcher first preserves source identity, metric gaps, travel mechanism, and
story-engine seeds, the existing creative rooms have honest material to work
from.

The north star: make the system stop picking posts that merely look similar,
and start picking posts whose travel mechanism can survive an A Story wrapper.
