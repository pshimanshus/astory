# Pacing Editor Pass - Nina

Run: `2026-06-14_02-21_hard-to-love`
Agent: `Pacing Editor - Nina`
Persona: `.agents/skills/astory/personas/story-room/pacing-editor.md`
Approved idea: `The Chair Outside The Door`

This is a pacing-room contribution only. It does not overwrite shared story
artifacts, and it does not write final prompts or images.

## Evidence Ledger

| Artifact | Path | What I Used | Gap Or Risk |
| --- | --- | --- | --- |
| Creative brief | `runs/2026-06-14_02-21_hard-to-love/input/creative_brief.json` | The concept question family around "am i hard to love / handle / understand"; the creator constraint not to force both people into every slide; final style must be airy best-illustration watercolor-and-ink, not the dark concept style. | Story must avoid becoming a quote-card that merely repeats the question family. |
| Idea approval | `runs/2026-06-14_02-21_hard-to-love/docs/approvals.md` | `HITL_IDEA_LOCK` is approved at `2026-06-14T11:14:34+05:30`; creator said to proceed to storyboard. | `selected_idea.json` still says `hitl_status: pending`, so the approval file is the fresher state. |
| Selected idea | `runs/2026-06-14_02-21_hard-to-love/planning/selected_idea.json` | Locked angle: Aachu worries that going quiet makes her hard to love; Zuv answers by staying nearby without forcing the door open. Required corrections include practical chair, no sleeping martyr, no dramatic embrace, and visible object continuity. | If the story makes Zuv too perfect or too theatrical, the idea fails its own risk list. |
| Scene landing preview | `runs/2026-06-14_02-21_hard-to-love/planning/scene_landing_preview.md` | The preview's five-part object arc: door/chair, water and charger, time passing through changed objects, cracked door, accepted care as payoff. | The mini arc is strong but can become visually repetitive unless each slide changes distance, object state, or viewer knowledge. |
| Memory recall | `runs/2026-06-14_02-21_hard-to-love/planning/memory_recall.md` | Use visible artifacts and direct markdown only; do not treat concept screenshots as style; avoid repeated two-face close angles; final prompts later need native `1080x1080 px`. | Automated recall had no run-specific cited results, so no uncited memory claims are used. |
| Creator corrections | `runs/2026-06-14_02-21_hard-to-love/planning/creator_direction_notes.md` | Active constraints: not generic, do not force both people into every slide, scene must prove the line, concept style is not house style, use closed packets. | The "closed packet" correction is process-critical; story content still needs its own proof. |
| House style | `.agents/skills/astory/references/house-style-contract.md` | Negative space for handwritten text, neutral off-white paper, scene logic as hard gate, exact text later, tiny brandmark later. | Door/hallway scenes can go too dark or parchment if the prompt room does not keep paper neutral. |
| Master prompt | `.agents/skills/astory/references/master-prompt.md` | Identity references are highest priority later; best-illustration style controls finish; concept references control mood/story only; prompts must stay compact. | Master prompt says the same two people must appear in every slide, but creator notes override the impulse to force both into every slide. |
| Identity anchors | `references/identity/aachu/`, `references/identity/zuv/`, `references/identity/together/` | Repo anchors exist for Aachu, Zuv, and together/body-language support. Pacing should keep face-visible slides close enough for real identity anchors when faces appear. | This pass did not perform final reference visibility proof; that belongs before imagegen, not story pacing. |

## Premise Lock

The approved story is not "sad girl behind a door." It is: Aachu goes quiet and
fears that quiet makes her hard to love; Zuv proves love by staying practically
near, learning the right distance, and letting objects carry care before words
return.

Must preserve:

- The closed door, the practical chair, and the question: `am i hard to love when i go quiet?`
- The object continuity: water level, charger path, folded cloth, light under the door, door crack, chair distance.
- The creator correction that both people do not need to be visible in every slide.
- Zuv's restraint. He can act, leave objects, adjust distance, and stay available; he cannot become a hallway martyr.
- A payoff without a hug, speech, apology monologue, or savior pose.

