"""
Action executor for handling action requests.
"""
from typing import Dict, List, Any, Optional
from .base import ActionResult
from .registry import get_action, get_registered_actions


class ActionExecutor:
    """Executes actions based on requests"""

    async def execute_action(self, action_request: Dict[str, Any]) -> ActionResult:
        """Execute a single action"""
        try:
            action_name = action_request.get("name")
            if not action_name:
                return ActionResult(
                    success=False,
                    message="Missing action name",
                    error="Action request must include 'name' field"
                )

            action_class = get_action(action_name)
            action_instance = action_class()
            parameters = action_request.get("parameters", {})

            return await action_instance.execute(parameters)

        except ValueError as e:
            return ActionResult(
                success=False,
                message="Invalid action",
                error=str(e)
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message="Action execution failed",
                error=str(e)
            )

    async def execute_action_sequence(self, actions: List[Dict[str, Any]]) -> List[ActionResult]:
        """Execute a sequence of actions"""
        results = []
        for action_request in actions:
            result = await self.execute_action(action_request)
            results.append(result)
        return results

    def get_available_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available actions"""
        actions_info = {}
        for name, action_class in get_registered_actions().items():
            actions_info[name] = {
                "name": action_class.name,
                "description": action_class.description,
                "required_parameters": action_class.required_parameters,
                "examples": [example.dict() for example in action_class.examples]
            }
        return actions_info 