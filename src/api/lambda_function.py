import boto3
import json
import logging
from decimal import Decimal
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])  # Replace with your table name

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define a custom encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    logger.info(event)
    operation = event['httpMethod']

    if operation == 'POST':
        return create(event)
    elif operation == 'GET':
        return read(event)
    elif operation == 'PUT':
        return update(event)
    elif operation == 'DELETE':
        return delete(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid operation specified')
        }

def create(event):
    # Extract attributes from event body and add item to DynamoDB
    body = json.loads(event['body'])
    table.put_item(Item={
        'DeviceID': int(body['DeviceID']),
        'DeviceName': body['DeviceName'],
        'PowerRating': str(body['PowerRating']),
        'Location': body['Location']
    })
    return {
        'statusCode': 200,
        'body': json.dumps('Item created successfully')
    }

def read(event):
    # Retrieve an item from DynamoDB using its ID
    item_id = event['queryStringParameters']['DeviceID']
    response = table.get_item(Key={'DeviceID': int(item_id)})
    logger.info(response)

      # Check if 'Item' is present in the response and if 'PowerRating' exists
    if 'Item' in response and 'PowerRating' in response['Item']:
        # Convert the 'PowerRating' value to a float
        response['Item']['PowerRating'] = float(response['Item']['PowerRating'])
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Item', {}),  cls=DecimalEncoder)
    }

def update(event):
    # Update an item in DynamoDB
    body = json.loads(event['body'])
    device_id = int(body['DeviceID'])
    update_expression = "set DeviceName = :n, PowerRating = :p, #loc = :l"
    expression_values = {
        ':n': body['DeviceName'],
        ':p': str(body['PowerRating']),
        ':l': body['Location']
    }
    expressionAttributeNames={
        "#loc": "Location"
    }
    table.update_item(
        Key={'DeviceID': device_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expressionAttributeNames
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Item updated successfully')
    }


def delete(event):
    # Delete an item from DynamoDB using its ID
    device_id = int(event['queryStringParameters']['DeviceID'])
    table.delete_item(Key={'DeviceID': device_id})
    return {
        'statusCode': 200,
        'body': json.dumps('Item deleted successfully')
    }