Must not change:

- This is about quiet shutdown, not a general "I'm difficult" label.
- The answer must be proved through observed behavior, not explained in caption logic.
- The chair stays practical. It is a tool of presence, not a throne of suffering.

## Tension Ladder

1. Recognition: the closed door and empty chair make the viewer ask whether quietness will make someone leave or force their way in.
2. First answer: Zuv places care near the door without demanding access, changing the question from "will he stay?" to "does he understand how to stay?"
3. Pressure turn: time passes, and the chair moves to a better distance. The story proves this is learned care, not one dramatic gesture.
4. Acceptance: the door cracks open and one object crosses the threshold. Aachu still does not have to explain, but the care has reached her.
5. Payoff: the changed objects answer the hook. She was not hard to love; she was hard to rush.

## Slide Economy

Recommended slide count: **5**.

Five is the count where the object logic has enough time to become evidence
instead of decor. Four can tell the plot, but it rushes the proof. Six starts
inventorying props and turns the story into a patience performance.

Why fewer fails:

- Three slides collapses the arc into hook, care, payoff. The viewer never sees time, adjustment, or acceptance, so Zuv feels magically correct.
- Four slides can work only by merging either "time passing" with "acceptance" or "acceptance" with "payoff." Both merges weaken the central proof: quiet love needs duration and changed evidence.
- Fewer than five makes the chair a symbol. Five makes it behavior.

Why more dilutes:

- A sixth slide would almost certainly split water, charger, cloth, or chair distance into separate proof beats. That is not story; that is prop accounting.
- Extra waiting slides make Zuv look saintly, which the selected idea explicitly rejects.
- More than five risks repeating the same doorway composition until swipe tension drops.

Cut or keep verdict:

| Beat | Verdict | Reason |
| --- | --- | --- |
| Closed door + practical chair hook | keep | This is the recognition slide and the only place the question should hit cleanly. |
| Zuv places water/charger and leaves frame | keep | This proves restraint without speech. |
| Time passes through changed chair distance/light/cloth | keep | This is the slide that turns one nice act into learned care. |
| Door crack + object accepted | keep | This is the first proof that care reached Aachu before explanation. |
| Final changed-object answer | keep | This pays off the question without a hug or speech. |
| Separate slide of Zuv waiting/sleeping outside | cut | Martyr staging. It flatters Zuv instead of proving the relationship rule. |
| Separate slide for every care object | cut | Prop inventory. The swipe-through will sag. |
| Dramatic embrace/apology finale | cut | Replaces the premise with generic romance closure. |
| Aachu crying alone behind the door | cut | Sad quote-card gravity. It makes the viewer pity her instead of recognizing the care rule. |

## Decision Table

These are pacing text proposals for story-room discussion, not prompt-lock copy.

