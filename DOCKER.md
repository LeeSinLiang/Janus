# Docker Setup Guide

This guide explains how to run Janus using Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Initial Setup

Before running Docker Compose for the first time, you need to initialize the required files and directories:

```bash
# Run the setup script
./docker-setup.sh
```

This script will:
- Create an empty `db.sqlite3` file for the SQLite database
- Create the `generated_videos` directory for media files
- Copy `.env.example` to `.env` (you'll need to add your API keys)

### Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create empty database file
touch backend/src/db.sqlite3

# Create media directories
mkdir -p backend/generated_videos
mkdir -p backend/src/media

# Copy environment file
cp backend/.env.example .env
```

## Configuration

Edit the `.env` file and add your API keys:

```bash
# Required: Get your API key from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_api_key_here

# Optional: For media generation (image/video)
MEDIA_GEMINI_API_KEY=your_media_api_key_here
```

## Running with Docker

### Build the containers

```bash
docker compose build
```

### Start the application

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

### Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/

### Stop the application

```bash
docker compose down
```

## Volume Mounts

The `docker-compose.yml` file mounts several volumes to persist data:

- `./backend/src/db.sqlite3` - SQLite database (persists campaign data)
- `./backend/src/media` - User-uploaded media files
- `./backend/generated_videos` - AI-generated videos
- `./.env` - Environment variables

## Troubleshooting

### Error: "Are you trying to mount a directory onto a file?"

This error occurs when required files don't exist before Docker tries to mount them. Solution:

1. Run the setup script: `./docker-setup.sh`
2. Or manually create the missing files as shown in the Manual Setup section

### Database migrations

If you need to run Django migrations inside the container:

```bash
# Access the container shell
docker exec -it janus-app /bin/bash

# Run migrations
cd backend/src
python manage.py migrate
```

### View logs

```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs for specific service
docker compose logs -f janus
```

### Reset database

To reset the database, stop the containers and delete the db.sqlite3 file:

```bash
docker compose down
rm backend/src/db.sqlite3
touch backend/src/db.sqlite3
docker compose up
```

## Development Tips

- The application runs in development mode with hot-reload enabled
- Code changes are reflected immediately (no need to rebuild)
- For production deployment, see the main CLAUDE.md documentation

## Next Steps

After starting the application:

1. Visit http://localhost:3000 to access the frontend
2. Create your first campaign
3. Check the backend API at http://localhost:8000/api/

For more detailed information about the application architecture and features, see `CLAUDE.md`.
