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
