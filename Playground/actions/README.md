# Actions

Actions are capabilities that can be executed by the LLM. Each action is a Python class that inherits from `BaseAction` and implements specific functionality.

## Creating a New Action

1. Create a new Python file in the `actions_list` directory
2. Name the file with a descriptive name ending in `_action.py` (e.g., `weather_action.py`)
3. Implement your action class inheriting from `BaseAction`

## Action Requirements

Each action must:
- Inherit from `BaseAction`
- Define class attributes:
  - `name`: Unique identifier for the action
  - `description`: Human-readable description of what the action does
  - `required_parameters`: Dictionary of required parameters and their descriptions
  - `examples`: List of `ActionExample` objects showing how to use the action
- Implement the `execute` method

## Example Action Structure

```python
from typing import Dict, Any
from ..base import BaseAction, ActionResult, ActionExample

class MyAction(BaseAction):
    """Description of what your action does"""
    name = "my_action"
    description = "Human-readable description of the action"
    required_parameters = {
        "param1": "Description of first parameter",
        "param2": "Description of second parameter"
    }
    examples = [
        ActionExample(
            query="Example user query",
            response={
                "actions": [{
                    "name": "my_action",
                    "parameters": {
                        "param1": "example_value",
                        "param2": "example_value"
                    }
                }]
            },
            description="Description of this example"
        )
    ]

    async def execute(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute the action with the given parameters"""
        try:
            # Your action implementation here
            result = "Action result"
            
            return ActionResult(
                success=True,
                message=f"Action completed: {result}",
                data={
                    "result": result,
                    # Additional data as needed
                }
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message="Action failed",
                error=str(e)
            )
```

## Auto-Registration

Actions are automatically discovered and registered when:
1. They are placed in the `actions_list` directory
2. The file name ends with `_action.py`
3. The class inherits from `BaseAction`

No manual registration is required.

## Best Practices

1. **Error Handling**
   - Always wrap your execution code in try/except
   - Return meaningful error messages
   - Include relevant error details in the ActionResult

2. **Parameter Validation**
   - Validate all required parameters are present
   - Validate parameter types and values
   - Return clear error messages for invalid parameters

3. **Documentation**
   - Provide clear descriptions for parameters
   - Include helpful examples
   - Document any external dependencies or API keys needed

4. **Testing**
   - Test with various parameter combinations
   - Test error cases
   - Test edge cases

## Example Actions

See existing actions for reference:
- `weather_action.py`: Gets weather information for a location
- `greeting_action.py`: Generates greetings in different languages 