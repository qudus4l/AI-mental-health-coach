"""Crisis detection service for the mental health coach application.

This module provides functionality for detecting potential crisis situations
in user messages and providing appropriate responses.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import re
from collections import Counter

# Crisis keywords grouped by category
CRISIS_KEYWORDS: Dict[str, List[str]] = {
    "suicide": [
        "suicide", "kill myself", "end my life", "take my own life", "no reason to live",
        "better off dead", "can't go on", "don't want to be alive", "want to die", 
        "die", "dying", "death", "fatal", "obituary", "sleeping forever",
    ],
    "self_harm": [
        "cut myself", "cutting myself", "self-harm", "self harm", "hurt myself", 
        "injure myself", "harm myself", "self-injury", "self injury", "hurting myself",
        "injuring myself", "harming myself", "self-mutilation", "self mutilation",
        "burn myself", "burning myself", "punish myself", "punishing myself",
    ],
    "severe_depression": [
        "hopeless", "worthless", "empty", "can't feel anything", "severe depression",
        "deeply depressed", "no purpose", "burden to others", "nothing matters",
        "pointless", "helpless", "trapped", "desperate", "miserable", "unbearable",
    ],
    "severe_anxiety": [
        "panic attack", "can't breathe", "heart racing", "terrified", "constant worry",
        "overwhelming anxiety", "paralyzed with fear", "can't control thoughts",
        "extreme worry", "catastrophic", "doom", "impending doom", "terrifying",
    ],
    "substance_abuse": [
        "overdose", "alcohol problem", "drug problem", "addiction", "substance abuse",
        "drinking too much", "can't stop using", "withdrawal", "relapse", "too many pills",
        "using again", "binge drinking", "blackout", "drunk", "high",
    ],
    "domestic_violence": [
        "abusive relationship", "domestic violence", "partner hurts me", "afraid of partner",
        "threatened me", "physical abuse", "emotional abuse", "controlling partner",
        "violent partner", "unsafe at home", "partner hits", "intimate partner violence",
    ],
    "child_abuse": [
        "child abuse", "abused as a child", "molested", "sexually abused", "hurt a child",
        "child in danger", "child neglect", "harm to children", "underage abuse",
    ],
}

# Emergency resources by category
EMERGENCY_RESOURCES: Dict[str, List[Dict[str, str]]] = {
    "general": [
        {
            "name": "Emergency Services",
            "contact": "911",
            "description": "Call for immediate emergency assistance",
        },
        {
            "name": "Crisis Text Line",
            "contact": "Text HOME to 741741",
            "description": "24/7 crisis support via text message",
        },
    ],
    "suicide": [
        {
            "name": "National Suicide Prevention Lifeline",
            "contact": "1-800-273-8255",
            "description": "24/7 support for people in suicidal crisis",
        },
        {
            "name": "988 Suicide & Crisis Lifeline",
            "contact": "988",
            "description": "Call or text 988 for mental health crisis support",
        },
    ],
    "self_harm": [
        {
            "name": "Self-harm Crisis Text Line",
            "contact": "Text HOME to 741741",
            "description": "24/7 support for self-harm issues",
        },
        {
            "name": "S.A.F.E. Alternatives",
            "contact": "1-800-DONT-CUT",
            "description": "Treatment for self-harm behavior",
        },
    ],
    "substance_abuse": [
        {
            "name": "SAMHSA's National Helpline",
            "contact": "1-800-662-HELP (4357)",
            "description": "Treatment referral and information service for substance abuse",
        },
        {
            "name": "Alcoholics Anonymous",
            "contact": "https://www.aa.org/",
            "description": "Support for alcohol addiction recovery",
        },
    ],
    "domestic_violence": [
        {
            "name": "National Domestic Violence Hotline",
            "contact": "1-800-799-SAFE (7233)",
            "description": "24/7 support for domestic violence victims",
        },
    ],
    "child_abuse": [
        {
            "name": "Childhelp National Child Abuse Hotline",
            "contact": "1-800-4-A-CHILD (1-800-422-4453)",
            "description": "24/7 hotline for child abuse situations",
        },
    ],
}


class CrisisDetector:
    """Detector for crisis situations in messages.
    
    This class provides functionality to analyze text for potential crisis
    indicators and provides appropriate emergency resources.
    """

    def __init__(
        self,
        crisis_keywords: Optional[Dict[str, List[str]]] = None,
        emergency_resources: Optional[Dict[str, List[Dict[str, str]]]] = None,
    ) -> None:
        """Initialize the crisis detector.
        
        Args:
            crisis_keywords: Dictionary mapping crisis categories to keyword lists.
                Defaults to the predefined CRISIS_KEYWORDS.
            emergency_resources: Dictionary mapping crisis categories to resource lists.
                Defaults to the predefined EMERGENCY_RESOURCES.
        """
        self.crisis_keywords = crisis_keywords or CRISIS_KEYWORDS
        self.emergency_resources = emergency_resources or EMERGENCY_RESOURCES
    
    def detect_crisis(
        self, message: str, message_history: Optional[List[str]] = None, user_profile: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], List[Dict[str, str]], Dict[str, Any]]:
        """Detect potential crisis indicators in a message with enhanced context awareness.
        
        Args:
            message: The message to analyze.
            message_history: Optional list of previous messages for context.
            user_profile: Optional user profile data for personalized detection.
            
        Returns:
            Tuple containing:
                - Boolean indicating if a crisis was detected
                - List of detected crisis categories
                - List of relevant emergency resources
                - Dictionary with additional analysis details
        """
        message = message.lower()
        detected_categories = []
        
        # Basic keyword detection (same as before)
        for category, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    detected_categories.append(category)
                    break
        
        # Specific check for self-harm with more flexible matching
        if "self_harm" not in detected_categories:
            if "hurt" in message and ("myself" in message or "self" in message):
                detected_categories.append("self_harm")
            elif "harm" in message and ("myself" in message or "self" in message):
                detected_categories.append("self_harm")
        
        # Enhanced detection: Pattern recognition
        additional_analysis = self._perform_advanced_analysis(message, message_history, user_profile)
        
        # Check for context patterns that might indicate crisis
        context_categories = additional_analysis.get("context_categories", [])
        for category in context_categories:
            if category not in detected_categories:
                detected_categories.append(category)
        
        # If no crisis detected
        if not detected_categories:
            return False, [], [], additional_analysis
        
        # Get relevant resources
        resources = self.get_resources(detected_categories)
        
        return True, detected_categories, resources, additional_analysis
    
    def _perform_advanced_analysis(
        self, message: str, message_history: Optional[List[str]] = None, user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform advanced analysis on the message to detect subtle crisis indicators.
        
        Args:
            message: The message to analyze.
            message_history: Optional list of previous messages for context.
            user_profile: Optional user profile data for personalized detection.
            
        Returns:
            Dictionary containing analysis results.
        """
        analysis_results = {
            "context_categories": [],
            "pattern_matches": [],
            "risk_level": "low",
            "confidence_score": 0.0,
        }
        
        # Pattern matching for indirect expressions of suicidal intent
        indirect_suicide_patterns = [
            r"(don't|won't|can't) be (here|around) (anymore|much longer)",
            r"(saying|say) goodbye",
            r"(this|it) (is|will be) (my last|the last)",
            r"(leave|leaving) (this world|everything behind)",
            r"(tired|exhausted|done) (of|with) (living|life|everything)",
        ]
        
        for pattern in indirect_suicide_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                analysis_results["pattern_matches"].append(pattern)
                if "suicide" not in analysis_results["context_categories"]:
                    analysis_results["context_categories"].append("suicide")
        
        # Check for combination of concerning words
        concerning_combinations = [
            (["plan", "die"], "suicide"),
            (["hurt", "myself", "again"], "self_harm"),
            (["no", "hope", "future"], "severe_depression"),
            (["afraid", "home", "hurt"], "domestic_violence"),
        ]
        
        for word_set, category in concerning_combinations:
            if all(word in message for word in word_set):
                if category not in analysis_results["context_categories"]:
                    analysis_results["context_categories"].append(category)
        
        # Analyze message history for patterns if available
        if message_history and len(message_history) > 0:
            # Join recent history with current message
            full_text = " ".join(message_history[-5:] + [message])
            
            # Count crisis keywords in recent history
            crisis_word_count = 0
            all_crisis_words = [word for category_words in self.crisis_keywords.values() for word in category_words]
            for word in all_crisis_words:
                if word in full_text:
                    crisis_word_count += 1
            
            # If there's a high density of crisis words across messages, escalate risk
            if crisis_word_count >= 3:
                analysis_results["risk_level"] = "medium"
                analysis_results["confidence_score"] = 0.6
            
            # Detect rapid deterioration in mood
            mood_words_neg = ["worse", "harder", "difficult", "struggling", "can't", "terrible"]
            mood_words_pos = ["better", "improving", "hopeful", "managing", "coping", "good"]
            
            neg_count = sum(word in full_text for word in mood_words_neg)
            pos_count = sum(word in full_text for word in mood_words_pos)
            
            # If negative mood words vastly outnumber positive ones, this could indicate deterioration
            if neg_count > 3 and neg_count > pos_count * 2:
                analysis_results["risk_level"] = "medium"
                analysis_results["confidence_score"] = max(analysis_results["confidence_score"], 0.65)
        
        # Consider user profile risk factors if available
        if user_profile:
            # Check for high baseline depression/anxiety scores
            depression_score = user_profile.get("depression_score", 0)
            anxiety_score = user_profile.get("anxiety_score", 0)
            
            if depression_score and depression_score >= 8:  # High depression score
                if "severe_depression" in analysis_results["context_categories"]:
                    analysis_results["risk_level"] = "high"
                    analysis_results["confidence_score"] = max(analysis_results["confidence_score"], 0.8)
            
            if anxiety_score and anxiety_score >= 8:  # High anxiety score
                if "severe_anxiety" in analysis_results["context_categories"]:
                    analysis_results["risk_level"] = "high"
                    analysis_results["confidence_score"] = max(analysis_results["confidence_score"], 0.7)
        
        # Set confidence based on direct keyword matches
        if len(analysis_results["context_categories"]) > 0:
            analysis_results["confidence_score"] = max(analysis_results["confidence_score"], 0.75)
            analysis_results["risk_level"] = max(analysis_results["risk_level"], "medium", key=self._risk_level_order)
        
        return analysis_results
    
    def _risk_level_order(self, level: str) -> int:
        """Helper function to order risk levels.
        
        Args:
            level: Risk level string.
            
        Returns:
            Integer representing the risk level order.
        """
        order = {"low": 0, "medium": 1, "high": 2}
        return order.get(level, 0)
    
    def get_resources(self, categories: List[str]) -> List[Dict[str, str]]:
        """Get emergency resources for the detected crisis categories.
        
        Args:
            categories: List of detected crisis categories.
            
        Returns:
            List of relevant emergency resources.
        """
        resources = []
        
        # Always include general resources
        for resource in self.emergency_resources.get("general", []):
            resources.append(resource)
        
        # Add category-specific resources
        for category in categories:
            for resource in self.emergency_resources.get(category, []):
                if resource not in resources:  # Avoid duplicates
                    resources.append(resource)
        
        return resources
    
    def get_crisis_response(self, categories: List[str], analysis_details: Dict[str, Any] = None) -> str:
        """Generate an appropriate response for the detected crisis.
        
        Args:
            categories: List of detected crisis categories.
            analysis_details: Optional additional analysis details.
            
        Returns:
            String containing a supportive crisis response.
        """
        # Start with a general response
        response = (
            "I notice you're expressing some thoughts that concern me. "
            "Your safety and well-being are important. "
            "Remember that there are people who can help, and "
            "reaching out to a mental health professional is a good step. "
        )
        
        # Add category-specific responses
        if "suicide" in categories:
            response += (
                "I'm especially concerned about your safety right now. "
                "Please consider calling a crisis helpline immediately. "
                "They are trained to help with thoughts of suicide and can provide immediate support. "
            )
        
        if "self_harm" in categories:
            response += (
                "Self-harm is a serious concern, and there are healthier ways to cope with difficult feelings. "
                "Please reach out to a mental health professional who can help you develop safer coping strategies. "
            )
        
        if "severe_depression" in categories:
            response += (
                "Depression can be overwhelming, but professional support can make a significant difference. "
                "A therapist or counselor can help you work through these feelings. "
            )
        
        if "substance_abuse" in categories:
            response += (
                "Substance use concerns can be addressed with the right support. "
                "There are specialized resources available to help with recovery and healing. "
            )
        
        if "domestic_violence" in categories:
            response += (
                "Your safety at home is paramount. There are confidential services "
                "that can help you create a safety plan and provide support. "
            )
        
        if "child_abuse" in categories:
            response += (
                "Child safety is critically important. There are dedicated services "
                "that can provide guidance and support in these situations. "
            )
        
        # Add risk-level specific guidance if available
        if analysis_details and "risk_level" in analysis_details:
            risk_level = analysis_details.get("risk_level")
            
            if risk_level == "high":
                response += (
                    "Based on what you've shared, I strongly encourage you to reach out for professional help right away. "
                    "This is not something you need to handle alone, and immediate support is available. "
                )
            elif risk_level == "medium":
                response += (
                    "It sounds like you're going through a really difficult time. "
                    "Please consider speaking with a mental health professional soon about what you're experiencing. "
                )
        
        # Add a closing statement with the resources introduction
        response += (
            "Below I'm providing some resources that might be helpful. "
            "Please consider reaching out to one of them for professional support:\n\n"
        )
        
        return response
    
    def format_resources(self, resources: List[Dict[str, str]]) -> str:
        """Format emergency resources into a readable string.
        
        Args:
            resources: List of resource dictionaries.
            
        Returns:
            Formatted string with resource information.
        """
        if not resources:
            return ""
        
        formatted = "Emergency Resources:\n\n"
        
        for resource in resources:
            formatted += f"• {resource['name']}\n"
            formatted += f"  {resource['contact']}\n"
            formatted += f"  {resource['description']}\n\n"
        
        return formatted
    
    def get_historical_crisis_indicators(self, message_history: List[str]) -> Dict[str, Any]:
        """Analyze message history for crisis patterns over time.
        
        Args:
            message_history: List of previous messages.
            
        Returns:
            Dictionary containing historical analysis results.
        """
        if not message_history:
            return {"pattern_found": False}
        
        # Flatten all crisis keywords into a single list
        all_crisis_words = [word for category_words in self.crisis_keywords.values() for word in category_words]
        
        # Count occurrences of crisis keywords in each message
        crisis_word_counts = []
        for msg in message_history:
            count = sum(1 for word in all_crisis_words if word in msg.lower())
            crisis_word_counts.append(count)
        
        # Check for increasing pattern of crisis keywords
        increasing_pattern = False
        if len(crisis_word_counts) >= 3:
            # Check if there's a consistent increase in the last few messages
            if all(crisis_word_counts[-i] <= crisis_word_counts[-i+1] for i in range(3, 1, -1)):
                increasing_pattern = True
        
        # Check for persistence of specific categories
        category_persistence = {}
        for category, keywords in self.crisis_keywords.items():
            category_hits = []
            for msg in message_history:
                msg_lower = msg.lower()
                category_hit = any(keyword in msg_lower for keyword in keywords)
                category_hits.append(category_hit)
            
            # Calculate the percentage of messages containing this category
            persistence_rate = sum(category_hits) / len(category_hits) if category_hits else 0
            category_persistence[category] = persistence_rate
        
        # Identify persistent categories (mentioned in at least 30% of messages)
        persistent_categories = [
            category for category, rate in category_persistence.items() if rate >= 0.3
        ]
        
        return {
            "pattern_found": increasing_pattern or len(persistent_categories) > 0,
            "increasing_pattern": increasing_pattern,
            "persistent_categories": persistent_categories,
            "category_persistence": category_persistence,
        } 