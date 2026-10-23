# AWS cost safety

This project does not create AWS resources automatically. Local defaults are `AWS_DEPLOY_ENABLED=false`, `AI_PROVIDER=mock`, and `BEDROCK_ENABLED=false`.

Review current AWS pricing and your account Free Tier status at [AWS Pricing](https://aws.amazon.com/pricing/) and [AWS Billing](https://console.aws.amazon.com/billing/). Free Tier limits vary by account age, region, and service; budget alerts notify but do not cap spending. Before deployment, create a small AWS Budget, confirm the exact resource list, region, retention, and Bedrock model pricing, then explicitly approve the change. Never assume the cost is zero.

Potential charges: API Gateway requests, Lambda duration, DynamoDB reads/writes/storage, CloudWatch logs, S3/CloudFront hosting, Cognito usage, and Bedrock tokens. Bedrock is intentionally not wired into the default path.

Teardown: delete the SAM stack, verify the DynamoDB table and Lambda/API resources are gone, remove CloudWatch log groups, empty/delete any hosting buckets and CloudFront distributions, then check Billing Cost Explorer after the service's reporting delay. Do not run teardown commands until the stack name and account are verified.
