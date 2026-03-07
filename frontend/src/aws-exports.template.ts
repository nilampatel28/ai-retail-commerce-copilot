// AWS Configuration Template
// Copy this file to aws-exports.ts and fill in your values from CDK deployment

export const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'YOUR_USER_POOL_ID',  // From CDK output: UserPoolId
      userPoolClientId: 'YOUR_CLIENT_ID',  // From CDK output: UserPoolClientId
      region: 'us-east-1'
    }
  }
};

export const apiEndpoint = 'YOUR_API_ENDPOINT';  // From CDK output: ApiEndpoint
