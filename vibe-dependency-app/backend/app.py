import os
import base64
import pickle
import time
import json
import tempfile
import sys

# Patch for Python 3.11+ where cgi module was removed
# We need to create a stub module before importing google.cloud.storage
if 'cgi' not in sys.modules:
    import types
    cgi_module = types.ModuleType('cgi')
    
    # Add the parse_header function that google.cloud.storage.blob uses
    def parse_header(line):
        """Return (value, params) from a Content-Type like header.
        
        This is a simplified version of the function from the old cgi module.
        """
        parts = line.split(';')
        value = parts[0].strip()
        params = {}
        for part in parts[1:]:
            if '=' not in part:
                continue
            key, val = part.split('=', 1)
            key = key.strip()
            val = val.strip()
            if val and val[0] == val[-1] == '"':
                val = val[1:-1]
            params[key] = val
        return value, params
    
    # Add the function to our stub module
    cgi_module.parse_header = parse_header
    
    # Register the module
    sys.modules['cgi'] = cgi_module
    print("Added stub 'cgi' module for Google Cloud Storage compatibility")

from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import storage
from static_server import setup_static_serving

app = Flask(__name__)
CORS(app)

# Cache settings
CACHE_TIMEOUT = 300  # Cache timeout in seconds (5 minutes)
graph_cache = {}  # Cache for graph data
stats_cache = {}  # Cache for graph stats
gantt_cache = {}  # Cache for gantt chart data
recent_blocks_cache = {
    'data': None,
    'timestamp': 0
}  # Cache for recent blocks
min_block_cache = {
    'data': None,
    'timestamp': 0
}  # Cache for min block number

