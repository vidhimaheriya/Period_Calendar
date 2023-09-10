import json
import boto3
import os
import uuid 
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PeriodCalenderUserData')
eventbridge = boto3.client('events')
lambda_arn = os.environ['SendMailLambda']

def calculate_next_period_date(selected_date, cycle_days):
    period_started_date = datetime.strptime(selected_date, '%Y-%m-%d')
    next_period_date = period_started_date + timedelta(days=cycle_days)
    return next_period_date.strftime('%Y-%m-%d')

def lambda_handler(event, context):
    try:
            
        body = json.loads(event['body'])
        email = body['email']
        selected_date = body['selectedDate']
        cycle_days = int(body['cycleDays'])
        
        # Calculate the next period's date
        next_period_date = calculate_next_period_date(selected_date, cycle_days)
        
        selected_date = selected_date.split('T')[0]
        
        # Update the information in DynamoDB for the specific user
        table.update_item(
            Key={'email': email},
            UpdateExpression='SET selectedDate = :sd, cycleDays = :cd, nextPeriodDate = :npd',
            ExpressionAttributeValues={
                ':sd': selected_date,  
                ':cd': cycle_days,
                ':npd': next_period_date
            }
        )

        # Calculate the reminder date (one day before the next period date)
        reminder_date = datetime.strptime(next_period_date, '%Y-%m-%d') - timedelta(days=1)

        # Modify the email address to be a valid rule name 
        rule_name = f'{email.replace("@", "_")}-ReminderRule'
            
        target_id = str(uuid.uuid4())

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events/client/put_rule.html# 
        # https://www.baeldung.com/cron-expressions
        # Schedule an event to notify the user one day before the next period date
        eventbridge.put_rule(
            Name=rule_name,
            ScheduleExpression=f'cron({reminder_date.minute} {reminder_date.hour} {reminder_date.day} {reminder_date.month} ? {reminder_date.year})',
            State='ENABLED'
        )

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events/client/put_targets.html
        # Set EventBridge target to trigger the second Lambda function
        target_input = {
            'email': email,
            'nextPeriodDate': next_period_date
        }
        eventbridge.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': target_id,
                    'Arn': lambda_arn,
                    'Input': json.dumps(target_input)
                }
            ]
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Event scheduled successfully', 'nextPeriodDate': next_period_date, 'cycleDays': cycle_days})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
