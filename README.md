# Cloud-Native REST API with Docker and LocalStack

This project demonstrates a fully containerized RESTful API using Docker, Docker Compose, and LocalStack to simulate an AWS cloud environment. The API provides CRUD (Create, Read, Update, Delete) operations for items stored in a mock Amazon DynamoDB table and Amazon S3 bucket.

The entire stack, including the API, mock AWS services, and the test suite, is orchestrated with Docker Compose, enabling consistent and reproducible environments for both development and Continuous Integration.

[![Run Docker Compose Tests](https://github.com/CCLynch/3-orchestration-CRUD/actions/workflows/ci.yml/badge.svg)](https://github.com/CCLynch/3-orchestration-CRUD/actions/workflows/ci.yml)

## Architecture

This project uses Docker Compose to manage a multi-container environment:

-   **`api`**: A Python Flask container that serves the REST API. It's configured to communicate with the `localstack` service for all its backend needs.
-   **`localstack`**: A container running [LocalStack](https://www.localstack.cloud/), which provides mock S3 and DynamoDB services. An initialization script (`init-aws.sh`) runs on startup to create the necessary S3 bucket and DynamoDB table.
-   **`tests`**: A short-lived container that runs the `pytest` suite. It makes HTTP requests to the `api` service and exits with a status code indicating pass (0) or fail (non-zero).

## Local Development and Testing

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

### Running the API Stack

This command builds and starts the `api` and `localstack` containers in the background.

```bash
# Make the script executable (only needed once)
chmod +x run_api.sh

# Run the script
./run_api.sh
```

The API will be accessible at `http://localhost:5001`. 

You can then use `curl` to interact with the endpoints (`/items`, `/items/<id>`).

To stop the stack:
```bash
docker compose down
```

### Running the Test Suite

This command orchestrates a complete, isolated test run. It builds and starts the `api`, `localstack`, and `tests` containers, runs the `pytest` suite against the live API, and then automatically tears down the entire stack.

```bash
# Make the script executable (only needed once)
chmod +x run_tests.sh

# Run the script
./run_tests.sh
```

The script will exit with a `0` on success and a non-zero code on failure, making it ideal for CI/CD pipelines.

## Approach and Citations:

Initially, I attempted to implement an asynchronous architecture based on the [AWS SQS-Lambda Pattern](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html) as described in [Understanding asynchronous messaging for microservices](https://aws.amazon.com/blogs/compute/understanding-asynchronous-messaging-for-microservices/). The goal was to have an API-facing Lambda publish jobs to an SQS queue, with a separate Lambda processing them. My intention was to implement this complex architecture with a simple task as practice for the final project.

However, after running into significant orchestration challenges and failing tests, I pivoted to the simpler synchronous architecture used in the previous assignments, with a [Flask application](https://flask.palletsprojects.com/en/stable/tutorial/) as the API server, communicating with AWS using [Boto3](https://aws.amazon.com/sdk-for-python/).

### Troubleshooting

The primary struggle was pretty simple in hindsight; a race condition where the `tests` container would start making API calls before the Flask application inside the `api` container was fully booted and ready. This resulted in connection errors and failing tests.

Once I determined that the test errors were due to orchestration, I followed the examples in **[Docker: Control startup and shutdown order in Compose](https://docs.docker.com/compose/how-tos/startup-order/)** to build a healthcheck in the compose files. 

I still ran into some issues with failing health checks that I couldn't fix, so my solution was `pytest` fixture in the test suite (`test_api.py`) to repeatedly poll the API until it received a successful response, only allowing the tests to proceed once the API was returned a 200 status code. 
