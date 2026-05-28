resource "aws_iam_role" "lambda_agent" {
  name = "${var.project_name}-lambda-agent"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_agent.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_layer_version" "python_deps" {
  s3_bucket           = aws_s3_bucket.security_reports.id
  s3_key              = "lambda/lambda_layer.zip"
  layer_name          = "${var.project_name}-python-deps"
  compatible_runtimes = ["python3.13"]
  description         = "requests and dependencies for security agent"
}

data "archive_file" "lambda_agent" {
  type        = "zip"
  output_path = "${path.module}/lambda_agent.zip"
  source {
    content  = file("${path.module}/handler.py")
    filename = "handler.py"
  }
}

resource "aws_lambda_function" "security_agent" {
  filename         = data.archive_file.lambda_agent.output_path
  function_name    = "${var.project_name}-security-agent"
  role             = aws_iam_role.lambda_agent.arn
  handler          = "handler.handler"
  runtime          = "python3.13"
  timeout          = 60
  memory_size      = 256
  source_code_hash = data.archive_file.lambda_agent.output_base64sha256
  layers           = [aws_lambda_layer_version.python_deps.arn]

  environment {
    variables = {
      GROQ_API_KEY = var.groq_api_key
    }
  }
}
