module "whois_lambda" {
  source = "../../../modules/whois_lambda"
  region = "${var.region}"
  profile = "${var.profile}"
  backend_bucket = "${var.backend_bucket_name}"
}