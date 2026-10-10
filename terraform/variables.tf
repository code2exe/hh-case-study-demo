variable "region" {
  description = "AWS region for ECR."
  type        = string
}

variable "github_owner" {
  description = "GitHub user or organization that owns the repository."
  type        = string
}

variable "repo_name" {
  description = "GitHub repository name allowed to push images from main."
  type        = string
}
