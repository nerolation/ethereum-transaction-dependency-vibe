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
            
            # Show JS files
            js_dir = os.path.join(static_dir, 'js')
            if os.path.exists(js_dir):
                js_files = os.listdir(js_dir)
                print(f"JS directory exists at: {js_dir}")
                print(f"JS files: {js_files}")
                
                # Check for the specific JS file that's 404ing
                main_js = [f for f in js_files if f.startswith('main') and f.endswith('.js')]
                if main_js:
                    print(f"Found main JS file: {main_js[0]}")
                    main_js_path = os.path.join(js_dir, main_js[0])
                    print(f"Main JS path: {main_js_path}")
                    print(f"Main JS exists: {os.path.exists(main_js_path)}")
                else:
                    print("WARNING: Cannot find main.*.js file")
            
            # Show CSS files
            css_dir = os.path.join(static_dir, 'css')
            if os.path.exists(css_dir):
                css_files = os.listdir(css_dir)
                print(f"CSS directory exists at: {css_dir}")
                print(f"CSS files: {css_files}")
                
                # Check for the specific CSS file that's 404ing
                main_css = [f for f in css_files if f.startswith('main') and f.endswith('.css')]
                if main_css:
                    print(f"Found main CSS file: {main_css[0]}")
                    main_css_path = os.path.join(css_dir, main_css[0])
                    print(f"Main CSS path: {main_css_path}")
                    print(f"Main CSS exists: {os.path.exists(main_css_path)}")
                else:
                    print("WARNING: Cannot find main.*.css file")
        else:
            print(f"Warning: Static directory does not exist at: {static_dir}")
    else:
        print(f"Warning: Build directory does not exist at: {static_folder}")

    # Handle all static files in the /static directory
    @app.route('/static/<path:filename>')
    def serve_static_files(filename):
        print(f"Received request for /static/{filename}")
        static_dir = os.path.join(static_folder, 'static')
        full_path = os.path.join(static_dir, filename)
        
        print(f"Checking for static file at: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            print(f"Found static file at: {full_path}")
            print(f"Serving file using send_file")
            return send_file(full_path)
        else:
            print(f"Static file not found at: {full_path}")
            
            # Try with different combinations since the filename might have changed during build
            if 'main.' in filename and filename.endswith('.js'):
                js_dir = os.path.join(static_dir, 'js')
                if os.path.exists(js_dir):
                    js_files = [f for f in os.listdir(js_dir) if f.startswith('main') and f.endswith('.js')]
                    if js_files:
                        actual_js_path = os.path.join(js_dir, js_files[0])
                        print(f"Found alternative main JS file: {actual_js_path}")
                        return send_file(actual_js_path)
            
            if 'main.' in filename and filename.endswith('.css'):
                css_dir = os.path.join(static_dir, 'css')
                if os.path.exists(css_dir):
                    css_files = [f for f in os.listdir(css_dir) if f.startswith('main') and f.endswith('.css')]
                    if css_files:
                        actual_css_path = os.path.join(css_dir, css_files[0])
                        print(f"Found alternative main CSS file: {actual_css_path}")
                        return send_file(actual_css_path)
            
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