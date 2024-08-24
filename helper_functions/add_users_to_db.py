import boto3
import json

# Create a session using the 'gor' profile
session = boto3.Session(profile_name='gor')

# Initialize DynamoDB client
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('GameofRiddles_users')

def add_user(user_data):
    try:
        table.put_item(Item=user_data)
        print(f"Successfully added user: {user_data['username']}")
    except Exception as e:
        print(f"Error adding user: {str(e)}")

if __name__ == '__main__':
    False # will overwrite progress
    # Load users from JSON file
    with open('data/users.json', encoding='utf-8') as file:
        users = json.load(file)

    # Add each user to the database
    for user in users:
        add_user(user)

    print(f"Finished adding {len(users)} users.")