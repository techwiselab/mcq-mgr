output "api_gw_url" {
  value = aws_api_gateway_stage.mcq_api_gateway_stage.invoke_url
}

output "mcq_web_ui_access_key_id" {
  value = module.iam_user_module.mcq_web_ui_access_key_id
  sensitive = true
}

output "mcq_web_ui_secret_access_key" {
  value = module.iam_user_module.mcq_web_ui_secret_access_key
  sensitive = true
}

output "mcq_api_key" {
  value     = aws_api_gateway_api_key.mcq_api_key.value
  sensitive = true
}
