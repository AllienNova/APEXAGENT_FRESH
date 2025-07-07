"""
Dr. TARDIS Main System Module

This module integrates all components of Dr. TARDIS (Technical Assistance, Remote Diagnostics, 
and Interactive Support) and provides the main entry points for the system.
"""

import asyncio
import datetime
import json
import logging
import os
import sys
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set, Union, AsyncGenerator, Callable

# Import core components
from dr_tardis.core.conversation_manager import (
    ConversationManager, 
    ConversationState,
    DialogueContext,
    PersonalityProfile
)
from dr_tardis.core.knowledge_engine import (
    KnowledgeEngine,
    KnowledgeQuery,
    KnowledgeSource,
    DiagnosticProcedure
)
from dr_tardis.core.multimodal_interaction import (
    MultimodalInteractionLayer,
    ModalityType,
    ProcessedInput,
    MultimodalOutput,
    ResourceConstraints
)
from dr_tardis.core.diagnostic_engine import (
    DiagnosticEngine,
    ProblemAnalysis,
    DiagnosticWorkflow,
    Solution
)

# Import integration components
from dr_tardis.integration.gemini_live_integration import (
    DrTardisGeminiIntegration,
    GeminiLiveMode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dr_tardis.log')
    ]
)

logger = logging.getLogger('dr_tardis')

