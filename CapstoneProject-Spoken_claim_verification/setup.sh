#!/bin/bash

# Setup Script for Spoken Claim Verification System
# This script initializes the system, installs dependencies, and starts services

set -e

echo "=========================================="
echo "Spoken Claim Verification System Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Whisper service dependencies
echo "Installing Whisper service dependencies..."
pip install -r whisper_service/requirements.txt

# Copy environment file
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Environment file created. Please update .env with your API keys"
else
    echo "Environment file already exists"
fi

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/videos
mkdir -p data/audio
mkdir -p data/transcripts
mkdir -p logs

# Check Docker installation
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker to use containerized services."
else
    echo "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose not found. Please install Docker Compose."
    else
        echo "Docker Compose found: $(docker-compose --version)"
        
        # Start services
        echo "Starting Docker services..."
        docker-compose up -d
        echo "Docker services started"
        
        # Wait for services to be ready
        echo "Waiting for services to be ready..."
        sleep 10
    fi
fi

# Download Whisper model
echo "Downloading Whisper model (this may take a while)..."
python3 -c "import whisper; whisper.load_model('large-v3')"
echo "Whisper model downloaded successfully"

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Start the application with: python app.py"
echo "3. Access Grafana at: http://localhost:3000"
echo "4. Access MySQL at: localhost:3306"
echo ""
