
## Prerequisites

1. An AWS Account 
2. Install Terraform 

## Step 1 : Create AWS resources

Run the Terraform script to create the resources within your AWS Account

Note : you may optionally change the region in the [terraform.auto.tfvars](./terraform.auto.tfvars) file 

```sh
terraform init
terraform apply
```

### Test

Wait for a few (3-5) mins & then run the below to test if the API is operational

```sh
API_KEY=$(terraform output -raw mcq_api_key)
API_URL=$(terraform output -raw api_gw_url)

# echo $API_URL
# echo $API_KEY

curl --request POST "$API_URL/questionset/batch" \
  --header "Content-Type: application/json" \
  --header "x-api-key:$API_KEY" \
  --data '{
"questionsetid": "api-test-2503151722",
  "name": "AWS API GW Test",
  "description": "A set of questions to test knowledge on advanced features and use cases of AWS API Gateway.",
  "questions": [    
    {
      "text": "What is the primary purpose of AWS API Gateway?",
      "choices": [
        {
          "text": "To create, publish, maintain, monitor, and secure APIs at any scale.",
          "targetedResponse": "Correct! AWS API Gateway is a fully managed service that makes it easy to create and manage APIs.",
          "isCorrect": true
        },
        {
          "text": "To store and retrieve data with low latency.",
          "targetedResponse": "Incorrect. This describes Amazon DynamoDB, not API Gateway.",
          "isCorrect": false
        },
        {
          "text": "To manage serverless compute resources.",
          "targetedResponse": "Incorrect. This describes AWS Lambda, not API Gateway.",
          "isCorrect": false
        }
      ],
      "tags": [
        "api-gateway",
        "aws",
        "serverless"
      ]
    }
  ]
}'
```

```sh
clear
ACCESS_KEY_ID=$(terraform output -raw mcq_web_ui_access_key_id
SECRET_ACCESS_KEY=$(terraform output -raw mcq_web_ui_secret_access_key)
AWS_REGION=us-east-2

docker run -p 5001:5000 --name mcq-tool -e AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION sagarmhatre/mcquery:1.9


docker run -p 5001:5000 --name mcq-tool -e AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION sagarmhatre/mcquery:1.9


docker run -d -p 5001:5000 --name mcq-tool -e AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION sagarmhatre/mcquery:1.9


docker run -d -p 5001:5000 --name mcq-tool -e AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION sagarmhatre/mcquery:1.9


```

## Step 2 : Set up our Custom GPT 


https://pages.awscloud.com/GLOBAL-other-GC-Traincert-Foundational-and-Associate-Certification-Challenge-2025-reg.html?sc_icampaign=aware_global_200_certification_found-assoc-challenge_1up_tnc&sc_ichannel=ha&sc_icontent=awssm-2022050_aware_tnc&sc_iplace=1up&trk=9047985f-e9d5-42d4-813d-e98786e3b854~ha_awssm-2022050_aware_tnc

## How to destroy locally

```sh
cd mcq-mgr/infra
terraform init

terraform plan -destroy 

# Review the above & then ...

terraform destroy

```