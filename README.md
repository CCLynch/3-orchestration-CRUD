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

This command orchestrates a complete, isolated test run. It builds and starts the `api`, `localstack`, and `tests` containers, runs the `pytest` suite, and then automatically tears down the entire stack.

The script will exit with a `0` on success and a non-zero code on failure, making it ideal for CI/CD pipelines.

The API will be accessible at `http://localhost:5001`. You can then use tools like `curl` or Postman to interact with the endpoints (`/items`, `/items/<id>`).

To stop the stack:
```bash
docker compose down
```

## Citations:

In the course of this building this repository, I referred to following resources:

### Docs and References

* **[AWS SQS-Lambda Pattern](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)**

* **[Boto3 - AWS SDK for Python](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)**: Used in `run.py` to create and configure AWS resources inside LocalStack

### Troubleshooting

I struggled with the orchestration of resources, consistently getting 500 responses in my tests. In hindsight this was due to a race condition in `run.py` script sending API calls to LocalStack before SQS and Lambda were ready. 

I used the [Docker `healthcheck` docs](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck), [LocalStack readiness docs](https://docs.localstack.cloud/user-guide/ci/readiness-checking/) and **[Flask Documentation](https://flask.palletsprojects.com/)**: Used to create the simple web server for the Docker Compose health check. But flawed logic in the `/health` endpoint was also creating false errors. 

I used **[AWS CLI docs (`awslocal`)](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)** extensively for sending test messages and checking Lambda logs and eventually found the issue with my healthcheck. 