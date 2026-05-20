resource "aws_security_group" "lambda" {
  name_prefix = "${var.project_name}-${var.environment}-lambda-"
  vpc_id      = var.vpc_id
  description = "Security group for Reflection Lambda"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound (Valkey, Bedrock, AgentCore)"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-lambda-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "valkey_from_lambda" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.lambda.id
  security_group_id        = var.valkey_security_group_id
  description              = "Valkey access from Lambda"
}

resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-${var.environment}-reflection-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.project_name}-${var.environment}-reflection-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
        ]
        Resource = ["arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-*"]
      },
      {
        Effect = "Allow"
        Action = [
          "elasticache:Connect",
        ]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
        ]
        Resource = [var.dynamodb_table_arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = ["arn:aws:logs:*:*:*"]
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
        ]
        Resource = ["*"]
      },
    ]
  })
}

data "aws_region" "current" {}

resource "aws_lambda_function" "reflection" {
  function_name = "${var.project_name}-${var.environment}-reflection"
  role          = aws_iam_role.lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory

  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      VALKEY_ENDPOINT    = var.valkey_endpoint
      DYNAMODB_TABLE     = "vehicle-profiles"
      BEDROCK_MODEL_ID   = "anthropic.claude-3-5-haiku-20241022-v1:0"
      ENVIRONMENT        = var.environment
    }
  }

  reserved_concurrent_executions = 10

  tags = {
    Name = "${var.project_name}-${var.environment}-reflection"
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.reflection.function_name}"
  retention_in_days = 90
}
