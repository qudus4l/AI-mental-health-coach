/**
 * Homework routes for the API
 */
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { createHomeworkRepository } from '@ai-mental-health-coach/db';
import { HomeworkStatus } from '@ai-mental-health-coach/core';

/**
 * Homework repository instance
 */
const homeworkRepository = createHomeworkRepository();

/**
 * Homework schema
 */
const homeworkSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  conversationId: z.string().uuid(),
  content: z.string(),
  status: z.enum([
    HomeworkStatus.ASSIGNED,
    HomeworkStatus.IN_PROGRESS,
    HomeworkStatus.COMPLETED,
    HomeworkStatus.SKIPPED,
  ]),
  assignedAt: z.string().datetime(),
  dueDate: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional(),
  notes: z.string().optional(),
});

/**
 * Create homework schema
 */
const createHomeworkSchema = z.object({
  conversationId: z.string().uuid(),
  content: z.string().min(1),
  dueDate: z.string().datetime().optional(),
  notes: z.string().optional(),
});

/**
 * Update homework status schema
 */
const updateHomeworkStatusSchema = z.object({
  status: z.enum([
    HomeworkStatus.ASSIGNED,
    HomeworkStatus.IN_PROGRESS,
    HomeworkStatus.COMPLETED,
    HomeworkStatus.SKIPPED,
  ]),
  notes: z.string().optional(),
});

/**
 * Register homework routes
 * 
 * @param server - Fastify server instance
 */
export function registerHomeworkRoutes(server: FastifyInstance): void {
  /**
   * Get homework assignments for the current user
   */
  server.get(
    '/api/homework',
    {
      schema: {
        tags: ['Homework'],
        summary: 'Get homework assignments for the current user',
        security: [{ bearerAuth: [] }],
        querystring: z.object({
          status: z.enum([
            HomeworkStatus.ASSIGNED,
            HomeworkStatus.IN_PROGRESS,
            HomeworkStatus.COMPLETED,
            HomeworkStatus.SKIPPED,
          ]).optional(),
        }),
        response: {
          200: z.array(homeworkSchema),
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { status } = request.query as { status?: HomeworkStatus };
        
        const homeworkAssignments = await homeworkRepository.getUserHomework(userId, status);
        
        return homeworkAssignments.map(hw => ({
          ...hw,
          assignedAt: hw.assignedAt.toISOString(),
          dueDate: hw.dueDate?.toISOString(),
          completedAt: hw.completedAt?.toISOString(),
        }));
      } catch (error) {
        console.error('Error getting homework assignments:', error);
        return reply.code(500).send({ error: 'Failed to get homework assignments' });
      }
    }
  );

  /**
   * Get homework assignments for a conversation
   */
  server.get(
    '/api/conversations/:conversationId/homework',
    {
      schema: {
        tags: ['Homework'],
        summary: 'Get homework assignments for a conversation',
        security: [{ bearerAuth: [] }],
        params: z.object({
          conversationId: z.string().uuid(),
        }),
        response: {
          200: z.array(homeworkSchema),
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
        const { conversationId } = request.params as { conversationId: string };
        
        // Verify conversation exists and belongs to user (in a real implementation, check this)
        // For now, we'll just query homework and let it be empty if the conversation doesn't exist
        
        const homeworkAssignments = await homeworkRepository.getConversationHomework(conversationId);
        
        // Filter to ensure only user's homework is returned
        const userHomework = homeworkAssignments.filter(hw => hw.userId === userId);
        
        return userHomework.map(hw => ({
          ...hw,
          assignedAt: hw.assignedAt.toISOString(),
          dueDate: hw.dueDate?.toISOString(),
          completedAt: hw.completedAt?.toISOString(),
        }));
      } catch (error) {
        console.error('Error getting conversation homework:', error);
        return reply.code(500).send({ error: 'Failed to get homework assignments' });
      }
    }
  );

  /**
   * Get a specific homework assignment by ID
   */
  server.get(
    '/api/homework/:id',
    {
      schema: {
        tags: ['Homework'],
        summary: 'Get a specific homework assignment by ID',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        response: {
          200: homeworkSchema,
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
        
        const homework = await homeworkRepository.getHomeworkById(id);
        
        if (!homework) {
          return reply.code(404).send({ error: 'Homework assignment not found' });
        }
        
        if (homework.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to homework assignment' });
        }
        
        return {
          ...homework,
          assignedAt: homework.assignedAt.toISOString(),
          dueDate: homework.dueDate?.toISOString(),
          completedAt: homework.completedAt?.toISOString(),
        };
      } catch (error) {
        console.error('Error getting homework assignment:', error);
        return reply.code(500).send({ error: 'Failed to get homework assignment' });
      }
    }
  );

  /**
   * Create a new homework assignment
   */
  server.post(
    '/api/homework',
    {
      schema: {
        tags: ['Homework'],
        summary: 'Create a new homework assignment',
        security: [{ bearerAuth: [] }],
        body: createHomeworkSchema,
        response: {
          201: homeworkSchema,
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const homeworkData = createHomeworkSchema.parse(request.body);
        
        const homework = await homeworkRepository.createHomeworkAssignment({
          userId,
          conversationId: homeworkData.conversationId,
          content: homeworkData.content,
          status: HomeworkStatus.ASSIGNED,
          dueDate: homeworkData.dueDate ? new Date(homeworkData.dueDate) : undefined,
          notes: homeworkData.notes,
        });
        
        return reply.code(201).send({
          ...homework,
          assignedAt: homework.assignedAt.toISOString(),
          dueDate: homework.dueDate?.toISOString(),
          completedAt: homework.completedAt?.toISOString(),
        });
      } catch (error) {
        console.error('Error creating homework assignment:', error);
        return reply.code(500).send({ error: 'Failed to create homework assignment' });
      }
    }
  );

  /**
   * Update homework status
   */
  server.patch(
    '/api/homework/:id/status',
    {
      schema: {
        tags: ['Homework'],
        summary: 'Update homework status',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        body: updateHomeworkStatusSchema,
        response: {
          200: homeworkSchema,
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
        const { status, notes } = updateHomeworkStatusSchema.parse(request.body);
        
        // Check if homework exists and belongs to user
        const homework = await homeworkRepository.getHomeworkById(id);
        
        if (!homework) {
          return reply.code(404).send({ error: 'Homework assignment not found' });
        }
        
        if (homework.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to homework assignment' });
        }
        
        // Update homework status
        const updatedHomework = await homeworkRepository.updateHomeworkStatus(id, status, notes);
        
        return {
          ...updatedHomework,
          assignedAt: updatedHomework.assignedAt.toISOString(),
          dueDate: updatedHomework.dueDate?.toISOString(),
          completedAt: updatedHomework.completedAt?.toISOString(),
        };
      } catch (error) {
        console.error('Error updating homework status:', error);
        return reply.code(500).send({ error: 'Failed to update homework status' });
      }
    }
  );
} 