"""
Routes for settings-related endpoints.
"""
from flask import Blueprint, jsonify, request
from ..state import providers
import os
from dotenv import load_dotenv, set_key

settings_bp = Blueprint('settings', __name__, url_prefix='/api')

@settings_bp.get('/settings')
async def get_settings():
    """Get current settings including API keys (masked) and theme preferences"""
    settings = {
        'api_keys': {},
        'theme': os.getenv('UI_THEME', 'dark')  # Default to dark theme
    }
    
    # Get masked API keys for each provider that requires an API key
    for provider_name in providers.keys():
        # Skip Ollama as it doesn't require an API key
        if provider_name == 'ollama':
            continue
            
        env_key = f"{provider_name.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        if api_key:
            # Mask the API key, showing only the last 4 characters
            settings['api_keys'][provider_name] = '•' * 8 + api_key[-4:]
        else:
            settings['api_keys'][provider_name] = None
            
    return jsonify(settings)

@settings_bp.post('/settings')
async def update_settings():
    """Update settings including API keys and theme preferences"""
    data = request.json
    
    try:
        # Update API keys
        if 'api_keys' in data:
            for provider, api_key in data['api_keys'].items():
                if api_key:  # Only update if a value is provided
                    env_key = f"{provider.upper()}_API_KEY"
                    # Update the environment variable
                    os.environ[env_key] = api_key
                    # Update the .env file
                    set_key('.env', env_key, api_key)
                    
                    # Reinitialize the provider if it exists
                    if provider in providers:
                        provider_instance = providers[provider]
                        if hasattr(provider_instance, 'initialize'):
                            await provider_instance.initialize()
        
        # Update theme preference
        if 'theme' in data:
            os.environ['UI_THEME'] = data['theme']
            set_key('.env', 'UI_THEME', data['theme'])
        
        return jsonify({'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 