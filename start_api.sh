#!/bin/bash
echo "Starting Lead Scorer API..."
uvicorn api_wrapper:app --host 0.0.0.0 --port ${PORT:-8001} --reload