| Slide | Keep/Cut | Story Role | On-Image Text | micro_action | Swipe Reason | Face Visibility | Visual Risk | Prompt Handoff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | keep | setup | `am i hard to love when i go quiet?` | A closed bedroom door leaks a thin line of warm light; an empty practical chair sits nearby but not pressed against the door. | Viewer wants to know whether the person outside knocks, leaves, or learns the right distance. | No faces needed; identity is not the job of this slide. | Door plus text can become generic sadness if the chair is too theatrical or the hallway too dark. | Need a quiet hallway composition with readable upper-middle text and a chair that feels recently placed, not staged. |
| 2 | keep | escalation | `or do you know where to leave the water?` | Zuv's hand places a glass and phone charger beside the door where the door will not hit them; his body is already turning away. | The care is active, but he is not forcing a response. | Zuv can be partial: hand, forearm, side posture. If his face appears, keep it readable enough for anchors. | If he kneels sadly or presses against the door, it becomes rescuer theater. | Visual scene must prove placement logic: water and charger reachable, door swing clear, no crowding. |
| 3 | keep | bridge | `you learned the chair distance` | Time has passed: chair shifted back, folded cloth added over the chair, light under the door changed, water level slightly lower. | Viewer sees this is learned restraint, not one perfect gesture. | No face required; this should be an object-continuity slide. | Repeating slide 1 too closely will feel static. Too many objects will feel like a care-kit meme. | Need a different camera distance or angle from slide 1, with object-state changes legible on a phone. |
| 4 | keep | escalation | `the words came later. the charger came first.` | Door is cracked; charger cable crosses the threshold or disappears inside; Aachu's fingers or partial face appears near the opening. | The viewer gets first evidence that Aachu accepted care without being required to explain. | Aachu should be at least partially identity-safe here: close hand/face detail if shown, not a tiny hidden figure. | If her face is hidden on every slide, the carousel may lose Aachu-specific emotional ownership. | Visual discussion must decide whether this is fingers at the crack, cheek/eye in soft partial view, or charger-only threshold proof. |
| 5 | keep | payoff | `i was not hard to love. i was hard to rush.` | The door is open enough to show the glass empty or half-empty, cloth pulled inside, charger in use, and chair still nearby but unoccupied or calmly angled away. | The answer lands through changed evidence, not a confession scene. | Prefer Aachu readable in soft partial profile or three-quarter view; Zuv can remain implied or distant. Do not force both faces. | A hug, speech bubble, or face-to-face reconciliation would erase the quiet premise. | Need final frame that feels accepted, not solved: no dramatic embrace, no overlit saint pose, no sudden perfect couple close-up. |

## Slides To Protect

- Slide 1: protect the exact hook and the empty chair. This is the send-this-to-him recognition.
- Slide 2: protect the first practical care action. Without it, Zuv's love becomes abstract.
- Slide 3: protect the chair-distance/time-passing beat. This is the spine of the pacing.
- Slide 4: protect the first acceptance evidence. The door crack must matter before the payoff.
- Slide 5: protect the changed-object answer. The final image should feel quieter than a hug and stronger because of it.

## Slides To Cut

- Any "he waits all night in the chair" slide.
- Any separate object-delivery slide after slide 2 unless it changes viewer knowledge.
- Any Aachu-only crying slide that asks pity to do the story work.
- Any direct explanatory text-message or speech-bubble slide.
- Any final hug, apology, or grand reassurance slide.

## Pacing Risks

- Static doorway risk: five slides can still feel like one drawing repeated unless every beat changes distance, object state, or threshold openness.
- Saintly-Zuv risk: keep him practical and lightly present. The story is not "look how patiently he suffered."
- Over-subtle risk: object changes must be readable at phone size: glass level, charger cable, cloth location, door crack, and chair angle cannot be tiny Easter eggs.
- Identity evaporation risk: not forcing both people is correct, but at least one later slide should give Aachu enough readable presence to keep this from becoming anonymous.
- Text density risk: each slide should carry one short line. No paragraphing, no over-explaining the metaphor.

## Scoring

| Criterion | Score | Nina's Note |
| --- | --- | --- |
| pacing fit | 5/5 | Five beats match the preview's natural proof chain. |
| slide necessity | 4.5/5 | All five keepers change viewer knowledge; only risk is slide 3 if visual scene cannot make time legible. |
| swipe retention | 4.5/5 | Each swipe asks a new question, but visual variety must be actively protected. |
| payoff timing | 5/5 | The final line lands after acceptance evidence, not before it. |
| simplicity | 4/5 | The object continuity is simple emotionally, but execution can clutter if too many props are shown. |
| visual variety | 4/5 | Strong if angles and threshold states vary; weak if every frame is a centered door. |

## Retention Pass

- Slide 1 to 2: "Will he push, leave, or understand the quiet?"
- Slide 2 to 3: "Does he only do one sweet thing, or does he learn the rhythm?"
- Slide 3 to 4: "Will the care reach her before words do?"
- Slide 4 to 5: "What is the answer to the first question if no one gives a speech?"

## Visual Handoff Questions

- How do we make the chair-distance change obvious without drawing a technical before/after?
- Which object is the hero continuity object: water, charger, cloth, or chair angle? Pick one primary and two supporting details.
- Where can Aachu appear without turning the quiet into a dramatic reveal?
- Can slide 2 show enough Zuv action while still making his restraint clear?
- What camera variation prevents five doorway-adjacent slides from flattening?

