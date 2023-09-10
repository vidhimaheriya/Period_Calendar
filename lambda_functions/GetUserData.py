import json
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PeriodCalenderUserData') 

def lambda_handler(event, context):
    try:

        body = json.loads(event['body'])
        email = body['email']

        # Get the user's record from DynamoDB based on their email
        response = table.get_item(Key={'email': email})
        item = response.get('Item', {})

        # Check if the item was found in DynamoDB and contains data
        if 'selectedDate' in item and 'cycleDays' in item:
            
            selected_date = item['selectedDate']
            cycle_days = int(item['cycleDays'])
            return {
                'statusCode': 200,
                'body': json.dumps({'selectedDate': selected_date, 'cycleDays': cycle_days})
            }
        else:
            # If the user's data is not found, return an error response
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User data not found'})
            }
    except ClientError as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
