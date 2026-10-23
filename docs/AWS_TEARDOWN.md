# AWS teardown

After a manually approved demo, delete the SAM stack in the verified account and region, then confirm the API, Lambda, DynamoDB table, log groups, hosting bucket/distribution, and Cognito resources are gone. Check Cost Explorer after AWS reporting delay. Never run teardown against an unverified stack name.
