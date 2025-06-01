'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { FiClock, FiPlay, FiPause, FiRepeat, FiChevronLeft, FiCheck, FiX } from 'react-icons/fi';

import { Card, CardContent } from '../../../../../components/ui/Card';
import { Button } from '../../../../../components/ui/Button';
import { BreathingAnimation } from '../../../../../components/exercises/BreathingAnimation';

// Demo exercise data
const demoExercises = [
  {
    id: '1',
    title: 'Mindful Breathing',
    description: 'A simple breathing exercise to calm your mind and reduce anxiety.',
    longDescription: 'This mindful breathing exercise helps you focus on your breath, bringing your attention to the present moment. Regular practice can reduce stress, lower anxiety, and improve focus.',
    instructions: [
      'Find a comfortable seated position with your back straight',
      'Close your eyes or maintain a soft gaze',
      'Breathe naturally through your nose',
      'Focus your attention on the sensation of breathing',
      'When your mind wanders, gently bring it back to your breath',
      'Continue for the duration of the exercise'
    ],
    duration: 5,
    category: 'breathing',
    level: 'beginner',
    imageUrl: '/images/breathing.jpg',
    breathPattern: { inhale: 4, hold: 2, exhale: 6, pause: 2 }
  },
  {
    id: '2',
    title: 'Body Scan Meditation',
    description: 'A progressive relaxation technique to release tension in your body.',
    longDescription: 'The body scan is a form of meditation that involves mentally scanning your body from head to toe, bringing awareness to each part and noticing any sensations without judgment.',
    instructions: [
      'Lie down on your back in a comfortable position',
      'Close your eyes and take a few deep breaths',
      'Begin to focus your attention at the top of your head',
      'Slowly move your attention down through your body',
      'Notice any sensations without trying to change them',
      'If your mind wanders, gently bring it back'
    ],
    duration: 10,
    category: 'meditation',
    level: 'intermediate',
    imageUrl: '/images/body-scan.jpg'
  },
  {
    id: '4',
    title: '4-7-8 Breathing Technique',
    description: 'A breathing pattern that promotes relaxation and helps with falling asleep.',
    longDescription: 'The 4-7-8 breathing technique is a powerful tool that acts as a natural tranquilizer for the nervous system. It can help reduce anxiety, manage stress, and even help with falling asleep more quickly.',
    instructions: [
      'Sit in a comfortable position with your back straight',
      'Place the tip of your tongue against the roof of your mouth',
      'Exhale completely through your mouth, making a whoosh sound',
      'Close your mouth and inhale through your nose for 4 counts',
      'Hold your breath for 7 counts',
      'Exhale completely through your mouth for 8 counts',
      'Repeat the cycle 3-4 times'
    ],
    duration: 3,
    category: 'breathing',
    level: 'beginner',
    imageUrl: '/images/4-7-8.jpg',
    breathPattern: { inhale: 4, hold: 7, exhale: 8, pause: 0 }
  }
];

