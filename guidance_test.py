import guidance
from guidance import models, gen, select, system, one_or_more, zero_or_more, instruction
import torch



model = models.Transformers("mistralai/Mistral-7B-Instruct-v0.2", device_map="auto", load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

ontology = f'''\
Im feeling very sad.

Is the above text a negative text? {gen(regex="[0-2]?[0-9]:[0-5][0-9]:[0-5][0-9]")}
'''

model = model + ontology
print(model)
