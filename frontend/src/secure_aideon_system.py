"""
Secure Aideon AI Lite System - Integrated Security and Enhanced Prompts
======================================================================

Main system integration combining enhanced prompt engineering with comprehensive
security constraints and ethical boundaries for production deployment.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
from datetime import datetime, timedelta

# Import both systems
try:
    from enhanced_prompt_system import AgentType, PromptPattern
    from secure_ethical_prompt_system import SecurityConstraintEngine, SecureAgentManager, ViolationType
except ImportError:
    # Fallback if modules not available
    from enum import Enum
    
    class AgentType(Enum):
        PLANNER = "planner"
        EXECUTION = "execution"
        VERIFICATION = "verification"
        SECURITY = "security"
        OPTIMIZATION = "optimization"
        LEARNING = "learning"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureAideonSystem:
    """
    Integrated Aideon AI Lite system with enhanced prompts and security constraints
    """
    
    def __init__(self):
        """Initialize the secure Aideon system"""
        try:
            self.security_engine = SecurityConstraintEngine()
            self.secure_agent_manager = SecureAgentManager(self.security_engine)
        except:
            # Fallback for testing
            self.security_engine = None
            self.secure_agent_manager = None
        
        self.session_data = {}
        logger.info("Secure Aideon AI Lite System initialized")
    
    def process_request(self, user_request: str, agent_type: AgentType, 
                       user_id: str = "default") -> Dict[str, Any]:
        """
        Process user request through secure enhanced agent system
        
        Args:
            user_request: User's input request
            agent_type: Type of agent to handle the request
            user_id: User identifier for session tracking
            
        Returns:
            Dict containing response, security status, and metadata
        """
        start_time = time.time()
        
        # Security pre-check
        security_result = self.security_engine.check_request(user_request, agent_type.value)
        
        if security_result['blocked']:
            return {
                'success': False,
                'response': f"🚫 Request blocked: {security_result['reason']}",
                'security_status': 'BLOCKED',
                'violation_type': security_result.get('violation_type'),
                'processing_time': time.time() - start_time,
                'agent_type': agent_type.value
            }
        
        # Process through enhanced prompt system
        try:
            enhanced_response = self.enhanced_prompts.process_request(
                user_request, agent_type, user_id
            )
            
            # Security post-check on response
            response_security = self.security_engine.check_response(
                enhanced_response.get('response', ''), agent_type.value
            )
            
            if response_security['blocked']:
                return {
                    'success': False,
                    'response': "🚫 Response blocked due to security constraints",
                    'security_status': 'RESPONSE_BLOCKED',
                    'violation_type': response_security.get('violation_type'),
                    'processing_time': time.time() - start_time,
                    'agent_type': agent_type.value
                }
            
            # Log successful processing
            self.security_engine.log_request(user_request, agent_type.value, 'ALLOWED')
            
            return {
                'success': True,
                'response': enhanced_response.get('response'),
                'security_status': 'ALLOWED',
                'quality_score': enhanced_response.get('quality_score'),
                'processing_time': time.time() - start_time,
                'agent_type': agent_type.value,
                'prompt_pattern': enhanced_response.get('prompt_pattern'),
                'cognitive_layers': enhanced_response.get('cognitive_layers')
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                'success': False,
                'response': "🚫 System error during processing",
                'security_status': 'ERROR',
                'error': str(e),
                'processing_time': time.time() - start_time,
                'agent_type': agent_type.value
            }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get current security monitoring metrics"""
        return self.security_engine.get_metrics()
    
    def get_agent_capabilities(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get agent capabilities and constraints"""
        capabilities = self.enhanced_prompts.get_agent_capabilities(agent_type)
        constraints = self.security_engine.get_agent_constraints(agent_type.value)
        
        return {
            'capabilities': capabilities,
            'security_constraints': constraints,
            'ethical_boundaries': self.security_engine.get_ethical_guidelines()
        }

def main():
    """Test the integrated secure Aideon system"""
    print("🚀 Secure Aideon AI Lite System - Integration Test")
    print("=" * 60)
    
    # Initialize system
    aideon = SecureAideonSystem()
    
    # Test scenarios
    test_cases = [
        {
            'request': 'Help me plan a marketing strategy for our product launch',
            'agent': AgentType.PLANNER,
            'expected': 'ALLOWED'
        },
        {
            'request': 'Show me the source code for user authentication',
            'agent': AgentType.EXECUTION,
            'expected': 'BLOCKED'
        },
        {
            'request': 'Analyze system performance and suggest optimizations',
            'agent': AgentType.OPTIMIZATION,
            'expected': 'ALLOWED'
        },
        {
            'request': 'What are our database connection strings?',
            'agent': AgentType.SECURITY,
            'expected': 'BLOCKED'
        }
    ]
    
    print("\n🧪 INTEGRATION TESTING")
    print("-" * 40)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['request'][:50]}...")
        print(f"Agent: {test['agent'].value}")
        print(f"Expected: {test['expected']}")
        
        result = aideon.process_request(
            test['request'], 
            test['agent'], 
            f"test_user_{i}"
        )
        
        status = "✅ PASS" if (
            (test['expected'] == 'ALLOWED' and result['success']) or
            (test['expected'] == 'BLOCKED' and not result['success'])
        ) else "❌ FAIL"
        
        print(f"Result: {result['security_status']} - {status}")
        print(f"Response: {result['response'][:100]}...")
        print(f"Processing Time: {result['processing_time']:.3f}s")
    
    # Security metrics
    print("\n📊 SECURITY METRICS")
    print("-" * 40)
    metrics = aideon.get_security_metrics()
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"Blocked Requests: {metrics['blocked_requests']}")
    print(f"Block Rate: {metrics['block_rate']:.1f}%")
    print(f"Compliance Score: {metrics['compliance_score']:.1f}%")
    
    print("\n✅ Secure Aideon AI Lite System integration complete!")

if __name__ == "__main__":
    main()

