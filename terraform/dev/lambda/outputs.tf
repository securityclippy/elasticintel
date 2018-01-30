output "ingest_intel_lambda_arn" {
  value = "${module.lambda.ingest_intel_lambda_arn}"
}

output "ingest_intel_lambda_name" {
  value = "${module.lambda.ingest_intel_lambda_name}"
}

output "feed_scheduler_lambda_name" {
  value = "${module.lambda.feed_scheduler_lambda_name}"
}
output "ingest_intel_iam_role" {
  value = "${module.lambda.ingest_intel_iam_role}"
}