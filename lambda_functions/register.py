import boto3
import json
import os

table_name = 'PeriodCalenderUserData'
sns_topic_arn = os.environ['PeriodCalendarTopic']

# Function to send a subscription email to the user
def send_confirmation_email(email):
    sns_client = boto3.client('sns')

    # https://aws.amazon.com/tutorials/filter-messages-published-to-topics/
    # Define the filter policy for sns
    
    filter_policy = {
        'email': [email]
    }
    print(sns_topic_arn)
    # send subscription email
    sns_client.subscribe(
        TopicArn=sns_topic_arn,
        Protocol='email',
        Endpoint=email,
        Attributes={
            'FilterPolicy': json.dumps(filter_policy)
        }
    )

# Function to check if the email is already registered
def is_email_registered(email):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    response = table.get_item(Key={'email': email}, ProjectionExpression='email')

    return 'Item' in response
    
# Lambda Function to handle user registration
def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        email = data['email']
        password = data['password']

        if is_email_registered(email):
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'Email is already registered'})
            }

        # Save the user data to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        item = {
            'email': email,
            'password': password
        }

        table.put_item(Item=item)
        
        # Send email and subscribe the user to the SNS topic
        send_confirmation_email(email)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User registered successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error processing request: ' + str(e)})
        }