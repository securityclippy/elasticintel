variable "region" {}
variable "aws_profile" {}
#variable "prefix" {}

variable "elasticsearch_domain_name" {
  description = "name of elasticsearch domain"
  default = "elastic-intel"
}

variable "user_ip_address" {
  type = "list"
  description = "Ip address for basic testing"
}

variable "es_instance_type" {
  default = "t2.small.elasticsearch"
}

variable "instance_count" {
  default = 1
}

variable "dedicated_master" {
  default = true
}

variable "dedicated_master_count" {
  default = 1
}

variable "dedicated_master_type" {
  default = "t2.small.elasticsearch"
}

variable "ebs_volume_size" {
  default = 30
}

variable "ebs_volume_type" {
  default = "gp2"
}

variable "multi_zone_enabled" {
  default = false
}