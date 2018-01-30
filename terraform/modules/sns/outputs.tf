output "sns_topic_arn" {
  value = "${aws_sns_topic.intel_sns_topic.arn}"
}