# Check for alternate Google Cloud credentials format (separate env vars)
if ('GOOGLE_CREDENTIALS_TYPE' in os.environ and 
    'GOOGLE_CREDENTIALS_PROJECT_ID' in os.environ and
    'GOOGLE_CREDENTIALS_CLIENT_EMAIL' in os.environ):
    print("Using credentials from separate environment variables")
    try:
        # Construct a credentials dictionary from individual env vars
        credentials = {
            "type": os.environ.get('GOOGLE_CREDENTIALS_TYPE'),
            "project_id": os.environ.get('GOOGLE_CREDENTIALS_PROJECT_ID'),
            "private_key_id": os.environ.get('GOOGLE_CREDENTIALS_PRIVATE_KEY_ID', ""),
            "private_key": os.environ.get('GOOGLE_CREDENTIALS_PRIVATE_KEY', ""),
            "client_email": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_EMAIL'),
            "client_id": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_ID', ""),
            "auth_uri": os.environ.get('GOOGLE_CREDENTIALS_AUTH_URI', "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.environ.get('GOOGLE_CREDENTIALS_TOKEN_URI', "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.environ.get('GOOGLE_CREDENTIALS_AUTH_PROVIDER_X509_CERT_URL', "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_X509_CERT_URL', "")
        }
        
        # Create a temporary file with the credentials
        temp = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        temp.write(json.dumps(credentials, indent=2))
        temp.flush()
        temp_filename = temp.name
        temp.close()
        
        print(f"Created temporary credentials file: {temp_filename}")
        
        # Set environment variable to point to the temp file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_filename
        
        # Initialize client
        storage_client = storage.Client()
        print("Successfully initialized Google Cloud Storage client from separate env vars")
        DEMO_MODE = False
        
        # Cleanup function
        import atexit
        def cleanup_temp_file():
            try:
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    print(f"Cleaned up temporary credentials file: {temp_filename}")
            except Exception as e:
                print(f"Error cleaning up temporary file: {e}")
        atexit.register(cleanup_temp_file)
        
    except Exception as e:
        print(f"Error initializing Google Cloud Storage client from separate env vars: {e}")
        print("Running in demo mode with mock data...")
        DEMO_MODE = True
# Check for Google Cloud credentials
elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    # Use the credential file path
    print(f"Using credentials from file: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
    try:
        storage_client = storage.Client()
        DEMO_MODE = False
    except Exception as e:
        print(f"Error initializing Google Cloud Storage client from file: {e}")
        print("Running in demo mode with mock data...")
        DEMO_MODE = True
elif 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
    # Use the credential JSON directly from environment variable
    print("Using credentials from environment variable")
    try:
        # Create a temporary file with the credentials
        creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
        
        # Ensure we have valid JSON
        try:
            # Validate JSON format
            # Heroku may add quotes around the JSON content or format it differently
            creds_json = creds_json.strip()
            # Remove outer quotes if present (Heroku sometimes adds these)
            if (creds_json.startswith('"') and creds_json.endswith('"')) or \
               (creds_json.startswith("'") and creds_json.endswith("'")):
                creds_json = creds_json[1:-1]
                
            # Replace escaped quotes if needed
            creds_json = creds_json.replace('\\"', '"').replace("\\'", "'")
            
            # Validate and format JSON
            json_content = json.loads(creds_json)
            # Format it nicely for the file
            creds_json = json.dumps(json_content, indent=2)
            print("Successfully parsed JSON credentials")
        except json.JSONDecodeError as je:
            print(f"Warning: Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON: {je}")
            print("Will try to use it as provided")
        
        # Write to temporary file
        temp = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        temp.write(creds_json)
        temp.flush()
        temp_filename = temp.name
        temp.close()
        
        print(f"Wrote credentials to temporary file: {temp_filename}")
        
        # Set environment variable to point to the temp file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_filename
        
        # Initialize client
        storage_client = storage.Client()
        print("Successfully initialized Google Cloud Storage client")
        DEMO_MODE = False
        
        # We'll clean up the temporary file when the app exits
        # Don't delete immediately as the client might still need it
        import atexit
        def cleanup_temp_file():
            try:
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    print(f"Cleaned up temporary credentials file: {temp_filename}")
            except Exception as e:
                print(f"Error cleaning up temporary file: {e}")
        atexit.register(cleanup_temp_file)
        
    except Exception as e:
        print(f"Error initializing Google Cloud Storage client from JSON: {e}")
        print("Running in demo mode with mock data...")
        DEMO_MODE = True
else:
    print("WARNING: No Google Cloud credentials found!")
    print("To set up credentials, either:")
    print("1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable to point to your credentials file")
    print("2. Set GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable with the JSON content")
    print("3. Set individual GOOGLE_CREDENTIALS_* environment variables")
    print("\nRunning in demo mode with mock data...")
    DEMO_MODE = True

# GCS bucket and folder configuration
BUCKET_NAME = "ethereum-graphs"
IMAGES_FOLDER = "images"
CHARTS_FOLDER = "chart_data"  # Folder for Gantt charts

# Mock data for demo mode
MOCK_BLOCKS = ["22216953", "22216952", "22216951", "22216950", "22216949", 
               "22216948", "22216947", "22216946", "22216945"]
MOCK_NODE_COUNTS = {block: 50 + int(block[-1]) * 5 for block in MOCK_BLOCKS}
MOCK_EDGE_COUNTS = {block: 80 + int(block[-1]) * 8 for block in MOCK_BLOCKS}

# Demo mock image - a simple 1x1 pixel transparent PNG
# In a real implementation, you would include actual sample images
MOCK_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def get_image_from_gcs(block_number):
    """Get a pre-rendered image from Google Cloud Storage."""
    if DEMO_MODE:
        # Return a mock image in demo mode
        return MOCK_IMAGE
    
    # Check cache first
    if block_number in graph_cache and time.time() - graph_cache[block_number]['timestamp'] < CACHE_TIMEOUT:
        return graph_cache[block_number]['image']
        
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{IMAGES_FOLDER}/{block_number}.png")
    
    if not blob.exists():
        return None
    
    # Download as bytes
    image_data = blob.download_as_bytes()
    
    # Encode to base64 for frontend display
    img_str = base64.b64encode(image_data).decode('utf-8')
    
    # Cache the result
    graph_cache[block_number] = {
        'image': img_str,
        'timestamp': time.time()
    }
    
    return img_str

def get_gantt_from_gcs(block_number):
    """Get a pre-rendered Gantt chart image from Google Cloud Storage."""
    if DEMO_MODE:
        # Return a mock image in demo mode
        return MOCK_IMAGE
    
    # Check cache first
    if block_number in gantt_cache and time.time() - gantt_cache[block_number]['timestamp'] < CACHE_TIMEOUT:
        return gantt_cache[block_number]['image']
        
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"chart_data_images/{block_number}.png")
    
    if not blob.exists():
        return None
    
    try:
        # Download as bytes
        image_data = blob.download_as_bytes()
        
        # Encode to base64 for frontend display
        img_str = base64.b64encode(image_data).decode('utf-8')
        
        # Cache the result
        gantt_cache[block_number] = {
            'image': img_str,
            'timestamp': time.time()
        }
        
        return img_str
        
    except Exception as e:
        print(f"Error loading Gantt chart image for block {block_number}: {e}")
        return None

def get_recent_block_numbers():
    """Get the most recent block numbers from GCS."""
    if DEMO_MODE:
        return MOCK_BLOCKS
    
    # Check cache first
    if recent_blocks_cache['data'] and time.time() - recent_blocks_cache['timestamp'] < CACHE_TIMEOUT:
        return recent_blocks_cache['data']
        
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=f"{IMAGES_FOLDER}/"))
    
    # Extract block numbers from filenames
    block_numbers = []
    for blob in blobs:
        filename = blob.name.split('/')[-1]
        if filename.endswith('.png'):
            try:
                block_number = filename.split('.')[0]
                block_numbers.append(block_number)
            except ValueError:
                continue
    
    # Sort and get 9 highest block numbers
    # We'll convert to int for sorting, then back to string
    if block_numbers:
        block_numbers = sorted(block_numbers, key=lambda x: int(x), reverse=True)
        result = block_numbers[:9]
        
        # Cache the result
        recent_blocks_cache['data'] = result
        recent_blocks_cache['timestamp'] = time.time()
        
        return result
    
    return []

