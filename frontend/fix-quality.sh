#!/bin/bash
# Frontend Code Quality Fix Script
# This script automatically fixes formatting and linting issues

set -e  # Exit on error

echo "🔧 Fixing Frontend Code Quality Issues..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Run Prettier to format code
echo "✨ Formatting code with Prettier..."
npm run format
echo "✅ Code formatted!"
echo ""

# Run ESLint with auto-fix
echo "🔎 Fixing linting issues with ESLint..."
npm run lint:fix
echo "✅ Linting issues fixed!"
echo ""

echo "🎉 All quality issues fixed!"
