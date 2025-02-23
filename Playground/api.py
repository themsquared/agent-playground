"""
Main API file for the Playground application.
"""
from flask import Flask
from flask_cors import CORS
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from dotenv import load_dotenv
import atexit

from .routes import blueprints
from .state import providers

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable credentials for cookies

# Register all route blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)

async def cleanup_providers():
    """Cleanup all provider resources"""
    for provider in providers.values():
        await provider.cleanup()

def sync_cleanup():
    """Synchronous wrapper for cleanup"""
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.run_until_complete(cleanup_providers())
    except Exception:
        # Silently ignore cleanup errors
        pass

# Register cleanup handler
atexit.register(sync_cleanup)

async def main():
    config = Config()
    config.bind = ["localhost:5000"]
    await serve(app, config)

if __name__ == '__main__':
    asyncio.run(main())