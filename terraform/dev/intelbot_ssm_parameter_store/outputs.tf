output "lambda_bot_token_arn" {
  value = "${module.ssm_parameter.lambda_bot_token_arn}"
}

output "lambda_bot_verification_token_arn" {
  value = "${module.ssm_parameter.lambda_bot_verification_token_arn}"
}