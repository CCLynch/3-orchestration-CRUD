#!/bin/bash
# 'set -e' will make the script exit if any command fails
set -e

echo "--- Initializing AWS resources ---"

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Wait for services to be ready by polling a known command
until awslocal dynamodb list-tables &> /dev/null; do
  >&2 echo "Services not yet available. Retrying..."
  sleep 2
done

echo "Services are ready. Creating resources..."

awslocal s3 mb s3://my-unique-bucket-name

awslocal dynamodb create-table \
    --table-name items \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

echo "--- AWS resources initialization complete ---"