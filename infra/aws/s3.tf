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

# Bucket público para el security dashboard
resource "aws_s3_bucket" "security_dashboard" {
  bucket = "${var.project_name}-dashboard-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "security_dashboard" {
  bucket = aws_s3_bucket.security_dashboard.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "security_dashboard" {
  bucket = aws_s3_bucket.security_dashboard.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_policy" "security_dashboard" {
  bucket = aws_s3_bucket.security_dashboard.id
  depends_on = [aws_s3_bucket_public_access_block.security_dashboard]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.security_dashboard.arn}/*"
    }]
  })
}
