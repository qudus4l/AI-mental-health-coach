/**
 * Prisma client instance for database access
 */
import { PrismaClient } from '@prisma/client';

/**
 * Creates a singleton instance of the Prisma client
 */
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

/**
 * PrismaClient instance for database access
 */
export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
} 