"""
Shared application state.
"""
import os
import uuid
from typing import Dict
from flask import request
from dotenv import load_dotenv

from .llm_providers import (
    OpenAIProvider,
    AnthropicProvider,
    GrokProvider,
    OllamaProvider
)
from .actions import ActionExecutor

# Load environment variables first
load_dotenv()

def get_or_create_session_id():
    """Get existing session ID from cookie or create a new one"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

# Initialize providers
providers: Dict[str, any] = {
    'openai': OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
    'anthropic': AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
    # 'grok': GrokProvider(api_key=os.getenv("GROK_API_KEY")),
    'ollama': OllamaProvider(host="http://localhost:11434")
}

# Initialize action executor
action_executor = ActionExecutor() 