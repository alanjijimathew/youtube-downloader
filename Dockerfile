# Use a lightweight Python image
FROM python:3.11-slim

# Install ffmpeg and curl (needed for yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Create a directory for downloads (Render's disk is ephemeral, but this prevents errors)
RUN mkdir -p /tmp/downloads

# Expose the port Render will use
EXPOSE 8000

# Command to run the app (using the port Render provides)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]