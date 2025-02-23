"""
Routes for action-related endpoints.
"""
from flask import Blueprint, jsonify, make_response, request
from ..actions import get_registered_actions
from ..state import action_executor, get_or_create_session_id

actions_bp = Blueprint('actions', __name__, url_prefix='/api')

@actions_bp.get('/actions')
async def get_available_actions():
    """Get list of available actions and their descriptions"""
    actions = get_registered_actions()
    
    # Get detailed information about each action
    action_details = {}
    for name, action_class in actions.items():
        action_instance = action_class()
        action_details[name] = {
            "description": action_instance.description,
            "required_parameters": action_instance.required_parameters
        }
    
    return jsonify(action_details)

@actions_bp.post('/execute_actions')
async def execute_actions():
    """Execute a sequence of actions"""
    data = request.json
    actions = data.get('actions', [])
    session_id = get_or_create_session_id()

    try:
        results = await action_executor.execute_action_sequence(actions)
        response = make_response(jsonify([{
            'success': result.success,
            'message': result.message,
            'data': result.data,
            'error': result.error
        } for result in results]))
        response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500 