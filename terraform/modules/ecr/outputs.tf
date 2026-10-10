output "repository_url" {
  description = "URL used to tag and push container images."
  value       = aws_ecr_repository.this.repository_url
}

output "repository_arn" {
  description = "ARN used to scope image push permissions."
  value       = aws_ecr_repository.this.arn
}
