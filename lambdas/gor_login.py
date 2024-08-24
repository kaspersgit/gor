import json
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('GameofRiddles_users')
riddle_table = dynamodb.Table('GameofRiddles_riddle')


def lambda_handler(event, context):
    # try:
        username = event['username']
        current_time = datetime.utcnow().isoformat()

        # Lookup user in the first table
        user_response = user_table.get_item(Key={'username': username})

        if 'Item' in user_response:
            # Username exists, save information
            user_data = user_response['Item']
            user_level = user_data['level']
        else:
            # Username doesn't exist, add to table with default info and timestamp
            new_item = {
                'username': username,  # Using username as the key
                'score': 0,
                'level': 1,
                'created_at': current_time,
                'last_active': current_time
            }
            user_table.put_item(Item=new_item)

            user_level = new_item['level']

        # Fetch riddle based on user's level
        try:
            riddle_response = riddle_table.get_item(Key={'id': user_level})
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error retrieving riddle data'})
            }

        # Check if riddle exists for this level
        if 'Item' not in riddle_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Riddle not found for this level'})
            }

        riddle_data = riddle_response['Item']

        # Return combined user and riddle data
        return {
            'statusCode': 200,
            'body': json.dumps({
                'userData': user_data,
                'riddle': riddle_data
            })
        }

    # except Exception as e:
    #     print(f'Error: {str(e)}')
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps({'message': 'Internal server error'})
    #     }

