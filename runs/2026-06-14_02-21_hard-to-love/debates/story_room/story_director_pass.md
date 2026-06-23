# Story Director Pass

Run: `2026-06-14_02-21_hard-to-love`  
Agent: `Story Director - Dev`  
Persona: `.agents/skills/astory/personas/story-room/story-director.md`  
Prompt packet: `.agents/skills/astory/templates/agents/story_room_agent_prompt.md`

## Evidence Ledger

| Artifact | Path | What You Used | Gap Or Risk |
| --- | --- | --- | --- |
| Creative brief | `runs/2026-06-14_02-21_hard-to-love/input/creative_brief.json` | The source question family is "am i hard to love / handle / understand / not enough / worth the risk?"; concept screenshots are premise/text references only; both people must not be forced into every slide. | Final prompts still need native `1080x1080 px` and brandmark, but this pass does not write prompts. |
| Selected idea | `runs/2026-06-14_02-21_hard-to-love/planning/selected_idea.json` | Locked idea: `The Chair Outside The Door`; emotional truth is not decoding Aachu immediately, but not abandoning her while she becomes speakable again. | File says `hitl_status: pending`; `docs/approvals.md` and the current user instruction mark the idea approved. |
| Scene landing preview | `runs/2026-06-14_02-21_hard-to-love/planning/scene_landing_preview.md` | The carousel must be proven by changed objects: chair distance, glass level, charger path, folded cloth, door crack, and light under the door. | A static hallway would become sad quote-card energy. The visual round must make state changes readable. |
| Memory recall | `runs/2026-06-14_02-21_hard-to-love/planning/memory_recall.md` | Use current visible references and direct artifact evidence; avoid repeated close-angle two-face defaults; concept style is not the house style. | Automated recall produced no run-specific cited results, and brain lint is failing from unrelated reference churn. |
| Creator corrections | `runs/2026-06-14_02-21_hard-to-love/planning/creator_direction_notes.md` | Do not force both Aachu and Zuv into every slide; the vulnerable line alone is not enough; closed prompt packets matter. | Master prompt language still says the same two people appear in every slide; Prompt QA must adapt that to this run's correction. |
| HITL approval | `runs/2026-06-14_02-21_hard-to-love/docs/approvals.md` | `HITL_IDEA_LOCK` is approved at `2026-06-14T11:14:34+05:30`; creator said proceed to storyboard. | No shared story artifacts should be overwritten by this isolated pass. |
| Story Director persona | `.agents/skills/astory/personas/story-room/story-director.md` | Protect the tiny truth, deepen the spine, avoid repeated beats, mean payoff, narration doing the image's job, and quote-card endings. | None. |
| House style | `.agents/skills/astory/references/house-style-contract.md` | Airy off-white watercolor-and-ink, generous upper-middle negative space, exact readable text, scene must visually prove the written line. | Hallway warmth must not turn into yellow/parchment cast later. |
| Master prompt | `.agents/skills/astory/references/master-prompt.md` | Compact identity-first prompt contract; raw face anchors and best-illustration style references are mandatory before final imagegen. | Its "same two people every slide" sentence conflicts with the active creator correction; story beats should not inherit that force. |
| Identity anchors | `references/identity/aachu/`, `references/identity/zuv/`, `references/identity/together/` | Aachu and Zuv face anchors exist; representative close and together anchors were inspected for face-readability and body-language support. | This story deliberately uses several no-face or partial-presence slides. Any visible face must remain large enough for the raw anchors to protect likeness. |

## Persona Required Fields

- `title`: `The Chair Outside The Door`
- `one_line_summary`: Aachu fears her quiet makes her hard to love; Zuv answers by staying nearby without forcing the door, until the changed objects prove she trusted the care.
- `emotional_hook`: The ache is not "will he fix me?" It is "will he stay gentle when I cannot explain myself yet?"
- `setup`: A closed door, a practical chair, and one unanswered question establish the fear of being too quiet to love well.
- `escalation`: Zuv does care, but edits out pressure: water and charger placed out of the door swing, the chair moved back, no second knock.
- `payoff`: The door cracks, the water drops, the charger crosses the threshold, and the chair is still findable without being heroic.
- `relationship_truth`: He did not learn how to force her open. He learned the distance where care still reaches her.
- `risks`: Static hallway repetition, saintly-rescuer framing, sleeping-martyr staging, dramatic hug payoff, unreadable object continuity, and prompt drift that forces both faces into every frame.

## 1. Premise Lock

