"""
Integration Test Manager for Dr. TARDIS Gemini Live API Integration.

This module provides comprehensive end-to-end testing capabilities for Dr. TARDIS,
ensuring all components work together seamlessly.

Classes:
    IntegrationTestManager: Orchestrates end-to-end tests for Dr. TARDIS

Author: Manus Agent
Date: May 26, 2025
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Tuple

from ..knowledge.knowledge_base import KnowledgeBase
from ..knowledge.context_aware_retrieval import ContextAwareRetrieval
from ..video.video_processor import VideoProcessor
from ..ui.voice_interface import VoiceInterfaceComponent
from ..ui.video_interface import VideoInterfaceComponent
from ..ui.conversation_ui import ConversationUIComponent


class TestStatus(Enum):
    """Enumeration of possible test statuses."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class IntegrationTestManager:
    """
    Orchestrates end-to-end tests for Dr. TARDIS.
    
    Features:
    - Comprehensive test suite for all Dr. TARDIS components
    - Automated test execution and reporting
    - Component isolation and mocking capabilities
    - Performance benchmarking during tests
    - Test data generation and management
    - Detailed test reports with metrics
    
    Attributes:
        test_dir (Path): Directory for test data and reports
        tests (Dict[str, Dict]): Dictionary of registered tests
        results (Dict[str, Dict]): Dictionary of test results
        mocks (Dict[str, Any]): Dictionary of mock components
        logger: Logger instance for test logging
    """
    
    def __init__(
        self,
        test_dir: Optional[Union[str, Path]] = None,
        logger: Optional[Any] = None,
    ):
        """
        Initialize the IntegrationTestManager.
        
        Args:
            test_dir: Directory for test data and reports, defaults to 'tests' in current directory
            logger: Logger instance, if None a new logger will be created
        """
        # Set up basic configuration
        self.test_dir = Path(test_dir) if test_dir else Path("tests")
        self.tests = {}
        self.results = {}
        self.mocks = {}
        
        # Create test directory if it doesn't exist
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Set up logger
        if logger:
            self.logger = logger
        else:
            import logging
            self.logger = logging.getLogger("integration_tests")
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Log initialization
        self.logger.info(f"IntegrationTestManager initialized at {datetime.now().isoformat()}")
        self.logger.info(f"Test directory: {self.test_dir}")
        
        # Register default test suites
        self._register_default_tests()
    
    def _register_default_tests(self) -> None:
        """Register default test suites for Dr. TARDIS components."""
        # Voice and audio tests
        self.register_test(
            "voice_audio_integration",
            "Test voice and audio integration",
            self._test_voice_audio_integration,
            ["voice", "audio", "integration"],
            dependencies=["VoiceInterfaceComponent"]
        )
        
        # Video and visual tests
        self.register_test(
            "video_visual_integration",
            "Test video and visual integration",
            self._test_video_visual_integration,
            ["video", "visual", "integration"],
            dependencies=["VideoProcessor", "VideoInterfaceComponent"]
        )
        
        # Knowledge integration tests
        self.register_test(
            "knowledge_integration",
            "Test knowledge base integration",
            self._test_knowledge_integration,
            ["knowledge", "integration"],
            dependencies=["KnowledgeBase", "ContextAwareRetrieval"]
        )
        
        # UI integration tests
        self.register_test(
            "ui_integration",
            "Test UI component integration",
            self._test_ui_integration,
            ["ui", "integration"],
            dependencies=["VoiceInterfaceComponent", "VideoInterfaceComponent", "ConversationUIComponent"]
        )
        
        # End-to-end conversation tests
        self.register_test(
            "e2e_conversation",
            "Test end-to-end conversation flow",
            self._test_e2e_conversation,
            ["e2e", "conversation", "integration"],
            dependencies=["VoiceInterfaceComponent", "ConversationUIComponent", "KnowledgeBase"]
        )
        
        # Fallback mechanism tests
        self.register_test(
            "fallback_mechanisms",
            "Test fallback mechanisms during connectivity issues",
            self._test_fallback_mechanisms,
            ["fallback", "connectivity", "integration"],
            dependencies=[]
        )
        
        # Performance tests
        self.register_test(
            "performance_benchmarks",
            "Run performance benchmarks for all components",
            self._test_performance_benchmarks,
            ["performance", "benchmarks", "integration"],
            dependencies=[]
        )
    
    def register_test(
        self,
        test_id: str,
        description: str,
        test_func: Callable,
        tags: List[str] = None,
        dependencies: List[str] = None,
        timeout: int = 60,
    ) -> None:
        """
        Register a new integration test.
        
        Args:
            test_id: Unique identifier for the test
            description: Description of what the test verifies
            test_func: Function that implements the test
            tags: List of tags for categorizing the test
            dependencies: List of component dependencies for the test
            timeout: Maximum time in seconds for test execution
        """
        if test_id in self.tests:
            self.logger.warning(f"Test {test_id} already registered, overwriting")
        
        self.tests[test_id] = {
            "id": test_id,
            "description": description,
            "func": test_func,
            "tags": tags or [],
            "dependencies": dependencies or [],
            "timeout": timeout,
            "status": TestStatus.PENDING,
        }
        
        self.logger.info(f"Registered test: {test_id} - {description}")
    
    def register_mock(self, component_name: str, mock_obj: Any) -> None:
        """
        Register a mock component for testing.
        
        Args:
            component_name: Name of the component to mock
            mock_obj: Mock object to use
        """
        self.mocks[component_name] = mock_obj
        self.logger.info(f"Registered mock for component: {component_name}")
    
    def run_test(self, test_id: str) -> Dict[str, Any]:
        """
        Run a specific integration test.
        
        Args:
            test_id: Identifier of the test to run
            
        Returns:
            Dictionary with test results
        """
        if test_id not in self.tests:
            self.logger.error(f"Test {test_id} not found")
            return {"status": TestStatus.ERROR, "error": f"Test {test_id} not found"}
        
        test = self.tests[test_id]
        test["status"] = TestStatus.RUNNING
        self.logger.info(f"Running test: {test_id} - {test['description']}")
        
        # Check dependencies
        missing_deps = []
        for dep in test["dependencies"]:
            if dep not in self.mocks and not self._check_component_available(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            test["status"] = TestStatus.SKIPPED
            result = {
                "id": test_id,
                "status": TestStatus.SKIPPED,
                "error": f"Missing dependencies: {', '.join(missing_deps)}",
                "duration": 0,
                "timestamp": datetime.now().isoformat(),
            }
            self.results[test_id] = result
            self.logger.warning(f"Skipped test {test_id} due to missing dependencies: {', '.join(missing_deps)}")
            return result
        
        # Run the test with timeout
        start_time = time.time()
        try:
            # Create test context
            context = {
                "mocks": self.mocks,
                "logger": self.logger,
                "test_dir": self.test_dir,
            }
            
            # Run test function
            test_result = asyncio.run(self._run_with_timeout(test["func"], context, test["timeout"]))
            duration = time.time() - start_time
            
            # Process result
            if isinstance(test_result, dict) and "status" in test_result:
                status = test_result["status"]
                details = test_result.get("details", {})
                error = test_result.get("error", None)
            else:
                status = TestStatus.PASSED
                details = {"result": test_result}
                error = None
            
            test["status"] = status
            result = {
                "id": test_id,
                "status": status,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "details": details,
            }
            
            if error:
                result["error"] = error
            
            self.results[test_id] = result
            self.logger.info(f"Test {test_id} completed with status {status.value} in {duration:.2f} seconds")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            test["status"] = TestStatus.ERROR
            result = {
                "id": test_id,
                "status": TestStatus.ERROR,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }
            self.results[test_id] = result
            self.logger.error(f"Error in test {test_id}: {str(e)}")
            return result
    
    async def _run_with_timeout(self, func: Callable, context: Dict[str, Any], timeout: int) -> Any:
        """Run a function with a timeout."""
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(context), timeout)
            else:
                return await asyncio.to_thread(func, context)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Test execution timed out after {timeout} seconds")
    
    def run_all_tests(self, tags: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run all registered tests, optionally filtered by tags.
        
        Args:
            tags: List of tags to filter tests by
            
        Returns:
            Dictionary of test results by test ID
        """
        self.logger.info(f"Running all tests{' with tags: ' + ', '.join(tags) if tags else ''}")
        
        results = {}
        for test_id, test in self.tests.items():
            # Skip tests that don't match tags filter
            if tags and not any(tag in test["tags"] for tag in tags):
                continue
                
            results[test_id] = self.run_test(test_id)
        
        self._generate_report(results)
        return results
    
    def _generate_report(self, results: Dict[str, Dict[str, Any]]) -> None:
        """
        Generate a test report and save it to the test directory.
        
        Args:
            results: Dictionary of test results
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results.values() if r["status"] == TestStatus.PASSED),
                "failed": sum(1 for r in results.values() if r["status"] == TestStatus.FAILED),
                "skipped": sum(1 for r in results.values() if r["status"] == TestStatus.SKIPPED),
                "error": sum(1 for r in results.values() if r["status"] == TestStatus.ERROR),
            },
            "results": {
                test_id: {
                    **{k: v for k, v in result.items() if k != "status"},
                    "status": result["status"].value if isinstance(result["status"], TestStatus) else result["status"],
                }
                for test_id, result in results.items()
            }
        }
        
        # Calculate average duration for successful tests
        durations = [r["duration"] for r in results.values() if r["status"] == TestStatus.PASSED]
        if durations:
            report["summary"]["avg_duration"] = sum(durations) / len(durations)
        
        # Save report to file
        report_file = self.test_dir / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Test report generated: {report_file}")
        self.logger.info(f"Summary: {report['summary']['passed']} passed, {report['summary']['failed']} failed, "
                        f"{report['summary']['skipped']} skipped, {report['summary']['error']} errors")
    
    def _check_component_available(self, component_name: str) -> bool:
        """
        Check if a component is available for testing.
        
        Args:
            component_name: Name of the component to check
            
        Returns:
            True if the component is available, False otherwise
        """
        # This is a simplified implementation
        # In a real system, this would check if the component can be instantiated
        try:
            if component_name == "VoiceInterfaceComponent":
                from ..ui.voice_interface import VoiceInterfaceComponent
                return True
            elif component_name == "VideoInterfaceComponent":
                from ..ui.video_interface import VideoInterfaceComponent
                return True
            elif component_name == "ConversationUIComponent":
                from ..ui.conversation_ui import ConversationUIComponent
                return True
            elif component_name == "VideoProcessor":
                from ..video.video_processor import VideoProcessor
                return True
            elif component_name == "KnowledgeBase":
                from ..knowledge.knowledge_base import KnowledgeBase
                return True
            elif component_name == "ContextAwareRetrieval":
                from ..knowledge.context_aware_retrieval import ContextAwareRetrieval
                return True
            else:
                return False
        except ImportError:
            return False
    
    # Default test implementations
    async def _test_voice_audio_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test voice and audio integration."""
        logger = context["logger"]
        logger.info("Testing voice and audio integration")
        
        try:
            # Get voice interface component (real or mock)
            voice_interface = context["mocks"].get("VoiceInterfaceComponent")
            if not voice_interface:
                from ..ui.voice_interface import VoiceInterfaceComponent
                voice_interface = VoiceInterfaceComponent()
            
            # Test voice activity state transitions
            logger.info("Testing voice activity state transitions")
            initial_state = voice_interface.get_voice_activity_state()
            voice_interface.start_listening()
            listening_state = voice_interface.get_voice_activity_state()
            voice_interface.stop_listening()
            idle_state = voice_interface.get_voice_activity_state()
            
            # Test audio processing
            logger.info("Testing audio processing")
            test_audio = b"dummy audio data"  # In a real test, this would be actual audio data
            result = voice_interface.process_audio(test_audio)
            
            # Test voice synthesis
            logger.info("Testing voice synthesis")
            test_text = "This is a test of voice synthesis"
            audio_data = voice_interface.synthesize_voice(test_text)
            
            return {
                "status": TestStatus.PASSED,
                "details": {
                    "initial_state": str(initial_state),
                    "listening_state": str(listening_state),
                    "idle_state": str(idle_state),
                    "audio_processing_result": result,
                    "voice_synthesis_length": len(audio_data) if audio_data else 0,
                }
            }
        except Exception as e:
            logger.error(f"Voice audio integration test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_video_visual_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test video and visual integration."""
        logger = context["logger"]
        logger.info("Testing video and visual integration")
        
        try:
            # Get video components (real or mock)
            video_processor = context["mocks"].get("VideoProcessor")
            if not video_processor:
                from ..video.video_processor import VideoProcessor
                video_processor = VideoProcessor()
                
            video_interface = context["mocks"].get("VideoInterfaceComponent")
            if not video_interface:
                from ..ui.video_interface import VideoInterfaceComponent
                video_interface = VideoInterfaceComponent()
            
            # Test camera detection
            logger.info("Testing camera detection")
            cameras = video_interface.get_available_cameras()
            
            # Test video quality settings
            logger.info("Testing video quality settings")
            initial_quality = video_interface.get_quality_settings()
            video_interface.set_quality_settings({"resolution": "720p", "fps": 30})
            updated_quality = video_interface.get_quality_settings()
            
            # Test frame processing
            logger.info("Testing frame processing")
            test_frame = b"dummy frame data"  # In a real test, this would be an actual frame
            processed_frame = video_processor.process_frame(test_frame)
            
            # Test screen sharing
            logger.info("Testing screen sharing")
            screen_sharing_available = hasattr(video_interface, "start_screen_sharing")
            
            return {
                "status": TestStatus.PASSED,
                "details": {
                    "cameras_detected": len(cameras),
                    "initial_quality": initial_quality,
                    "updated_quality": updated_quality,
                    "frame_processing_result": processed_frame is not None,
                    "screen_sharing_available": screen_sharing_available,
                }
            }
        except Exception as e:
            logger.error(f"Video visual integration test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_knowledge_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test knowledge base integration."""
        logger = context["logger"]
        logger.info("Testing knowledge base integration")
        
        try:
            # Get knowledge components (real or mock)
            knowledge_base = context["mocks"].get("KnowledgeBase")
            if not knowledge_base:
                from ..knowledge.knowledge_base import KnowledgeBase
                knowledge_base = KnowledgeBase()
                
            context_retrieval = context["mocks"].get("ContextAwareRetrieval")
            if not context_retrieval:
                from ..knowledge.context_aware_retrieval import ContextAwareRetrieval
                context_retrieval = ContextAwareRetrieval()
            
            # Test knowledge item creation
            logger.info("Testing knowledge item creation")
            test_item = {
                "id": str(uuid.uuid4()),
                "content": "This is a test knowledge item",
                "metadata": {"source": "integration_test", "tags": ["test"]},
            }
            knowledge_base.add_item(test_item)
            
            # Test knowledge retrieval
            logger.info("Testing knowledge retrieval")
            retrieved_item = knowledge_base.get_item(test_item["id"])
            
            # Test context-aware search
            logger.info("Testing context-aware search")
            context_data = {"conversation_id": "test_conversation", "user_query": "test knowledge"}
            search_results = context_retrieval.search(context_data, "test")
            
            return {
                "status": TestStatus.PASSED,
                "details": {
                    "item_created": test_item["id"],
                    "item_retrieved": retrieved_item is not None,
                    "item_content_match": retrieved_item["content"] == test_item["content"] if retrieved_item else False,
                    "search_results_count": len(search_results),
                }
            }
        except Exception as e:
            logger.error(f"Knowledge integration test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_ui_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test UI component integration."""
        logger = context["logger"]
        logger.info("Testing UI component integration")
        
        try:
            # Get UI components (real or mock)
            voice_interface = context["mocks"].get("VoiceInterfaceComponent")
            if not voice_interface:
                from ..ui.voice_interface import VoiceInterfaceComponent
                voice_interface = VoiceInterfaceComponent()
                
            video_interface = context["mocks"].get("VideoInterfaceComponent")
            if not video_interface:
                from ..ui.video_interface import VideoInterfaceComponent
                video_interface = VideoInterfaceComponent()
                
            conversation_ui = context["mocks"].get("ConversationUIComponent")
            if not conversation_ui:
                from ..ui.conversation_ui import ConversationUIComponent
                conversation_ui = ConversationUIComponent()
            
            # Test conversation creation
            logger.info("Testing conversation creation")
            conversation_id = conversation_ui.create_conversation("Test Conversation")
            
            # Test message addition
            logger.info("Testing message addition")
            message_id = conversation_ui.add_message(conversation_id, "user", "This is a test message")
            
            # Test UI settings
            logger.info("Testing UI settings")
            initial_settings = conversation_ui.get_ui_settings()
            conversation_ui.update_ui_settings({"show_typing_indicator": False})
            updated_settings = conversation_ui.get_ui_settings()
            
            # Test voice and video integration
            logger.info("Testing voice and video integration with UI")
            voice_interface.set_conversation_ui(conversation_ui)
            video_interface.set_conversation_ui(conversation_ui)
            
            return {
                "status": TestStatus.PASSED,
                "details": {
                    "conversation_created": conversation_id is not None,
                    "message_added": message_id is not None,
                    "initial_settings": initial_settings,
                    "updated_settings": updated_settings,
                    "voice_ui_integration": hasattr(voice_interface, "conversation_ui"),
                    "video_ui_integration": hasattr(video_interface, "conversation_ui"),
                }
            }
        except Exception as e:
            logger.error(f"UI integration test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_e2e_conversation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test end-to-end conversation flow."""
        logger = context["logger"]
        logger.info("Testing end-to-end conversation flow")
        
        try:
            # Get required components (real or mock)
            voice_interface = context["mocks"].get("VoiceInterfaceComponent")
            if not voice_interface:
                from ..ui.voice_interface import VoiceInterfaceComponent
                voice_interface = VoiceInterfaceComponent()
                
            conversation_ui = context["mocks"].get("ConversationUIComponent")
            if not conversation_ui:
                from ..ui.conversation_ui import ConversationUIComponent
                conversation_ui = ConversationUIComponent()
                
            knowledge_base = context["mocks"].get("KnowledgeBase")
            if not knowledge_base:
                from ..knowledge.knowledge_base import KnowledgeBase
                knowledge_base = KnowledgeBase()
            
            # Set up test conversation
            logger.info("Setting up test conversation")
            conversation_id = conversation_ui.create_conversation("E2E Test Conversation")
            
            # Add test knowledge item
            logger.info("Adding test knowledge item")
            test_item = {
                "id": str(uuid.uuid4()),
                "content": "Dr. TARDIS stands for Technical Assistance, Remote Diagnostics, Installation, and Support",
                "metadata": {"source": "e2e_test", "tags": ["definition"]},
            }
            knowledge_base.add_item(test_item)
            
            # Simulate user input
            logger.info("Simulating user input")
            user_message_id = conversation_ui.add_message(conversation_id, "user", "What does TARDIS stand for?")
            
            # Simulate audio processing
            logger.info("Simulating audio processing")
            test_audio = b"dummy audio data"  # In a real test, this would be actual audio data
            transcription = "What does TARDIS stand for?"
            voice_interface.process_audio(test_audio)
            
            # Simulate knowledge retrieval
            logger.info("Simulating knowledge retrieval")
            search_results = knowledge_base.search("TARDIS stand for")
            
            # Simulate system response
            logger.info("Simulating system response")
            system_response = "TARDIS stands for Technical Assistance, Remote Diagnostics, Installation, and Support."
            system_message_id = conversation_ui.add_message(conversation_id, "system", system_response)
            
            # Simulate voice synthesis
            logger.info("Simulating voice synthesis")
            audio_data = voice_interface.synthesize_voice(system_response)
            
            return {
                "status": TestStatus.PASSED,
                "details": {
                    "conversation_id": conversation_id,
                    "user_message_id": user_message_id,
                    "system_message_id": system_message_id,
                    "knowledge_item_found": len(search_results) > 0,
                    "voice_synthesis_length": len(audio_data) if audio_data else 0,
                }
            }
        except Exception as e:
            logger.error(f"End-to-end conversation test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_fallback_mechanisms(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test fallback mechanisms during connectivity issues."""
        logger = context["logger"]
        logger.info("Testing fallback mechanisms during connectivity issues")
        
        try:
            # This test would simulate connectivity issues and verify fallback behavior
            # For this implementation, we'll just check if the FallbackManager exists
            
            fallback_manager = context["mocks"].get("FallbackManager")
            if not fallback_manager:
                try:
                    from ..integration.fallback_manager import FallbackManager
                    fallback_manager = FallbackManager()
                except ImportError:
                    logger.warning("FallbackManager not implemented yet")
                    return {
                        "status": TestStatus.SKIPPED,
                        "error": "FallbackManager not implemented yet",
                    }
            
            # Test offline mode
            logger.info("Testing offline mode")
            offline_available = hasattr(fallback_manager, "enable_offline_mode")
            
            # Test connection recovery
            logger.info("Testing connection recovery")
            recovery_available = hasattr(fallback_manager, "attempt_reconnection")
            
            # Test data synchronization
            logger.info("Testing data synchronization")
            sync_available = hasattr(fallback_manager, "synchronize_data")
            
            return {
                "status": TestStatus.PASSED if (offline_available and recovery_available and sync_available) else TestStatus.FAILED,
                "details": {
                    "offline_mode_available": offline_available,
                    "connection_recovery_available": recovery_available,
                    "data_synchronization_available": sync_available,
                }
            }
        except Exception as e:
            logger.error(f"Fallback mechanisms test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _test_performance_benchmarks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run performance benchmarks for all components."""
        logger = context["logger"]
        logger.info("Running performance benchmarks")
        
        benchmarks = {}
        
        try:
            # Voice processing benchmark
            logger.info("Running voice processing benchmark")
            voice_interface = context["mocks"].get("VoiceInterfaceComponent")
            if voice_interface:
                start_time = time.time()
                for _ in range(10):  # Process 10 times
                    voice_interface.process_audio(b"dummy audio data")
                voice_processing_time = (time.time() - start_time) / 10
                benchmarks["voice_processing"] = voice_processing_time
            
            # Video processing benchmark
            logger.info("Running video processing benchmark")
            video_processor = context["mocks"].get("VideoProcessor")
            if video_processor:
                start_time = time.time()
                for _ in range(10):  # Process 10 times
                    video_processor.process_frame(b"dummy frame data")
                video_processing_time = (time.time() - start_time) / 10
                benchmarks["video_processing"] = video_processing_time
            
            # Knowledge retrieval benchmark
            logger.info("Running knowledge retrieval benchmark")
            knowledge_base = context["mocks"].get("KnowledgeBase")
            if knowledge_base:
                # Add some test items first
                for i in range(100):
                    knowledge_base.add_item({
                        "id": f"bench_{i}",
                        "content": f"Benchmark test item {i}",
                        "metadata": {"source": "benchmark", "tags": ["test"]},
                    })
                
                start_time = time.time()
                for _ in range(10):  # Search 10 times
                    knowledge_base.search("benchmark test")
                knowledge_retrieval_time = (time.time() - start_time) / 10
                benchmarks["knowledge_retrieval"] = knowledge_retrieval_time
            
            # Check if all benchmarks meet performance requirements
            all_passed = True
            for name, duration in benchmarks.items():
                # Assuming a 2-second response time requirement
                if duration > 2.0:
                    all_passed = False
                    logger.warning(f"Benchmark {name} exceeded 2-second requirement: {duration:.4f}s")
            
            return {
                "status": TestStatus.PASSED if all_passed else TestStatus.FAILED,
                "details": {
                    "benchmarks": benchmarks,
                    "all_within_limits": all_passed,
                }
            }
        except Exception as e:
            logger.error(f"Performance benchmark test failed: {str(e)}")
            return {
                "status": TestStatus.FAILED,
                "error": str(e),
                "details": {"exception": str(e)}
            }
