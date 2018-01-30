output "event_path" {
  value = "${aws_api_gateway_resource.LambdabotResource.path}"
}

output "invoke_url" {
  value = "${aws_api_gateway_deployment.lambdabot.invoke_url}"
}

output "event_subscription_url" {
  value = "${aws_api_gateway_deployment.lambdabot.invoke_url}${aws_api_gateway_resource.LambdabotResource.path}"
}