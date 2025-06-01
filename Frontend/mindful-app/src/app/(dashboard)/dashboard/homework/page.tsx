'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCheck, FiClock, FiFileText, FiCalendar, FiChevronRight, FiPlus } from 'react-icons/fi';
import Link from 'next/link';

import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { Button } from '../../../../components/ui/Button';

// Demo homework data
const demoHomework = [
  {
    id: '1',
    title: 'Daily Gratitude Journal',
    description: 'Write down three things you are grateful for each day.',
    dueDate: '2024-07-15',
    assignedDate: '2024-07-08',
    status: 'in-progress',
    progress: 5,
    totalDays: 7,
    type: 'journal'
  },
  {
    id: '2',
    title: 'Mindful Breathing Practice',
    description: 'Practice the 4-7-8 breathing technique twice daily for 5 minutes.',
    dueDate: '2024-07-14',
    assignedDate: '2024-07-07',
    status: 'in-progress',
    progress: 4,
    totalDays: 7,
    type: 'exercise'
  },
  {
    id: '3',
    title: 'Thought Record',
    description: 'Keep track of negative thoughts and practice reframing them into more balanced perspectives.',
    dueDate: '2024-07-12',
    assignedDate: '2024-07-05',
    status: 'completed',
    progress: 7,
    totalDays: 7,
    type: 'worksheet'
  },
  {
    id: '4',
    title: 'Values Exploration',
    description: 'Complete the values worksheet to identify what matters most to you.',
    dueDate: '2024-07-10',
    assignedDate: '2024-07-03',
    status: 'completed',
    progress: 1,
    totalDays: 1,
    type: 'worksheet'
  },
  {
    id: '5',
    title: 'Pleasant Activity Scheduling',
    description: 'Plan and engage in at least one enjoyable activity each day.',
    dueDate: '2024-07-17',
    assignedDate: '2024-07-10',
    status: 'not-started',
    progress: 0,
    totalDays: 7,
    type: 'activity'
  }
];

// Helper function to format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  }).format(date);
};

// Helper function to calculate days remaining
const getDaysRemaining = (dueDateStr: string) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const dueDate = new Date(dueDateStr);
  dueDate.setHours(0, 0, 0, 0);
  
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return 'Overdue';
  if (diffDays === 0) return 'Due Today';
  if (diffDays === 1) return '1 day left';
  return `${diffDays} days left`;
};

// Helper function to get status color
const getStatusColor = (status: string, daysRemaining: string) => {
  if (status === 'completed') return 'bg-sage-100 text-sage-700';
  if (daysRemaining === 'Overdue') return 'bg-red-100 text-red-700';
  if (daysRemaining === 'Due Today') return 'bg-amber-100 text-amber-700';
  return 'bg-cream-100 text-sage-700';
};

export default function HomeworkPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [homework, setHomework] = useState(demoHomework);
  const [activeFilter, setActiveFilter] = useState('all');
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Filter homework
  const getFilteredHomework = () => {
    if (activeFilter === 'all') return homework;
    if (activeFilter === 'active') return homework.filter(item => item.status !== 'completed');
    if (activeFilter === 'completed') return homework.filter(item => item.status === 'completed');
    return homework;
  };
  
  const filteredHomework = getFilteredHomework();
  
  // Calculate stats
  const totalAssignments = homework.length;
  const completedAssignments = homework.filter(item => item.status === 'completed').length;
  const completionRate = Math.round((completedAssignments / totalAssignments) * 100) || 0;
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Homework</h1>
          <p className="text-sage-600 mt-2">Track your therapeutic assignments and progress</p>
        </div>
        
        <Button className="flex items-center gap-2">
          <FiPlus /> New Entry
        </Button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Total Assignments */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiFileText className="mr-2 text-sage-500" />
              Total Assignments
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{totalAssignments}</div>
                <p className="text-sage-600 text-sm mt-1">homework assignments</p>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Completion Rate */}
        <Card className="floating-delayed">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCheck className="mr-2 text-sage-500" />
              Completion Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                <div className="text-3xl font-bold text-sage-800">{completionRate}%</div>
                <p className="text-sage-600 text-sm mt-1">{completedAssignments} of {totalAssignments} completed</p>
                <div className="mt-4 bg-cream-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-sage-500 h-full rounded-full" style={{ width: `${completionRate}%` }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Current Due Dates */}
        <Card className="floating">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FiCalendar className="mr-2 text-sage-500" />
              Upcoming Due Dates
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-20 bg-cream-100 animate-pulse rounded-lg"></div>
            ) : (
              <div>
                {filteredHomework
                  .filter(item => item.status !== 'completed')
                  .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime())
                  .slice(0, 2)
                  .map((item, i) => (
                    <div key={i} className="flex justify-between items-center mb-2 text-sm">
                      <span className="text-sage-700 truncate pr-2">{item.title}</span>
                      <span className="text-sage-500 whitespace-nowrap">{formatDate(item.dueDate)}</span>
                    </div>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Filter tabs */}
      <div className="border-b border-cream-200 mb-6">
        <div className="flex space-x-6">
          {['all', 'active', 'completed'].map((filter) => (
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
      
      {/* Homework List */}
      <div className="space-y-4">
        {isLoading ? (
          Array(3).fill(0).map((_, i) => (
            <div key={i} className="h-24 bg-cream-100 animate-pulse rounded-lg"></div>
          ))
        ) : filteredHomework.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-sage-600">No homework assignments found</p>
            </CardContent>
          </Card>
        ) : (
          filteredHomework.map((item) => {
            const daysRemaining = getDaysRemaining(item.dueDate);
            const statusColor = getStatusColor(item.status, daysRemaining);
            
            return (
              <Card key={item.id} className="overflow-hidden floating">
                <div className="flex flex-col md:flex-row">
                  {/* Status indicator */}
                  <div 
                    className="md:w-2 w-full h-2 md:h-auto"
                    style={{ 
                      backgroundColor: item.status === 'completed' 
                        ? 'rgba(128, 143, 118, 0.5)' 
                        : daysRemaining === 'Overdue'
                          ? 'rgba(220, 38, 38, 0.5)'
                          : daysRemaining === 'Due Today'
                            ? 'rgba(217, 119, 6, 0.5)'
                            : 'rgba(212, 192, 158, 0.5)'
                    }}
                  ></div>
                  
                  <div className="flex-1 p-4">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                      <div>
                        <h3 className="font-semibold text-sage-800">{item.title}</h3>
                        <p className="text-sage-600 text-sm mt-1">{item.description}</p>
                      </div>
                      
                      <div className="flex items-center mt-3 md:mt-0">
                        {item.status !== 'completed' && (
                          <span className={`text-xs font-medium px-2 py-1 rounded-full mr-3 ${statusColor}`}>
                            {daysRemaining}
                          </span>
                        )}
                        
                        <span className="text-xs bg-mist-100 text-mist-700 px-2 py-1 rounded-full capitalize">
                          {item.type}
                        </span>
                        
                        <Link href={`/dashboard/homework/${item.id}`} className="ml-4 p-1 text-sage-600 hover:text-sage-800">
                          <FiChevronRight />
                        </Link>
                      </div>
                    </div>
                    
                    {item.totalDays > 1 && (
                      <div className="mt-3">
                        <div className="flex justify-between text-xs text-sage-600 mb-1">
                          <span>Progress</span>
                          <span>{item.progress} of {item.totalDays} days</span>
                        </div>
                        <div className="bg-cream-100 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className="bg-sage-500 h-full rounded-full" 
                            style={{ width: `${(item.progress / item.totalDays) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            );
          })
        )}
      </div>
    </motion.div>
  );
} 