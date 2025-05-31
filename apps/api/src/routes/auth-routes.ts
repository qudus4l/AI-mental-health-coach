/**
 * Authentication routes for the API
 */
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { prisma } from '@ai-mental-health-coach/db';

/**
 * Authentication token schema
 */
const tokenSchema = z.object({
  token: z.string().min(1),
});

/**
 * User info schema
 */
const userInfoSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().optional(),
  image: z.string().optional(),
});

/**
 * Register authentication routes
 * 
 * @param server - Fastify server instance
 */
export function registerAuthRoutes(server: FastifyInstance): void {
  /**
   * Verify a JWT token and return user information
   */
  server.post(
    '/api/auth/verify',
    {
      schema: {
        tags: ['Auth'],
        summary: 'Verify a JWT token and get user information',
        body: tokenSchema,
        response: {
          200: userInfoSchema,
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const { token } = tokenSchema.parse(request.body);
        
        // Verify token
        const payload = server.jwt.verify<{ sub: string }>(token);
        
        if (!payload.sub) {
          return reply.code(401).send({ error: 'Invalid token' });
        }
        
        // Get user from database
        const user = await prisma.user.findUnique({
          where: { id: payload.sub },
          select: {
            id: true,
            email: true,
            name: true,
            image: true,
          },
        });
        
        if (!user) {
          return reply.code(401).send({ error: 'User not found' });
        }
        
        return user;
      } catch (error) {
        return reply.code(401).send({ error: 'Invalid token' });
      }
    }
  );
  
  /**
   * Get current user information
   * This endpoint requires authentication (JWT token in header)
   */
  server.get(
    '/api/auth/me',
    {
      schema: {
        tags: ['Auth'],
        summary: 'Get current user information',
        security: [{ bearerAuth: [] }],
        response: {
          200: userInfoSchema,
          401: z.object({
            error: z.string(),
          }),
        },
      },
    },
    async (request, reply) => {
      try {
        const userId = request.user.sub;
        
        // Get user from database
        const user = await prisma.user.findUnique({
          where: { id: userId },
          select: {
            id: true,
            email: true,
            name: true,
            image: true,
          },
        });
        
        if (!user) {
          return reply.code(401).send({ error: 'User not found' });
        }
        
        return user;
      } catch (error) {
        return reply.code(401).send({ error: 'Unauthorized' });
      }
    }
  );
} 