# Creator Direction Notes

## 2026-06-13 21:10 IST - Concept references are not style references

Creator correction:
"you dont need to copy the visual style of referces ~ its not landing well and not our style"

Rejected assumption:
The shared "Who is your yellow?" screenshots were treated too strongly as visual-style references. Their painterly blur, heavy yellow atmosphere, and quote-card feel should not steer the final A Story render.

Active constraint:
Use the shared screenshots only for concept, emotional premise, broad composition, and text idea. Do not copy their visual style, yellow cast, painterly texture, poster/quote-card treatment, or typography look. Final artwork must stay in the A Story house style: premium romantic watercolor-and-ink, clean expressive Aachu/Zuv faces, neutral off-white paper, integrated handwritten text, and no yellow/parchment dominance.

Next prompt repair:
Rebuild the prompt around A Story house style first. The scene can still be "your yellow person," but the visual proof should come from Aachu and Zuv's tenderness, trust, and a small localized warmth, not from copying the screenshots' color or finish.

## 2026-06-13 22:08 IST - Observational intimacy is not a scene template

Creator correction:
"I didn't like this ~ ths is visually bad and the 2nd image follows too much observatiponal intimcy deisgn and wardrove and eevrythong, i don't liek repetition. Observational intimacy is just for refercne not to copy"

Rejected assumption:
The approved observational-intimacy/best-illustration references were treated too literally. The generated slides copied familiar design choices: white oversized shirt, navy shirt, bedroom/floor intimacy, centered handwritten text, soft domestic stillness, and repeated A Story reference poses/settings. That made the work feel derivative of the reference set instead of fresh for this concept.

Active constraint:
Observational intimacy is a quality bar, not a visual recipe. Use it only for emotional truth, restraint, clean faces, integrated hand lettering, paper discipline, and craft finish. Do not copy its wardrobe, room design, pose language, layout, camera distance, color distribution, or domestic-scene formula. Every new carousel must invent a fresh visual situation that proves the text without recycling earlier A Story compositions.

Specific hard avoids for the next "yellow person" repair:
- no lakeside/night hug frame
- no floor-by-bed vulnerable conversation frame
- no white oversized shirt + navy tee pairing
- no centered observational-intimacy text block copied from style references
- no "generic tender couple in room" scene
- no overuse of blue wash as the whole visual idea

Next prompt repair:
Run an "avoid first-round patterns" visual treatment pass. Build from a specific, fresh Aachu/Zuv behavior or object that proves "yellow person" without copying the concept screenshots or the observational-intimacy reference set.

## 2026-06-13 22:30 IST - Stop default close-sideways faces

Creator correction:
"I am done withthe close angel where both looks sideways akways"

Rejected assumption:
The repair still leaned on a familiar close emotional framing where both faces are close together and turned sideways or away. Even with a new car setting, that camera/eyeline habit feels repetitive and visually stale.

Active constraint:
Do not default to close-angle two-face side-profile/sideways-looking compositions. For future repairs, vary camera distance, eyeline, and body arrangement. At least one face should usually be readable and front/three-quarter when identity matters, and the scene should use a concrete action or object rather than relying on two close faces looking sideways.

Specific hard avoids for the next repair:
- no tight two-head close-up
- no both-looking-sideways/away pose as the emotional proof
- no cheek-on-shoulder or face-nestled pose
- no center-console handhold as the whole scene if it forces close sideways faces
- no repeating "quiet couple close together" as the visual idea

Next prompt repair:
Create a wider, action-led scene with clearer face readability and fresh eyelines. The image should prove "yellow person" through a specific behavior: one person quietly protecting space, saving them from judgment, or receiving a vulnerable truth without forcing both faces into the same sideways close pose.

## 2026-06-13 23:00 IST - Follow locked scene brief literally

Creator correction:
"too many visual mistakes in this..... see the reference images and see what you are creating. Lookign too bad... Scene 1: both standing and hugging eachg other in rain on a banglore road like one I shared. Scene 2: aachu sitting on zuv's lap, face not visible. both sitting in balcony zuv is sitting on a chair and aachu is sitting on his lap huggign him like she is in a vulnerable state. Also, this shot is from back side, its raning outside .."

Rejected assumption:
The repair kept inventing alternate settings and props instead of following the creator's now-specific scene lock. Stairwell, car, convenience-store objects, and other substitutions are wrong for this pass.

Active constraint:
Use the creator's locked scene brief literally.

Scene 1 lock:
Aachu and Zuv are both standing and hugging each other in rain on a Bangalore road, inspired by the provided close blue reference posture but rendered in A Story house style. The road should feel like Bangalore rain: wet asphalt, muted streetlights, parked scooters/cars or building silhouettes, rain haze. Do not turn it into a lake, stairwell, car interior, or domestic room.

Scene 2 lock:
Balcony in rain, back-side shot. Zuv sits on a chair in the balcony. Aachu sits on Zuv's lap, hugging him in a vulnerable state. Aachu's face is not visible. Rain is visible outside beyond the balcony. This is not a front-facing observational-intimacy domestic floor scene.

Next prompt repair:
Generate only these two locked scenes. Treat the user-provided references as scene/posture references, not style references. Avoid adding invented props or changing the physical situation.

## 2026-06-14 00:07 IST - Native 1080x1350 generation is mandatory

Creator correction:
"I have tolf you this many times don 't fuck up with the images, the iamge is extend but not created in the format and dimension i have shared abd I don't know whty you are not ensuring your give imagegen the dimension clarity in each prompt. Ensure and don't fuck this up"

