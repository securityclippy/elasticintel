output "lambda_bot_token_arn" {
  value = "${aws_ssm_parameter.lamba_bot_token.arn}"
}

output "lambda_bot_verification_token_arn" {
  value = "${aws_ssm_parameter.lambda_bot_verification_token.arn}"
}

output "lambda_bot_name" {
  value = "${var.lambda_bot_name}"
}