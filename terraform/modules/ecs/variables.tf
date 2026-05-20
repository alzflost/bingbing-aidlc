variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "alb_target_group_arn" {
  type = string
}

variable "valkey_endpoint" {
  type = string
}

variable "dynamodb_table_arn" {
  type = string
}

variable "dynamodb_table_name" {
  type = string
}

variable "api_service_cpu" {
  type = number
}

variable "api_service_memory" {
  type = number
}

variable "agent_service_cpu" {
  type = number
}

variable "agent_service_memory" {
  type = number
}

variable "desired_count" {
  type = number
}

variable "alb_security_group_id" {
  type = string
}

variable "valkey_security_group_id" {
  type = string
}
