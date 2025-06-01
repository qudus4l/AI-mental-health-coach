'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiSmile, FiCheck } from 'react-icons/fi';
import { BsEmojiLaughing, BsEmojiSmile, BsEmojiNeutral, BsEmojiFrown, BsEmojiDizzy } from 'react-icons/bs';

import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

interface MoodEntryProps {
  onClose: () => void;
  onSave: (mood: number, note: string) => void;
}

export function MoodEntry({ onClose, onSave }: MoodEntryProps) {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const moodEmojis = [
    { value: 1, icon: BsEmojiDizzy, label: 'Very Low', color: 'bg-cream-100 text-cream-700' },
    { value: 2, icon: BsEmojiFrown, label: 'Low', color: 'bg-cream-50 text-cream-600' },
    { value: 3, icon: BsEmojiNeutral, label: 'Neutral', color: 'bg-mist-100 text-mist-600' },
    { value: 4, icon: BsEmojiSmile, label: 'Good', color: 'bg-sage-100 text-sage-600' },
    { value: 5, icon: BsEmojiLaughing, label: 'Very Good', color: 'bg-sage-200 text-sage-700' },
  ];
  
  const handleSubmit = () => {
    if (selectedMood === null) {
      setError('Please select a mood');
      return;
    }
    
    onSave(selectedMood, note);
  };
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="fixed inset-0 flex items-center justify-center z-50 p-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative w-full max-w-md">
          <button
            onClick={onClose}
            className="absolute -top-10 right-0 text-white bg-sage-500 hover:bg-sage-600 p-2 rounded-full"
          >
            <FiX />
          </button>
          
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-lg font-medium flex items-center">
                <FiSmile className="mr-2 text-sage-500" />
                How are you feeling today?
              </CardTitle>
            </CardHeader>
            
            <CardContent>
              {error && (
                <div className="p-3 mb-4 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                  {error}
                </div>
              )}
              
              <div className="grid grid-cols-5 gap-2 mb-6">
                {moodEmojis.map((mood) => {
                  const Icon = mood.icon;
                  return (
                    <button
                      key={mood.value}
                      onClick={() => {
                        setSelectedMood(mood.value);
                        setError(null);
                      }}
                      className={`p-4 rounded-lg flex flex-col items-center justify-center transition-all
                        ${selectedMood === mood.value ? `${mood.color} ring-2 ring-offset-2 ring-sage-500` : 'bg-cream-50 hover:bg-cream-100'}`}
                    >
                      <Icon className={`text-2xl ${selectedMood === mood.value ? '' : 'text-sage-500'}`} />
                      <span className={`text-xs mt-2 ${selectedMood === mood.value ? 'font-medium' : 'text-sage-600'}`}>
                        {mood.label}
                      </span>
                    </button>
                  );
                })}
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-sage-700 mb-1">
                  Notes (optional)
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg border bg-cream-50/50 border-cream-300 focus:outline-none focus:ring-2 focus:ring-sage-200 focus:border-transparent resize-none transition-all"
                  rows={4}
                  placeholder="How are you feeling? What's on your mind?"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onClose}
                >
                  Cancel
                </Button>
                
                <Button
                  type="button"
                  onClick={handleSubmit}
                  className="flex items-center"
                >
                  <FiCheck className="mr-1" />
                  Save Entry
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </AnimatePresence>
  );
} 