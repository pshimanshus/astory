# A Story of Two — App Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clickable, phone-shaped web prototype of the full A Story of Two app flow (paper landing → name capture → photo pick → voice story → "printing" wait → reveal → rate → send-as-gift), with AI generation, transcription, and uniqueness-judging faked.

**Architecture:** A single-page React app rendered inside a phone frame. A small pure flow state machine drives a linear sequence of screens; a session store holds the user's names/photos/recording/rating; pure service modules fake transcription, carousel generation, and share-payload construction. Logic units are TDD'd with Vitest; visual screens are built against concrete acceptance criteria and verified in the browser.

**Tech Stack:** Vite + React 18 + TypeScript, Framer Motion (animation/transitions), Vitest + @testing-library/react + jsdom (tests), plain CSS with custom-property design tokens (paper/ink aesthetic). Browser APIs: MediaRecorder (mic), Web Share API (send). No router (the flow machine switches screens). New code lives under `app/`.

---

## Core types (defined once, used everywhere — keep names consistent)

These types are created in Task 2/3 and referenced throughout. Do not rename them in later tasks.

```ts
// app/src/flow/steps.ts
export type Step =
  | 'landing'
  | 'hello'
  | 'photos'
  | 'review'
  | 'record'
  | 'printing'
  | 'reveal'
  | 'rate'
  | 'send';
// 'cap-reached' is a branch state, not part of the linear ORDER.

// app/src/session/session.ts
export type Relationship = 'together' | 'sending';

export interface Slide {
  id: string;
  imageUrl: string;   // path to a house-style illustration asset
  caption: string;    // interpolated with names + story beats
}

export interface SessionState {
  relationship: Relationship | null;
  creatorName: string;
  partnerName: string;
  photos: string[];              // selected sample-photo ids
  recordingUrl: string | null;   // object URL of the recorded audio
  recordingDurationSec: number;
  storyBeats: string[];          // faked transcription output
  rating: number | null;         // 1..5
  slides: Slide[] | null;        // faked generated carousel
}
```

---

## File structure (created across the tasks below)

```
app/
  package.json                  # deps + scripts (Task 0)
  vite.config.ts                # vite + vitest config (Task 0)
  tsconfig.json                 # (Task 0)
  index.html                    # mount point (Task 0)
  src/
    main.tsx                    # React entry (Task 0)
    test/setup.ts               # testing-library/jsdom setup (Task 0)
    App.tsx                     # PhoneFrame + FlowProvider + current screen (Task 5)
    flow/
      steps.ts                  # Step type + ORDER + nextStep/prevStep (Task 2)
      steps.test.ts             # (Task 2)
      FlowProvider.tsx          # React context: current step + advance/back/goTo (Task 5)
    session/
      session.ts                # SessionState, Slide, createInitialSession, derives (Task 3)
      session.test.ts           # (Task 3)
      SessionProvider.tsx       # React context wrapping session + setters (Task 5)
      deviceId.ts               # device id + 3-cap persistence (Task 4)
      deviceId.test.ts          # (Task 4)
    services/
      carouselContent.ts        # house-slide templates + buildSlides (Task 11)
      carouselContent.test.ts   # (Task 11)
      fakeGeneration.ts         # deriveStoryBeats + phase timings (Task 12)
      fakeGeneration.test.ts    # (Task 12)
      share.ts                  # buildShareMessage + SHARE_TARGETS + shareTo (Task 16)
      share.test.ts             # (Task 16)
    content/
      copy.ts                   # all brand-voice copy strings (Task 1)
      sampleGallery.ts          # bundled sample photos (Task 8)
      houseSlides.ts            # house-style slide asset list (Task 11)
    components/
      PhoneFrame.tsx            # phone-shaped frame (Task 0/1)
      PaperBackground.tsx       # paper texture layer (Task 1)
      HandDrawnArrow.tsx        # arrow + caption motif (Task 6)
      Carousel.tsx              # swipeable carousel (Task 13)
      MicButton.tsx             # record button + waveform (Task 10)
    screens/
      LandingScreen.tsx         # (Task 6)
      HelloScreen.tsx           # (Task 7)
      PhotoSelectScreen.tsx     # (Task 8)
      PhotoReviewScreen.tsx     # (Task 9)
      RecordScreen.tsx          # (Task 10)
      PrintingScreen.tsx        # (Task 14)
      RevealScreen.tsx          # (Task 13/15)
      RateScreen.tsx            # (Task 15)
      SendScreen.tsx            # (Task 17)
      CapReachedScreen.tsx      # (Task 18)
    styles/
      tokens.css                # design tokens (Task 1)
      global.css                # resets + base (Task 1)
    assets/                     # paper texture, house-style illustrations (Task 1/11)
```

---

## Task 0: Scaffold the Vite + React + TS + Vitest project

**Files:**
- Create: `app/package.json`, `app/vite.config.ts`, `app/tsconfig.json`, `app/index.html`, `app/src/main.tsx`, `app/src/test/setup.ts`, `app/src/App.tsx` (temporary), `app/.gitignore`

- [ ] **Step 1: Create the project skeleton files**

`app/package.json`:
```json
{
  "name": "astory-app-prototype",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "framer-motion": "^11.3.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "jsdom": "^24.1.0",
    "typescript": "^5.5.0",
    "vite": "^5.3.0",
    "vitest": "^2.0.0"
  }
}
```

`app/vite.config.ts`:
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
});
```

`app/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src"]
}
```

`app/index.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
    <title>A Story of Two</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`app/src/main.tsx`:
```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

`app/src/test/setup.ts`:
```ts
import '@testing-library/jest-dom/vitest';
```

`app/src/App.tsx` (temporary, replaced in Task 5):
```tsx
export default function App() {
  return <h1>A Story of Two — prototype</h1>;
}
```

`app/.gitignore`:
```
node_modules
dist
```

- [ ] **Step 2: Install dependencies**

Run: `cd app && npm install`
Expected: dependencies install with no errors; `app/node_modules` exists.

- [ ] **Step 3: Verify the dev server boots**

Run: `cd app && npm run dev` (then stop it with Ctrl-C after confirming)
Expected: Vite prints a `Local: http://localhost:5173/` URL; opening it shows "A Story of Two — prototype".

- [ ] **Step 4: Verify the test runner works**

Run: `cd app && npm test`
Expected: Vitest runs and reports "no test files found" (exit 0) — confirms config is valid.

- [ ] **Step 5: Commit**

```bash
git add app/package.json app/package-lock.json app/vite.config.ts app/tsconfig.json app/index.html app/src/main.tsx app/src/test/setup.ts app/src/App.tsx app/.gitignore
git commit -m "chore(app): scaffold vite+react+ts+vitest prototype"
```

---

## Task 1: Design tokens, paper background, brand copy, phone frame

**Files:**
- Create: `app/src/styles/tokens.css`, `app/src/styles/global.css`, `app/src/components/PaperBackground.tsx`, `app/src/components/PhoneFrame.tsx`, `app/src/content/copy.ts`

- [ ] **Step 1: Create design tokens**

`app/src/styles/tokens.css`:
```css
:root {
  /* Paper + ink palette */
  --paper: #f6f1e7;
  --paper-shadow: #e7dfcf;
  --ink: #2b2622;
  --ink-soft: #6b6258;
  --accent: #c2462f;        /* warm red used sparingly */
  --hairline: #d8cfbd;

  /* Type */
  --font-hand: 'Caveat', 'Bradley Hand', cursive;   /* hand-drawn captions */
  --font-body: 'Georgia', 'Times New Roman', serif;  /* warm serif body */

  /* Spacing + motion */
  --space: 16px;
  --radius: 20px;
  --ease-soft: cubic-bezier(0.22, 1, 0.36, 1);
}
```

`app/src/styles/global.css`:
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, #root { height: 100%; }
body {
  font-family: var(--font-body);
  color: var(--ink);
  background: #15110d;       /* dark surround behind the phone */
  display: flex;
  align-items: center;
  justify-content: center;
}
button { font: inherit; cursor: pointer; border: none; background: none; color: inherit; }
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

- [ ] **Step 2: Create the PhoneFrame component**

