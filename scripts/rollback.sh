#!/usr/bin/env bash
# Usage: rollback.sh <environment> <compose_file> <previous_tag>
set -euo pipefail
ENVIRONMENT_NAME="${1:?environment}"
COMPOSE_FILE="${2:?compose file}"
PREVIOUS_TAG="${3:-}"

if [ -z "${PREVIOUS_TAG}" ]; then
  echo "No previous tag recorded for ${ENVIRONMENT_NAME}; cannot roll back"
  exit 1
fi

echo "Rolling back ${ENVIRONMENT_NAME} to image tag ${PREVIOUS_TAG}"
IMAGE_TAG="${PREVIOUS_TAG}" docker compose -p "shd-${ENVIRONMENT_NAME}" -f "${COMPOSE_FILE}" up -d
echo "Running image now:"
docker inspect --format '{{.Config.Image}}' "app-${ENVIRONMENT_NAME}"
