"""
Utility module for calculating LLM API costs.
Pricing information from:
- OpenAI: https://openai.com/pricing
- Anthropic: https://anthropic.com/pricing
- Others: Estimated/placeholder values
"""
from typing import Dict, Optional

# OpenAI pricing per 1K tokens (as of February 2024)
OPENAI_COSTS = {
    "gpt-4-vision-preview": {"input": 0.01, "output": 0.03},
    "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004}
}

# Anthropic pricing per 1K tokens (as of February 2024)
ANTHROPIC_COSTS = {
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.0005, "output": 0.0025},
    "claude-2.1": {"input": 0.008, "output": 0.024}
}

# Grok pricing (placeholder/estimated values)
GROK_COSTS = {
    "grok-1": {"input": 0.002, "output": 0.006},
    "grok-1-pro": {"input": 0.005, "output": 0.015}
}

# Ollama costs are typically zero as it runs locally
OLLAMA_COSTS = {
    "llama2": {"input": 0.0, "output": 0.0},
    "mistral": {"input": 0.0, "output": 0.0},
    "codellama": {"input": 0.0, "output": 0.0},
    "mixtral": {"input": 0.0, "output": 0.0},
    "neural-chat": {"input": 0.0, "output": 0.0},
    "starling-lm": {"input": 0.0, "output": 0.0},
    "dolphin-mistral": {"input": 0.0, "output": 0.0},
    "orca-mini": {"input": 0.0, "output": 0.0},
    "vicuna": {"input": 0.0, "output": 0.0}
}

def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    provider: str = "openai"
) -> Dict[str, float]:
    """
    Calculate the cost of an API call based on token usage.
    
    Args:
        model: The model name
        input_tokens: Number of input (prompt) tokens
        output_tokens: Number of output (completion) tokens
        provider: The LLM provider name (openai, anthropic, grok, ollama)
    
    Returns:
        Dictionary containing input_cost, output_cost, and total_cost in USD
    """
    costs_map = {
        "openai": OPENAI_COSTS,
        "anthropic": ANTHROPIC_COSTS,
        "grok": GROK_COSTS,
        "ollama": OLLAMA_COSTS
    }
    
    provider_costs = costs_map.get(provider, {})
    model_costs = provider_costs.get(model, {"input": 0.0, "output": 0.0})
    
    input_cost = (input_tokens / 1000) * model_costs["input"]
    output_cost = (output_tokens / 1000) * model_costs["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6)
    } 