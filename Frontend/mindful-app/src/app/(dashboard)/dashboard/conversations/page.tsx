'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiMessageCircle, FiPlus, FiCalendar, FiClock } from 'react-icons/fi';

import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';

// Demo data
const demoConversations = [
  {
    id: 1,
    title: 'Weekly Session #12',
    isSession: true,
    date: '2024-07-08T16:30:00',
    preview: 'Discussed anxiety management techniques and breathing exercises.',
  },
  {
    id: 2,
    title: 'Quick check-in',
    isSession: false,
    date: '2024-07-05T10:15:00',
    preview: 'Talked about progress with daily mindfulness practice.',
  },
  {
    id: 3,
    title: 'Weekly Session #11',
    isSession: true,
    date: '2024-07-01T16:30:00',
    preview: 'Worked on identifying thought patterns and cognitive distortions.',
  },
  {
    id: 4,
    title: 'Sleep difficulty',
    isSession: false,
    date: '2024-06-28T22:45:00',
    preview: 'Discussed strategies for improving sleep quality and bedtime routine.',
  },
];

// Format date function
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric',
  }).format(date);
};

export default function ConversationsPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="floating-delayed"
    >
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sage-800">Conversations</h1>
          <p className="text-sage-600 mt-2">View your previous conversations or start a new one</p>
        </div>
        
        <Button className="flex items-center gap-2">
          <FiPlus /> New Conversation
        </Button>
      </div>
      
      <div className="space-y-4">
        {isLoading ? (
          // Loading states
          Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-24 bg-cream-100 animate-pulse rounded-lg"></div>
          ))
        ) : (
          // Conversations list
          demoConversations.map((conversation) => (
            <Link href={`/dashboard/conversations/${conversation.id}`} key={conversation.id}>
              <Card className="p-0 overflow-hidden transition-all hover:shadow-md floating">
                <div className="flex">
                  <div className={`w-2 ${conversation.isSession ? 'bg-sage-500' : 'bg-mist-500'}`}></div>
                  <div className="flex-1 p-4 sm:p-5">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                          conversation.isSession ? 'bg-sage-100' : 'bg-mist-100'
                        }`}>
                          {conversation.isSession ? (
                            <FiCalendar className="text-sage-600" />
                          ) : (
                            <FiMessageCircle className="text-mist-600" />
                          )}
                        </div>
                        <div>
                          <h3 className="font-medium text-sage-800">{conversation.title}</h3>
                          <p className="text-sm text-sage-500 flex items-center">
                            <FiClock className="mr-1" size={14} />
                            {formatDate(conversation.date)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="sm:text-right">
                        {conversation.isSession && (
                          <span className="text-xs bg-sage-100 text-sage-700 px-2 py-1 rounded-full">
                            Formal Session
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <p className="mt-3 text-sage-600 line-clamp-1">{conversation.preview}</p>
                  </div>
                </div>
              </Card>
            </Link>
          ))
        )}
      </div>
    </motion.div>
  );
} 