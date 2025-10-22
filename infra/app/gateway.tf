resource "aws_apigatewayv2_api" "san_mrssa_aaa" {
  name          = "san_mrssa_${var.environment}_aaa"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "san_mrssa_aas" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.san_mrssa_aclg_gateway.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_default" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai.id}"
}

resource "aws_cloudwatch_log_group" "san_mrssa_aclg_gateway" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.san_mrssa_aaa.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "san_mrssa_alp" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.san_mrssa_alf.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.san_mrssa_aaa.execution_arn}/*/*"
}
