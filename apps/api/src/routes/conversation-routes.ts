/**
 * Conversation routes for the API
 */
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { createConversationRepository } from '@ai-mental-health-coach/db';
import { MessageRole } from '@ai-mental-health-coach/core';
import { processMessage } from '../services/conversation-service';

/**
 * Conversation repository instance
 */
const conversationRepository = createConversationRepository();

/**
 * Create conversation schema
 */
const createConversationSchema = z.object({
  title: z.string().min(1),
});

/**
 * Conversation response schema
 */
const conversationSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  userId: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

/**
 * Message schema
 */
const messageSchema = z.object({
  id: z.string().uuid(),
  conversationId: z.string().uuid(),
  userId: z.string().uuid(),
  role: z.enum([MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM]),
  content: z.string(),
  createdAt: z.string().datetime(),
});

/**
 * Add message schema
 */
const addMessageSchema = z.object({
  content: z.string().min(1),
});

/**
 * Register conversation routes
 * 
 * @param server - Fastify server instance
 */
export function registerConversationRoutes(server: FastifyInstance): void {
  /**
   * Get all conversations for the current user
   */
  server.get(
    '/api/conversations',
    {
      schema: {
        tags: ['Conversations'],
        summary: 'Get all conversations for the current user',
        security: [{ bearerAuth: [] }],
        response: {
          200: z.array(conversationSchema),
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const conversations = await conversationRepository.getUserConversations(userId);
        
        return conversations.map(conv => ({
          ...conv,
          createdAt: conv.createdAt.toISOString(),
          updatedAt: conv.updatedAt.toISOString(),
          // Don't include messages in the list view
          messages: undefined,
        }));
      } catch (error) {
        console.error('Error getting conversations:', error);
        return reply.code(500).send({ error: 'Failed to get conversations' });
      }
    }
  );

  /**
   * Create a new conversation
   */
  server.post(
    '/api/conversations',
    {
      schema: {
        tags: ['Conversations'],
        summary: 'Create a new conversation',
        security: [{ bearerAuth: [] }],
        body: createConversationSchema,
        response: {
          201: conversationSchema,
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        const { title } = createConversationSchema.parse(request.body);
        
        const conversation = await conversationRepository.createConversation(userId, title);
        
        return reply.code(201).send({
          ...conversation,
          createdAt: conversation.createdAt.toISOString(),
          updatedAt: conversation.updatedAt.toISOString(),
          // Don't include messages in the response
          messages: undefined,
        });
      } catch (error) {
        console.error('Error creating conversation:', error);
        return reply.code(500).send({ error: 'Failed to create conversation' });
      }
    }
  );

  /**
   * Get a specific conversation by ID
   */
  server.get(
    '/api/conversations/:id',
    {
      schema: {
        tags: ['Conversations'],
        summary: 'Get a specific conversation by ID',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        response: {
          200: conversationSchema.extend({
            messages: z.array(messageSchema),
          }),
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
        
        const conversation = await conversationRepository.getConversationById(id);
        
        if (!conversation) {
          return reply.code(404).send({ error: 'Conversation not found' });
        }
        
        if (conversation.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to conversation' });
        }
        
        return {
          ...conversation,
          createdAt: conversation.createdAt.toISOString(),
          updatedAt: conversation.updatedAt.toISOString(),
          messages: conversation.messages.map(msg => ({
            ...msg,
            createdAt: msg.createdAt.toISOString(),
          })),
        };
      } catch (error) {
        console.error('Error getting conversation:', error);
        return reply.code(500).send({ error: 'Failed to get conversation' });
      }
    }
  );

  /**
   * Add a message to a conversation
   */
  server.post(
    '/api/conversations/:id/messages',
    {
      schema: {
        tags: ['Conversations'],
        summary: 'Add a message to a conversation',
        security: [{ bearerAuth: [] }],
        params: z.object({
          id: z.string().uuid(),
        }),
        body: addMessageSchema,
        response: {
          200: z.object({
            userMessage: messageSchema,
            assistantMessage: messageSchema,
            homework: z.string().optional(),
            crisisFlag: z.boolean(),
          }),
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
        const { content } = addMessageSchema.parse(request.body);
        
        const conversation = await conversationRepository.getConversationById(id);
        
        if (!conversation) {
          return reply.code(404).send({ error: 'Conversation not found' });
        }
        
        if (conversation.userId !== userId) {
          return reply.code(403).send({ error: 'Unauthorized access to conversation' });
        }
        
        // Process the message and get AI response
        const result = await processMessage(userId, id, content);
        
        return {
          ...result,
          userMessage: {
            ...result.userMessage,
            createdAt: result.userMessage.createdAt.toISOString(),
          },
          assistantMessage: {
            ...result.assistantMessage,
            createdAt: result.assistantMessage.createdAt.toISOString(),
          },
        };
      } catch (error) {
        console.error('Error adding message:', error);
        return reply.code(500).send({ error: 'Failed to process message' });
      }
    }
  );
} 