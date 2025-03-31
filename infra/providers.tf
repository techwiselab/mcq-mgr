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
}

# Feeding the AWS providers with the data it needs
provider "aws" {
  # Set the default region
  region = var.region
}