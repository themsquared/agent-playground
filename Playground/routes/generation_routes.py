"""
Routes for text generation endpoints.
"""
from flask import Blueprint, jsonify, make_response, request
import json
from ..state import providers, action_executor, get_or_create_session_id

generation_bp = Blueprint('generation', __name__, url_prefix='/api')

@generation_bp.post('/generate')
async def generate_response():
    """Generate response from selected provider"""
    data = request.json
    provider_name = data.get('provider', 'openai')
    model = data.get('model')
    prompt = data.get('prompt')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens')
    session_id = get_or_create_session_id()

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        provider = providers[provider_name]
        if model:
            provider.model = model

        # Initialize if not already initialized
        if not provider.client:
            await provider.initialize()

        # Create kwargs dict without None values
        kwargs = {}
        if max_tokens is not None:  # Only include max_tokens if it's not None
            kwargs['max_tokens'] = max_tokens

        response = await provider.generate(
            prompt=prompt,
            temperature=temperature,
            session_id=session_id,
            **kwargs
        )

        # Try to parse actions from the response and execute them
        action_results = []
        try:
            response_data = json.loads(response.content)
            if 'actions' in response_data:
                # Execute the actions
                action_results = await action_executor.execute_action_sequence(response_data['actions'])
                # Convert action results to serializable format
                action_results = [{
                    'success': result.success,
                    'message': result.message,
                    'data': result.data,
                    'error': result.error
                } for result in action_results]
            else:
                action_results = []
        except json.JSONDecodeError:
            action_results = []
        except Exception as e:
            print(f"Error executing actions: {str(e)}")
            action_results = []

        api_response = make_response(jsonify({
            'content': response.content,
            'model_used': response.model_used,
            'usage': response.usage,
            'cost': response.cost,
            'action_results': action_results
        }))
        api_response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
        return api_response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.post('/stream')
async def stream_response():
    """Stream response from selected provider"""
    data = request.json
    provider_name = data.get('provider', 'openai')
    model = data.get('model')
    prompt = data.get('prompt')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens')
    session_id = get_or_create_session_id()

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        provider = providers[provider_name]
        if model:
            provider.model = model

        # Initialize if not already initialized
        if not provider.client:
            await provider.initialize()

        async def generate():
            # Set cookie in the first chunk
            yield f"data: {{'cookie': '{session_id}'}}\n\n"
            
            # Create kwargs dict without None values
            kwargs = {}
            if max_tokens is not None:  # Only include max_tokens if it's not None
                kwargs['max_tokens'] = max_tokens

            full_response = ""
            async for chunk in provider.stream(
                prompt=prompt,
                temperature=temperature,
                session_id=session_id,
                **kwargs
            ):
                full_response += chunk
                yield f"data: {chunk}\n\n"

            # Try to parse and execute actions after the full response
            try:
                response_data = json.loads(full_response)
                actions = response_data.get("actions", [])
                if actions:
                    action_results = await action_executor.execute_action_sequence(actions)
                    for result in action_results:
                        if result.success:
                            yield f"data: [Action Result] {result.message}\n\n"
            except json.JSONDecodeError:
                pass

        response = request.app.response_class(
            generate(),
            mimetype='text/event-stream'
        )
        response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500