`app/src/components/PhoneFrame.tsx`:
```tsx
import type { ReactNode } from 'react';

export function PhoneFrame({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        width: 390,
        height: 844,
        maxHeight: '95vh',
        borderRadius: 44,
        overflow: 'hidden',
        position: 'relative',
        boxShadow: '0 30px 80px rgba(0,0,0,0.55)',
        border: '10px solid #0b0907',
        background: 'var(--paper)',
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 3: Create the PaperBackground component**

`app/src/components/PaperBackground.tsx`:
```tsx
import type { ReactNode } from 'react';

// Full-bleed warm paper layer. Subtle layered radial grain via CSS only.
export function PaperBackground({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background:
          'radial-gradient(120% 80% at 50% 0%, #fbf7ee 0%, var(--paper) 55%, var(--paper-shadow) 100%)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 4: Create the brand copy module**

`app/src/content/copy.ts`:
```ts
// All user-facing brand-voice strings live here so they can be tuned in one place.
export const copy = {
  landing: {
    cta: 'say your story, get it illustrated',
    disclaimer:
      'We may post your story on A Story of Two. If it’s unique and our agent loves it, you’ll get your illustrated carousel. Max 3 per person.',
  },
  hello: {
    prompt: 'Are you here with your special one — or sending them something from afar?',
    together: 'We’re together',
    sending: 'I’m sending them something',
    yourName: 'your name',
    theirName: 'their name',
    continue: 'begin',
  },
  photos: { title: 'choose your photos', hint: 'pick the moments that are you two', done: 'these are us' },
  review: { mic: 'record your story — we draw from your voice' },
  record: { prompt: 'tell us about you two. take your time.', stop: 'that’s our story' },
  printing: {
    greet: (name: string) => `${name}, while your story prints — let me tell you ours.`,
    askOnce: 'no pressure — follow only if this already feels like you.',
    follow: 'follow A Story of Two',
  },
  reveal: { title: 'your story, drawn' },
  rate: { prompt: 'did this feel like you?' },
  send: {
    primary: (name: string) => `send it to ${name}`,
    note: 'no downloads — this is meant to be given, not saved.',
  },
  cap: { title: 'you’ve made your three.', body: 'three stories is all we draw per heart. thank you for trusting us with them.' },
} as const;
```

- [ ] **Step 5: Verify it compiles**

Run: `cd app && npx tsc -b --noEmit`
Expected: no type errors.

- [ ] **Step 6: Commit**

```bash
git add app/src/styles app/src/components/PhoneFrame.tsx app/src/components/PaperBackground.tsx app/src/content/copy.ts
git commit -m "feat(app): design tokens, paper background, phone frame, brand copy"
```

---

## Task 2: Flow state machine (TDD)

**Files:**
- Create: `app/src/flow/steps.ts`, `app/src/flow/steps.test.ts`

- [ ] **Step 1: Write the failing test**

`app/src/flow/steps.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { ORDER, nextStep, prevStep, isFirst, isLast } from './steps';

describe('flow steps', () => {
  it('has the linear happy-path order', () => {
    expect(ORDER).toEqual([
      'landing', 'hello', 'photos', 'review', 'record', 'printing', 'reveal', 'rate', 'send',
    ]);
  });

  it('advances forward through the order', () => {
    expect(nextStep('landing')).toBe('hello');
    expect(nextStep('record')).toBe('printing');
  });

  it('stays on the last step when advancing past the end', () => {
    expect(nextStep('send')).toBe('send');
  });

  it('goes back through the order', () => {
    expect(prevStep('hello')).toBe('landing');
  });

  it('stays on the first step when going back past the start', () => {
    expect(prevStep('landing')).toBe('landing');
  });

  it('knows first and last', () => {
    expect(isFirst('landing')).toBe(true);
    expect(isLast('send')).toBe(true);
    expect(isLast('reveal')).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && npx vitest run src/flow/steps.test.ts`
Expected: FAIL — cannot resolve `./steps`.

- [ ] **Step 3: Write minimal implementation**

`app/src/flow/steps.ts`:
```ts
export type Step =
  | 'landing' | 'hello' | 'photos' | 'review' | 'record'
  | 'printing' | 'reveal' | 'rate' | 'send';

export const ORDER: Step[] = [
  'landing', 'hello', 'photos', 'review', 'record', 'printing', 'reveal', 'rate', 'send',
];

export function nextStep(step: Step): Step {
  const i = ORDER.indexOf(step);
  return ORDER[Math.min(i + 1, ORDER.length - 1)];
}

export function prevStep(step: Step): Step {
  const i = ORDER.indexOf(step);
  return ORDER[Math.max(i - 1, 0)];
}

export const isFirst = (step: Step) => ORDER.indexOf(step) === 0;
export const isLast = (step: Step) => ORDER.indexOf(step) === ORDER.length - 1;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && npx vitest run src/flow/steps.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add app/src/flow/steps.ts app/src/flow/steps.test.ts
git commit -m "feat(app): flow step machine with tests"
```

---

## Task 3: Session state (TDD)

**Files:**
- Create: `app/src/session/session.ts`, `app/src/session/session.test.ts`

- [ ] **Step 1: Write the failing test**

`app/src/session/session.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { createInitialSession, hasPhotos, hasRecording, displayPartnerName } from './session';

describe('session', () => {
  it('starts empty', () => {
    const s = createInitialSession();
    expect(s.relationship).toBeNull();
    expect(s.creatorName).toBe('');
    expect(s.partnerName).toBe('');
    expect(s.photos).toEqual([]);
    expect(s.recordingUrl).toBeNull();
    expect(s.storyBeats).toEqual([]);
    expect(s.rating).toBeNull();
    expect(s.slides).toBeNull();
  });

  it('detects photos and recording presence', () => {
    const s = createInitialSession();
    expect(hasPhotos(s)).toBe(false);
    expect(hasRecording(s)).toBe(false);
    expect(hasPhotos({ ...s, photos: ['a'] })).toBe(true);
    expect(hasRecording({ ...s, recordingUrl: 'blob:x' })).toBe(true);
  });

  it('falls back to a warm placeholder when partner name is blank', () => {
    const s = createInitialSession();
    expect(displayPartnerName(s)).toBe('your person');
    expect(displayPartnerName({ ...s, partnerName: 'Mira' })).toBe('Mira');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && npx vitest run src/session/session.test.ts`
Expected: FAIL — cannot resolve `./session`.

- [ ] **Step 3: Write minimal implementation**

`app/src/session/session.ts`:
```ts
export type Relationship = 'together' | 'sending';

export interface Slide {
  id: string;
  imageUrl: string;
  caption: string;
}

export interface SessionState {
  relationship: Relationship | null;
  creatorName: string;
  partnerName: string;
  photos: string[];
  recordingUrl: string | null;
  recordingDurationSec: number;
  storyBeats: string[];
  rating: number | null;
  slides: Slide[] | null;
}

export function createInitialSession(): SessionState {
  return {
    relationship: null,
    creatorName: '',
    partnerName: '',
    photos: [],
    recordingUrl: null,
    recordingDurationSec: 0,
    storyBeats: [],
    rating: null,
    slides: null,
  };
}

export const hasPhotos = (s: SessionState) => s.photos.length > 0;
export const hasRecording = (s: SessionState) => s.recordingUrl !== null;
export const displayPartnerName = (s: SessionState) =>
  s.partnerName.trim() ? s.partnerName.trim() : 'your person';
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && npx vitest run src/session/session.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add app/src/session/session.ts app/src/session/session.test.ts
git commit -m "feat(app): session state model with tests"
```

---

## Task 4: Device id + 3-carousel cap (TDD)

**Files:**
- Create: `app/src/session/deviceId.ts`, `app/src/session/deviceId.test.ts`

- [ ] **Step 1: Write the failing test**

`app/src/session/deviceId.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import {
  MAX_CAROUSELS, getDeviceId, getCarouselsCreated, getRemaining,
  recordCarouselCreated, hasReachedCap,
} from './deviceId';

beforeEach(() => localStorage.clear());

describe('deviceId + 3-cap', () => {
  it('creates and persists a stable device id', () => {
    const id = getDeviceId();
    expect(id).toMatch(/^dev_/);
    expect(getDeviceId()).toBe(id); // stable across calls
  });

  it('starts with zero created and full remaining', () => {
    expect(getCarouselsCreated()).toBe(0);
    expect(getRemaining()).toBe(MAX_CAROUSELS);
    expect(hasReachedCap()).toBe(false);
  });

  it('counts up and reaches the cap at 3', () => {
    recordCarouselCreated();
    recordCarouselCreated();
    expect(getRemaining()).toBe(1);
    expect(hasReachedCap()).toBe(false);
    recordCarouselCreated();
    expect(getCarouselsCreated()).toBe(3);
    expect(getRemaining()).toBe(0);
    expect(hasReachedCap()).toBe(true);
  });

  it('never lets remaining go negative', () => {
    for (let i = 0; i < 5; i++) recordCarouselCreated();
    expect(getRemaining()).toBe(0);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && npx vitest run src/session/deviceId.test.ts`
Expected: FAIL — cannot resolve `./deviceId`.

- [ ] **Step 3: Write minimal implementation**

`app/src/session/deviceId.ts`:
```ts
export const MAX_CAROUSELS = 3;
const ID_KEY = 'astory.deviceId';
const COUNT_KEY = 'astory.carouselsCreated';

export function getDeviceId(): string {
  let id = localStorage.getItem(ID_KEY);
  if (!id) {
    id = `dev_${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
    localStorage.setItem(ID_KEY, id);
  }
  return id;
}

export function getCarouselsCreated(): number {
  return Number(localStorage.getItem(COUNT_KEY) ?? '0');
}

export function getRemaining(): number {
  return Math.max(0, MAX_CAROUSELS - getCarouselsCreated());
}

export function recordCarouselCreated(): void {
  localStorage.setItem(COUNT_KEY, String(getCarouselsCreated() + 1));
}

export function hasReachedCap(): boolean {
  return getRemaining() === 0;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && npx vitest run src/session/deviceId.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add app/src/session/deviceId.ts app/src/session/deviceId.test.ts
git commit -m "feat(app): device id + 3-carousel cap persistence with tests"
```

---

## Task 5: Providers + App shell with screen switching

**Files:**
- Create: `app/src/flow/FlowProvider.tsx`, `app/src/session/SessionProvider.tsx`
- Modify: `app/src/App.tsx` (replace temporary content)

- [ ] **Step 1: Create the FlowProvider**

`app/src/flow/FlowProvider.tsx`:
```tsx
import { createContext, useContext, useState, type ReactNode } from 'react';
import { type Step, nextStep, prevStep } from './steps';

interface FlowCtx {
  step: Step | 'cap-reached';
  advance: () => void;
  back: () => void;
  goTo: (s: Step | 'cap-reached') => void;
}

const Ctx = createContext<FlowCtx | null>(null);

export function FlowProvider({ children }: { children: ReactNode }) {
  const [step, setStep] = useState<Step | 'cap-reached'>('landing');
  const advance = () => setStep((s) => (s === 'cap-reached' ? s : nextStep(s)));
  const back = () => setStep((s) => (s === 'cap-reached' ? 'landing' : prevStep(s)));
  const goTo = (s: Step | 'cap-reached') => setStep(s);
  return <Ctx.Provider value={{ step, advance, back, goTo }}>{children}</Ctx.Provider>;
}

export function useFlow() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useFlow must be used within FlowProvider');
  return c;
}
```

- [ ] **Step 2: Create the SessionProvider**

`app/src/session/SessionProvider.tsx`:
```tsx
import { createContext, useContext, useState, type ReactNode } from 'react';
import { type SessionState, createInitialSession } from './session';

interface SessionCtx {
  session: SessionState;
  update: (patch: Partial<SessionState>) => void;
  reset: () => void;
}

const Ctx = createContext<SessionCtx | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<SessionState>(createInitialSession);
  const update = (patch: Partial<SessionState>) => setSession((s) => ({ ...s, ...patch }));
  const reset = () => setSession(createInitialSession());
  return <Ctx.Provider value={{ session, update, reset }}>{children}</Ctx.Provider>;
}

