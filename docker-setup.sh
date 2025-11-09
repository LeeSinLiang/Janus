#!/bin/bash

# Docker Setup Script
# This script initializes files and directories required for Docker Compose volume mounts

set -e

echo "🐳 Initializing Docker environment for Janus..."

# Create db.sqlite3 file if it doesn't exist
if [ ! -f "backend/src/db.sqlite3" ]; then
    echo "📄 Creating empty db.sqlite3 file..."
    touch backend/src/db.sqlite3
else
    echo "✅ db.sqlite3 already exists"
fi

# Create generated_videos directory if it doesn't exist
if [ ! -d "backend/generated_videos" ]; then
    echo "📁 Creating generated_videos directory..."
    mkdir -p backend/generated_videos
else
    echo "✅ generated_videos directory already exists"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from .env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example .env
        echo "⚠️  WARNING: Please update .env with your actual API keys!"
    else
        echo "❌ Error: backend/.env.example not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Create media directory if it doesn't exist
if [ ! -d "backend/src/media" ]; then
    echo "📁 Creating media directory..."
    mkdir -p backend/src/media
else
    echo "✅ media directory already exists"
fi

echo ""
echo "✅ Docker environment initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GOOGLE_API_KEY"
echo "2. Run: docker compose build"
echo "3. Run: docker compose up"
echo ""
