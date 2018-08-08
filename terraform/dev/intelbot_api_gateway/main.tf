module "api_gateway" {
  source = "../../modules/intelbot_api_gateway"
  aws_profile = "${var.aws_profile}"
  lambda_bot_name = "${var.lambda_bot_name}"
  backend_bucket = "${var.backend_bucket_name}"
}