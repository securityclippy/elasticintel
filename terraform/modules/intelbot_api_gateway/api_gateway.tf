provider "aws" {
  region = "${var.aws_region}"
  profile = "${var.aws_profile}"
}

data "aws_caller_identity"  "current" {}

data "terraform_remote_state" "intelbot_lambda" {
  backend = "local"
  config {
    path = "../intelbot_lambda/terraform.tfstate"
  }
}

resource "aws_api_gateway_rest_api" "lambdabot_api" {
  name = "${var.lambda_bot_name}BotAPI"
  description = "API for lambda bot to use to call lambda functions"
}

resource "aws_api_gateway_resource" "LambdabotResource" {
  parent_id = "${aws_api_gateway_rest_api.lambdabot_api.root_resource_id}"
  path_part = "event-handler"
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
}

resource "aws_api_gateway_method" "lambdabot_post_method" {
  authorization = "NONE"
  http_method = "POST"
  resource_id = "${aws_api_gateway_resource.LambdabotResource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
}

resource "aws_api_gateway_integration" "lambdabot_event_handler_integration" {
  http_method = "POST"
  resource_id = "${aws_api_gateway_resource.LambdabotResource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
  integration_http_method = "POST"
  type = "AWS"
  uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${data.terraform_remote_state.intelbot_lambda.lambda_arn}/invocations"
  depends_on = ["aws_api_gateway_method.lambdabot_post_method"]
}

resource "aws_api_gateway_method_response" "lambdabot_response_method" {
  http_method = "POST"
  resource_id = "${aws_api_gateway_resource.LambdabotResource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
  status_code = "200"
  response_models {
    "application/json" = "Empty"
  }
  depends_on = ["aws_api_gateway_integration.lambdabot_event_handler_integration"]
}

resource "aws_api_gateway_integration_response" "lambdabot_event_handler_integration_response" {
  http_method = "${aws_api_gateway_method_response.lambdabot_response_method.http_method}"
  resource_id = "${aws_api_gateway_resource.LambdabotResource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
  status_code = "${aws_api_gateway_method_response.lambdabot_response_method.status_code}"
  depends_on = ["aws_api_gateway_method_response.lambdabot_response_method"]
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${data.terraform_remote_state.intelbot_lambda.lambda_function_name}"
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.lambdabot_api.id}/*/${aws_api_gateway_method.lambdabot_post_method.http_method}${aws_api_gateway_resource.LambdabotResource.path}"

}

resource "aws_api_gateway_deployment" "lambdabot" {
  rest_api_id = "${aws_api_gateway_rest_api.lambdabot_api.id}"
  stage_name = "dev"
  depends_on = [
    "aws_api_gateway_integration.lambdabot_event_handler_integration",
    "aws_api_gateway_integration_response.lambdabot_event_handler_integration_response"]
}