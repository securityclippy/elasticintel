terraform {
  backend "s3" {
    bucket = "demo-backend-bucket"
    profile = "demo-profile"
    key = "dev/s3/terraform.tfstate"
    encrypt = true
    region = "us-east-1"
  }
}

