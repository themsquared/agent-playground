"""
Routes package for the Playground API.
Contains all route blueprints for different endpoint categories.
"""
from flask import Blueprint
from .models_routes import models_bp
from .actions_routes import actions_bp
from .history_routes import history_bp
from .generation_routes import generation_bp
from .settings_routes import settings_bp
from .evaluation_routes import evaluation_bp

# Create a list of all blueprints for easy registration
blueprints = [
    models_bp,
    actions_bp,
    history_bp,
    generation_bp,
    settings_bp,
    evaluation_bp
] 