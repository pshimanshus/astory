# Swipe Retention Pass - Arjun

Run: `2026-06-14_02-21_hard-to-love`
Agent: `Swipe Retention Critic - Arjun`
Persona: `.agents/skills/astory/personas/story-room/swipe-retention-critic.md`
Approved idea: `The Chair Outside The Door`

This is a bounded retention critique of the emerging five-slide storyboard. It
does not overwrite shared story artifacts, does not write final prompts, and
does not call imagegen.

## Evidence Ledger

| Artifact | Path | What I Used | Gap Or Risk |
| --- | --- | --- | --- |
| Creative brief | `runs/2026-06-14_02-21_hard-to-love/input/creative_brief.json` | The source question family is "am i hard to love / handle / understand / not enough / worth the risk?"; concept references are emotional/text inspiration only; creator explicitly says not to force both people into every slide. | The question cadence is useful, but repeating question after question can turn the carousel into a quote-card instead of a story machine. |
| Creator corrections | `runs/2026-06-14_02-21_hard-to-love/planning/creator_direction_notes.md` | Active constraints: not generic, do not force both people into every slide, scene must prove the line, concept style is not house style, and closed packets matter. | "Vulnerable line alone is not enough" is the retention law here. Every slide needs a new visible piece of proof. |
| Memory recall | `runs/2026-06-14_02-21_hard-to-love/planning/memory_recall.md` | Use visible artifacts and direct markdown evidence only; avoid repeated close-angle two-face defaults; concept screenshots are not style truth. | Automated recall returned no run-specific cited results, so I am not using memory as taste proof beyond the cited direct notes. |
| Selected idea | `runs/2026-06-14_02-21_hard-to-love/planning/selected_idea.json` | Locked angle: Aachu fears going quiet makes her hard to love; Zuv answers by staying nearby without forcing the door. Required corrections: practical chair, no sleeping martyr, no dramatic embrace, object continuity must read. | The idea wins only if objects visibly change. If the chair/water/charger/cloth/light/door crack are too subtle, the swipe dies in the middle. |
| Story Director pass | `runs/2026-06-14_02-21_hard-to-love/debates/story_room/story_director_pass.md` | Five-slide spine: hook, water/charger, chair-distance/time passage, object accepted through cracked door, final "stays where i can find him" payoff. | Strong structure. Middle text is sometimes too abstract, and the proposed final line risks repeating the same presence beat instead of paying back the hook. |
| Pacing Editor pass | `runs/2026-06-14_02-21_hard-to-love/debates/story_room/pacing_editor_pass.md` | Five beats with sharper text: `or do you know where to leave the water?`, `you learned the chair distance`, `the words came later. the charger came first.`, `i was not hard to love. i was hard to rush.` | Best retention copy so far, but slide 3 and slide 5 still require phone-clear object proof or they become clever captions floating over a hallway. |
| House style | `.agents/skills/astory/references/house-style-contract.md` | Airy off-white watercolor-and-ink, exact readable handwritten text, generous upper-middle negative space, and scene logic as a hard gate. | The hallway must stay warm and clear without going dark, yellow, theatrical, or prop-cluttered. Text must not cover the door crack or object continuity. |
| Master prompt context | `.agents/skills/astory/references/master-prompt.md` | Later prompts must protect identity anchors, best-illustration finish, native `1080x1080 px`, exact text, no yellow/parchment, and no prompt overload. | Its generic "same two people every slide" line conflicts with this run's creator correction and must not steer storyboard retention. |
| Identity anchor context | `references/identity/`; `runs/2026-06-14_02-21_hard-to-love/input/identity/` | Aachu and Zuv identity files exist. Retention can use object-only slides, but any visible face later must be large enough for anchors to protect likeness. | Too many faceless slides can make the story anonymous. At least one late Aachu presence should be readable without forcing both people into frame. |

## Premise Lock

The retention contract is not "sad girl behind door, patient boy outside." It is:
Aachu fears quiet makes her hard to love; Zuv proves the opposite by learning the
distance where care reaches her without rushing her.

Do not change: practical chair, water, charger, folded cloth, light under the
door, door crack, and changed chair distance. Do not add sleeping-martyr Zuv,
dramatic hug, speech-bubble explanation, generic reassurance, or both-person
coverage in every slide.

## retention_risks

1. **Abstract-question sag in the middle.** The Story Director's slide 2 and 3
   questions are emotionally accurate, but two question slides after the hook
   can feel like the same thought wearing different clothes. The thumb needs a
   new object state, not another phrasing of quietness.
2. **Slide 3 is the leak if chair distance is not unmistakable.** "Time passed"
   is not visible by itself. If the chair shift, folded cloth, changed light, and
   water state do not read on a phone, slide 3 repeats slide 1 and loses the
   swipe.
3. **The payoff cannot only be "he stayed."** Staying is already implied by the
   chair. The last slide has to reframe Aachu's fear: she was not hard to love,
   she was hard to rush. That is the save line.
