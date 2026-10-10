output "ecr_repository_url" {
  description = "ECR URL for the Kubernetes image reference."
  value       = module.ecr.repository_url
}

output "ci_role_arn" {
  description = "Value for the GitHub repository variable AWS_ROLE_ARN."
  value       = aws_iam_role.ci.arn
}
