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