export function useSession() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useSession must be used within SessionProvider');
  return c;
}
```

- [ ] **Step 3: Replace App.tsx with the shell + temporary nav buttons**

`app/src/App.tsx`:
```tsx
import { AnimatePresence, motion } from 'framer-motion';
import './styles/tokens.css';
import './styles/global.css';
import { PhoneFrame } from './components/PhoneFrame';
import { PaperBackground } from './components/PaperBackground';
import { FlowProvider, useFlow } from './flow/FlowProvider';
import { SessionProvider } from './session/SessionProvider';

function CurrentScreen() {
  const { step, advance, back } = useFlow();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={step}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.35 }}
        style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 24 }}
      >
        {/* Screens are swapped in here in later tasks. Temporary nav for now: */}
        <p style={{ marginTop: 'auto' }}>step: {step}</p>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={back}>back</button>
          <button onClick={advance}>next</button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <SessionProvider>
      <FlowProvider>
        <PhoneFrame>
          <PaperBackground>
            <CurrentScreen />
          </PaperBackground>
        </PhoneFrame>
      </FlowProvider>
    </SessionProvider>
  );
}
```

- [ ] **Step 4: Verify navigation in the browser**

Run: `cd app && npm run dev`
Expected: the phone frame shows on a dark surround; "step: landing" is visible; clicking **next** walks landing → hello → … → send and stops; **back** walks in reverse and stops at landing.

- [ ] **Step 5: Commit**

```bash
git add app/src/flow/FlowProvider.tsx app/src/session/SessionProvider.tsx app/src/App.tsx
git commit -m "feat(app): flow + session providers and screen-switching shell"
```

---

## Task 6: Landing screen — paper page, + button, hand-drawn arrow, disclaimer

**Files:**
- Create: `app/src/components/HandDrawnArrow.tsx`, `app/src/screens/LandingScreen.tsx`
- Modify: `app/src/App.tsx` (render `LandingScreen` when `step === 'landing'`)

**Acceptance criteria:** blank paper; a centered circular `+` button; a hand-drawn arrow + caption (`copy.landing.cta`) pointing to it; a small tappable "why?" / disclaimer line that opens a dismissable card showing `copy.landing.disclaimer`. Tapping `+` checks the cap: if `hasReachedCap()` → `goTo('cap-reached')`, else `advance()`.

- [ ] **Step 1: Create the HandDrawnArrow component**

`app/src/components/HandDrawnArrow.tsx`:
```tsx
export function HandDrawnArrow({ caption }: { caption: string }) {
  return (
    <div style={{ textAlign: 'center', color: 'var(--ink-soft)' }}>
      <p style={{ fontFamily: 'var(--font-hand)', fontSize: 24, lineHeight: 1.2 }}>{caption}</p>
      <svg width="60" height="70" viewBox="0 0 60 70" aria-hidden style={{ display: 'block', margin: '0 auto' }}>
        <path d="M30 4 C 18 26, 42 40, 30 62" fill="none" stroke="var(--ink-soft)" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M20 52 L30 64 L40 52" fill="none" stroke="var(--ink-soft)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
}
```

- [ ] **Step 2: Create the LandingScreen**

`app/src/screens/LandingScreen.tsx`:
```tsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { copy } from '../content/copy';
import { HandDrawnArrow } from '../components/HandDrawnArrow';
import { useFlow } from '../flow/FlowProvider';
import { hasReachedCap } from '../session/deviceId';

export function LandingScreen() {
  const { advance, goTo } = useFlow();
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  const start = () => (hasReachedCap() ? goTo('cap-reached') : advance());

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 24, padding: 24 }}>
      <HandDrawnArrow caption={copy.landing.cta} />
      <motion.button
        onClick={start}
        whileTap={{ scale: 0.94 }}
        aria-label="start your story"
        style={{ width: 84, height: 84, borderRadius: '50%', background: 'var(--ink)', color: 'var(--paper)', fontSize: 40, lineHeight: 1, boxShadow: '0 10px 24px rgba(0,0,0,0.25)' }}
      >
        +
      </motion.button>

      <button onClick={() => setShowDisclaimer(true)} style={{ position: 'absolute', bottom: 24, fontSize: 13, color: 'var(--ink-soft)', textDecoration: 'underline' }}>
        before you begin
      </button>

      {showDisclaimer && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} onClick={() => setShowDisclaimer(false)}
          style={{ position: 'absolute', inset: 0, background: 'rgba(20,16,12,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 28 }}>
          <div style={{ background: 'var(--paper)', borderRadius: 'var(--radius)', padding: 22, fontSize: 15, lineHeight: 1.5 }}>
            <p>{copy.landing.disclaimer}</p>
            <p style={{ marginTop: 14, fontFamily: 'var(--font-hand)', color: 'var(--ink-soft)' }}>tap anywhere to close</p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Wire it into App.tsx**

In `app/src/App.tsx`, import `LandingScreen` and render it for the landing step. Replace the temporary block inside `CurrentScreen`'s `motion.div` with a switch:
```tsx
import { LandingScreen } from './screens/LandingScreen';
// ...inside motion.div, replace the temporary <p>/buttons with:
{step === 'landing' && <LandingScreen />}
{step !== 'landing' && (
  <div style={{ marginTop: 'auto' }}>
    <p>step: {step}</p>
    <div style={{ display: 'flex', gap: 8 }}>
      <button onClick={back}>back</button><button onClick={advance}>next</button>
    </div>
  </div>
)}
```
(The temporary nav stays for not-yet-built screens and is removed in Task 19.)

- [ ] **Step 4: Verify in the browser**

Run: `cd app && npm run dev`
Expected: paper landing with the arrow + caption above a `+`; "before you begin" opens the disclaimer card and tapping closes it; tapping `+` advances to the hello step.

- [ ] **Step 5: Commit**

```bash
git add app/src/components/HandDrawnArrow.tsx app/src/screens/LandingScreen.tsx app/src/App.tsx
git commit -m "feat(app): landing paper screen with + button, arrow, disclaimer"
```

---

## Task 7: Hello screen — relationship + names

**Files:**
- Create: `app/src/screens/HelloScreen.tsx`
- Modify: `app/src/App.tsx` (render for `step === 'hello'`)

**Acceptance criteria:** shows `copy.hello.prompt`; two choices (`together` / `sending`) that set `session.relationship`; two text inputs for `creatorName` and `partnerName`; a `begin` button enabled only when relationship is chosen and `creatorName` is non-empty; on continue, writes names to session and `advance()`.

- [ ] **Step 1: Create the HelloScreen**

`app/src/screens/HelloScreen.tsx`:
```tsx
import { useState } from 'react';
import { copy } from '../content/copy';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';
import type { Relationship } from '../session/session';

export function HelloScreen() {
  const { advance } = useFlow();
  const { session, update } = useSession();
  const [rel, setRel] = useState<Relationship | null>(session.relationship);
  const [me, setMe] = useState(session.creatorName);
  const [them, setThem] = useState(session.partnerName);

  const ready = rel !== null && me.trim().length > 0;
  const begin = () => { update({ relationship: rel, creatorName: me.trim(), partnerName: them.trim() }); advance(); };

  const choice = (value: Relationship, label: string) => (
    <button onClick={() => setRel(value)}
      style={{ padding: '12px 16px', borderRadius: 14, border: `1.5px solid ${rel === value ? 'var(--ink)' : 'var(--hairline)'}`, background: rel === value ? 'var(--ink)' : 'transparent', color: rel === value ? 'var(--paper)' : 'var(--ink)' }}>
      {label}
    </button>
  );

  const field = (ph: string, v: string, on: (s: string) => void) => (
    <input value={v} placeholder={ph} onChange={(e) => on(e.target.value)}
      style={{ padding: '12px 14px', borderRadius: 12, border: '1.5px solid var(--hairline)', background: 'transparent', fontFamily: 'var(--font-body)', fontSize: 16 }} />
  );

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 18, padding: 28 }}>
      <p style={{ fontSize: 20, lineHeight: 1.35 }}>{copy.hello.prompt}</p>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {choice('together', copy.hello.together)}
        {choice('sending', copy.hello.sending)}
      </div>
      {field(copy.hello.yourName, me, setMe)}
      {field(copy.hello.theirName, them, setThem)}
      <button disabled={!ready} onClick={begin}
        style={{ marginTop: 8, padding: '14px', borderRadius: 14, background: ready ? 'var(--accent)' : 'var(--hairline)', color: 'var(--paper)', fontSize: 16 }}>
        {copy.hello.continue}
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Wire into App.tsx**

Add `import { HelloScreen } from './screens/HelloScreen';` and `{step === 'hello' && <HelloScreen />}` to the screen switch; remove `'hello'` from the temporary-nav fallback by extending the built-screens condition (track built steps as you go).

- [ ] **Step 3: Verify in the browser**

Run: `cd app && npm run dev`
Expected: from landing → `+`, the hello screen appears; `begin` is disabled until a relationship is picked and a name is typed; continuing advances to photos.

- [ ] **Step 4: Commit**

```bash
git add app/src/screens/HelloScreen.tsx app/src/App.tsx
git commit -m "feat(app): hello screen — relationship + name capture"
```

---

## Task 8: Photo select — multi-select gallery

**Files:**
- Create: `app/src/content/sampleGallery.ts`, `app/src/screens/PhotoSelectScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** a grid of ~9 bundled sample photos; tapping toggles selection (visible check/ring); a `these are us` button enabled when ≥1 selected; on continue writes selected ids to `session.photos` and `advance()`.

- [ ] **Step 1: Create the sample gallery data**

`app/src/content/sampleGallery.ts`:
```ts
// Bundled sample photos for the simulated gallery. Uses picsum seeds so no binary assets are needed.
export interface GalleryPhoto { id: string; url: string; }
export const sampleGallery: GalleryPhoto[] = Array.from({ length: 9 }, (_, i) => ({
  id: `photo-${i + 1}`,
  url: `https://picsum.photos/seed/astory${i + 1}/400/400`,
}));
```

- [ ] **Step 2: Create the PhotoSelectScreen**

`app/src/screens/PhotoSelectScreen.tsx`:
```tsx
import { useState } from 'react';
import { copy } from '../content/copy';
import { sampleGallery } from '../content/sampleGallery';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';

