FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure scripts are executable
RUN chmod +x run_map_with_github.sh push_to_github.sh

# Start cron and run the scraper
CMD ["cron", "-f"]