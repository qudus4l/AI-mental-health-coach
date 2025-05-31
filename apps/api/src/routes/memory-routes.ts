/**
 * Memory routes for the API
 */
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { createMemoryRepository } from '@ai-mental-health-coach/db';
import { MemoryCategory } from '@ai-mental-health-coach/core';

/**
 * Memory repository instance
 */
const memoryRepository = createMemoryRepository();

/**
 * Memory schema
 */
const memorySchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  conversationId: z.string().uuid(),
  content: z.string(),
  category: z.enum([
    MemoryCategory.TRIGGER,
    MemoryCategory.COPING,
    MemoryCategory.BREAKTHROUGH,
    MemoryCategory.GOAL,
  ]),
  importance: z.number().min(0).max(1),
  createdAt: z.string().datetime(),
});

/**
 * Create memory schema
 */
const createMemorySchema = z.object({
  conversationId: z.string().uuid(),
  content: z.string().min(1),
  category: z.enum([
    MemoryCategory.TRIGGER,
    MemoryCategory.COPING,
    MemoryCategory.BREAKTHROUGH,
    MemoryCategory.GOAL,
  ]),
});

/**
 * Update memory schema
 */
const updateMemorySchema = z.object({
  content: z.string().min(1).optional(),
  category: z.enum([
    MemoryCategory.TRIGGER,
    MemoryCategory.COPING,
    MemoryCategory.BREAKTHROUGH,
    MemoryCategory.GOAL,
  ]).optional(),
  importance: z.number().min(0).max(1).optional(),
});

/**
 * Register memory routes
 * 
 * @param server - Fastify server instance
 */
export function registerMemoryRoutes(server: FastifyInstance): void {
  /**
   * Get memories for the current user
   */
  server.get(
    '/api/memories',
    {
      schema: {
        tags: ['Memories'],
        summary: 'Get memories for the current user',
        security: [{ bearerAuth: [] }],
        querystring: z.object({
          conversationId: z.string().uuid().optional(),
          category: z.enum([
            MemoryCategory.TRIGGER,
            MemoryCategory.COPING,
            MemoryCategory.BREAKTHROUGH,
            MemoryCategory.GOAL,
          ]).optional(),
          limit: z.string().transform(Number).optional(),
          minImportance: z.string().transform(Number).optional(),
        }),
        response: {
          200: z.array(memorySchema),
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const query = request.query as {
          conversationId?: string;
          category?: MemoryCategory;
          limit?: number;
          minImportance?: number;
        };
        
        const memories = await memoryRepository.retrieveRelevantMemories({
          userId,
          ...query,
        });
        
        return memories.map(memory => ({
          ...memory,
          createdAt: memory.createdAt.toISOString(),
        }));
      } catch (error) {
        console.error('Error getting memories:', error);
        return reply.code(500).send({ error: 'Failed to get memories' });
      }
    }
  );

  /**
   * Get a specific memory by ID
   */
  server.get(
    '/api/memories/:id',
    {
      schema: {
        tags: ['Memories'],
        summary: 'Get a specific memory by ID',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        response: {
          200: memorySchema,
          401: z.object({
            error: z.string(),
          }),
          404: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { id } = request.params as { id: string };
        
        const memory = await memoryRepository.getMemoryById(id);
        
        if (!memory) {
          return reply.code(404).send({ error: 'Memory not found' });
        }
        
        if (memory.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to memory' });
        }
        
        return {
          ...memory,
          createdAt: memory.createdAt.toISOString(),
        };
      } catch (error) {
        console.error('Error getting memory:', error);
        return reply.code(500).send({ error: 'Failed to get memory' });
      }
    }
  );

  /**
   * Create a new memory
   */
  server.post(
    '/api/memories',
    {
      schema: {
        tags: ['Memories'],
        summary: 'Create a new memory',
        security: [{ bearerAuth: [] }],
        body: createMemorySchema,
        response: {
          201: memorySchema,
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { conversationId, content, category } = createMemorySchema.parse(request.body);
        
        const memory = await memoryRepository.storeImportantMemory({
          userId,
          conversationId,
          content,
          category,
          importance: 0, // Will be calculated by service
        });
        
        return reply.code(201).send({
          ...memory,
          createdAt: memory.createdAt.toISOString(),
        });
      } catch (error) {
        console.error('Error creating memory:', error);
        return reply.code(500).send({ error: 'Failed to create memory' });
      }
    }
  );

  /**
   * Update a memory
   */
  server.patch(
    '/api/memories/:id',
    {
      schema: {
        tags: ['Memories'],
        summary: 'Update a memory',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        body: updateMemorySchema,
        response: {
          200: memorySchema,
          401: z.object({
            error: z.string(),
          }),
          404: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { id } = request.params as { id: string };
        const updates = updateMemorySchema.parse(request.body);
        
        // Check if memory exists and belongs to user
        const memory = await memoryRepository.getMemoryById(id);
        
        if (!memory) {
          return reply.code(404).send({ error: 'Memory not found' });
        }
        
        if (memory.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to memory' });
        }
        
        // Update memory
        const updatedMemory = await memoryRepository.updateMemory(id, updates);
        
        return {
          ...updatedMemory,
          createdAt: updatedMemory.createdAt.toISOString(),
        };
      } catch (error) {
        console.error('Error updating memory:', error);
        return reply.code(500).send({ error: 'Failed to update memory' });
      }
    }
  );

  /**
   * Delete a memory
   */
  server.delete(
    '/api/memories/:id',
    {
      schema: {
        tags: ['Memories'],
        summary: 'Delete a memory',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        response: {
          204: z.null(),
          401: z.object({
            error: z.string(),
          }),
          404: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { id } = request.params as { id: string };
        
        // Check if memory exists and belongs to user
        const memory = await memoryRepository.getMemoryById(id);
        
        if (!memory) {
          return reply.code(404).send({ error: 'Memory not found' });
        }
        
        if (memory.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to memory' });
        }
        
        // Delete memory
        await memoryRepository.deleteMemory(id);
        
        return reply.code(204).send(null);
      } catch (error) {
        console.error('Error deleting memory:', error);
        return reply.code(500).send({ error: 'Failed to delete memory' });
      }
    }
  );
} 