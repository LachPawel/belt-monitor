# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install --frozen-lockfile

COPY frontend/ .

# Build the frontend
RUN npm run build

# Stage 2: Build backend with frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    ffmpeg \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create directories
RUN mkdir -p data/uploads reports

# Configure nginx to serve frontend and proxy API
RUN mkdir -p /etc/nginx/conf.d

RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 8080;
    server_name _;
    client_max_body_size 100M;

    # Serve frontend
    location / {
        root /app/frontend;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Also proxy /docs and /openapi.json for API docs
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://localhost:8000;
    }
}
EOF

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start both services
CMD ["sh", "-c", "nginx -g 'daemon off;' & uvicorn app.api:app --host 127.0.0.1 --port 8000"]