export function PhotoSelectScreen() {
  const { advance } = useFlow();
  const { session, update } = useSession();
  const [picked, setPicked] = useState<string[]>(session.photos);

  const toggle = (id: string) =>
    setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));

  const done = () => { update({ photos: picked }); advance(); };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 20, gap: 14 }}>
      <p style={{ fontSize: 20 }}>{copy.photos.title}</p>
      <p style={{ fontSize: 14, color: 'var(--ink-soft)' }}>{copy.photos.hint}</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, overflowY: 'auto', flex: 1 }}>
        {sampleGallery.map((ph) => {
          const on = picked.includes(ph.id);
          return (
            <button key={ph.id} onClick={() => toggle(ph.id)}
              style={{ position: 'relative', aspectRatio: '1', borderRadius: 12, overflow: 'hidden', outline: on ? '3px solid var(--accent)' : 'none' }}>
              <img src={ph.url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: on ? 1 : 0.85 }} />
              {on && <span style={{ position: 'absolute', top: 6, right: 6, background: 'var(--accent)', color: '#fff', borderRadius: '50%', width: 22, height: 22, display: 'grid', placeItems: 'center', fontSize: 13 }}>✓</span>}
            </button>
          );
        })}
      </div>
      <button disabled={picked.length === 0} onClick={done}
        style={{ padding: 14, borderRadius: 14, background: picked.length ? 'var(--ink)' : 'var(--hairline)', color: 'var(--paper)', fontSize: 16 }}>
        {copy.photos.done} {picked.length ? `(${picked.length})` : ''}
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Wire into App.tsx and verify**

Add the import + `{step === 'photos' && <PhotoSelectScreen />}`. Run `cd app && npm run dev`.
Expected: grid of photos; tapping toggles a ring + check; button disabled at 0 selected; continuing advances to review.

- [ ] **Step 4: Commit**

```bash
git add app/src/content/sampleGallery.ts app/src/screens/PhotoSelectScreen.tsx app/src/App.tsx
git commit -m "feat(app): multi-select photo gallery screen"
```

