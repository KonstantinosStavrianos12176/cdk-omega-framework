import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    # Extract the token from the event
    token = event['authorizationToken']

    # Mock validation of the token
    # This is just a simple check. In a real-world scenario, you'd verify the JWT, check its signature, 
    # inspect claims, ensure it hasn't expired, etc.
    if token == "valid_token":
        return generate_policy('user', 'Allow', event['methodArn'])
    else:
        return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    """Generate a policy to allow or deny access."""
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
    return policy
