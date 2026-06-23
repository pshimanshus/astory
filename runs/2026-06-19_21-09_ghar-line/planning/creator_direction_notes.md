# Creator Direction Notes

Run: `2026-06-19_21-09_ghar-line`

## 2026-06-19T21:39:18+05:30 — Slide 2 Rejected

Creator rejected the proposed second-slide copy:

```text
sab kuch hai yahan.
bas tum nahi ho.
thak ke bhi aa jaana.
main abhi bhi tumhara ghar hoon.
```

## What Was Wrong

- The line sounded fake-soft, needy, and constructed.
- `thak ke bhi aa jaana` moved the feeling into a generic return-home invitation.
- `main abhi bhi tumhara ghar hoon` sounded like relationship quote-page copy, not the real emotional backbone of `Ghar`.
- The copy treated the song line as "come back to me" instead of the deeper ache: without you, even the speaker/home is empty.
- The visible output underperformed the creator's emotional standard despite the agent workflow.

## Rejected Assumption

The rejected assumption was that slide 2 should comfort the receiver by inviting them to come back tired, imperfect, or quiet.

That is not the right emotional lane for this request.

## Active Constraint Going Forward

Slide 2 must stay closer to the ache inside the creator's line:

- not a welcome-back note;
- not a "home is a person" explanation;
- not a therapeutic reassurance;
- not polished Hinglish poetry;
- not a constructed sentence that sounds written for a carousel;
- it should feel like the quiet realization that the place/person called ghar is hollow without the one person.

Any repaired slide 2 must pass this before being shown:

> Does this feel like the emotional backbone of `khaali hai jo tere bina, main woh ghar hoon tera`, or does it sound like generic comfort copy?

If it sounds like generic comfort copy, mark `AI_SLOP_COPY_DRIFT` and rewrite before presenting.

## 2026-06-19T21:57:55+05:30 - Repaired Concept Input For Illustration

Creator supplied a new repaired concept and asked to create the illustration from it.

Active input:

```text
Slide 1
Khaali hai jo tere bina,
main woh ghar hoon tera.

Slide 2
Some people don't just enter your life,
they become the place your heart keeps returning to.
Without them, even the most familiar corners feel empty.
And with them, even silence feels safe.
That is the real ache of Ghar -
not just missing someone, but realizing that your sense of home was never a place.
It was always that one person.
```

Active constraint: the repaired text finally points at the correct emotional backbone, but it cannot be rendered as a dense quote-card paragraph. Preserve the meaning and the creator's cadence while letting Story Room decide whether phone readability requires splitting the supplied Slide 2 content across additional slides.

Rejected assumption: "create illustration" does not mean skip identity, scene, text, or HITL gates. The run can advance from idea repair into Story Room, but final Aachu/Zuv imagegen remains blocked until story lock, prompt lock, visible local references, and repo QA pass.

## 2026-06-19T22:36:40+05:30 - Visual Lane Correction: Do Not Literalize Ghar As House

Creator interrupted the first imagegen lane and corrected the visual assumption:

```text
not necessarily you always crammed us in house, you can think creatively like,
the girl is in some place full of people still feling lost and alone ..
like sitting in acafe or in a club or in a party or in some friends setting..
let's create the 2st iteration form girl's perspective completly. all sldies
```

## What Was Wrong

- The run over-literalized `Ghar` into a living-room/sofa/house-corner visual system.
- The first generated lane made every slide physically domestic, which weakened the deeper idea that home is a person.
- The girl can feel ghar-empty outside a house: cafe, party, friends setting, club, or any people-filled place where her body is present but her sense of home is missing.

## Rejected Assumption

The rejected assumption is: because the line says `ghar`, the illustration must stay inside a house or use an empty sofa/corner as the recurring visual metaphor.

That assumption is now invalid for iteration 2.

## Active Constraint Going Forward

Iteration 2 must be fully from the girl's perspective and should prove loneliness-in-crowd before it proves emptiness-in-house:

- Aachu may be surrounded by people, noise, lights, cafe tables, friends, or party movement and still feel alone.
- Zuv should remain emotionally present by absence, not as a ghost, memory figure, phone wallpaper, poster, or literal silhouette.
- All slides should keep Aachu's perspective primary; do not switch into Zuv's POV or a balanced couple POV until a creator-approved final payoff demands it.
- Do not repeat the living-room sofa as the main structure for this iteration.
- The visual should make `home was never a place` feel earned: if she can be in a full place and still feel misplaced, the final line lands harder.

Rejected first visual lane: `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt` and generated candidate at `/Users/himanshusharma/.codex/generated_images/019ee0b2-e889-7141-bcb0-f47908b32f67/ig_0fba9b61d5684270016a35757ea3788191bf907de106cf8630.png`.

## 2026-06-19T22:47:56+05:30 - No Comeback Payoff

Creator corrected the iteration 2 payoff:

```text
you willn deceve the real impact if he comes bacl
```

Interpreted active meaning: the real emotional impact is deceived/weakened if Zuv physically comes back in the final slide.

## What Was Wrong

- Showing Zuv sitting beside Aachu on slide 4 turns the carousel into a reunion.
- A reunion visually solves the ache, but the repaired Ghar concept is about realizing why every full place still feels empty.
- The final impact should not be "he came back and made it better." It should be "now I understand why nothing feels like home without that one person."

## Active Constraint Going Forward

- Zuv must not physically appear in any slide of iteration 2.
- No arrival, no comeback, no reunion, no hand-holding, no silhouette, no ghost, no memory figure, no phone wallpaper.
- The final slide should stay from Aachu's perspective and land as realization-through-absence.
- The text `And with them, even silence feels safe` should read as the missing contrast: the viewer understands that the safe silence is not available in this frame because he is not there.
- The payoff is the ache, not resolution.

## 2026-06-19T23:32:32+05:30 - Do Not Copy Identity Reference Emotion/Pose

Creator rejected the slide 1 iteration 2 output:

```text
why is she smiling, you are superinoosing the existihg identity image as it is
and thats the worst thing that you can do
```

Interpreted active meaning: the output copied the cafe identity reference's smile, jacket, cup/table pose, and general photo energy instead of using the reference only for face structure. The prompt also wrongly asked for a "smile a fraction too late," which contradicted the actual ache.

## What Was Wrong

- Aachu should not be smiling in this beat. Even a late or weak smile softens the loneliness and makes the frame feel copied from a pleasant cafe reference.
- The identity image was effectively used as a composition/expression template: front cafe pose, cup in both hands, table setup, jacket, and mild smile.
- That is the worst identity failure mode for this run: a recognizable-ish face pasted into the old photo's emotional state instead of a new lived scene.

## Active Constraint Going Forward

- For this Ghar lane, Aachu's public-setting expression must be unsmiling, held back, absent, or socially unable to join; not smiling, smirking, cute, coy, or pleasantly nostalgic.
- Identity references are face-structure evidence only. They must not drive pose, expression, wardrobe, hand placement, table/cup setup, lighting, background, camera angle, or scene composition.
- The full cafe identity image is dangerous for this scene because it carries the exact unwanted smile/cup/table/jacket composition. If used at all, it must be treated as face identity only and explicitly blocked as pose/composition reference; prefer safer face crops/neutral anchors for the next generation route.
- Remove cup-holding-as-proof from slide 1. Use disconnected body language instead: still hands, untouched cup off to the side, shoulders slightly closed, gaze not joining the group, mouth relaxed/closed.
- Reject any candidate that looks like an identity reference superimposed into watercolor, even if the text and setting are correct.
