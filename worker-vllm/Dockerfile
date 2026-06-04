FROM nvidia/cuda:13.0.2-devel-ubuntu22.04

RUN apt-get update -y \
    && apt-get install -y python3-pip curl git \
    && curl -LsSf https://astral.sh/uv/install.sh  | sh

ENV PATH="/root/.local/bin:$PATH"

RUN ldconfig /usr/local/cuda-13.0/compat/

COPY vllm_config.yaml /vllm_config.yaml

ENV VLLM_CONFIG_FILE=/vllm_config.yaml

# Install vLLM with FlashInfer - use CUDA 130 PyTorch wheels
RUN uv pip install --system "packaging>=24.2" && \
    uv pip install --system "vllm[flashinfer]==0.20.2" && \
    uv pip install --system git+https://github.com/deepseek-ai/DeepGEMM.git@714dd1a4a980f7937a74343d19a8eba4fe321480 --no-build-isolation

# Install additional Python dependencies (after vLLM to avoid PyTorch version conflicts)
COPY builder/requirements.txt /requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r /requirements.txt

# Setup for Option 2: Building the Image with the Model included
ARG BASE_PATH="/runpod-volume"
ARG VLLM_NIGHTLY="false"

# Dossier racine utilisé par Hugging Face pour ses caches.
# Ici, on le met sur le Network Volume RunPod pour persister entre les redémarrages.
ENV HF_HOME="/runpod-volume/huggingface-cache"

# Cache des modèles, tokenizers et fichiers téléchargés depuis Hugging Face Hub.
# Utile si le worker doit télécharger ou réutiliser des artifacts HF.
ENV HUGGINGFACE_HUB_CACHE="/runpod-volume/huggingface-cache/hub"

# Cache des datasets Hugging Face.
# Pas indispensable pour de l’inférence pure, mais safe si certains scripts utilisent datasets.
ENV HF_DATASETS_CACHE="/runpod-volume/huggingface-cache/datasets"

# Active/désactive hf_transfer pour accélérer les téléchargements Hugging Face.
# 0 = désactivé. Mets 1 seulement si hf_transfer est installé dans l’image.
ENV HF_HUB_ENABLE_HF_TRANSFER=0

# Désactive le parallélisme automatique des tokenizers Rust.
# Évite des warnings ou problèmes de threads dans les containers serverless.
ENV TOKENIZERS_PARALLELISM=false

# Désactive la télémétrie/statistiques d’usage Ray.
# Utile pour éviter des logs inutiles.
ENV RAY_DISABLE_USAGE_STATS=1

# Désactive l’export des métriques Ray.
# Évite des warnings liés à l’agent metrics dans un environnement containerisé.
ENV RAY_METRICS_EXPORT_ENABLED=0

# Limite le nombre de threads Rayon utilisés par certaines libs Rust, notamment tokenizers.
# Utile si le container a une limite de threads/process.
ENV RAYON_NUM_THREADS=4

# Désactive DeepGEMM par défaut.
# DeepGEMM est surtout utile pour certains modèles DeepSeek/MoE ; pas nécessaire pour Qwen dense.
ENV VLLM_USE_DEEP_GEMM=0

# Indique au worker vLLM où trouver le fichier de configuration vLLM.
# Ce fichier contient model, quantization, max-model-len, max-num-seqs, etc.
ENV VLLM_CONFIG_FILE=/vllm_config.yaml

ENV PYTHONPATH="/:/vllm-workspace"

RUN if [ "${VLLM_NIGHTLY}" = "true" ]; then \
    uv pip install --system -U vllm --pre --index-url https://pypi.org/simple --extra-index-url https://wheels.vllm.ai/nightly && \
    apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/* && \
    uv pip install --system git+https://github.com/huggingface/transformers.git; \
fi

COPY src /src
RUN chmod +x /src/start.sh
# RUN --mount=type=secret,id=HF_TOKEN,required=false \
#     if [ -f /run/secrets/HF_TOKEN ]; then \
#     export HF_TOKEN=$(cat /run/secrets/HF_TOKEN); \
#     fi && \
#     if [ -n "$MODEL_NAME" ]; then \
#     python3 /src/download_model.py; \
#     fi

#CMD ["vllm", "serve", "--config", "/vllm_config.yaml"]
# Start the handler
CMD ["/bin/bash", "/src/start.sh"]
