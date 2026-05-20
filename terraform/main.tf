module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  domain_name       = var.domain_name
}

module "elasticache" {
  source = "./modules/elasticache"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}

module "dynamodb" {
  source = "./modules/dynamodb"

  project_name = var.project_name
  environment  = var.environment
}

module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  alb_target_group_arn = module.alb.target_group_arn
  valkey_endpoint    = module.elasticache.endpoint
  dynamodb_table_arn = module.dynamodb.table_arn
  dynamodb_table_name = module.dynamodb.table_name

  api_service_cpu    = var.api_service_cpu
  api_service_memory = var.api_service_memory
  agent_service_cpu    = var.agent_service_cpu
  agent_service_memory = var.agent_service_memory
  desired_count      = var.desired_count

  alb_security_group_id       = module.alb.security_group_id
  valkey_security_group_id    = module.elasticache.security_group_id
}

module "lambda" {
  source = "./modules/lambda"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  valkey_endpoint    = module.elasticache.endpoint
  dynamodb_table_arn = module.dynamodb.table_arn
  lambda_memory      = var.lambda_memory
  lambda_timeout     = var.lambda_timeout

  valkey_security_group_id = module.elasticache.security_group_id
}

module "eventbridge" {
  source = "./modules/eventbridge"

  project_name    = var.project_name
  environment     = var.environment
  lambda_arn      = module.lambda.function_arn
  lambda_name     = module.lambda.function_name
}
