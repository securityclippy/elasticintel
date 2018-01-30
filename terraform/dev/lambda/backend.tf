terraform {
  backend "s3" {
    bucket = "demo-backend-bucket"
    profile = "demo-profile"
    key = "dev/lambda/terraform.tfstate"
    encrypt = true
    region = "us-east-1"
  }
}

