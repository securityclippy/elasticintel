data "terraform_remote_state" "s3_bucket" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key    = "dev/s3/terraform.tfstate"
    region = "${var.region}"
    profile = "${var.aws_profile}"
  }
}

data "terraform_remote_state" "elasticsearch" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key    = "dev/elasticsearch/terraform.tfstate"
    region = "${var.region}"
    profile = "${var.aws_profile}"
  }
}

data "terraform_remote_state" "sns" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key    = "dev/sns/terraform.tfstate"
    region = "${var.region}"
    profile = "${var.aws_profile}"
  }
}

data "aws_iam_policy_document" "ingest_intel_iam_policy_document" {
  statement {
    sid = "1"
    effect = "Allow"
    actions = [
      "s3:*",
      "logs:*"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    sid = "2"
    effect = "Allow"
    actions = [
      "es:*"
    ]
    resources = [
      "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_arn}/*"
    ]
  }
}


data "aws_iam_policy_document" "ingest_intel_lambda_assume_role_policy" {
  statement {
    actions = [
      "sts:AssumeRole"]
    effect = "Allow"
    principals = {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"]
    }
  }
}


resource "aws_iam_role" "ingest_intel_iam_role" {
  name = "ingest_intel_iam_role"
  assume_role_policy = "${data.aws_iam_policy_document.ingest_intel_lambda_assume_role_policy.json}"
}

resource "aws_iam_role_policy" "ingest_intel_aim_policy" {
  policy = "${data.aws_iam_policy_document.ingest_intel_iam_policy_document.json}"
  role = "${aws_iam_role.ingest_intel_iam_role.id}"
}

data "archive_file" "lb_zip" {
  type = "zip"
  source_dir = "../../../ingest_feed_lambda"
  output_path = "../../../ingest_feed_lambda/lambda.zip"
}

resource "aws_s3_bucket_object" "ingest_s3_zip" {
  bucket = "${data.terraform_remote_state.s3_bucket.s3_bucket_name}"
  key = "ingest_feed_lambda.zip"
  source = "../../../ingest_feed_lambda/lambda.zip"
  etag = "${md5(file("../../../ingest_feed_lambda/lambda.zip"))}"
  depends_on = ["data.archive_file.lb_zip"]
}

resource "aws_lambda_function" "ingest_intel_lambda" {
  depends_on = [
    "aws_s3_bucket_object.ingest_s3_zip"
  ]
  function_name = "ingest_intel_lambda"
  #filename = "../../../ingest_feed_lambda/lambda.zip"
  s3_bucket = "${data.terraform_remote_state.s3_bucket.s3_bucket_name}"
  s3_key = "ingest_feed_lambda.zip"
  role = "${aws_iam_role.ingest_intel_iam_role.arn}"
  handler = "ingest_intel_lambda.handler"
  #source_code_hash = "${base64sha256(file("../../../ingest_feed_lambda/lambda.zip"))}"a
  source_code_hash = "${base64sha256(aws_s3_bucket_object.ingest_s3_zip.key)}"
  runtime = "python3.6"
  timeout = 300
  memory_size = 1024
}

resource "aws_cloudwatch_log_group" "ingest_feed_lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.ingest_intel_lambda.function_name}"
  retention_in_days = 7
}


data "aws_iam_policy_document" "feed_scheduler_iam_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*",
      "logs:*"
    ]
    resources = [
      //"${data.terraform_remote_state.s3_bucket.s3_bucket_arn}"
      "*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "sns:*"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:*"
    ]
    resources = ["*"]
  }
}


