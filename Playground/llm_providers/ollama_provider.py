from typing import Any, AsyncGenerator, Dict, Optional, List
import ollama
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from functools import partial
import aiohttp

from .base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """Ollama API provider implementation using official Python client"""

    provider_name = "ollama"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mistral",  # Default to mistral but will be validated
        host: str = "http://localhost:11434"
    ):
        super().__init__(api_key)
        self.host = host
        self.client = None
        self.model = model
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._message_history: Dict[str, List[Dict[str, str]]] = {}
        os.environ["OLLAMA_HOST"] = host
        self.available_models = {}  # Will be populated during initialization

    @classmethod
    async def list_available_models(cls) -> Dict[str, str]:
        """Returns a dictionary of available models and their descriptions"""
        try:
            # Create a synchronous client
            models = ollama.list()
            available_models = {}
            
            # Process each model
            for model in models.models:
                name = str(model.model)
                clean_name = name.split(':')[0] if ':' in name else name
                
                # Create description from model details
                details = []
                if hasattr(model, 'details'):
                    if model.details.parameter_size:
                        details.append(f"Size: {model.details.parameter_size}")
                    if model.details.format:
                        details.append(f"Format: {model.details.format}")
                    if model.details.family:
                        details.append(f"Family: {model.details.family}")
                details_str = ", ".join(details) if details else "No additional details"
                available_models[clean_name] = f"{clean_name} model ({details_str})"
            
            return available_models
        except Exception as e:
            print(f"Error listing Ollama models: {e}")
            return {}

    async def _detect_available_models(self) -> None:
        """Detect which models are actually available in the local Ollama instance"""
        try:
            print("\nChecking Ollama server connection...")
            list_func = partial(ollama.list)
            models_response = await self._run_sync(list_func)
            
            print("Connected to Ollama server successfully")
            print("\nDetecting available models...")
            self.available_models = {}
            
            if not hasattr(models_response, 'models'):
                raise ValueError("Invalid response format from Ollama server")
            
            print("Processing models:")
            for model in models_response.models:
                name = str(model.model)  # Convert model attribute to string
                clean_name = name.split(':')[0] if ':' in name else name
                
                # Create description from model details
                details = []
                if hasattr(model, 'details'):
                    if model.details.parameter_size:
                        details.append(f"Size: {model.details.parameter_size}")
                    if model.details.format:
                        details.append(f"Format: {model.details.format}")
                    if model.details.family:
                        details.append(f"Family: {model.details.family}")
                details_str = ", ".join(details) if details else "No additional details"
                self.available_models[clean_name] = f"{clean_name} model ({details_str})"
                print(f"- Found model: {clean_name} (original name: {name})")
            
            if not self.available_models:
                print("\nNo models found in Ollama server.")
                print("You can install models using 'ollama pull <model>'")
                print("Example: ollama pull mistral")
                raise ValueError("No models available in Ollama server")
            
            print(f"\nTotal models available: {len(self.available_models)}")
            for name, desc in self.available_models.items():
                print(f"- {name}: {desc}")
            
        except Exception as e:
            if "connection refused" in str(e).lower():
                print("\nError: Could not connect to Ollama server")
                print("Please ensure Ollama is running with:")
                print("1. Install Ollama from https://ollama.ai")
                print("2. Start the Ollama server by running 'ollama serve'")
                print(f"3. Verify Ollama is accessible at {self.host}")
                raise ValueError(f"Ollama server not running at {self.host}")
            else:
                print(f"\nError detecting Ollama models: {str(e)}")
                print(f"Error type: {type(e)}")
                print(f"Error details: {str(e)}")
                raise ValueError(f"Failed to detect Ollama models: {str(e)}")

    async def initialize(self) -> None:
        """Initialize the Ollama client and detect available models"""
        print(f"\nInitializing Ollama provider...")
        print(f"Host: {self.host}")
        print(f"Requested model: {self.model}")
        
        self.client = True
        await self._detect_available_models()
        
        # Validate selected model
        if self.model not in self.available_models:
            print(f"\nRequested model '{self.model}' not available")
            available = list(self.available_models.keys())
            if available:
                # Fall back to first available model
                self.model = available[0]
                print(f"Falling back to available model: {self.model}")
                print(f"You can pull your desired model using: ollama pull {self.model}")
            else:
                print("\nNo models available in Ollama server")
                print("Please install at least one model using: ollama pull <model>")
                print("Example: ollama pull llama2")
                raise ValueError("No models available in Ollama server")
        else:
            print(f"\nUsing model: {self.model}")
            print(f"Description: {self.available_models[self.model]}")

    async def _run_sync(self, func):
        """Run synchronous function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, func)

    def _get_or_create_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get or create message history for a session"""
        if session_id not in self._message_history:
            self._message_history[session_id] = []
        return self._message_history[session_id]

    def clear_history(self, session_id: str) -> None:
        """Clear message history for a session"""
        if session_id in self._message_history:
            self._message_history[session_id] = []

    def _get_system_message(self) -> str:
        """Get the system message that explains how to use actions"""
        return """You are a helpful AI assistant with access to various actions. When a user's request requires an action, respond with a JSON object containing the actions to execute.

Available actions:
- get_weather: Get current weather information for a location
  Parameters:
  - location (required): Name of the city or location
  - units (optional): Temperature units (metric/imperial), defaults to metric

Example response format when actions are needed:
{
  "actions": [
    {
      "name": "get_weather",
      "parameters": {
        "location": "New York",
        "units": "metric"
      }
    }
  ]
}

Important:
1. Always use "name" (not "action") to specify the action identifier
2. Always include "parameters" object with the required parameters
3. Format response as valid JSON with an "actions" array
4. For weather queries, always respond with a JSON action, don't provide natural text

If no actions are needed, respond with natural language text.
"""

    def _prepare_messages(self, prompt: str, session_id: str) -> list[dict[str, str]]:
        """Prepare messages for the chat, including system message and history"""
        messages = []
        
        # Add system message if not already in history
        history = self._get_or_create_history(session_id)
        if not history or history[0].get('role') != 'system':
            messages.append({
                'role': 'system',
                'content': self._get_system_message()
            })
        
        # Add history
        messages.extend(history)
        
        # Add current prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        return messages

    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int | None = None, session_id: str = 'default') -> LLMResponse:
        """Generate a response using the Ollama model"""
        messages = self._prepare_messages(prompt, session_id)
        
        chat_func = partial(
            ollama.chat,
            model=self.model,
            messages=messages,
            options={
                'temperature': temperature
            }
        )
        
        response = await self._run_sync(chat_func)
        content = response['message']['content']
        
        # Update history with the exchange
        history = self._get_or_create_history(session_id)
        history.append({'role': 'user', 'content': prompt})
        history.append({'role': 'assistant', 'content': content})
        self._message_history[session_id] = history
        
        # Convert response to dictionary format
        raw_response = {
            'model': response.get('model', self.model),
            'message': {
                'role': response['message'].get('role', 'assistant'),
                'content': content
            },
            'done': response.get('done', True),
            'total_duration': response.get('total_duration', 0),
            'load_duration': response.get('load_duration', 0),
            'prompt_eval_duration': response.get('prompt_eval_duration', 0),
            'eval_duration': response.get('eval_duration', 0)
        }
        
        return LLMResponse(
            content=content,
            model_used=self.model,
            usage={
                'total_duration': response.get('total_duration', 0),
                'prompt_eval_duration': response.get('prompt_eval_duration', 0),
                'eval_duration': response.get('eval_duration', 0)
            },
            raw_response=raw_response,
            cost=self.calculate_response_cost(
                model=self.model,
                usage={
                    "prompt_tokens": 0,  # Ollama doesn't provide token counts
                    "completion_tokens": 0
                }
            )
        )

    async def stream(self, prompt: str, temperature: float = 0.7, max_tokens: int | None = None, session_id: str = 'default') -> AsyncGenerator[str, None]:
        """Stream a response using the Ollama model"""
        messages = self._prepare_messages(prompt, session_id)
        
        chat_func = partial(
            ollama.chat,
            model=self.model,
            messages=messages,
            options={
                'temperature': temperature
            },
            stream=True
        )
        
        full_response = ''
        async for chunk in self._run_sync(chat_func):
            content = chunk['message']['content']
            full_response += content
            yield content
        
        # Update history with the exchange
        history = self._get_or_create_history(session_id)
        history.append({'role': 'user', 'content': prompt})
        history.append({'role': 'assistant', 'content': full_response})
        self._message_history[session_id] = history

    def __del__(self):
        """Cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=False)