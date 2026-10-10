# hh-hello-api

## 1. What this is

A small FastAPI service with tests, a two-stage Docker image, GitHub Actions CI, Kubernetes manifests, and Terraform for ECR and CI access. The API exposes `/health`, `/hello?name=X`, and `/version`. `GREETING` defaults to `Hello`. `APP_VERSION` defaults to `unknown` when unset.

## 2. Run locally

Use Python 3.13. Run these commands from the repository root. The virtual environment lives outside the repository.

```sh
python3.13 -m venv /tmp/hh-hello-api-venv
. /tmp/hh-hello-api-venv/bin/activate
pip install -r app/requirements.txt -r app/requirements-dev.txt
ruff check app/
pytest app/
GREETING=Hello APP_VERSION=1.0.0 uvicorn main:app --app-dir app --port 8000
```

Or build and run the container:

```sh
docker build -f docker/Dockerfile -t hello-api .
docker run --rm -p 8000:8000 -e GREETING=Hello -e APP_VERSION=1.0.0 hello-api
```

In another terminal:

```sh
curl http://localhost:8000/health
curl 'http://localhost:8000/hello?name=X'
curl http://localhost:8000/version
```

Docker reads an ignore file at the build-context root or as `<Dockerfile>.dockerignore` next to the Dockerfile; this project uses `docker/Dockerfile.dockerignore`.

## 3. How to trigger CI

A pull request targeting `main` runs tests, builds the image, and scans it. Trivy fails the build for fixable HIGH or CRITICAL vulnerabilities. A merge or push to `main` also pushes the scanned image to ECR when `AWS_ROLE_ARN` is set. The image tag is the commit SHA.

Set the repository variable `AWS_ROLE_ARN` to the Terraform `ci_role_arn` output. Set `AWS_REGION` in the workflow to the same region used by Terraform; its default is `us-east-1`. Without `AWS_ROLE_ARN`, all AWS steps are skipped. Tests, builds, and scans still run and can fail.

## 4. How to apply the manifests

Replace the image placeholder in `k8s/03-deployment.yaml` with the ECR repository URL and commit SHA tag. Update `APP_VERSION` in the ConfigMap to match the release.

```sh
kubectl apply -f k8s/
```

The cluster needs Traefik in the `traefik` namespace and a CNI that enforces NetworkPolicy. Cluster nodes must be able to pull from the private ECR repository. DNS pods must run in `kube-system`. Point `hello-api.example.com` at the ingress address for testing, or replace it with your hostname.

The policy permits inbound TCP 8000 only from `traefik`, and outbound UDP/TCP 53 only to `kube-system`. All other pod traffic is denied by this policy.

## 5. Terraform

Use Terraform 1.10 or newer and an authenticated AWS operator identity with permission to create the described resources. Apply bootstrap first. It stores state locally and creates the protected state bucket.

```sh
terraform -chdir=terraform/bootstrap init
terraform -chdir=terraform/bootstrap plan -var='region=<REGION>' -var='bucket_name=<STATE_BUCKET_NAME>'
terraform -chdir=terraform/bootstrap apply -var='region=<REGION>' -var='bucket_name=<STATE_BUCKET_NAME>'
terraform -chdir=terraform/bootstrap output -raw bucket_name
```

Replace the placeholders in `terraform/backend.tf`. Use the bucket output, a state key such as `hh-hello-api/terraform.tfstate`, and the bucket region. Fill in `terraform/terraform.tfvars.example` with the region, GitHub owner, and repository name. Then run:

```sh
terraform -chdir=terraform init
terraform -chdir=terraform plan -var-file=terraform.tfvars.example
terraform -chdir=terraform apply -var-file=terraform.tfvars.example
terraform -chdir=terraform output -raw ecr_repository_url
terraform -chdir=terraform output -raw ci_role_arn
```

Review each plan before applying. Keep the bootstrap state safe. Do not commit state files, `.terraform/`, local variable values, or credentials. No cloud resources are required to run the local checks:

```sh
terraform fmt -check -recursive terraform
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
actionlint
trivy image hello-api
```

The CI-equivalent vulnerability gate is:

```sh
trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 hello-api
```

## 6. Secrets

No real secrets belong in git. CI uses OIDC, so no AWS keys are stored. The Kubernetes Secret contains only the placeholder `REPLACE_ME`. Production would use External Secrets Operator with AWS Secrets Manager.

## 7. Migration question

1. Add an `import` block for the existing resource.
2. Write the resource code to match the live settings.
3. Run `terraform plan` until it shows `1 to import, 0 to change, 0 to destroy`.
4. Never accept a plan that replaces the resource.
5. Apply that import-only plan. Import changes only the state file, so the live resource is not touched and there is no downtime.

## 8. Assumptions and shortcuts

- One `/health` endpoint serves both probes.
- Actions are pinned to version tags, not commit SHAs.
- There is one environment only.
- Manifests use plain YAML, not Helm or Kustomize.
- The app does not read the Secret; it shows the wiring only.
- Pip is removed after installing dependencies; the runtime does not need a package installer.
- The service name is `hh-hello-api`. The image, ECR repository, and namespace use the requested name `hello-api`.
- The account has no existing GitHub OIDC provider. Import an existing provider instead of trying to create a duplicate.
- The GitHub OIDC subject must be `repo:<GITHUB_OWNER>/<REPO_NAME>:ref:refs/heads/main`. Repositories using immutable-ID subjects need their subject configuration aligned before CI can assume this role; see [GitHub's OIDC guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
- Terraform provider lock files are omitted to keep the requested file list. Initialization generates them locally.
- Ingress uses HTTP for this demo. TLS and live cluster verification are outside this example.
