# Use a lightweight Python image
FROM python:3.12-slim

# Install ffmpeg and other utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy the Deno binary directly from the official Deno image
COPY --from=denoland/deno:bin-2.1.4 /deno /usr/local/bin/deno

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
# Install yt-dlp with the [default] and [deno] extras so it includes the solver scripts and finds Deno
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default,deno]"

# Copy the application code
COPY app.py .

# Expose the port Render will use
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
