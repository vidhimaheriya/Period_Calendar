import json
import boto3
import os

# https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
sns_topic_arn = os.environ['PeriodCalendarTopic']

def lambda_handler(event, context):
    try:
        details= event['detail']
        input_t = json.loads(details['input'])
        email = input_t['email']
        next_period_date = input_t['nextPeriodDate']
        
        # https://docs.aws.amazon.com/sns/latest/dg/example-filter-policies.html
        # Publish a message to the SNS topic with the filter policy
        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message="Your period might start tommorrow.",
            MessageAttributes={
                "email": {
                    'DataType': 'String',
                    'StringValue': email
                },
                "nextPeriodDate":{
                    'DataType': 'String',
                    'StringValue': next_period_date
                }
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Email sent successfully'})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
