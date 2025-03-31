# // Donot uncomment this file. This file will be uncommented only in Github Actions
#   terraform {
#    // Backend as S3 for Remote State Storage
#     backend "s3" {
#       bucket = "terraform-on-aws-eks-sagar-2024"
#       key    = "dev/mcq-mgr/terraform.tfstate"
#       region = "us-east-1"

#       // For State Locking
#       dynamodb_table = "dev-mcq-mgr"    
#     } 
#   }