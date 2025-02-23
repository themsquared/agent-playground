"""
This module handles automatic registration of actions from the actions_list directory.
"""
import importlib
import inspect
import os
import sys
from typing import List, Type
from ..base import BaseAction
from ..config import _debug_print

def get_all_actions() -> List[Type[BaseAction]]:
    """
    Automatically discover and return all action classes in the actions_list directory.
    """
    actions = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    _debug_print(f"Scanning for actions in directory: {current_dir}")
    
    # Get all .py files in the directory
    for file in os.listdir(current_dir):
        if file.endswith('.py') and not file.startswith('__'):
            module_name = file[:-3]  # Remove .py extension
            _debug_print(f"Found potential action file: {file}")
            
            # Import the module
            module = importlib.import_module(f'.{module_name}', package=__package__)
            _debug_print(f"Imported module: {module.__name__}")
            
            # Find all classes that inherit from BaseAction
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseAction) and 
                    obj != BaseAction):
                    _debug_print(f"Found action class: {name} in {module.__name__}")
                    actions.append(obj)
    
    _debug_print(f"Total actions discovered: {len(actions)}")
    for action in actions:
        _debug_print(f"- {action.__name__}: {action.name if hasattr(action, 'name') else 'No name'}")
    
    return actions 