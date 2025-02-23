"""
Routes for conversation history endpoints.
"""
from flask import Blueprint, jsonify, make_response, request
from ..state import providers, get_or_create_session_id

history_bp = Blueprint('history', __name__, url_prefix='/api')

@history_bp.get('/history')
async def get_conversation_history():
    """Get conversation history for the current session"""
    provider_name = request.args.get('provider', 'openai')
    session_id = get_or_create_session_id()

    if provider_name not in providers:
        return jsonify({'error': 'Invalid provider'}), 400

    provider = providers[provider_name]
    history = provider.get_history(session_id)
    
    response = make_response(jsonify({'history': history}))
    response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
    return response

@history_bp.post('/history/clear')
async def clear_conversation_history():
    """Clear conversation history for the current session"""
    provider_name = request.json.get('provider', 'openai')
    session_id = get_or_create_session_id()

    if provider_name not in providers:
        return jsonify({'error': 'Invalid provider'}), 400

    provider = providers[provider_name]
    provider.clear_history(session_id)
    
    response = make_response(jsonify({'message': 'History cleared successfully'}))
    response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
    return response 