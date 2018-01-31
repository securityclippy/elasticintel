provider "aws" {
  region = "${var.region}"
  profile = "${var.profile}"
}

data "terraform_remote_state" "lambda" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key = "dev/lambda/terraform.tfstate"
    region = "us-east-1"
    profile = "${var.profile}"
  }
}

data "terraform_remote_state" "elasticsearch" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key    = "dev/elasticsearch/terraform.tfstate"
    region = "us-east-1"
    profile = "${var.profile}"
  }
}

data "archive_file" "whois_lambda" {
  type = "zip"
  source_dir = "../../../../whois_lambda"
  output_path = "../../../../whois_lambda/lambda.zip"
}

resource "aws_lambda_function" "whois_lambda" {
  function_name = "${var.prefix}-${var.region}-whois_lambda"
  handler = "lambda_function.handler"
  #role = "${data.aws_iam_role.lambda_iam_role.arn}"
  role = "${data.terraform_remote_state.lambda.ingest_intel_iam_role}"
  runtime = "python3.6"
  memory_size = 128
  timeout = 300
  filename = "../../../../whois_lambda/lambda.zip"
  source_code_hash = "${base64sha256(file("../../../../whois_lambda/lambda.zip"))}"
  environment {
    variables {
      "ES_HOST" = "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_endpoint}",
    }
  }
}

resource "aws_cloudwatch_event_rule" "every_3_minutes" {
  name = "${var.prefix}-${var.region}_every_3_minutes"
  description = "run every 3 minutes"
  schedule_expression = "rate(3 minutes)"
}

resource "aws_cloudwatch_event_target" "whois_lambda_trigger" {
  arn = "${aws_lambda_function.whois_lambda.arn}"
  rule = "${aws_cloudwatch_event_rule.every_3_minutes.name}"
}

resource "aws_lambda_permission" "permit_cloudwatch_trigger" {
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.whois_lambda.function_name}"
  principal = "events.amazonaws.com"
  statement_id = "AllowExecutionFromCloudWatch"
  source_arn = "${aws_cloudwatch_event_rule.every_3_minutes.arn}"
}

resource "aws_cloudwatch_log_group" "log_group2" {
  name = "/aws/lambda/${aws_lambda_function.whois_lambda.function_name}"
  retention_in_days = 1
}
