resource "aws_dynamodb_table" "vehicle_profiles" {
  name         = "${var.project_name}-${var.environment}-vehicle-profiles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "vehicle_id"
  range_key    = "actor_id"

  attribute {
    name = "vehicle_id"
    type = "S"
  }

  attribute {
    name = "actor_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-vehicle-profiles"
  }
}
