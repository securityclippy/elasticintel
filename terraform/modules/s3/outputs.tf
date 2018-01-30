output "s3_bucket_name" {
  value = "${aws_s3_bucket.s3_intel_bucket.bucket}"
}

output "s3_bucket_arn" {
  value = "${aws_s3_bucket.s3_intel_bucket.arn}"
}