Rejected assumption:
Wrong-size imagegen outputs were padded/extended/resized into final Instagram assets. That violates the creator's requested format and hides the actual generation failure.

Active constraint:
Every imagegen prompt for Instagram posts must explicitly require a native canvas of exactly 1080px wide by 1350px tall, 4:5 portrait, with no later extension, padding, cropping, or format conversion used to pretend compliance. If imagegen returns a non-1080x1350 asset, that candidate is rejected for final use and must be regenerated with stronger native-size instructions.

Specific hard avoids:
- no side padding to make a tall/narrow image 4:5
- no canvas extension after generation
- no cropping away content to force 4:5
- no calling resized/post-processed wrong-size candidates "final"

Next prompt repair:
Regenerate the two locked scenes with native-size instructions in the first lines of each prompt. Verify generated pixel dimensions before copying into final package.

## 2026-06-14 00:58 IST - Repeated native-size gate reinforcement

Creator correction:
"I have tolf you this many times don 't fuck up with the images, the iamge is extend but not created in the format and dimension i have shared abd I don't know whty you are not ensuring your give imagegen the dimension clarity in each prompt. Ensure and don't fuck this up"

Rejected assumption:
It is not enough for the exported file to inspect as 1080x1350 if the generated artwork was first produced at the wrong native size and then extended, padded, cropped, or format-forced afterward.

Active constraint:
Every imagegen prompt for Instagram post artwork must start with the exact native canvas requirement: "Create a native Instagram 4:5 portrait illustration exactly 1080px wide by 1350px tall." The prompt must also explicitly forbid a taller, narrower, landscape, square, bordered, padded, or extended canvas. If imagegen returns any other size or unrelated content, the candidate remains rejected and the run stays blocked; do not relabel post-processed output as final.

Specific hard avoids:
- no "final" package from side-padded, extended, or resized wrong-size outputs
- no burying dimensions late in the prompt
- no accepting approximate 4:5 or visually similar ratios
- no continuing to final package when imagegen ignores native-size instructions

Next prompt repair:
Do not generate more final artwork until the first prompt lines enforce native 1080x1350 4:5, and verification confirms the raw generated file itself is 1080x1350 before export.

## 2026-06-14 01:22 IST - Identity angle references are not pose instructions

Creator correction:
"this iamge is my face's side angel. desn't mean you need to create the end image using side angel"

Rejected assumption:
A Zuv side-angle face reference was treated too much like a final camera/pose direction. Identity reference angle must not force the end illustration into side profile or repeated sideways-looking staging.

Active constraint:
Identity images define facial structure, hair, beard, brows, skin tone, and likeness cues only. They do not define the final scene camera angle, body pose, eyeline, wardrobe, or composition unless the creator explicitly says so. For scene 1, avoid side-profile Zuv as the default; prefer a readable natural three-quarter/front-ish angle that preserves likeness while keeping the rain-road hug composition. For scene 2, follow the locked backside balcony brief because the scene itself requires back view, not because of identity-reference angle.

Specific hard avoids:
- no copying a face-reference crop angle into the final illustration
- no side-profile Zuv just because one identity anchor is side profile
- no both-looking-sideways composition
- no treating identity refs as wardrobe or pose refs

Next prompt repair:
Separate identity cues from staging instructions in every prompt. Add: "Use identity references for likeness only; do not copy their camera angle, pose, or wardrobe."

## 2026-06-14 01:38 IST - Use latest attached references as target and likeness anchors

Creator direction:
"please use these refercne image to create the final illustration on the concept I have attached. images for erefcne I atached are perfect but just not in expected format."

Active constraint:
Treat the newly attached concept screenshot as the visual target for the two scenes: slide 1 rain-road standing hug; slide 2 balcony back-side lap hug. Treat the newly attached Aachu and Zuv images as stronger likeness anchors only, especially front/three-quarter face structure, hair, brows, beard, and natural expressions. Do not copy reference photo wardrobe, pose, camera angle, or background unless it matches the locked scene.

Format constraint remains:
Final shareable files must come from raw native 1080px wide by 1350px tall 4:5 imagegen outputs. If imagegen produces a wrong-size raw file, reject it; do not use post-processing to make it final.

## 2026-06-14 01:48 IST - Visual logic must pass before format talk

Creator correction:
"is this reallly making sense"

Rejected assumption:
A generated image that roughly resembles the previous target composition is not acceptable if the scene itself feels visually incoherent or generic. The latest rain-road candidate copied the broad setup but lost the emotional logic, identity specificity, wardrobe consistency, readable hook, and native canvas requirement.

Active constraint:
Before any future candidate is discussed as an export, it must pass a visual-logic gate: does the relationship pose read as intentional, vulnerable, and believable; do Aachu and Zuv look like themselves rather than generic substitutes; is the on-image text readable; does the locked scene still match the creator's concept; and is the raw file natively 1080x1350. If any one of these fails, reject before packaging.

Specific hard avoids:
- no generic couple stand-in just because the rain-road setting looks pretty
- no tiny/unreadable hook text
- no identity/wardrobe drift while chasing composition
- no accepting "close enough visually" when the emotional body logic is off
- no final/shareable file from a wrong-size raw image

Next prompt repair:
Reduce pose ambiguity and keep the emotional logic explicit: a believable protective standing hug in rain, with Aachu visibly seeking safety and Zuv visibly receiving/holding her, while keeping likeness cues and readable text.
