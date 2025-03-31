variable "environment" {
  description = "The environment e.g uat or prod or dev"
  type        = string
  default     = "v0"
}

variable "region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-2"
}