import os
import yaml
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from waitress import serve
from loguru import logger
from automation_task import execute_automation
from link_opener import open_links_from_file
import asyncio

# --- Configuration ---
CONFIG_FILE = 'config.yaml'
IMAGE_FOLDER = 'uploads'

# --- In-memory state ---
# For a real application, you might use a database or a more robust solution
task_state = {
    "status": "idle", # idle, running, completed, failed
    "results": []
}

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

# Ensure the upload folder exists on startup
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)
    logger.info(f"Created missing image folder: {IMAGE_FOLDER}")

# --- Helper Functions ---
def load_config():
    """Loads the YAML configuration file."""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config_data):
    """Saves the configuration data to the YAML file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)

# --- Link Opener Task ---
def run_link_opener_task_wrapper(filename, config):
    """Wrapper to run the link opener task with a specific file and configuration."""
    logger.info(f"Starting link opener task for file: {filename}...")
    try:
        # We run the async function in a new event loop
        asyncio.run(open_links_from_file(filename, config))
        logger.success(f"Link opener task for {filename} finished.")
    except Exception as e:
        logger.error(f"Link opener task for {filename} failed in wrapper: {e}")

# --- Automation Task ---
def run_automation_task_wrapper(pc_image_path):
    """Wrapper to run the task and update state."""
    global task_state
    task_state['status'] = 'running'
    task_state['results'] = []
    logger.info("Starting automation task...")
    
    try:
        config = load_config()
        # Dynamically set the pc_image_path for this run
        # config['task']['pc_image_path'] = pc_image_path
        
        results = execute_automation(config)
        if results is None: # Check for failure signal
             task_state['status'] = 'failed'
             logger.error("Automation task failed. Please check logs for details.")
        else:
            task_state['results'] = results
            task_state['status'] = 'completed'
            logger.success("Automation task finished successfully.")
    except Exception as e:
        task_state['status'] = 'failed'
        logger.error(f"Automation task failed in wrapper: {e}")

# --- Routes ---
@app.route('/', methods=['GET'])
def index():
    """Main page to display configuration and list of link files."""
    config = load_config()
    
    # Ensure web_automation key exists with default values to prevent Jinja errors
    if 'web_automation' not in config:
        config['web_automation'] = {
            'proxy_server': '',
            'miaoshou_url': '',
            'miaoshou_username': '',
            'miaoshou_password': '',
            'extension_path': ''
        }

    # Ensure the image path uses forward slashes for JavaScript compatibility
    if config.get('task', {}).get('pc_image_path'):
        config['task']['pc_image_path'] = config['task']['pc_image_path'].replace('\\', '/')

    # List and sort link files
    links_dir = 'shared_links'
    link_files = []
    if os.path.exists(links_dir):
        try:
            # Get all .txt files and sort them descending by name (which includes the timestamp)
            files = [f for f in os.listdir(links_dir) if f.startswith('links-') and f.endswith('.txt')]
            files.sort(reverse=True)
            link_files = files
        except Exception as e:
            logger.error(f"Error reading or sorting link files: {e}")

    return render_template('index.html', config=config, link_files=link_files)

@app.route('/api/images')
def list_images():
    """API endpoint to list images from the server's image folder."""
    image_folder = app.config['IMAGE_FOLDER']
    if not os.path.exists(image_folder):
        os.makedirs(image_folder) # Create folder if it doesn't exist
        logger.info(f"Created image folder: {image_folder}")
        return jsonify([])

    try:
        files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
        # Filter for common image extensions
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return jsonify(image_files)
    except Exception as e:
        logger.error(f"Error reading image folder '{image_folder}': {e}")
        return jsonify({"error": "Could not read image directory"}), 500

