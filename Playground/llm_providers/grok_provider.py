from typing import Any, AsyncGenerator, Dict, Optional
import aiohttp
import asyncio
import os

from .base import BaseLLMProvider, LLMResponse


class GrokProvider(BaseLLMProvider):
    """Grok API provider implementation"""

    provider_name = "grok"

    GROK1 = "grok-1"
    GROK1_PRO = "grok-1-pro"

    AVAILABLE_MODELS = {
        GROK1: "Base Grok model with general capabilities",
        GROK1_PRO: "Enhanced Grok model with additional capabilities"
    }

    # Class-level cache for fetched models
    _cached_models: Dict[str, str] = {}
    _models_fetched = False

    def __init__(self, api_key: Optional[str] = None, model: str = GROK1):
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model} not available. Choose from: {list(self.AVAILABLE_MODELS.keys())}")
        super().__init__(api_key)
        self.model = model
        self.client = None
        self.base_url = "https://api.grok.x.ai/v1"
        self._cleanup_lock = asyncio.Lock()
        self._is_closed = False
        self.available_models = {}

    @classmethod
    async def _fetch_available_models(cls, api_key: str) -> Dict[str, str]:
        """Fetch available models from Grok API"""
        # Return cached models if already fetched
        if cls._models_fetched:
            return cls._cached_models

        try:
            async with aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {api_key}"}
            ) as session:
                async with session.get(
                    "https://api.grok.x.ai/v1/models"
                ) as response:
                    if response.status != 200:
                        print(f"Error fetching Grok models: {response.status}")
                        return cls.AVAILABLE_MODELS
                    
                    data = await response.json()
                    models = {}
                    for model in data.get("data", []):
                        model_id = model.get("id")
                        if not model_id:
                            continue
                            
                        description = []
                        if "capabilities" in model:
                            caps = model["capabilities"]
                            if caps.get("vision"):
                                description.append("Vision capable")
                            if caps.get("code"):
                                description.append("Code optimized")
                            
                        description.append(model.get("description", "No description available"))
                        models[model_id] = " - ".join(description)
                    
                    # Cache the results
                    cls._cached_models = models or cls.AVAILABLE_MODELS
                    cls._models_fetched = True
                    return cls._cached_models
        except Exception as e:
            print(f"Error fetching Grok models: {e}")
            return cls.AVAILABLE_MODELS

    @classmethod
    async def list_available_models(cls) -> Dict[str, str]:
        """Returns a dictionary of available models and their descriptions"""
        return cls.AVAILABLE_MODELS

    async def initialize(self) -> None:
        """Initialize the Grok client"""
        if not self.api_key:
            raise ValueError("Grok API key is required")
        
        if not self.client or self.client.closed:
            self.client = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            self._is_closed = False
        
        self.available_models = self.AVAILABLE_MODELS
        
        if self.model not in self.available_models:
            available = list(self.available_models.keys())
            if available:
                self.model = available[0]
                print(f"Selected model not available, using: {self.model}")
            else:
                raise ValueError("No Grok models available")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        async with self._cleanup_lock:
            if self.client and not self.client.closed and not self._is_closed:
                await self.client.close()
                self._is_closed = True

    def __del__(self):
        """Synchronous cleanup method"""
        if self.client and not self.client.closed and not self._is_closed:
            # If we're in an event loop, run cleanup
            try:
                loop = asyncio.get_running_loop()
                if not loop.is_closed():
                    loop.create_task(self.cleanup())
            except RuntimeError:
                # No event loop - just close the connector directly
                self.client._connector._close()
            self._is_closed = True

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response using Grok"""
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

        async with self.client.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        ) as response:
            result = await response.json()

            # Add the assistant's response to the history if we're tracking it
            if session_id:
                messages.append({
                    "role": "assistant",
                    "content": result["choices"][0]["message"]["content"]
                })
                self._message_history[session_id] = messages

            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                raw_response=result,
                model_used=self.model,
                usage={
                    "prompt_tokens": result["usage"]["prompt_tokens"],
                    "completion_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                },
                cost=self.calculate_response_cost(
                    model=self.model,
                    usage={
                        "prompt_tokens": result["usage"]["prompt_tokens"],
                        "completion_tokens": result["usage"]["completion_tokens"]
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
        """Stream responses from Grok"""
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

        async with self.client.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
        ) as response:
            full_response_content = ""
            async for line in response.content:
                chunk = line.decode().strip()
                if chunk and chunk.startswith("data: "):
                    data = chunk[6:]
                    full_response_content += data
                    yield data

            # After streaming is complete, add the full response to history if we're tracking it
            if session_id:
                messages.append({
                    "role": "assistant",
                    "content": full_response_content
                })
                self._message_history[session_id] = messages 