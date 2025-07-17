#!/usr/bin/env python3
"""
Financial Analysis Workflow Web Interface

A Flask-based web application that provides a user interface for running
the financial analysis workflow and viewing real-time logs.
"""

import os
import asyncio
import threading
import datetime
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import subprocess
import sys
from pathlib import Path
import time
import logging
from logging.handlers import RotatingFileHandler
import markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DEBUG'] = True
socketio = SocketIO(app, cors_allowed_origins="*")

# Add error handler for better debugging
@app.errorhandler(500)
def handle_500(e):
    logger.error(f'Internal server error: {e}')
    import traceback
    traceback.print_exc()
    return render_template('error.html', error=str(e)), 500

# Global variables to track workflow status
workflow_status = {
    'running': False,
    'completed': False,
    'error': None,
    'start_time': None,
    'end_time': None,
    'logs': []
}

class LogCapture:
    """Capture and broadcast logs to web interface"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.logs = []
    
    def write(self, message):
        if message.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message.strip()}"
            self.logs.append(log_entry)
            workflow_status['logs'].append(log_entry)
            
            # Broadcast to connected clients
            self.socketio.emit('log_update', {
                'message': log_entry,
                'timestamp': timestamp
            })
    
    def flush(self):
        pass

# Initialize log capture
log_capture = LogCapture(socketio)

@app.route('/')
def index():
    """Main page with workflow interface"""
    return render_template('index.html')

@app.route('/api/workflow/start', methods=['POST'])
def start_workflow():
    """Start the financial analysis workflow"""
    global workflow_status
    
    if workflow_status['running']:
        return jsonify({'error': 'Workflow is already running'}), 400
    
    try:
        # Get company name from request
        data = request.get_json()
        company_name = data.get('company', 'Tesco')
        
        # Reset workflow status
        workflow_status = {
            'running': True,
            'completed': False,
            'error': None,
            'start_time': datetime.datetime.now().isoformat(),
            'end_time': None,
            'logs': []
        }
        
        # Start workflow in background thread
        thread = threading.Thread(target=run_workflow_async, args=(company_name,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Workflow started successfully', 'status': 'started'})
        
    except Exception as e:
        workflow_status['error'] = str(e)
        workflow_status['running'] = False
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/status')
def get_workflow_status():
    """Get current workflow status"""
    return jsonify(workflow_status)

@app.route('/api/workflow/logs')
def get_workflow_logs():
    """Get workflow logs"""
    return jsonify({'logs': workflow_status['logs']})

@app.route('/api/workflow/stop', methods=['POST'])
def stop_workflow():
    """Stop the workflow (if possible)"""
    global workflow_status
    
    if not workflow_status['running']:
        return jsonify({'error': 'No workflow is currently running'}), 400
    
    # Note: This is a simple implementation. In production, you'd want proper process management
    workflow_status['running'] = False
    workflow_status['error'] = 'Workflow stopped by user'
    workflow_status['end_time'] = datetime.datetime.now().isoformat()
    
    return jsonify({'message': 'Workflow stop requested'})

@app.route('/api/reports')
def list_reports():
    """List available reports"""
    reports_dir = Path('outputs')
    reports = []
    
    if reports_dir.exists():
        for report_dir in reports_dir.iterdir():
            if report_dir.is_dir():
                report_file = report_dir / 'financial_analysis_report.md'
                if report_file.exists():
                    reports.append({
                        'name': report_dir.name,
                        'path': str(report_file),
                        'created': datetime.datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
                    })
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x['created'], reverse=True)
    return jsonify({'reports': reports})

@app.route('/api/reports/<report_name>')
def get_report(report_name):
    """Get a specific report as JSON"""
    report_path = Path('outputs') / report_name / 'financial_analysis_report.md'
    
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        with open(report_path, 'r') as f:
            content = f.read()
        return jsonify({'content': content, 'name': report_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports/<report_name>')
def view_report(report_name):
    """View a specific report in HTML format"""
    report_path = Path('outputs') / report_name / 'financial_analysis_report.md'
    
    if not report_path.exists():
        return render_template('error.html', error='Report not found'), 404
    
    try:
        with open(report_path, 'r') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.attr_list',
                'markdown.extensions.def_list'
            ]
        )
        
        # Get current time for display
        current_time = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        return render_template('report.html', 
                             content=html_content, 
                             name=report_name, 
                             current_time=current_time)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route('/api/reports/<report_name>/download')
def download_report(report_name):
    """Download a specific report"""
    report_path = Path('outputs') / report_name / 'financial_analysis_report.md'
    
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    return send_file(report_path, as_attachment=True)

def run_workflow_async(company_name):
    """Run the financial workflow asynchronously"""
    global workflow_status
    
    try:
        # Set SSL certificate environment variable
        env = os.environ.copy()
        env['SSL_CERT_FILE'] = '/Users/crazykevin/Desktop/hackathon_fa_agents/.venv/lib/python3.11/site-packages/certifi/cacert.pem'
        
        # Emit start message
        socketio.emit('workflow_started', {'company': company_name})
        
        # Run the workflow script
        process = subprocess.Popen(
            [sys.executable, 'financial_analysis_workflow.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            cwd='/Users/crazykevin/Desktop/hackathon_fa_agents'
        )
        
        # Stream output in real-time
        for line in iter(process.stdout.readline, ''):
            if line:
                log_capture.write(line)
                time.sleep(0.1)  # Small delay to prevent overwhelming the client
        
        process.wait()
        
        # Check if process completed successfully
        if process.returncode == 0:
            workflow_status['completed'] = True
            workflow_status['running'] = False
            workflow_status['end_time'] = datetime.datetime.now().isoformat()
            socketio.emit('workflow_completed', {'status': 'success'})
        else:
            workflow_status['error'] = f'Process exited with code {process.returncode}'
            workflow_status['running'] = False
            workflow_status['end_time'] = datetime.datetime.now().isoformat()
            socketio.emit('workflow_error', {'error': workflow_status['error']})
            
    except Exception as e:
        workflow_status['error'] = str(e)
        workflow_status['running'] = False
        workflow_status['end_time'] = datetime.datetime.now().isoformat()
        socketio.emit('workflow_error', {'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Financial Analysis Workflow'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create outputs directory if it doesn't exist
    Path('outputs').mkdir(exist_ok=True)
    
    # Run the Flask app with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
