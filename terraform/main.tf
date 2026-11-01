resource "kubernetes_namespace_v1" "homework" {
  metadata {
    name = "homework"
    labels = {
      "managed-by" = "terraform"
    }
  }
}

resource "helm_release" "homework" {
  name      = "homework"
  chart     = "../helm"
  namespace = kubernetes_namespace_v1.homework.metadata[0].name

  atomic          = true
  cleanup_on_fail = true
  timeout         = 120


  set = [{
    name  = "image.repository"
    value = var.image_repository
    }, {
    name  = "image.tag"
    value = var.image_tag
    }, {
    name  = "environment"
    value = var.environment
  }]
}
