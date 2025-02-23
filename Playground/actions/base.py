from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel


class ActionResult(BaseModel):
    """Result of an action execution"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ActionExample(BaseModel):
    """Example usage of an action"""
    query: str
    response: Dict[str, Any]
    description: Optional[str] = None


class BaseAction(ABC):
    """Base class for all actions"""
    name: str
    description: str
    required_parameters: Dict[str, str]
    examples: List[ActionExample]

    def __init__(self):
        if not hasattr(self, 'name'):
            raise ValueError("Action must have a name")
        if not hasattr(self, 'description'):
            raise ValueError("Action must have a description")
        if not hasattr(self, 'required_parameters'):
            self.required_parameters = {}
        if not hasattr(self, 'examples'):
            self.examples = []

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute the action with the given parameters"""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate that all required parameters are present"""
        return all(param in parameters for param in self.required_parameters)

    def get_documentation(self) -> Dict[str, Any]:
        """Get the action's documentation"""
        return {
            "name": self.name,
            "description": self.description,
            "required_parameters": self.required_parameters,
            "examples": [example.dict() for example in self.examples]
        }