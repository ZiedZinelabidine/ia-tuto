#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/workspace/agent-zz/vllm"
PY_SCRIPT="inference-model-withouthttp.py"
VENV_DIR="/workspace/vllm-env"

# Version stable à tester pour éviter le wheel PyPI CUDA 13
VLLM_VERSION="${VLLM_VERSION:-0.20.0}"
CUDA_BACKEND="${CUDA_BACKEND:-cu129}"

echo "=== RunPod vLLM clean install ==="
echo "Project: ${PROJECT_DIR}"
echo "Script:  ${PY_SCRIPT}"
echo "vLLM:    ${VLLM_VERSION}"
echo "CUDA:    ${CUDA_BACKEND}"

cd "${PROJECT_DIR}"

echo
echo "=== GPU info ==="
nvidia-smi || true

echo
echo "=== Remove old venv ==="
deactivate 2>/dev/null || true
rm -rf "${VENV_DIR}"

echo
echo "=== Install Python venv deps ==="
apt update
apt install -y python3.12-venv python3-full curl

echo
echo "=== Create clean venv ==="
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

unset PYTHONPATH || true
export PYTHONNOUSERSITE=1
export UV_TORCH_BACKEND="${CUDA_BACKEND}"

python -m pip install -U pip setuptools wheel uv

echo
echo "=== Install vLLM ${VLLM_VERSION} with ${CUDA_BACKEND} ==="

uv pip install --no-cache \
  "vllm==${VLLM_VERSION}" \
  --torch-backend="${CUDA_BACKEND}" \
  --extra-index-url "https://wheels.vllm.ai/${VLLM_VERSION}/${CUDA_BACKEND}" \
  --extra-index-url "https://download.pytorch.org/whl/${CUDA_BACKEND}" \
  --index-strategy unsafe-best-match

echo
echo "=== Version check ==="
python - <<'PY'
import torch
import importlib.metadata as md

print("torch:", torch.__version__)
print("torch cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
print("vllm:", md.version("vllm"))
PY

echo
echo "=== vLLM import check ==="
python - <<'PY'
from vllm import LLM, SamplingParams
print("vLLM import OK")
PY

echo
echo "=== CUDA linkage check ==="
VLLM_SO="$(find "${VENV_DIR}/lib/python3.12/site-packages/vllm" -name '_C*.so' -print -quit || true)"

if [ -n "${VLLM_SO}" ]; then
  echo "vLLM extension: ${VLLM_SO}"
  ldd "${VLLM_SO}" | grep -E 'cudart|cuda' || true

  if ldd "${VLLM_SO}" | grep -q 'libcudart.so.13'; then
    echo
    echo "ERROR: mauvais wheel vLLM détecté: libcudart.so.13"
    echo "Le pod charge encore une build CUDA 13."
    echo "Essaie:"
    echo "  VLLM_VERSION=0.19.0 bash /workspace/install-and-run-vllm.sh"
    exit 13
  fi
fi

echo
echo "=== Run your script ==="
python "${PROJECT_DIR}/${PY_SCRIPT}"
