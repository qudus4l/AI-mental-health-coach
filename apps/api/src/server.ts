/**
 * Server setup for the AI Mental Health Coach API
 */
import Fastify, { FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';

// Import routes
import { registerRoutes } from './routes';

/**
 * Create and configure the Fastify server
 * 
 * @returns Configured Fastify server instance
 */
export async function createServer(): Promise<FastifyInstance> {
  const server = Fastify({
    logger: process.env.NODE_ENV === 'development',
    trustProxy: true,
  });

  // Register plugins
  await server.register(cors, {
    origin: process.env.WEB_URL || 'http://localhost:3000',
    credentials: true,
  });

  await server.register(jwt, {
    secret: process.env.JWT_SECRET || 'development-secret-key',
  });

  // Register Swagger
  await server.register(swagger, {
    openapi: {
      info: {
        title: 'AI Mental Health Coach API',
        description: 'API for the AI Mental Health Coach application',
        version: '0.1.0',
      },
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer',
            bearerFormat: 'JWT',
          },
        },
      },
    },
  });

  await server.register(swaggerUi, {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: true,
    },
  });

  // Register authentication hook
  server.addHook('onRequest', async (request, reply) => {
    try {
      // Skip authentication for specific routes
      if (
        request.url === '/health' ||
        request.url === '/docs' ||
        request.url === '/docs/json' ||
        request.url === '/docs/uiConfig' ||
        request.url === '/docs/static' ||
        request.url.startsWith('/docs/static/') ||
        request.url === '/api/auth'
      ) {
        return;
      }

      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized' });
    }
  });

  // Health check route
  server.get('/health', async () => {
    return { status: 'ok' };
  });

  // Register all API routes
  registerRoutes(server);

  return server;
} 