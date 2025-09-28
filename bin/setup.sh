#!/bin/bash

# FastAPI Template Setup Script
# This script will:
# 1. Check if uv is installed
# 2. Install uv if not present
# 3. Run uv sync to install dependencies
# 4. Run database migrations

set -e  # Exit on any error

echo "🚀 Setting up FastAPI Template..."
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install uv
install_uv() {
    echo "📦 Installing uv..."
    if command_exists curl; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command_exists wget; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        echo "❌ Error: Neither curl nor wget is available. Please install one of them first."
        exit 1
    fi
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify installation
    if command_exists uv; then
        echo "✅ uv installed successfully!"
    else
        echo "❌ Error: uv installation failed. Please install uv manually."
        echo "Visit: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
}

# Check if uv is installed
echo "🔍 Checking for uv installation..."
if command_exists uv; then
    echo "✅ uv is already installed: $(uv --version)"
else
    echo "⚠️  uv not found. Installing uv..."
    install_uv
fi

echo ""

# Install dependencies
echo "📚 Installing project dependencies..."
uv sync
echo "✅ Dependencies installed successfully!"

echo ""

# Run database migrations
echo "🗄️  Running database migrations..."
if uv run alembic upgrade head; then
    echo "✅ Database migrations completed successfully!"
else
    echo "⚠️  Database migrations failed. This might be expected if the database is not set up yet."
    echo "   Make sure to configure your database settings in .env file."
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your environment variables"
echo "2. Set up your PostgreSQL and Redis instances"
echo "3. Run 'make dev' to start the development server"
echo "4. Run 'make worker' to start the Celery worker"
echo ""
echo "Happy coding! 🚀"