terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local backend for workshop environment
  # Production: switch to S3 backend
  # backend "s3" {
  #   bucket         = "family-copilot-tfstate"
  #   key            = "prod/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "family-copilot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
