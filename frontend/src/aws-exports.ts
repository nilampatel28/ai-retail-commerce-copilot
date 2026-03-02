const awsconfig = {
  aws_project_region: 'us-east-1',
  aws_cognito_region: 'us-east-1',
  aws_user_pools_id: 'us-east-1_7vla7DTpD',
  aws_user_pools_web_client_id: '1coc3d5stv0pr1ua3lta9idop2',
  aws_cloud_logic_custom: [
    {
      name: 'RetailBrainAPI',
      endpoint: 'https://au9tcxurp4.execute-api.us-east-1.amazonaws.com/prod/',
      region: 'us-east-1'
    }
  ]
};

export default awsconfig;
