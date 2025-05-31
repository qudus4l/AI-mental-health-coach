"""Crisis detection service for the mental health coach application.

This module provides functionality for detecting potential crisis situations
in user messages and providing appropriate responses.
"""

from typing import Dict, List, Optional, Set, Tuple

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
    
    def detect_crisis(self, message: str) -> Tuple[bool, List[str], List[Dict[str, str]]]:
        """Detect potential crisis indicators in a message.
        
        Args:
            message: The message to analyze.
            
        Returns:
            Tuple containing:
                - Boolean indicating if a crisis was detected
                - List of detected crisis categories
                - List of relevant emergency resources
        """
        message = message.lower()
        detected_categories = []
        
        # Check each category for keyword matches
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
        
        # If no crisis detected
        if not detected_categories:
            return False, [], []
        
        # Get relevant resources
        resources = self.get_resources(detected_categories)
        
        return True, detected_categories, resources
    
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
    
    def get_crisis_response(self, categories: List[str]) -> str:
        """Generate an appropriate response for the detected crisis.
        
        Args:
            categories: List of detected crisis categories.
            
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