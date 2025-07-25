#!/bin/bash
# Ensures a clean slate by taking down any running dev stack
echo "Making sure the development stack is down..."
docker-compose down -v --remove-orphans

echo "Building and running the test stack..."

# The flags below orchestrate the test run and capture the exit code
docker-compose -f docker-compose.test.yml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from tests

EXIT_CODE=$?

# Clean up the test environment completely
echo "Cleaning up the test stack..."
docker-compose -f docker-compose.test.yml down -v

if [ $EXIT_CODE -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed. Exit code: $EXIT_CODE"
fi

exit $EXIT_CODE