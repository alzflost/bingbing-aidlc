variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "github_repo" {
  description = "GitHub repository (org/repo format)"
  type        = string
  default     = "alzflost/bingbing-aidlc"
}
