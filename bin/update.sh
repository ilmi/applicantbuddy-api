#!/bin/bash

# Update script for fastapi-template project
# This script pulls latest changes, syncs dependencies, and restarts services

set -e  # Exit on any error

echo "Starting update process..."

# Pull latest changes from git
echo "Pulling latest changes from git..."
git pull

# Sync dependencies with uv
echo "Syncing dependencies with uv..."
uv sync

# Restart systemd services
echo "Restarting service-api.service..."
sudo systemctl restart service-api.service

echo "Restarting service-worker.service..."
sudo systemctl restart service-worker.service

echo "Update process completed successfully!"