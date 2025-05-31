/**
 * Database package for the AI Mental Health Coach
 */

// Export the Prisma client
export * from './client';

// Export the repositories
export * from './repositories/memory-repository';
export * from './repositories/conversation-repository';
export * from './repositories/homework-repository';

// Export a factory for creating repositories
import { prisma } from './client';
import { PrismaMemoryRepository } from './repositories/memory-repository';
import { PrismaConversationRepository } from './repositories/conversation-repository';
import { PrismaHomeworkRepository } from './repositories/homework-repository';

/**
 * Creates memory repository instance
 * 
 * @returns Memory repository instance
 */
export function createMemoryRepository() {
  return new PrismaMemoryRepository(prisma);
}

/**
 * Creates conversation repository instance
 * 
 * @returns Conversation repository instance
 */
export function createConversationRepository() {
  return new PrismaConversationRepository(prisma);
}

/**
 * Creates homework repository instance
 * 
 * @returns Homework repository instance
 */
export function createHomeworkRepository() {
  return new PrismaHomeworkRepository(prisma);
} 