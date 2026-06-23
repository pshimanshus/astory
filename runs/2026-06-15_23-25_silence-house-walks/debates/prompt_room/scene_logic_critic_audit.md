# Scene Logic Critic Audit

Run: `2026-06-15_23-25_silence-house-walks`
Agent: Samar, Scene Logic Critic
Stage: pre-imagegen prompt QA

## status

`revise`

The scene is close and the chosen option `1B` is the right direction. It is not
a block because the setup is physically possible and emotionally legible. But it
needs a prompt repair before imagegen: the image must prove "the house starts
walking carefully" through visible object behavior, not through the prompt
explaining that the door, curtain, and chair "make the house feel" careful.

Cover-the-text result: partial pass. With the text hidden, Aachu silent and Zuv
stepping in carefully reads. The house itself being careful is still weaker than
the human being careful.

## Evidence Basis

- Prompt reviewed: `runs/2026-06-15_23-25_silence-house-walks/prompts/slide_01_prompt.txt`
- Scene options reviewed: `runs/2026-06-15_23-25_silence-house-walks/planning/scene_options.json`
- Selected scene reviewed: `runs/2026-06-15_23-25_silence-house-walks/planning/selected_scenes.json`
- Landing preview reviewed: `runs/2026-06-15_23-25_silence-house-walks/planning/scene_landing_preview.md`
- Contracts reviewed: `failure-taxonomy.md`, `house-style-contract.md`, `imagegen-contract.md`

No alternate copy and no carousel recommendation. The creator asked for one
single illustration using the supplied copy as-is.

## contradictions

1. **Cup clink logic is underdrawn.**
   The prompt says Zuv is "holding a cup with both hands so it will not clink,"
   but a lone cup has no visible clink source. The scene options had stronger
   logic: cup and saucer held apart. The current prompt may generate a cup held
   carefully, but the viewer will not know what noise is being prevented.

   Required fix: restore a visible clink-prevention detail. Use one clear prop
   behavior: cup lifted slightly away from its saucer, or a teaspoon pinned still
   against the cup rim. Do not add both if it crowds the hand pose.

2. **House-careful proof is partly mood language.**
   "Half-open door, still curtain, and slightly angled chair" can read as quiet
   decor, not as the house physically walking carefully. The chair especially
   risks looking randomly crooked unless its relationship to silence is clear.

   Required fix: make one house object visibly prevented from making sound. Best
   repair: Zuv's fingertips lightly hold the door edge/handle so it does not
   swing or creak, while the chair remains a subtle secondary object. The door
   then becomes the house behaving carefully instead of a generic background
   detail.

## pose_risks

1. **One lifted foot plus both hands on a cup can force an awkward balancing pose.**
   Keep Zuv upright, not crouched, with the lifted socked foot only slightly off
   the floor. Do not make him tiptoe with bent knees, twisted hips, or a hunched
   doorway lean.

2. **Cup-hand detail can create bad fingers.**
   If the prompt asks for cup, saucer, spoon, both hands, and a stepping pose all
   at once, hand anatomy risk rises. Choose one clean clink-prevention prop
   behavior and keep the hands simple.

3. **Aachu lower-right stillness must not become theatrical sadness.**
   Keep hands resting naturally in her lap, shoulders relaxed, soft
   three-quarter profile. Avoid collapsed posture, hidden face, or a hunched
   crying pose.

4. **Doorway scale can shrink Zuv's face too much.**
   He can be smaller than Aachu, but his face still needs enough readable
   identity for a final Aachu/Zuv illustration.

## required_scene_fixes

1. Change the prompt's cup action from generic careful holding to a visible
   no-clink action: cup separated from saucer, or teaspoon pinned silent against
   the cup.

2. Give the house one concrete quiet behavior: Zuv's free fingers holding the
   half-open door/handle so it does not swing, or the door shown stopped softly
   by his hand. This is stronger than relying on a still curtain and angled
   chair.

3. Keep the frame to three readable proof carriers only: Aachu's silence, Zuv's
   careful footstep/cup, and one house object being kept quiet. Do not add more
   actions.

4. Specify Zuv's pose as upright and natural, with a low lifted socked foot, not
   a dramatic tiptoe or crouch.

5. Keep Aachu still but not performed: profile visible, hands in lap, eyes down
   or away, no exaggerated tears or melodrama.

## scores

Scale: `1` weak/high-risk, `5` strong/low-risk.

| Criterion | Score | Note |
| --- | ---: | --- |
| text-scene alignment | 4 | The human carefulness lands; the house-careful part needs one stronger physical proof. |
| prop clarity | 3 | Cup/door/chair are good candidates, but cup clink and chair logic are not yet visually self-evident. |
| pose safety | 4 | Natural if kept upright and simple; risk rises if tiptoe plus cup plus door are all over-specified. |
| anatomy risk | 3 | Hands and lifted foot are the main danger zones. |
| emotional readability | 4 | Reads as post-fight silence without turning into a lecture. |
| phone-screen clarity | 4 | Good lower-scene/upper-text structure; subtle house-object behavior must be large enough to read. |

## failure_codes

- `SCENE_LOGIC_CONTRADICTION` risk if the cup is still described as avoiding a
  clink without a visible second object or sound source.
- `VISUAL_SETTING_CONTRADICTION` risk if the door/curtain/chair remain generic
  decor instead of physically supporting the locked beat.
- `ANATOMY_FAILURE` risk if Zuv is forced into a crouched/twisted tiptoe while
  holding the cup.
- `VISUAL_ONLY_MOOD_WORDS` risk if "careful house" is left as atmosphere rather
  than object behavior.

## Final Gate

Revise before imagegen. Do not change the supplied on-image text. Do not expand
this into a carousel. Do not add more plot. The repaired scene should still be:
Aachu's silence in the room, Zuv entering carefully, and the house itself being
made quiet around her.
