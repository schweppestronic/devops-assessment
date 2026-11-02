variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
  default     = "homework"
}

variable "environment" {
  type        = string
  description = "App's deploy environment"
  default     = "dev"
}

variable "image_repository" {
  type        = string
  description = "Docker image repository"
  default     = "registry.dock/homework"
}

variable "image_tag" {
  type        = string
  description = "Full version docker image tag"
  default     = "1.0.0"

  validation {
    condition     = var.image_tag != "latest" && var.image_tag != ""
    error_message = "Tag 'latest' is not allowed, use full version tags instead."
  }
}

variable "kubeconfig_path" {
  description = "Path to kubernetes config file"
  type        = string
  default     = "~/.kube/config"
}
