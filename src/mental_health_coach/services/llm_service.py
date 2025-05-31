"""LLM service for the mental health coach application.

This module provides integration with OpenAI's API to generate
responses for the mental health coach using the gpt-4.1-mini-2025-04-14 model.
"""

from typing import Dict, List, Optional, Any
import os
import logging
from openai import OpenAI

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message

# Configure logging
logger = logging.getLogger(__name__)

# Default system prompt for the mental health coach
DEFAULT_SYSTEM_PROMPT = """
# ROLE
You are “Ami,” an AI mental-health *coach* (not a therapist) for adults (18-35) with mild-to-moderate anxiety or depression.  
You use Cognitive-Behavioral Therapy (CBT) and other evidence-based skills to teach coping strategies and track progress.

# COMMUNICATION DNA
• Warm, empathetic, concise • Professional but friendly  
• Non-judgmental • Encouraging and strengths-focused

# CORE TOOLKIT
1. Psycho-education (explain CBT concepts plainly)  
2. Socratic questioning & cognitive restructuring  
3. Behavioral activation & exposure hierarchies  
4. Grounding / mindfulness / breathing skills  
5. Goal setting, homework, and progress review

# SAFETY & BOUNDARIES
• **Do NOT**: diagnose, prescribe, or claim to treat.  
• **If user is in crisis** → Immediately activate “Crisis Protocol” (see Crisis section).  
• Provide local emergency numbers when country is known.  
• Maintain confidentiality and remind users of AI limitations.

# SESSION MODES
| Mode       | Trigger                               | Structure                                                |
|------------|---------------------------------------|----------------------------------------------------------|
| **Formal** | Scheduled session or `SESSION_MODE = formal` | 1 Check-in & homework ✔ → 2 Topic deep-dive → 3 Skill practice → 4 Summary & new homework |
| **Casual** | Any time outside scheduled sessions   | Flexible, conversational; still evidence-based and safe  |

# INTERACTION RULES
1. Ask clarifying questions when unsure.  
2. Offer concrete, step-by-step coping ideas.  
3. Encourage self-reflection and celebrate progress.  
4. Reference past sessions when helpful (see Memory API).  
5. Finish each formal session with a concise summary and homework.

# CRISIS PROTOCOL (outline only—full details injected by context prompt)
If `CRISIS_FLAG = true`:  
a) Express empathy and calm. b) Assess immediate safety.  
c) Provide emergency resources & stay with user until stable or help arrives.

# OUTPUT STYLE
Default to short paragraphs or bullet lists. Use plain language; avoid jargon unless user requests depth.  

"""


