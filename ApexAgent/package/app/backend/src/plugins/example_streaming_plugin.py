import asyncio
import logging
from typing import AsyncGenerator, Dict, Optional, Any, Callable, Awaitable

from ..core.base_enhanced_plugin import BaseEnhancedPlugin
from ..core.exceptions import PluginArgumentError, PluginExecutionError

class ExampleStreamingPlugin(BaseEnhancedPlugin):
    """
    An example plugin demonstrating actions that stream output using async generators.
    """
    def __init__(self, 
                 plugin_id: str, 
                 plugin_version: str, 
                 config: Optional[Dict[str, Any]] = None, 
                 progress_callback: Optional[Callable[..., Awaitable[None] | None]] = None):
        super().__init__(plugin_id, plugin_version, config, progress_callback)
        self.logger.info(f"ExampleStreamingPlugin (ID: {self.plugin_id}) initialized.")

    async def generate_text_stream(self, prompt: str, num_chunks: int = 5) -> AsyncGenerator[str, None]:
        """
        Simulates generating text chunk by chunk as an asynchronous stream.

        Args:
            prompt (str): The input prompt.
            num_chunks (int): The number of text chunks to generate.

        Yields:
            str: Chunks of generated text.
        """
        if not isinstance(prompt, str) or not prompt:
            raise PluginArgumentError("Argument 'prompt' must be a non-empty string.")
        if not isinstance(num_chunks, int) or num_chunks <= 0:
            raise PluginArgumentError("Argument 'num_chunks' must be a positive integer.")

        self.logger.info(f"Starting text stream generation for prompt: 
{prompt}
")
        for i in range(num_chunks):
            await asyncio.sleep(0.02) # Simulate work for each chunk
            chunk = f"Chunk {i+1}/{num_chunks} for 
{prompt}
. "
            # Report progress for each chunk generated, if a callback is provided
            await self._report_progress(
                action_name="generate_text_stream",
                current_step=i + 1,
                total_steps=num_chunks,
                message=f"Generated chunk {i+1}"
            )
            yield chunk
        self.logger.info("Finished text stream generation.")

    async def stream_with_error(self, total_items: int, error_at_item: int) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Simulates a stream that encounters an error partway through.

        Args:
            total_items (int): Total number of items to attempt to stream.
            error_at_item (int): The item number at which to raise an error (1-indexed).

        Yields:
            dict: Items before the error.
        
        Raises:
            PluginExecutionError: When the specified error_at_item is reached.
        """
        if not isinstance(total_items, int) or total_items <= 0:
            raise PluginArgumentError("Argument 'total_items' must be a positive integer.")
        if not isinstance(error_at_item, int) or error_at_item <= 0 or error_at_item > total_items:
            raise PluginArgumentError(f"Argument 'error_at_item' must be between 1 and {total_items}.")

        self.logger.info(f"Starting stream_with_error, expecting error at item {error_at_item}.")
        for i in range(total_items):
            current_item_num = i + 1
            if current_item_num == error_at_item:
                self.logger.warning(f"Simulating error in stream_with_error at item {current_item_num}.")
                raise PluginExecutionError(f"Simulated error at item {current_item_num} in stream_with_error.")
            
            await asyncio.sleep(0.01)
            yield {"item_number": current_item_num, "data": f"Data for item {current_item_num}"}
        self.logger.info("stream_with_error completed (should not be reached if error_at_item is valid).")

    def non_streaming_action(self, value: int) -> int:
        """
        A simple synchronous, non-streaming action for contrast.
        """
        self.logger.info(f"Executing non_streaming_action with value: {value}")
        return value * 2

# Example of how this plugin might be used (for direct testing or as a script)
# This would typically be orchestrated by the PluginManager
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def demo_progress_callback(**kwargs):
        print(f"[DEMO PROGRESS CALLBACK] {kwargs}")

    async def run_streaming_plugin_demo():
        plugin_config = {"api_key": "dummy_key_for_streaming_plugin"}
        example_plugin = ExampleStreamingPlugin(
            plugin_id="com.example.streamer",
            plugin_version="1.0.0",
            config=plugin_config,
            progress_callback=demo_progress_callback
        )

        print("\n--- Testing generate_text_stream (successful) ---")
        try:
            num_chunks_to_generate = 3
            stream_generator = await example_plugin.execute_action("generate_text_stream", prompt="Test Prompt", num_chunks=num_chunks_to_generate)
            
            if inspect.isasyncgen(stream_generator):
                print("Received async generator. Consuming stream:")
                count = 0
                async for chunk in stream_generator:
                    print(f"  Consumed from stream: 
{chunk}
")
                    count += 1
                assert count == num_chunks_to_generate, f"Expected {num_chunks_to_generate} chunks, got {count}"
                print("Stream consumed successfully.")
            else:
                print(f"Error: Expected AsyncGenerator, got {type(stream_generator)}")
        except Exception as e:
            print(f"Error during generate_text_stream demo: {e}")

        print("\n--- Testing stream_with_error ---")
        try:
            error_stream_generator = await example_plugin.execute_action("stream_with_error", total_items=5, error_at_item=3)
            if inspect.isasyncgen(error_stream_generator):
                print("Received async generator for error stream. Consuming stream:")
                items_before_error = []
                async for item in error_stream_generator:
                    print(f"  Consumed from error stream: {item}")
                    items_before_error.append(item)
                # This line should not be reached if the error is raised correctly within the stream
                print(f"Error: Stream completed without expected error. Items: {items_before_error}") 
            else:
                print(f"Error: Expected AsyncGenerator for error stream, got {type(error_stream_generator)}")
        except PluginExecutionError as e:
            print(f"Successfully caught expected PluginExecutionError in stream: {e}")
        except Exception as e:
            print(f"Unexpected error during stream_with_error demo: {e}")

        print("\n--- Testing non_streaming_action ---")
        try:
            result = await example_plugin.execute_action("non_streaming_action", value=10)
            print(f"Result of non_streaming_action: {result}")
            assert result == 20
        except Exception as e:
            print(f"Error during non_streaming_action: {e}")

    asyncio.run(run_streaming_plugin_demo())

