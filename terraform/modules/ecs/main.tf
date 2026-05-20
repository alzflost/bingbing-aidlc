resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }
}

# --- Security Groups ---

resource "aws_security_group" "api_service" {
  name_prefix = "${var.project_name}-${var.environment}-api-"
  vpc_id      = var.vpc_id
  description = "Security group for API Service"

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
    description     = "From ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "agent_service" {
  name_prefix = "${var.project_name}-${var.environment}-agent-"
  vpc_id      = var.vpc_id
  description = "Security group for Agent Service"

  ingress {
    from_port       = 8081
    to_port         = 8081
    protocol        = "tcp"
    security_groups = [aws_security_group.api_service.id]
    description     = "From API Service"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-agent-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Valkey ingress from ECS services
resource "aws_security_group_rule" "valkey_from_api" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.api_service.id
  security_group_id        = var.valkey_security_group_id
  description              = "Valkey from API Service"
}

resource "aws_security_group_rule" "valkey_from_agent" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.agent_service.id
  security_group_id        = var.valkey_security_group_id
  description              = "Valkey from Agent Service"
}

# --- IAM Roles ---

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "api_task" {
  name = "${var.project_name}-${var.environment}-api-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "api_task" {
  name = "${var.project_name}-${var.environment}-api-task-policy"
  role = aws_iam_role.api_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["transcribe:StartStreamTranscription"]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = ["elasticache:Connect"]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:Query"]
        Resource = [var.dynamodb_table_arn]
      },
      {
        Effect   = "Allow"
        Action   = ["events:PutEvents"]
        Resource = ["*"]
      },
    ]
  })
}

resource "aws_iam_role" "agent_task" {
  name = "${var.project_name}-${var.environment}-agent-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "agent_task" {
  name = "${var.project_name}-${var.environment}-agent-task-policy"
  role = aws_iam_role.agent_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = ["arn:aws:bedrock:*::foundation-model/anthropic.claude-*"]
      },
      {
        Effect   = "Allow"
        Action   = ["elasticache:Connect"]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
        ]
        Resource = [var.dynamodb_table_arn]
      },
      {
        Effect   = "Allow"
        Action   = ["verifiedpermissions:IsAuthorized"]
        Resource = ["*"]
      },
    ]
  })
}

# --- Task Definitions ---

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}-${var.environment}/api-service"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "agent" {
  name              = "/ecs/${var.project_name}-${var.environment}/agent-service"
  retention_in_days = 90
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-${var.environment}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_service_cpu
  memory                   = var.api_service_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.api_task.arn

  container_definitions = jsonencode([{
    name  = "api-service"
    image = "placeholder:latest"
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    environment = [
      { name = "VALKEY_ENDPOINT", value = var.valkey_endpoint },
      { name = "DYNAMODB_TABLE", value = var.dynamodb_table_name },
      { name = "AGENT_SERVICE_URL", value = "http://agent.${var.project_name}.local:8081" },
      { name = "ENVIRONMENT", value = var.environment },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.api.name
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "api"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "agent" {
  family                   = "${var.project_name}-${var.environment}-agent"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_service_cpu
  memory                   = var.agent_service_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.agent_task.arn

  container_definitions = jsonencode([{
    name  = "agent-service"
    image = "placeholder:latest"
    portMappings = [{
      containerPort = 8081
      protocol      = "tcp"
    }]
    environment = [
      { name = "VALKEY_ENDPOINT", value = var.valkey_endpoint },
      { name = "DYNAMODB_TABLE", value = var.dynamodb_table_name },
      { name = "BEDROCK_MODEL_ID", value = "anthropic.claude-3-5-haiku-20241022-v1:0" },
      { name = "ENVIRONMENT", value = var.environment },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.agent.name
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "agent"
      }
    }
  }])
}

data "aws_region" "current" {}

# --- Services ---

resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${var.project_name}.local"
  vpc  = var.vpc_id
}

resource "aws_service_discovery_service" "agent" {
  name = "agent"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.api_service.id]
  }

  load_balancer {
    target_group_arn = var.alb_target_group_arn
    container_name   = "api-service"
    container_port   = 8080
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
}

resource "aws_ecs_service" "agent" {
  name            = "${var.project_name}-${var.environment}-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.agent_service.id]
  }

  service_registries {
    registry_arn = aws_service_discovery_service.agent.arn
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
}
