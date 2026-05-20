resource "aws_cloudwatch_event_rule" "trip_ended" {
  name        = "${var.project_name}-${var.environment}-trip-ended"
  description = "Trigger Reflection Lambda on trip end"

  event_pattern = jsonencode({
    source      = ["family-copilot.api-service"]
    detail-type = ["trip.ended"]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-trip-ended-rule"
  }
}

resource "aws_cloudwatch_event_target" "reflection_lambda" {
  rule      = aws_cloudwatch_event_rule.trip_ended.name
  target_id = "reflection-lambda"
  arn       = var.lambda_arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trip_ended.arn
}
