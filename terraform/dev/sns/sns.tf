provider "aws" {
  region = "us-east-1"
  profile = "${var.aws_profile}"
}

module "sns" {
  source = "../../modules/sns"
}
