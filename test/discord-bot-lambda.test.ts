// Import necessary libraries/modules from AWS CDK and the local directory
import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as DiscordBotLambda from '../lib/discord-bot-lambda-stack';
import { run } from 'node:test';

// Define a test to check whether an SQS Queue is created with specified properties
test('SQS Queue Created', () => {
  // Initializing a new CDK app
  const app = new cdk.App();
  
  // WHEN: Creating a new stack in the app
  const stack = new DiscordBotLambda.DiscordBotLambdaStack(app, 'MyTestStack');
  
  // THEN: Creating a template from the stack
  const template = Template.fromStack(stack);

  // Asserting that the template has a resource of type AWS::SQS::Queue with specified properties
  template.hasResourceProperties('AWS::SQS::Queue', {
    VisibilityTimeout: 300
  });
});
// run test by running the following command in the terminal: npx jest