`The Chair Outside The Door` is about Aachu going quiet and fearing that quiet makes her hard to love, while Zuv proves love by staying close enough to be found and far enough not to corner her.

What must not change:

- The answer must be restraint, not rescue.
- The chair must remain practical, not sacrificial.
- Objects must carry the proof: water, charger, folded cloth, chair distance, light, and door crack.
- Zuv must not become a perfect martyr sleeping outside the door.
- The payoff must not become a dramatic embrace, apology speech, or generic reassurance quote.
- The story must respect the creator correction: not every slide needs both people visible.

## 2. Tension Ladder

1. Aachu's fear is named before anyone is seen: she is behind the door, but the real question is whether quietness makes her unlovable.
2. Zuv acts without making himself the center: water and a charger appear where the door can still open, proving he understands pressure can look like help.
3. Time passes, and the care calibrates: the chair shifts back, a cloth appears, the light changes. He is not leaving, but he is also not guarding the door.
4. Aachu accepts one object before she accepts a conversation: the charger or glass crosses the threshold. This is the first visible change in her agency.
5. The payoff lands on distance as love: the chair remains findable, the door opens just enough, and the used objects answer the first question without a speech.

The viewer's knowledge changes every time: first fear, then method, then patience, then acceptance, then relationship rule.

## 3. Slide Economy

Recommended slide count: `5`.

Why five: the premise is not a single reveal. It needs visible state changes so the care does not look like one decorative still life outside a door. Five slides give the chair and objects enough time to become evidence without adding therapy-dialogue clutter.

Why fewer fails: three slides would jump from question to payoff too fast, making Zuv's care look magically perfect or turning the final into a caption explaining what the objects did not prove.

Why more dilutes: six or more slides would start repeating the hallway, adding extra emotional explanation, or drifting into a speech/hug resolution the idea is specifically avoiding.

Cut or keep verdict:

- Slide 1: `keep` - the hook needs the door and chair as the first emotional contract.
- Slide 2: `keep` - the first care action proves Zuv knows not to knock his way in.
- Slide 3: `keep` - the chair distance and time passage are the anti-martyr correction.
- Slide 4: `keep` - Aachu must show agency by accepting one object.
- Slide 5: `keep` - the payoff needs the accepted care plus the still-findable chair.
- Candidate Slide 6, hug/apology/explanation: `cut` - it would make the image solve the story with romance theatre instead of observed behavior.

## 4. slide_beat_contract

### Slide 1

- Story role: `setup`
- Exact on-image text: `am i hard to love when i go quiet?`
- Emotional contradiction: Aachu wants the door closed, but fears the closed door will be read as rejection.
- Relationship action: nobody intrudes; the room announces presence with the light under the door.
- micro_action: a plain chair sits near the door but not touching it; no hand on the handle, no knock marks, no dramatic shadow.
- Face visibility: no face required; identity risk is low because the point is absence/presence.
- Why it earns a swipe: the viewer wants to know whether the person outside leaves, knocks, or learns the right distance.
- Observed detail: the chair is angled slightly toward the door, like someone placed it after trying to decide how close was too close.
- Imagegen risk: if the hallway goes dark or theatrical, it becomes generic sadness instead of A Story restraint.

### Slide 2

- Story role: `escalation`
- Exact on-image text: `when i want you near, not knocking?`
- Emotional contradiction: she wants closeness, but the usual proof of closeness would feel like pressure.
- Relationship action: Zuv places care within reach and removes himself from the demand.
- micro_action: only Zuv's hand and forearm place a water glass and phone charger beside the chair, safely outside the door swing.
- Face visibility: Zuv face not required; if shown, keep him partial and not crowding the door.
- Why it earns a swipe: the viewer sees he understands the rule, but not whether she will accept it.
- Observed detail: the charger cable is neatly threaded toward the wall, not tossed like a romantic prop.
- Imagegen risk: vague prompting may put the glass directly in front of the door or make his hand look like he is reaching for the handle.

### Slide 3

- Story role: `bridge`
- Exact on-image text: `when one more question feels too loud?`
- Emotional contradiction: care continues, but every extra question would make the quiet harder.
- Relationship action: Zuv adjusts his presence rather than increasing it.
- micro_action: the chair has moved one tile farther back; a folded cloth is now on the chair; the water level is lower or condensation has changed; the light under the door is softer.
- Face visibility: no face required; a small seated figure from the side is optional only if it does not become martyr staging.
- Why it earns a swipe: the viewer understands time has passed and asks whether Aachu will respond to the care.
- Observed detail: faint chair-leg marks or shifted floor alignment show the chair did not vanish, it was recalibrated.
- Imagegen risk: if the chair movement is not readable, the slide repeats slide 1 with extra props.

