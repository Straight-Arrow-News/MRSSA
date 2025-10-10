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

variable "brightcove_policy_key" {
  type = string
}

variable "brightcove_account_id" {
  type = string
}