---

## Task 9: Photo review — horizontal strip + mic prompt

**Files:**
- Create: `app/src/screens/PhotoReviewScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** selected photos shown in a horizontal-scroll row of rounded-rectangle cards; below, a mic icon with `HandDrawnArrow` caption `copy.review.mic`; tapping the mic `advance()`s to record.

- [ ] **Step 1: Create the PhotoReviewScreen**

`app/src/screens/PhotoReviewScreen.tsx`:
```tsx
import { copy } from '../content/copy';
import { sampleGallery } from '../content/sampleGallery';
import { HandDrawnArrow } from '../components/HandDrawnArrow';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';

export function PhotoReviewScreen() {
  const { advance } = useFlow();
  const { session } = useSession();
  const chosen = sampleGallery.filter((p) => session.photos.includes(p.id));

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 20, gap: 22, justifyContent: 'center' }}>
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', padding: '8px 4px' }}>
        {chosen.map((p) => (
          <img key={p.id} src={p.url} alt=""
            style={{ width: 180, height: 240, flex: '0 0 auto', objectFit: 'cover', borderRadius: 18, boxShadow: '0 8px 20px rgba(0,0,0,0.18)' }} />
        ))}
      </div>
      <button onClick={advance} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, alignSelf: 'center' }}>
        <HandDrawnArrow caption={copy.review.mic} />
        <span style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--accent)', color: '#fff', display: 'grid', placeItems: 'center', fontSize: 30 }}>🎙</span>
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Wire into App.tsx and verify**

Add import + `{step === 'review' && <PhotoReviewScreen />}`. Run dev server.
Expected: chosen photos scroll horizontally as rounded cards; the mic+arrow appears beneath; tapping the mic advances to record.

- [ ] **Step 3: Commit**

```bash
git add app/src/screens/PhotoReviewScreen.tsx app/src/App.tsx
git commit -m "feat(app): photo review strip with mic prompt"
```

---

## Task 10: Record screen — mic capture + waveform

**Files:**
- Create: `app/src/components/MicButton.tsx`, `app/src/screens/RecordScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** a large record button; pressing starts `MediaRecorder` (animated pulsing while recording) and shows an elapsed timer; pressing again stops, stores an object URL + duration on the session, and `advance()`s. If mic permission is denied or unavailable, fall back to a "skip — we'll imagine it" button that advances with a 0-duration recording so the prototype never dead-ends.

- [ ] **Step 1: Create the MicButton component**

`app/src/components/MicButton.tsx`:
```tsx
import { motion } from 'framer-motion';

export function MicButton({ recording, onToggle }: { recording: boolean; onToggle: () => void }) {
  return (
    <motion.button onClick={onToggle} aria-pressed={recording}
      animate={recording ? { scale: [1, 1.08, 1] } : { scale: 1 }}
      transition={recording ? { repeat: Infinity, duration: 1.1 } : {}}
      style={{ width: 96, height: 96, borderRadius: '50%', background: recording ? 'var(--accent)' : 'var(--ink)', color: 'var(--paper)', fontSize: 34, display: 'grid', placeItems: 'center' }}>
      {recording ? '■' : '🎙'}
    </motion.button>
  );
}
```

- [ ] **Step 2: Create the RecordScreen**

`app/src/screens/RecordScreen.tsx`:
```tsx
import { useEffect, useRef, useState } from 'react';
import { copy } from '../content/copy';
import { MicButton } from '../components/MicButton';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';

export function RecordScreen() {
  const { advance } = useFlow();
  const { update } = useSession();
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState(false);
  const recRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const startedRef = useRef(0);

  useEffect(() => {
    if (!recording) return;
    const t = setInterval(() => setSeconds(Math.floor((Date.now() - startedRef.current) / 1000)), 250);
    return () => clearInterval(t);
  }, [recording]);

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      chunksRef.current = [];
      rec.ondataavailable = (e) => chunksRef.current.push(e.data);
      rec.onstop = () => {
        const url = URL.createObjectURL(new Blob(chunksRef.current, { type: 'audio/webm' }));
        update({ recordingUrl: url, recordingDurationSec: seconds });
        stream.getTracks().forEach((tk) => tk.stop());
        advance();
      };
      recRef.current = rec;
      startedRef.current = Date.now();
      setSeconds(0);
      rec.start();
      setRecording(true);
    } catch {
      setError(true);
    }
  };

  const stop = () => { recRef.current?.stop(); setRecording(false); };
  const skip = () => { update({ recordingUrl: 'simulated', recordingDurationSec: 0 }); advance(); };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 22, padding: 28, textAlign: 'center' }}>
      <p style={{ fontSize: 18, color: 'var(--ink-soft)' }}>{copy.record.prompt}</p>
      {recording && <p style={{ fontFamily: 'var(--font-hand)', fontSize: 28 }}>{seconds}s</p>}
      <MicButton recording={recording} onToggle={recording ? stop : start} />
      {recording && <button onClick={stop} style={{ color: 'var(--accent)' }}>{copy.record.stop}</button>}
      {error && <button onClick={skip} style={{ color: 'var(--ink-soft)', textDecoration: 'underline' }}>skip — we’ll imagine it</button>}
    </div>
  );
}
```

- [ ] **Step 3: Wire into App.tsx and verify**

Add import + `{step === 'record' && <RecordScreen />}`. Run dev server.
Expected: tapping the mic prompts for mic permission; while recording the button pulses and a timer counts; stopping advances to printing. Denying permission reveals the "skip" fallback, which also advances.

- [ ] **Step 4: Commit**

```bash
git add app/src/components/MicButton.tsx app/src/screens/RecordScreen.tsx app/src/App.tsx
git commit -m "feat(app): voice record screen with mic capture + skip fallback"
```

---

## Task 11: Carousel content service (TDD)

**Files:**
- Create: `app/src/content/houseSlides.ts`, `app/src/services/carouselContent.ts`, `app/src/services/carouselContent.test.ts`

**Acceptance criteria:** `buildSlides(session)` returns one `Slide` per house template, with captions interpolated from `creatorName`, `displayPartnerName(session)`, and `storyBeats` (cycled if fewer beats than slides).

- [ ] **Step 1: Create the house-slide asset list**

`app/src/content/houseSlides.ts`:
```ts
// House-style illustration frames for the faked reveal. Replace urls with real
// A Story of Two assets dropped into app/src/assets/ when available.
export interface HouseTemplate { id: string; imageUrl: string; captionTemplate: string; }
export const houseSlides: HouseTemplate[] = [
  { id: 's1', imageUrl: 'https://picsum.photos/seed/astory-draw1/900/1100', captionTemplate: 'the day {creator} first really saw {partner}.' },
  { id: 's2', imageUrl: 'https://picsum.photos/seed/astory-draw2/900/1100', captionTemplate: '{beat}' },
  { id: 's3', imageUrl: 'https://picsum.photos/seed/astory-draw3/900/1100', captionTemplate: '{beat}' },
  { id: 's4', imageUrl: 'https://picsum.photos/seed/astory-draw4/900/1100', captionTemplate: 'and still, {creator} & {partner}.' },
];
```

- [ ] **Step 2: Write the failing test**

`app/src/services/carouselContent.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { buildSlides } from './carouselContent';
import { createInitialSession } from '../session/session';
import { houseSlides } from '../content/houseSlides';

