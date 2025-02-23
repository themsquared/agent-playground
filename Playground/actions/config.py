"""
Configuration module for actions package.
"""

# Debug flag - set to True to enable debug logging
DEBUG = False

def _debug_print(message: str) -> None:
    """Print debug messages if DEBUG is True"""
    if DEBUG:
        print(message) 