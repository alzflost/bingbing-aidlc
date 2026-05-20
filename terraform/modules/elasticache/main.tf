resource "aws_security_group" "valkey" {
  name_prefix = "${var.project_name}-${var.environment}-valkey-"
  vpc_id      = var.vpc_id
  description = "Security group for ElastiCache Valkey"

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    description = "Valkey access from private subnets"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-valkey-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_vpc" "selected" {
  id = var.vpc_id
}

resource "aws_elasticache_serverless_cache" "valkey" {
  engine = "valkey"
  name   = "${var.project_name}-${var.environment}"

  cache_usage_limits {
    data_storage {
      maximum = 5
      unit    = "GB"
    }

    ecpu_per_second {
      maximum = 5000
    }
  }

  subnet_ids         = var.private_subnet_ids
  security_group_ids = [aws_security_group.valkey.id]

  tags = {
    Name = "${var.project_name}-${var.environment}-valkey"
  }
}
