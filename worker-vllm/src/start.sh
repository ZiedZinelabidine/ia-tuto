#!/bin/bash
set -e

if [ -n "${TRANSFORMERS_VERSION}" ]; then
    echo "Installing transformers==${TRANSFORMERS_VERSION}"
    uv pip install --system "transformers==${TRANSFORMERS_VERSION}"
fi

# echo "=== CHECK RUNPOD VOLUME ==="
# ls -lah /runpod-volume || true
# ls -lah /runpod-volume/models || true
# ls -lah /runpod-volume/models/qwen2.5-coder-14b-instruct-awq || true

# echo "=== CHECK MODEL FILES ==="
# find /runpod-volume/models -maxdepth 3 -type f | head -50 || true

# echo "=== CHECK CONFIG ==="
# cat /vllm_config.yaml || true

exec python3 /src/handler.py
