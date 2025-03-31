# The main.tf file contains the actual implementation of our requirements using the different resources and data elements.

/*
To add an expression to a variable like adding a suffix/prefix, 
we can make use of a locals declaration wherein we can declare variables that support expression syntaxes.
*/
locals {
  name-suffix = "${var.region}-${var.environment}"
}

# Fetch AWS account details
data "aws_caller_identity" "current" {}

# Resources are the actual infrastructure objects that need to be declared in terraform
resource "aws_dynamodb_table" "mcq-questionsets" {
  name           = "mcq-questionsets"
  hash_key       = "questionsetId"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "questionsetId"
    type = "S"
  }
}

# Table name : mcq-questions
# Partition key :  questionsetId (String)
# Sort key : questionId (String)

resource "aws_dynamodb_table" "mcq-questions" {
  name           = "mcq-questions"
  hash_key       = "questionsetId"
  range_key      = "questionId"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "questionsetId"
    type = "S"
  }

  attribute {
    name = "questionId"
    type = "S"
  }
}

# Table name : mcq-attempts
# Partition key :  questionsetId (String)

resource "aws_dynamodb_table" "mcq-attempts" {
  name           = "mcq-attempts"
  hash_key       = "questionsetId"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "questionsetId"
    type = "S"
  }
}

// IAM Policy to read / write to DynamoDB

resource "aws_iam_policy" "mcq_apigw_dynamodb" {
  name        = "mcq-apigw-dynamodb-rw"
  description = "Allows Read & Write access to the mcq tables"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:BatchWriteItem",
          "dynamodb:Query",
          "dynamodb:GetItem"
        ]
        Resource = [
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/mcq-questionsets",
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/mcq-questions"
        ]
      }
    ]
  })
}

#  Role for API GW to read / write to DynamoDB

resource "aws_iam_role" "mcq_apigw_role" {
  name        = "MCQ-APIGW-Role-RW"
  description = "Allows API Gateway to push logs to CloudWatch Logs."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Also attach the Policy to enable API GW to write to CW Logs 

resource "aws_iam_role_policy_attachment" "mcq_apigw_logs" {
  role       = aws_iam_role.mcq_apigw_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_iam_role_policy_attachment" "mcq_apigw_dynamodb" {
  role       = aws_iam_role.mcq_apigw_role.name
  policy_arn = aws_iam_policy.mcq_apigw_dynamodb.arn
}

# API Gateway

resource "aws_api_gateway_rest_api" "mcq_api" {
  name        = "MCQ-API"
  description = "API for MCQ tool"
}

resource "aws_api_gateway_resource" "questionset" {
  rest_api_id = aws_api_gateway_rest_api.mcq_api.id
  parent_id   = aws_api_gateway_rest_api.mcq_api.root_resource_id
  path_part   = "questionset"
}

resource "aws_api_gateway_resource" "batch" {
  rest_api_id = aws_api_gateway_rest_api.mcq_api.id
  parent_id   = aws_api_gateway_resource.questionset.id
  path_part   = "batch"
}

resource "aws_api_gateway_method" "post_batch" {
  rest_api_id   = aws_api_gateway_rest_api.mcq_api.id
  resource_id   = aws_api_gateway_resource.batch.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_batch" {
  rest_api_id             = aws_api_gateway_rest_api.mcq_api.id
  resource_id             = aws_api_gateway_resource.batch.id
  http_method             = aws_api_gateway_method.post_batch.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.region}:dynamodb:action/BatchWriteItem"
  credentials             = aws_iam_role.mcq_apigw_role.arn

  request_templates = {
    "application/json" = <<EOF
#set($inputRoot = $input.path('$'))
{
  "RequestItems": {
    "mcq-questionsets": [
      {
        "PutRequest": {
          "Item": {
            "questionsetId": {"S": "$inputRoot.questionsetid"},
            "name": {"S": "$inputRoot.name"},
            "description": {"S": "$inputRoot.description"}
          }
        }
      }
    ],
    "mcq-questions": [
      #foreach($q in $inputRoot.questions)
      {
        "PutRequest": {
          "Item": {
            "questionsetId": {"S": "$inputRoot.questionsetid"},
            "questionId": {"S": "$foreach.index"},
            "questionText": {"S": "$q.text"},
            "tags": {
              "L": [
                #foreach($tag in $q.tags)
                {"S": "$tag"}#if($foreach.hasNext),#end
                #end
              ]
            },
            "choices": {"L": [
              #foreach($choice in $q.choices)
              {"M": {
                "text": {"S": "$choice.text"},
                "targetedResponse": {"S": "$choice.targetedResponse"},
                "isCorrect": {"BOOL": $choice.isCorrect}
              }}#if($foreach.hasNext),#end
              #end
            ]}
          }
        }
      }#if($foreach.hasNext),#end
      #set($counter = $counter + 1)
      #end
    ]
  }
}
EOF
  }
}

resource "aws_api_gateway_integration_response" "post_batch_response" {
  rest_api_id = aws_api_gateway_rest_api.mcq_api.id
  resource_id = aws_api_gateway_resource.batch.id
  http_method = aws_api_gateway_method.post_batch.http_method
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  depends_on = [aws_api_gateway_integration.post_batch]
  
}

resource "aws_api_gateway_method_response" "post_batch_response_200" {
  rest_api_id = aws_api_gateway_rest_api.mcq_api.id
  resource_id = aws_api_gateway_resource.batch.id
  http_method = aws_api_gateway_method.post_batch.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_deployment" "mcq_api_deployment" {
  depends_on = [aws_api_gateway_integration.post_batch]
  rest_api_id = aws_api_gateway_rest_api.mcq_api.id
  
}

resource "aws_api_gateway_stage" "mcq_api_gateway_stage" {
      rest_api_id = aws_api_gateway_rest_api.mcq_api.id
      deployment_id = aws_api_gateway_deployment.mcq_api_deployment.id
      stage_name = "v1"
    }

module "iam_user_module" {
  source         = "./modules/iam_user_module"
  region         = var.region
  account_number = data.aws_caller_identity.current.account_id
}

# Create an API Gateway usage plan
resource "aws_api_gateway_usage_plan" "mcq_usage_plan" {
  name = "MCQ-Usage-Plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.mcq_api.id
    stage  = aws_api_gateway_stage.mcq_api_gateway_stage.stage_name
  }

  throttle_settings {
    rate_limit = 1000
    burst_limit = 1000
  }

  quota_settings {
    limit  = 10000
    period = "MONTH"
  }
}

# Create an API Gateway API key
resource "aws_api_gateway_api_key" "mcq_api_key" {
  name        = "MCQ-API-Key"
  description = "API Key for MCQ tool"
  enabled     = true
}

# Associate the API key with the usage plan
resource "aws_api_gateway_usage_plan_key" "mcq_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.mcq_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.mcq_usage_plan.id
}