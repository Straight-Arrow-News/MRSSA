output "api_gateway_id" {
  value       = aws_apigatewayv2_api.san_mrssa_aaa.id
  description = "The ID of the API Gateway"
}

output "api_gateway_endpoint" {
  value       = aws_apigatewayv2_api.san_mrssa_aaa.api_endpoint
  description = "The endpoint URL of the API Gateway"
}

output "api_gateway_domain_name" {
  value       = replace(replace(aws_apigatewayv2_api.san_mrssa_aaa.api_endpoint, "https://", ""), "http://", "")
  description = "The domain name of the API Gateway (without protocol)"
}

output "api_gateway_stage_name" {
  value       = aws_apigatewayv2_stage.san_mrssa_aas.name
  description = "The name of the API Gateway stage"
}
