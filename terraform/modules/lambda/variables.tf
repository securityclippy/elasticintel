variable "intel_scheduler_lambda" {
  description = "Name of intel scheduler lambda"
  default = "feed_scheduler_lambda"
}

variable "ingest_intel_feed_lambda" {
  description = "Name of lambda used to retrieve and parse intel"
  default = "ingest_intel_feed_lambda"
}

variable "ingest_lambda_source_dir" {}

variable "feed_scheduler_lambda_source_dir" {}

variable "region" {}
variable "aws_profile" {}
variable "backend_bucket" {}
variable "prefix" {}