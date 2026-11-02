# Code review: homework deployment (follow-up)

All five blockers from the first review are fixed, and the Terraform code validates again. The chart is wired together, values and variables are used, `latest` is rejected, the pipeline tests, builds, and deploys, and the pod is hardened. A few gaps remain before the pipeline can be trusted to deploy unattended.

Checks run for this review:

| Check             | Result                                   |
| ----------------- | ---------------------------------------- |
| `pytest` (app)    | 23 passed                                |
| `helm lint helm`  | Passed (only the optional `icon` notice) |
| `tofu fmt -check` | Passed                                   |
| `tofu validate`   | Passed                                   |

## What's fixed since the first review

| First review                   | Status                                                                                                                                                                                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Terraform doesn't run       | Syntax fixed, chart path is `../helm`, providers pinned in [providers.tf](terraform/providers.tf), lock file committed, helm provider uses the 3.x `kubernetes = { }` syntax. The release references `kubernetes_namespace_v1.homework`, which matches the resource name. |
| 2. Traffic can't reach the app | Name, labels, and ports come from [values.yaml](helm/values.yaml). The container port is named `http` and the Service targets it by name. The Ingress points to `{{ .Values.name }}-service` and uses `ingress.path`.                                                     |
| 3. Unused values and variables | `replicaCount`, `service.port`, `var.namespace`, `var.environment`, and `var.image_tag` are all used. Variables have descriptions and defaults.                                                                                                                           |
| 4. Deploying `latest`          | The pipeline tags images with `$CI_COMMIT_SHORT_SHA`, and the `image_tag` validation in [variables.tf](terraform/variables.tf) rejects `latest` and empty tags.                                                                                                           |
| 5. Pipeline does nothing       | [.gitlab-ci.yml](.gitlab-ci.yml) has test, build, and deploy jobs. Deploy runs only on the default branch and takes the kubeconfig from a File-type variable.                                                                                                             |
| Chart name                     | Renamed to `homework`.                                                                                                                                                                                                                                                    |
| Resources                      | Requests and limits set (10m/100m CPU, 32Mi/64Mi memory).                                                                                                                                                                                                                 |

Also fixed:

- [Dockerfile](app/Dockerfile): it runs as non-root user 10001, sets `APP_VERSION` from the build argument (so `/version` reports the CI tag), and gunicorn binds to `$PORT`.
- [deployment.yaml](helm/templates/deployment.yaml): it has a Pod and container `securityContext` (`runAsNonRoot`, read-only root filesystem, no privilege escalation, all capabilities dropped, `RuntimeDefault` seccomp profile) and a writable in-memory `/tmp` for gunicorn.

**Tip:** add `tofu fmt -check` and `tofu validate` (after `tofu init -backend=false`) to the test stage, so that a broken reference can't reach the deploy job.

## 1. The cluster can't pull the CI image

The pipeline pushes to the GitLab registry (`$CI_REGISTRY_IMAGE/homework`), which is private by default. The chart has no `imagePullSecrets`, so pods end up in `ImagePullBackOff`.

**Fix:** add an `imagePullSecrets` value to the chart, and have Terraform create a `kubernetes_secret_v1` of type `kubernetes.io/dockerconfigjson` from a GitLab deploy token (`read_registry` scope). Pass the token as a masked CI/CD variable.

## 2. State is still local

[providers.tf](terraform/providers.tf) uses `backend "local"`. In CI the state file disappears when the job ends, so the next run tries to create the namespace and release again and fails because they already exist.

**Fix:** switch to the GitLab-managed HTTP backend (or S3/GCS) before the deploy job runs a second time. It also gives you state locking, so concurrent pipelines can't apply over each other.

## 3. No liveness or readiness probes

The app exposes `/health`, but the Deployment doesn't use it. Kubernetes cannot restart a hung pod, and `atomic = true` only waits for the container to start, not for the app to answer.

**Fix:**

```yaml
readinessProbe:
  httpGet: { path: /health, port: http }
  periodSeconds: 5
livenessProbe:
  httpGet: { path: /health, port: http }
  initialDelaySeconds: 10
  periodSeconds: 10
```

## Smaller items

- **The CI runner must reach the cluster.** The deploy job runs `tofu apply` against the kubeconfig in `$KUBECONFIG`. A KubeSolo cluster on a laptop is only reachable from a runner on the same network, so document that or register a local runner.
- **Hard-coded values in outputs.** The `service_endpoint` output in [outputs.tf](terraform/outputs.tf) hard-codes `homework-service` and port `8080`. Build it from the release name and the same port value the chart uses.
- **Port in two places.** Building the image with `--build-arg PORT=…` also requires changing `containerPort` in [values.yaml](helm/values.yaml). A comment next to each setting would prevent the mismatch.

## Suggested order

Fix points 1 and 2 first, so the pipeline can pull its image and deploy more than once. Then do point 3. The smaller items can wait for a cleanup pass.