@app.route('/start', methods=['POST'])
def start_task():
    """Starts the automation task in a background thread."""
    global task_state
    if task_state['status'] == 'running':
        return jsonify({"status": "error", "message": "Task is already running."}), 400

    # Get the selected image from the request
    image_path=None
    selected_image = request.json.get('pc_image_path')
    if not selected_image:
        # Construct the full, absolute path for the image
        image_path = os.path.abspath(os.path.join(app.config['IMAGE_FOLDER'], selected_image))
        logger.info(f"Received request to start automation task with image: {image_path}")
    
    # Pass the dynamic image path to the task wrapper
    task_thread = threading.Thread(target=run_automation_task_wrapper, args=(image_path,))
    task_thread.start()
    
    return jsonify({"status": "success", "message": "Automation task started in the background."})

@app.route('/save_task_config', methods=['POST'])
def save_task_config():
    """Saves the task-related configuration."""
    config = load_config()
    
    config['task']['max_products_to_process'] = int(request.form['max_products_to_process'])
    
    # The pc_image_path is no longer saved to config
    # It's now provided dynamically when the task starts
    
    save_config(config)
    logger.success("Task configuration saved.")
    return jsonify({"status": "success", "message": "APP自动化任务已保存。"})

@app.route('/save_web_config', methods=['POST'])
def save_web_config():
    """Saves the web automation configuration."""
    config = load_config()
    
    if 'web_automation' not in config:
        config['web_automation'] = {}
        
    config['web_automation']['proxy_server'] = request.form['proxy_server']
    config['web_automation']['miaoshou_url'] = request.form['miaoshou_url']
    config['web_automation']['miaoshou_username'] = request.form['miaoshou_username']
    config['web_automation']['miaoshou_password'] = request.form['miaoshou_password']
    config['web_automation']['extension_path'] = request.form['extension_path']
    
    save_config(config)
    logger.success("Web automation configuration saved.")
    return jsonify({"status": "success", "message": "Web自动化配置已保存。"})

@app.route('/save_mobile_config', methods=['POST'])
def save_mobile_config():
    """Saves the mobile device configuration."""
    config = load_config()
    
    config['device']['platform_version'] = request.form['platform_version']
    config['device']['device_name'] = request.form['device_name']
    config['tiktok']['app_package'] = request.form['tiktok_app_package']
    config['tiktok']['app_activity'] = request.form['tiktok_app_activity']
    
    save_config(config)
    logger.success("Mobile configuration saved.")
    return jsonify({"status": "success", "message": "APP自动化配置已保存。"})

@app.route('/api/link_files')
def list_link_files():
    """API endpoint to list collected link files."""
    links_dir = 'shared_links'
    try:
        if not os.path.exists(links_dir):
            return jsonify([])
        
        # Get all .txt files starting with links- and sort them descending by name
        files = [f for f in os.listdir(links_dir) if f.startswith('links-') and f.endswith('.txt')]
        files.sort(reverse=True)
        
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error reading link files directory: {e}")
        return jsonify({"error": "Could not read directory"}), 500

@app.route('/open_links', methods=['POST'])
def start_link_opener():
    """Starts the link opener task in a background thread."""
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({"status": "error", "message": "No filename provided."}), 400

    config = load_config()
    web_config = config.get('web_automation', {})

    logger.info(f"Received request to open links from file: {filename}")
    task_thread = threading.Thread(target=run_link_opener_task_wrapper, args=(filename, web_config))
    task_thread.start()
    return jsonify({"status": "success", "message": f"正在后台打开文件 '{filename}' 中的链接..."})

@app.route('/status')
def status():
    """Returns the current status of the automation task."""
    return jsonify(task_state)

@app.route('/results')
def results():
    """Displays the collected links."""
    return render_template('results.html', results=task_state['results'], status=task_state['status'])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves a file from the uploads directory."""
    logger.info(f"Attempting to serve file: {filename} from {app.config['IMAGE_FOLDER']}")
    try:
        return send_from_directory(app.config['IMAGE_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

# --- Main Entry Point ---
if __name__ == '__main__':
    logger.info("Starting web server...")
    serve(app, host='0.0.0.0', port=8080)
