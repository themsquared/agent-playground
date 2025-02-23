from typing import Dict, Any
from ..base import BaseAction, ActionResult, ActionExample


class GreetingAction(BaseAction):
    """Action to generate greeting messages in different languages"""
    name = "greeting"
    description = "Generates a greeting message"
    required_parameters = {
        "name": "Name of the person to greet",
        "language": "Language to greet in (en/es/fr), defaults to en"
    }
    examples = [
        ActionExample(
            query="Say hello to Alice",
            response={
                "actions": [{
                    "name": "greeting",
                    "parameters": {
                        "name": "Alice"
                    }
                }]
            },
            description="Basic greeting"
        ),
        ActionExample(
            query="Greet Bob in Spanish",
            response={
                "actions": [{
                    "name": "greeting",
                    "parameters": {
                        "name": "Bob",
                        "language": "es"
                    }
                }]
            },
            description="Greeting in specific language"
        )
    ]

    async def execute(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute the greeting action"""
        try:
            name = parameters["name"]
            language = parameters.get("language", "en")

            greetings = {
                "en": f"Hello, {name}!",
                "es": f"¡Hola, {name}!",
                "fr": f"Bonjour, {name}!"
            }

            if language not in greetings:
                return ActionResult(
                    success=False,
                    message=f"Unsupported language: {language}",
                    error=f"Language must be one of: {', '.join(greetings.keys())}"
                )

            message = greetings[language]
            return ActionResult(
                success=True,
                message=message,
                data={
                    "language": language,
                    "name": name,
                    "greeting": message
                }
            )

        except KeyError as e:
            return ActionResult(
                success=False,
                message="Missing required parameter",
                error=f"Missing parameter: {str(e)}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to generate greeting",
                error=str(e)
            ) 