describe('buildSlides', () => {
  it('produces one slide per template with names interpolated', () => {
    const s = { ...createInitialSession(), creatorName: 'Arjun', partnerName: 'Mira', storyBeats: ['we met in the rain', 'we argued about coffee'] };
    const slides = buildSlides(s);
    expect(slides).toHaveLength(houseSlides.length);
    expect(slides[0].caption).toBe('the day Arjun first really saw Mira.');
    expect(slides[3].caption).toBe('and still, Arjun & Mira.');
  });

  it('fills {beat} slots from storyBeats, cycling if needed', () => {
    const s = { ...createInitialSession(), creatorName: 'A', partnerName: 'B', storyBeats: ['only beat'] };
    const slides = buildSlides(s);
    expect(slides[1].caption).toBe('only beat');
    expect(slides[2].caption).toBe('only beat'); // cycled
  });

  it('uses the warm placeholder when partner name is blank', () => {
    const s = { ...createInitialSession(), creatorName: 'A', partnerName: '', storyBeats: ['x'] };
    expect(buildSlides(s)[0].caption).toBe('the day A first really saw your person.');
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd app && npx vitest run src/services/carouselContent.test.ts`
Expected: FAIL — cannot resolve `./carouselContent`.

- [ ] **Step 4: Write minimal implementation**

`app/src/services/carouselContent.ts`:
```ts
import type { SessionState, Slide } from '../session/session';
import { displayPartnerName } from '../session/session';
import { houseSlides } from '../content/houseSlides';

export function buildSlides(session: SessionState): Slide[] {
  const creator = session.creatorName.trim() || 'someone';
  const partner = displayPartnerName(session);
  let beatIdx = 0;
  const beats = session.storyBeats.length ? session.storyBeats : ['a story still being written'];

  return houseSlides.map((t) => {
    const caption = t.captionTemplate
      .replace(/\{creator\}/g, creator)
      .replace(/\{partner\}/g, partner)
      .replace(/\{beat\}/g, () => beats[beatIdx++ % beats.length]);
    return { id: t.id, imageUrl: t.imageUrl, caption };
  });
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd app && npx vitest run src/services/carouselContent.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add app/src/content/houseSlides.ts app/src/services/carouselContent.ts app/src/services/carouselContent.test.ts
git commit -m "feat(app): house-style slide builder with caption interpolation"
```

---

## Task 12: Fake generation service (TDD)

**Files:**
- Create: `app/src/services/fakeGeneration.ts`, `app/src/services/fakeGeneration.test.ts`

**Acceptance criteria:** `deriveStoryBeats(session)` returns a deterministic, non-empty list of believable beats seeded from the names + relationship (so the same session always yields the same beats). `PHASE_TIMINGS` exposes the greet/read/feed durations (ms) used by the printing screen.

- [ ] **Step 1: Write the failing test**

`app/src/services/fakeGeneration.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { deriveStoryBeats, PHASE_TIMINGS } from './fakeGeneration';
import { createInitialSession } from '../session/session';

describe('fakeGeneration', () => {
  it('derives a deterministic, non-empty set of beats from the session', () => {
    const s = { ...createInitialSession(), relationship: 'together' as const, creatorName: 'Arjun', partnerName: 'Mira' };
    const a = deriveStoryBeats(s);
    const b = deriveStoryBeats(s);
    expect(a.length).toBeGreaterThanOrEqual(3);
    expect(a).toEqual(b); // deterministic
    expect(a.join(' ')).toContain('Mira'); // personalized
  });

  it('changes when names change', () => {
    const base = { ...createInitialSession(), relationship: 'sending' as const, creatorName: 'A', partnerName: 'B' };
    const other = { ...base, partnerName: 'C' };
    expect(deriveStoryBeats(base)).not.toEqual(deriveStoryBeats(other));
  });

  it('exposes positive phase timings', () => {
    expect(PHASE_TIMINGS.greet).toBeGreaterThan(0);
    expect(PHASE_TIMINGS.read).toBeGreaterThan(0);
    expect(PHASE_TIMINGS.feed).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && npx vitest run src/services/fakeGeneration.test.ts`
Expected: FAIL — cannot resolve `./fakeGeneration`.

- [ ] **Step 3: Write minimal implementation**

`app/src/services/fakeGeneration.ts`:
```ts
import type { SessionState } from '../session/session';
import { displayPartnerName } from '../session/session';

export const PHASE_TIMINGS = { greet: 3500, read: 6000, feed: 5500 } as const;

const TOGETHER = (p: string) => [
  `the small fights that end in laughing about ${p}`,
  `the way ${p} hums when the food is good`,
  `choosing each other again on an ordinary Tuesday`,
];
const SENDING = (p: string) => [
  `the distance that never quite reached ${p}`,
  `saving the good news to tell ${p} first`,
  `counting days until ${p} is close again`,
];

export function deriveStoryBeats(session: SessionState): string[] {
  const p = displayPartnerName(session);
  return session.relationship === 'sending' ? SENDING(p) : TOGETHER(p);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && npx vitest run src/services/fakeGeneration.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add app/src/services/fakeGeneration.ts app/src/services/fakeGeneration.test.ts
git commit -m "feat(app): faked story-beat derivation + phase timings"
```

---

## Task 13: Carousel component + reveal wiring helper

**Files:**
- Create: `app/src/components/Carousel.tsx`

**Acceptance criteria:** a swipeable/clickable horizontal carousel that shows `Slide` images with captions and a dot indicator; works with mouse drag and arrow taps. (Used by the reveal screen in Task 15 and conceptually by the feed in Task 14.)

- [ ] **Step 1: Create the Carousel component**

`app/src/components/Carousel.tsx`:
```tsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Slide } from '../session/session';

export function Carousel({ slides }: { slides: Slide[] }) {
  const [i, setI] = useState(0);
  const go = (d: number) => setI((p) => Math.max(0, Math.min(slides.length - 1, p + d)));
  if (!slides.length) return null;
  const s = slides[i];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, width: '100%' }}>
      <div style={{ position: 'relative', width: '100%', aspectRatio: '9/11', borderRadius: 18, overflow: 'hidden', background: 'var(--paper-shadow)' }}>
        <AnimatePresence mode="wait">
          <motion.img key={s.id} src={s.imageUrl} alt={s.caption}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}
            drag="x" dragConstraints={{ left: 0, right: 0 }}
            onDragEnd={(_, info) => { if (info.offset.x < -60) go(1); if (info.offset.x > 60) go(-1); }}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AnimatePresence>
      </div>
      <p style={{ fontFamily: 'var(--font-hand)', fontSize: 22, textAlign: 'center', minHeight: 56 }}>{s.caption}</p>
      <div style={{ display: 'flex', gap: 6 }}>
        {slides.map((sl, idx) => (
          <span key={sl.id} onClick={() => setI(idx)}
            style={{ width: 8, height: 8, borderRadius: '50%', background: idx === i ? 'var(--ink)' : 'var(--hairline)' }} />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd app && npx tsc -b --noEmit`
Expected: no type errors.

- [ ] **Step 3: Commit**

```bash
git add app/src/components/Carousel.tsx
git commit -m "feat(app): swipeable carousel component"
```

---

## Task 14: Printing screen — the mixed wait

**Files:**
- Create: `app/src/screens/PrintingScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** on mount, computes story beats (`deriveStoryBeats`) and slides (`buildSlides`) and writes them to the session, then runs three timed phases using `PHASE_TIMINGS`: (1) **greet** — brand voice greets by name + a hand-drawn "printing" animation; (2) **read** — a short story/letter; (3) **feed** — a swipeable feed of real carousels with a single dismissable follow ask (`copy.printing.askOnce` / `copy.printing.follow`). After the feed phase, `advance()` to reveal. A skip-ahead affordance is allowed but the follow ask must never block.

- [ ] **Step 1: Create the PrintingScreen**

`app/src/screens/PrintingScreen.tsx`:
```tsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { copy } from '../content/copy';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';
import { deriveStoryBeats, PHASE_TIMINGS } from '../services/fakeGeneration';
import { buildSlides } from '../services/carouselContent';

type Phase = 'greet' | 'read' | 'feed';

export function PrintingScreen() {
  const { advance } = useFlow();
  const { session, update } = useSession();
  const [phase, setPhase] = useState<Phase>('greet');
  const [followed, setFollowed] = useState(false);
  const [askDismissed, setAskDismissed] = useState(false);

  // Compute the faked generation once on mount.
  useEffect(() => {
    const beats = deriveStoryBeats(session);
    update({ storyBeats: beats, slides: buildSlides({ ...session, storyBeats: beats }) });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const t1 = setTimeout(() => setPhase('read'), PHASE_TIMINGS.greet);
    const t2 = setTimeout(() => setPhase('feed'), PHASE_TIMINGS.greet + PHASE_TIMINGS.read);
    const t3 = setTimeout(() => advance(), PHASE_TIMINGS.greet + PHASE_TIMINGS.read + PHASE_TIMINGS.feed);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const name = session.creatorName || 'friend';

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 24, gap: 16, justifyContent: 'center' }}>
      <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 2 }}
        style={{ fontFamily: 'var(--font-hand)', fontSize: 16, color: 'var(--ink-soft)', textAlign: 'center' }}>
        …drawing your story…
      </motion.div>

      {phase === 'greet' && (
        <p style={{ fontSize: 20, lineHeight: 1.4, textAlign: 'center' }}>{copy.printing.greet(name)}</p>
      )}

      {phase === 'read' && (
        <p style={{ fontSize: 16, lineHeight: 1.6 }}>
          We started A Story of Two for one couple, on cheap paper, late at night. Every story since has been
          someone trusting us with the smallest true thing about their love. Yours is printing now.
        </p>
      )}

      {phase === 'feed' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', gap: 10, overflowX: 'auto' }}>
            {[1, 2, 3].map((n) => (
              <img key={n} src={`https://picsum.photos/seed/astory-feed${n}/300/380`} alt=""
                style={{ width: 150, height: 190, flex: '0 0 auto', borderRadius: 14, objectFit: 'cover' }} />
            ))}
          </div>
          {!askDismissed && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}>
              <p style={{ fontSize: 13, color: 'var(--ink-soft)', textAlign: 'center' }}>{copy.printing.askOnce}</p>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => setFollowed(true)}
                  style={{ padding: '8px 16px', borderRadius: 12, background: followed ? 'var(--ink)' : 'var(--accent)', color: '#fff', fontSize: 14 }}>
                  {followed ? 'following ♥' : copy.printing.follow}
                </button>
                <button onClick={() => setAskDismissed(true)} style={{ color: 'var(--ink-soft)', fontSize: 13 }}>not now</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Wire into App.tsx and verify**

Add import + `{step === 'printing' && <PrintingScreen />}`. Run dev server, walk to printing.
Expected: a pulsing "drawing your story" line; greet text greets by name; ~3.5s later a short letter; then a feed with a single follow ask that can be dismissed; after the feed phase it auto-advances to reveal. `session.slides` is populated.

- [ ] **Step 3: Commit**

```bash
git add app/src/screens/PrintingScreen.tsx app/src/App.tsx
git commit -m "feat(app): mixed printing/wait screen (greet/read/feed + soft follow ask)"
```

---

## Task 15: Reveal + rate screens

**Files:**
- Create: `app/src/screens/RevealScreen.tsx`, `app/src/screens/RateScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** RevealScreen renders `copy.reveal.title` + the `Carousel` of `session.slides` with a soft entrance, and a continue button → `advance()` to rate. RateScreen shows `copy.rate.prompt` + a 5-star picker writing `session.rating`; a continue button (enabled once rated) → `advance()` to send.

- [ ] **Step 1: Create the RevealScreen**

`app/src/screens/RevealScreen.tsx`:
```tsx
import { motion } from 'framer-motion';
import { copy } from '../content/copy';
import { Carousel } from '../components/Carousel';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';

export function RevealScreen() {
  const { advance } = useFlow();
  const { session } = useSession();
  return (
    <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }}
      style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 20, gap: 14, justifyContent: 'center' }}>
      <p style={{ fontSize: 22, textAlign: 'center' }}>{copy.reveal.title}</p>
      <Carousel slides={session.slides ?? []} />
      <button onClick={advance} style={{ padding: 14, borderRadius: 14, background: 'var(--ink)', color: 'var(--paper)', fontSize: 16 }}>
        continue
      </button>
    </motion.div>
  );
}
```

- [ ] **Step 2: Create the RateScreen**

`app/src/screens/RateScreen.tsx`:
```tsx
import { useState } from 'react';
import { copy } from '../content/copy';
import { useFlow } from '../flow/FlowProvider';
import { useSession } from '../session/SessionProvider';

export function RateScreen() {
  const { advance } = useFlow();
  const { session, update } = useSession();
  const [rating, setRating] = useState(session.rating ?? 0);

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 22, padding: 28 }}>
      <p style={{ fontSize: 20, textAlign: 'center' }}>{copy.rate.prompt}</p>
      <div style={{ display: 'flex', gap: 8 }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} onClick={() => { setRating(n); update({ rating: n }); }}
            style={{ fontSize: 36, color: n <= rating ? 'var(--accent)' : 'var(--hairline)' }} aria-label={`${n} stars`}>
            ★
          </button>
        ))}
      </div>
      <button disabled={rating === 0} onClick={advance}
        style={{ padding: 14, borderRadius: 14, background: rating ? 'var(--ink)' : 'var(--hairline)', color: 'var(--paper)', fontSize: 16, width: '100%' }}>
        continue
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Wire both into App.tsx and verify**

