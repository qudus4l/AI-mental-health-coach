import { describe, expect, it, vi, beforeEach } from 'vitest';
import { LLMService, CBT_SYSTEM_PROMPT } from '../llm';
import { MessageRole, LLMResponse } from '../types';

// Mock OpenAI client
vi.mock('openai', () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      chat: {
        completions: {
          create: vi.fn()
        }
      }
    }))
  };
});

describe('LLM Service', () => {
  let llmService: LLMService;
  let mockCreateCompletion: any;

  const mockConfig = {
    apiKey: 'test-api-key',
    model: 'gpt-4',
    temperature: 0.5,
    maxTokens: 1000
  };

  const mockMessages = [
    {
      role: MessageRole.USER,
      content: 'I feel anxious about my upcoming presentation.'
    }
  ];

  const mockResponse: LLMResponse = {
    assistant: 'I understand that presentations can be anxiety-inducing. Let\'s explore what specific aspects worry you the most.',
    homework: 'Take 5 minutes before bed to write down your specific presentation concerns and one small step to address each one.',
    crisisFlag: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
    llmService = new LLMService(mockConfig);
    // Get reference to the mocked method
    mockCreateCompletion = (llmService as any).openai.chat.completions.create;
  });

  it('should initialize with the provided configuration', () => {
    expect((llmService as any).config.apiKey).toBe(mockConfig.apiKey);
    expect((llmService as any).config.model).toBe(mockConfig.model);
    expect((llmService as any).config.temperature).toBe(mockConfig.temperature);
    expect((llmService as any).config.maxTokens).toBe(mockConfig.maxTokens);
  });

  it('should use default values when not provided', () => {
    const partialConfig = {
      apiKey: 'test-api-key',
      model: 'gpt-4'
    };
    const service = new LLMService(partialConfig);
    expect((service as any).config.temperature).toBeDefined();
    expect((service as any).config.maxTokens).toBeDefined();
  });

  it('should process conversation and return properly formatted response', async () => {
    // Setup mock response
    mockCreateCompletion.mockResolvedValueOnce({
      choices: [
        {
          message: {
            content: JSON.stringify(mockResponse)
          }
        }
      ]
    });

    const result = await llmService.processConversation(mockMessages);

    // Verify the correct parameters were passed
    expect(mockCreateCompletion).toHaveBeenCalledWith({
      model: mockConfig.model,
      messages: [
        { role: 'system', content: CBT_SYSTEM_PROMPT },
        { role: 'user', content: mockMessages[0].content }
      ],
      temperature: mockConfig.temperature,
      max_tokens: mockConfig.maxTokens,
      response_format: { type: 'json_object' }
    });

    // Verify the result
    expect(result).toEqual(mockResponse);
  });

  it('should handle malformed JSON responses', async () => {
    // Setup mock response with invalid JSON
    mockCreateCompletion.mockResolvedValueOnce({
      choices: [
        {
          message: {
            content: 'Not a valid JSON response'
          }
        }
      ]
    });

    const result = await llmService.processConversation(mockMessages);

    // Verify fallback handling
    expect(result).toEqual({
      assistant: 'Not a valid JSON response',
      crisisFlag: false
    });
  });

  it('should throw an error when API call fails', async () => {
    mockCreateCompletion.mockRejectedValueOnce(new Error('API error'));

    await expect(llmService.processConversation(mockMessages)).rejects.toThrow('Failed to process conversation with AI coach');
  });

  it('should throw an error when response is empty', async () => {
    mockCreateCompletion.mockResolvedValueOnce({
      choices: [{ message: { content: null } }]
    });

    await expect(llmService.processConversation(mockMessages)).rejects.toThrow('No response content from LLM');
  });
}); 