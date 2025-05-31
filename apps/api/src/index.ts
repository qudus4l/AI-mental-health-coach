/**
 * Main entry point for the AI Mental Health Coach API
 */
import 'dotenv/config';
import { createServer } from './server';

/**
 * Server port
 */
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3001;

/**
 * Starts the server
 */
async function start() {
  try {
    const server = await createServer();
    
    // Start listening
    await server.listen({ port: PORT, host: '0.0.0.0' });
    
    // Log startup message
    console.log(`🚀 Server listening at http://localhost:${PORT}`);
    console.log(`📚 API documentation available at http://localhost:${PORT}/docs`);
  } catch (err) {
    console.error('Error starting server:', err);
    process.exit(1);
  }
}

// Start the server
start(); 