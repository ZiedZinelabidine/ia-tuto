import os
import sys
import signal
import subprocess


MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3-30B-A3B-GPTQ-Int4")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")
MAX_MODEL_LEN = os.getenv("MAX_MODEL_LEN", "16384")
GPU_MEMORY_UTILIZATION = os.getenv("GPU_MEMORY_UTILIZATION", "0.90")
QUANTIZATION = os.getenv("QUANTIZATION", "gptq")


def check_vllm_installed():
    try:
        import vllm  # noqa: F401
        print("vLLM library detected.")
    except ImportError:
        print("vLLM is not installed.")
        print("Install it with: pip install -U vllm")
        sys.exit(1)


def main():
    check_vllm_installed()

    command = [
        sys.executable,
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        MODEL_NAME,
        "--host",
        HOST,
        "--port",
        PORT,
        "--max-model-len",
        MAX_MODEL_LEN,
        "--gpu-memory-utilization",
        GPU_MEMORY_UTILIZATION,
        "--trust-remote-code",
        "--quantization",
        QUANTIZATION,
    ]

    print("Starting vLLM OpenAI-compatible server...")
    print("Model:", MODEL_NAME)
    print("Port:", PORT)
    print("Command:", " ".join(command))

    process = subprocess.Popen(command)

    def stop_server(signum, frame):
        print("Stopping vLLM...")
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)

    process.wait()


if __name__ == "__main__":
    main()