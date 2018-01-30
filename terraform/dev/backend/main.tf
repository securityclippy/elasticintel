provider "aws" {
  region = "us-east-1"
  profile = "demo-profile"
}

resource "aws_s3_bucket" "backend_bucket" {
  bucket = "demo-backend-bucket"
  acl = "private"
  lifecycle {
    prevent_destroy = true
  }
  versioning {
    enabled = true
  }
}