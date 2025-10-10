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

resource "aws_apigatewayv2_integration" "san_mrssa_aai_flipboard" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/flipboard"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_imds" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/imds"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_middleblock" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/middleblock"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_newsbreak" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/newsbreak"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_simplefeed_msn" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/simplefeed-msn"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_smart_news" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/smart-news"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_wurl" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/wurl"
  }
}

resource "aws_apigatewayv2_integration" "san_mrssa_aai_yahoo" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  integration_uri    = aws_lambda_function.san_mrssa_alf.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  request_parameters = {
    "overwrite:path" = "/simplefeed-msn"
  }
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_flipboard" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /flipboard"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_flipboard.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_imds" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /imds"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_imds.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_middleblock" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /middleblock"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_middleblock.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_newsbreak" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /newsbreak"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_newsbreak.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_simplefeed_msn_hyphen" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /simplefeed-msn"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_simplefeed_msn.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_smart_news" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /smart-news"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_smart_news.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_wurl" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /wurl"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_wurl.id}"
}

resource "aws_apigatewayv2_route" "san_mrssa_aar_yahoo" {
  api_id = aws_apigatewayv2_api.san_mrssa_aaa.id

  route_key = "GET /yahoo"
  target    = "integrations/${aws_apigatewayv2_integration.san_mrssa_aai_yahoo.id}"
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
