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

variable "brightcove_policy_key" {
  type = string
}

variable "brightcove_account_id" {
  type = string
}

variable "rss_feed_url" {
  type = string
}

variable "grafana_labs_token" {
  type = string
}

variable "otel_exporter_otlp_endpoint" {
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
  source                      = "../infra/app"
  brightcove_policy_key       = var.brightcove_policy_key
  brightcove_account_id       = var.brightcove_account_id
  rss_feed_url                = var.rss_feed_url
  environment                 = var.environment
  grafana_labs_token          = var.grafana_labs_token
  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
}

