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

# Generamos el zip directamente desde un string, sin depender de /tmp local
resource "aws_lambda_function" "security_agent" {
  filename         = "${path.module}/lambda_placeholder.zip"
  function_name    = "${var.project_name}-security-agent"
  role             = aws_iam_role.lambda_agent.arn
  handler          = "handler.handler"
  runtime          = "python3.13"
  timeout          = 60
  memory_size      = 256

  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256
}

data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"

  source {
    content  = "def handler(event, context): return {'statusCode': 200, 'body': 'placeholder'}"
    filename = "handler.py"
  }
}
