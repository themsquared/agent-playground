from typing import Any, AsyncGenerator, Dict, Optional
from anthropic import AsyncAnthropic

from .base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider implementation"""

    provider_name = "anthropic"

    CLAUDE3_OPUS = "claude-3-opus-20240229"
    CLAUDE3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE2 = "claude-2.1"

    AVAILABLE_MODELS = {
        CLAUDE3_OPUS: "Most capable model, best for complex tasks and reasoning",
        CLAUDE3_SONNET: "Balanced model with strong performance and reasonable cost",
        CLAUDE3_HAIKU: "Fastest and most cost-effective model",
        CLAUDE2: "Legacy Claude 2 model for backwards compatibility"
    }

    # Class-level cache for fetched models
    _cached_models: Dict[str, str] = {}
    _models_fetched = False

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key)
        self.model = model
        self.client = None
        self.available_models = {}

    @classmethod
    async def _fetch_available_models(cls, api_key: str) -> Dict[str, str]:
        """Fetch available models from Anthropic API"""
        # Return cached models if already fetched
        if cls._models_fetched:
            return cls._cached_models

        try:
            client = AsyncAnthropic(api_key=api_key)
            test_messages = [{"role": "user", "content": "test"}]
            
            available_models = {}
            for model_id, description in cls.AVAILABLE_MODELS.items():
                try:
                    await client.messages.create(
                        model=model_id,
                        messages=test_messages,
                        max_tokens=1
                    )
                    available_models[model_id] = description
                    print(f"Model {model_id} is available")
                except Exception as e:
                    if "model not found" in str(e).lower():
                        print(f"Model {model_id} is not available: {e}")
                        continue
                    elif "invalid api key" in str(e).lower():
                        raise
                    else:
                        available_models[model_id] = description
                        print(f"Model {model_id} availability check error: {e}")
            
            # Cache the results
            cls._cached_models = available_models
            cls._models_fetched = True
            return cls._cached_models
        except Exception as e:
            print(f"Error fetching Anthropic models: {e}")
            return {}

    @classmethod
    async def list_available_models(cls) -> Dict[str, str]:
        """Returns a dictionary of available models and their descriptions"""
        # Return cached models if already fetched
        if cls._models_fetched:
            return cls._cached_models

        try:
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("No Anthropic API key found, returning static model list")
                return cls.AVAILABLE_MODELS

            models = await cls._fetch_available_models(api_key)
            if not models:
                print("No models returned from API, falling back to static list")
                return cls.AVAILABLE_MODELS
            return models
        except Exception as e:
            print(f"Error listing Anthropic models: {e}")
            return cls.AVAILABLE_MODELS

    async def initialize(self) -> None:
        """Initialize the Anthropic client and fetch available models"""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.available_models = await self._fetch_available_models(self.api_key)
        
        if self.model not in self.available_models:
            available = list(self.available_models.keys())
            if available:
                self.model = available[0]
                print(f"Selected model not available, using: {self.model}")
            else:
                raise ValueError("No Anthropic models available")

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response using Anthropic"""
        if not self.client:
            await self.initialize()

        # Get or create message history for this session
        messages = (
            self._get_or_create_history(session_id)
            if session_id
            else []
        ).copy()

        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self._get_system_message()})

        # Add the new user message
        messages.append({"role": "user", "content": prompt})

        response = await self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        # Add the assistant's response to the history if we're tracking it
        if session_id:
            messages.append({
                "role": "assistant",
                "content": response.content[0].text
            })
            self._message_history[session_id] = messages

        return LLMResponse(
            content=response.content[0].text,
            raw_response=response.model_dump(),
            model_used=self.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            cost=self.calculate_response_cost(
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens
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
        """Stream responses from Anthropic"""
        if not self.client:
            await self.initialize()

        # Get or create message history for this session
        messages = (
            self._get_or_create_history(session_id)
            if session_id
            else []
        ).copy()

        # Add the new user message
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs
        )

        full_response_content = ""
        async for chunk in stream:
            if chunk.type == "content_block" and chunk.content.text:
                content = chunk.content.text
                full_response_content += content
                yield content

        # After streaming is complete, add the full response to history if we're tracking it
        if session_id:
            messages.append({
                "role": "assistant",
                "content": full_response_content
            })
            self._message_history[session_id] = messages 