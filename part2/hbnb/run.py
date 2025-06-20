"""
run.py: Entrypoint for the HBnB Flask application.

This module imports the application factory and starts the development server.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    """
    Start the Flask development server with debug mode enabled.
    """
    app.run(debug=True)
