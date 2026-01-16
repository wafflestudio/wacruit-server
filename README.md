# wacruit-server

[![Python 3.11.1](https://img.shields.io/badge/python-3.11.1-blue.svg)](https://www.python.org/downloads/release/python-3111/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## Prerequisites

- Python version 3.11 and above is required.
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager to install all the dependencies.
- A MySQL client is required for database operations in your local machine. On macos, you can install via `brew install mysql-client` or `brew install mysql`. Don't forget to add it to PATH.
- This project requires [wacruit-judge](https://github.com/wafflestudio/wacruit-judge) which is the fork version of [Judge0](https://github.com/judge0/judge0). To test this project, you first need to clone wacruit-judge and run it using docker-compose.

## Installation

### Dependencies

Run the following command to install all the dependencies:
```bash
uv sync
```
The above command will install all the required dependencies in a virtual environment.

### Pre-commit hooks

This repository uses pre-commit hooks to ensure consistent code quality. To install pre-commit hooks, run the following command:

```bash
pre-commit install
```

## Convention

- [Python Google Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black](https://black.readthedocs.io/en/stable/)
- [Isort](https://pycqa.github.io/isort/)


## Migration

To generate migrations you should run:

```bash
# For automatic change detection.
alembic revision --autogenerate -m "revision summary"

# For empty file generation.
alembic revision
```

If you want to migrate your database, you should run following commands:

```bash
# To perform all pending migrations.
alembic upgrade head

# To run all migrations until the migration with revision_id.
alembic upgrade <revision_id>
```

If you want to revert migrations, you should run:
```bash
# Revert everything.
alembic downgrade base

# revert all migrations up to: revision_id.
alembic downgrade <revision_id>
```

## Testing

### MySQL Test DB

```
docker run --name wacruit-test \
  -e MYSQL_USER=test-user \
  -e MYSQL_PASSWORD=password \
  -e MYSQL_ROOT_PASSWORD=root-password \
  -e MYSQL_DATABASE=testdb \
  -p 3307:3306 \
  -d mysql:5.7  # or mysql:latest
```

## Infra
- CI/CD
  - Define a Dockerfile to run the application(`wacruit-server`) and expose the port(`8080`).
  - Using **Github Actions**, build and push a Docker image of `main` repository to **ECR**.
    - 1) Configure AWS Credentials (aws-access-key-id, aws-secret-access-key, aws-region)
    - 2) Login to ECR (aws-actions/amazon-ecr-login@v1)
    - 3) Build/Tag/Push an image to ECR
- ecr-heimdall ([link](https://github.com/wafflestudio/ecr-heimdall))
  - **ECR** push event triggers **AWS Lambda** function to update manifest files in [waffle-world](https://github.com/wafflestudio/waffle-world).
    > `docker build -t ecr-heimdall . --platform linux/amd64`

    > `docker run --platform linux/amd64 -v ~/.aws/ccredentials:/root/.aws/credentials -it ecr-heimdall`
  - ArgoCD detects the change in the manifest file and deploys the new image in `waffle-cluster`.
- GitOps
  - With **ArgoCD**, `waffle-cluster` lets the new image to be deployed as a **Deployment** API resource.
  - Define a manifest file in [waffle-world/apps/](https://github.com/wafflestudio/waffle-world/tree/main/apps)[projectName] including **Deployment**, **ServiceAccount**, **Service**, **VirtualService**, etc.
  - DevOps tools(ex. Istio, Prometheus, etc.) have been managed by **Helm**([/charts](https://github.com/wafflestudio/waffle-world/tree/main/charts)) and **kubectl** command([/misc](https://github.com/wafflestudio/waffle-world/tree/main/misc)).
