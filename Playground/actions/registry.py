"""
Registry module for managing action registration.
"""
from typing import Dict, Type
from .base import BaseAction
from .actions_list import get_all_actions
from .config import _debug_print

# Dictionary to store registered actions
_registered_actions: Dict[str, Type[BaseAction]] = {}

def register_action(action_class: Type[BaseAction]) -> None:
    """Register a single action class"""
    _debug_print(f"Registering action: {action_class.__name__} with name '{action_class.name}'")
    _registered_actions[action_class.name] = action_class

def register_all_actions() -> None:
    """
    Automatically register all actions from the actions_list directory.
    """
    _debug_print("\nStarting action registration process...")
    _debug_print(f"Current registered actions: {list(_registered_actions.keys())}")
    
    discovered_actions = get_all_actions()
    _debug_print(f"Discovered {len(discovered_actions)} actions")
    
    for action_class in discovered_actions:
        register_action(action_class)
    
    _debug_print(f"Final registered actions: {list(_registered_actions.keys())}")

def get_action(name: str) -> Type[BaseAction]:
    """Get an action by name"""
    if name not in _registered_actions:
        raise ValueError(f"Action '{name}' not found. Available actions: {list(_registered_actions.keys())}")
    return _registered_actions[name]

def get_registered_actions() -> Dict[str, Type[BaseAction]]:
    """Get all registered actions"""
    return _registered_actions.copy()

# Register all actions when the module is imported
register_all_actions()