### Slide 4

- Story role: `escalation`
- Exact on-image text: `he moves the chair back.`
- Emotional contradiction: the most loving move is not getting closer.
- Relationship action: Aachu accepts the care without having to perform readiness.
- micro_action: the door is cracked just enough for Aachu's hand to pull the charger or folded cloth inside; the chair sits farther back, empty, still in frame.
- Face visibility: Aachu face not required; a hand at the threshold is safer and more emotionally exact.
- Why it earns a swipe: this is the first proof that the care reached her, but the emotional answer is not complete yet.
- Observed detail: the charger cable crosses the threshold through the door crack, making acceptance visible without a caption.
- Imagegen risk: the door crack and hand anatomy can become confusing; the visual scene round must choose a clean, physically possible threshold angle.

### Slide 5

- Story role: `payoff`
- Exact on-image text: `and stays where i can find him.`
- Emotional contradiction: staying does not mean sitting guard; loving distance can be active and quiet.
- Relationship action: Zuv remains available nearby while Aachu has accepted the offered care.
- micro_action: from inside the slightly open doorway, the half-empty glass and charging phone are visible; outside, the chair is still nearby but not blocking the door, with Zuv implied down the hall or softly partial in the background.
- Face visibility: if Aachu or Zuv appears, only one readable face at most; do not force a two-face close-up. A partial Aachu profile may work if large enough for identity anchors.
- Why it earns a save/share: it gives language to a care rule many couples know but rarely name.
- Observed detail: the chair is not occupied like a vigil; it is simply waiting in the right place.
- Imagegen risk: if Zuv is shown as a glowing patient saint, the payoff turns performative. If nobody's acceptance is visible, the ending becomes too subtle.

## 5. Retention Pass

- Slide 1 to 2: the viewer wants to know what love does outside a closed door.
- Slide 2 to 3: the viewer sees care offered and wants to know whether Zuv will pressure her for a response.
- Slide 3 to 4: the changed chair asks whether Aachu will notice or accept the care.
- Slide 4 to 5: the accepted object asks what the final answer to the first question will be.
- Save/share trigger: the carousel gives a partner a non-accusatory way to say, "thank you for staying gentle when I shut down."

## 6. Visual Handoff

The Visual Scene Discussion agent must answer:

- Which hallway geometry makes the door swing, chair placement, glass, and charger physically believable?
- How do we show the chair moved back without using before/after labels or confusing the viewer?
- Which continuity object should be primary: charger crossing the threshold, water level, or folded cloth?
- Does slide 3 include a partial Zuv, or is the empty chair stronger and less saintly?
- In slide 5, should Zuv be implied down the hall, shown as a soft partial figure, or omitted entirely?
- Can Aachu's acceptance be shown through hand/threshold/object movement without creating fragile hand anatomy?
- Where does handwritten text sit on each square so it remains readable without covering the door crack or object proof?

## 7. Blocker Pass

No hard blocker for story progression if the visual scene round solves the chair-distance and threshold geometry.

Required revisions before prompt writing:

- Prompt QA must adapt the master prompt's "same two people must appear in every slide" line to this run's creator correction. Forcing both faces into every slide would damage the locked idea.
- The visual scene round must reject any slide that places water or charger where the door could hit them.
- The payoff must avoid a hug, apology speech, Zuv asleep outside the door, or a glowing rescuer posture.
- The story should proceed to visual selection, not prompt writing or imagegen.

Failure codes flagged as risks, not current blockers: `VISUAL_GENERIC_RISK`, `SCENE_LOGIC_CONTRADICTION`, `TEXT_UNREADABLE`.

## Decision Table

