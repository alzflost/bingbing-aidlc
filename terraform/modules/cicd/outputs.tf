output "deploy_role_arn" {
  description = "ARN of the GitHub Actions deploy role (set as repo secret AWS_DEPLOY_ROLE_ARN)"
  value       = aws_iam_role.github_deploy.arn
}
