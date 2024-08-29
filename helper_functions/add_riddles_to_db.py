import boto3
import json

# Create a session using the 'gor' profile
session = boto3.Session(profile_name='gor')

# Initialize DynamoDB client
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('GameofRiddles_riddles')

def add_riddle(riddle_data):
    try:
        table.put_item(Item=riddle_data)
        print(f"Successfully added riddle: {riddle_data['id']}")
    except Exception as e:
        print(f"Error adding riddle: {str(e)}")

if __name__ == '__main__':
    # Load riddles from JSON file
    with open('data/riddles_en.json', encoding='utf-8') as file:
        riddles = json.load(file)

    # Add each riddle to the database
    for riddle in riddles:
        add_riddle(riddle)

    print(f"Finished adding {len(riddles)} riddles.")