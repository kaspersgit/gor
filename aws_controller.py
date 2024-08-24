import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Create a session using the 'gor' profile
session = boto3.Session(profile_name='gor')

# Initialize DynamoDB client
dynamodb = session.resource('dynamodb')
table_users = dynamodb.Table('GameofRiddles_users')
table_riddles = dynamodb.Table('GameofRiddles_riddles')

# Get user
def get_user(username):
    try:
        response = table_users.get_item(Key={'username': username})
        if 'Item' in response:
            return response['Item']
        else:
            # User doesn't exist, add a new one
            add_user(username)
            return get_user(username)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # User doesn't exist, add a new one
            add_user(username)
            return get_user(username)
        else:
            raise e

# Add new user
def add_user(username):
    current_time = datetime.utcnow().isoformat()
    # Username doesn't exist, add to table with default info and timestamp
    new_item = {
        'username': username,  # Using username as the key
        'progress': {},
        'created_at': current_time,
        'last_active': current_time
    }
    return table_users.put_item(Item=new_item)

# Get riddle
def get_riddle(riddle_id):
    response = table_riddles.get_item(Key={'id': riddle_id})
    return response['Item']

# Get all riddles
def get_all_riddles():
    response = table_riddles.scan()
    return response['Items']

# Get all users
def get_all_users():
    response = table_users.scan()
    return response['Items']

# Update users progress
def update_user_progress(username, riddle_id, solved = False):
    current_time = datetime.utcnow().isoformat()
    try:
        # Retrieve the user's progress
        response = table_users.get_item(Key={'username': username})
        user_progress = response.get('Item', {}).get('progress', {})

        # Update the progress for the specific riddle
        # Increase nr of attempts by 1
        user_progress[str(riddle_id)] = {
            "attempts": user_progress.get(str(riddle_id), {"attempts": 0})["attempts"] + 1
        }

        # Add date of completion
        if solved:
            user_progress[str(riddle_id)].update({
                "completed_at": current_time
            })

        # Update the user's progress in DynamoDB
        table_users.put_item(
            Item={
                'username': username,
                'progress': user_progress,
                'created_at': response.get('Item', {}).get('created_at', current_time),
                'last_active': current_time
            }
        )

        return user_progress

    except ClientError as e:
        raise e

if __name__ == '__main__':
    resp = get_all_users()
    print(resp)
