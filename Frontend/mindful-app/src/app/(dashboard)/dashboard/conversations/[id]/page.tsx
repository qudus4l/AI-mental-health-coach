'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { FiArrowLeft, FiSend, FiCalendar, FiInfo, FiUser } from 'react-icons/fi';

import { Button } from '../../../../components/ui/Button';
import { Card } from '../../../../components/ui/Card';

// Demo conversation data
const demoConversation = {
  id: 1,
  title: 'Weekly Session #12',
  date: '2024-07-08T16:30:00',
  isSession: true,
  messages: [
    {
      id: 1,
      content: "Hello! How are you feeling today?",
      isUser: false,
      timestamp: "2024-07-08T16:30:00",
    },
    {
      id: 2,
      content: "I've been feeling a bit anxious lately, especially at work.",
      isUser: true,
      timestamp: "2024-07-08T16:31:12",
    },
    {
      id: 3,
      content: "I'm sorry to hear you've been feeling anxious. That can be challenging. Can you tell me more about what's been happening at work that's triggering this anxiety?",
      isUser: false,
      timestamp: "2024-07-08T16:31:45",
    },
    {
      id: 4,
      content: "I have a big presentation coming up next week, and I'm worried I'll mess it up. I've been having trouble sleeping thinking about it.",
      isUser: true,
      timestamp: "2024-07-08T16:33:02",
    },
    {
      id: 5,
      content: "That's understandable. Public speaking and important presentations can definitely trigger anxiety for many people. Let's work through this together. First, it might help to identify what specific aspects of the presentation are causing you the most worry. Is it the preparation, the delivery, or perhaps the response from your audience?",
      isUser: false,
      timestamp: "2024-07-08T16:34:10",
    },
  ]
};

// Format time from ISO string
const formatMessageTime = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default function ConversationPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [conversation, setConversation] = useState(demoConversation);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Scroll to bottom of messages when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [conversation.messages, isTyping]);
  
  const handleSendMessage = () => {
    if (!newMessage.trim()) return;
    
    // Add user message
    const userMessage = {
      id: conversation.messages.length + 1,
      content: newMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };
    
    setConversation(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));
    
    setNewMessage('');
    
    // Simulate AI typing
    setIsTyping(true);
    
    // Simulate AI response after delay
    setTimeout(() => {
      const aiMessage = {
        id: conversation.messages.length + 2,
        content: "Thank you for sharing that. I understand how stressful preparing for presentations can be. Let's work on some breathing exercises that might help reduce your anxiety. Would you like to try one now?",
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      
      setConversation(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
      }));
      
      setIsTyping(false);
    }, 2000);
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="h-[calc(100vh-2rem)] md:h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-4"
      >
        <div className="flex items-center">
          <Button 
            variant="ghost" 
            size="sm" 
            className="mr-2"
            onClick={() => router.push('/dashboard/conversations')}
          >
            <FiArrowLeft />
          </Button>
          
          <div>
            <h1 className="text-xl font-bold text-sage-800">{conversation.title}</h1>
            <p className="text-sm text-sage-600 flex items-center">
              <FiCalendar className="mr-1" size={14} />
              {new Date(conversation.date).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        <Button variant="ghost" size="sm">
          <FiInfo />
        </Button>
      </motion.div>
      
      {/* Messages Container */}
      <Card className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-sage-200 border-t-sage-500 rounded-full"></div>
          </div>
        ) : (
          <div 
            ref={messageContainerRef}
            className="h-full overflow-y-auto p-4 space-y-4"
          >
            {conversation.messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div className="flex items-end max-w-[80%]">
                  {!message.isUser && (
                    <div className="w-8 h-8 rounded-full bg-sage-500 flex items-center justify-center mr-2 flex-shrink-0">
                      <span className="text-white font-semibold text-sm">A</span>
                    </div>
                  )}
                  
                  <div>
                    <div 
                      className={`p-3 rounded-lg ${
                        message.isUser 
                          ? 'bg-sage-500 text-white rounded-br-none' 
                          : 'bg-cream-100 text-sage-800 rounded-bl-none'
                      }`}
                    >
                      {message.content}
                    </div>
                    <div className="text-xs text-sage-500 mt-1">
                      {formatMessageTime(message.timestamp)}
                    </div>
                  </div>
                  
                  {message.isUser && (
                    <div className="w-8 h-8 rounded-full bg-mist-500 flex items-center justify-center ml-2 flex-shrink-0">
                      <FiUser className="text-white" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            
            {/* AI typing indicator */}
            <AnimatePresence>
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex items-end max-w-[80%]">
                    <div className="w-8 h-8 rounded-full bg-sage-500 flex items-center justify-center mr-2 flex-shrink-0">
                      <span className="text-white font-semibold text-sm">A</span>
                    </div>
                    
                    <div className="p-3 rounded-lg bg-cream-100 text-sage-800 rounded-bl-none">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </Card>
      
      {/* Message Input */}
      <Card className="mt-4 p-2">
        <div className="flex items-end">
          <textarea
            className="flex-1 resize-none border-0 bg-transparent p-2 focus:ring-0 focus:outline-none text-sage-800 placeholder:text-sage-400"
            placeholder="Type your message..."
            rows={1}
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || isTyping}
          />
          <Button 
            size="sm" 
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || isLoading || isTyping}
            className="rounded-full p-2"
          >
            <FiSend />
          </Button>
        </div>
      </Card>
    </div>
  );
} 