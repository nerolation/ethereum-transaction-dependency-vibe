import os
from flask import Flask, send_from_directory, send_file

def setup_static_serving(app):
    # Path to the static files (frontend build)
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))
    print(f"Setting up static file serving from: {static_folder}")
    
    # Check if build directory exists and log its contents
    if os.path.exists(static_folder):
        print(f"Build directory exists at: {static_folder}")
        print(f"Build directory contents: {os.listdir(static_folder)}")
        
        # Check if static directory exists
        static_dir = os.path.join(static_folder, 'static')
        if os.path.exists(static_dir):
            print(f"Static directory exists at: {static_dir}")
            print(f"Static directory contents: {os.listdir(static_dir)}")
        else:
            print(f"Warning: Static directory does not exist at: {static_dir}")
    else:
        print(f"Warning: Build directory does not exist at: {static_folder}")

    # Handle all static files in the /static directory
    @app.route('/static/<path:filename>')
    def serve_static_files(filename):
        print(f"Received request for /static/{filename}")
        static_dir = os.path.join(static_folder, 'static')
        
        # Check each path component
        path_components = filename.split('/')
        current_dir = static_dir
        for component in path_components[:-1]:  # All except the last one (filename)
            current_dir = os.path.join(current_dir, component)
            if not os.path.exists(current_dir):
                print(f"Directory {current_dir} does not exist")
                return f"Static file not found: {filename}", 404
        
        full_path = os.path.join(static_dir, filename)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            print(f"Found static file at: {full_path}")
            return send_file(full_path)
        else:
            print(f"Static file not found at: {full_path}")
            # Try as a direct path without the 'static' prefix
            alt_path = os.path.join(static_folder, filename)
            if os.path.exists(alt_path) and os.path.isfile(alt_path):
                print(f"Found static file at alternate location: {alt_path}")
                return send_file(alt_path)
            return f"Static file not found: {filename}", 404

    # Serve root index.html
    @app.route('/')
    def serve_root():
        print(f"Serving index.html for root path")
        return send_from_directory(static_folder, 'index.html')
    
    # Handle all other files - either serve the file if it exists, or return index.html for client routing
    @app.route('/<path:path>')
    def serve_path(path):
        print(f"Request for path: {path}")
        
        # First, check if this is a file that exists in the build directory
        file_path = os.path.join(static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"Serving file: {file_path}")
            return send_file(file_path)
        
        # If not a file, it could be a route handled by the React app, so serve index.html
        print(f"Path not found as file, serving index.html for: {path}")
        return send_from_directory(static_folder, 'index.html')
    
    return app 