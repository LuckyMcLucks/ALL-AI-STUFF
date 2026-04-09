#!/bin/bash

# Activate virtual environment (optional)
# source venv/bin/activate

# Start FastAPI server
cd Tweet_AI
source .venv/bin/activate
uvicorn infernece:app --reload --host 0.0.0.0 --port 8000