4. **Prop inventory risk.** Water, charger, cloth, chair, light, and door crack
   are continuity proof, not a checklist. One object should lead each slide, with
   the others supporting.
5. **Identity evaporation risk.** Not forcing both faces is correct, but if all
   five slides are doors and props, the story can become anonymous. Slide 4 or 5
   should give Aachu a small readable presence: fingers, cheek/eye, or partial
   profile, depending on what stays physically clean.
6. **Saintly-Zuv drift.** Any seated/sleeping/waiting-all-night version makes the
   carousel about his suffering. Keep him practical: hand placing, body turning
   away, presence implied, chair findable.
7. **Phone-screen clarity.** Door crack, cable path, chair distance, and water
   level are small details. If text covers them, or if the angle is too cute, the
   proof vanishes.

## slides_that_earn_place

| Slide | Verdict | Why It Earns The Swipe |
| --- | --- | --- |
| 1 | Keep | The hook detonates instantly: closed door, empty chair, and `am i hard to love when i go quiet?` create a real viewer question. |
| 2 | Keep with concrete copy | Zuv's first care action answers the opener without resolving it. Water and charger make "near, not knocking" physical. |
| 3 | Keep, conditional | The chair-distance beat is the spine. It proves learned care over time, but only if the visual change is obvious. |
| 4 | Keep | Aachu accepting the charger/cloth before words gives her agency. This is the first "care reached her" proof. |
| 5 | Keep | The final frame can pay back all five swipes if the used objects and open threshold earn the line `i was not hard to love. i was hard to rush.` |

## slides_to_rewrite

| Slide | Current Risk | Rewrite Direction |
| --- | --- | --- |
| 2 | `when i want you near, not knocking?` is good, but still abstract. It tells me the rule instead of making me notice the water. | Use the Pacing version: `or do you know where to leave the water?` It is stranger, more couple-owned, and makes the image do work. |
| 3 | `when one more question feels too loud?` repeats the quiet/pressure idea from slide 1 and 2. | Use `you learned the chair distance` or a close variant. The swipe exists because the chair moved, not because the feeling got restated. |
| 4 | `he moves the chair back.` gives away the slide 3/4 mechanism too flatly if used as the whole beat. | Prefer `the words came later. the charger came first.` The charger crossing the threshold is acceptance before explanation. |
| 5 | `and stays where i can find him.` is tender, but it is the same presence idea again. It may close softly instead of sharply. | Use `i was not hard to love. i was hard to rush.` This finally answers the first question instead of merely describing Zuv's location. |

## hook_recommendation

Keep the hook exactly:

`am i hard to love when i go quiet?`

Do not add another line, a subtitle, or a visible crying face. The first slide
works because it makes the viewer ask what love does outside the closed door:
leave, knock, or learn the distance. The chair should be close enough to feel
chosen and far enough to avoid pressure. If slide 1 shows too much of Zuv or
Aachu, it spends mystery before the carousel earns it.

## payoff_recommendation

Use the final line:

`i was not hard to love. i was hard to rush.`

But only if the image has already shown acceptance: charger in use or crossing
the threshold, water lowered, cloth moved inside, door open enough to breathe,
chair still findable but not blocking. Without those object states, the line
turns into generic reassurance. With them, it pays the viewer back for every
swipe.

Do not close on a hug, apology, speech bubble, forehead-kiss rescue, or Zuv
asleep in the chair. The ending should feel like the room got quieter because
the care worked, not because the couple performed closure.

## transition-by-transition swipe logic

| Transition | Viewer Question | The Next Slide Must Answer By Showing | Leak To Avoid |
| --- | --- | --- | --- |
| Slide 1 -> Slide 2 | "What does love do outside this door?" | Zuv leaves water/charger where the door can still open, then exits pressure. | A hand on the handle, a knock, or a sad full-body Zuv waiting for sympathy. |
| Slide 2 -> Slide 3 | "Was that one nice act, or does he understand the rhythm?" | Chair moved back, cloth added, light changed, water state changed: time and calibration. | Same camera, same chair, same closed door with extra props. That is a dead swipe. |
| Slide 3 -> Slide 4 | "Did the care reach her before words did?" | Door crack, charger/cloth crossing threshold, Aachu's small readable acceptance. | A fully open door or face-to-face scene that resolves too early. |
| Slide 4 -> Slide 5 | "What was the real answer to the first question?" | Used objects and a findable chair prove she was loved at her pace. | "He stayed" as a soft repeat, or a dramatic reconciliation that throws away the object story. |

## Recommended Retention Copy Spine

This is critique copy direction, not final prompt writing:

