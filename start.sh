#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if the first argument is "docker"
if [ "$1" == "docker" ]; then
    echo "Starting with Docker Compose..."
    docker-compose up
else
    # Run the FastAPI application
    echo "Starting FastAPI application..."
    poetry run python3 run.py
fi
