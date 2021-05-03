import json
import sys
import boto3
import botocore
import datetime
import os

# Function to parse evenet payload and extract relevant information

def event_parser(event):
   event_dict = dict()
   event_dict['resultToken'] = event['resultToken']
   event_dict['ruleParameters'] = json.loads(event['ruleParameters'])
   changed_event = json.loads(event['invokingEvent'])
   event_dict['orderingtimestamp'] = changed_event['configurationItem']['configurationItemCaptureTime']
   event_dict['lambda_arn'] = changed_event['configurationItem']['ARN']
   return event_dict

# Function to check compliance by retrieving lambda details

def evaluate_compliance(lambda_arn):
   lambdaclient = boto3.client('lambda')
   lambda_details = lambdaclient.get_function(
      FunctionName=lambda_arn
   )
   if "tracingConfig" not in lambda_details['Configuration']:
        return "NON_COMPLIANT"
   else:
       return "COMPLIANT"

# Function to build the final message to post to AWS Config Rule

def build_config_message(compliance_status,lambda_arn,orderingtimestamp,resultToken):
   config_client = boto3.client("config")
   if compliance_status ==  "COMPLIANT":
      try:
          config_client.put_evaluations(
                 Evaluations=[
                 {
                     'ComplianceResourceType' : 'AWS::Lambda::Function',
                     'ComplianceResourceId' : lambda_arn,
                     'ComplianceType' : compliance_status,
                     'Annotation' : 'This Lambda function is configured to allow x-ray tracing.',
                     'OrderingTimestamp' : orderingtimestamp
                 },
               ],
                 ResultToken=resultToken,
                 TestMode=os.environ['TestMode'] == "True"
                 )
          return None
      except:
          return "Error posting to ConfigRule"             

   elif compliance_status == "NON_COMPLIANT":
       try:
           config_client.put_evaluations(
                 Evaluations=[
                 {
                     'ComplianceResourceType' : 'AWS::Lambda::Function',
                     'ComplianceResourceId' : lambda_arn,
                     'ComplianceType' : compliance_status,
                     'Annotation' : 'This Lambda function is not configured to allow x-ray tracing.',
                     'OrderingTimestamp' : orderingtimestamp
                 },
               ],
                 ResultToken=resultToken,
                 TestMode=os.environ['TestMode'] == "True"
              )
           return None
       except:
           return "Error posting to ConfigRule"

   else:
       try:
           config_client.put_evaluations(
                 Evaluations=[
                 {
                     'ComplianceResourceType' : 'AWS::Lambda::Function',
                     'ComplianceResourceId' : lambda_arn,
                     'ComplianceType' : compliance_status,
                     'Annotation' : 'This Lambda function is missing variables.',
                     'OrderingTimestamp' : orderingtimestamp
                 },
               ],
                 ResultToken=resultToken,
                 TestMode=os.environ['TestMode'] == "True"
              )
           return None
       except:
           return "Error posting to ConfigRule"

# Main Lambda event handler that receives payload and calls other functions

def lambda_handler(event, context):
    event_dict = event_parser(event)
    compliance_status = evaluate_compliance(event_dict['lambda_arn'])
    build_config_message(compliance_status,event_dict['lambda_arn'],event_dict['orderingtimestamp'],event_dict['resultToken'])
    print(compliance_status)
    print('KEY DATA')
    print(event_dict)
    return event_dict