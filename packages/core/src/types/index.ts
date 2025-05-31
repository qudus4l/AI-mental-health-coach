/**
 * Core type definitions for the AI Mental Health Coach application
 */

/**
 * Memory category types for important insights
 */
export enum MemoryCategory {
  TRIGGER = "trigger",
  COPING = "coping",
  BREAKTHROUGH = "breakthrough",
  GOAL = "goal",
}

/**
 * Important memory structure
 */
export interface ImportantMemory {
  id: string;
  userId: string;
  conversationId: string;
  content: string;
  category: MemoryCategory;
  importance: number;
  createdAt: Date;
}

/**
 * Message role types for conversation
 */
export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
}

/**
 * Message structure for conversations
 */
export interface Message {
  id: string;
  conversationId: string;
  userId: string;
  role: MessageRole;
  content: string;
  createdAt: Date;
}

/**
 * Conversation structure
 */
export interface Conversation {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
}

/**
 * Homework completion status
 */
export enum HomeworkStatus {
  ASSIGNED = "assigned",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  SKIPPED = "skipped",
}

/**
 * Homework assignment structure
 */
export interface HomeworkAssignment {
  id: string;
  userId: string;
  conversationId: string;
  content: string;
  status: HomeworkStatus;
  assignedAt: Date;
  dueDate?: Date;
  completedAt?: Date;
  notes?: string;
}

/**
 * LLM response format
 */
export interface LLMResponse {
  assistant: string;
  homework?: string;
  crisisFlag: boolean;
}

/**
 * Options for memory retrieval
 */
export interface MemoryRetrievalOptions {
  userId: string;
  conversationId?: string;
  category?: MemoryCategory;
  limit?: number;
  minImportance?: number;
}

/**
 * Repository interface for memory storage
 */
export interface MemoryRepository {
  storeImportantMemory(memory: Omit<ImportantMemory, "id" | "createdAt">): Promise<ImportantMemory>;
  retrieveRelevantMemories(options: MemoryRetrievalOptions): Promise<ImportantMemory[]>;
  getMemoryById(id: string): Promise<ImportantMemory | null>;
  updateMemory(id: string, data: Partial<ImportantMemory>): Promise<ImportantMemory>;
  deleteMemory(id: string): Promise<void>;
}

/**
 * Repository interface for conversation storage
 */
export interface ConversationRepository {
  createConversation(userId: string, title: string): Promise<Conversation>;
  getConversationById(id: string): Promise<Conversation | null>;
  getUserConversations(userId: string): Promise<Conversation[]>;
  addMessageToConversation(conversationId: string, message: Omit<Message, "id" | "conversationId" | "createdAt">): Promise<Message>;
  getConversationMessages(conversationId: string): Promise<Message[]>;
}

/**
 * Repository interface for homework management
 */
export interface HomeworkRepository {
  createHomeworkAssignment(homework: Omit<HomeworkAssignment, "id" | "assignedAt">): Promise<HomeworkAssignment>;
  getHomeworkById(id: string): Promise<HomeworkAssignment | null>;
  getUserHomework(userId: string, status?: HomeworkStatus): Promise<HomeworkAssignment[]>;
  updateHomeworkStatus(id: string, status: HomeworkStatus, notes?: string): Promise<HomeworkAssignment>;
  getConversationHomework(conversationId: string): Promise<HomeworkAssignment[]>;
} 