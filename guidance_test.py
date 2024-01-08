import guidance
from guidance import models, gen, select, system, one_or_more, zero_or_more, instruction
import torch



model = models.Transformers("mistralai/Mistral-7B-Instruct-v0.2", device_map="auto", load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

prompt = "Generate a number with 5 digits."
regex = "[0-2]?[0-9]:[0-5][0-9]:[0-5][0-9]"

temp_llm = model

temp_llm = temp_llm + prompt + gen(name="value", regex="-?[0-9]+")

print(temp_llm["value"])