Add imports + `{step === 'reveal' && <RevealScreen />}` and `{step === 'rate' && <RateScreen />}`. Run dev server.
Expected: reveal shows the captioned carousel (swipeable), continue → rate; stars set the rating; continue (enabled after rating) → send.

- [ ] **Step 4: Commit**

```bash
git add app/src/screens/RevealScreen.tsx app/src/screens/RateScreen.tsx app/src/App.tsx
git commit -m "feat(app): reveal carousel + rating screens"
```

---

## Task 16: Share service (TDD)

**Files:**
- Create: `app/src/services/share.ts`, `app/src/services/share.test.ts`

**Acceptance criteria:** `buildShareMessage(session)` returns `{ text, inviteUrl }` where `text` addresses the partner by name and `inviteUrl` is the A Story invite (so the gift doubles as the referral). `SHARE_TARGETS` lists the send-only destinations (no download/copy). `shareTo` is a thin wrapper documented as side-effecting (not unit-tested for the navigator call).

- [ ] **Step 1: Write the failing test**

`app/src/services/share.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { buildShareMessage, SHARE_TARGETS } from './share';
import { createInitialSession } from '../session/session';

describe('share', () => {
  it('addresses the partner and carries the invite url', () => {
    const s = { ...createInitialSession(), creatorName: 'Arjun', partnerName: 'Mira' };
    const msg = buildShareMessage(s);
    expect(msg.text).toContain('Mira');
    expect(msg.text.toLowerCase()).toContain('arjun');
    expect(msg.inviteUrl).toMatch(/^https?:\/\//);
  });

  it('falls back to the warm placeholder for a blank partner name', () => {
    const s = { ...createInitialSession(), creatorName: 'Arjun', partnerName: '' };
    expect(buildShareMessage(s).text).toContain('your person');
  });

  it('offers only send-only targets (no download/copy)', () => {
    const ids = SHARE_TARGETS.map((t) => t.id);
    expect(ids).toEqual(['whatsapp', 'whatsapp-status', 'instagram-story', 'wallpaper-mobile', 'wallpaper-desktop']);
    expect(ids).not.toContain('download');
    expect(ids).not.toContain('copy');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && npx vitest run src/services/share.test.ts`
Expected: FAIL — cannot resolve `./share`.

- [ ] **Step 3: Write minimal implementation**

`app/src/services/share.ts`:
```ts
import type { SessionState } from '../session/session';
import { displayPartnerName } from '../session/session';

export const INVITE_URL = 'https://astoryof.two/app';

export interface ShareMessage { text: string; inviteUrl: string; }

export function buildShareMessage(session: SessionState): ShareMessage {
  const creator = session.creatorName.trim() || 'someone who loves you';
  const partner = displayPartnerName(session);
  return {
    text: `${partner} — ${creator} made this for you. our story, drawn. ${INVITE_URL}`,
    inviteUrl: INVITE_URL,
  };
}

export type ShareTargetId =
  | 'whatsapp' | 'whatsapp-status' | 'instagram-story' | 'wallpaper-mobile' | 'wallpaper-desktop';

export interface ShareTarget { id: ShareTargetId; label: string; }

export const SHARE_TARGETS: ShareTarget[] = [
  { id: 'whatsapp', label: 'send on WhatsApp' },
  { id: 'whatsapp-status', label: 'WhatsApp status' },
  { id: 'instagram-story', label: 'Instagram story' },
  { id: 'wallpaper-mobile', label: 'set as phone wallpaper' },
  { id: 'wallpaper-desktop', label: 'desktop wallpaper' },
];

// Side-effecting: uses the Web Share API where available, else simulates.
export async function shareTo(target: ShareTarget, msg: ShareMessage): Promise<void> {
  if (target.id === 'whatsapp' && 'share' in navigator) {
    try { await navigator.share({ text: msg.text, url: msg.inviteUrl }); return; } catch { /* fall through */ }
  }
  // Prototype fallback: log the intended action.
  console.info(`[share] ${target.label}:`, msg.text);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && npx vitest run src/services/share.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add app/src/services/share.ts app/src/services/share.test.ts
git commit -m "feat(app): share service — gift-as-referral message + send-only targets"
```

