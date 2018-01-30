data "aws_iam_policy_document" "es_domain_policy" {
  statement {
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = ["*"]
    }
    actions = [
      "es:*"
    ]
    resources = [
      "${aws_elasticsearch_domain.elasticsearch.arn}/*"
    ]
    condition {
      test = "IpAddress"
      values = [
        "${var.user_ip_address}",
      ]
      variable = "aws:SourceIp"
    }
  }
}

resource "aws_elasticsearch_domain_policy" "elasticsearch_domain_policy" {
  domain_name = "${var.elasticsearch_domain_name}"
  access_policies = "${data.aws_iam_policy_document.es_domain_policy.json}"
  depends_on = ["aws_elasticsearch_domain.elasticsearch"]
}

resource "aws_elasticsearch_domain" "elasticsearch" {
  domain_name = "${var.elasticsearch_domain_name}"
  elasticsearch_version = "6.0"
  cluster_config {
    zone_awareness_enabled = "${var.multi_zone_enabled}"
    instance_count = "${var.instance_count}"
    instance_type = "${var.es_instance_type}"
    dedicated_master_enabled = "${var.dedicated_master}"
    dedicated_master_count = "${var.dedicated_master_count}"
    dedicated_master_type = "${var.dedicated_master_type}"
  }
  ebs_options {
    ebs_enabled = true
    volume_size = "${var.ebs_volume_size}"
    volume_type = "${var.ebs_volume_type}"
  }
}