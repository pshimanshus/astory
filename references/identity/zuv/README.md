# Zuv References

Use Zuv references by role.

- `face/`: 8 clean portrait anchors/derived close crops for face identity, hair volume, brows, beard, skin tone, and build.
- `smiles/`: smile and laugh support; do not replace face anchors.
- `reactions/`: posture, gym/build, selfie angle, or mood support.

Images with sunglasses or tinted glasses must not be used for eye identity or
primary face identity.

Default generation starts from these close crops:

- `face/zuv-face-crop-balcony-neutral-01.jpg`
- `face/zuv-face-crop-balcony-neutral-03.jpg`
- `face/zuv-face-crop-balcony-neutral-02.jpg`
- `face/zuv-face-crop-dinner-smile-02.jpg`

Use side/profile and laughing crops only as scene-specific angle or expression support.
