#!/bin/bash
set -e

echo "==================================="
echo "🚀 Starting Janus GTM OS"
echo "==================================="

# Navigate to backend directory
cd /app/backend/src

# Run Django migrations
echo "📦 Running Django migrations..."
python manage.py migrate --noinput

# Collect static files (if needed)
# python manage.py collectstatic --noinput

echo "🔧 Starting backend server on port 8000..."
# Start Django development server in background
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Navigate to frontend directory
cd /app/frontend

echo "🎨 Starting frontend server on port 3000..."
# Start Next.js server in background
npm start &
FRONTEND_PID=$!

# Function to handle shutdown
shutdown() {
    echo ""
    echo "⏹️  Shutting down gracefully..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Shutdown complete"
    exit 0
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

echo ""
echo "✅ Janus is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop"
echo "==================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
