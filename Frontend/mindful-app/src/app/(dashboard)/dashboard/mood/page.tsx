'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiPlusCircle, FiTrendingUp, FiHeart } from 'react-icons/fi';

import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { MoodChart } from '../../../components/mood/MoodChart';
import { MoodEntry } from '../../../components/mood/MoodEntry';

// Demo mood data
const demoMoodData = [
  { date: '2024-07-01', mood: 3, note: 'Feeling okay, a bit tired.' },
  { date: '2024-07-02', mood: 4, note: 'Better day, meditation helped.' },
  { date: '2024-07-03', mood: 3, note: 'Work stress returning.' },
  { date: '2024-07-04', mood: 2, note: 'Difficult day, anxiety high.' },
  { date: '2024-07-05', mood: 3, note: 'Slightly improved.' },
  { date: '2024-07-06', mood: 4, note: 'Weekend relaxation helped.' },
  { date: '2024-07-07', mood: 5, note: 'Feeling great today!' },
  { date: '2024-07-08', mood: 4, note: 'Good start to the week.' },
  { date: '2024-07-09', mood: 3, note: 'Neutral day.' },
  { date: '2024-07-10', mood: 4, note: 'Session was helpful today.' },
];

export default function MoodPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [moodData, setMoodData] = useState(demoMoodData);
  const [showMoodEntry, setShowMoodEntry] = useState(false);
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Handle adding a new mood entry
  const handleAddMood = (mood: number, note: string) => {
    const today = new Date().toISOString().split('T')[0];
    const newEntry = { date: today, mood, note };
    
    setMoodData(prev => [newEntry, ...prev]);
    setShowMoodEntry(false);
  };
  
  // Calculate average mood
  const averageMood = moodData.length 
    ? (moodData.reduce((sum, entry) => sum + entry.mood, 0) / moodData.length).toFixed(1)
    : 'N/A';
  
  // Get trend (up, down, or stable)
  const getMoodTrend = () => {
    if (moodData.length < 3) return 'stable';
    
    const recent = moodData.slice(0, 3).map(entry => entry.mood);
    const avg = recent.reduce((sum, mood) => sum + mood, 0) / recent.length;
    const older = moodData.slice(3, 6).map(entry => entry.mood);
    const olderAvg = older.reduce((sum, mood) => sum + mood, 0) / older.length;
    
    if (avg > olderAvg + 0.5) return 'up';
    if (avg < olderAvg - 0.5) return 'down';
    return 'stable';
  };
  
  const moodTrend = getMoodTrend();
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Mood Tracking</h1>
          <p className="text-sage-600 mt-2">Monitor your emotional well-being over time</p>
        </div>
        
        <Button 
          onClick={() => setShowMoodEntry(true)}
          className="flex items-center gap-2"
        >
          <FiPlusCircle /> Record Mood
        </Button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Average Mood */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiHeart className="mr-2 text-sage-500" />
              Average Mood
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{averageMood}</div>
                <p className="text-sage-600 text-sm mt-1">out of 5</p>
                <div className="mt-4 flex">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <div 
                      key={value}
                      className={`w-8 h-8 rounded-full flex items-center justify-center mr-1
                        ${parseFloat(averageMood) >= value 
                          ? 'bg-sage-500 text-white' 
                          : 'bg-cream-200 text-sage-500'}`}
                    >
                      {value}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Recent Trend */}
        <Card className="floating-delayed">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiTrendingUp className="mr-2 text-sage-500" />
              Recent Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="flex items-center">
                  {moodTrend === 'up' && (
                    <>
                      <div className="w-10 h-10 rounded-full bg-sage-100 flex items-center justify-center">
                        <FiTrendingUp className="text-sage-600 text-xl" />
                      </div>
                      <div className="ml-3">
                        <div className="font-medium text-sage-800">Improving</div>
                        <p className="text-sm text-sage-600">Your mood is trending upward</p>
                      </div>
                    </>
                  )}
                  
                  {moodTrend === 'down' && (
                    <>
                      <div className="w-10 h-10 rounded-full bg-cream-100 flex items-center justify-center">
                        <FiTrendingUp className="text-cream-600 text-xl transform rotate-180" />
                      </div>
                      <div className="ml-3">
                        <div className="font-medium text-sage-800">Declining</div>
                        <p className="text-sm text-sage-600">Your mood is trending downward</p>
                      </div>
                    </>
                  )}
                  
                  {moodTrend === 'stable' && (
                    <>
                      <div className="w-10 h-10 rounded-full bg-mist-100 flex items-center justify-center">
                        <div className="w-4 h-0.5 bg-mist-500 rounded-full"></div>
                      </div>
                      <div className="ml-3">
                        <div className="font-medium text-sage-800">Stable</div>
                        <p className="text-sm text-sage-600">Your mood is consistent</p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Entries Count */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCalendar className="mr-2 text-sage-500" />
              Tracking History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{moodData.length}</div>
                <p className="text-sage-600 text-sm mt-1">days tracked</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-sage-500 h-full rounded-full" style={{ width: `${Math.min(moodData.length * 3.3, 100)}%` }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Mood Visualization */}
      <Card className="floating-delayed">
        <CardHeader>
          <CardTitle className="text-lg font-medium flex items-center">
            <FiTrendingUp className="mr-2 text-sage-500" />
            Mood History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-64 bg-cream-100 animate-pulse rounded-lg"></div>
          ) : (
            <div className="h-64">
              <MoodChart data={moodData} />
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Recent Entries */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-sage-800 mb-4">Recent Entries</h2>
        
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {moodData.slice(0, 5).map((entry, index) => (
              <Card key={index} className="overflow-hidden">
                <div className="flex">
                  <div 
                    className="w-2" 
                    style={{ 
                      backgroundColor: `rgba(${128 - entry.mood * 10}, ${143 + entry.mood * 10}, ${118}, ${0.7 + entry.mood * 0.06})`
                    }}
                  ></div>
                  <div className="flex-1 p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="text-sm text-sage-500">
                          {new Date(entry.date).toLocaleDateString('en-US', { 
                            weekday: 'short', 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </span>
                        <p className="text-sage-700 mt-1">{entry.note}</p>
                      </div>
                      
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center
                        ${entry.mood >= 4 
                          ? 'bg-sage-100 text-sage-600' 
                          : entry.mood <= 2 
                            ? 'bg-cream-100 text-cream-700' 
                            : 'bg-mist-100 text-mist-600'}`}
                      >
                        {entry.mood}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
      
      {/* Mood Entry Modal */}
      {showMoodEntry && (
        <MoodEntry onClose={() => setShowMoodEntry(false)} onSave={handleAddMood} />
      )}
    </motion.div>
  );
} 