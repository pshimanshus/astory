# Publishing QA Audit

Status: fail current candidate; do not export.

## Passes

- Main on-image text is exact:

```text
pay rent for living in
my heart
```

- Role logic mostly reads correctly: Aachu asks, Zuv receives.
- Brandmark is present at bottom-right.

## Failures

- Current file is `983 x 1600`, not native 4:5.
- Extra prop text appears on the note: `heart rent due: always`.
- The visual gag is too literal and feels fake-cute rather than premium observational intimacy.
- Style is still too polished/AI-photo hybrid.

## Hard Text Rule

The only readable text anywhere in the image must be:

```text
pay rent for living in
my heart
```

and the tiny bottom-right brandmark `@a.storyof.two`.

No other letters, numbers, labels, note text, receipt text, doodled words, UI text, symbols, or handwritten prop text.

## Final QA Checklist

- Native 4:5 verified by dimensions.
- Main text exact, lowercase, two lines.
- No prop text anywhere.
- Aachu clearly asks; Zuv clearly receives.
- Brandmark tiny, bottom-right, exact.
- Faces match identity refs.
- Off-white paper, premium watercolor-and-ink, restrained observational intimacy.
- No export until all above pass.
