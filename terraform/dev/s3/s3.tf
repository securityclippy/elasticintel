provider "aws" {
  region = "${var.region}"
  profile = "${var.aws_profile}"
}

module "s3" {
  source = "../../modules/s3"
  s3_bucket_name = "${var.s3_bucket_name}"
}
