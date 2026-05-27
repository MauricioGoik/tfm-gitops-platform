resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "security_reports" {
  bucket = "${var.project_name}-security-reports-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "security_reports" {
  bucket = aws_s3_bucket.security_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "security_reports" {
  bucket = aws_s3_bucket.security_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "security_reports" {
  bucket = aws_s3_bucket.security_reports.id
  versioning_configuration {
    status = "Enabled"
  }
}
