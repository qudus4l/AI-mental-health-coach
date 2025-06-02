'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiClock, FiTrendingUp, FiMessageSquare, FiActivity, FiHeart } from 'react-icons/fi';
import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { MoodChart } from '../../components/mood/MoodChart';

import { 
  getDashboardStats, 
  getMoodHistory, 
  getRecommendedExercises,
  DashboardStats,
  MoodData,
  RecommendedExercise
} from '../../../lib/api/dashboard';

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
const getDaysUntilNextSession = (dateStr: string | null) => {
  if (!dateStr) return 'No sessions scheduled';
  
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
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [moodData, setMoodData] = useState<MoodData[]>([]);
  const [exercises, setExercises] = useState<RecommendedExercise[]>([]);
  
  // Load dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch stats, mood data, and exercises in parallel
        const [statsData, moodHistoryData, exercisesData] = await Promise.all([
          getDashboardStats(),
          getMoodHistory('week'),
          getRecommendedExercises(3)
        ]);
        
        setStats(statsData);
        setMoodData(moodHistoryData);
        setExercises(exercisesData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
      setIsLoading(false);
      }
    };
    
    fetchDashboardData();
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
      
      {error && (
        <div className="bg-red-100 text-red-700 p-4 mb-4 rounded-lg">
          {error}
        </div>
      )}
      
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
                <div className="text-3xl font-bold text-sage-800">{stats?.total_sessions || 0}</div>
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
                {stats?.next_session ? (
                  <>
                    <div className="text-sage-800 font-medium">{formatDate(stats.next_session)}</div>
                <span className="text-sm px-2 py-1 bg-sage-100 text-sage-700 rounded-full inline-block mt-2">
                      {getDaysUntilNextSession(stats.next_session)}
                </span>
                <div className="mt-4">
                  <Button variant="outline" size="sm">Reschedule</Button>
                </div>
                  </>
                ) : (
                  <>
                    <div className="text-sage-800 font-medium">No sessions scheduled</div>
                    <div className="mt-4">
                      <Button variant="outline" size="sm">Schedule Session</Button>
                    </div>
                  </>
                )}
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
                  {stats ? `${stats.completed_homework}/${stats.total_homework}` : '0/0'}
                </div>
                <p className="text-sage-600 text-sm mt-1">Assignments completed</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-sage-500 h-full rounded-full" 
                    style={{ 
                      width: stats ? 
                        `${stats.total_homework > 0 ? (stats.completed_homework / stats.total_homework) * 100 : 0}%` : 
                        '0%' 
                    }}
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
                {stats?.last_conversation ? (
                  <>
                    <div className="text-sage-800 font-medium">{formatDate(stats.last_conversation)}</div>
                    <div className="mt-4">
                      <Link href="/dashboard/conversations">
                        <Button variant="outline" size="sm">View Conversations</Button>
                      </Link>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-sage-800 font-medium">No recent conversations</div>
                <div className="mt-4">
                      <Link href="/dashboard/conversations">
                        <Button variant="outline" size="sm">Start a Conversation</Button>
                      </Link>
                </div>
                  </>
                )}
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
                {moodData.length > 0 ? (
                  <MoodChart data={moodData} />
                ) : (
                  <div className="flex items-center justify-center h-full text-sage-600">
                    No mood data available yet. Start tracking your mood to see trends.
                  </div>
                )}
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
          ) : exercises.length > 0 ? (
            exercises.map((exercise) => (
              <Card key={exercise.id} className="h-full floating">
                <CardContent className="p-5">
                  <div className="flex flex-col h-full">
                    <h3 className="font-medium text-sage-800">{exercise.title}</h3>
                    <p className="text-sm text-sage-600 mt-1 flex-1">{exercise.description}</p>
                    <div className="flex justify-between items-center mt-4">
                      <span className="text-xs px-2 py-1 bg-cream-100 text-sage-700 rounded-full">
                        {exercise.duration} min
                      </span>
                      <Button variant="outline" size="sm">Start</Button>
                    </div>
                    </div>
                  </CardContent>
                </Card>
            ))
          ) : (
            <div className="col-span-3 text-center py-10 text-sage-600">
              No exercises available yet. Check back soon!
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
} 