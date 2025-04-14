import os
import base64
import pickle
import time
import json
import tempfile
import sys
import traceback
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('dependency-static-generator')

# Log startup info
logger.info("Starting dependency.pics static file generator...")
logger.info(f"Python version: {sys.version}")

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
    logger.info("Added stub 'cgi' module for Google Cloud Storage compatibility")

try:
    from google.cloud import storage
    logger.info("Successfully imported Google Cloud Storage client")
except ImportError as e:
    logger.error(f"Failed to import Google Cloud Storage: {e}")
    logger.error("Please run: pip install google-cloud-storage")
    sys.exit(1)

# Global storage client
storage_client = None

def get_storage_client():
    """Get or create a Google Cloud Storage client instance."""
    global storage_client
    if storage_client is None:
        logger.info("Initializing Google Cloud Storage client")
        storage_client = storage.Client()
    return storage_client

# Log environment variables (without sensitive data)
logger.info(f"Number of environment variables: {len(os.environ)}")
if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    logger.info(f"GOOGLE_APPLICATION_CREDENTIALS is set to: {creds_path}")
    if os.path.exists(creds_path):
        logger.info(f"Credentials file exists at {creds_path}")
    else:
        logger.warning(f"Credentials file does not exist at {creds_path}")
else:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

# Check for alternate Google Cloud credentials format (separate env vars)
if ('GOOGLE_CREDENTIALS_TYPE' in os.environ and 
    'GOOGLE_CREDENTIALS_PROJECT_ID' in os.environ and
    'GOOGLE_CREDENTIALS_CLIENT_EMAIL' in os.environ):
    print("Using credentials from separate environment variables")
    try:
        # Construct a credentials dictionary from individual env vars
        private_key = os.environ.get('GOOGLE_CREDENTIALS_PRIVATE_KEY', "")
        
        # Fix private key format - Heroku sets environment variables with literal '\n' instead of newlines
        if '\\n' in private_key and '\n' not in private_key:
            print("Converting literal \\n in private key to actual newlines")
            private_key = private_key.replace('\\n', '\n')
        
        credentials = {
            "type": os.environ.get('GOOGLE_CREDENTIALS_TYPE'),
            "project_id": os.environ.get('GOOGLE_CREDENTIALS_PROJECT_ID'),
            "private_key_id": os.environ.get('GOOGLE_CREDENTIALS_PRIVATE_KEY_ID', ""),
            "private_key": private_key,
            "client_email": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_EMAIL'),
            "client_id": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_ID', ""),
            "auth_uri": os.environ.get('GOOGLE_CREDENTIALS_AUTH_URI', "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.environ.get('GOOGLE_CREDENTIALS_TOKEN_URI', "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.environ.get('GOOGLE_CREDENTIALS_AUTH_PROVIDER_X509_CERT_URL', "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.environ.get('GOOGLE_CREDENTIALS_CLIENT_X509_CERT_URL', "")
        }
        
        # Create a temporary file with the credentials
        temp = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        credentials_json = json.dumps(credentials, indent=2)
        temp.write(credentials_json)
        temp.flush()
        temp_filename = temp.name
        temp.close()
        
        print(f"Created temporary credentials file: {temp_filename}")
        
        # Set environment variable to point to the temp file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_filename
        
        # Initialize client using our helper function instead of directly
        get_storage_client()
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
        # Initialize client using our helper function instead of directly
        get_storage_client()
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
        
        # Initialize client using our helper function instead of directly
        get_storage_client()
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
        print(f"Error initializing Google Cloud Storage client from environment variable: {e}")
        print(traceback.format_exc())
        print("Running in demo mode with mock data...")
        DEMO_MODE = True
else:
    print("No Google Cloud credentials found. Running in demo mode with mock data...")
    DEMO_MODE = True

def get_image_from_gcs(block_number):
    """Get an image from Google Cloud Storage."""
    if DEMO_MODE:
        # Return mock data for demo mode
        return {
            'block_number': block_number,
            'image': None,  # This will be base64 encoded PNG in production
            'node_count': 10,
            'edge_count': 15,
            'demo_mode': True
        }
    
    try:
        client = get_storage_client()
        bucket = client.bucket('dependency-pics')
        blob_path = f'eth-txs/{block_number.zfill(8)}.png'
        blob = bucket.blob(blob_path)
        
        print(f"Looking for blob: {blob_path}")
        
        # Check if blob exists
        if not blob.exists():
            print(f"Blob {blob_path} does not exist")
            return None
        
        # Download blob content to memory
        content = blob.download_as_bytes()
        
        # Get blob metadata
        metadata = blob.metadata or {}
        node_count = int(metadata.get('node_count', 0))
        edge_count = int(metadata.get('edge_count', 0))
        
        # Encode image as base64 for JSON response
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        return {
            'block_number': block_number,
            'image': image_base64,
            'node_count': node_count,
            'edge_count': edge_count,
            'demo_mode': False
        }
    except Exception as e:
        print(f"Error retrieving image from GCS: {e}")
        print(traceback.format_exc())
        return None

def get_gantt_from_gcs(block_number):
    """Get a gantt chart image from Google Cloud Storage."""
    if DEMO_MODE:
        # Return mock data for demo mode
        return {
            'block_number': block_number,
            'image': None,  # This will be base64 encoded PNG in production
            'demo_mode': True
        }
    
    try:
        client = get_storage_client()
        bucket = client.bucket('dependency-pics')
        blob_path = f'eth-txs/{block_number.zfill(8)}_gantt.png'
        blob = bucket.blob(blob_path)
        
        print(f"Looking for blob: {blob_path}")
        
        # Check if blob exists
        if not blob.exists():
            print(f"Blob {blob_path} does not exist")
            return None
        
        # Download blob content to memory
        content = blob.download_as_bytes()
        
        # Encode image as base64 for JSON response
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        return {
            'block_number': block_number,
            'image': image_base64,
            'demo_mode': False
        }
    except Exception as e:
        print(f"Error retrieving gantt chart from GCS: {e}")
        print(traceback.format_exc())
        return None

def get_recent_block_numbers():
    """Get a list of recent block numbers."""
    if DEMO_MODE:
        # Return mock data for demo mode
        blocks = ['16000000', '16000001', '16000002', '16000003', '16000004', '16000005']
        return [{'block_number': block} for block in blocks]
    
    try:
        client = get_storage_client()
        bucket = client.bucket('dependency-pics')
        blobs = list(bucket.list_blobs(prefix='eth-txs/', delimiter='/'))
        
        recent_blocks = []
        for blob in blobs:
            # Only include the dependency graph PNGs, not gantt charts or other files
            if blob.name.endswith('.png') and not blob.name.endswith('_gantt.png'):
                # Extract the block number from the filename
                # Filename format is eth-txs/00000000.png
                block_number = blob.name.split('/')[-1].split('.')[0].lstrip('0')
                if block_number == '':
                    block_number = '0'
                
                # Get metadata for additional information
                metadata = blob.metadata or {}
                node_count = int(metadata.get('node_count', 0))
                edge_count = int(metadata.get('edge_count', 0))
                
                # Only add if not already in the list (avoid duplicates)
                if not any(block['block_number'] == block_number for block in recent_blocks):
                    recent_blocks.append({
                        'block_number': block_number,
                        'node_count': node_count,
                        'edge_count': edge_count
                    })
        
        # Sort by block number in descending order (newest first)
        recent_blocks.sort(key=lambda x: int(x['block_number']), reverse=True)
        
        # Limit to newest 9 blocks
        return recent_blocks[:9]
    except Exception as e:
        print(f"Error retrieving recent block numbers: {e}")
        print(traceback.format_exc())
        return []

def get_graph_stats(block_number):
    """Get statistics for a graph."""
    if DEMO_MODE:
        # Return mock data for demo mode
        return {
            'node_count': 10,
            'edge_count': 15
        }
    
    try:
        client = get_storage_client()
        bucket = client.bucket('dependency-pics')
        blob_path = f'eth-txs/{block_number.zfill(8)}.png'
        blob = bucket.blob(blob_path)
        
        # Check if blob exists
        if not blob.exists():
            return None
        
        # Get blob metadata
        metadata = blob.metadata or {}
        node_count = int(metadata.get('node_count', 0))
        edge_count = int(metadata.get('edge_count', 0))
        
        return {
            'node_count': node_count,
            'edge_count': edge_count
        }
    except Exception as e:
        print(f"Error retrieving graph stats: {e}")
        print(traceback.format_exc())
        return None

def get_min_block_number():
    """Get the minimum available block number."""
    if DEMO_MODE:
        return '16000000'
    
    try:
        client = get_storage_client()
        bucket = client.bucket('dependency-pics')
        blobs = list(bucket.list_blobs(prefix='eth-txs/', delimiter='/'))
        
        min_block = None
        for blob in blobs:
            # Only include the dependency graph PNGs, not gantt charts or other files
            if blob.name.endswith('.png') and not blob.name.endswith('_gantt.png'):
                # Extract the block number from the filename
                # Filename format is eth-txs/00000000.png
                block_number = blob.name.split('/')[-1].split('.')[0].lstrip('0')
                if block_number == '':
                    block_number = '0'
                
                # Update minimum block number
                if min_block is None or int(block_number) < int(min_block):
                    min_block = block_number
        
        return min_block or '0'
    except Exception as e:
        print(f"Error retrieving minimum block number: {e}")
        print(traceback.format_exc())
        return '0'

def save_image_to_file(block_data, output_dir):
    """Save an image from base64 to a PNG file."""
    if not block_data or 'image' not in block_data or not block_data['image']:
        print(f"No image data for block {block_data.get('block_number', 'unknown')}")
        return False
    
    block_number = block_data['block_number']
    image_base64 = block_data['image']
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the image as PNG
    image_path = os.path.join(output_dir, f"{block_number}.png")
    try:
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_base64))
        print(f"Saved image to {image_path}")
        return True
    except Exception as e:
        print(f"Error saving image to {image_path}: {e}")
        print(traceback.format_exc())
        return False

