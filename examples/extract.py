from guidance import models
import torch
from ontokit.engines.constrained_generation.main import ConstrainedGeneration

with open("data/input/resume.txt", encoding="utf-8") as f:
    text = f.read()

model = models.Transformers(
    "mistralai/Mistral-7B-Instruct-v0.2",
    device_map="auto",
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)

ontokit = ConstrainedGeneration(
    model=model,
    path_to_linkml_schema="data/seed_ontologies/resume.yaml",
    text=text,
)

extracted_ontology = ontokit.extract_ontology()
print(extracted_ontology)