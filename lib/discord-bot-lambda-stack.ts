import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sqs from "aws-cdk-lib/aws-sqs"; // <-- ADD THIS for Test
import * as dotenv from "dotenv";
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';

dotenv.config();

export class DiscordBotLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const dockerFunction = new lambda.DockerImageFunction(
      this,
      "DockerFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset("./src"),
        memorySize: 1024,
        timeout: cdk.Duration.seconds(60),
        architecture: lambda.Architecture.ARM_64,
        environment: {
          DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY!,
        },
      }
    );

    // <-- ADD THIS BLOCK for test
    const queue = new sqs.Queue(this, 'MyQueue', {
       visibilityTimeout: cdk.Duration.seconds(300),
    });
    // END OF ADDED BLOCK

    // Connect SQS as an event source to Lambda, to make it poll for new messages in the SQS queue
    // like auto-scaling, this is a feature that is not yet supported by the CDK for Lambda functions
    dockerFunction.addEventSource(new lambdaEventSources.SqsEventSource(queue));
    // defeat sizes of 5 batch 

    const functionUrl = dockerFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    new cdk.CfnOutput(this, "FunctionUrl", {
      value: functionUrl.url,
    });
  }
}
