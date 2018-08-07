provider "aws" {
  region = "${var.region}"
  profile = "${var.aws_profile}"
}

module "lambda" {
  source = "../../modules/lambda"
  ingest_lambda_source_dir = "../../ingest_feed_lambda"
  feed_scheduler_lambda_source_dir = "../../feed_scheduler_lambda"
  region = "${var.region}"
  aws_profile = "${var.aws_profile}"
  backend_bucket = "${var.backend_bucket_name}"
  prefix = "${var.prefix}"
}
