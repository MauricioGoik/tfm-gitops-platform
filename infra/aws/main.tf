terraform {
  cloud {
    organization = "tfm-devops-mauricio"
    workspaces {
      name = "tfm-gitops-platform"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "tfm-gitops-platform"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}
