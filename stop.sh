#!/bin/bash

# Document Builder Platform - Stop All Services
# This script gracefully stops all running services

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

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Document Builder Platform${NC}"
echo -e "${BLUE}  Stopping Services${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No running services found${NC}"
    echo -e "${YELLOW}   PID file not found: $PID_FILE${NC}"
    echo ""

    # Try to find any running uvicorn processes anyway
    echo -e "${BLUE}Checking for uvicorn processes...${NC}"
    if pgrep -f "uvicorn.*services\.(content_intake|gestalt_engine|document_formatter)" > /dev/null; then
        echo -e "${YELLOW}Found running uvicorn processes${NC}"
        echo ""
        ps aux | grep -E "uvicorn.*services\.(content_intake|gestalt_engine|document_formatter)" | grep -v grep
        echo ""
        read -p "Kill these processes? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f "uvicorn.*services\.(content_intake|gestalt_engine|document_formatter)"
            echo -e "${GREEN}✓${NC} Processes terminated"
        fi
    else
        echo -e "${GREEN}No uvicorn service processes found${NC}"
    fi
    exit 0
fi

# Read PIDs from file and stop services
echo -e "${BLUE}Stopping services...${NC}"
echo ""

stopped_count=0
failed_count=0

while IFS=':' read -r service_name pid port; do
    echo -e "${BLUE}■${NC}  Stopping ${service_name} (PID: ${pid}, Port: ${port})..."

    # Check if process exists
    if ps -p "$pid" > /dev/null 2>&1; then
        # Send SIGTERM for graceful shutdown
        kill -TERM "$pid" 2>/dev/null || true

        # Wait for process to stop (max 5 seconds)
        for i in {1..10}; do
            if ! ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}  ${service_name} stopped"
                ((stopped_count++))
                break
            fi
            sleep 0.5
        done

        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠${NC}  ${service_name} did not stop gracefully, forcing..."
            kill -KILL "$pid" 2>/dev/null || true
            sleep 0.5
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${RED}✗${NC}  Failed to stop ${service_name}"
                ((failed_count++))
            else
                echo -e "${GREEN}✓${NC}  ${service_name} stopped (forced)"
                ((stopped_count++))
            fi
        fi
    else
        echo -e "${YELLOW}⚠${NC}  ${service_name} (PID: ${pid}) not running"
    fi
done < "$PID_FILE"

# Remove PID file
rm -f "$PID_FILE"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Services stopped${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${GREEN}Stopped: ${stopped_count}${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${RED}Failed:  ${failed_count}${NC}"
fi
echo ""

# Check for any remaining processes
if pgrep -f "uvicorn.*services\.(content_intake|gestalt_engine|document_formatter)" > /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Some uvicorn processes may still be running${NC}"
    echo -e "${YELLOW}   Run the following to check:${NC}"
    echo -e "${YELLOW}   ps aux | grep uvicorn${NC}"
    echo ""
fi
