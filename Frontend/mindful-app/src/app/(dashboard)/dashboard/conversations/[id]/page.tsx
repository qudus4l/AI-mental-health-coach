'use client';

import { useState, useEffect, useRef, use } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { FiArrowLeft, FiSend, FiCalendar, FiUser } from 'react-icons/fi';

import { Button } from '../../../../components/ui/Button';
import { Card } from '../../../../components/ui/Card';
import { 
  getConversation, 
  getMessages, 
  sendMessage, 
  endConversation,
  Conversation,
  Message
} from '../../../../../lib/api/conversations';

// Format time from ISO string
const formatMessageTime = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default function ConversationPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  
  // Unwrap params promise
  const { id } = use(params);
  
  // Load conversation and messages
  useEffect(() => {
    const conversationId = parseInt(id);
    if (isNaN(conversationId)) {
      setError('Invalid conversation ID');
      setIsLoading(false);
      return;
    }
    
    const fetchConversation = async () => {
      try {
        setIsLoading(true);
        
        // Get conversation details
        const conversationData = await getConversation(conversationId);
        setConversation(conversationData);
        
        // Get messages
        const messagesData = await getMessages(conversationId);
        setMessages(messagesData);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching conversation:', err);
        setError('Failed to load conversation. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchConversation();
  }, [id]);
  
  // Scroll to bottom of messages when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);
  
  const handleSendMessage = async () => {
    if (!newMessage.trim() || !conversation || isSending) return;
    
    const conversationId = parseInt(id);
    if (isNaN(conversationId)) {
      setError('Invalid conversation ID');
      return;
    }
    
    try {
      setIsSending(true);
      
      // Send the message
      const messageResponse = await sendMessage(conversationId, {
        content: newMessage,
        is_from_user: true
      });
      
      // Update UI immediately with user message
      setMessages(prev => [...prev, messageResponse.message]);
      
      // Clear input
    setNewMessage('');
    
      // Show AI typing indicator
    setIsTyping(true);
    
      // If AI response is included, add it after a delay to simulate typing
      if (messageResponse.ai_message) {
    setTimeout(() => {
          setMessages(prev => [...prev, messageResponse.ai_message!]);
          setIsTyping(false);
        }, 1000);
      } else {
        // If no AI response (unusual), clear typing indicator
        setIsTyping(false);
      }
      
      // If crisis was detected, show alert
      if (messageResponse.crisis_detected) {
        alert('Crisis detected. Emergency resources have been provided.');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      setIsTyping(false);
    } finally {
      setIsSending(false);
    }
  };
  
  const handleEndConversation = async () => {
    if (!conversation) return;
    
    const conversationId = parseInt(id);
    if (isNaN(conversationId)) {
      setError('Invalid conversation ID');
      return;
    }
    
    if (window.confirm('Are you sure you want to end this conversation?')) {
      try {
        await endConversation(conversationId);
        
        // Update the local conversation state
        setConversation(prev => prev ? { ...prev, ended_at: new Date().toISOString() } : null);
        
        // Add system message
        const systemMessage: Message = {
          id: Date.now(),
          conversation_id: conversationId,
          user_id: null,
          content: 'Conversation ended',
          is_from_user: false,
          created_at: new Date().toISOString(),
          is_transcript: false
        };
        
        setMessages(prev => [...prev, systemMessage]);
      } catch (err) {
        console.error('Error ending conversation:', err);
        setError('Failed to end conversation. Please try again.');
      }
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const isConversationEnded = conversation?.ended_at !== null;
  
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
            <h1 className="text-xl font-bold text-sage-800">
              {conversation?.title || (
                conversation?.is_formal_session 
                  ? `Weekly Session #${conversation.session_number}` 
                  : 'Casual Conversation'
              )}
            </h1>
            {conversation && (
            <p className="text-sm text-sage-600 flex items-center">
              <FiCalendar className="mr-1" size={14} />
                {new Date(conversation.started_at).toLocaleDateString()}
            </p>
            )}
          </div>
        </div>
        
        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleEndConversation}
          disabled={isLoading || isConversationEnded}
        >
          {isConversationEnded ? 'Conversation Ended' : 'End Conversation'}
        </Button>
      </motion.div>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-4 mb-4 rounded-lg">
          {error}
        </div>
      )}
      
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
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-sage-600">
                Start a conversation by sending a message below.
              </div>
            ) : (
              messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.is_from_user ? 'justify-end' : 'justify-start'}`}
              >
                <div className="flex items-end max-w-[80%]">
                    {!message.is_from_user && (
                    <div className="w-8 h-8 rounded-full bg-sage-500 flex items-center justify-center mr-2 flex-shrink-0">
                      <span className="text-white font-semibold text-sm">A</span>
                    </div>
                  )}
                  
                  <div>
                    <div 
                      className={`p-3 rounded-lg ${
                          message.is_from_user 
                          ? 'bg-sage-500 text-white rounded-br-none' 
                          : 'bg-cream-100 text-sage-800 rounded-bl-none'
                      }`}
                    >
                      {message.content}
                    </div>
                    <div className="text-xs text-sage-500 mt-1">
                        {formatMessageTime(message.created_at)}
                    </div>
                  </div>
                  
                    {message.is_from_user && (
                    <div className="w-8 h-8 rounded-full bg-mist-500 flex items-center justify-center ml-2 flex-shrink-0">
                      <FiUser className="text-white" />
                    </div>
                  )}
                </div>
              </motion.div>
              ))
            )}
            
            {/* AI Typing Indicator */}
              {isTyping && (
                <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                <div className="flex items-end">
                    <div className="w-8 h-8 rounded-full bg-sage-500 flex items-center justify-center mr-2 flex-shrink-0">
                      <span className="text-white font-semibold text-sm">A</span>
                    </div>
                    
                  <div className="bg-cream-100 p-3 rounded-lg rounded-bl-none">
                      <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-sage-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-sage-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-sage-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
          </div>
        )}
      </Card>
      
      {/* Message Input */}
      <div className="mt-4">
        <div className="flex">
          <textarea
            className="flex-1 p-3 rounded-lg border border-cream-300 focus:outline-none focus:ring-2 focus:ring-sage-500 resize-none"
            placeholder="Type your message..."
            rows={1}
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || isSending || isConversationEnded}
          />
          <Button 
            className="ml-2 flex-shrink-0" 
            disabled={!newMessage.trim() || isLoading || isSending || isConversationEnded}
            onClick={handleSendMessage}
          >
            <FiSend />
          </Button>
        </div>
        {isConversationEnded && (
          <p className="text-sm text-sage-600 mt-2">
            This conversation has ended. Start a new one from the conversations page.
          </p>
        )}
      </div>
    </div>
  );
} 