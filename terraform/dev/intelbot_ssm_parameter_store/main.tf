module "ssm_parameter" {
  source = "../../modules/intelbot_ssm_parameter_store"
  lambda_bot_token = "${var.lambda_bot_token}"
  lambda_bot_verification_token = "${var.lambda_bot_verification_token}"
  aws_profile = "${var.aws_profile}"
  lambda_bot_name = "${var.lambda_bot_name}"
}