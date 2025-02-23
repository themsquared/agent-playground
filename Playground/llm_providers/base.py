from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional, List

from pydantic import BaseModel
from Playground.actions import get_action, get_registered_actions
from .cost_calculator import calculate_cost


class LLMResponse(BaseModel):
    """Structured response from LLM providers"""
    content: str
    raw_response: Dict[str, Any]
    model_used: str
    usage: Dict[str, int]
    cost: Dict[str, float]  # Contains input_cost, output_cost, and total_cost in USD


class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    provider_name: str = "base"  # Override in each provider

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._message_history: Dict[str, List[Dict[str, str]]] = {}
        self.client = None

    async def cleanup(self) -> None:
        """Cleanup resources - override in providers that need special cleanup"""
        try:
            if hasattr(self, 'client') and self.client and hasattr(self.client, 'aclose'):
                await self.client.aclose()
        except Exception:
            # Silently ignore cleanup errors
            pass

    def __del__(self):
        """Ensure resources are cleaned up"""
        try:
            import asyncio
            if self.client:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    # No event loop running
                    return
                
                if not loop.is_closed():
                    loop.create_task(self.cleanup())
        except Exception:
            # Silently ignore cleanup errors
            pass

    def calculate_response_cost(self, model: str, usage: Dict[str, int]) -> Dict[str, float]:
        """Calculate the cost of a response based on token usage"""
        return calculate_cost(
            model=model,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            provider=self.provider_name
        )

    def _get_system_message(self) -> str:
        """Get the system message that explains how to use actions"""
        # Get all registered actions
        actions = []
        for action_name, action_class in get_registered_actions().items():
            action = action_class()
            actions.append(action.get_documentation())

        # Get the exact action names for validation
        action_names = [action['name'] for action in actions]
        action_names_str = ', '.join(f'"{name}"' for name in action_names)

        # Build each part separately
        capabilities = f"""You are a helpful AI assistant that MUST use actions to perform tasks.
Available actions: {action_names_str}

IMPORTANT: You MUST ALWAYS respond with an action when performing a task. NEVER respond with plain text or custom JSON formats."""

        # Build examples for each action
        action_examples = []
        for action in actions:
            examples = []
            for example in action.get('examples', []):
                examples.append(f"Example query: \"{example.get('query', '')}\"")
                examples.append(f"Example response: {str(example.get('response', {}))}\n")
            
            action_examples.append(
                f"{len(action_examples) + 1}. {action['description']}\n"
                f"   Required parameters: {action['required_parameters']}\n"
                f"   {chr(10).join(examples)}"
            )

        instructions = f"""
When asked what you can do, respond naturally but ALWAYS include ALL capabilities:

"I can help you with these things:

{chr(10).join(action_examples)}

Let me know which of these you'd like help with!"

RESPONSE FORMAT RULES:
1. You MUST ALWAYS respond with the exact JSON format below when performing actions:
{{
  "actions": [
    {{
      "name": "<exact_action_name>",
      "parameters": {{
        // all required parameters for the action
      }}
    }}
  ]
}}

2. NEVER respond with plain text or custom JSON formats
3. NEVER modify the "actions" format - it must be exactly as shown
4. ALWAYS include ALL required parameters for the action
5. Use the exact action names as listed above
6. You can chain multiple actions in the "actions" array if needed

Example: If someone says "Say hi to Bob in Spanish", you MUST respond with:
{{
  "actions": [
    {{
      "name": "greeting",
      "parameters": {{
        "name": "Bob",
        "language": "es"
      }}
    }}
  ]
}}"""

        # Combine all parts
        return capabilities + instructions

    def _get_or_create_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get or create message history for a session"""
        if session_id not in self._message_history:
            self._message_history[session_id] = []
        return self._message_history[session_id]

    def clear_history(self, session_id: str) -> None:
        """Clear message history for a session"""
        if session_id in self._message_history:
            self._message_history[session_id] = []

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get the message history for a session"""
        return self._get_or_create_history(session_id).copy()

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider with necessary setup"""
        raise NotImplementedError()

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream responses from the LLM"""
        pass

    @classmethod
    async def list_available_models(cls) -> Dict[str, str]:
        """Returns a dictionary of available models and their descriptions"""
        return {} 