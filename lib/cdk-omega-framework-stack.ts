import { Duration, Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as path from 'path';
import { Construct } from 'constructs';

export class CdkOmegaFrameworkStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const dynamodb_table = new dynamodb.Table(this, "Table", {
      tableName: 'PowerDevices',
      partitionKey: { name: "DeviceID", type: dynamodb.AttributeType.NUMBER },
      removalPolicy: RemovalPolicy.DESTROY
      }
    );

    const lambda_backend = new lambda.DockerImageFunction(this, 'PowerServicesService', {
      functionName: `PowerServicesService`,
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../src/api')),
      timeout: Duration.minutes(5),
      memorySize: 512,
      environment: {
        TABLE_NAME: dynamodb_table.tableName
      },
    });

    const lambda_auth = new lambda.DockerImageFunction(this, 'Authorizer', {
      functionName: `Authorizer`,
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../src/auth')),
      timeout: Duration.minutes(5),
      memorySize: 512,
    });

    dynamodb_table.grantFullAccess(lambda_backend)
    lambda_backend.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ["*"],
      resources: [dynamodb_table.tableArn]}))

    const api = new apigateway.RestApi(this, "RestAPI", {
      deployOptions: {
        dataTraceEnabled: true,
        tracingEnabled: true
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
      },

    })

    const auth = new apigateway.TokenAuthorizer(this, 'devicesAuthorizer', {
      handler: lambda_auth
    });


    const endpoint = api.root.addResource("device")
    endpoint.addMethod("GET", new apigateway.LambdaIntegration(lambda_backend), {
      authorizer: auth
    })
    endpoint.addMethod("POST", new apigateway.LambdaIntegration(lambda_backend))
    endpoint.addMethod("PUT", new apigateway.LambdaIntegration(lambda_backend))
    endpoint.addMethod("DELETE", new apigateway.LambdaIntegration(lambda_backend))



    
  }
}
