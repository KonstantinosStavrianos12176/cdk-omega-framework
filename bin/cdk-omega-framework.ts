#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkOmegaFrameworkStack } from '../lib/cdk-omega-framework-stack';

const app = new cdk.App();
new CdkOmegaFrameworkStack(app, 'CdkOmegaFrameworkStack');
