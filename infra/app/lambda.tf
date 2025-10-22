resource "aws_iam_role" "san_mrssa_air" {
  name = "san_mrssa_${var.environment}_air"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "san_mrssa_airpa" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.san_mrssa_air.name
}

resource "aws_lambda_function" "san_mrssa_alf" {
  function_name = "san_mrssa_${var.environment}_alf"
  role          = aws_iam_role.san_mrssa_air.arn
  description   = "Function feeds for syndication partners"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.san_mrssa_aer.repository_url}:latest"

  timeout     = 60
  memory_size = 2048
  environment {
    variables = {
      REGION_AWS                  = var.aws_region
      FEED_URL                    = var.san_feed_url
      OTEL_DEPLOYMENT_ENVIRONMENT = var.environment
    }
  }

  lifecycle {
    ignore_changes = [image_uri]
  }
}

resource "aws_cloudwatch_log_group" "san_mrssa_aclg" {
  name              = "/aws/lambda/${aws_lambda_function.san_mrssa_alf.function_name}"
  retention_in_days = 14
}
