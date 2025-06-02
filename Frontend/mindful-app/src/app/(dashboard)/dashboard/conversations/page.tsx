'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiMessageCircle, FiPlus, FiCalendar, FiClock } from 'react-icons/fi';

import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { getConversations, createConversation, Conversation } from '../../../../lib/api/conversations';

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
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Load conversations from the API
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setIsLoading(true);
        const data = await getConversations();
        setConversations(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching conversations:', err);
        setError('Failed to load conversations. Please try again.');
      } finally {
      setIsLoading(false);
      }
    };
    
    fetchConversations();
  }, []);
  
  const handleNewConversation = async () => {
    try {
      setIsLoading(true);
      const newConversation = await createConversation({
        title: 'New Conversation',
        is_formal_session: false
      });
      
      // Navigate to the new conversation
      router.push(`/dashboard/conversations/${newConversation.id}`);
    } catch (err) {
      console.error('Error creating new conversation:', err);
      setError('Failed to create new conversation. Please try again.');
      setIsLoading(false);
    }
  };
  
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
        
        <Button 
          className="flex items-center gap-2"
          onClick={handleNewConversation}
          disabled={isLoading}
        >
          <FiPlus /> New Conversation
        </Button>
      </div>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-4 mb-4 rounded-lg">
          {error}
        </div>
      )}
      
      <div className="space-y-4">
        {isLoading ? (
          // Loading states
          Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-24 bg-cream-100 animate-pulse rounded-lg"></div>
          ))
        ) : conversations.length === 0 ? (
          // Empty state
          <div className="text-center py-12">
            <div className="text-sage-600 mb-4">
              No conversations yet. Start a new one!
            </div>
            <Button 
              className="flex items-center gap-2 mx-auto"
              onClick={handleNewConversation}
            >
              <FiPlus /> Start Conversation
            </Button>
          </div>
        ) : (
          // Conversations list
          conversations.map((conversation) => (
            <Link href={`/dashboard/conversations/${conversation.id}`} key={conversation.id}>
              <Card className="p-0 overflow-hidden transition-all hover:shadow-md floating">
                <div className="flex">
                  <div className={`w-2 ${conversation.is_formal_session ? 'bg-sage-500' : 'bg-mist-500'}`}></div>
                  <div className="flex-1 p-4 sm:p-5">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                          conversation.is_formal_session ? 'bg-sage-100' : 'bg-mist-100'
                        }`}>
                          {conversation.is_formal_session ? (
                            <FiCalendar className="text-sage-600" />
                          ) : (
                            <FiMessageCircle className="text-mist-600" />
                          )}
                        </div>
                        <div>
                          <h3 className="font-medium text-sage-800">
                            {conversation.title || (
                              conversation.is_formal_session 
                                ? `Weekly Session #${conversation.session_number}` 
                                : 'Casual Conversation'
                            )}
                          </h3>
                          <p className="text-sm text-sage-500 flex items-center">
                            <FiClock className="mr-1" size={14} />
                            {formatDate(conversation.started_at)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="sm:text-right">
                        {conversation.is_formal_session && (
                          <span className="text-xs bg-sage-100 text-sage-700 px-2 py-1 rounded-full">
                            Formal Session
                          </span>
                        )}
                      </div>
                    </div>
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