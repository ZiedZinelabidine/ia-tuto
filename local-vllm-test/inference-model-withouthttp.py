from vllm import LLM, SamplingParams

llm = LLM(
    model="Qwen/Qwen3-30B-A3B-GPTQ-Int4",
    quantization="gptq",
    trust_remote_code=True,
    max_model_len=16384,
    gpu_memory_utilization=0.90,
)

params = SamplingParams(
    temperature=0.4,
    max_tokens=1200,
)

messages = [
    {"role": "system", "content": "Tu es un assistant IA professionnel pour freelances."},
    {"role": "user", "content": "Donne moi les instruction pour installer un model ."}
]

outputs = llm.chat(messages, sampling_params=params)

print(outputs[0].outputs[0].text)