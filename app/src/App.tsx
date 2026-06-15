import { AnimatePresence, motion } from 'framer-motion';
import './styles/tokens.css';
import './styles/global.css';
import { PhoneFrame } from './components/PhoneFrame';
import { PaperBackground } from './components/PaperBackground';
import { FlowProvider, useFlow } from './flow/FlowProvider';
import { SessionProvider } from './session/SessionProvider';
import { LandingScreen } from './screens/LandingScreen';
import { HelloScreen } from './screens/HelloScreen';
import { PhotoSelectScreen } from './screens/PhotoSelectScreen';
import { PhotoReviewScreen } from './screens/PhotoReviewScreen';
import { RecordScreen } from './screens/RecordScreen';
import { PrintingScreen } from './screens/PrintingScreen';
import { RevealScreen } from './screens/RevealScreen';
import { RateScreen } from './screens/RateScreen';
import { SendScreen } from './screens/SendScreen';

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
        {step === 'landing' && <LandingScreen />}
        {step === 'hello' && <HelloScreen />}
        {step === 'photos' && <PhotoSelectScreen />}
        {step === 'review' && <PhotoReviewScreen />}
        {step === 'record' && <RecordScreen />}
        {step === 'printing' && <PrintingScreen />}
        {step === 'reveal' && <RevealScreen />}
        {step === 'rate' && <RateScreen />}
        {step === 'send' && <SendScreen />}
        {!['landing', 'hello', 'photos', 'review', 'record', 'printing', 'reveal', 'rate', 'send'].includes(step) && (
          <div style={{ marginTop: 'auto' }}>
            <p>step: {step}</p>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={back}>back</button><button onClick={advance}>next</button>
            </div>
          </div>
        )}
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
