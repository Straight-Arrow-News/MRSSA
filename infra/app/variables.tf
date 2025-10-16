variable "environment" {
  type = string
}
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "san_feed_url" {
  type    = string
  default = "https://api.san.com"
}

variable "rss_feed_url" {
  type = string
}

variable "brightcove_policy_key" {
  type = string
}

variable "brightcove_account_id" {
  type = string
}

variable "otel_exporter_otlp_endpoint" {
  type = string
}

variable "grafana_labs_token" {
  type = string
}
