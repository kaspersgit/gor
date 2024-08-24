import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('GameofRiddles_users')


def lambda_handler(event, context):
    username = event['username']
    current_time = datetime.utcnow().isoformat()

    # Check if the username exists
    response = table.get_item(Key={'username': username})

    if 'Item' in response:
        # Username exists, return information
        return {
            'exists': True,
            'info': response['Item']
        }
    else:
        # Username doesn't exist, add to table with default info and timestamp
        new_item = {
            'username': username,  # Using username as the key
            'score': 0,
            'level': 1,
            'created_at': current_time,
            'last_active': current_time
        }
        table.put_item(Item=new_item)
        return {
            'exists': False,
            'info': new_item
        }