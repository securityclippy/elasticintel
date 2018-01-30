provider "aws" {
  region = "us-east-1"
  profile = "elastic"
}

module "s3" {
  source = "../../modules/s3"
  s3_bucket_name = "${var.s3_bucket_name}"
}