| Slide | Keep/Cut | Story Role | On-Image Text | micro_action | Swipe Reason | Face Visibility | Visual Risk | Prompt Handoff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `keep` | `setup` | `am i hard to love when i go quiet?` | Chair waits near a closed door with warm light under it, not touching the door. | What will love do outside the closed door? | No face required. | Dark hallway or sad poster energy. | Airy off-white hallway; practical chair; no hand on handle. |
| 2 | `keep` | `escalation` | `when i want you near, not knocking?` | Zuv's hand places water and charger outside the door swing, then leaves frame. | He understands the care rule, but will she accept it? | Zuv face optional and partial only. | Hand may look like it is reaching for the handle. | Place objects safely and readably; charger path to outlet. |
| 3 | `keep` | `bridge` | `when one more question feels too loud?` | Chair moves one tile back; cloth appears; light and water level change. | The viewer sees time and patience, not a one-off gesture. | No face required; avoid martyr pose. | Chair shift may be too subtle. | Make distance change legible through floor/tile/door spacing. |
| 4 | `keep` | `escalation` | `he moves the chair back.` | Aachu's hand pulls charger or cloth through a cracked door while the chair stays farther back. | First proof that the care reached her. | Aachu hand only; face not required. | Door crack, cable, and hand can become physically messy. | Use clean threshold angle and one primary object crossing. |
| 5 | `keep` | `payoff` | `and stays where i can find him.` | Inside/outside threshold shows half-empty glass, charging phone, open door, and chair still nearby but not blocking. | The first question gets answered without a speech. | At most one readable face; do not force both. | Saintly Zuv or too-subtle acceptance. | Show availability without vigil: chair findable, Zuv implied or soft partial. |
| 6 candidate | `cut` | `payoff` | `hug / apology / explanation beat` | Dramatic embrace or spoken reassurance after door opens. | None; it explains what the objects already proved. | Would force both faces. | Generic romance theatre. | Do not generate as part of this story. |

## Scoring Rubric

| Criterion | Score | Note |
| --- | ---: | --- |
| story coherence | 5 | Each slide changes knowledge, action, or pressure. |
| emotional clarity | 5 | The contradiction is clean: near, not knocking. |
| payoff strength | 4 | Strong if the final object state is readable; weak if it becomes only a line. |
| tenderness | 5 | Care is gentle without making Aachu a problem or Zuv a savior. |
| brand fit | 5 | Airy, object-led, private, and specific to Aachu/Zuv's quiet-care grammar. |
| visual continuity | 4 | Depends on the visual round making chair distance and threshold logic unmistakable. |

## JSON-Ready Object

