provider "aws" {
  region = "${var.region}"
  profile = "${var.aws_profile}"
}

module "elasticsearch" {
  source = "../../modules/elasticsearch"
  user_ip_address = ["${var.user_ip_address}"]
  #t2.small.elasticseach | t2.medium.elasticsearch | c4.large | c4.xlarge | c4. 2xlarge | c4.4xlarge | c4.8xlarge
  es_instance_type = "m3.medium.elasticsearch"
  ebs_volume_size = "100"
  instance_count = "2"
  dedicated_master = false
  region = "${var.region}"
  aws_profile = "${var.aws_profile}"
  elasticsearch_domain_name = "${var.elasticsearch_domain_name}"
  #prefix = "${var.prefix}"
  #dedicated_master_count = 2
}


