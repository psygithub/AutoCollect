import os
import yaml
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify
from waitress import serve
from loguru import logger
from automation_task import execute_automation

# --- Configuration ---
CONFIG_FILE = 'config.yaml'

# --- In-memory state ---
# For a real application, you might use a database or a more robust solution
task_state = {
    "status": "idle", # idle, running, completed, failed
    "results": []
}

app = Flask(__name__)

# --- Helper Functions ---
def load_config():
    """Loads the YAML configuration file."""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config_data):
    """Saves the configuration data to the YAML file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)

# --- Automation Task ---
def run_automation_task_wrapper():
    """Wrapper to run the task and update state."""
    global task_state
    task_state['status'] = 'running'
    task_state['results'] = []
    logger.info("Starting automation task...")
    
    try:
        config = load_config()
        results = execute_automation(config)
        task_state['results'] = results
        task_state['status'] = 'completed'
        logger.success("Automation task finished successfully.")
    except Exception as e:
        task_state['status'] = 'failed'
        logger.error(f"Automation task failed in wrapper: {e}")

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page to display and update configuration."""
    if request.method == 'POST':
        config = load_config()
        # Update config from form data
        config['device']['platform_version'] = request.form['platform_version']
        config['device']['device_name'] = request.form['device_name']
        config['tiktok']['app_package'] = request.form['tiktok_app_package']
        config['tiktok']['app_activity'] = request.form['tiktok_app_activity']
        config['test']['max_products_to_process'] = int(request.form['max_products_to_process'])
        config['test']['share_target'] = request.form['share_target']
        
        save_config(config)
        return redirect(url_for('index'))
        
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/start', methods=['POST'])
def start_task():
    """Starts the automation task in a background thread."""
    global task_state
    if task_state['status'] == 'running':
        return jsonify({"status": "error", "message": "Task is already running."}), 400

    logger.info("Received request to start automation task.")
    task_thread = threading.Thread(target=run_automation_task_wrapper)
    task_thread.start()
    return jsonify({"status": "success", "message": "Automation task started in the background."})

@app.route('/status')
def status():
    """Returns the current status of the automation task."""
    return jsonify(task_state)

@app.route('/results')
def results():
    """Displays the collected links."""
    return render_template('results.html', results=task_state['results'], status=task_state['status'])

# --- Main Entry Point ---
if __name__ == '__main__':
    logger.info("Starting web server...")
    serve(app, host='0.0.0.0', port=8080)
