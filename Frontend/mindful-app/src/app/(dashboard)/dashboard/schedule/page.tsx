'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiClock, FiVideo, FiPhone, FiMapPin, FiPlus, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import Link from 'next/link';

import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { Button } from '../../../../components/ui/Button';

// Demo sessions data
const demoSessions = [
  {
    id: '1',
    date: '2024-07-15T15:00:00',
    type: 'video',
    duration: 50,
    therapist: 'Dr. Sarah Johnson',
    status: 'upcoming',
    notes: 'Follow-up on homework exercises and discuss progress with anxiety management techniques.'
  },
  {
    id: '2',
    date: '2024-07-22T15:00:00',
    type: 'video',
    duration: 50,
    therapist: 'Dr. Sarah Johnson',
    status: 'upcoming',
    notes: 'Weekly check-in, mindfulness practice review.'
  },
  {
    id: '3',
    date: '2024-07-29T15:00:00',
    type: 'video',
    duration: 50,
    therapist: 'Dr. Sarah Johnson',
    status: 'upcoming',
    notes: ''
  },
  {
    id: '4',
    date: '2024-07-08T15:00:00',
    type: 'video',
    duration: 50,
    therapist: 'Dr. Sarah Johnson',
    status: 'completed',
    notes: 'Introduced new breathing techniques. Discussed work stress triggers. Assigned daily gratitude journal.'
  },
  {
    id: '5',
    date: '2024-07-01T15:00:00',
    type: 'video',
    duration: 50,
    therapist: 'Dr. Sarah Johnson',
    status: 'completed',
    notes: 'Initial assessment. Created treatment plan focusing on anxiety and stress management.'
  }
];

// Helper function to format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { 
    weekday: 'long',
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  }).format(date);
};

// Helper function to format time
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { 
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(date);
};

// Helper function to get days until session
const getDaysUntil = (dateStr: string) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const sessionDate = new Date(dateStr);
  sessionDate.setHours(0, 0, 0, 0);
  
  const diffTime = sessionDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return 'Past';
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  if (diffDays < 7) return `In ${diffDays} days`;
  if (diffDays < 14) return 'Next week';
  return `In ${diffDays} days`;
};

// Helper function to get session icon
const getSessionIcon = (type: string) => {
  switch (type) {
    case 'video':
      return <FiVideo />;
    case 'phone':
      return <FiPhone />;
    case 'in-person':
      return <FiMapPin />;
    default:
      return <FiCalendar />;
  }
};

