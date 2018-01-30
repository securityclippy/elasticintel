output "lambda_arn" {
  value = "${aws_lambda_function.lambdabot.arn}"
}

output "lambda_function_name" {
  value = "${aws_lambda_function.lambdabot.function_name}"
}