output "s3_bucket_name" {
  value = aws_s3_bucket.security_reports.id
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.security_reports.arn
}

output "github_actions_access_key_id" {
  value = aws_iam_access_key.github_actions.id
}

output "github_actions_secret_key" {
  value     = aws_iam_access_key.github_actions.secret
  sensitive = true
}

output "lambda_function_name" {
  value = aws_lambda_function.security_agent.function_name
}

output "dashboard_bucket_name" {
  description = "Nombre del bucket del dashboard"
  value       = aws_s3_bucket.security_dashboard.id
}

output "dashboard_url" {
  description = "URL pública del security dashboard"
  value       = "http://${aws_s3_bucket.security_dashboard.id}.s3-website-${var.aws_region}.amazonaws.com"
}
