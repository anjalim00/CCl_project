import boto3

# Get the service resource.
import key_config as keys

dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
                    aws_session_token=keys.AWS_SESSION_TOKEN)
# Create the DynamoDB table.

table = dynamodb.create_table(
    TableName='registration',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

table = dynamodb.create_table(
    TableName='user_history',
    KeySchema=[
        {
            'AttributeName': 'notes_title',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'notes_title',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 7,
        'WriteCapacityUnits': 7
    }
)

# Wait until the table exists.
table.wait_until_exists()
