#!/bin/bash

# Document Builder Platform - Start All Services
# This script starts all three microservices and logs their output

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# PID file to track running services
PID_FILE=".service_pids"

# Log directory
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Document Builder Platform${NC}"
echo -e "${BLUE}  Starting Services${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if services are already running
if [ -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  Warning: Services may already be running${NC}"
    echo -e "${YELLOW}   PID file exists: $PID_FILE${NC}"
    echo -e "${YELLOW}   Run './stop.sh' first to stop existing services${NC}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} Loading configuration from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo -e "${YELLOW}   Using default configuration${NC}"
    echo -e "${YELLOW}   Copy .env.example to .env and configure for production${NC}"
    echo ""
fi

# Set default ports if not defined
CONTENT_INTAKE_PORT="${CONTENT_INTAKE_PORT:-8001}"
GESTALT_ENGINE_PORT="${GESTALT_ENGINE_PORT:-8002}"
DOCUMENT_FORMATTER_PORT="${DOCUMENT_FORMATTER_PORT:-8003}"

# Check if PostgreSQL is accessible (optional check)
if command -v pg_isready &> /dev/null; then
    if ! pg_isready -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Warning: PostgreSQL does not appear to be running${NC}"
        echo -e "${YELLOW}   Content Intake Service requires PostgreSQL${NC}"
        echo -e "${YELLOW}   Start PostgreSQL or run: docker run --name docbuilder-postgres \\${NC}"
        echo -e "${YELLOW}     -e POSTGRES_USER=docbuilder -e POSTGRES_PASSWORD=changeme \\${NC}"
        echo -e "${YELLOW}     -e POSTGRES_DB=document_builder -p 5432:5432 -d postgres:14${NC}"
        echo ""
    else
        echo -e "${GREEN}✓${NC} PostgreSQL is running"
    fi
fi

echo ""
echo -e "${BLUE}Starting services...${NC}"
echo ""

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local log_file="$LOG_DIR/${service_name}.log"

    echo -e "${BLUE}▶${NC}  Starting ${service_name} on port ${port}..."

    # Start the service in background
    nohup uvicorn "${service_path}:app" \
        --host 0.0.0.0 \
        --port "$port" \
        --log-level info \
        > "$log_file" 2>&1 &

    local pid=$!

    # Wait a moment and check if process is still running
    sleep 1
    if ps -p $pid > /dev/null; then
        echo -e "${GREEN}✓${NC}  ${service_name} started (PID: ${pid}, Port: ${port})"
        echo "${service_name}:${pid}:${port}" >> "$PID_FILE"
    else
        echo -e "${RED}✗${NC}  ${service_name} failed to start"
        echo -e "${RED}   Check log: ${log_file}${NC}"
        return 1
    fi
}

# Start all services
start_service "Content Intake Service" "services.content_intake.main" "$CONTENT_INTAKE_PORT"
start_service "Gestalt Design Engine" "services.gestalt_engine.main" "$GESTALT_ENGINE_PORT"
start_service "Document Formatter" "services.document_formatter.main" "$DOCUMENT_FORMATTER_PORT"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  All services started successfully${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  • Content Intake:      http://localhost:${CONTENT_INTAKE_PORT}/"
echo -e "  • Content Intake API:  http://localhost:${CONTENT_INTAKE_PORT}/docs"
echo -e "  • Gestalt Engine:      http://localhost:${GESTALT_ENGINE_PORT}/docs"
echo -e "  • Document Formatter:  http://localhost:${DOCUMENT_FORMATTER_PORT}/docs"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  • Content Intake:      tail -f logs/Content\\ Intake\\ Service.log"
echo -e "  • Gestalt Engine:      tail -f logs/Gestalt\\ Design\\ Engine.log"
echo -e "  • Document Formatter:  tail -f logs/Document\\ Formatter.log"
echo ""
echo -e "${BLUE}Management:${NC}"
echo -e "  • Stop services:       ./stop.sh"
echo -e "  • View all logs:       tail -f logs/*.log"
echo ""
