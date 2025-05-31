/**
 * Prisma implementation of the homework repository
 */
import { PrismaClient } from '@prisma/client';
import {
  HomeworkAssignment,
  HomeworkRepository,
  HomeworkStatus,
} from '@ai-mental-health-coach/core';

/**
 * Prisma implementation of the homework repository
 */
export class PrismaHomeworkRepository implements HomeworkRepository {
  /**
   * The Prisma client instance
   */
  private prisma: PrismaClient;

  /**
   * Creates a new Prisma homework repository
   * 
   * @param prisma - The Prisma client instance
   */
  constructor(prisma: PrismaClient) {
    this.prisma = prisma;
  }

  /**
   * Creates a new homework assignment
   * 
   * @param homework - The homework assignment to create
   * @returns The created homework assignment
   */
  public async createHomeworkAssignment(
    homework: Omit<HomeworkAssignment, 'id' | 'assignedAt'>
  ): Promise<HomeworkAssignment> {
    const { userId, conversationId, content, status, dueDate, completedAt, notes } = homework;

    const result = await this.prisma.homeworkAssignment.create({
      data: {
        userId,
        conversationId,
        content,
        status: status.toString(),
        dueDate,
        completedAt,
        notes,
      },
    });

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      status: result.status as HomeworkStatus,
      assignedAt: result.assignedAt,
      dueDate: result.dueDate || undefined,
      completedAt: result.completedAt || undefined,
      notes: result.notes || undefined,
    };
  }

  /**
   * Gets a homework assignment by ID
   * 
   * @param id - The homework assignment ID
   * @returns The homework assignment or null if not found
   */
  public async getHomeworkById(id: string): Promise<HomeworkAssignment | null> {
    const result = await this.prisma.homeworkAssignment.findUnique({
      where: { id },
    });

    if (!result) {
      return null;
    }

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      status: result.status as HomeworkStatus,
      assignedAt: result.assignedAt,
      dueDate: result.dueDate || undefined,
      completedAt: result.completedAt || undefined,
      notes: result.notes || undefined,
    };
  }

  /**
   * Gets all homework assignments for a user
   * 
   * @param userId - The user ID
   * @param status - Optional status filter
   * @returns Array of homework assignments
   */
  public async getUserHomework(
    userId: string,
    status?: HomeworkStatus
  ): Promise<HomeworkAssignment[]> {
    const whereClause: any = { userId };

    if (status) {
      whereClause.status = status.toString();
    }

    const results = await this.prisma.homeworkAssignment.findMany({
      where: whereClause,
      orderBy: {
        assignedAt: 'desc',
      },
    });

    return results.map((result) => ({
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      status: result.status as HomeworkStatus,
      assignedAt: result.assignedAt,
      dueDate: result.dueDate || undefined,
      completedAt: result.completedAt || undefined,
      notes: result.notes || undefined,
    }));
  }

  /**
   * Updates the status of a homework assignment
   * 
   * @param id - The homework assignment ID
   * @param status - The new status
   * @param notes - Optional notes to update
   * @returns The updated homework assignment
   */
  public async updateHomeworkStatus(
    id: string,
    status: HomeworkStatus,
    notes?: string
  ): Promise<HomeworkAssignment> {
    const data: any = {
      status: status.toString(),
    };

    if (status === HomeworkStatus.COMPLETED && !await this.isHomeworkCompleted(id)) {
      data.completedAt = new Date();
    }

    if (notes !== undefined) {
      data.notes = notes;
    }

    const result = await this.prisma.homeworkAssignment.update({
      where: { id },
      data,
    });

    return {
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      status: result.status as HomeworkStatus,
      assignedAt: result.assignedAt,
      dueDate: result.dueDate || undefined,
      completedAt: result.completedAt || undefined,
      notes: result.notes || undefined,
    };
  }

  /**
   * Gets all homework assignments for a conversation
   * 
   * @param conversationId - The conversation ID
   * @returns Array of homework assignments
   */
  public async getConversationHomework(
    conversationId: string
  ): Promise<HomeworkAssignment[]> {
    const results = await this.prisma.homeworkAssignment.findMany({
      where: { conversationId },
      orderBy: {
        assignedAt: 'desc',
      },
    });

    return results.map((result) => ({
      id: result.id,
      userId: result.userId,
      conversationId: result.conversationId,
      content: result.content,
      status: result.status as HomeworkStatus,
      assignedAt: result.assignedAt,
      dueDate: result.dueDate || undefined,
      completedAt: result.completedAt || undefined,
      notes: result.notes || undefined,
    }));
  }

  /**
   * Checks if a homework assignment is already completed
   * 
   * @param id - The homework assignment ID
   * @returns Whether the homework is completed
   */
  private async isHomeworkCompleted(id: string): Promise<boolean> {
    const homework = await this.prisma.homeworkAssignment.findUnique({
      where: { id },
      select: { status: true },
    });

    return homework?.status === HomeworkStatus.COMPLETED.toString();
  }
} 