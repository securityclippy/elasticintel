output "ingest_intel_lambda_arn" {
  value = "${aws_lambda_function.ingest_intel_lambda.arn}"
}

output "ingest_intel_lambda_name" {
  value = "${aws_lambda_function.ingest_intel_lambda.function_name}"
}

output "feed_scheduler_lambda_name" {
  value = "${aws_lambda_function.feed_scheduler_lambda.function_name}"
}

output "ingest_intel_iam_role" {
  value = "${aws_iam_role.ingest_intel_iam_role.arn}"
}
