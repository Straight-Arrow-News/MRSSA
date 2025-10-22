terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.12.0"
    }
  }
  backend "s3" {
    bucket                   = "terraform-s3-state-san"
    key                      = "san-mrssa-infra"
    region                   = "us-east-1"
    shared_credentials_files = ["~/.aws/credentials"]
  }
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "rss_feed_url" {
  type = string
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      environment = var.environment
    }
  }
}


module "san_mrss" {
  source       = "../infra/app"
  rss_feed_url = var.rss_feed_url
  environment  = var.environment
}

