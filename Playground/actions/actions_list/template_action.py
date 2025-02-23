"""
Template for creating new actions.
Copy this file and rename it to your_action_name_action.py
"""
from typing import Dict, Any
from ..base import BaseAction, ActionResult, ActionExample


class TemplateAction(BaseAction):
    """
    Template action showing how to create a new action.
    Replace this docstring with a description of what your action does.
    """

    # Required: Unique identifier for your action
    name = "template"

    # Required: Human-readable description of what your action does
    description = "Template action showing the structure of an action"

    # Required: Dictionary of parameters your action accepts
    required_parameters = {
        "param1": "Description of the first parameter",
        "param2": "Description of the second parameter (if needed)",
        # Add more parameters as needed
    }

    # Required: List of examples showing how to use your action
    examples = [
        ActionExample(
            query="Example of how a user might request this action",
            response={
                "actions": [{
                    "name": "template",
                    "parameters": {
                        "param1": "example_value1",
                        "param2": "example_value2"
                    }
                }]
            },
            description="Description of what this example demonstrates"
        ),
        # Add more examples to show different use cases
        ActionExample(
            query="Another way a user might request this action",
            response={
                "actions": [{
                    "name": "template",
                    "parameters": {
                        "param1": "different_value",
                        "param2": "another_value"
                    }
                }]
            },
            description="Description of what this example demonstrates"
        )
    ]

    def __init__(self):
        """
        Initialize your action.
        Add any setup code, API clients, or configuration here.
        """
        super().__init__()
        # Example: self.api_key = os.getenv("MY_API_KEY")
        # Example: self.base_url = "https://api.example.com/v1"

    async def execute(self, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute the action with the given parameters.
        This is where your action's main logic goes.

        Args:
            parameters: Dictionary of parameters passed to your action

        Returns:
            ActionResult containing:
            - success: Whether the action succeeded
            - message: Human-readable message about what happened
            - data: Optional dictionary of structured data
            - error: Error message if the action failed
        """
        try:
            # 1. Extract parameters
            param1 = parameters["param1"]
            param2 = parameters.get("param2", "default_value")  # Example of optional parameter

            # 2. Validate parameters
            if not isinstance(param1, str):
                return ActionResult(
                    success=False,
                    message="Invalid parameter type",
                    error="param1 must be a string"
                )

            # 3. Your action logic here
            # Example:
            # result = await self._make_api_call(param1, param2)
            result = f"Processed {param1} with {param2}"

            # 4. Return success result
            return ActionResult(
                success=True,
                message=f"Action completed successfully: {result}",
                data={
                    "result": result,
                    "param1": param1,
                    "param2": param2
                }
            )

        except KeyError as e:
            # Handle missing required parameters
            return ActionResult(
                success=False,
                message="Missing required parameter",
                error=f"Missing parameter: {str(e)}"
            )
        except Exception as e:
            # Handle unexpected errors
            return ActionResult(
                success=False,
                message="Action failed",
                error=str(e)
            )

    # Add any helper methods your action needs
    # async def _make_api_call(self, param1: str, param2: str) -> str:
    #     """Example helper method for API calls"""
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(
    #             f"{self.base_url}/endpoint",
    #             params={"param1": param1, "param2": param2}
    #         ) as response:
    #             data = await response.json()
    #             return data["result"] 