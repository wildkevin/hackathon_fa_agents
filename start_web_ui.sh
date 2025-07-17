#!/bin/bash
echo "Starting Financial Analysis Workflow Web UI..."
echo "Loading environment variables..."
source .env
export SSL_CERT_FILE=/Users/crazykevin/Desktop/hackathon_fa_agents/.venv/lib/python3.11/site-packages/certifi/cacert.pem

echo "Starting Flask application on port 8080..."
echo "Open your browser and navigate to: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
