output "release_name" {
  description = "Helm release name"
  value       = helm_release.homework.name
}

output "release_status" {
  description = "Helm release status (e.g. deployed, failed)"
  value       = helm_release.homework.status
}

output "release_revision" {
  description = "Helm release revision, useful for helm rollback"
  value       = helm_release.homework.metadata.revision
}

output "service_endpoint" {
  description = "In-cluster address of the app"
  value       = "homework-service.${kubernetes_namespace_v1.homework.metadata[0].name}.svc.cluster.local:8080"
}