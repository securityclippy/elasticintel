output "elasticsearch_domain_endpoint" {
  value = "${aws_elasticsearch_domain.elasticsearch.endpoint}"
}

output "elasticsearch_domain_arn" {
  value = "${aws_elasticsearch_domain.elasticsearch.arn}"
}