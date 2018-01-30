resource "aws_sns_topic" "intel_sns_topic" {
  name = "${var.sns_topic_name}"
}

