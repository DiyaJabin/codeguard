# AWS deployment (manual, not automated)

Install AWS SAM and configure credentials only when you are ready. Run `sam validate --template-file infra/template.yaml`, inspect the change set, and produce a resource/cost review before any `sam deploy`. Set a real frontend origin and add Cognito/JWT authorization before exposing the API. Keep Bedrock disabled unless model access, quotas, prompt controls, and pricing have been reviewed.
