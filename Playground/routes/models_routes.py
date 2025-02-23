"""
Routes for model-related endpoints.
"""
from flask import Blueprint, jsonify
from ..state import providers

models_bp = Blueprint('models', __name__, url_prefix='/api')

@models_bp.get('/models')
async def get_available_models():
    """Get available models for each provider"""
    try:
        available_models = {}
        for provider_name, provider in providers.items():
            try:
                models = await provider.__class__.list_available_models()
                available_models[provider_name] = models
            except Exception as e:
                print(f"Error getting models for {provider_name}: {e}")
                available_models[provider_name] = {}
        return jsonify(available_models)
    except Exception as e:
        print(f"Error getting models: {e}")
        return jsonify({'error': str(e)}), 500 