# This module creates a user that will be used in the backend of our Web UI to connect to the DynamoDB Tables

# Fetch AWS account details
data "aws_caller_identity" "current" {}

resource "aws_iam_user" "mcq_web_ui" {
  name = "mcq-web-ui"
}

resource "aws_iam_user_policy_attachment" "read_only_access" {
  user       = aws_iam_user.mcq_web_ui.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

resource "aws_iam_user_policy" "allow_attempts_put" {
  name   = "AllowDynamoDBPut"
  user   = aws_iam_user.mcq_web_ui.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "VisualEditor0"
        Effect   = "Allow"
        Action   = "dynamodb:PutItem"
        Resource = [
          "arn:aws:dynamodb:${var.region}:${var.account_number}:table/mcq-attempts",
          "arn:aws:dynamodb:${var.region}:${var.account_number}:table/mcq-questions",
          "arn:aws:dynamodb:${var.region}:${var.account_number}:table/mcq-questionsets"
          ]
      }
    ]
  })
}

resource "aws_iam_access_key" "mcq_web_ui_access_key" {
  user = aws_iam_user.mcq_web_ui.name
}

output "mcq_web_ui_access_key_id" {
  value = aws_iam_access_key.mcq_web_ui_access_key.id
   sensitive = true
}

output "mcq_web_ui_secret_access_key" {
  value = aws_iam_access_key.mcq_web_ui_access_key.secret
   sensitive = true
}

