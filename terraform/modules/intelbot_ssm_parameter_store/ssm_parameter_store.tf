provider "aws" {
  region = "${var.aws_region}"
  profile = "${var.aws_profile}"
}

resource "aws_ssm_parameter" "lamba_bot_token" {
  name = "${var.lambda_bot_name}_bot_token"
  type = "SecureString"
  value = "${var.lambda_bot_token}"
  overwrite = true
}

resource "aws_ssm_parameter" "lambda_bot_verification_token" {
  name = "${var.lambda_bot_name}_bot_verification_token"
  type = "SecureString"
  value = "${var.lambda_bot_verification_token}"
  overwrite = true
}