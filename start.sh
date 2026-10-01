#!/bin/bash

# Print a startup message
echo "Starting SmartSACCO AI Agent services..."

# Start the FastAPI backend in the background (&)
# It will run on port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit frontend in the foreground
# This keeps the Docker container alive. It will run on port 8501
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0