/**
 * Conversation service for processing messages with the LLM
 */
import {
  LLMService,
  MessageRole,
  MemoryCategory,
  Message,
  HomeworkStatus,
} from '@ai-mental-health-coach/core';
import {
  createConversationRepository,
  createMemoryRepository,
  createHomeworkRepository,
} from '@ai-mental-health-coach/db';

/**
 * Repository instances
 */
const conversationRepository = createConversationRepository();
const memoryRepository = createMemoryRepository();
const homeworkRepository = createHomeworkRepository();

/**
 * LLM service instance
 */
const llmService = new LLMService({
  apiKey: process.env.OPENAI_API_KEY || '',
  model: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
  temperature: 0.7,
  maxTokens: 1500,
});

/**
 * Response from processing a message
 */
interface ProcessMessageResponse {
  userMessage: Message;
  assistantMessage: Message;
  homework?: string;
  crisisFlag: boolean;
}

/**
 * Process a user message and get an AI response
 * 
 * @param userId - The user ID
 * @param conversationId - The conversation ID
 * @param content - The message content
 * @returns The processed message response
 */
export async function processMessage(
  userId: string,
  conversationId: string,
  content: string
): Promise<ProcessMessageResponse> {
  // Add user message to the conversation
  const userMessage = await conversationRepository.addMessageToConversation(
    conversationId,
    {
      userId,
      role: MessageRole.USER,
      content,
    }
  );

  // Get conversation history
  const messages = await conversationRepository.getConversationMessages(conversationId);

  // Get relevant memories for context
  const memories = await memoryRepository.retrieveRelevantMemories({
    userId,
    conversationId,
    limit: 5,
    minImportance: 0.6,
  });

  // Prepare conversation context for LLM
  const conversationContext = messages.map(msg => ({
    role: msg.role,
    content: msg.content,
  }));

  // Add memories as context if available
  if (memories.length > 0) {
    const memoryContext = `Previous important insights:\n${memories
      .map(
        mem => `- ${mem.content} (${mem.category})`
      )
      .join('\n')}`;
    
    conversationContext.unshift({
      role: MessageRole.SYSTEM,
      content: memoryContext,
    });
  }

  // Process the conversation with the LLM
  const llmResponse = await llmService.processConversation(conversationContext);

  // Add assistant message to the conversation
  const assistantMessage = await conversationRepository.addMessageToConversation(
    conversationId,
    {
      userId,
      role: MessageRole.ASSISTANT,
      content: llmResponse.assistant,
    }
  );

  // Create homework assignment if provided
  if (llmResponse.homework) {
    await homeworkRepository.createHomeworkAssignment({
      userId,
      conversationId,
      content: llmResponse.homework,
      status: HomeworkStatus.ASSIGNED,
    });
  }

  // Analyze the conversation for important memories
  await analyzeAndStoreMemories(userId, conversationId, content, llmResponse.assistant);

  return {
    userMessage,
    assistantMessage,
    homework: llmResponse.homework,
    crisisFlag: llmResponse.crisisFlag,
  };
}

/**
 * Simple keyword-based memory extraction (to be enhanced with LLM in future)
 * 
 * @param userId - The user ID
 * @param conversationId - The conversation ID
 * @param userMessage - The user message
 * @param assistantMessage - The assistant message
 */
async function analyzeAndStoreMemories(
  userId: string,
  conversationId: string,
  userMessage: string,
  assistantMessage: string
): Promise<void> {
  // For MVP: Simple keyword-based extraction
  // This would be enhanced with LLM-based extraction in future
  
  // Look for triggers in user messages
  if (
    userMessage.toLowerCase().includes('anxious') ||
    userMessage.toLowerCase().includes('afraid') ||
    userMessage.toLowerCase().includes('worried') ||
    userMessage.toLowerCase().includes('panic')
  ) {
    // Extract a sentence with the trigger
    const triggerSentences = userMessage.split(/[.!?]+/).filter(s => 
      s.toLowerCase().includes('anxious') ||
      s.toLowerCase().includes('afraid') ||
      s.toLowerCase().includes('worried') ||
      s.toLowerCase().includes('panic')
    );
    
    if (triggerSentences.length > 0) {
      await memoryRepository.storeImportantMemory({
        userId,
        conversationId,
        content: triggerSentences[0].trim(),
        category: MemoryCategory.TRIGGER,
        importance: 0.75,
      });
    }
  }
  
  // Look for coping strategies in assistant responses
  if (
    assistantMessage.toLowerCase().includes('try') ||
    assistantMessage.toLowerCase().includes('practice') ||
    assistantMessage.toLowerCase().includes('technique') ||
    assistantMessage.toLowerCase().includes('strategy')
  ) {
    // Extract a sentence with the coping strategy
    const copingSentences = assistantMessage.split(/[.!?]+/).filter(s => 
      s.toLowerCase().includes('try') ||
      s.toLowerCase().includes('practice') ||
      s.toLowerCase().includes('technique') ||
      s.toLowerCase().includes('strategy')
    );
    
    if (copingSentences.length > 0) {
      await memoryRepository.storeImportantMemory({
        userId,
        conversationId,
        content: copingSentences[0].trim(),
        category: MemoryCategory.COPING,
        importance: 0.8,
      });
    }
  }
  
  // Look for breakthroughs in user messages
  if (
    userMessage.toLowerCase().includes('realized') ||
    userMessage.toLowerCase().includes('understand') ||
    userMessage.toLowerCase().includes('noticed') ||
    userMessage.toLowerCase().includes('insight')
  ) {
    // Extract a sentence with the breakthrough
    const breakthroughSentences = userMessage.split(/[.!?]+/).filter(s => 
      s.toLowerCase().includes('realized') ||
      s.toLowerCase().includes('understand') ||
      s.toLowerCase().includes('noticed') ||
      s.toLowerCase().includes('insight')
    );
    
    if (breakthroughSentences.length > 0) {
      await memoryRepository.storeImportantMemory({
        userId,
        conversationId,
        content: breakthroughSentences[0].trim(),
        category: MemoryCategory.BREAKTHROUGH,
        importance: 0.9,
      });
    }
  }
  
  // Look for goals in user messages
  if (
    userMessage.toLowerCase().includes('want to') ||
    userMessage.toLowerCase().includes('goal') ||
    userMessage.toLowerCase().includes('hope to') ||
    userMessage.toLowerCase().includes('would like to')
  ) {
    // Extract a sentence with the goal
    const goalSentences = userMessage.split(/[.!?]+/).filter(s => 
      s.toLowerCase().includes('want to') ||
      s.toLowerCase().includes('goal') ||
      s.toLowerCase().includes('hope to') ||
      s.toLowerCase().includes('would like to')
    );
    
    if (goalSentences.length > 0) {
      await memoryRepository.storeImportantMemory({
        userId,
        conversationId,
        content: goalSentences[0].trim(),
        category: MemoryCategory.GOAL,
        importance: 0.85,
      });
    }
  }
} 