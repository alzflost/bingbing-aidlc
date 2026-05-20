variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "family-copilot"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "api_service_cpu" {
  description = "API Service CPU units"
  type        = number
  default     = 512
}

variable "api_service_memory" {
  description = "API Service memory (MiB)"
  type        = number
  default     = 1024
}

variable "agent_service_cpu" {
  description = "Agent Service CPU units"
  type        = number
  default     = 1024
}

variable "agent_service_memory" {
  description = "Agent Service memory (MiB)"
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "Desired ECS task count per service"
  type        = number
  default     = 2
}

variable "lambda_memory" {
  description = "Reflection Lambda memory (MiB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Reflection Lambda timeout (seconds)"
  type        = number
  default     = 300
}

variable "domain_name" {
  description = "Domain name for ALB certificate (optional)"
  type        = string
  default     = ""
}
