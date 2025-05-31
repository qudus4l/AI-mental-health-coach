/**
 * Prisma implementation of the memory repository
 */
import { PrismaClient } from '@prisma/client';
import {
  ImportantMemory,
  MemoryCategory,
  MemoryRepository,
  MemoryRetrievalOptions,
} from '@ai-mental-health-coach/core';

/**
 * Prisma implementation of the memory repository
 */
export class PrismaMemoryRepository implements MemoryRepository {
  /**
   * The Prisma client instance
   */
  private prisma: PrismaClient;

  /**
   * Creates a new Prisma memory repository
   * 
   * @param prisma - The Prisma client instance
   */
  constructor(prisma: PrismaClient) {
    this.prisma = prisma;
  }

  /**
   * Stores an important memory
   * 
   * @param memory - The memory to store
   * @returns The stored memory
   */
  public async storeImportantMemory(
    memory: Omit<ImportantMemory, 'id' | 'createdAt'>
  ): Promise<ImportantMemory> {
    const { userId, conversationId, content, category, importance } = memory;

    const result = await this.prisma.importantMemory.create({
      data: {
        userId,
        conversationId,
        content,
        category: category.toString(),
        importance,
      },
    });

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      category: result.category as MemoryCategory,
      importance: result.importance,
      createdAt: result.createdAt,
    };
  }

  /**
   * Retrieves relevant memories based on provided options
   * 
   * @param options - Memory retrieval options
   * @returns Array of relevant memories
   */
  public async retrieveRelevantMemories(
    options: MemoryRetrievalOptions
  ): Promise<ImportantMemory[]> {
    const { userId, conversationId, category, limit = 5, minImportance = 0.6 } = options;

    const whereClause: any = {
      userId,
      importance: {
        gte: minImportance,
      },
    };

    if (conversationId) {
      whereClause.conversationId = conversationId;
    }

    if (category) {
      whereClause.category = category.toString();
    }

    const results = await this.prisma.importantMemory.findMany({
      where: whereClause,
      orderBy: {
        importance: 'desc',
      },
      take: limit,
    });

    return results.map((result) => ({
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      category: result.category as MemoryCategory,
      importance: result.importance,
      createdAt: result.createdAt,
    }));
  }

  /**
   * Gets a specific memory by ID
   * 
   * @param id - The memory ID
   * @returns The memory or null if not found
   */
  public async getMemoryById(id: string): Promise<ImportantMemory | null> {
    const result = await this.prisma.importantMemory.findUnique({
      where: { id },
    });

    if (!result) {
      return null;
    }

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      category: result.category as MemoryCategory,
      importance: result.importance,
      createdAt: result.createdAt,
    };
  }

  /**
   * Updates a memory
   * 
   * @param id - The memory ID
   * @param data - The data to update
   * @returns The updated memory
   */
  public async updateMemory(
    id: string,
    data: Partial<ImportantMemory>
  ): Promise<ImportantMemory> {
    const updateData: any = { ...data };
    
    if (data.category) {
      updateData.category = data.category.toString();
    }

    const result = await this.prisma.importantMemory.update({
      where: { id },
      data: updateData,
    });

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      category: result.category as MemoryCategory,
      importance: result.importance,
      createdAt: result.createdAt,
    };
  }

  /**
   * Deletes a memory
   * 
   * @param id - The memory ID
   */
  public async deleteMemory(id: string): Promise<void> {
    await this.prisma.importantMemory.delete({
      where: { id },
    });
  }
} 