class LLMService:
    """Service for generating responses using OpenAI's LLM.
    
    Attributes:
        client: OpenAI client for API access.
        model: Name of the model to use.
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the LLM service.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to use OPENAI_API_KEY from environment.
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key not provided and OPENAI_API_KEY not set in environment")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1-mini-2025-04-14"
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]], 
        relevant_memories: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        is_formal_session: bool = False,
        crisis_detected: bool = False,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate a response to a user message.
        
        Args:
            user_message: The user's message to respond to.
            conversation_history: List of previous messages in the conversation.
            relevant_memories: Optional list of relevant memories to include in context.
            user_profile: Optional user profile information.
            is_formal_session: Whether this is a formal therapy session.
            crisis_detected: Whether a crisis was detected in the message.
            system_prompt: Optional custom system prompt to use.
            
        Returns:
            The generated response text.
        """
        # Build the message list for the API call
        messages = []
        
        # System prompt
        if system_prompt is None:
            system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # Add context about conversation type
        if is_formal_session:
            system_prompt += """\n\n

            SESSION_MODE = formal

            This is a scheduled 30–45 min therapeutic coaching session.  
            Follow the “Formal” structure in the system prompt exactly, enforce time boundaries gently, and confirm homework at start and end.
            
            """
        else:
            system_prompt += """\n\n

            SESSION_MODE = casual

            This is a spontaneous support chat.  
            Be flexible and conversational while still applying evidence-based techniques.  
            If the user requests a mini-session or shows crisis signals, switch modes accordingly.

            """
        
        # Add crisis awareness if detected
        if crisis_detected:
            system_prompt += """\n\n

            CRISIS_FLAG = true

            ⚠️  The user may be in acute distress (e.g., suicidal thoughts, self-harm intent, or severe panic).  
            Immediately execute the “Crisis Protocol” steps defined in the system prompt:

            1. Empathic acknowledgement (“I’m really sorry you’re feeling this way…”).  
            2. Direct safety assessment (ask about intent, plan, means, timeframe).  
            3. Offer grounding technique or breathing exercise.  
            4. Share **local** hotline / emergency numbers and encourage reaching out now.  
            5. Stay present and continue supportive dialogue until the user confirms they are safe or professional help has been contacted.  
            6. *Do not* discuss non-crisis topics until safety is established.

            """
        
        # Add system prompt
        messages.append({"role": "system", "content": system_prompt})
        
        # Add user profile if available
        if user_profile:
            profile_text = "User Profile Information:\n"
            for key, value in user_profile.items():
                profile_text += f"- {key}: {value}\n"
            
            messages.append({"role": "system", "content": profile_text})
        
        # Add relevant memories if available
        if relevant_memories and len(relevant_memories) > 0:
            memory_text = "Relevant Information from Past Conversations:\n"
            for memory in relevant_memories:
                if "text" in memory:
                    memory_text += f"- {memory['text']}\n"
                elif "content" in memory:
                    memory_text += f"- {memory['content']}\n"
            
            messages.append({"role": "system", "content": memory_text})
        
        # Add conversation history
        for message in conversation_history:
            role = "user" if message.get("is_from_user", False) else "assistant"
            content = message.get("content", "")
            messages.append({"role": role, "content": content})
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again later."
    
    def extract_important_memory(
        self,
        conversation_history: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Extract important memories from a conversation.
        
        Args:
            conversation_history: List of messages in the conversation.
            user_profile: Optional user profile information.
            
        Returns:
            Dictionary with memory content, category, and importance score, or None if no memory found.
        """
        # Build the memory extraction prompt
        system_prompt = """
        You are Ami, an AI mental-health coach reviewing the last user–assistant exchange.

        TASK
        • Decide if there is a single, therapeutically important item to save to long-term memory (e.g., new trigger, coping win, goal, insight, or measurable progress).

        OUTPUT (MUST be valid JSON **only**, no extra text):
        {
        "content": "<insight text or null>",
        "category": "<triggers | coping_strategies | goals | insights | progress | null>",
        "importance_score": <float 0.1-1.0>    // higher = more important
        }

        RULES
        • If nothing is worth saving, set `"content": null`, `"category": null`, `"importance_score": 0.0`.  
        • Do **not** include any keys besides the three specified.  
        • Keep `content` under 100 characters.  
        • Never reveal private user data beyond what is necessary for therapeutic continuity.

        """
        
        # Prepare messages for the API call
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        
        # Add user profile if available
        if user_profile:
            profile_text = "User Profile Information:\n"
            for key, value in user_profile.items():
                profile_text += f"- {key}: {value}\n"
            
            messages.append({"role": "system", "content": profile_text})
        
        # Add conversation history
        conversation_text = "Conversation History:\n"
        for message in conversation_history:
            sender = "User" if message.get("is_from_user", False) else "Coach"
            content = message.get("content", "")
            conversation_text += f"{sender}: {content}\n"
        
        messages.append({"role": "user", "content": conversation_text})
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Parse the JSON response
            import json
            memory_data = json.loads(result)
            
            # Check if a memory was found
            if memory_data.get("content") is None:
                return None
            
            return memory_data
        
        except Exception as e:
            logger.error(f"Error extracting memory: {str(e)}")
            return None 