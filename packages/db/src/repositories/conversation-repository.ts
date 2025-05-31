/**
 * Prisma implementation of the conversation repository
 */
import { PrismaClient } from '@prisma/client';
import {
  Conversation,
  ConversationRepository,
  Message,
  MessageRole,
} from '@ai-mental-health-coach/core';

/**
 * Prisma implementation of the conversation repository
 */
export class PrismaConversationRepository implements ConversationRepository {
  /**
   * The Prisma client instance
   */
  private prisma: PrismaClient;

  /**
   * Creates a new Prisma conversation repository
   * 
   * @param prisma - The Prisma client instance
   */
  constructor(prisma: PrismaClient) {
    this.prisma = prisma;
  }

  /**
   * Creates a new conversation
   * 
   * @param userId - The user ID
   * @param title - The conversation title
   * @returns The created conversation
   */
  public async createConversation(userId: string, title: string): Promise<Conversation> {
    const conversation = await this.prisma.conversation.create({
      data: {
        userId,
        title,
      },
    });

    return {
      id: conversation.id,
      userId: conversation.userId,
      title: conversation.title,
      createdAt: conversation.createdAt,
      updatedAt: conversation.updatedAt,
      messages: [],
    };
  }

  /**
   * Gets a conversation by ID
   * 
   * @param id - The conversation ID
   * @returns The conversation or null if not found
   */
  public async getConversationById(id: string): Promise<Conversation | null> {
    const conversation = await this.prisma.conversation.findUnique({
      where: { id },
      include: {
        messages: {
          orderBy: {
            createdAt: 'asc',
          },
        },
      },
    });

    if (!conversation) {
      return null;
    }

    return {
      id: conversation.id,
      userId: conversation.userId,
      title: conversation.title,
      createdAt: conversation.createdAt,
      updatedAt: conversation.updatedAt,
      messages: conversation.messages.map((message) => ({
        id: message.id,
        conversationId: message.conversationId,
        userId: message.userId,
        role: message.role as MessageRole,
        content: message.content,
        createdAt: message.createdAt,
      })),
    };
  }

  /**
   * Gets all conversations for a user
   * 
   * @param userId - The user ID
   * @returns Array of conversations
   */
  public async getUserConversations(userId: string): Promise<Conversation[]> {
    const conversations = await this.prisma.conversation.findMany({
      where: { userId },
      include: {
        messages: {
          orderBy: {
            createdAt: 'asc',
          },
          take: 1, // Just get the first message for preview
        },
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });

    return conversations.map((conversation) => ({
      id: conversation.id,
      userId: conversation.userId,
      title: conversation.title,
      createdAt: conversation.createdAt,
      updatedAt: conversation.updatedAt,
      messages: conversation.messages.map((message) => ({
        id: message.id,
        conversationId: message.conversationId,
        userId: message.userId,
        role: message.role as MessageRole,
        content: message.content,
        createdAt: message.createdAt,
      })),
    }));
  }

  /**
   * Adds a message to a conversation
   * 
   * @param conversationId - The conversation ID
   * @param message - The message to add
   * @returns The added message
   */
  public async addMessageToConversation(
    conversationId: string,
    message: Omit<Message, 'id' | 'conversationId' | 'createdAt'>
  ): Promise<Message> {
    const { userId, role, content } = message;

    // Update conversation updatedAt
    await this.prisma.conversation.update({
      where: { id: conversationId },
      data: { updatedAt: new Date() },
    });

    // Create message
    const createdMessage = await this.prisma.message.create({
      data: {
        conversationId,
        userId,
        role: role.toString(),
        content,
      },
    });

    return {
      id: createdMessage.id,
      conversationId: createdMessage.conversationId,
      userId: createdMessage.userId,
      role: createdMessage.role as MessageRole,
      content: createdMessage.content,
      createdAt: createdMessage.createdAt,
    };
  }

  /**
   * Gets all messages for a conversation
   * 
   * @param conversationId - The conversation ID
   * @returns Array of messages
   */
  public async getConversationMessages(conversationId: string): Promise<Message[]> {
    const messages = await this.prisma.message.findMany({
      where: { conversationId },
      orderBy: {
        createdAt: 'asc',
      },
    });

    return messages.map((message) => ({
      id: message.id,
      conversationId: message.conversationId,
      userId: message.userId,
      role: message.role as MessageRole,
      content: message.content,
      createdAt: message.createdAt,
    }));
  }
} 