import json
import boto3
import uuid  
from datetime import datetime, timedelta
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PeriodCalenderUserData')
eventbridge = boto3.client('events')
lambda_arn = os.environ['SendMailLambda']

def calculate_cycle_days(selected_date, last_period_date, last_cycle_days, last_next_period_date):
    # Calculate the time difference in days between the last recorded period start date and the new selected date
    time_difference = (datetime.strptime(selected_date, '%Y-%m-%d') - last_period_date).days

    # Calculate the cycle days based on the time difference
    cycle_days = last_cycle_days + time_difference

    # Calculate the time difference in days between the last predicted next period date and the new actual period start date
    time_difference_actual = (last_period_date - last_next_period_date).days

    # Adjust the cycle days if the actual period start date is earlier than the predicted next period date
    if time_difference_actual < 0:
        cycle_days -= abs(time_difference_actual)

    # Ensure that the cycle days are within a reasonable range
    cycle_days = max(20, min(cycle_days, 45))

    return cycle_days

def calculate_next_period_date(selected_date, cycle_days):
    period_started_date = datetime.strptime(selected_date, '%Y-%m-%d')
    next_period_date = period_started_date + timedelta(days=int(cycle_days))
    return next_period_date.strftime('%Y-%m-%d')  # Convert to string in default ISO 8601 format

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body['email']
        selected_date = body['selectedDate']

        selected_date = selected_date.split('T')[0]

        
        # Fetch the user's record from DynamoDB
        response = table.get_item(Key={'email': email})
        item = response.get('Item', {})
        
        # Check if cycleDays and selectedDate are already in the record
        cycle_days = item.get('cycleDays', None)
        last_period_date = datetime.strptime(item.get('selectedDate', selected_date), '%Y-%m-%d')
        last_next_period_date = datetime.strptime(item.get('nextPeriodDate', selected_date), '%Y-%m-%d')

        if cycle_days is None:
            # If cycle days are not available
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Please provide your cycle days input.', 'code': 'CYCLE_DAYS_REQUIRED'})
            }

        # Calculate the cycle days based on the time difference 
        cycle_days = calculate_cycle_days(selected_date, last_period_date, cycle_days, last_next_period_date)

        # Calculate the next period's date
        next_period_date = calculate_next_period_date(selected_date, cycle_days)

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

        # Modify the email address to be a valid rule name 
        rule_name = f'{email.replace("@", "_")}-ReminderRule'
            
        target_id = str(uuid.uuid4())
            
        # Calculate the reminder date (one day before the next period date)
        reminder_date = datetime.strptime(next_period_date, '%Y-%m-%d') - timedelta(days=1)

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
            'body': json.dumps({'nextPeriodDate': next_period_date, 'cycleDays': int(cycle_days)})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }

