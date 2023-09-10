import boto3
import json 

# AWS DynamoDB table name
table_name = 'PeriodCalenderUserData'

# Lambda Function to handle user login
def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        email = data['email']
        password = data['password']

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        response = table.get_item(Key={'email': email})

        if 'Item' in response:
            user_data = response['Item']
            stored_password = user_data['password']

            if password == stored_password:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Login successful', 'email': email})
                }
            else:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Invalid email or password'})
                }
        else:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid email or password'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'Error processing request: ' + str(e)})
        }