---

## Task 17: Send screen — unlock = gift + send-only surface

**Files:**
- Create: `app/src/screens/SendScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** a primary button `copy.send.primary(displayPartnerName)` — tapping it reveals the send-only surface listing `SHARE_TARGETS` (each calls `shareTo`); shows `copy.send.note` (no downloads). On first reveal of the surface, call `recordCarouselCreated()` exactly once (this is the completed carousel). No download/copy button anywhere.

- [ ] **Step 1: Create the SendScreen**

`app/src/screens/SendScreen.tsx`:
```tsx
import { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { copy } from '../content/copy';
import { useSession } from '../session/SessionProvider';
import { displayPartnerName } from '../session/session';
import { SHARE_TARGETS, buildShareMessage, shareTo } from '../services/share';
import { recordCarouselCreated } from '../session/deviceId';

export function SendScreen() {
  const { session } = useSession();
  const [open, setOpen] = useState(false);
  const counted = useRef(false);
  const partner = displayPartnerName(session);
  const msg = buildShareMessage(session);

  const reveal = () => {
    if (!counted.current) { recordCarouselCreated(); counted.current = true; }
    setOpen(true);
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, padding: 28 }}>
      {!open ? (
        <motion.button whileTap={{ scale: 0.95 }} onClick={reveal}
          style={{ padding: '16px 28px', borderRadius: 16, background: 'var(--accent)', color: '#fff', fontSize: 20 }}>
          {copy.send.primary(partner)}
        </motion.button>
      ) : (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          style={{ display: 'flex', flexDirection: 'column', gap: 10, width: '100%' }}>
          {SHARE_TARGETS.map((t) => (
            <button key={t.id} onClick={() => shareTo(t, msg)}
              style={{ padding: 14, borderRadius: 14, border: '1.5px solid var(--hairline)', fontSize: 16, textAlign: 'left' }}>
              {t.label}
            </button>
          ))}
          <p style={{ fontSize: 13, color: 'var(--ink-soft)', textAlign: 'center', marginTop: 6 }}>{copy.send.note}</p>
        </motion.div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Wire into App.tsx and verify**

Add import + `{step === 'send' && <SendScreen />}`. Run dev server, walk to send.
Expected: a single "send it to [name]" button; tapping reveals the five send-only targets + the "no downloads" note; there is no download or copy button. Tapping WhatsApp triggers the share sheet (or logs in the console fallback).

- [ ] **Step 3: Commit**

```bash
git add app/src/screens/SendScreen.tsx app/src/App.tsx
git commit -m "feat(app): send screen — gift unlock + send-only share surface"
```

---

## Task 18: Cap-reached screen + final wiring

**Files:**
- Create: `app/src/screens/CapReachedScreen.tsx`
- Modify: `app/src/App.tsx`

**Acceptance criteria:** when `step === 'cap-reached'`, show `copy.cap.title` + `copy.cap.body` and a single "back to start" button → `goTo('landing')`. (Reachable from landing when `hasReachedCap()` is true after three completed carousels.)

- [ ] **Step 1: Create the CapReachedScreen**

`app/src/screens/CapReachedScreen.tsx`:
```tsx
import { copy } from '../content/copy';
import { useFlow } from '../flow/FlowProvider';

export function CapReachedScreen() {
  const { goTo } = useFlow();
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, padding: 32, textAlign: 'center' }}>
      <p style={{ fontSize: 24, fontFamily: 'var(--font-hand)' }}>{copy.cap.title}</p>
      <p style={{ fontSize: 16, lineHeight: 1.5, color: 'var(--ink-soft)' }}>{copy.cap.body}</p>
      <button onClick={() => goTo('landing')} style={{ padding: 14, borderRadius: 14, background: 'var(--ink)', color: 'var(--paper)', fontSize: 16 }}>
        back to start
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Wire into App.tsx and verify the cap path**

Add import + `{step === 'cap-reached' && <CapReachedScreen />}`. To verify without making three carousels, temporarily run `localStorage.setItem('astory.carouselsCreated','3')` in the browser console, then tap `+` on landing.
Expected: the cap screen appears; "back to start" returns to landing. Clear the key (`localStorage.clear()`) afterward.

- [ ] **Step 3: Commit**

```bash
git add app/src/screens/CapReachedScreen.tsx app/src/App.tsx
git commit -m "feat(app): cap-reached screen + landing cap branch"
```

---

## Task 19: Polish pass — remove scaffolding, full-flow verification

**Files:**
- Modify: `app/src/App.tsx` (remove the temporary back/next nav fallback)

- [ ] **Step 1: Remove the temporary nav fallback**

In `app/src/App.tsx`, delete the temporary `{step !== 'landing' && (...back/next...)}` block so only real screens render. The `CurrentScreen` switch should now map every step to its screen:
```tsx
{step === 'landing' && <LandingScreen />}
{step === 'hello' && <HelloScreen />}
{step === 'photos' && <PhotoSelectScreen />}
{step === 'review' && <PhotoReviewScreen />}
{step === 'record' && <RecordScreen />}
{step === 'printing' && <PrintingScreen />}
{step === 'reveal' && <RevealScreen />}
{step === 'rate' && <RateScreen />}
{step === 'send' && <SendScreen />}
{step === 'cap-reached' && <CapReachedScreen />}
```

- [ ] **Step 2: Run the full test suite**

Run: `cd app && npm test`
Expected: all suites pass (steps, session, deviceId, carouselContent, fakeGeneration, share).

- [ ] **Step 3: Type-check and build**

Run: `cd app && npm run build`
Expected: `tsc -b` passes and `vite build` produces `app/dist` with no errors.

- [ ] **Step 4: Full-flow browser verification**

Run: `cd app && npm run dev` and walk the entire flow start to finish:
Expected: landing → `+` → hello (pick relationship + names) → photos (multi-select) → review (horizontal strip + mic) → record (mic or skip) → printing (greet → read → feed, dismissable follow) → reveal (captioned swipeable carousel with the names you entered) → rate (stars) → send ("send it to [name]" → five send-only targets, no download). Transitions animate; `prefers-reduced-motion` disables them. Reloading after a full run and making three total carousels lands on the cap screen.

- [ ] **Step 5: Commit**

```bash
git add app/src/App.tsx
git commit -m "feat(app): finalize flow wiring; remove scaffolding nav"
```

---

## Self-review notes (author check against the spec)

- **Spec coverage:** landing/paper + disclaimer (T6), no-onboarding device-id + name capture (T4, T7), multi-select photos (T8), horizontal review strip + mic (T9), voice record (T10), mixed wait greet/read/feed + single honest follow ask (T14), house-style faked reveal captioned with names/beats (T11–T13, T15), rate (T15), unlock = gift = referral (T16–T17), send-only surface incl. wallpaper (T16–T17), 3-cap silent + cap state (T4, T18). All locked decisions map to tasks.
- **Faked seams:** transcription/uniqueness/generation are all simulated (T11, T12, T14); agent always "loves" the story (happy path) — matches the out-of-scope list.
- **Type consistency:** `Step`/`ORDER` (T2), `SessionState`/`Slide`/`displayPartnerName` (T3) reused unchanged in T5/T11/T12/T16/T17; `buildSlides`, `deriveStoryBeats`, `PHASE_TIMINGS`, `buildShareMessage`, `SHARE_TARGETS`, `shareTo` names are consistent between their defining tasks and consumers.
- **Out of scope (unbuilt, per spec):** real generation/moderation, accounts, payments, live IG/WhatsApp APIs, rejection path.
```