class DrTardisSystem:
    """Main system class for Dr. TARDIS."""
    
    def __init__(self, config_path: str = None):
        """Initialize Dr. TARDIS system with configuration."""
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
        
        # Active user sessions
        self.active_sessions = {}
        
        logger.info("Dr. TARDIS system initialized")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
            "knowledge_base_path": os.environ.get("KNOWLEDGE_BASE_PATH", "./knowledge"),
            "diagnostic_procedures_path": os.environ.get("DIAGNOSTIC_PROCEDURES_PATH", "./procedures"),
            "log_level": os.environ.get("LOG_LEVEL", "INFO"),
            "default_personality": "helpful",
            "max_inactive_time": 3600,  # 1 hour
            "default_modalities": ["TEXT", "IMAGE"],
            "enable_voice": True,
            "enable_video": False,
            "security": {
                "require_authentication": True,
                "session_timeout": 1800,  # 30 minutes
                "max_failed_attempts": 5
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
        
        return default_config
    
    def _initialize_components(self):
        """Initialize all system components."""
        # Set log level
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logger.setLevel(log_level)
        
        # Initialize core components
        self.conversation_manager = ConversationManager()
        self.knowledge_engine = KnowledgeEngine(self.config["knowledge_base_path"])
        self.multimodal_layer = MultimodalInteractionLayer()
        self.diagnostic_engine = DiagnosticEngine()
        
        # Initialize integration components
        self.gemini_integration = DrTardisGeminiIntegration(self.config["gemini_api_key"])
        
        # Initialize default personality profiles
        self._initialize_personality_profiles()
        
        # Load diagnostic procedures
        self._load_diagnostic_procedures()
    
    def _initialize_personality_profiles(self):
        """Initialize default personality profiles."""
        # Create default profiles
        helpful_profile = PersonalityProfile(
            profile_id="helpful",
            name="Helpful Assistant",
            traits={
                "formality": 0.5,  # Moderate formality
                "empathy": 0.8,    # High empathy
                "technical_detail": 0.7,  # Moderately technical
                "conciseness": 0.5,  # Balanced conciseness
                "humor": 0.3       # Light humor
            },
            voice_characteristics={
                "pace": "moderate",
                "tone": "warm",
                "pitch": "medium"
            }
        )
        
        technical_profile = PersonalityProfile(
            profile_id="technical",
            name="Technical Expert",
            traits={
                "formality": 0.7,  # Higher formality
                "empathy": 0.4,    # Lower empathy
                "technical_detail": 0.9,  # Very technical
                "conciseness": 0.8,  # More concise
                "humor": 0.1       # Minimal humor
            },
            voice_characteristics={
                "pace": "measured",
                "tone": "authoritative",
                "pitch": "medium-low"
            }
        )
        
        friendly_profile = PersonalityProfile(
            profile_id="friendly",
            name="Friendly Guide",
            traits={
                "formality": 0.3,  # Less formal
                "empathy": 0.9,    # Very empathetic
                "technical_detail": 0.5,  # Moderate technical detail
                "conciseness": 0.4,  # More verbose
                "humor": 0.6       # More humor
            },
            voice_characteristics={
                "pace": "relaxed",
                "tone": "friendly",
                "pitch": "medium-high"
            }
        )
        
        # Register profiles with conversation manager
        self.conversation_manager.register_personality_profile(helpful_profile)
        self.conversation_manager.register_personality_profile(technical_profile)
        self.conversation_manager.register_personality_profile(friendly_profile)
    
    def _load_diagnostic_procedures(self):
        """Load diagnostic procedures from the configured path."""
        procedures_path = self.config["diagnostic_procedures_path"]
        if os.path.exists(procedures_path):
            try:
                # This is a placeholder for actual procedure loading
                # In a real implementation, this would load procedures from files
                logger.info(f"Loading diagnostic procedures from {procedures_path}")
                
                # Register procedures with knowledge engine
                # This is a placeholder for actual procedure registration
            except Exception as e:
                logger.error(f"Error loading diagnostic procedures: {e}")
    
    async def start_session(self, user_id: str, user_info: Dict[str, Any] = None) -> str:
        """Start a new user session with Dr. TARDIS."""
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create conversation state
        conversation_state = ConversationState(
            conversation_id=session_id,
            user_id=user_id,
            start_time=datetime.datetime.now(),
            personality_profile=self.config["default_personality"],
            context=DialogueContext()
        )
        
        # Register conversation with conversation manager
        self.conversation_manager.register_conversation(conversation_state)
        
        # Start Gemini conversation
        initial_context = {
            "user_info": user_info or {},
            "session_id": session_id,
            "personality": self.config["default_personality"]
        }
        gemini_session_id = await self.gemini_integration.start_conversation(user_id, initial_context)
        
        # Store session information
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "gemini_session_id": gemini_session_id,
            "start_time": datetime.datetime.now(),
            "last_activity": datetime.datetime.now(),
            "active_workflows": {},
            "resource_constraints": ResourceConstraints(),
            "user_info": user_info or {}
        }
        
        logger.info(f"Started session {session_id} for user {user_id}")
        return session_id
    
    async def end_session(self, session_id: str) -> bool:
        """End a user session."""
        if session_id not in self.active_sessions:
            logger.warning(f"Attempted to end non-existent session {session_id}")
            return False
        
        # Get user ID
        user_id = self.active_sessions[session_id]["user_id"]
        
        # End Gemini conversation
        await self.gemini_integration.end_conversation(user_id)
        
        # Remove conversation from conversation manager
        self.conversation_manager.remove_conversation(session_id)
        
        # Remove session
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session {session_id} for user {user_id}")
        return True
    
    async def process_text_input(self, session_id: str, text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Process text input from user and generate responses."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Update session activity
        self.active_sessions[session_id]["last_activity"] = datetime.datetime.now()
        
        # Get user ID
        user_id = self.active_sessions[session_id]["user_id"]
        
        # Process input with multimodal layer
        processed_input = self.multimodal_layer.process_input(text, ModalityType.TEXT)
        
        # Update conversation context
        conversation_state = self.conversation_manager.get_conversation(session_id)
        if conversation_state:
            self.conversation_manager.add_user_message(
                conversation_id=session_id,
                message=processed_input.processed_text
            )
        
        # Check for modality switch
        modality_switch = self.multimodal_layer.detect_modality_switch(text)
        if modality_switch:
            # Handle modality switch
            yield {
                "type": "modality_switch",
                "requested_modality": modality_switch.value,
                "message": f"Switching to {modality_switch.value} mode"
            }
        
        # Check for diagnostic intent
        diagnostic_intent = self._detect_diagnostic_intent(text)
        if diagnostic_intent:
            # Start diagnostic workflow
            problem_analysis = self.diagnostic_engine.analyze_problem(
                text, 
                {"user_id": user_id, "session_id": session_id}
            )
            
            workflow_id = self.diagnostic_engine.create_diagnostic_workflow(problem_analysis)
            
            # Store workflow ID
            self.active_sessions[session_id]["active_workflows"][workflow_id] = {
                "problem_id": problem_analysis.problem_id,
                "start_time": datetime.datetime.now(),
                "status": "active"
            }
            
            # Get first step
            current_step = self.diagnostic_engine.get_current_step(workflow_id)
            
            # Yield diagnostic information
            yield {
                "type": "diagnostic_start",
                "workflow_id": workflow_id,
                "problem_analysis": problem_analysis.to_dict(),
                "current_step": current_step.to_dict() if current_step else None
            }
        
        # Process with Gemini
        async for response in self.gemini_integration.send_message(user_id, text):
            # Update conversation context with assistant response
            if "message" in response and "content" in response["message"]:
                content = response["message"]["content"]
                if isinstance(content, str):
                    self.conversation_manager.add_assistant_message(
                        conversation_id=session_id,
                        message=content
                    )
            
            # Yield response
            yield {
                "type": "text_response",
                "content": response
            }
    
    async def process_multimodal_input(self, 
                                     session_id: str, 
                                     text: str, 
                                     media: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """Process multimodal input from user and generate responses."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Update session activity
        self.active_sessions[session_id]["last_activity"] = datetime.datetime.now()
        
        # Get user ID
        user_id = self.active_sessions[session_id]["user_id"]
        
        # Process inputs for each modality
        processed_inputs = {}
        
        # Process text
        if text:
            processed_inputs[ModalityType.TEXT] = self.multimodal_layer.process_input(
                text, ModalityType.TEXT
            )
        
        # Process media
        for item in media:
            media_type = item.get("type")
            if media_type == "image":
                processed_inputs[ModalityType.IMAGE] = self.multimodal_layer.process_input(
                    {"data": item.get("data", ""), "mime_type": item.get("mime_type", "image/jpeg")},
                    ModalityType.IMAGE
                )
            elif media_type == "audio":
                processed_inputs[ModalityType.VOICE] = self.multimodal_layer.process_input(
                    {"data": item.get("data", ""), "mime_type": item.get("mime_type", "audio/wav")},
                    ModalityType.VOICE
                )
            elif media_type == "video":
                processed_inputs[ModalityType.VIDEO] = self.multimodal_layer.process_input(
                    {"data": item.get("data", ""), "mime_type": item.get("mime_type", "video/mp4")},
                    ModalityType.VIDEO
                )
        
        # Fuse inputs if multiple modalities
        if len(processed_inputs) > 1:
            fused_input = self.multimodal_layer.fuse_multimodal_inputs(processed_inputs)
        else:
            # Use the single input
            fused_input = next(iter(processed_inputs.values()))
        
        # Update conversation context
        conversation_state = self.conversation_manager.get_conversation(session_id)
        if conversation_state:
            self.conversation_manager.add_user_message(
                conversation_id=session_id,
                message=fused_input.processed_text,
                metadata={"modalities": [m.value for m in processed_inputs.keys()]}
            )
        
        # Process with Gemini
        async for response in self.gemini_integration.send_multimodal_message(
            user_id, text, media
        ):
            # Update conversation context with assistant response
            if "message" in response and "content" in response["message"]:
                content = response["message"]["content"]
                if isinstance(content, str):
                    self.conversation_manager.add_assistant_message(
                        conversation_id=session_id,
                        message=content
                    )
            
            # Yield response
            yield {
                "type": "multimodal_response",
                "content": response
            }
    
    async def process_diagnostic_step(self, 
                                    session_id: str, 
                                    workflow_id: str, 
                                    step_result: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Process the result of a diagnostic step and get the next step."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Check if workflow exists
        if workflow_id not in self.active_sessions[session_id]["active_workflows"]:
            raise ValueError(f"Workflow {workflow_id} not found for session {session_id}")
        
        # Update session activity
        self.active_sessions[session_id]["last_activity"] = datetime.datetime.now()
        
        # Get outcome from step result
        outcome = step_result.get("outcome")
        if not outcome:
            yield {
                "type": "error",
                "message": "No outcome provided for diagnostic step"
            }
            return
        
        # Advance workflow
        next_step = self.diagnostic_engine.advance_workflow(workflow_id, outcome)
        
        if next_step:
            # Workflow continues
            yield {
                "type": "diagnostic_step",
                "workflow_id": workflow_id,
                "step": next_step.to_dict()
            }
        else:
            # Workflow complete or no next step
            workflow_status = self.diagnostic_engine.get_workflow_status(workflow_id)
            
            if workflow_status.get("is_complete", False):
                # Workflow is complete
                solution = self.diagnostic_engine.select_solution(workflow_id)
                
                # Update workflow status
                self.active_sessions[session_id]["active_workflows"][workflow_id]["status"] = "completed"
                
                yield {
                    "type": "diagnostic_complete",
                    "workflow_id": workflow_id,
                    "status": workflow_status,
                    "solution": solution.to_dict() if solution else None
                }
            else:
                # No next step but workflow not complete (error)
                yield {
                    "type": "error",
                    "message": "No next step available but workflow is not complete"
                }
    
    async def verify_solution(self, 
                            session_id: str, 
                            workflow_id: str, 
                            verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify that a solution has resolved the problem."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Check if workflow exists
        if workflow_id not in self.active_sessions[session_id]["active_workflows"]:
            raise ValueError(f"Workflow {workflow_id} not found for session {session_id}")
        
        # Update session activity
        self.active_sessions[session_id]["last_activity"] = datetime.datetime.now()
        
        # Verify resolution
        resolved = self.diagnostic_engine.verify_resolution(workflow_id, verification_data)
        
        if resolved:
            # Update workflow status
            self.active_sessions[session_id]["active_workflows"][workflow_id]["status"] = "resolved"
        
        return {
            "workflow_id": workflow_id,
            "resolved": resolved,
            "message": "Problem has been resolved" if resolved else "Problem has not been resolved"
        }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_data = self.active_sessions[session_id]
        
        # Get conversation history
        conversation_state = self.conversation_manager.get_conversation(session_id)
        conversation_history = []
        if conversation_state:
            conversation_history = self.conversation_manager.get_conversation_history(session_id)
        
        # Get active workflows
        active_workflows = {}
        for workflow_id, workflow_data in session_data["active_workflows"].items():
            workflow_status = self.diagnostic_engine.get_workflow_status(workflow_id)
            active_workflows[workflow_id] = {
                **workflow_data,
                "status_details": workflow_status
            }
        
        return {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "start_time": session_data["start_time"].isoformat(),
            "last_activity": session_data["last_activity"].isoformat(),
            "duration": (datetime.datetime.now() - session_data["start_time"]).total_seconds(),
            "conversation_length": len(conversation_history),
            "active_workflows": active_workflows,
            "user_info": session_data["user_info"]
        }
    
    def list_active_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self.active_sessions.keys())
    
    async def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions."""
        now = datetime.datetime.now()
        max_inactive_time = self.config.get("max_inactive_time", 3600)  # Default 1 hour
        sessions_to_close = []
        
        # Find inactive sessions
        for session_id, session_data in self.active_sessions.items():
            inactive_time = (now - session_data["last_activity"]).total_seconds()
            if inactive_time > max_inactive_time:
                sessions_to_close.append(session_id)
        
        # Close inactive sessions
        for session_id in sessions_to_close:
            await self.end_session(session_id)
        
        return len(sessions_to_close)
    
    def _detect_diagnostic_intent(self, text: str) -> bool:
        """Detect if text indicates a diagnostic intent."""
        # This is a simple keyword-based detection
        # In a real implementation, this would use more sophisticated NLU
        
        diagnostic_keywords = [
            "problem", "issue", "error", "not working", "broken", "fix",
            "troubleshoot", "diagnose", "help me with", "doesn't work"
        ]
        
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in diagnostic_keywords)
    
    def shutdown(self):
        """Shutdown the Dr. TARDIS system."""
        logger.info("Shutting down Dr. TARDIS system")
        # Perform cleanup
        # In a real implementation, this would close connections, save state, etc.

# Example usage
async def main():
    # Initialize Dr. TARDIS
    dr_tardis = DrTardisSystem()
    
    # Start a session
    session_id = await dr_tardis.start_session("user123", {"name": "Test User"})
    
    # Process a text input
    async for response in dr_tardis.process_text_input(session_id, "Hello, I need help with a connection issue"):
        print(response)
    
    # End the session
    await dr_tardis.end_session(session_id)
    
    # Shutdown
    dr_tardis.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