data "aws_iam_policy_document" "feed_scheduler_lambda_assume_role_policy_document" {
  statement {
    actions = [
      "sts:AssumeRole"]
    effect = "Allow"
    principals = {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "feed_scheduler_lambda_iam_role" {
  name = "feed_scheduler_lambda_iam_role"
  assume_role_policy = "${data.aws_iam_policy_document.feed_scheduler_lambda_assume_role_policy_document.json}"
}


resource "aws_iam_role_policy" "feed_scheduler_lambda_iam_role_policy" {
  role = "${aws_iam_role.feed_scheduler_lambda_iam_role.id}"
  policy = "${data.aws_iam_policy_document.feed_scheduler_iam_policy_document.json}"
}

data "archive_file" "fsl_zip" {
  type = "zip"
  source_dir = "${path.root}/../../../feed_scheduler_lambda"
  output_path = "${path.root}/../../../feed_scheduler_lambda/lambda.zip"
}

resource "aws_lambda_function" "feed_scheduler_lambda" {
  function_name = "feed_scheduler_lambda_terraform"
  filename = "${path.root}/../../../feed_scheduler_lambda/lambda.zip"
  #filename = "${path.module}/../../../feed_scheduler_lambda.zip"
  role = "${aws_iam_role.feed_scheduler_lambda_iam_role.arn}"
  handler = "feed_scheduler_lambda.handler"
  source_code_hash = "${base64sha256(file("${path.root}/../../../feed_scheduler_lambda/lambda.zip"))}"
  #source_code_hash = "${base64sha256(file("${path.module}../../../feed_scheduler_lambda.zip"))}"
  runtime = "python3.6"
  timeout = 300
  memory_size = 128
  environment {
    variables {
      "INTEL_BUCKET_NAME" = "${data.terraform_remote_state.s3_bucket.s3_bucket_name}",
      "INTEL_SNS_TOPIC_ARN" = "${data.terraform_remote_state.sns.sns_topic_arn}"
    }
  }
  depends_on = ["data.archive_file.fsl_zip"]
}

resource "aws_cloudwatch_log_group" "feed_scheduler_lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.feed_scheduler_lambda.function_name}"
  retention_in_days = 7
}

data "template_file" "config_data" {
  template = "${file("config.json")}"
  vars {
    elasticsearch_domain_endpoint = "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_endpoint}"
    ingest_intel_lambda_name = "${aws_lambda_function.ingest_intel_lambda.function_name}"
    feed_scheduler_lambda_name = "${aws_lambda_function.feed_scheduler_lambda.function_name}"
  }
}

resource "aws_s3_bucket_object" "config_json" {
  bucket = "${data.terraform_remote_state.s3_bucket.s3_bucket_name}"
  key = "/config/config.json"
  content = "${data.template_file.config_data.rendered}"
}

resource "aws_sns_topic_subscription" "ingest_intel_lambda_sns_subscription" {
  topic_arn = "${data.terraform_remote_state.sns.sns_topic_arn}"
  protocol = "lambda"
  endpoint = "${aws_lambda_function.ingest_intel_lambda.arn}"
}

resource "aws_cloudwatch_event_rule" "hourly_intel_run" {
    name = "hourly_intel_scheduler_run"
    description = "runs once an hour"
    schedule_expression = "rate(60 minutes)"
}

resource "aws_cloudwatch_event_target" "run_feed_scheduler_lambda" {
    rule = "${aws_cloudwatch_event_rule.hourly_intel_run.name}"
    target_id = "check_foo"
    arn = "${aws_lambda_function.feed_scheduler_lambda.arn}"
}

resource "aws_lambda_permission" "sns_topic_trigger" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.ingest_intel_lambda.function_name}"
    principal = "sns.amazonaws.com"
    source_arn = "${data.terraform_remote_state.sns.sns_topic_arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_feed_scheduler" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.feed_scheduler_lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.hourly_intel_run.arn}"
}


### IOC Search Lambda
/*
data "aws_iam_policy_document" "iocs_search_iam_policy_document" {
  statement {
    sid = "1"
    effect = "Allow"
    actions = [
      "logs:*"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    sid = "2"
    effect = "Allow"
    actions = [
      "es:*"
    ]
    resources = [
      "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "ioc_search_lambda_assume_role_policy" {
  statement {
    actions = [
      "sts:AssumeRole"]
    effect = "Allow"
    principals = {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ioc_search_intel_iam_role" {
  name = "ioc_search_iam_role"
  assume_role_policy = "${data.aws_iam_policy_document.ioc_search_lambda_assume_role_policy.json}"
}

resource "aws_iam_role_policy" "iocsearch_aim_policy" {
  policy = "${data.aws_iam_policy_document.iocs_search_iam_policy_document.json}"
  role = "${aws_iam_role.ioc_search_intel_iam_role.id}"
}

data "archive_file" "ioc_search_zip" {
  type = "zip"
  source_dir = "../../../iocsearch"
  output_path = "../../../iocsearch/lambda.zip"
}

resource "aws_lambda_function" "iocsearch_lambda" {
  function_name = "iocsearch_lambda_terraform"
  filename = "${path.root}/../../../iocsearch/lambda.zip"
  role = "${aws_iam_role.ioc_search_intel_iam_role.arn}"
  handler = "iocsearch_lambda.handler"
  source_code_hash = "${base64sha256(file("${path.root}/../../../iocsearch/lambda.zip"))}"
  runtime = "python3.6"
  timeout = 300
  memory_size = 128
  environment {
    variables {
      "ES_HOST" = "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_endpoint}",
    }
  }
  depends_on = ["data.archive_file.ioc_search_zip"]
}
*/
