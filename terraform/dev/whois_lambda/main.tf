module "whois_lambda" {
  source = "../../../modules/whois_lambda"
  region = "${var.region}"
  profile = "${var.aws_profile}"
  backend_bucket = "${var.backend_bucket_name}"
}