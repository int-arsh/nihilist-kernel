#!/usr/bin/env bash
set -euo pipefail

# --- config ---
NS="${NS:-nihikernel-dev}"
DOCKER_USER="${DOCKER_USER:-akashdocker303}"
SHA="${SHA:-$(git rev-parse --short=12 HEAD)}"
MINIKUBE_IP="${MINIKUBE_IP:-$(minikube ip)}"

BACKEND_IMAGE="docker.io/${DOCKER_USER}/nihikernel-backend:devo-${SHA}"
FRONTEND_IMAGE="docker.io/${DOCKER_USER}/nihikernel-frontend:devo-${SHA}"
FRONTEND_API_URL="http://${MINIKUBE_IP}:30050"

echo "Namespace      : ${NS}"
echo "Tag            : devo-${SHA}"
echo "Backend image  : ${BACKEND_IMAGE}"
echo "Frontend image : ${FRONTEND_IMAGE}"
echo "Frontend API   : ${FRONTEND_API_URL}"

# --- prechecks ---
kubectl get ns "${NS}" >/dev/null 2>&1 || {
  echo "Namespace '${NS}' not found. Create it first."
  exit 1
}

# --- build & push ---
echo ">> Building backend"
docker build -t "${BACKEND_IMAGE}" ./bend
docker push "${BACKEND_IMAGE}"

echo ">> Building frontend"
docker build \
  --build-arg VITE_API_BASE_URL="${FRONTEND_API_URL}" \
  -t "${FRONTEND_IMAGE}" \
  ./fend
docker push "${FRONTEND_IMAGE}"

# --- deploy immutable tags ---
echo ">> Updating deployments"
kubectl -n "${NS}" set image deployment/backend backend="${BACKEND_IMAGE}"
kubectl -n "${NS}" set image deployment/frontend frontend="${FRONTEND_IMAGE}"

echo ">> Waiting for rollout"
kubectl -n "${NS}" rollout status deployment/backend --timeout=180s
kubectl -n "${NS}" rollout status deployment/frontend --timeout=180s

echo ">> Current deployed images"
kubectl -n "${NS}" get deploy -o "custom-columns=NAME:.metadata.name,IMAGE:.spec.template.spec.containers[*].image"

echo "✅ Deploy complete"