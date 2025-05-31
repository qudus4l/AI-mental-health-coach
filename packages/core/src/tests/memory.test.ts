import { describe, expect, it, vi, beforeEach } from 'vitest';
import { MemoryService, calculateImportance } from '../memory';
import { MemoryCategory, ImportantMemory, MemoryRepository, MemoryRetrievalOptions } from '../types';

describe('Memory Utilities', () => {
  describe('calculateImportance', () => {
    it('should calculate importance based on category', () => {
      const triggerImportance = calculateImportance('I get anxious when speaking in public', MemoryCategory.TRIGGER);
      const copingImportance = calculateImportance('Deep breathing helps me calm down', MemoryCategory.COPING);
      const breakthroughImportance = calculateImportance('I realized my anxiety comes from childhood experiences', MemoryCategory.BREAKTHROUGH);
      const goalImportance = calculateImportance('I want to be able to give a presentation without panic', MemoryCategory.GOAL);
      
      expect(triggerImportance).toBeGreaterThan(0);
      expect(copingImportance).toBeGreaterThan(triggerImportance);
      expect(breakthroughImportance).toBeGreaterThan(copingImportance);
      expect(goalImportance).toBeGreaterThan(triggerImportance);
      
      // All importance scores should be between 0 and 1
      [triggerImportance, copingImportance, breakthroughImportance, goalImportance].forEach(score => {
        expect(score).toBeGreaterThanOrEqual(0);
        expect(score).toBeLessThanOrEqual(1);
      });
    });
    
    it('should adjust importance based on content length', () => {
      const shortContent = 'Short memory';
      const longContent = 'This is a much longer memory with more details and context. It describes a specific situation in great detail, including emotional responses, physical sensations, and cognitive patterns that were observed during a triggering event. The additional context and specificity should make this memory more important for therapeutic purposes.';
      
      const shortImportance = calculateImportance(shortContent, MemoryCategory.TRIGGER);
      const longImportance = calculateImportance(longContent, MemoryCategory.TRIGGER);
      
      expect(longImportance).toBeGreaterThan(shortImportance);
    });
    
    it('should cap importance at 1.0', () => {
      const veryLongContent = 'a'.repeat(10000);
      const importance = calculateImportance(veryLongContent, MemoryCategory.BREAKTHROUGH);
      
      expect(importance).toBeLessThanOrEqual(1.0);
    });
  });
  
  describe('MemoryService', () => {
    let memoryService: MemoryService;
    let mockRepository: MemoryRepository;
    
    const mockMemory: ImportantMemory = {
      id: 'memory-id-1',
      userId: 'user-id-1',
      conversationId: 'conversation-id-1',
      content: 'I feel anxious when speaking in public',
      category: MemoryCategory.TRIGGER,
      importance: 0.75,
      createdAt: new Date()
    };
    
    beforeEach(() => {
      mockRepository = {
        storeImportantMemory: vi.fn().mockResolvedValue(mockMemory),
        retrieveRelevantMemories: vi.fn().mockResolvedValue([mockMemory]),
        getMemoryById: vi.fn().mockResolvedValue(mockMemory),
        updateMemory: vi.fn().mockResolvedValue(mockMemory),
        deleteMemory: vi.fn().mockResolvedValue(undefined)
      };
      
      memoryService = new MemoryService(mockRepository);
    });
    
    it('should store an important memory with calculated importance', async () => {
      const result = await memoryService.storeImportantMemory(
        'user-id-1',
        'conversation-id-1',
        'I feel anxious when speaking in public',
        MemoryCategory.TRIGGER
      );
      
      expect(mockRepository.storeImportantMemory).toHaveBeenCalledWith({
        userId: 'user-id-1',
        conversationId: 'conversation-id-1',
        content: 'I feel anxious when speaking in public',
        category: MemoryCategory.TRIGGER,
        importance: expect.any(Number)
      });
      
      expect(result).toEqual(mockMemory);
    });
    
    it('should retrieve relevant memories with default options', async () => {
      const options: MemoryRetrievalOptions = {
        userId: 'user-id-1'
      };
      
      await memoryService.retrieveRelevantMemories(options);
      
      expect(mockRepository.retrieveRelevantMemories).toHaveBeenCalledWith({
        userId: 'user-id-1',
        limit: 5,
        minImportance: 0.6
      });
    });
    
    it('should retrieve relevant memories with custom options', async () => {
      const options: MemoryRetrievalOptions = {
        userId: 'user-id-1',
        conversationId: 'conversation-id-1',
        category: MemoryCategory.COPING,
        limit: 10,
        minImportance: 0.8
      };
      
      await memoryService.retrieveRelevantMemories(options);
      
      expect(mockRepository.retrieveRelevantMemories).toHaveBeenCalledWith(options);
    });
    
    it('should get a specific memory by ID', async () => {
      await memoryService.getMemoryById('memory-id-1');
      expect(mockRepository.getMemoryById).toHaveBeenCalledWith('memory-id-1');
    });
    
    it('should update a memory', async () => {
      const updateData = {
        content: 'Updated content',
        importance: 0.85
      };
      
      await memoryService.updateMemory('memory-id-1', updateData);
      
      expect(mockRepository.updateMemory).toHaveBeenCalledWith('memory-id-1', updateData);
    });
    
    it('should delete a memory', async () => {
      await memoryService.deleteMemory('memory-id-1');
      expect(mockRepository.deleteMemory).toHaveBeenCalledWith('memory-id-1');
    });
  });
}); 