# Use a lightweight Python image
FROM python:3.11-slim

# Install ffmpeg, curl, and a JavaScript runtime (Deno)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Deno (JavaScript runtime for yt-dlp)
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
# Install yt-dlp with the [default] extra to include all optional dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default]"

# Copy the application code
COPY app.py .

# Expose the port Render will use
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
