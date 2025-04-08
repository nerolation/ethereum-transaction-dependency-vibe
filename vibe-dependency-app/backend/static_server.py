import os
from flask import Flask, send_from_directory

def setup_static_serving(app):
    # Path to the static files (frontend build)
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))
    print(f"Setting up static file serving from: {static_folder}")
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        print(f"Received request for path: '{path}'")
        if path and os.path.exists(os.path.join(static_folder, path)):
            print(f"Serving file: {os.path.join(static_folder, path)}")
            return send_from_directory(static_folder, path)
        else:
            print(f"Serving index.html as fallback for path: '{path}'")
            return send_from_directory(static_folder, 'index.html')
    
    return app 