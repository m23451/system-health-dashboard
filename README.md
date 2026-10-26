# System Health Dashboard

A small Flask API that exposes basic status information for engineers and
automated monitoring checks. The project demonstrates a Git-to-deployment
workflow: feature branches, pull requests, automated tests, a Docker image,
and a Jenkins pipeline.

## Endpoints

| Endpoint | Response |
|---|---|
| `/health` | `{"status": "UP"}` |
| `/version` | `{"version": "1.1.0"}` |
| `/environment` | `{"environment": "dev"}` (the value of `APP_ENV`; `unknown` if unset) |

## Prerequisites

- Git
- Python 3.9 or later, with `venv`
- Docker
- Jenkins (only to run the pipeline)

## Run locally

```bash
git clone https://github.com/m23451/system-health-dashboard.git
cd system-health-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_ENV=dev python app.py
```

Verify from a second terminal:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/version
curl http://localhost:5000/environment
```

Expected: `UP`, the version, and `dev`.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `APP_ENV` | Environment name returned by `/environment` | `unknown` |
| `APP_VERSION` | Version returned by `/version` | `1.1.0` |

## Run the tests

```bash
python -m pytest -v
```

## Run in Docker

```bash
docker build -t system-health-dashboard:1.0.0 .
docker run -d --name shd -p 5000:5000 -e APP_ENV=docker system-health-dashboard:1.0.0
curl http://localhost:5000/health
curl http://localhost:5000/version
curl http://localhost:5000/environment    # returns "docker"
docker rm -f shd
```

## Jenkins pipeline

The `Jenkinsfile` defines these stages:

| Stage | Action |
|---|---|
| Checkout | Retrieves the repository and branch |
| Install | Creates a virtual environment and installs dependencies |
| Test | Runs the pytest suite and publishes results; a failure stops the pipeline |
| Build | Builds the Docker image |
| Tag | Tags the image with the Jenkins build number |
| Health check | Runs the container and checks `/health` |

To run it: create a Pipeline job, choose "Pipeline script from SCM", set the
repository URL, branch `*/main`, and Script Path `Jenkinsfile`. The Jenkins
agent needs Git, Python 3 with venv, and access to Docker.

NOTE: I employed the use of AI (Claude) as a guide to plan and complete the project, covering the Git branching workflow, the structure of the Flask application and tests, the Dockerfile and .dockerignore, the Jenkinsfile, setting up Jenkins in Docker, and troubleshooting errors along the way. AI provided example code and step-by-step instructions, which I ran, tested and adapted. I carried out all Git operations, builds and pipeline runs myself, and I understand and can explain every submitted file.
