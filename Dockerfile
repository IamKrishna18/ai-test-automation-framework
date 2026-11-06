# ==========================================
# Fast & Lightweight Production Dockerfile
# Serves FastAPI backend + Pre-compiled React UI
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

# Copy backend, sample target API, and pre-compiled frontend assets
COPY backend/ ./backend/
COPY sample_target_api/ ./sample_target_api/
COPY frontend/dist/ ./frontend/dist/

# Expose port (Render/Railway inject $PORT)
ENV PORT=8000
EXPOSE 8000

# Start unified FastAPI server using python -m uvicorn
CMD ["sh", "-c", "python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
