from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

# Mets ici le chemin réel de ton modèle déjà téléchargé
model_dir = "../sft/pretrained_models/Qwen/Qwen2.5-Coder-1.5B"

tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto").eval()

# Now you do not need to add "trust_remote_code=True"
# tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-32B")
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-Coder-32B", device_map="auto").eval()


# tokenize the input into tokens
#input_text = "#write a quick sort algorithm"
input_text = "Écris un Service Kubernetes ClusterIP pour nginx sur le port 80."

model_inputs = tokenizer([input_text], return_tensors="pt").to(device)

# Use `max_new_tokens` to control the maximum output length.
# generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=1024, do_sample=False)[0]
# The generated_ids include prompt_ids, so we only need to decode the tokens after prompt_ids.
# generated_ids = model.generate(
#     input_ids=model_inputs["input_ids"],
#     attention_mask=model_inputs["attention_mask"],
#     max_new_tokens=512,
#     do_sample=False,
#     pad_token_id=tokenizer.eos_token_id
# )[0]

# output_text = tokenizer.decode(generated_ids[len(model_inputs.input_ids[0]):], skip_special_tokens=True)

# print(f"Prompt: {input_text}\n\nGenerated text: {output_text}")
print(f"Prompt: {input_text}\n\Tokenizer text: {model_inputs}")