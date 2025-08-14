"""
Conversation Management Layer for Dr. TARDIS

This module implements the conversation state management, dialogue control,
and personality components of Dr. TARDIS as defined in the architecture.
"""

import datetime
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set

# Define enums and types
class ModalityType(Enum):
    """Types of interaction modalities supported by Dr. TARDIS."""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    MULTIMODAL = "multimodal"

class SensitivityLevel(Enum):
    """Information sensitivity levels for security classification."""
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    SECRET = 4

class Intent(Enum):
    """User intent categories for conversation planning."""
    GENERAL_QUESTION = "general_question"
    TROUBLESHOOTING = "troubleshooting"
    INSTALLATION_HELP = "installation_help"
    FEATURE_INQUIRY = "feature_inquiry"
    ACCOUNT_ISSUE = "account_issue"
    FEEDBACK = "feedback"
    GREETING = "greeting"
    FAREWELL = "farewell"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    NEGATION = "negation"
    UNKNOWN = "unknown"

class EmotionalState(Enum):
    """Emotional states for tracking user sentiment."""
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    IMPATIENT = "impatient"
    APPRECIATIVE = "appreciative"
    ANGRY = "angry"

class ConversationTurn:
    """Represents a single turn in a conversation."""
    
    def __init__(
        self,
        user_input: str,
        system_response: str,
        timestamp: datetime.datetime,
        modality: ModalityType,
        intent: Intent,
        emotional_state: EmotionalState,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.user_input = user_input
        self.system_response = system_response
        self.timestamp = timestamp
        self.modality = modality
        self.intent = intent
        self.emotional_state = emotional_state
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation turn to a dictionary."""
        return {
            "user_input": self.user_input,
            "system_response": self.system_response,
            "timestamp": self.timestamp.isoformat(),
            "modality": self.modality.value,
            "intent": self.intent.value,
            "emotional_state": self.emotional_state.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create a conversation turn from a dictionary."""
        return cls(
            user_input=data["user_input"],
            system_response=data["system_response"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            modality=ModalityType(data["modality"]),
            intent=Intent(data["intent"]),
            emotional_state=EmotionalState(data["emotional_state"]),
            metadata=data.get("metadata", {})
        )

class ConversationContext:
    """Maintains the context of a conversation."""
    
    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        start_time: datetime.datetime,
        current_topic: Optional[str] = None,
        active_workflow: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        system_state: Optional[Dict[str, Any]] = None,
        history: Optional[List[ConversationTurn]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.start_time = start_time
        self.last_updated = start_time
        self.current_topic = current_topic
        self.active_workflow = active_workflow
        self.entities = entities or {}
        self.user_preferences = user_preferences or {}
        self.system_state = system_state or {}
        self.history = history or []
        self.metadata = metadata or {}
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the history."""
        self.history.append(turn)
        self.last_updated = turn.timestamp
    
    def get_recent_history(self, turns: int = 5) -> List[ConversationTurn]:
        """Get the most recent conversation turns."""
        return self.history[-turns:] if len(self.history) > 0 else []
    
    def update_entity(self, entity_name: str, entity_value: Any) -> None:
        """Update an entity in the context."""
        self.entities[entity_name] = entity_value
        self.last_updated = datetime.datetime.now()
    
    def get_entity(self, entity_name: str) -> Optional[Any]:
        """Get an entity from the context."""
        return self.entities.get(entity_name)
    
    def update_system_state(self, key: str, value: Any) -> None:
        """Update the system state."""
        self.system_state[key] = value
        self.last_updated = datetime.datetime.now()
    
    def get_system_state(self, key: str) -> Optional[Any]:
        """Get a value from the system state."""
        return self.system_state.get(key)
    
    def update_user_preference(self, preference: str, value: Any) -> None:
        """Update a user preference."""
        self.user_preferences[preference] = value
        self.last_updated = datetime.datetime.now()
    
    def get_user_preference(self, preference: str) -> Optional[Any]:
        """Get a user preference."""
        return self.user_preferences.get(preference)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation context to a dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "current_topic": self.current_topic,
            "active_workflow": self.active_workflow,
            "entities": self.entities,
            "user_preferences": self.user_preferences,
            "system_state": self.system_state,
            "history": [turn.to_dict() for turn in self.history],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create a conversation context from a dictionary."""
        return cls(
            conversation_id=data["conversation_id"],
            user_id=data["user_id"],
            start_time=datetime.datetime.fromisoformat(data["start_time"]),
            current_topic=data.get("current_topic"),
            active_workflow=data.get("active_workflow"),
            entities=data.get("entities", {}),
            user_preferences=data.get("user_preferences", {}),
            system_state=data.get("system_state", {}),
            history=[ConversationTurn.from_dict(turn) for turn in data.get("history", [])],
            metadata=data.get("metadata", {})
        )

class ResponseStrategy:
    """Defines a strategy for responding to user input."""
    
    def __init__(
        self,
        intent: Intent,
        response_type: str,
        priority_modalities: List[ModalityType],
        required_knowledge: List[str],
        workflow_id: Optional[str] = None,
        follow_up_questions: Optional[List[str]] = None,
        tone_guidance: Optional[str] = None,
        max_response_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.intent = intent
        self.response_type = response_type
        self.priority_modalities = priority_modalities
        self.required_knowledge = required_knowledge
        self.workflow_id = workflow_id
        self.follow_up_questions = follow_up_questions or []
        self.tone_guidance = tone_guidance
        self.max_response_length = max_response_length
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response strategy to a dictionary."""
        return {
            "intent": self.intent.value,
            "response_type": self.response_type,
            "priority_modalities": [m.value for m in self.priority_modalities],
            "required_knowledge": self.required_knowledge,
            "workflow_id": self.workflow_id,
            "follow_up_questions": self.follow_up_questions,
            "tone_guidance": self.tone_guidance,
            "max_response_length": self.max_response_length,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseStrategy':
        """Create a response strategy from a dictionary."""
        return cls(
            intent=Intent(data["intent"]),
            response_type=data["response_type"],
            priority_modalities=[ModalityType(m) for m in data["priority_modalities"]],
            required_knowledge=data["required_knowledge"],
            workflow_id=data.get("workflow_id"),
            follow_up_questions=data.get("follow_up_questions", []),
            tone_guidance=data.get("tone_guidance"),
            max_response_length=data.get("max_response_length"),
            metadata=data.get("metadata", {})
        )

class ProcessedInput:
    """Represents processed user input."""
    
    def __init__(
        self,
        raw_input: Any,
        modality_type: ModalityType,
        processed_text: str,
        detected_intent: Intent,
        confidence: float,
        entities: Dict[str, Any],
        emotional_state: EmotionalState,
        timestamp: datetime.datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.raw_input = raw_input
        self.modality_type = modality_type
        self.processed_text = processed_text
        self.detected_intent = detected_intent
        self.confidence = confidence
        self.entities = entities
        self.emotional_state = emotional_state
        self.timestamp = timestamp
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the processed input to a dictionary."""
        return {
            "processed_text": self.processed_text,
            "modality_type": self.modality_type.value,
            "detected_intent": self.detected_intent.value,
            "confidence": self.confidence,
            "entities": self.entities,
            "emotional_state": self.emotional_state.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_input: Any = None) -> 'ProcessedInput':
        """Create processed input from a dictionary."""
        return cls(
            raw_input=raw_input,
            modality_type=ModalityType(data["modality_type"]),
            processed_text=data["processed_text"],
            detected_intent=Intent(data["detected_intent"]),
            confidence=data["confidence"],
            entities=data["entities"],
            emotional_state=EmotionalState(data["emotional_state"]),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )

class ConversationStateManager:
    """Manages conversation state and context."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.conversations: Dict[str, ConversationContext] = {}
        self.storage_path = storage_path
    
    def create_conversation(self, user_id: str) -> ConversationContext:
        """Create a new conversation context."""
        conversation_id = str(uuid.uuid4())
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            start_time=datetime.datetime.now()
        )
        self.conversations[conversation_id] = context
        return context
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get a conversation context by ID."""
        return self.conversations.get(conversation_id)
    
    def get_user_conversations(self, user_id: str) -> List[ConversationContext]:
        """Get all conversations for a user."""
        return [
            context for context in self.conversations.values()
            if context.user_id == user_id
        ]
    
    def update_context(self, input_data: ProcessedInput, 
                      conversation_id: str) -> ConversationContext:
        """Update conversation context based on new input."""
        context = self.get_conversation(conversation_id)
        if not context:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Update entities from input
        for entity_name, entity_value in input_data.entities.items():
            context.update_entity(entity_name, entity_value)
        
        # Update system state based on input
        if input_data.metadata.get("system_state_updates"):
            for key, value in input_data.metadata["system_state_updates"].items():
                context.update_system_state(key, value)
        
        return context
    
    def retrieve_context(self, conversation_id: str, 
                        lookback_turns: int = 5) -> ConversationContext:
        """Retrieve context for a specific conversation."""
        context = self.get_conversation(conversation_id)
        if not context:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Create a copy with limited history
        limited_context = ConversationContext(
            conversation_id=context.conversation_id,
            user_id=context.user_id,
            start_time=context.start_time,
            current_topic=context.current_topic,
            active_workflow=context.active_workflow,
            entities=context.entities.copy(),
            user_preferences=context.user_preferences.copy(),
            system_state=context.system_state.copy(),
            history=context.get_recent_history(lookback_turns),
            metadata=context.metadata.copy()
        )
        
        return limited_context
    
    def merge_sessions(self, source_id: str, target_id: str) -> bool:
        """Merge conversation history from two sessions."""
        source = self.get_conversation(source_id)
        target = self.get_conversation(target_id)
        
        if not source or not target:
            return False
        
        # Merge history
        for turn in source.history:
            if turn not in target.history:
                target.history.append(turn)
        
        # Sort history by timestamp
        target.history.sort(key=lambda turn: turn.timestamp)
        
        # Merge entities
        for entity_name, entity_value in source.entities.items():
            if entity_name not in target.entities:
                target.entities[entity_name] = entity_value
        
        # Merge user preferences
        for pref_name, pref_value in source.user_preferences.items():
            if pref_name not in target.user_preferences:
                target.user_preferences[pref_name] = pref_value
        
        # Update last updated timestamp
        target.last_updated = datetime.datetime.now()
        
        return True
    
    def save_conversation(self, conversation_id: str) -> bool:
        """Save a conversation to storage."""
        if not self.storage_path:
            return False
        
        context = self.get_conversation(conversation_id)
        if not context:
            return False
        
        # Implementation for saving to storage would go here
        # This is a placeholder for the actual implementation
        return True
    
    def load_conversation(self, conversation_id: str) -> bool:
        """Load a conversation from storage."""
        if not self.storage_path:
            return False
        
        # Implementation for loading from storage would go here
        # This is a placeholder for the actual implementation
        return False

class IntentRecognizer:
    """Recognizes user intents from input."""
    
    def __init__(self):
        # Initialize intent recognition models or rules
        pass
    
    def recognize_intent(self, input_text: str, 
                        context: Optional[ConversationContext] = None) -> Tuple[Intent, float]:
        """Recognize intent from input text."""
        # This is a placeholder for actual intent recognition logic
        # In a real implementation, this would use NLP models or rules
        
        # Simple keyword-based intent recognition for demonstration
        input_lower = input_text.lower()
        
        # Check for greetings
        if any(greeting in input_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return Intent.GREETING, 0.9
        
        # Check for farewells
        if any(farewell in input_lower for farewell in ["bye", "goodbye", "see you", "farewell"]):
            return Intent.FAREWELL, 0.9
        
        # Check for troubleshooting
        if any(issue in input_lower for issue in ["problem", "issue", "error", "not working", "broken", "fix"]):
            return Intent.TROUBLESHOOTING, 0.8
        
        # Check for installation help
        if any(install in input_lower for install in ["install", "setup", "configure", "deployment"]):
            return Intent.INSTALLATION_HELP, 0.8
        
        # Check for feature inquiries
        if any(feature in input_lower for feature in ["how to", "feature", "capability", "can it", "does it"]):
            return Intent.FEATURE_INQUIRY, 0.7
        
        # Check for account issues
        if any(account in input_lower for account in ["account", "login", "password", "subscription"]):
            return Intent.ACCOUNT_ISSUE, 0.8
        
        # Check for feedback
        if any(feedback in input_lower for feedback in ["feedback", "suggest", "improve", "opinion"]):
            return Intent.FEEDBACK, 0.7
        
        # Check for clarification
        if any(clarify in input_lower for clarify in ["what do you mean", "clarify", "explain", "don't understand"]):
            return Intent.CLARIFICATION, 0.8
        
        # Check for confirmation
        if any(confirm in input_lower for confirm in ["yes", "correct", "right", "exactly", "sure"]):
            return Intent.CONFIRMATION, 0.9
        
        # Check for negation
        if any(negate in input_lower for negate in ["no", "not", "don't", "incorrect", "wrong"]):
            return Intent.NEGATION, 0.9
        
        # Default to general question
        return Intent.GENERAL_QUESTION, 0.5

class EmotionDetector:
    """Detects user emotional state from input."""
    
    def __init__(self):
        # Initialize emotion detection models or rules
        pass
    
    def detect_emotion(self, input_text: str, 
                      context: Optional[ConversationContext] = None) -> EmotionalState:
        """Detect emotional state from input text."""
        # This is a placeholder for actual emotion detection logic
        # In a real implementation, this would use sentiment analysis models
        
        # Simple keyword-based emotion detection for demonstration
        input_lower = input_text.lower()
        
        # Check for frustration
        if any(frustration in input_lower for frustration in ["frustrated", "annoying", "annoyed", "irritating", "not working"]):
            return EmotionalState.FRUSTRATED
        
        # Check for confusion
        if any(confusion in input_lower for confusion in ["confused", "don't understand", "unclear", "what do you mean"]):
            return EmotionalState.CONFUSED
        
        # Check for satisfaction
        if any(satisfaction in input_lower for satisfaction in ["great", "excellent", "perfect", "thanks", "thank you"]):
            return EmotionalState.SATISFIED
        
        # Check for impatience
        if any(impatience in input_lower for impatience in ["hurry", "quickly", "fast", "now", "immediately"]):
            return EmotionalState.IMPATIENT
        
        # Check for appreciation
        if any(appreciation in input_lower for appreciation in ["appreciate", "helpful", "useful", "good job"]):
            return EmotionalState.APPRECIATIVE
        
        # Check for anger
        if any(anger in input_lower for anger in ["angry", "furious", "terrible", "worst", "hate"]):
            return EmotionalState.ANGRY
        
        # Default to neutral
        return EmotionalState.NEUTRAL

class EntityExtractor:
    """Extracts entities from user input."""
    
    def __init__(self):
        # Initialize entity extraction models or rules
        pass
    
    def extract_entities(self, input_text: str, 
                        context: Optional[ConversationContext] = None) -> Dict[str, Any]:
        """Extract entities from input text."""
        # This is a placeholder for actual entity extraction logic
        # In a real implementation, this would use NER models or rules
        
        # Simple regex-based entity extraction for demonstration
        entities = {}
        
        # Extract version numbers
        import re
        version_match = re.search(r'version\s+(\d+\.\d+(\.\d+)?)', input_text, re.IGNORECASE)
        if version_match:
            entities["version"] = version_match.group(1)
        
        # Extract operating systems
        os_keywords = {
            "windows": ["windows", "win", "win10", "win11"],
            "macos": ["mac", "macos", "osx", "mac os"],
            "linux": ["linux", "ubuntu", "debian", "fedora", "centos"]
        }
        
        for os_name, keywords in os_keywords.items():
            if any(keyword in input_text.lower() for keyword in keywords):
                entities["operating_system"] = os_name
                break
        
        # Extract product names
        product_keywords = {
            "apexagent": ["apexagent", "apex agent", "agent"],
            "dr_tardis": ["dr tardis", "tardis", "dr. tardis", "doctor tardis"]
        }
        
        for product_name, keywords in product_keywords.items():
            if any(keyword in input_text.lower() for keyword in keywords):
                entities["product"] = product_name
                break
        
        return entities

class DialogueController:
    """Controls conversation flow and structure."""
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.emotion_detector = EmotionDetector()
        self.entity_extractor = EntityExtractor()
    
    def process_input(self, input_text: str, modality: ModalityType, 
                     context: Optional[ConversationContext] = None) -> ProcessedInput:
        """Process user input to extract intent, emotion, and entities."""
        intent, confidence = self.intent_recognizer.recognize_intent(input_text, context)
        emotion = self.emotion_detector.detect_emotion(input_text, context)
        entities = self.entity_extractor.extract_entities(input_text, context)
        
        return ProcessedInput(
            raw_input=input_text,
            modality_type=modality,
            processed_text=input_text,  # In a real implementation, this might be normalized
            detected_intent=intent,
            confidence=confidence,
            entities=entities,
            emotional_state=emotion,
            timestamp=datetime.datetime.now(),
            metadata={}
        )
    
    def plan_response(self, user_intent: Intent, 
                     context: ConversationContext) -> ResponseStrategy:
        """Plan a response strategy based on user intent and context."""
        # This is a placeholder for actual response planning logic
        # In a real implementation, this would use more sophisticated planning
        
        # Default modalities prioritize text first
        default_modalities = [ModalityType.TEXT]
        
        # Add voice if user has used voice before
        if any(turn.modality == ModalityType.VOICE for turn in context.history):
            default_modalities.append(ModalityType.VOICE)
        
        # Add video if user has used video before
        if any(turn.modality == ModalityType.VIDEO for turn in context.history):
            default_modalities.append(ModalityType.VIDEO)
        
        # Determine response type and required knowledge based on intent
        if user_intent == Intent.GREETING:
            return ResponseStrategy(
                intent=user_intent,
                response_type="greeting",
                priority_modalities=default_modalities,
                required_knowledge=["user_preferences"],
                tone_guidance="friendly and welcoming",
                follow_up_questions=["How can I assist you today?"]
            )
        
        elif user_intent == Intent.FAREWELL:
            return ResponseStrategy(
                intent=user_intent,
                response_type="farewell",
                priority_modalities=default_modalities,
                required_knowledge=["conversation_summary"],
                tone_guidance="friendly and appreciative"
            )
        
        elif user_intent == Intent.TROUBLESHOOTING:
            # Check if we have an active workflow
            if context.active_workflow:
                return ResponseStrategy(
                    intent=user_intent,
                    response_type="troubleshooting_continuation",
                    priority_modalities=default_modalities,
                    required_knowledge=["troubleshooting_guides", "system_state"],
                    workflow_id=context.active_workflow,
                    tone_guidance="helpful and clear"
                )
            else:
                return ResponseStrategy(
                    intent=user_intent,
                    response_type="troubleshooting_initiation",
                    priority_modalities=default_modalities,
                    required_knowledge=["problem_categories", "diagnostic_procedures"],
                    tone_guidance="empathetic and solution-oriented",
                    follow_up_questions=[
                        "Can you describe the issue in more detail?",
                        "When did you first notice this problem?",
                        "Have you tried any solutions already?"
                    ]
                )
        
        elif user_intent == Intent.INSTALLATION_HELP:
            return ResponseStrategy(
                intent=user_intent,
                response_type="installation_guide",
                priority_modalities=[ModalityType.TEXT, ModalityType.VIDEO],
                required_knowledge=["installation_guides", "system_requirements"],
                tone_guidance="clear and step-by-step",
                follow_up_questions=[
                    "What operating system are you using?",
                    "Which version of the software are you trying to install?"
                ]
            )
        
        elif user_intent == Intent.FEATURE_INQUIRY:
            return ResponseStrategy(
                intent=user_intent,
                response_type="feature_explanation",
                priority_modalities=default_modalities,
                required_knowledge=["feature_documentation", "usage_examples"],
                tone_guidance="informative and enthusiastic",
                follow_up_questions=[
                    "Would you like me to show you how to use this feature?",
                    "Are there specific aspects of this feature you're interested in?"
                ]
            )
        
        elif user_intent == Intent.ACCOUNT_ISSUE:
            return ResponseStrategy(
                intent=user_intent,
                response_type="account_support",
                priority_modalities=[ModalityType.TEXT],  # Limit to text for security
                required_knowledge=["account_procedures", "security_protocols"],
                tone_guidance="professional and secure",
                follow_up_questions=[
                    "What specific account issue are you experiencing?",
                    "Have you tried resetting your password?"
                ]
            )
        
        # Default strategy for other intents
        return ResponseStrategy(
            intent=user_intent,
            response_type="general_response",
            priority_modalities=default_modalities,
            required_knowledge=["general_knowledge", "faq"],
            tone_guidance="helpful and conversational",
            follow_up_questions=["Is there anything else you'd like to know?"]
        )
    
    def handle_interruption(self, current_strategy: ResponseStrategy, 
                           new_input: ProcessedInput) -> ResponseStrategy:
        """Adapt strategy when user interrupts current response."""
        # This is a placeholder for actual interruption handling logic
        
        # If the new input is a clarification request, modify the current strategy
        if new_input.detected_intent == Intent.CLARIFICATION:
            current_strategy.tone_guidance = "extra clear and simple"
            current_strategy.metadata["interrupted"] = True
            return current_strategy
        
        # If the new input is a negation, change course
        if new_input.detected_intent == Intent.NEGATION:
            current_strategy.response_type = "correction"
            current_strategy.metadata["interrupted"] = True
            current_strategy.metadata["requires_correction"] = True
            return current_strategy
        
        # For other interruptions, create a new strategy based on the new input
        # This would typically call plan_response with the new intent
        return current_strategy

class PersonalityEngine:
    """Implements the Dr. TARDIS persona and communication style."""
    
    def __init__(self):
        # Initialize personality traits and parameters
        self.base_traits = {
            "helpfulness": 0.9,  # Very helpful
            "formality": 0.6,    # Moderately formal
            "enthusiasm": 0.7,   # Fairly enthusiastic
            "technical_depth": 0.8,  # Quite technical
            "conciseness": 0.5,  # Balanced conciseness
            "empathy": 0.8,      # Highly empathetic
            "humor": 0.3         # Mild humor
        }
    
    def adapt_to_user(self, user_preferences: Dict[str, Any], 
                     emotional_state: EmotionalState) -> Dict[str, float]:
        """Adapt personality traits based on user preferences and emotional state."""
        adapted_traits = self.base_traits.copy()
        
        # Adapt based on user preferences
        if "formality_preference" in user_preferences:
            adapted_traits["formality"] = user_preferences["formality_preference"]
        
        if "technical_depth_preference" in user_preferences:
            adapted_traits["technical_depth"] = user_preferences["technical_depth_preference"]
        
        if "conciseness_preference" in user_preferences:
            adapted_traits["conciseness"] = user_preferences["conciseness_preference"]
        
        # Adapt based on emotional state
        if emotional_state == EmotionalState.FRUSTRATED:
            adapted_traits["empathy"] += 0.1
            adapted_traits["conciseness"] += 0.2  # More concise when user is frustrated
            adapted_traits["humor"] -= 0.2  # Less humor when user is frustrated
        
        elif emotional_state == EmotionalState.CONFUSED:
            adapted_traits["technical_depth"] -= 0.2  # Less technical when user is confused
            adapted_traits["conciseness"] -= 0.2  # More detailed when user is confused
        
        elif emotional_state == EmotionalState.IMPATIENT:
            adapted_traits["conciseness"] += 0.3  # Much more concise when user is impatient
            adapted_traits["formality"] -= 0.1  # Slightly less formal when user is impatient
        
        # Ensure traits stay within bounds
        for trait, value in adapted_traits.items():
            adapted_traits[trait] = max(0.0, min(1.0, value))
        
        return adapted_traits
    
    def generate_tone_guidance(self, traits: Dict[str, float], 
                              response_strategy: ResponseStrategy) -> str:
        """Generate tone guidance based on personality traits and response strategy."""
        guidance_elements = []
        
        # Base guidance from response strategy
        if response_strategy.tone_guidance:
            guidance_elements.append(response_strategy.tone_guidance)
        
        # Add trait-based guidance
        if traits["formality"] > 0.7:
            guidance_elements.append("formal and professional")
        elif traits["formality"] < 0.3:
            guidance_elements.append("casual and conversational")
        
        if traits["technical_depth"] > 0.7:
            guidance_elements.append("technically precise")
        elif traits["technical_depth"] < 0.3:
            guidance_elements.append("using simple terms")
        
        if traits["conciseness"] > 0.7:
            guidance_elements.append("concise and to-the-point")
        elif traits["conciseness"] < 0.3:
            guidance_elements.append("detailed and thorough")
        
        if traits["empathy"] > 0.7:
            guidance_elements.append("empathetic and understanding")
        
        if traits["enthusiasm"] > 0.7:
            guidance_elements.append("enthusiastic and energetic")
        
        if traits["humor"] > 0.7:
            guidance_elements.append("with appropriate humor")
        
        # Combine guidance elements
        return ", ".join(guidance_elements)
    
    def apply_personality(self, response_text: str, traits: Dict[str, float]) -> str:
        """Apply personality traits to modify response text."""
        # This is a placeholder for actual personality application logic
        # In a real implementation, this would use more sophisticated NLP techniques
        
        # For now, we'll just return the original text
        # In a real implementation, this would modify the text based on traits
        return response_text

class ConversationManager:
    """Main class that coordinates conversation management components."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.state_manager = ConversationStateManager(storage_path)
        self.dialogue_controller = DialogueController()
        self.personality_engine = PersonalityEngine()
    
    def process_user_input(self, user_input: str, modality: ModalityType, 
                          conversation_id: Optional[str] = None, 
                          user_id: str = "anonymous") -> Tuple[ProcessedInput, ConversationContext]:
        """Process user input and update conversation context."""
        # Get or create conversation context
        if conversation_id and self.state_manager.get_conversation(conversation_id):
            context = self.state_manager.get_conversation(conversation_id)
        else:
            context = self.state_manager.create_conversation(user_id)
            conversation_id = context.conversation_id
        
        # Process input
        processed_input = self.dialogue_controller.process_input(
            input_text=user_input,
            modality=modality,
            context=context
        )
        
        # Update context with processed input
        updated_context = self.state_manager.update_context(
            input_data=processed_input,
            conversation_id=conversation_id
        )
        
        return processed_input, updated_context
    
    def generate_response_strategy(self, processed_input: ProcessedInput, 
                                 context: ConversationContext) -> ResponseStrategy:
        """Generate a response strategy based on processed input and context."""
        # Check if we need to handle an interruption
        if context.metadata.get("active_response"):
            current_strategy = ResponseStrategy.from_dict(context.metadata["active_response"])
            return self.dialogue_controller.handle_interruption(current_strategy, processed_input)
        
        # Otherwise, plan a new response
        return self.dialogue_controller.plan_response(
            user_intent=processed_input.detected_intent,
            context=context
        )
    
    def apply_personality_to_strategy(self, strategy: ResponseStrategy, 
                                    context: ConversationContext) -> ResponseStrategy:
        """Apply personality traits to a response strategy."""
        # Get the most recent emotional state
        emotional_state = EmotionalState.NEUTRAL
        if context.history:
            emotional_state = context.history[-1].emotional_state
        
        # Adapt traits to user and emotional state
        adapted_traits = self.personality_engine.adapt_to_user(
            user_preferences=context.user_preferences,
            emotional_state=emotional_state
        )
        
        # Generate tone guidance
        tone_guidance = self.personality_engine.generate_tone_guidance(
            traits=adapted_traits,
            response_strategy=strategy
        )
        
        # Update strategy with new tone guidance
        strategy.tone_guidance = tone_guidance
        strategy.metadata["personality_traits"] = adapted_traits
        
        return strategy
    
    def record_interaction(self, user_input: str, system_response: str, 
                         processed_input: ProcessedInput, 
                         context: ConversationContext) -> None:
        """Record an interaction in the conversation history."""
        turn = ConversationTurn(
            user_input=user_input,
            system_response=system_response,
            timestamp=datetime.datetime.now(),
            modality=processed_input.modality_type,
            intent=processed_input.detected_intent,
            emotional_state=processed_input.emotional_state,
            metadata={
                "confidence": processed_input.confidence,
                "entities": processed_input.entities
            }
        )
        
        context.add_turn(turn)
        self.state_manager.save_conversation(context.conversation_id)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Generate a summary of a conversation."""
        context = self.state_manager.get_conversation(conversation_id)
        if not context:
            return {"error": "Conversation not found"}
        
        # Count turns
        turn_count = len(context.history)
        
        # Calculate duration
        if turn_count > 0:
            duration = context.history[-1].timestamp - context.start_time
            duration_minutes = duration.total_seconds() / 60
        else:
            duration_minutes = 0
        
        # Count intents
        intent_counts = {}
        for turn in context.history:
            intent_name = turn.intent.value
            intent_counts[intent_name] = intent_counts.get(intent_name, 0) + 1
        
        # Identify main topics
        topics = set()
        for entity_dict in [turn.metadata.get("entities", {}) for turn in context.history]:
            if "product" in entity_dict:
                topics.add(f"Product: {entity_dict['product']}")
            if "operating_system" in entity_dict:
                topics.add(f"OS: {entity_dict['operating_system']}")
        
        return {
            "conversation_id": conversation_id,
            "user_id": context.user_id,
            "start_time": context.start_time.isoformat(),
            "last_updated": context.last_updated.isoformat(),
            "turn_count": turn_count,
            "duration_minutes": round(duration_minutes, 2),
            "intent_distribution": intent_counts,
            "topics": list(topics),
            "active_workflow": context.active_workflow
        }
