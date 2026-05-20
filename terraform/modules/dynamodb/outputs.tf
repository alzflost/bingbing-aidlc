output "table_arn" {
  value = aws_dynamodb_table.vehicle_profiles.arn
}

output "table_name" {
  value = aws_dynamodb_table.vehicle_profiles.name
}