def save_json_to_file(data, output_path):
    """Save data to a JSON file."""
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved JSON to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving JSON to {output_path}: {e}")
        print(traceback.format_exc())
        return False

def process_recent_blocks(static_dir):
    """Process recent blocks and save them as static files."""
    # Get list of recent blocks
    recent_blocks = get_recent_block_numbers()
    
    if not recent_blocks:
        print("No recent blocks found")
        return False
    
    # Create a copy of recent blocks that doesn't include image data
    # (to use for index)
    recent_blocks_light = []
    
    # Process each block
    for block_info in recent_blocks:
        block_number = block_info['block_number']
        print(f"Processing block {block_number}")
        
        # Get graph image
        graph_data = get_image_from_gcs(block_number)
        if graph_data:
            # Save PNG image
            graphs_dir = os.path.join(static_dir, 'graphs')
            save_image_to_file(graph_data, graphs_dir)
            
            # Save stats as JSON
            stats = {
                'block_number': block_number,
                'node_count': graph_data['node_count'],
                'edge_count': graph_data['edge_count'],
                'demo_mode': graph_data.get('demo_mode', False)
            }
            stats_path = os.path.join(static_dir, 'data', f"{block_number}.json")
            save_json_to_file(stats, stats_path)
            
            # Add to light list (without image data)
            recent_blocks_light.append({
                'block_number': block_number,
                'node_count': graph_data['node_count'],
                'edge_count': graph_data['edge_count'],
                'demo_mode': graph_data.get('demo_mode', False)
            })
        else:
            print(f"No graph data for block {block_number}")
        
        # Get gantt chart
        gantt_data = get_gantt_from_gcs(block_number)
        if gantt_data:
            # Save PNG image
            gantt_dir = os.path.join(static_dir, 'gantt')
            save_image_to_file(gantt_data, gantt_dir)
        else:
            print(f"No gantt data for block {block_number}")
    
    # Save the recent blocks index file
    index_path = os.path.join(static_dir, 'data', 'recent_blocks.json')
    save_json_to_file(recent_blocks_light, index_path)
    
    # Save the minimum block number
    min_block = get_min_block_number()
    min_block_data = {'min_block_number': min_block}
    min_block_path = os.path.join(static_dir, 'data', 'min_block.json')
    save_json_to_file(min_block_data, min_block_path)
    
    print(f"Processed {len(recent_blocks)} recent blocks")
    return True

def main():
    # Determine the location of the static directory
    # This should be in the root of the repo
    repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    static_dir = os.path.join(repo_dir, 'static')
    
    print(f"Static directory: {static_dir}")
    
    # Create the static directory structure if it doesn't exist
    os.makedirs(os.path.join(static_dir, 'graphs'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'gantt'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'data'), exist_ok=True)
    
    # Process recent blocks
    process_recent_blocks(static_dir)
    
    print("Static file generation complete")

if __name__ == "__main__":
    main() 