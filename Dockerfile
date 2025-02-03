FROM python:3.9.7-slim

LABEL maintainer="cassius66"
LABEL description="Distributed MapReduce Framework"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose ports
EXPOSE 8002 8008 8009

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8008))" || exit 1

# Default command
CMD ["python", "main.py", "server"]
