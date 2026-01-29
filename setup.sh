#!/bin/bash
# Setup script for Enterprise AI Platform
# This script creates the conda environment and initializes Poetry

set -e  # Exit on error

echo "🚀 Setting up Enterprise AI Platform..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# Create conda environment
echo "📦 Creating conda environment..."
conda env create -f environment.yml

echo "✅ Conda environment created successfully!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment:"
echo "     conda activate enterprise-ai-platform"
echo ""
echo "  2. Initialize Poetry dependencies:"
echo "     poetry install"
echo ""
echo "  3. Start development!"
