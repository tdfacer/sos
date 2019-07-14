output "dynamo_table_arn" {
  value = module.sos-infrasctructure.dynamo_table_arn
  description = "The ARN of the DynamoDB Table."
}
