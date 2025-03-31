
## Prerequisites

1. AWS Account ,  [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 
2. Terraform 
3. Git 
4. ChatGPT Plus / Pro Subscription 

## Step 1 : Create AWS resources

Run the Terraform script to create the resources within your AWS Account

Note : you may optionally change the region in the [infra/terraform.auto.tfvars](./infra/terraform.auto.tfvars) file 

```sh
cd infra
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


## Step 2 : Set up Custom GPT 






## Step 3 : Run Web App

### Local Run ( without docker )

```sh

cd infra

AWS_ACCESS_KEY_ID=$(terraform output -raw mcq_web_ui_access_key_id)
AWS_SECRET_ACCESS_KEY=$(terraform output -raw mcq_web_ui_secret_access_key)
AWS_REGION=us-east-2

# echo $AWS_ACCESS_KEY_ID
# echo $AWS_SECRET_ACCESS_KEY

cd ..

# Navigate to the application directory
cd app

# Set up virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Run the Flask server
python server.py
```

Navigate to [Dashboard](http://127.0.0.1:5000/static/dashboard.html)


### With Docker 


```sh

cd infra

AWS_ACCESS_KEY_ID=$(terraform output -raw mcq_web_ui_access_key_id)
AWS_SECRET_ACCESS_KEY=$(terraform output -raw mcq_web_ui_secret_access_key)
AWS_REGION=us-east-2

# echo $AWS_ACCESS_KEY_ID
# echo $AWS_SECRET_ACCESS_KEY

cd ..

# Navigate to the application directory
cd app

docker build -t mcq-mgr:1.0 .

docker rm mcq-tool -f

docker run -d -p 5000:5000 --name mcq-mgr -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e  AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION mcq-tool:1.0 

```

Navigate to [Dashboard](http://127.0.0.1:5000/static/dashboard.html)


## AWS resources cleanup 

Note : Proceed with caution , will permanantly delete your data

```sh
cd infra
terraform plan -destroy 
# Review the above & then ...
terraform destroy
```