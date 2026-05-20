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

variable "valkey_endpoint" {
  type = string
}

variable "dynamodb_table_arn" {
  type = string
}

variable "lambda_memory" {
  type = number
}

variable "lambda_timeout" {
  type = number
}

variable "valkey_security_group_id" {
  type = string
}
