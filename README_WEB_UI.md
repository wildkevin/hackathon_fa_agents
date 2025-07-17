# Financial Analysis Workflow Web UI

A web-based interface for running the financial analysis workflow with real-time log monitoring and report management.

## Features

- **Interactive Dashboard**: Clean, modern web interface built with Flask and Bulma CSS
- **Real-time Logs**: Live streaming of workflow execution logs using WebSocket
- **Status Monitoring**: Visual status indicators showing workflow progress
- **Report Management**: View and download generated financial reports
- **Company Selection**: Easy input for different company analysis

## Quick Start

### Option 1: Using the Startup Script (Recommended)
```bash
./start_web_ui.sh
```

### Option 2: Manual Start
```bash
# Load environment variables
source .env

# Set SSL certificate (if needed)
export SSL_CERT_FILE=/Users/crazykevin/Desktop/hackathon_fa_agents/.venv/lib/python3.11/site-packages/certifi/cacert.pem

# Start the web application
python app.py
```

## Access the Web Interface

Open your browser and navigate to: **http://localhost:8080**

## How to Use

1. **Start Analysis**: 
   - Enter a company name (default: "Tesco")
   - Click "Start Analysis" button
   - Watch real-time logs in the terminal-style log viewer

2. **Monitor Progress**:
   - Status indicator shows current workflow state (Idle/Running/Completed/Error)
   - Progress bar appears during execution
   - Real-time log updates stream automatically

3. **View Reports**:
   - Generated reports appear in the "Generated Reports" section
   - Click "View" to open a report in a new tab
   - Click "Download" to save the report locally

4. **Stop Workflow**:
   - Click "Stop" button to halt execution (if needed)
   - Status will update to show stopping/stopped state

## Architecture

- **Backend**: Flask + Flask-SocketIO for real-time communication
- **Frontend**: HTML + JavaScript + Bulma CSS framework
- **Communication**: WebSocket for real-time log streaming
- **Process Management**: Subprocess execution of financial analysis workflow

## API Endpoints

- `GET /` - Main web interface
- `POST /api/workflow/start` - Start financial analysis workflow
- `POST /api/workflow/stop` - Stop running workflow
- `GET /api/workflow/status` - Get current workflow status
- `GET /api/workflow/logs` - Get workflow logs
- `GET /api/reports` - List available reports
- `GET /api/reports/<name>` - View specific report
- `GET /api/reports/<name>/download` - Download report

## WebSocket Events

- `connect` - Client connection established
- `log_update` - Real-time log message
- `workflow_started` - Workflow execution begins
- `workflow_completed` - Workflow finished successfully
- `workflow_error` - Workflow encountered an error

## File Structure

```
├── app.py                  # Main Flask application
├── templates/
│   └── index.html         # Web interface template
├── outputs/               # Generated reports directory
├── start_web_ui.sh       # Startup script
└── README_WEB_UI.md      # This file
```

## Requirements

- Python 3.11+
- Flask
- Flask-SocketIO
- All dependencies from financial_analysis_workflow.py

## Troubleshooting

### Port Already in Use
If port 8080 is in use, modify the port in `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=XXXX)
```

### SSL Certificate Issues
The startup script automatically sets the SSL certificate path. If you encounter SSL issues:
1. Ensure the certificate path is correct in `.env`
2. Check that certifi is installed: `pip install certifi`

### Workflow Not Starting
1. Verify all environment variables are set in `.env`
2. Check that `financial_analysis_workflow.py` runs successfully independently
3. Review the real-time logs for error messages

## Security Notes

- This is a development/demo interface
- For production use, implement proper authentication
- Consider HTTPS for secure communication
- Review and harden security settings

## Support

For issues or questions, check:
1. Real-time logs in the web interface
2. Console output where the Flask app is running
3. Ensure all dependencies are properly installed
