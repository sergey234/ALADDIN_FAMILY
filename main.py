#!/usr/bin/env python3
"""
ALADDIN Family Security System - Main Application
Entry point for Docker container
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ALADDIN Family Security"}

def main():
    """Main application entry point"""
    logger.info("🚀 Starting ALADDIN Family Security System")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Import and start the application
        from core.app import create_app
        app = create_app()
        
        # Start the server
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Running in minimal mode...")
        
        # Minimal health check server
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = health_check()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
        
        logger.info("Starting health check server on port 8000")
        server = HTTPServer(('0.0.0.0', 8000), HealthHandler)
        server.serve_forever()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
