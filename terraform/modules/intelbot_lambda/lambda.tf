provider "aws" {
  region = "${var.aws_region}"
  profile = "${var.aws_profile}"
}

data "terraform_remote_state" "ssm_parameter_store" {
  backend = "local"
  config {
    path = "../intelbot_ssm_parameter_store/terraform.tfstate"
  }
}

data "terraform_remote_state" "elasticsearch" {
  backend = "s3"
  config {
    bucket = "${var.backend_bucket}"
    key    = "dev/elasticsearch/terraform.tfstate"
    region = "${var.aws_region}"
    profile = "${var.aws_profile}"
  }
}

data "aws_iam_policy_document" "lambdabot_iam_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricData",
      "ssm:GetParameter",
      "ssm:GetParameters"
    ],
    resources = [
      #"${data.terraform_remote_state.ssm_parameter_store.lambda_bot_token_arn}",
      #"${data.terraform_remote_state.ssm_parameter_store.lambda_bot_token_arn}/*",
      #"${data.terraform_remote_state.ssm_parameter_store.lambda_bot_verification_token_arn}",
      #"${data.terraform_remote_state.ssm_parameter_store.lambda_bot_verification_token_arn}/*"
      "*"
    ]
  }
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


resource "aws_iam_policy" "lambdabot_iam_policy" {
  name = "${var.lambda_bot_name}_bot_policy"
  policy = "${data.aws_iam_policy_document.lambdabot_iam_policy_doc.json}"
}

data "aws_iam_policy_document" "lambdabot_assume_role_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals = {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "lambdabot_iam_role" {
  name = "${var.lambda_bot_name}_iam_role"
  assume_role_policy = "${data.aws_iam_policy_document.lambdabot_assume_role_policy_doc.json}"
}

resource "aws_iam_role_policy" "lambdabot_iam_role_policy" {
  name = "${var.lambda_bot_name}_iam_role_policy"
  policy = "${data.aws_iam_policy_document.lambdabot_iam_policy_doc.json}"
  role = "${aws_iam_role.lambdabot_iam_role.id}"
}

data "archive_file" "lambdabot_zip" {
  type = "zip"
  output_path = "../../../intelbot/lambda.zip"
  source_dir = "../../../intelbot"
}

resource "aws_lambda_function" "lambdabot" {
  filename = "../../../intelbot/lambda.zip"
  source_code_hash = "${base64sha256(file("../../../intelbot/lambda.zip"))}"
  function_name = "${var.lambda_bot_name}"
  handler = "lambda_function.handler"
  role = "${aws_iam_role.lambdabot_iam_role.arn}"
  environment {
    variables {
      "BOT_NAME" = "${var.lambda_bot_name}"
      "ES_HOST" = "${data.terraform_remote_state.elasticsearch.elasticsearch_domain_endpoint}",
    }
  }
  runtime = "python3.6"
  timeout = 120

}

