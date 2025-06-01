'use client';

import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BreathPattern {
  inhale: number;
  hold: number;
  exhale: number;
  pause: number;
}

interface BreathingAnimationProps {
  isPlaying: boolean;
  pattern: BreathPattern;
}

type BreathPhase = 'inhale' | 'hold' | 'exhale' | 'pause';

export function BreathingAnimation({ isPlaying, pattern }: BreathingAnimationProps) {
  const [phase, setPhase] = useState<BreathPhase>('inhale');
  const [text, setText] = useState('Inhale');
  const [count, setCount] = useState(pattern.inhale);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // For announcing changes to screen readers
  const ariaLiveRef = useRef<HTMLDivElement>(null);
  
  // Calculate total cycle time
  const totalCycle = pattern.inhale + pattern.hold + pattern.exhale + pattern.pause;
  
  useEffect(() => {
    if (!isPlaying) {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      setPhase('inhale');
      setText('Inhale');
      setCount(pattern.inhale);
      return;
    }
    
    const nextPhase = () => {
      if (count > 1) {
        setCount(count - 1);
        return;
      }
      
      // Transition to next phase
      switch (phase) {
        case 'inhale':
          setPhase('hold');
          setText('Hold');
          setCount(pattern.hold || 1);
          break;
        case 'hold':
          setPhase('exhale');
          setText('Exhale');
          setCount(pattern.exhale);
          break;
        case 'exhale':
          setPhase('pause');
          setText('Pause');
          setCount(pattern.pause || 1);
          break;
        case 'pause':
          setPhase('inhale');
          setText('Inhale');
          setCount(pattern.inhale);
          break;
      }
    };
    
    timerRef.current = setTimeout(nextPhase, 1000);
    
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [isPlaying, count, phase, pattern]);
  
  // Update the aria-live region whenever the phase or count changes
  useEffect(() => {
    if (ariaLiveRef.current) {
      ariaLiveRef.current.textContent = `${text} ${count}`;
    }
  }, [text, count]);
  
  // Calculate the circle size based on phase
  const getCircleSize = () => {
    switch (phase) {
      case 'inhale':
        // Start small, grow to full size
        const inhalePct = (pattern.inhale - count + 1) / pattern.inhale;
        return 40 + 160 * inhalePct;
      case 'hold':
        // Stay at full size
        return 200;
      case 'exhale':
        // Shrink back down
        const exhalePct = count / pattern.exhale;
        return 40 + 160 * exhalePct;
      case 'pause':
        // Stay at small size
        return 40;
      default:
        return 120;
    }
  };
  
  // Get text color based on phase
  const getTextClass = () => {
    switch (phase) {
      case 'inhale':
        return 'text-sage-600';
      case 'hold':
        return 'text-sage-700';
      case 'exhale':
        return 'text-cream-600';
      case 'pause':
        return 'text-cream-700';
      default:
        return 'text-sage-600';
    }
  };
  
  // Get circle color based on phase
  const getCircleClass = () => {
    switch (phase) {
      case 'inhale':
        return 'bg-sage-100 border-sage-200';
      case 'hold':
        return 'bg-sage-200 border-sage-300';
      case 'exhale':
        return 'bg-cream-100 border-cream-200';
      case 'pause':
        return 'bg-cream-200 border-cream-300';
      default:
        return 'bg-sage-100 border-sage-200';
    }
  };
  
  // Get descriptive text for pattern
  const getPatternDescription = () => {
    return `Breathing pattern: Inhale for ${pattern.inhale} seconds, hold for ${pattern.hold} seconds, exhale for ${pattern.exhale} seconds${pattern.pause ? `, pause for ${pattern.pause} seconds` : ''}.`;
  };
  
  return (
    <div 
      className="w-full h-full flex items-center justify-center"
      role="region" 
      aria-label="Breathing exercise animation"
      aria-live="polite"
    >
      {/* Hidden screen reader text */}
      <div 
        ref={ariaLiveRef} 
        className="sr-only" 
        aria-live="assertive"
      >
        {`${text} ${count}`}
      </div>
      
      <div className="relative flex flex-col items-center justify-center">
        <motion.div
          animate={{
            width: getCircleSize(),
            height: getCircleSize(),
          }}
          transition={{
            duration: 1,
            ease: "easeInOut"
          }}
          className={`rounded-full ${getCircleClass()} border-2 flex items-center justify-center`}
          role="img"
          aria-label={`Breathing circle, current phase: ${phase}`}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={`${phase}-${count}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex flex-col items-center justify-center"
            >
              <span className={`text-2xl font-semibold ${getTextClass()}`}>{text}</span>
              <span className={`text-4xl font-bold ${getTextClass()}`}>{count}</span>
            </motion.div>
          </AnimatePresence>
        </motion.div>
        
        {!isPlaying && (
          <div 
            className="absolute inset-0 flex items-center justify-center" 
            aria-live="polite"
          >
            <div className="text-sage-500 text-center">
              <p className="text-sm mb-1">Press play to start</p>
              <p className="text-xs text-sage-400" aria-label={getPatternDescription()}>
                {pattern.inhale}-{pattern.hold}-{pattern.exhale}
                {pattern.pause ? `-${pattern.pause}` : ''} pattern
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 