export default function ExercisePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [isLoading, setIsLoading] = useState(true);
  const [exercise, setExercise] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Simulate loading data
  useEffect(() => {
    const loadExercise = () => {
      const foundExercise = demoExercises.find(ex => ex.id === id);
      if (foundExercise) {
        setExercise(foundExercise);
        setTimeRemaining(foundExercise.duration * 60); // Convert to seconds
      } else {
        // Exercise not found, redirect
        router.push('/dashboard/exercises');
      }
      setIsLoading(false);
    };
    
    const timer = setTimeout(loadExercise, 800);
    return () => clearTimeout(timer);
  }, [id, router]);
  
  // Timer logic
  useEffect(() => {
    if (isPlaying && timeRemaining > 0) {
      timerRef.current = setTimeout(() => {
        setTimeRemaining(prevTime => {
          if (prevTime <= 1) {
            setIsPlaying(false);
            setCompleted(true);
            setShowCompletionModal(true);
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    }
    
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [isPlaying, timeRemaining]);
  
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };
  
  const resetTimer = () => {
    setIsPlaying(false);
    setTimeRemaining(exercise.duration * 60);
    setCompleted(false);
  };
  
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  const handleComplete = () => {
    setShowCompletionModal(false);
    // In a real app, you would save completion data to the server here
  };
  
  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-cream-100 rounded-lg w-1/2"></div>
        <div className="h-64 bg-cream-100 rounded-lg"></div>
        <div className="h-32 bg-cream-100 rounded-lg"></div>
      </div>
    );
  }
  
  if (!exercise) {
    return <div>Exercise not found</div>;
  }
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-6 flex items-center">
        <button 
          onClick={() => router.push('/dashboard/exercises')}
          className="mr-3 p-2 rounded-full hover:bg-cream-100 text-sage-700"
        >
          <FiChevronLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">{exercise.title}</h1>
          <p className="text-sage-600 mt-1">{exercise.description}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content and instructions */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardContent className="p-6">
              <p className="text-sage-700 leading-relaxed">{exercise.longDescription}</p>
              
              <div className="mt-6">
                <h2 className="text-lg font-semibold text-sage-800 mb-3">Instructions</h2>
                <ol className="space-y-2 pl-4">
                  {exercise.instructions.map((instruction: string, index: number) => (
                    <li key={index} className="text-sage-700">
                      <span className="font-medium text-sage-600 mr-2">{index + 1}.</span> {instruction}
                    </li>
                  ))}
                </ol>
              </div>
              
              <div className="flex items-center mt-6 space-x-3">
                <span className="text-sm font-medium bg-sage-100 text-sage-700 px-3 py-1 rounded-full flex items-center">
                  <FiClock className="mr-1" /> {exercise.duration} minutes
                </span>
                <span className="text-sm font-medium bg-cream-100 text-sage-700 px-3 py-1 rounded-full capitalize">
                  {exercise.level}
                </span>
                <span className="text-sm font-medium bg-mist-100 text-sage-700 px-3 py-1 rounded-full capitalize">
                  {exercise.category}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Exercise timer and controls */}
        <div className="space-y-6">
          <Card className="overflow-hidden">
            <div className="aspect-square bg-sage-100 flex items-center justify-center relative">
              {exercise.breathPattern ? (
                <BreathingAnimation 
                  isPlaying={isPlaying} 
                  pattern={exercise.breathPattern}
                />
              ) : (
                <div className="text-4xl text-sage-400 font-light">
                  {formatTime(timeRemaining)}
                </div>
              )}
              
              {completed && (
                <div className="absolute inset-0 bg-sage-50/80 flex items-center justify-center">
                  <div className="text-sage-700 font-medium text-lg text-center">
                    <FiCheck className="mx-auto text-3xl text-sage-600 mb-2" />
                    Exercise Completed
                  </div>
                </div>
              )}
            </div>
            
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-4">
                <div className="font-medium text-sage-800">Time Remaining</div>
                <div className="text-xl font-semibold text-sage-800">{formatTime(timeRemaining)}</div>
              </div>
              
              <div className="relative pt-1">
                <div className="overflow-hidden h-2 text-xs flex rounded bg-cream-100">
                  <div 
                    className="bg-sage-500 rounded transition-all duration-1000 ease-out"
                    style={{ width: `${(1 - timeRemaining / (exercise.duration * 60)) * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="flex justify-center space-x-3 mt-4">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={resetTimer}
                  className="rounded-full"
                  disabled={isLoading}
                >
                  <FiRepeat />
                </Button>
                
                <Button
                  size="lg"
                  onClick={togglePlay}
                  className={`rounded-full w-12 h-12 ${isPlaying ? 'bg-cream-600 hover:bg-cream-700' : ''}`}
                  disabled={isLoading || completed}
                >
                  {isPlaying ? <FiPause /> : <FiPlay className="ml-0.5" />}
                </Button>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <h3 className="font-semibold text-sage-800 mb-2">Benefits</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-sage-500 mr-2">•</span>
                  <span className="text-sage-700">Reduces stress and anxiety</span>
                </li>
                <li className="flex items-start">
                  <span className="text-sage-500 mr-2">•</span>
                  <span className="text-sage-700">Improves focus and concentration</span>
                </li>
                <li className="flex items-start">
                  <span className="text-sage-500 mr-2">•</span>
                  <span className="text-sage-700">Promotes emotional well-being</span>
                </li>
                <li className="flex items-start">
                  <span className="text-sage-500 mr-2">•</span>
                  <span className="text-sage-700">Helps build resilience to stress</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Completion Modal */}
      {showCompletionModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/40 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-sage-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiCheck className="text-3xl text-sage-600" />
              </div>
              
              <h2 className="text-xl font-bold text-sage-800 mb-2">Exercise Completed!</h2>
              <p className="text-sage-700 mb-4">
                Great job completing your {exercise.duration}-minute {exercise.title} session. 
                How do you feel?
              </p>
              
              <div className="flex space-x-3 justify-center mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowCompletionModal(false)}
                  className="flex items-center"
                >
                  <FiX className="mr-1" />
                  Close
                </Button>
                
                <Button
                  onClick={handleComplete}
                  className="flex items-center"
                >
                  <FiCheck className="mr-1" />
                  Save Progress
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
} 