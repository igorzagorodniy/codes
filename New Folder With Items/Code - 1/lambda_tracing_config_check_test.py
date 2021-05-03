import unittest
import json
import os
import lambda_tracing_config
from unittest.mock import patch


class lambda_tracing_config_test(unittest.TestCase):

    def setUp(self):
        os.environ["DEBUSSY"] = "1"
        os.environ["TestMode"] = "True"
        self.compliance_status = "COMPLIANT"
        self.lambda_arn = "arn:aws:lambda:us-east-2:123456789012:instance/i-00000000"
        self.orderingtimestamp = "2016-02-17T01:36:34.043Z"
        self.resultToken = "myResultToken"
        self.Annotation = "My Annotation"
        self.event = {
            "invokingEvent": "{\"configurationItem\":{\"configurationItemCaptureTime\":\"2016-02-17T01:36:34.043Z\",\"awsAccountId\":\"123456789012\",\"configurationItemStatus\":\"OK\",\"resourceId\":\"i-00000000\",\"ARN\":\"arn:aws:lambda:us-east-2:123456789012:instance/i-00000000\",\"awsRegion\":\"us-east-2\",\"availabilityZone\":\"us-east-2a\",\"resourceType\":\"AWS::EC2::Instance\",\"tags\":{\"Foo\":\"Bar\"},\"relationships\":[{\"resourceId\":\"eipalloc-00000000\",\"resourceType\":\"AWS::EC2::EIP\",\"name\":\"Is attached to ElasticIp\"}],\"configuration\":{\"foo\":\"bar\"}},\"messageType\":\"ConfigurationItemChangeNotification\"}",
            "ruleParameters": "{\"myParameterKey\":\"myParameterValue\"}",
            "resultToken": "myResultToken",
            "eventLeftScope": "false",
            "executionRoleArn": "arn:aws:iam::123456789012:role/config-role",
            "configRuleArn": "arn:aws:config:us-east-2:123456789012:config-rule/config-rule-0123456",
            "configRuleName": "change-triggered-config-rule",
            "configRuleId": "config-rule-0123456",
            "accountId": "123456789012",
            "version": "1.0"
        }
        self.lambda_details = {
            "Code": {
                'Location': "Test"
            },
            "Configuration": {
                'CodeSha256': 'YFgDgEKG3ugvF1+pX64gV6tu9qNuIYNUdgJm8nCxsm4=',
                'CodeSize': 5797206,
                'Description': 'Process image objects from Amazon S3.',
                'Environment': {
                    'Variables': {
                        'BUCKET': 'my-bucket-1xpuxmplzrlbh',
                        'PREFIX': 'inbound',
                    },
                },
                'FunctionArn': 'arn:aws:lambda:us-east-2:123456789012:function:my-function',
                'FunctionName': 'my-function',
                'Handler': 'index.handler',
                'KMSKeyArn': 'arn:aws:kms:us-east-2:123456789012:key/b0844d6c-xmpl-4463-97a4-d49f50839966',
                'LastModified': '2020-04-10T19:06:32.563+0000',
                'LastUpdateStatus': 'Successful',
                'MemorySize': 256,
                'RevisionId': 'b75dcd81-xmpl-48a8-a75a-93ba8b5b9727',
                'Role': 'arn:aws:iam::123456789012:role/lambda-role',
                'Runtime': 'nodejs12.x',
                'State': 'Active',
                'Timeout': 15,
                'TracingConfig': {
                    'Mode': 'Active',
                },
                'Version': '$LATEST',
            },
            'Tags': {
                'DEPARTMENT': 'Assets',
            }
        }

    def tearDown(self):
        self.event = {}
        self.lambda_details = {}
        self.lambda_arn = ""
        self.compliance_status = ""
        self.orderingtimestamp = ""
        self.resultToken = ""
        self.Annotation = ""

    # Test to check for event_parser function
    def test_event_parser_lambda_arn(self):
        expected_value = "arn:aws:lambda:us-east-2:123456789012:instance/i-00000000"
        returned_function = lambda_tracing_config.event_parser(self.event)
        self.assertEqual(expected_value, returned_function['lambda_arn'], msg="Lambda ARN retrieval is incorrect")

    # Test to check for event_parser function
    def test_event_parser_ordering_timestamp(self):
        expected_value = "2016-02-17T01:36:34.043Z"
        returned_function = lambda_tracing_config.event_parser(self.event)
        self.assertEqual(expected_value, returned_function['orderingtimestamp'], msg="Timestamp retrieval is incorrect")

    # Test to check for build_config_function
    def test_build_config_message(self):
        returned_function = lambda_tracing_config.build_config_message(self.compliance_status, self.lambda_arn,
                                                                       self.orderingtimestamp, self.resultToken)
        self.assertIsNotNone(returned_function)

    # Test to check for  evaluate_compliance_function
    def test_evaluate_compliance(self):
        expected_value = "NON_COMPLIANT"
        with patch('lambda_tracing_config.boto3.client') as mock_boto3_client:
            mock_boto3_client.return_value.get_function.return_value = self.lambda_details
            returned_function = lambda_tracing_config.evaluate_compliance(self.lambda_details)
            self.assertEqual(expected_value, returned_function, msg="Evaluation is correct")


if __name__ == "__main__":
    unittest.main()