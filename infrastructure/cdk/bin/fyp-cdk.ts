#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { FypHaStack } from '../lib/fyp-ha-stack';

const app = new cdk.App();

new FypHaStack(app, 'FypHaStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  backendImageUri: app.node.tryGetContext('backendImageUri') || process.env.BACKEND_IMAGE_URI || '',
  frontendImageUri: app.node.tryGetContext('frontendImageUri') || process.env.FRONTEND_IMAGE_URI || '',
  dbName: app.node.tryGetContext('dbName') || process.env.DB_NAME || 'db_exam',
});