export default function SchedulePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [sessions, setSessions] = useState(demoSessions);
  const [activeFilter, setActiveFilter] = useState('upcoming');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Filter sessions
  const getFilteredSessions = () => {
    if (activeFilter === 'all') return sessions;
    return sessions.filter(session => session.status === activeFilter);
  };
  
  const filteredSessions = getFilteredSessions();
  const nextSession = sessions.find(session => session.status === 'upcoming');
  
  // Calendar navigation
  const navigateMonth = (direction: number) => {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(currentMonth.getMonth() + direction);
    setCurrentMonth(newMonth);
  };
  
  // Generate calendar days
  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    // Get first day of month and total days in month
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const daysInMonth = lastDayOfMonth.getDate();
    
    // Get day of week for first day (0 = Sunday)
    const firstDayWeekday = firstDayOfMonth.getDay();
    
    // Create array for calendar days
    const calendarDays = [];
    
    // Add empty cells for days before first day of month
    for (let i = 0; i < firstDayWeekday; i++) {
      calendarDays.push({ day: '', isCurrentMonth: false });
    }
    
    // Add cells for days in month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const hasSession = sessions.some(session => {
        const sessionDate = new Date(session.date);
        return (
          sessionDate.getDate() === date.getDate() && 
          sessionDate.getMonth() === date.getMonth() && 
          sessionDate.getFullYear() === date.getFullYear()
        );
      });
      
      calendarDays.push({ 
        day, 
        isCurrentMonth: true,
        hasSession,
        isToday: 
          date.getDate() === new Date().getDate() && 
          date.getMonth() === new Date().getMonth() && 
          date.getFullYear() === new Date().getFullYear()
      });
    }
    
    return calendarDays;
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Session Schedule</h1>
          <p className="text-sage-600 mt-2">Manage your therapy appointments</p>
        </div>
        
        <Button className="flex items-center gap-2">
          <FiPlus /> Schedule Session
        </Button>
      </div>
      
      {/* Next Session Card */}
      <Card className="mb-8 overflow-hidden floating">
        <div className="flex flex-col md:flex-row">
          <div className="md:w-2/3 p-6">
            <h2 className="text-xl font-semibold text-sage-800">Next Session</h2>
            
            {isLoading ? (
              <div className="space-y-4 mt-4">
                <div className="h-8 bg-cream-100 animate-pulse rounded-lg w-2/3"></div>
                <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
                <div className="h-10 bg-cream-100 animate-pulse rounded-lg w-1/3"></div>
              </div>
            ) : nextSession ? (
              <>
                <div className="mt-4">
                  <h3 className="text-lg font-semibold text-sage-700">{formatDate(nextSession.date)}</h3>
                  <div className="flex items-center mt-1">
                    <FiClock className="text-sage-500 mr-1" />
                    <span className="text-sage-600">{formatTime(nextSession.date)} · {nextSession.duration} minutes</span>
                  </div>
                  <div className="flex items-center mt-1">
                    {getSessionIcon(nextSession.type)}
                    <span className="ml-1 text-sage-600 capitalize">{nextSession.type} session with {nextSession.therapist}</span>
                  </div>
                  
                  {nextSession.notes && (
                    <p className="mt-4 text-sage-600 text-sm">{nextSession.notes}</p>
                  )}
                </div>
                
                <div className="mt-6 flex space-x-3">
                  <Button>Join Session</Button>
                  <Button variant="outline">Reschedule</Button>
                </div>
              </>
            ) : (
              <div className="mt-4 text-sage-600">
                No upcoming sessions scheduled. Use the "Schedule Session" button to book your next appointment.
              </div>
            )}
          </div>
          
          <div className="md:w-1/3 bg-sage-50 flex items-center justify-center p-6">
            {isLoading ? (
              <div className="w-full h-full min-h-[200px] bg-cream-100 animate-pulse rounded-lg"></div>
            ) : nextSession ? (
              <div className="text-center">
                <div className="text-5xl font-light text-sage-700 mb-2">
                  {getDaysUntil(nextSession.date) === 'Today' ? (
                    'Today'
                  ) : getDaysUntil(nextSession.date) === 'Tomorrow' ? (
                    'Tomorrow'
                  ) : (
                    getDaysUntil(nextSession.date).includes('days') ? (
                      <>
                        <span className="text-7xl">{getDaysUntil(nextSession.date).split(' ')[1]}</span>
                        <span className="text-2xl ml-2">days</span>
                      </>
                    ) : (
                      getDaysUntil(nextSession.date)
                    )
                  )}
                </div>
                <p className="text-sage-600">until your next session</p>
              </div>
            ) : (
              <div className="text-center text-sage-600">
                <FiCalendar className="text-5xl mx-auto mb-4 text-sage-400" />
                No upcoming sessions
              </div>
            )}
          </div>
        </div>
      </Card>
      
      {/* Calendar View */}
      <Card className="mb-8 floating-delayed">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCalendar className="mr-2 text-sage-500" />
              Calendar
            </CardTitle>
            
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => navigateMonth(-1)}
                className="p-1 rounded-full hover:bg-cream-100 text-sage-700"
              >
                <FiChevronLeft />
              </button>
              
              <span className="text-sage-700 font-medium">
                {currentMonth.toLocaleString('default', { month: 'long', year: 'numeric' })}
              </span>
              
              <button 
                onClick={() => navigateMonth(1)}
                className="p-1 rounded-full hover:bg-cream-100 text-sage-700"
              >
                <FiChevronRight />
              </button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-4">
          {isLoading ? (
            <div className="h-64 bg-cream-100 animate-pulse rounded-lg"></div>
          ) : (
            <div className="grid grid-cols-7 gap-1">
              {/* Day labels */}
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center text-sage-600 text-xs font-medium py-2">
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {generateCalendarDays().map((day, i) => (
                <div 
                  key={i} 
                  className={`
                    h-12 text-center p-1 relative
                    ${day.isCurrentMonth ? 'text-sage-800' : 'text-sage-400'}
                    ${day.isToday ? 'font-bold' : ''}
                  `}
                >
                  <div className={`
                    h-full w-full flex items-center justify-center rounded-full relative
                    ${day.isToday ? 'bg-sage-100' : ''}
                    ${day.hasSession && !day.isToday ? 'after:absolute after:w-1 after:h-1 after:bg-sage-500 after:rounded-full after:bottom-1' : ''}
                  `}>
                    {day.day}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Filter tabs */}
      <div className="border-b border-cream-200 mb-6">
        <div className="flex space-x-6">
          {['upcoming', 'completed', 'all'].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-4 py-2 border-b-2 font-medium transition-colors capitalize
                ${activeFilter === filter 
                  ? 'border-sage-500 text-sage-800' 
                  : 'border-transparent text-sage-600 hover:text-sage-800 hover:border-sage-200'}`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>
      
      {/* Sessions List */}
      <div className="space-y-4">
        {isLoading ? (
          Array(3).fill(0).map((_, i) => (
            <div key={i} className="h-24 bg-cream-100 animate-pulse rounded-lg"></div>
          ))
        ) : filteredSessions.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-sage-600">No {activeFilter} sessions found</p>
            </CardContent>
          </Card>
        ) : (
          filteredSessions.map((session) => (
            <Card key={session.id} className="overflow-hidden floating">
              <div className="flex flex-col md:flex-row">
                {/* Status indicator */}
                <div 
                  className="md:w-2 w-full h-2 md:h-auto"
                  style={{ 
                    backgroundColor: session.status === 'completed' 
                      ? 'rgba(128, 143, 118, 0.5)' 
                      : getDaysUntil(session.date) === 'Today'
                        ? 'rgba(220, 38, 38, 0.5)'
                        : 'rgba(212, 192, 158, 0.5)'
                  }}
                ></div>
                
                <div className="flex-1 p-4">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                      <div className="font-semibold text-sage-800">
                        {formatDate(session.date)} · {formatTime(session.date)}
                      </div>
                      <div className="flex items-center mt-1 text-sage-600 text-sm">
                        {getSessionIcon(session.type)}
                        <span className="ml-1 capitalize">{session.type} session with {session.therapist}</span>
                      </div>
                      
                      {session.notes && (
                        <p className="text-sage-600 text-sm mt-2">{session.notes}</p>
                      )}
                    </div>
                    
                    <div className="mt-3 md:mt-0 flex items-center">
                      {session.status === 'upcoming' && (
                        <span className={`text-xs font-medium bg-cream-100 text-sage-700 px-2 py-1 rounded-full`}>
                          {getDaysUntil(session.date)}
                        </span>
                      )}
                      
                      {session.status === 'upcoming' ? (
                        <div className="flex space-x-2 ml-4">
                          <Button size="sm">Join</Button>
                          <Button size="sm" variant="outline">Details</Button>
                        </div>
                      ) : (
                        <Button size="sm" variant="outline" className="ml-4">
                          Notes
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </motion.div>
  );
} 