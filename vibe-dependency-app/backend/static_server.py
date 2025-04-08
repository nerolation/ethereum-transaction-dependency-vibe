import os
from flask import Flask, send_from_directory, send_file, current_app

def setup_static_serving(app):
    # Path to the static files (frontend build)
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))
    print(f"Setting up static file serving from: {static_folder}")
    
    # Check if build directory exists
    if os.path.exists(static_folder):
        print(f"Build directory exists at: {static_folder}")
        print(f"Contents: {os.listdir(static_folder)}")
        
        # Check for static subdirectory
        static_dir = os.path.join(static_folder, 'static')
        if os.path.exists(static_dir):
            print(f"Static subdirectory exists: {os.listdir(static_dir)}")
    else:
        print(f"WARNING: Build directory doesn't exist at: {static_folder}")
    
    # Serve the static files from the build/static directory
    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        print(f"Serving JS file: {filename}")
        return send_from_directory(os.path.join(static_folder, 'static', 'js'), filename)
    
    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        print(f"Serving CSS file: {filename}")
        return send_from_directory(os.path.join(static_folder, 'static', 'css'), filename)
    
    @app.route('/static/media/<path:filename>')
    def serve_media(filename):
        print(f"Serving media file: {filename}")
        return send_from_directory(os.path.join(static_folder, 'static', 'media'), filename)

    # Serve static assets from the root of the build directory
    @app.route('/<path:filename>')
    def serve_static_assets(filename):
        if filename.startswith('static/'):
            # This should be handled by the more specific routes above
            return f"Invalid static path: use /static/js/ or /static/css/ directly", 400
            
        file_path = os.path.join(static_folder, filename)
        print(f"Looking for static file: {file_path}")
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"Serving static file: {filename}")
            return send_from_directory(static_folder, filename)
        else:
            # If the file doesn't exist, it might be a frontend route, so serve index.html
            print(f"File {filename} not found, serving index.html")
            return send_from_directory(static_folder, 'index.html')
    
    # Serve root path (index.html)
    @app.route('/')
    def serve_index():
        print("Serving index.html")
        return send_from_directory(static_folder, 'index.html')
        
    return app 