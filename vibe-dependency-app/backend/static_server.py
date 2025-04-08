import os
from flask import Flask, send_from_directory

def setup_static_serving(app):
    # Path to the static files (frontend build)
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))
    print(f"Setting up static file serving from: {static_folder}")
    
    # Configure static file serving
    # Using add_url_rule instead of route decorator to ensure it's picked up by Gunicorn
    def serve_index(path=''):
        print(f"Serving index.html for path: '{path}'")
        return send_from_directory(static_folder, 'index.html')
    
    def serve_static(path):
        print(f"Serving static file: '{path}'")
        if os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            return serve_index()
    
    # Add URL rules directly instead of using decorators
    # This ensures the rules are added when the function is called, not when the module is imported
    app.add_url_rule('/', 'serve_index', serve_index)
    app.add_url_rule('/<path:path>', 'serve_static', serve_static)
    
    return app 