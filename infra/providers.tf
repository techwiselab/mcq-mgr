# The provider.tf contains the provider definitions and the dependencies information.
# Setting and locking the Dependencies
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.52.0"
    }
  }

  required_version = "~> 1.10.0"

  # Backend as S3 for Remote State Storage
  backend "s3" {
    bucket = "terraform-on-aws-eks-sagar-2024"
    key    = "dev/mcq-mgr/terraform.tfstate"
    region = "us-east-2"
    
    # For State Locking
    dynamodb_table = "dev-mcq-mgr"    
  } 
}

# Feeding the AWS providers with the data it needs
provider "aws" {
  # Set the default region
  region = var.region
}