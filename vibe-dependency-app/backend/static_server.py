import os
from flask import Flask, send_from_directory

def setup_static_serving(app):
    # Path to the static files (frontend build)
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            return send_from_directory(static_folder, 'index.html')
    
    return app 