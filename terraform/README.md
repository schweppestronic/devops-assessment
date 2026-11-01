<!-- BEGIN_TF_DOCS -->

## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.5 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | ~> 3.3 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | ~> 3.4 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_helm"></a> [helm](#provider\_helm) | 3.3.0 |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | 3.4.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [helm_release.homework](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [kubernetes_namespace_v1.homework](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/resources/namespace_v1) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_environment"></a> [environment](#input\_environment) | App's deploy environment | `string` | `"dev"` | no |
| <a name="input_image_repository"></a> [image\_repository](#input\_image\_repository) | Docker image repository | `string` | `"registry.dock/homework"` | no |
| <a name="input_image_tag"></a> [image\_tag](#input\_image\_tag) | Full version docker image tag | `string` | `"1.0.0"` | no |
| <a name="input_kubeconfig_path"></a> [kubeconfig\_path](#input\_kubeconfig\_path) | Path to kubernetes config file | `string` | `"~/.kube/config"` | no |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | Kubernetes namespace | `string` | `"homework"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_release_name"></a> [release\_name](#output\_release\_name) | Helm release name |
| <a name="output_release_revision"></a> [release\_revision](#output\_release\_revision) | Helm release revision, useful for helm rollback |
| <a name="output_release_status"></a> [release\_status](#output\_release\_status) | Helm release status (e.g. deployed, failed) |
| <a name="output_service_endpoint"></a> [service\_endpoint](#output\_service\_endpoint) | In-cluster address of the app |

<!-- END_TF_DOCS -->