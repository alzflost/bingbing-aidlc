output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.dns_name
}

output "valkey_endpoint" {
  description = "ElastiCache Valkey endpoint"
  value       = module.elasticache.endpoint
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = module.dynamodb.table_name
}

output "api_service_url" {
  description = "API Service URL (via ALB)"
  value       = "https://${module.alb.dns_name}"
}

output "lambda_function_name" {
  description = "Reflection Lambda function name"
  value       = module.lambda.function_name
}

output "github_deploy_role_arn" {
  description = "GitHub Actions deploy role ARN (set as repo secret AWS_DEPLOY_ROLE_ARN)"
  value       = module.cicd.deploy_role_arn
}
