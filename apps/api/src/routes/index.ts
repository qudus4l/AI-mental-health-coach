/**
 * API routes registration
 */
import { FastifyInstance } from 'fastify';
import { registerConversationRoutes } from './conversation-routes';
import { registerMemoryRoutes } from './memory-routes';
import { registerHomeworkRoutes } from './homework-routes';
import { registerAuthRoutes } from './auth-routes';

/**
 * Register all API routes with the Fastify server
 * 
 * @param server - Fastify server instance
 */
export function registerRoutes(server: FastifyInstance): void {
  // Register all route groups
  registerAuthRoutes(server);
  registerConversationRoutes(server);
  registerMemoryRoutes(server);
  registerHomeworkRoutes(server);
} 