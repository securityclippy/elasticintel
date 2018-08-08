terraform {
  backend "s3" {
    bucket = "intel-backend-1"
    profile = "elastic"
    key = "dev/intelbot_ssm_parameter_store/terraform.tfstate"
    encrypt = true
    region = "us-east-1"
  }
}
