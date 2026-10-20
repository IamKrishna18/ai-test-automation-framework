# ==========================================
# Multi-stage Dockerfile for full-stack deployment
# Stage 1: Build React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend + Built Static UI
# ==========================================
FROM python:3.11-slim
WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend, sample target API, and built frontend
COPY backend/ ./backend/
COPY sample_target_api/ ./sample_target_api/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port (Render/Railway use $PORT environment variable)
ENV PORT=8000
EXPOSE 8000

# Start unified FastAPI server
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