## Blocker Pass

No hard blocker from pacing. Proceed to Story Room merge with these warnings:

- Do not expand beyond five without a new story reason that changes viewer knowledge.
- Do not compress below five unless the coordinator accepts losing either time passage or acceptance proof.
- Visual Scene Discussion must solve static-door repetition before prompt lock.

## JSON-Ready Object

```json
{
  "agent_role": "Pacing Editor - Nina",
  "premise_lock": {
    "must_preserve": [
      "Aachu fears her quiet makes her hard to love.",
      "Zuv answers through practical nearby care without forcing the door open.",
      "The practical chair, closed door, water, charger, cloth, light, door crack, and changed object states carry the proof.",
      "Both people must not be forced into every slide.",
      "No sleeping martyr, dramatic embrace, savior pose, or generic sad quote-card staging."
    ],
    "must_not_change": [
      "Do not turn quiet shutdown into a general difficult-girl label.",
      "Do not make the answer a speech or hug.",
      "Do not copy the dark/magenta/orange concept style.",
      "Do not pad the story with separate object inventory slides."
    ],
    "emotional_truth": "Some people are not asking to be decoded immediately; they are asking not to be abandoned while they become speakable again.",
    "relationship_dynamic": "Aachu retreats into quiet; Zuv stays close enough to be found and far enough not to rush her."
  },
  "slide_count_decision": {
    "recommended_slide_count": 5,
    "why_this_count": "Five lets the story move from question, to practical care, to learned distance, to accepted care, to quiet answer. Every keeper changes the viewer's knowledge.",
    "why_fewer_fails": "Three collapses proof into symbol, and four forces the story to merge time passage with acceptance or acceptance with payoff. The central evidence needs both duration and changed objects.",
    "why_more_dilutes": "Six or more starts splitting water, charger, cloth, and chair into separate proof beats, which becomes prop accounting and saintly waiting instead of story.",
    "cut_or_keep_verdict": [
      {
        "beat": "Closed door and practical chair hook",
        "verdict": "keep",
        "reason": "Recognition slide and clean emotional question."
      },
      {
        "beat": "Zuv places water and charger, then leaves frame",
        "verdict": "keep",
        "reason": "Active care plus restraint."
      },
      {
        "beat": "Time passes through changed chair distance, light, cloth, and water level",
        "verdict": "keep",
        "reason": "Turns one nice act into learned care."
      },
      {
        "beat": "Door crack and object accepted",
        "verdict": "keep",
        "reason": "First proof care reached Aachu before explanation."
      },
      {
        "beat": "Changed-object payoff",
        "verdict": "keep",
        "reason": "Answers the hook without speech or hug."
      },
      {
        "beat": "Zuv waiting or sleeping outside the door",
        "verdict": "cut",
        "reason": "Martyr staging."
      },
      {
        "beat": "Separate slide for every care object",
        "verdict": "cut",
        "reason": "Prop inventory and swipe dilution."
      },
      {
        "beat": "Dramatic embrace or apology finale",
        "verdict": "cut",
        "reason": "Generic romance closure that replaces the premise."
      }
    ]
  },
  "slide_beat_contract": [
    {
      "slide_number": 1,
      "story_role": "setup",
      "exact_on_image_text": "am i hard to love when i go quiet?",
      "viewer_question_created": "Will the person outside knock, leave, or learn the right distance?",
      "micro_action": "A thin line of warm light leaks under a closed door while a practical chair sits nearby but not pressed against it.",
      "emotional_shift": "Fear of abandonment becomes a visible threshold.",
      "face_visibility_requirement": "No faces required.",
      "visual_evidence_needed": "Closed door, empty chair, warm light strip, negative space for text.",
      "imagegen_risk": "Generic sad door or too-dark hallway.",
      "visual_scene_questions": [
        "How close should the chair be so it reads as care, not surveillance?",
        "What camera angle keeps the text readable?"
      ]
    },
    {
      "slide_number": 2,
      "story_role": "escalation",
      "exact_on_image_text": "or do you know where to leave the water?",
      "viewer_question_created": "Does Zuv understand how to care without forcing access?",
      "micro_action": "Zuv's hand places water and a charger where the door will not hit them, while his body turns away.",
      "emotional_shift": "Love becomes practical instead of invasive.",
      "face_visibility_requirement": "Partial Zuv is acceptable; if his face appears, it must be readable enough for identity anchors.",
      "visual_evidence_needed": "Door swing clearance, water glass, charger, hand leaving frame.",
      "imagegen_risk": "Kneeling rescuer pose or cluttered prop pile.",
      "visual_scene_questions": [
        "Can the door-swing logic be shown clearly?",
        "Should Zuv be hand-only or partial body?"
      ]
    },
    {
      "slide_number": 3,
      "story_role": "bridge",
      "exact_on_image_text": "you learned the chair distance",
      "viewer_question_created": "Was this one nice act, or learned patience?",
      "micro_action": "The chair is now shifted back, a folded cloth sits over it, the door light has changed, and the water level is lower.",
      "emotional_shift": "The story moves from gesture to pattern.",
      "face_visibility_requirement": "No faces required; object continuity is the face of this slide.",
      "visual_evidence_needed": "Chair position change, folded cloth, changed light, readable glass level.",
      "imagegen_risk": "Too similar to slide 1 or too many tiny props.",
      "visual_scene_questions": [
        "What angle makes changed chair distance obvious?",
        "Which two object changes are primary enough for phone-size readability?"
      ]
    },
    {
      "slide_number": 4,
      "story_role": "escalation",
      "exact_on_image_text": "the words came later. the charger came first.",
      "viewer_question_created": "Has Aachu accepted care before she can explain herself?",
      "micro_action": "The door is cracked and the charger cable crosses the threshold or disappears inside; Aachu's fingers or partial face is visible near the opening.",
      "emotional_shift": "The quiet starts letting care in.",
      "face_visibility_requirement": "Prefer partial Aachu presence close enough to protect identity if her face is shown.",
      "visual_evidence_needed": "Door crack, threshold, cable path, one accepted object.",
      "imagegen_risk": "Overdramatic reveal or hidden anonymous figure.",
      "visual_scene_questions": [
        "Should Aachu be shown through fingers, cheek/eye, or only accepted object movement?",
        "How open can the door be before the tension resolves too early?"
      ]
    },
    {
      "slide_number": 5,
      "story_role": "payoff",
      "exact_on_image_text": "i was not hard to love. i was hard to rush.",
      "viewer_question_created": "What was the real answer to the hook?",
      "micro_action": "The door is open enough to show the glass used, cloth pulled inside, charger in use, and chair still nearby but calm and unoccupied.",
      "emotional_shift": "The premise resolves into a care rule rather than a rescue scene.",
      "face_visibility_requirement": "Aachu should be readable in soft partial view if shown; Zuv can stay implied or distant. Do not force both faces.",
      "visual_evidence_needed": "Used care objects, open threshold, chair still available, no hug.",
      "imagegen_risk": "Generic couple reconciliation or sudden dramatic embrace.",
      "visual_scene_questions": [
        "How much of Aachu should be visible for identity without making it a reveal shot?",
        "Where is Zuv if the chair is empty: implied nearby, off-frame, or gently distant?"
      ]
    }
  ],
  "retention_notes": [
    "Slide 1 creates the question of whether quietness leads to pressure or abandonment.",
    "Slide 2 earns the swipe by showing care without access.",
    "Slide 3 earns the swipe by proving learned distance over time.",
    "Slide 4 earns the swipe by showing acceptance before explanation.",
    "Slide 5 pays off the first question through changed objects."
  ],
  "required_revisions": [
    "Visual Scene Discussion must solve static-door repetition.",
    "The merged storyboard should choose one hero continuity object and keep supporting props secondary.",
    "At least one later slide should give Aachu readable presence without forcing both people into every slide."
  ],
  "failure_codes": []
}
```
