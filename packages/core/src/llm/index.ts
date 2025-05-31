/**
 * LLM service for interacting with OpenAI API
 */
import OpenAI from 'openai';
import { MessageRole, LLMResponse } from '../types';

/**
 * System prompt for the AI mental health coach using CBT techniques
 */
export const CBT_SYSTEM_PROMPT = `You are an AI mental-health coach. Respond with empathetic CBT techniques, ask Socratic questions, and end with a brief actionable homework suggestion when appropriate. If the user expresses crisis language, set \`crisisFlag=true\` in the JSON response but **do not** attempt advanced crisis handling yet.`;

/**
 * Configuration options for the LLM service
 */
export interface LLMServiceConfig {
  apiKey: string;
  model: string;
  temperature?: number;
  maxTokens?: number;
}

/**
 * Message format for OpenAI API
 */
interface ChatMessage {
  role: string;
  content: string;
}

/**
 * LLM service for handling conversation with the OpenAI API
 */
export class LLMService {
  private openai: OpenAI;
  private config: LLMServiceConfig;

  /**
   * Creates a new LLM service instance
   * 
   * @param config - Configuration options for the service
   */
  constructor(config: LLMServiceConfig) {
    this.config = {
      temperature: 0.7,
      maxTokens: 1500,
      ...config
    };

    this.openai = new OpenAI({
      apiKey: this.config.apiKey
    });
  }

  /**
   * Processes a conversation using the OpenAI API
   * 
   * @param messages - Array of messages in the conversation
   * @returns The LLM response with assistant message, optional homework, and crisis flag
   */
  public async processConversation(messages: { role: MessageRole; content: string }[]): Promise<LLMResponse> {
    try {
      const formattedMessages: ChatMessage[] = [
        { role: 'system', content: CBT_SYSTEM_PROMPT },
        ...messages.map(msg => ({
          role: msg.role.toLowerCase(),
          content: msg.content
        }))
      ];

      const response = await this.openai.chat.completions.create({
        model: this.config.model,
        messages: formattedMessages,
        temperature: this.config.temperature,
        max_tokens: this.config.maxTokens,
        response_format: { type: 'json_object' }
      });

      const content = response.choices[0]?.message.content;
      
      if (!content) {
        throw new Error('No response content from LLM');
      }
      
      try {
        const parsedResponse = JSON.parse(content) as LLMResponse;
        return {
          assistant: parsedResponse.assistant || '',
          homework: parsedResponse.homework || undefined,
          crisisFlag: parsedResponse.crisisFlag || false
        };
      } catch (e) {
        console.error('Failed to parse LLM response as JSON:', e);
        return {
          assistant: content,
          crisisFlag: false
        };
      }
    } catch (error) {
      console.error('Error processing conversation with LLM:', error);
      throw new Error('Failed to process conversation with AI coach');
    }
  }
} 