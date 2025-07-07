import unittest
import asyncio
import sys
import os
from typing import AsyncIterator, Dict, Any, List, Optional, Callable
import json
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.base_plugin import BasePlugin, StreamMetadata, StreamCheckpoint
from src.core.async_utils import ProgressUpdate, CancellationToken
from src.core.plugin_exceptions import (
    StreamingNotSupportedError,
    StreamTransformationError,
    StreamCompositionError,
    StreamPersistenceError,
    PluginActionNotFoundError
)

# Test implementation of BasePlugin for testing streaming features
class TestStreamingPlugin(BasePlugin):
    """A test implementation of BasePlugin that supports streaming."""
    
    def __init__(self, plugin_id="test_plugin", plugin_name="Test Plugin", 
                 version="1.0.0", description="Test plugin for streaming", config=None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.initialize_called = False
        self.shutdown_called = False
        
    def initialize(self, agent_context=None):
        self.initialize_called = True
        self.agent_context = agent_context
        
    def get_actions(self):
        return [
            {
                "name": "test_action",
                "description": "A test action",
                "returns_stream": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "minimum": 1}
                    }
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "item_number": {"type": "integer"},
                        "data": {"type": "string"}
                    }
                }
            },
            {
                "name": "non_streaming_action",
                "description": "A non-streaming test action",
                "returns_stream": False
            }
        ]
        
    def execute_action(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        if action_name == "test_action":
            # For synchronous execution, return a list instead of a stream
            count = params.get("count", 5) if params else 5
            return [{"item_number": i, "data": f"Test data {i}"} for i in range(count)]
        elif action_name == "non_streaming_action":
            return "Non-streaming result"
        else:
            raise PluginActionNotFoundError(f"Unknown action: {action_name}")
    
    async def execute_action_stream(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        if action_name == "test_action":
            count = params.get("count", 5) if params else 5
            for i in range(count):
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                    
                # Simulate processing time
                await asyncio.sleep(0.01)
                
                # Report progress
                if progress_callback:
                    progress_callback(ProgressUpdate(
                        percentage=(i+1)/count * 100,
                        message=f"Generated item {i+1}/{count}",
                        status="running"
                    ))
                    
                # Yield a result chunk
                yield {"item_number": i, "data": f"Test data {i}"}
        else:
            # Use the default implementation which raises StreamingNotSupportedError
            async for item in super().execute_action_stream(action_name, params, progress_callback, cancellation_token):
                yield item
    
    async def get_stream_metadata(self, action_name, params=None):
        if action_name == "test_action":
            return StreamMetadata(
                content_type="application/json",
                item_schema={
                    "type": "object",
                    "properties": {
                        "item_number": {"type": "integer"},
                        "data": {"type": "string"}
                    }
                },
                supports_transformation=True,
                supports_composition=True,
                supports_persistence=True,
                estimated_size=params.get("count", 5) if params else 5
            )
        return await super().get_stream_metadata(action_name, params)
    
    async def transform_stream(self, stream, transform_type, transform_params=None, 
                              progress_callback=None, cancellation_token=None):
        if transform_type == "map":
            # Apply a mapping function to each item
            transform_func = transform_params.get("transform_func", lambda x: x)
            async for item in stream:
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                yield transform_func(item)
        elif transform_type == "filter":
            # Filter items based on a predicate
            predicate = transform_params.get("predicate", lambda x: True)
            async for item in stream:
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                if predicate(item):
                    yield item
        elif transform_type == "batch":
            # Batch items into groups
            batch_size = transform_params.get("batch_size", 2)
            batch = []
            async for item in stream:
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                batch.append(item)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:  # Don't forget the last partial batch
                yield batch
        else:
            # Use the default implementation which raises StreamTransformationError
            async for item in super().transform_stream(stream, transform_type, transform_params, 
                                                     progress_callback, cancellation_token):
                yield item
    
    async def compose_streams(self, streams, composition_type, composition_params=None, 
                             progress_callback=None, cancellation_token=None):
        if composition_type == "merge":
            # Simple implementation of merge for testing
            # In a real implementation, this would be more sophisticated
            for stream in streams:
                async for item in stream:
                    if cancellation_token and cancellation_token.is_cancelled:
                        break
                    yield item
        elif composition_type == "zip":
            # Simple implementation of zip for testing
            # This is not a proper zip implementation, just for testing
            iterators = [stream.__aiter__() for stream in streams]
            try:
                while True:
                    if cancellation_token and cancellation_token.is_cancelled:
                        break
                    items = []
                    for it in iterators:
                        try:
                            item = await it.__anext__()
                            items.append(item)
                        except StopAsyncIteration:
                            return  # One stream is exhausted
                    yield tuple(items)
            except StopAsyncIteration:
                pass
        else:
            # Use the default implementation which raises StreamCompositionError
            async for item in super().compose_streams(streams, composition_type, composition_params, 
                                                    progress_callback, cancellation_token):
                yield item
    
    async def create_stream_checkpoint(self, stream_id, position, state):
        # Create a checkpoint with the current time
        return StreamCheckpoint(
            stream_id=stream_id,
            position=position,
            state=state,
            timestamp=time.time()
        )
    
    async def resume_stream_from_checkpoint(self, action_name, checkpoint, params=None, 
                                          progress_callback=None, cancellation_token=None):
        if action_name == "test_action":
            # Resume from the checkpoint position
            count = params.get("count", 5) if params else 5
            start_position = checkpoint.position
            
            for i in range(start_position, count):
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                    
                # Simulate processing time
                await asyncio.sleep(0.01)
                
                # Report progress
                if progress_callback:
                    progress_callback(ProgressUpdate(
                        percentage=(i+1-start_position)/(count-start_position) * 100,
                        message=f"Resumed item {i+1}/{count} from checkpoint",
                        status="running"
                    ))
                    
                # Yield a result chunk
                yield {"item_number": i, "data": f"Resumed data {i}"}
        else:
            # Use the default implementation which raises StreamPersistenceError
            async for item in super().resume_stream_from_checkpoint(action_name, checkpoint, params, 
                                                                  progress_callback, cancellation_token):
                yield item
    
    def shutdown(self):
        self.shutdown_called = True


class TestBasePluginStreaming(unittest.TestCase):
    """Test cases for the streaming capabilities of BasePlugin."""
    
    def setUp(self):
        self.plugin = TestStreamingPlugin()
        
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        self.assertEqual(self.plugin.plugin_id, "test_plugin")
        self.assertEqual(self.plugin.name, "Test Plugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.description, "Test plugin for streaming")
        
    def test_get_actions(self):
        """Test that the plugin returns the correct actions."""
        actions = self.plugin.get_actions()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["name"], "test_action")
        self.assertTrue(actions[0]["returns_stream"])
        self.assertEqual(actions[1]["name"], "non_streaming_action")
        self.assertFalse(actions[1]["returns_stream"])
        
    def test_execute_action(self):
        """Test that execute_action returns the correct result."""
        result = self.plugin.execute_action("test_action", {"count": 3})
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["item_number"], 0)
        self.assertEqual(result[0]["data"], "Test data 0")
        
        result = self.plugin.execute_action("non_streaming_action")
        self.assertEqual(result, "Non-streaming result")
        
    async def async_test_execute_action_stream(self):
        """Test that execute_action_stream yields the correct items."""
        items = []
        progress_updates = []
        
        # Create a progress callback that records updates
        def progress_callback(update):
            progress_updates.append(update)
        
        # Execute the streaming action
        async for item in self.plugin.execute_action_stream("test_action", {"count": 3}, progress_callback):
            items.append(item)
        
        # Check the results
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["item_number"], 0)
        self.assertEqual(items[0]["data"], "Test data 0")
        
        # Check progress updates
        self.assertEqual(len(progress_updates), 3)
        self.assertAlmostEqual(progress_updates[0].percentage, 100/3, places=5)
        self.assertEqual(progress_updates[0].status, "running")
        
    def test_execute_action_stream(self):
        """Run the async test for execute_action_stream."""
        asyncio.run(self.async_test_execute_action_stream())
        
    async def async_test_execute_action_stream_with_cancellation(self):
        """Test that execute_action_stream respects cancellation."""
        items = []
        cancellation_token = CancellationToken()
        
        # Start the streaming action
        stream = self.plugin.execute_action_stream("test_action", {"count": 10}, cancellation_token=cancellation_token)
        
        # Get the first item
        item = await stream.__anext__()
        items.append(item)
        
        # Cancel after the first item
        cancellation_token.cancel()
        
        # Try to get more items (should stop after cancellation)
        try:
            async for item in stream:
                items.append(item)
        except StopAsyncIteration:
            pass
        
        # Should have at most a few items due to cancellation
        self.assertLessEqual(len(items), 3)  # Allow for a few items that might be processed before cancellation is checked
        
    def test_execute_action_stream_with_cancellation(self):
        """Run the async test for execute_action_stream with cancellation."""
        asyncio.run(self.async_test_execute_action_stream_with_cancellation())
        
    async def async_test_streaming_not_supported_error(self):
        """Test that StreamingNotSupportedError is raised for non-streaming actions."""
        with self.assertRaises(StreamingNotSupportedError):
            async for _ in self.plugin.execute_action_stream("non_streaming_action"):
                pass
        
    def test_streaming_not_supported_error(self):
        """Run the async test for StreamingNotSupportedError."""
        asyncio.run(self.async_test_streaming_not_supported_error())
        
    async def async_test_get_stream_metadata(self):
        """Test that get_stream_metadata returns the correct metadata."""
        metadata = await self.plugin.get_stream_metadata("test_action", {"count": 3})
        
        self.assertEqual(metadata.content_type, "application/json")
        self.assertTrue(metadata.supports_transformation)
        self.assertTrue(metadata.supports_composition)
        self.assertTrue(metadata.supports_persistence)
        self.assertEqual(metadata.estimated_size, 3)
        
        # Test for non-streaming action
        with self.assertRaises(StreamingNotSupportedError):
            await self.plugin.get_stream_metadata("non_streaming_action")
            
        # Test for non-existent action
        with self.assertRaises(PluginActionNotFoundError):
            await self.plugin.get_stream_metadata("non_existent_action")
        
    def test_get_stream_metadata(self):
        """Run the async test for get_stream_metadata."""
        asyncio.run(self.async_test_get_stream_metadata())
        
    async def async_test_transform_stream_map(self):
        """Test the map transformation."""
        # Create a stream
        stream = self.plugin.execute_action_stream("test_action", {"count": 3})
        
        # Define a transformation function
        def transform_func(item):
            return {
                "transformed_number": item["item_number"] * 2,
                "transformed_data": f"Transformed: {item['data']}"
            }
        
        # Apply the transformation
        transformed_stream = self.plugin.transform_stream(
            stream, 
            "map", 
            {"transform_func": transform_func}
        )
        
        # Collect the results
        results = []
        async for item in transformed_stream:
            results.append(item)
        
        # Check the results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["transformed_number"], 0)
        self.assertEqual(results[0]["transformed_data"], "Transformed: Test data 0")
        
    def test_transform_stream_map(self):
        """Run the async test for transform_stream map."""
        asyncio.run(self.async_test_transform_stream_map())
        
    async def async_test_transform_stream_filter(self):
        """Test the filter transformation."""
        # Create a stream
        stream = self.plugin.execute_action_stream("test_action", {"count": 5})
        
        # Define a predicate function
        def predicate(item):
            return item["item_number"] % 2 == 0  # Only even numbers
        
        # Apply the transformation
        transformed_stream = self.plugin.transform_stream(
            stream, 
            "filter", 
            {"predicate": predicate}
        )
        
        # Collect the results
        results = []
        async for item in transformed_stream:
            results.append(item)
        
        # Check the results
        self.assertEqual(len(results), 3)  # 0, 2, 4
        self.assertEqual(results[0]["item_number"], 0)
        self.assertEqual(results[1]["item_number"], 2)
        self.assertEqual(results[2]["item_number"], 4)
        
    def test_transform_stream_filter(self):
        """Run the async test for transform_stream filter."""
        asyncio.run(self.async_test_transform_stream_filter())
        
    async def async_test_transform_stream_batch(self):
        """Test the batch transformation."""
        # Create a stream
        stream = self.plugin.execute_action_stream("test_action", {"count": 5})
        
        # Apply the transformation
        transformed_stream = self.plugin.transform_stream(
            stream, 
            "batch", 
            {"batch_size": 2}
        )
        
        # Collect the results
        results = []
        async for batch in transformed_stream:
            results.append(batch)
        
        # Check the results
        self.assertEqual(len(results), 3)  # 3 batches: [0,1], [2,3], [4]
        self.assertEqual(len(results[0]), 2)
        self.assertEqual(len(results[1]), 2)
        self.assertEqual(len(results[2]), 1)
        self.assertEqual(results[0][0]["item_number"], 0)
        self.assertEqual(results[0][1]["item_number"], 1)
        
    def test_transform_stream_batch(self):
        """Run the async test for transform_stream batch."""
        asyncio.run(self.async_test_transform_stream_batch())
        
    async def async_test_transform_stream_unsupported(self):
        """Test that unsupported transformations raise StreamTransformationError."""
        # Create a stream
        stream = self.plugin.execute_action_stream("test_action", {"count": 3})
        
        # Try an unsupported transformation
        with self.assertRaises(StreamTransformationError):
            async for _ in self.plugin.transform_stream(stream, "unsupported_transform"):
                pass
        
    def test_transform_stream_unsupported(self):
        """Run the async test for unsupported transformations."""
        asyncio.run(self.async_test_transform_stream_unsupported())
        
    async def async_test_compose_streams_merge(self):
        """Test the merge composition."""
        # Create two streams
        stream1 = self.plugin.execute_action_stream("test_action", {"count": 2})
        stream2 = self.plugin.execute_action_stream("test_action", {"count": 3})
        
        # Compose the streams
        composed_stream = self.plugin.compose_streams(
            [stream1, stream2], 
            "merge"
        )
        
        # Collect the results
        results = []
        async for item in composed_stream:
            results.append(item)
        
        # Check the results
        self.assertEqual(len(results), 5)  # 2 from stream1 + 3 from stream2
        
    def test_compose_streams_merge(self):
        """Run the async test for compose_streams merge."""
        asyncio.run(self.async_test_compose_streams_merge())
        
    async def async_test_compose_streams_zip(self):
        """Test the zip composition."""
        # Create two streams
        stream1 = self.plugin.execute_action_stream("test_action", {"count": 2})
        stream2 = self.plugin.execute_action_stream("test_action", {"count": 2})
        
        # Compose the streams
        composed_stream = self.plugin.compose_streams(
            [stream1, stream2], 
            "zip"
        )
        
        # Collect the results
        results = []
        async for item in composed_stream:
            results.append(item)
        
        # Check the results
        self.assertEqual(len(results), 2)  # 2 pairs
        self.assertEqual(len(results[0]), 2)  # Each pair has 2 items
        self.assertEqual(results[0][0]["item_number"], 0)
        self.assertEqual(results[0][1]["item_number"], 0)
        
    def test_compose_streams_zip(self):
        """Run the async test for compose_streams zip."""
        asyncio.run(self.async_test_compose_streams_zip())
        
    async def async_test_compose_streams_unsupported(self):
        """Test that unsupported compositions raise StreamCompositionError."""
        # Create two streams
        stream1 = self.plugin.execute_action_stream("test_action", {"count": 2})
        stream2 = self.plugin.execute_action_stream("test_action", {"count": 2})
        
        # Try an unsupported composition
        with self.assertRaises(StreamCompositionError):
            async for _ in self.plugin.compose_streams([stream1, stream2], "unsupported_composition"):
                pass
        
    def test_compose_streams_unsupported(self):
        """Run the async test for unsupported compositions."""
        asyncio.run(self.async_test_compose_streams_unsupported())
        
    async def async_test_create_stream_checkpoint(self):
        """Test creating a stream checkpoint."""
        # Create a checkpoint
        checkpoint = await self.plugin.create_stream_checkpoint(
            "test_stream",
            2,
            {"last_item": {"item_number": 1, "data": "Test data 1"}}
        )
        
        # Check the checkpoint
        self.assertEqual(checkpoint.stream_id, "test_stream")
        self.assertEqual(checkpoint.position, 2)
        self.assertEqual(checkpoint.state["last_item"]["item_number"], 1)
        self.assertIsNotNone(checkpoint.timestamp)
        
    def test_create_stream_checkpoint(self):
        """Run the async test for create_stream_checkpoint."""
        asyncio.run(self.async_test_create_stream_checkpoint())
        
    async def async_test_resume_stream_from_checkpoint(self):
        """Test resuming a stream from a checkpoint."""
        # Create a checkpoint
        checkpoint = await self.plugin.create_stream_checkpoint(
            "test_stream",
            2,
            {"last_item": {"item_number": 1, "data": "Test data 1"}}
        )
        
        # Resume the stream
        resumed_stream = self.plugin.resume_stream_from_checkpoint(
            "test_action",
            checkpoint,
            {"count": 5}
        )
        
        # Collect the results
        results = []
        async for item in resumed_stream:
            results.append(item)
        
        # Check the results
        self.assertEqual(len(results), 3)  # Items 2, 3, 4
        self.assertEqual(results[0]["item_number"], 2)
        self.assertEqual(results[0]["data"], "Resumed data 2")
        
    def test_resume_stream_from_checkpoint(self):
        """Run the async test for resume_stream_from_checkpoint."""
        asyncio.run(self.async_test_resume_stream_from_checkpoint())
        
    async def async_test_resume_stream_unsupported(self):
        """Test that unsupported resumption raises StreamPersistenceError."""
        # Create a checkpoint
        checkpoint = await self.plugin.create_stream_checkpoint(
            "test_stream",
            2,
            {"last_item": {"item_number": 1, "data": "Test data 1"}}
        )
        
        # Try to resume an unsupported action
        with self.assertRaises(StreamPersistenceError):
            async for _ in self.plugin.resume_stream_from_checkpoint("non_streaming_action", checkpoint):
                pass
        
    def test_resume_stream_unsupported(self):
        """Run the async test for unsupported resumption."""
        asyncio.run(self.async_test_resume_stream_unsupported())


if __name__ == '__main__':
    unittest.main()