def get_graph_stats(block_number):
    """Get the number of nodes and edges for a graph."""
    if DEMO_MODE:
        return {
            "node_count": MOCK_NODE_COUNTS.get(block_number, 5),
            "edge_count": MOCK_EDGE_COUNTS.get(block_number, 5)
        }
    
    # Check cache first
    if block_number in stats_cache and time.time() - stats_cache[block_number]['timestamp'] < CACHE_TIMEOUT:
        return stats_cache[block_number]['stats']
    
    # Try to load the graph data from the pickle file
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"graphs/{block_number}.pkl")
        
        if blob.exists():
            # Download the pickle file
            pkl_data = blob.download_as_bytes()
            
            # Load the graph object
            graph = pickle.loads(pkl_data)
            
            # Extract node and edge counts
            stats = {
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges)
            }
            
            # Cache the result
            stats_cache[block_number] = {
                'stats': stats,
                'timestamp': time.time()
            }
            
            return stats
    except Exception as e:
        print(f"Error loading graph data for block {block_number}: {e}")
    
    # Fallback to placeholder values if loading fails
    return {
        "node_count": 10,  # Placeholder
        "edge_count": 15   # Placeholder
    }

def get_min_block_number():
    """Get the minimum block number available."""
    if DEMO_MODE:
        if MOCK_BLOCKS:
            return min(MOCK_BLOCKS, key=lambda x: int(x))
        return None
    
    # Check cache first
    if min_block_cache['data'] and time.time() - min_block_cache['timestamp'] < CACHE_TIMEOUT:
        return min_block_cache['data']
        
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=f"{IMAGES_FOLDER}/"))
    
    block_numbers = []
    for blob in blobs:
        filename = blob.name.split('/')[-1]
        if filename.endswith('.png'):
            try:
                block_number = filename.split('.')[0]
                block_numbers.append(int(block_number))
            except ValueError:
                continue
    
    if block_numbers:
        min_block = str(min(block_numbers))
        
        # Cache the result
        min_block_cache['data'] = min_block
        min_block_cache['timestamp'] = time.time()
        
        return min_block
    
    return None

@app.route('/api/graph/<block_number>', methods=['GET'])
def get_graph(block_number):
    image_data = get_image_from_gcs(block_number)
    
    if image_data is None:
        return jsonify({"error": "Graph not found"}), 404
    
    # Get graph stats
    stats = get_graph_stats(block_number)
    
    return jsonify({
        "block_number": block_number,
        "image": image_data,
        "node_count": stats["node_count"],
        "edge_count": stats["edge_count"],
        "demo_mode": DEMO_MODE
    })

@app.route('/api/gantt/<block_number>', methods=['GET'])
def get_gantt(block_number):
    """Get a Gantt chart for a given block number."""
    try:
        # Get chart image from GCS
        image_data = get_gantt_from_gcs(block_number)
        
        if not image_data:
            return jsonify({'error': f'Gantt chart not found for block {block_number}'}), 404
        
        # Get graph stats
        stats = get_graph_stats(block_number)
        
        # Return image data and stats
        response = {
            'block_number': block_number,
            'image': image_data,
            'node_count': stats['node_count'],
            'edge_count': stats['edge_count'],
            'demo_mode': DEMO_MODE
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error in gantt API for block {block_number}: {e}")
        return jsonify({'error': f'Error retrieving Gantt chart: {str(e)}'}), 500

@app.route('/api/recent_graphs', methods=['GET'])
def get_recent_graphs():
    """Get the 9 most recent graphs."""
    recent_blocks = get_recent_block_numbers()
    
    result = []
    for block in recent_blocks:
        image_data = get_image_from_gcs(block)
        if image_data:
            stats = get_graph_stats(block)
            result.append({
                "block_number": block,
                "image": image_data,
                "node_count": stats["node_count"],
                "edge_count": stats["edge_count"],
                "demo_mode": DEMO_MODE
            })
    
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the status of the backend."""
    min_block = get_min_block_number()
    
    return jsonify({
        "status": "ok",
        "demo_mode": DEMO_MODE,
        "message": "Demo mode active with mock data" if DEMO_MODE else "Connected to Backend",
        "min_block_number": min_block
    })

if __name__ == '__main__':
    # Check if we are in production environment (Heroku)
    if os.environ.get('PRODUCTION', False):
        # Setup static file serving in production
        app = setup_static_serving(app)
    
    # Get port from environment variable for Heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 