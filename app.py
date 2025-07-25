import os
import boto3
import uuid
import json
from flask import Flask, jsonify, request
from botocore.exceptions import ClientError

app = Flask(__name__)

# Boto3 will use environment variables for configuration
dynamodb_resource = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
BUCKET_NAME = os.environ['S3_BUCKET_NAME']
items_table = dynamodb_resource.Table(TABLE_NAME)


@app.route('/')
def hello_world():
    return 'Hello, World! Your API with AWS integration is running.'


@app.route('/items', methods=['POST'])
def create_item():
    item_data = request.get_json()
    if not item_data or 'name' not in item_data or 'description' not in item_data:
        return jsonify({'error': 'Missing name or description'}), 400

    item_id = str(uuid.uuid4())
    item_data['id'] = item_id

    try:
        # Prevent creating items with a duplicate name
        response = items_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('name').eq(item_data['name']))
        if response['Items']:
            return jsonify({'error': 'An item with this name already exists'}), 409

        items_table.put_item(Item=item_data)
        s3_client.put_object(Bucket=BUCKET_NAME, Key=item_id, Body=json.dumps(item_data))
        return jsonify(item_data), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        response = items_table.scan()
        return jsonify(response.get('Items', [])), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/items/<string:item_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_item(item_id):
    try:
        if request.method == 'GET':
            response = items_table.get_item(Key={'id': item_id})
            if 'Item' in response:
                return jsonify(response['Item']), 200
            else:
                return jsonify({'error': 'Item not found'}), 404

        elif request.method == 'PUT':
            update_data = request.get_json()
            if not update_data:
                return jsonify({'error': 'Missing update data'}), 400

            # Use ExpressionAttributeNames to handle potential reserved keywords
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            for i, (key, value) in enumerate(update_data.items()):
                if key != 'id':
                    key_placeholder = f"#k{i}"
                    value_placeholder = f":v{i}"
                    update_expression_parts.append(f"{key_placeholder} = {value_placeholder}")
                    expression_attribute_names[key_placeholder] = key
                    expression_attribute_values[value_placeholder] = value

            if not expression_attribute_values:
                return jsonify({'error': 'No valid fields to update'}), 400

            update_expression = "SET " + ", ".join(update_expression_parts)

            response = items_table.update_item(
                Key={'id': item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
                ConditionExpression="attribute_exists(id)" # Fail if item doesn't exist
            )
            updated_item = response['Attributes']
            s3_client.put_object(Bucket=BUCKET_NAME, Key=item_id, Body=json.dumps(updated_item))
            return jsonify(updated_item), 200

        elif request.method == 'DELETE':
            items_table.delete_item(
                Key={'id': item_id},
                ConditionExpression="attribute_exists(id)" # Fail if item doesn't exist
            )
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=item_id)
            return jsonify({'message': f'Item {item_id} deleted successfully'}), 200

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return jsonify({'error': 'Item not found'}), 404
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)