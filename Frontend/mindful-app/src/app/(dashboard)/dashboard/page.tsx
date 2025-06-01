'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiClock, FiTrendingUp, FiMessageSquare, FiActivity, FiHeart } from 'react-icons/fi';
import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { MoodChart } from '../../components/mood/MoodChart';

// Demo data for UI presentation
const demoStats = {
  totalSessions: 12,
  nextSession: '2024-07-10T15:00:00',
  completedHomework: 8,
  totalHomework: 10,
  moodTrend: 'positive',
  lastConversation: '2024-07-08T16:23:00',
  exercisesCompleted: 42,
  lastExercise: '2024-07-09T08:30:00',
};

// Demo mood data
const demoMoodData = [
  { date: '2024-07-01', mood: 3, note: 'Feeling okay, a bit tired.' },
  { date: '2024-07-02', mood: 4, note: 'Better day, meditation helped.' },
  { date: '2024-07-03', mood: 3, note: 'Work stress returning.' },
  { date: '2024-07-04', mood: 2, note: 'Difficult day, anxiety high.' },
  { date: '2024-07-05', mood: 3, note: 'Slightly improved.' },
  { date: '2024-07-06', mood: 4, note: 'Weekend relaxation helped.' },
  { date: '2024-07-07', mood: 5, note: 'Feeling great today!' },
];

// Demo exercise data
const recommendedExercises = [
  {
    id: '1',
    title: 'Mindful Breathing',
    duration: 5,
    category: 'breathing',
  },
  {
    id: '4',
    title: '4-7-8 Breathing Technique',
    duration: 3,
    category: 'breathing',
  },
  {
    id: '6',
    title: 'Anxiety Relief Visualization',
    duration: 12,
    category: 'visualization',
  },
];

// Helper function to format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { 
    weekday: 'short',
    month: 'short', 
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  }).format(date);
};

// Calculate days until next session
const getDaysUntilNextSession = (dateStr: string) => {
  const now = new Date();
  const nextSession = new Date(dateStr);
  const diffTime = Math.abs(nextSession.getTime() - now.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  return `In ${diffDays} days`;
};

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true);
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Welcome back</h1>
        <p className="text-sage-600 mt-2">Here's your mental health journey at a glance</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Session Card */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCalendar className="mr-2 text-sage-500" />
              Session Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{demoStats.totalSessions}</div>
                <p className="text-sage-600 text-sm mt-1">Sessions completed</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-sage-500 h-full rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Next Session Card */}
        <Card className="floating-delayed">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiClock className="mr-2 text-sage-500" />
              Next Session
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-sage-800 font-medium">{formatDate(demoStats.nextSession)}</div>
                <span className="text-sm px-2 py-1 bg-sage-100 text-sage-700 rounded-full inline-block mt-2">
                  {getDaysUntilNextSession(demoStats.nextSession)}
                </span>
                <div className="mt-4">
                  <Button variant="outline" size="sm">Reschedule</Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Homework Card */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiTrendingUp className="mr-2 text-sage-500" />
              Homework
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">
                  {demoStats.completedHomework}/{demoStats.totalHomework}
                </div>
                <p className="text-sage-600 text-sm mt-1">Assignments completed</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-sage-500 h-full rounded-full" 
                    style={{ width: `${(demoStats.completedHomework / demoStats.totalHomework) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Recent Activity Card */}
        <Card className="floating-delayed">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiMessageSquare className="mr-2 text-sage-500" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <p className="text-sage-700">Last conversation</p>
                <div className="text-sage-800 font-medium">{formatDate(demoStats.lastConversation)}</div>
                <div className="mt-4">
                  <Button variant="outline" size="sm">View Conversation</Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Weekly Mood Chart */}
      <div className="mt-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiActivity className="mr-2 text-sage-500" />
              Recent Mood Trends
            </CardTitle>
            <Link href="/dashboard/mood">
              <Button variant="ghost" size="sm" className="text-sage-600">
                View Full History
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-64 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div className="h-64">
                <MoodChart data={demoMoodData} />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Mindfulness Exercises */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-sage-800 flex items-center">
            <FiHeart className="mr-2 text-sage-500" />
            Recommended Exercises
          </h2>
          <Link href="/dashboard/exercises">
            <Button variant="ghost" size="sm" className="text-sage-600">
              View All Exercises
            </Button>
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {isLoading ? (
            Array(3).fill(0).map((_, i) => (
              <div key={i} className="h-32 bg-cream-100 animate-pulse rounded-lg"></div>
            ))
          ) : (
            recommendedExercises.map((exercise) => (
              <Link href={`/dashboard/exercises/${exercise.id}`} key={exercise.id} className="block">
                <Card className="h-full hover:shadow-md transition-shadow floating">
                  <CardContent className="p-4 flex flex-col h-full">
                    <h3 className="font-semibold text-sage-800">{exercise.title}</h3>
                    <div className="flex items-center mt-2 mb-auto">
                      <span className="text-xs font-medium bg-sage-100 text-sage-700 px-2 py-1 rounded-full flex items-center">
                        <FiClock className="mr-1" size={12} /> {exercise.duration} min
                      </span>
                      <span className="text-xs font-medium bg-cream-100 text-sage-700 px-2 py-1 rounded-full ml-2 capitalize">
                        {exercise.category}
                      </span>
                    </div>
                    <div className="mt-auto pt-3">
                      <Button size="sm" className="w-full flex items-center justify-center">
                        <FiHeart className="mr-1" /> Start Exercise
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))
          )}
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-sage-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/dashboard/conversations" className="w-full">
            <Button className="h-auto py-6 flex-col floating w-full" variant="outline">
              <FiMessageSquare className="text-2xl mb-2" />
              <span>Start Conversation</span>
            </Button>
          </Link>
          
          <Button className="h-auto py-6 flex-col floating-delayed" variant="outline">
            <FiCalendar className="text-2xl mb-2" />
            <span>Schedule Session</span>
          </Button>
          
          <Link href="/dashboard/mood" className="w-full">
            <Button className="h-auto py-6 flex-col floating w-full" variant="outline">
              <FiActivity className="text-2xl mb-2" />
              <span>Record Mood</span>
            </Button>
          </Link>
        </div>
      </div>
    </motion.div>
  );
} 