```json
{
  "agent_role": "Story Director - Dev",
  "premise_lock": {
    "must_preserve": [
      "Aachu worries that going quiet makes her hard to love.",
      "Zuv answers through calibrated presence, not pressure.",
      "The chair outside the door remains practical and emotionally load-bearing.",
      "Objects prove the care: water, charger, folded cloth, chair distance, light, and door crack."
    ],
    "must_not_change": [
      "Do not force both Aachu and Zuv into every slide.",
      "Do not turn Zuv into a saintly rescuer or sleeping martyr.",
      "Do not resolve with a dramatic hug, apology speech, or generic reassurance line.",
      "Do not copy the dark/magenta/orange concept style.",
      "Do not let the vulnerable line stand alone without visual proof."
    ],
    "emotional_truth": "Some people are not asking to be decoded immediately. They are asking not to be abandoned while they become speakable again.",
    "relationship_dynamic": "Aachu needs quiet without disappearance; Zuv loves her by learning the distance where care still reaches."
  },
  "slide_count_decision": {
    "recommended_slide_count": 5,
    "why_this_count": "Five slides give the care objects enough time to change state: fear named, care placed, distance adjusted, care accepted, and payoff proved.",
    "why_fewer_fails": "Fewer slides would skip the calibration and make Zuv seem magically perfect or force the caption to explain the care.",
    "why_more_dilutes": "More slides would repeat hallway beats or add a hug/explanation that weakens the observed object proof.",
    "cut_or_keep_verdict": [
      {
        "slide": 1,
        "verdict": "keep",
        "reason": "The door and chair establish the emotional contract."
      },
      {
        "slide": 2,
        "verdict": "keep",
        "reason": "Zuv's first care action proves nearness without knocking."
      },
      {
        "slide": 3,
        "verdict": "keep",
        "reason": "The chair shift proves patience and avoids martyr staging."
      },
      {
        "slide": 4,
        "verdict": "keep",
        "reason": "Aachu's acceptance gives the story agency instead of one-sided caretaking."
      },
      {
        "slide": 5,
        "verdict": "keep",
        "reason": "The payoff answers the hook through changed objects and calibrated distance."
      },
      {
        "slide": "6_candidate",
        "verdict": "cut",
        "reason": "A hug, apology, or explanation beat would dilute the object-led ending."
      }
    ]
  },
  "slide_beat_contract": [
    {
      "slide_number": 1,
      "story_role": "setup",
      "exact_on_image_text": "am i hard to love when i go quiet?",
      "viewer_question_created": "Will the person outside leave, knock, or learn how to stay gently?",
      "micro_action": "A practical chair waits near a closed door with warm light under it, close but not pressed against the door.",
      "emotional_shift": "Fear is named before either person is shown.",
      "face_visibility_requirement": "No face required; identity risk is low.",
      "visual_evidence_needed": "Closed door, light under door, practical chair, generous negative space, no dramatic darkness.",
      "imagegen_risk": "Dark hallway or staged sadness could make the slide generic.",
      "visual_scene_questions": [
        "How close is close enough without implying pressure?",
        "What door angle and hallway crop leave clean text space?"
      ]
    },
    {
      "slide_number": 2,
      "story_role": "escalation",
      "exact_on_image_text": "when i want you near, not knocking?",
      "viewer_question_created": "Can Zuv offer care without making himself the demand?",
      "micro_action": "Zuv's hand places a water glass and charger beside the chair, outside the door swing, then leaves the frame.",
      "emotional_shift": "Love becomes action, but the action edits out pressure.",
      "face_visibility_requirement": "Zuv face optional and partial only; not identity-critical.",
      "visual_evidence_needed": "Water, charger, safe placement, visible door swing logic, no hand on handle.",
      "imagegen_risk": "The hand may look like it is opening the door unless the prop placement is clear.",
      "visual_scene_questions": [
        "Which prop should be closest to the threshold?",
        "How do we show his hand leaving, not entering?"
      ]
    },
    {
      "slide_number": 3,
      "story_role": "bridge",
      "exact_on_image_text": "when one more question feels too loud?",
      "viewer_question_created": "Will patience stay gentle when there is no immediate response?",
      "micro_action": "The chair sits one tile farther back; a folded cloth appears; the water level or condensation changes; the door light softens.",
      "emotional_shift": "Care becomes calibrated distance, not constant asking.",
      "face_visibility_requirement": "No face required; if Zuv is present, keep him non-heroic and not guarding the door.",
      "visual_evidence_needed": "Readable time passage and chair-distance change.",
      "imagegen_risk": "If distance change is too subtle, it repeats the opener.",
      "visual_scene_questions": [
        "Use floor tiles, wall marks, or shadows to prove chair movement?",
        "Is Zuv absent stronger than a partial seated figure?"
      ]
    },
    {
      "slide_number": 4,
      "story_role": "escalation",
      "exact_on_image_text": "he moves the chair back.",
      "viewer_question_created": "Does Aachu accept the care once it stops pressing on the door?",
      "micro_action": "Aachu's hand pulls the charger or folded cloth through a cracked door while the chair remains farther back and empty.",
      "emotional_shift": "Aachu regains agency without needing to explain herself.",
      "face_visibility_requirement": "Aachu hand only; face not required.",
      "visual_evidence_needed": "Cracked door, object crossing threshold, chair visibly backed away.",
      "imagegen_risk": "Door, cable, and hand anatomy can become confusing if the angle is not simple.",
      "visual_scene_questions": [
        "Which object crosses the threshold most clearly?",
        "What camera angle avoids impossible hand/door geometry?"
      ]
    },
    {
      "slide_number": 5,
      "story_role": "payoff",
      "exact_on_image_text": "and stays where i can find him.",
      "viewer_question_created": "The hook is answered: quiet did not make her unlovable.",
      "micro_action": "The slightly open doorway shows a half-empty glass and charging phone; outside, the chair remains nearby but not blocking, with Zuv implied down the hall or softly partial.",
      "emotional_shift": "The answer moves from fear to a shared rule of care.",
      "face_visibility_requirement": "At most one readable face; do not force a two-face close-up.",
      "visual_evidence_needed": "Used objects, door acceptance, chair in the right distance, no vigil posture.",
      "imagegen_risk": "If Zuv is shown too centrally, he becomes saintly; if acceptance is too subtle, the payoff weakens.",
      "visual_scene_questions": [
        "Should Zuv be implied, partial, or absent in the payoff?",
        "How visible must Aachu be for acceptance to read without forcing a face?"
      ]
    }
  ],
  "retention_notes": [
    "Slide 1 creates the central question: what does love do outside a closed door?",
    "Slide 2 earns the swipe by showing care without pressure.",
    "Slide 3 keeps the viewer because the chair changes distance instead of repeating the same waiting beat.",
    "Slide 4 creates the first proof of acceptance through an object crossing the threshold.",
    "Slide 5 lands the share trigger: staying gentle when someone goes quiet."
  ],
  "required_revisions": [
    "Prompt QA must not force both people into every slide despite the generic master prompt wording.",
    "Visual Scene Discussion must solve chair-distance readability and door-threshold geometry before prompt writing.",
    "Reject any payoff that uses a hug, apology speech, sleeping Zuv, or saintly waiting pose."
  ],
  "failure_codes": []
}
```
