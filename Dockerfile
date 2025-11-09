# Multi-stage Dockerfile for Janus (Frontend + Backend)
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Accept build arguments for Next.js environment variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy package files
COPY frontend/janus/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source
COPY frontend/janus/ ./

# Build Next.js app (env vars are now available)
RUN npm run build

# Stage 2: Final Image with Backend + Built Frontend
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_VERSION=20

# Install Node.js (needed for Next.js server) and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source
COPY backend/ /app/backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend /app/frontend

# Copy startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/backend/src/media /app/backend/generated_videos

# Set working directory to backend for Django commands
WORKDIR /app/backend/src

# Run migrations (will also run in entrypoint for safety)
RUN python manage.py migrate --noinput || true

# Expose ports
EXPOSE 8000 3000

# Set entrypoint
WORKDIR /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
