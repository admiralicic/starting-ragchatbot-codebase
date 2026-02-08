#!/bin/bash
# Frontend Code Quality Check Script
# This script runs formatting and linting checks on frontend code

set -e  # Exit on error

echo "🔍 Running Frontend Code Quality Checks..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Run Prettier check
echo "✨ Checking code formatting with Prettier..."
npm run format:check
echo "✅ Formatting check passed!"
echo ""

# Run ESLint
echo "🔎 Linting JavaScript with ESLint..."
npm run lint
echo "✅ Linting check passed!"
echo ""

echo "🎉 All quality checks passed!"
