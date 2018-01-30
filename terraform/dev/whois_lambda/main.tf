module "whois_lambda" {
  source = "../../../modules/whois_lambda"
  region = "${var.region}"
  profile = "${var.profile}"
}