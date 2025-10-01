#!/bin/bash

# Test script för IGDB Game Recommendation System
# Detta script testar systemet lokalt

set -e

echo "🎮 IGDB Game Recommendation System - Local Test"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if terraform-admin-key.json exists
if [ ! -f "terraform-admin-key.json" ]; then
    print_error "terraform-admin-key.json not found. Please ensure GCP credentials are available."
    exit 1
fi

print_status "GCP credentials found"

# Build and start services
echo ""
echo "🚀 Building and starting services..."
docker-compose -f web-app/docker-compose.yml down
docker-compose -f web-app/docker-compose.yml build
docker-compose -f web-app/docker-compose.yml up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 30

# Test backend health
echo ""
echo "🔍 Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend is healthy"
else
    print_error "Backend health check failed"
    docker-compose -f web-app/docker-compose.yml logs backend
    exit 1
fi

# Test frontend
echo ""
echo "🔍 Testing frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_error "Frontend is not accessible"
    docker-compose -f web-app/docker-compose.yml logs frontend
    exit 1
fi

# Test API endpoints
echo ""
echo "🔍 Testing API endpoints..."

# Test search
echo "Testing game search..."
SEARCH_RESPONSE=$(curl -s "http://localhost:8000/games/search?query=zelda&limit=5")
if echo "$SEARCH_RESPONSE" | grep -q "name"; then
    print_status "Game search is working"
    echo "Found games: $(echo "$SEARCH_RESPONSE" | jq -r '.[0].name' 2>/dev/null || echo "Unknown")"
else
    print_warning "Game search returned no results or failed"
fi

# Test recommendations (if we have a game ID)
GAME_ID=$(echo "$SEARCH_RESPONSE" | jq -r '.[0].id' 2>/dev/null)
if [ "$GAME_ID" != "null" ] && [ "$GAME_ID" != "" ]; then
    echo "Testing recommendations for game ID: $GAME_ID"
    RECOMMENDATIONS_RESPONSE=$(curl -s "http://localhost:8000/recommendations/$GAME_ID?limit=3")
    if echo "$RECOMMENDATIONS_RESPONSE" | grep -q "recommended_games"; then
        print_status "Recommendations are working"
        RECOUNT=$(echo "$RECOMMENDATIONS_RESPONSE" | jq -r '.recommended_games | length' 2>/dev/null || echo "0")
        echo "Found $RECOUNT recommendations"
    else
        print_warning "Recommendations failed or returned no results"
    fi
else
    print_warning "No game ID available for testing recommendations"
fi

# Show service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose -f web-app/docker-compose.yml ps

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"

echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Open http://localhost:3000 in your browser"
echo "2. Search for a game (e.g., 'zelda', 'witcher', 'mario')"
echo "3. Click on a game to see recommendations"
echo "4. Check http://localhost:8000/docs for API documentation"

echo ""
print_status "Local system test completed successfully!"
echo ""
echo "To stop the services, run:"
echo "docker-compose -f web-app/docker-compose.yml down"
