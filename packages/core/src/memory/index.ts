/**
 * Memory utilities for storing and retrieving important memories
 */
import { ImportantMemory, MemoryCategory, MemoryRepository, MemoryRetrievalOptions } from '../types';

/**
 * Analyzes conversation context to determine memory importance score
 * 
 * @param content - The memory content to analyze
 * @param category - The memory category
 * @returns An importance score between 0 and 1
 */
export function calculateImportance(content: string, category: MemoryCategory): number {
  // Simple implementation for MVP - later phases will use more sophisticated analysis
  const baseImportance = {
    [MemoryCategory.TRIGGER]: 0.7,
    [MemoryCategory.COPING]: 0.8,
    [MemoryCategory.BREAKTHROUGH]: 0.9,
    [MemoryCategory.GOAL]: 0.85
  }[category] || 0.5;
  
  // Length-based adjustment (longer content often has more detail)
  const lengthAdjustment = Math.min(content.length / 500, 0.2);
  
  return Math.min(baseImportance + lengthAdjustment, 1.0);
}

/**
 * Memory service for storing and retrieving important memories
 */
export class MemoryService {
  private repository: MemoryRepository;

  /**
   * Creates a new memory service
   * 
   * @param repository - The memory repository implementation
   */
  constructor(repository: MemoryRepository) {
    this.repository = repository;
  }

  /**
   * Stores an important memory
   * 
   * @param userId - The user ID
   * @param conversationId - The conversation ID
   * @param content - The memory content
   * @param category - The memory category
   * @returns The stored memory
   */
  public async storeImportantMemory(
    userId: string,
    conversationId: string,
    content: string,
    category: MemoryCategory
  ): Promise<ImportantMemory> {
    const importance = calculateImportance(content, category);
    
    return this.repository.storeImportantMemory({
      userId,
      conversationId,
      content,
      category,
      importance
    });
  }

  /**
   * Retrieves relevant memories based on provided options
   * 
   * @param options - Memory retrieval options
   * @returns Array of relevant memories
   */
  public async retrieveRelevantMemories(options: MemoryRetrievalOptions): Promise<ImportantMemory[]> {
    return this.repository.retrieveRelevantMemories({
      ...options,
      // Default to retrieving most important memories
      limit: options.limit || 5,
      minImportance: options.minImportance || 0.6
    });
  }

  /**
   * Gets a specific memory by ID
   * 
   * @param id - The memory ID
   * @returns The memory or null if not found
   */
  public async getMemoryById(id: string): Promise<ImportantMemory | null> {
    return this.repository.getMemoryById(id);
  }

  /**
   * Updates a memory
   * 
   * @param id - The memory ID
   * @param data - The data to update
   * @returns The updated memory
   */
  public async updateMemory(id: string, data: Partial<ImportantMemory>): Promise<ImportantMemory> {
    return this.repository.updateMemory(id, data);
  }

  /**
   * Deletes a memory
   * 
   * @param id - The memory ID
   */
  public async deleteMemory(id: string): Promise<void> {
    return this.repository.deleteMemory(id);
  }
} 