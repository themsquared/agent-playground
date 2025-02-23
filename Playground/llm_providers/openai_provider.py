from typing import Any, AsyncGenerator, Dict, Optional
import openai
from openai import AsyncOpenAI

from .base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation"""

    provider_name = "openai"

    # Latest models (as of February 2024)
    GPT4_VISION = "gpt-4-vision-preview"
    GPT4_TURBO = "gpt-4-0125-preview"  # Latest GPT-4 Turbo
    GPT4 = "gpt-4-1106-preview"  # GPT-4 Turbo with better JSON mode
    GPT4_STABLE = "gpt-4"  # Stable GPT-4 release
    GPT35_TURBO = "gpt-3.5-turbo-0125"  # Latest GPT-3.5 Turbo
    GPT35_TURBO_STABLE = "gpt-3.5-turbo"  # Auto-updates to latest stable 3.5
    GPT35_TURBO_16K = "gpt-3.5-turbo-16k"  # Legacy 16k context model

    AVAILABLE_MODELS = {
        GPT4_VISION: "Latest GPT-4 model with vision capabilities",
        GPT4_TURBO: "Latest GPT-4 Turbo (Jan 2024) - Fastest and most capable model",
        GPT4: "GPT-4 Turbo with improved JSON mode and system prompts",
        GPT4_STABLE: "Stable GPT-4 release - Most reliable but may be slower",
        GPT35_TURBO: "Latest GPT-3.5 Turbo (Jan 2024) - Best price/performance ratio",
        GPT35_TURBO_STABLE: "Auto-updating stable GPT-3.5 Turbo",
        GPT35_TURBO_16K: "Legacy GPT-3.5 with 16k context window"
    }

    # Class-level cache for fetched models
    _cached_models: Dict[str, str] = {}
    _models_fetched = False

    # Add a class variable for models that support system messages
    MODELS_WITH_SYSTEM_SUPPORT = {
        'gpt-4', 'gpt-4-0125-preview', 'gpt-4-1106-preview', 'gpt-4-vision-preview',
        'gpt-3.5-turbo', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-16k'
    }

    # Add a class variable for models that support temperature
    MODELS_WITH_TEMPERATURE_SUPPORT = {
        'gpt-4', 'gpt-4-0125-preview', 'gpt-4-1106-preview', 'gpt-4-vision-preview',
        'gpt-3.5-turbo', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-16k'
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-0125-preview"):
        super().__init__(api_key)
        self.model = model
        self.client = None
        self.available_models = {}

    @classmethod
    async def _fetch_available_models(cls, api_key: str) -> Dict[str, str]:
        """Fetch available models from OpenAI API"""
        # Return cached models if already fetched
        if cls._models_fetched:
            return cls._cached_models

        try:
            client = AsyncOpenAI(api_key=api_key)
            models = await client.models.list()
            
            # Filter for chat models and organize them
            chat_models = {}
            for model in models.data:
                if model.id.startswith(('gpt-4', 'gpt-3.5', 'o')):
                    description = []
                    
                    # Add model family
                    if 'gpt-4' in model.id:
                        description.append("GPT-4")
                    elif 'gpt-3.5' in model.id:
                        description.append("GPT-3.5")
                    
                    # Add capabilities
                    if 'vision' in model.id:
                        description.append("Vision capable")
                    if 'turbo' in model.id:
                        description.append("Turbo version")
                    if '16k' in model.id:
                        description.append("16k context")
                    elif '32k' in model.id:
                        description.append("32k context")
                    
                    # Add preview/stable status
                    if 'preview' in model.id:
                        description.append("Preview")
                    
                    chat_models[model.id] = f"{' - '.join(description)}"
            
            # Cache the results
            cls._cached_models = chat_models
            cls._models_fetched = True
            return cls._cached_models
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            # Fallback to static list
            return cls.AVAILABLE_MODELS

    @classmethod
    async def list_available_models(cls) -> Dict[str, str]:
        """Returns a dictionary of available models and their descriptions"""
        # Return cached models if already fetched
        if cls._models_fetched:
            return cls._cached_models

        try:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("No OpenAI API key found, returning static model list")
                return cls.AVAILABLE_MODELS

            models = await cls._fetch_available_models(api_key)
            if not models:
                print("No models returned from API, falling back to static list")
                return cls.AVAILABLE_MODELS
            return models
        except Exception as e:
            print(f"Error listing OpenAI models: {e}")
            return cls.AVAILABLE_MODELS

    async def initialize(self) -> None:
        """Initialize the OpenAI client and fetch available models"""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.available_models = await self._fetch_available_models(self.api_key)
        
        if self.model not in self.available_models:
            available = list(self.available_models.keys())
            if available:
                self.model = available[0]
                print(f"Selected model not available, using: {self.model}")
            else:
                raise ValueError("No OpenAI models available")

    def _supports_system_messages(self) -> bool:
        """Check if the current model supports system messages"""
        return any(self.model.startswith(model) for model in self.MODELS_WITH_SYSTEM_SUPPORT)

    def _supports_temperature(self) -> bool:
        """Check if the current model supports temperature parameter"""
        return any(self.model.startswith(model) for model in self.MODELS_WITH_TEMPERATURE_SUPPORT)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response using OpenAI"""
        if not self.client:
            await self.initialize()

        # Get or create message history for this session
        messages = (
            self._get_or_create_history(session_id)
            if session_id
            else []
        ).copy()

        # Add system message if supported and not present
        if self._supports_system_messages():
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self._get_system_message()})
        elif messages and messages[0].get("role") == "system":
            # Remove system message if not supported
            messages = [msg for msg in messages if msg.get("role") != "system"]

        # Add the new user message
        messages.append({"role": "user", "content": prompt})

        # Set response format for JSON mode if using compatible model
        if self.model in [self.GPT4, self.GPT4_TURBO, self.GPT35_TURBO]:
            kwargs.setdefault("response_format", {"type": "json"})

        # Create completion kwargs without None values
        completion_kwargs = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        # Only add temperature if supported
        if self._supports_temperature():
            completion_kwargs["temperature"] = temperature

        # Only add max_tokens if provided
        if max_tokens is not None:
            completion_kwargs["max_tokens"] = max_tokens

        response = await self.client.chat.completions.create(**completion_kwargs)

        # Add the assistant's response to the history if we're tracking it
        if session_id:
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            self._message_history[session_id] = messages

        return LLMResponse(
            content=response.choices[0].message.content,
            raw_response=response.model_dump(),
            model_used=self.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            cost=self.calculate_response_cost(
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )
        )

    async def stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream responses from OpenAI"""
        if not self.client:
            await self.initialize()

        # Get or create message history for this session
        messages = (
            self._get_or_create_history(session_id)
            if session_id
            else []
        ).copy()

        # Add system message if supported and not present
        if self._supports_system_messages():
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self._get_system_message()})
        elif messages and messages[0].get("role") == "system":
            # Remove system message if not supported
            messages = [msg for msg in messages if msg.get("role") != "system"]

        # Add the new user message
        messages.append({"role": "user", "content": prompt})

        # Set response format for JSON mode if using compatible model
        if self.model in [self.GPT4, self.GPT4_TURBO, self.GPT35_TURBO]:
            kwargs.setdefault("response_format", {"type": "json"})

        # Create completion kwargs without None values
        completion_kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        # Only add temperature if supported
        if self._supports_temperature():
            completion_kwargs["temperature"] = temperature

        # Only add max_tokens if provided
        if max_tokens is not None:
            completion_kwargs["max_tokens"] = max_tokens

        stream = await self.client.chat.completions.create(**completion_kwargs)

        full_response_content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response_content += content
                yield content

        # After streaming is complete, add the full response to history if we're tracking it
        if session_id:
            messages.append({
                "role": "assistant",
                "content": full_response_content
            })
            self._message_history[session_id] = messages 