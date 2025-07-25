#!/bin/bash
echo "Starting the application stack (API + LocalStack)..."

docker compose up --build -d

echo ""
echo "API is accessible at http://localhost:5001"
echo "To stop the stack, run: docker-compose down -v"