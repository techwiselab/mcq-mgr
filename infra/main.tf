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

module "iam_user_module" {
  source         = "./modules/iam_user_module"
  region         = var.region
  account_number = data.aws_caller_identity.current.account_id
}
