#!/usr/bin/env python3
"""
Arcgis-Sys-Api-Dummy Flask Application Entry Point

This script starts the Flask development server.
For production, use a WSGI server like Gunicorn.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )