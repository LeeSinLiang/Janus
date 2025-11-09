# Docker Setup for Janus

This guide explains how to run Janus using Docker.

## Quick Start

### 1. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google API key
nano .env  # or use your preferred editor
```

**Required:** Set `GOOGLE_API_KEY` in `.env` (get it from https://ai.google.dev/gemini-api/docs/api-key)

### 2. Build and Run with Docker

**Option A: Using Docker Compose (Recommended)**

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

**Option B: Using Docker directly**

```bash
# Build the image
docker build -t janus-app .

# Run the container
docker run -p 3000:3000 -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/backend/src/db.sqlite3:/app/backend/src/db.sqlite3 \
  -v $(pwd)/backend/src/media:/app/backend/src/media \
  janus-app

# Run in detached mode
docker run -d \
  --name janus \
  -p 3000:3000 -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/backend/src/db.sqlite3:/app/backend/src/db.sqlite3 \
  -v $(pwd)/backend/src/media:/app/backend/src/media \
  janus-app

# View logs
docker logs -f janus

# Stop the container
docker stop janus
docker rm janus
```

### 3. Access the Application

Once the container is running, access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/

## Container Architecture

The Docker setup includes:

- **Multi-stage build**: Frontend built in Node.js stage, then copied to final image
- **Python 3.12 Slim**: Minimal Python image (~150MB base)
- **Both services**: Django backend + Next.js frontend in one container
- **Single entrypoint**: `docker-entrypoint.sh` starts both services

## Volume Mounts

The following directories are mounted for persistence:

- `backend/src/db.sqlite3` - SQLite database
- `backend/src/media/` - Uploaded media files
- `backend/generated_videos/` - AI-generated videos
- `.env` - Environment variables

## Environment Variables

**Required:**
- `GOOGLE_API_KEY` - Google Gemini API key for AI agents

**Optional:**
- `MEDIA_GEMINI_API_KEY` - For Imagen 3 / Veo 2 media generation
- `SECRET_KEY` - Django secret key (auto-generated if not set)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `NEXT_PUBLIC_API_URL` - Backend URL for frontend (default: http://localhost:8000)

## Running Django Commands

```bash
# Create superuser for admin access
docker-compose exec janus bash -c "cd /app/backend/src && python manage.py createsuperuser"

# Run migrations
docker-compose exec janus bash -c "cd /app/backend/src && python manage.py migrate"

# Access Django shell
docker-compose exec janus bash -c "cd /app/backend/src && python manage.py shell"

# View database
docker-compose exec janus bash -c "cd /app/backend/src && python manage.py dbshell"
```

## Testing the Demo

```bash
# Run the 3-scenario demo workflow
docker-compose exec janus bash -c "cd /app/backend && python demo.py"

# Test individual agents
docker-compose exec janus bash -c "cd /app/backend/src && python -m agents.supervisor"
docker-compose exec janus bash -c "cd /app/backend/src && python -m agents.content_creator"
```

## Production Deployment

For production, consider:

1. **Use PostgreSQL** instead of SQLite:
   - Uncomment the `db` service in `docker-compose.yml`
   - Update Django settings to use PostgreSQL

2. **Set production environment variables**:
   ```bash
   DEBUG=False
   SECRET_KEY=<generate-a-secure-random-key>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. **Use a reverse proxy** (nginx/Caddy) for HTTPS

4. **Run migrations separately**:
   ```bash
   docker-compose run --rm janus bash -c "cd /app/backend/src && python manage.py migrate"
   ```

5. **Collect static files**:
   ```bash
   docker-compose run --rm janus bash -c "cd /app/backend/src && python manage.py collectstatic --noinput"
   ```

## Troubleshooting

**Container won't start:**
- Check logs: `docker-compose logs`
- Ensure `.env` file exists with `GOOGLE_API_KEY`
- Check ports 3000 and 8000 are not in use

**Database errors:**
- Delete `db.sqlite3` and restart: migrations will recreate it
- Or run migrations manually: `docker-compose exec janus bash -c "cd /app/backend/src && python manage.py migrate"`

**Port conflicts:**
- Change ports in `docker-compose.yml`:
  ```yaml
  ports:
    - "3001:3000"  # Frontend on 3001
    - "8001:8000"  # Backend on 8001
  ```

**Build errors:**
- Clear Docker cache: `docker-compose build --no-cache`
- Check Docker has enough memory (4GB+ recommended)

## Development Workflow

For active development, you may want to mount source code:

```yaml
# Add to docker-compose.yml under 'volumes:'
volumes:
  - ./backend:/app/backend
  - ./frontend/janus:/app/frontend
  - /app/frontend/node_modules  # Prevent overwriting
  - /app/frontend/.next          # Prevent overwriting
```

This allows live code changes without rebuilding the container.