| Slide | Retention Job | Recommended On-Image Text | Primary Visual Proof |
| --- | --- | --- | --- |
| 1 | Recognition hook | `am i hard to love when i go quiet?` | Closed door, warm light strip, practical chair near but not pressing. |
| 2 | Care without pressure | `or do you know where to leave the water?` | Water and charger placed outside the door swing; Zuv leaving frame. |
| 3 | Learned distance | `you learned the chair distance` | Chair one tile back, folded cloth, changed light/water state. |
| 4 | Acceptance before explanation | `the words came later. the charger came first.` | Charger or cloth crosses the cracked-door threshold; Aachu partially present. |
| 5 | Payoff | `i was not hard to love. i was hard to rush.` | Used objects, slightly open door, chair still nearby but not heroic. |

## JSON-Ready Object

```json
{
  "agent_role": "Swipe Retention Critic - Arjun",
  "run_id": "2026-06-14_02-21_hard-to-love",
  "title": "The Chair Outside The Door",
  "scope": "bounded_retention_critique_only",
  "premise_lock": {
    "must_preserve": [
      "Aachu fears going quiet makes her hard to love.",
      "Zuv proves love through calibrated presence, not pressure.",
      "Object continuity must remain visible: chair distance, water, charger, folded cloth, light, and door crack.",
      "Both Aachu and Zuv must not be forced into every slide."
    ],
    "must_not_use": [
      "sleeping-martyr Zuv",
      "dramatic hug",
      "speech-bubble explanation",
      "generic reassurance",
      "forced two-person slide coverage"
    ]
  },
  "retention_risks": [
    "Middle slides can sag if they remain abstract questions instead of concrete object-state changes.",
    "Slide 3 leaks retention if chair distance and time passage are not phone-readable.",
    "The payoff weakens if it only repeats that Zuv stayed nearby.",
    "Too many object-only slides can make Aachu anonymous unless slide 4 or 5 gives her readable partial presence.",
    "Any waiting-all-night staging turns Zuv into a martyr and breaks the premise."
  ],
  "slides_that_earn_place": [
    {
      "slide": 1,
      "verdict": "keep",
      "reason": "The hook is instantly recognizable and creates the central question."
    },
    {
      "slide": 2,
      "verdict": "keep_with_rewrite",
      "reason": "The first practical care action is necessary, but the copy should point at the water instead of restating nearness."
    },
    {
      "slide": 3,
      "verdict": "keep_conditionally",
      "reason": "Chair distance proves learned care, but only if the visual change is unmistakable."
    },
    {
      "slide": 4,
      "verdict": "keep_with_rewrite",
      "reason": "Accepted care before words gives Aachu agency and earns the final swipe."
    },
    {
      "slide": 5,
      "verdict": "keep_with_payoff_rewrite",
      "reason": "The final line must reframe the hook, not merely say he stayed."
    }
  ],
  "slides_to_rewrite": [
    {
      "slide": 2,
      "replace_or_pressure": "Prefer `or do you know where to leave the water?` over `when i want you near, not knocking?`."
    },
    {
      "slide": 3,
      "replace_or_pressure": "Prefer `you learned the chair distance` over another abstract question."
    },
    {
      "slide": 4,
      "replace_or_pressure": "Prefer `the words came later. the charger came first.` over a flat chair-back explanation."
    },
    {
      "slide": 5,
      "replace_or_pressure": "Prefer `i was not hard to love. i was hard to rush.` over `and stays where i can find him.`"
    }
  ],
  "hook_recommendation": {
    "text": "am i hard to love when i go quiet?",
    "action": "Keep exact hook. Do not add extra explanation or force a face reveal."
  },
  "payoff_recommendation": {
    "text": "i was not hard to love. i was hard to rush.",
    "condition": "Only use if the final frame clearly shows accepted care through changed objects and the findable chair."
  },
  "transition_swipe_logic": [
    {
      "transition": "1_to_2",
      "viewer_question": "What does love do outside the closed door?",
      "required_answer": "Care placed nearby without knocking or blocking the door."
    },
    {
      "transition": "2_to_3",
      "viewer_question": "Was it one sweet act or learned restraint?",
      "required_answer": "Chair distance, cloth, light, and water state prove time/calibration."
    },
    {
      "transition": "3_to_4",
      "viewer_question": "Did the care reach Aachu before words did?",
      "required_answer": "Cracked door and charger/cloth crossing the threshold."
    },
    {
      "transition": "4_to_5",
      "viewer_question": "What is the answer to the first question?",
      "required_answer": "Used objects and findable chair prove she was hard to rush, not hard to love."
    }
  ],
  "scores": {
    "first_slide_hook": 5,
    "swipe_curiosity": 4,
    "beat_progression": 4,
    "final_payoff": 4,
    "text_economy": 4,
    "phone_screen_clarity": 3.5
  },
  "score_basis": "Scores are for the emerging five-slide storyboard under this pass's recommended retention rewrites; phone-screen clarity remains the largest unresolved visual risk.",
  "failure_codes_flagged_as_risks": [
    "WEAK_PAYOFF",
    "TEXT_UNREADABLE",
    "VISUAL_GENERIC_RISK",
    "SCENE_LOGIC_CONTRADICTION"
  ],
  "hard_blocker": null
}
```
