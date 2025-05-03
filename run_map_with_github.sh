#!/bin/bash

# Ensure Docker Desktop is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker Desktop is not running. Please start it and try again."
    exit 1
fi

# Set working directory and variables
WORKDIR=/app
CONTAINER_NAME=geodnet-map
IMAGE_NAME=geodnet-map:latest
SPREADSHEET_ID=1E6u3Eyx_GHFpIbWGmEc6b00KoiWD0DsSSJwHZx686EA
GITHUB_REPO=b3stearns/new-truenav-map
GITHUB_TOKEN=$GITHUB_TOKEN
BRANCH=main

# Create Docker network if it doesn't exist
docker network create geodnet-network 2>/dev/null || true

# Build Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME -f Dockerfile .

# Stop and remove existing container if it exists
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Run container
echo "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    --network geodnet-network \
    -v $(pwd):$WORKDIR \
    -e CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    -e SPREADSHEET_ID=$SPREADSHEET_ID \
    -e GITHUB_TOKEN=$GITHUB_TOKEN \
    $IMAGE_NAME

# Schedule data fetch and GitHub push every hour
echo "Scheduling data fetch and GitHub push..."
docker exec $CONTAINER_NAME bash -c "
    echo '0 * * * * python /app/fetch_data.py && /app/push_to_github.sh >> /app/update_map.log 2>&1' | crontab -
"

echo "Map container is running. Logs are in $WORKDIR/geodnet_map.log and $WORKDIR/update_map.log"
echo "Access the map at connections_map.html in the working directory."