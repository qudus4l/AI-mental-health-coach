/**
 * Seed script for populating the database with demo data
 */
import { PrismaClient } from '@prisma/client';
import { HomeworkStatus, MemoryCategory, MessageRole } from '@ai-mental-health-coach/core';
import * as crypto from 'crypto';

// Create a Prisma client instance
const prisma = new PrismaClient();

/**
 * Encrypts sensitive data using AES-256-CBC
 * 
 * @param text - Text to encrypt
 * @param key - Encryption key (32 bytes)
 * @param iv - Initialization vector (16 bytes)
 * @returns Encrypted text
 */
function encrypt(text: string, key: string, iv: string): string {
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key), Buffer.from(iv));
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

/**
 * Seeds the database with demo data
 */
async function seed() {
  try {
    console.log('🌱 Starting database seeding...');

    // Get encryption key and IV from environment variables or use defaults (for demo only)
    const encryptionKey = process.env.ENCRYPTION_KEY || '12345678901234567890123456789012';
    const encryptionIv = process.env.ENCRYPTION_IV || '1234567890123456';

    // Create a demo user
    const demoUser = await prisma.user.upsert({
      where: { email: 'demo@example.com' },
      update: {},
      create: {
        email: 'demo@example.com',
        encryptedEmail: encrypt('demo@example.com', encryptionKey, encryptionIv),
        name: 'Demo User',
      },
    });

    console.log(`👤 Created demo user: ${demoUser.id}`);

    // Create a demo conversation
    const demoConversation = await prisma.conversation.create({
      data: {
        userId: demoUser.id,
        title: 'My anxiety about public speaking',
      },
    });

    console.log(`💬 Created demo conversation: ${demoConversation.id}`);

    // Create demo messages
    const messages = [
      {
        role: MessageRole.USER,
        content: "Hi, I've been feeling really anxious about an upcoming presentation at work.",
      },
      {
        role: MessageRole.ASSISTANT,
        content: "I understand that presentations can be anxiety-inducing for many people. Let's explore what specifically about the presentation is causing you anxiety. Is it fear of judgment, concern about forgetting your material, or something else?",
      },
      {
        role: MessageRole.USER,
        content: "I think it's mostly about being judged. I'm worried I'll freeze up and look incompetent in front of my colleagues.",
      },
      {
        role: MessageRole.ASSISTANT,
        content: "That's a common concern. Our fear of negative evaluation can be quite powerful. Let's examine this fear: What's the worst that could realistically happen if you do make a mistake during your presentation? And how likely is it that this worst-case scenario will actually occur?",
      },
      {
        role: MessageRole.USER,
        content: "I suppose the worst case is I'd stumble over my words or forget something important. People might think I'm not prepared or not knowledgeable enough. But realistically, it probably wouldn't be as bad as I'm imagining.",
      },
      {
        role: MessageRole.ASSISTANT,
        content: "You've just demonstrated a key CBT technique - reality testing. You're recognizing that while there's a possibility of making mistakes, the catastrophic outcomes you fear are unlikely. Remember that most people are focused on their own concerns rather than scrutinizing others. Have you had any positive experiences with presentations in the past that might counter these fears?",
      },
    ];

    for (const message of messages) {
      await prisma.message.create({
        data: {
          conversationId: demoConversation.id,
          userId: demoUser.id,
          role: message.role,
          content: message.content,
        },
      });
    }

    console.log(`📝 Created ${messages.length} demo messages`);

    // Create demo memories
    const memories = [
      {
        content: "I feel anxious and fear judgment when speaking in public",
        category: MemoryCategory.TRIGGER,
        importance: 0.8,
      },
      {
        content: "Reality testing helps me recognize that catastrophic outcomes are unlikely",
        category: MemoryCategory.COPING,
        importance: 0.85,
      },
      {
        content: "Most people are focused on their own concerns rather than scrutinizing others",
        category: MemoryCategory.BREAKTHROUGH,
        importance: 0.9,
      },
    ];

    for (const memory of memories) {
      await prisma.importantMemory.create({
        data: {
          userId: demoUser.id,
          conversationId: demoConversation.id,
          content: memory.content,
          category: memory.category,
          importance: memory.importance,
        },
      });
    }

    console.log(`🧠 Created ${memories.length} demo memories`);

    // Create a demo homework assignment
    const homework = await prisma.homeworkAssignment.create({
      data: {
        userId: demoUser.id,
        conversationId: demoConversation.id,
        content: "Practice your presentation in front of a mirror or record yourself on video. Note any moments of anxiety and write down what specific thoughts came up.",
        status: HomeworkStatus.ASSIGNED,
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 1 week from now
      },
    });

    console.log(`📚 Created demo homework assignment: ${homework.id}`);
    console.log('✅ Seeding completed successfully!');
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the seed function
seed(); 