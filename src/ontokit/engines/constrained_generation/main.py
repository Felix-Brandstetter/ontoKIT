from linkml_runtime import SchemaView
from guidance import models, gen, select, system, one_or_more, zero_or_more, instruction
import logging
import json
from linkml_runtime.linkml_model.meta import SlotDefinition
from jinja2 import Template

logger = logging.getLogger(__name__)


class ConstrainedGeneration:
    def __init__(self, model: models.Model, path_to_linkml_schema: str, text: str):
        self.model = model
        self.text = text
        try:
            self._ontology_schema = SchemaView(path_to_linkml_schema)
            self.tree_root_class = self._get_tree_root_class()
        except FileNotFoundError as e:
            logger.error("Could not find schema at %s: %s", path_to_linkml_schema, e)
            raise e
        except Exception as e:
            logger.error("Could not load schema at %s: %s", path_to_linkml_schema, e)
            raise e

    def _get_tree_root_class(self):
        """
        Returns the root class of the ontology schema.

        :return: The name of the root class.
        :rtype: str
        """
        for class_name, class_def in self._ontology_schema.all_classes().items():
            if class_def.tree_root:
                logger.info("Found root class in LinkML schema: %s", class_name)
                return class_name
        logger.error("No root class found in LinkML schema")
        raise Exception("No root class found in LinkML schema")

    def extract_ontology(self) -> str:
        # Extrahieren der Slots der Root-Klasse (ohne Klassenname)
        json_schema = json.dumps(
            self._extract_slots_from_class(self.tree_root_class), indent=1
        )
        return json_schema

    def _extract_slots_from_class(self, class_name: str):
        extracted_ontology = {}

        # Iteration durch alle Slots der Klasse
        for slot in self._ontology_schema.class_induced_slots(class_name):
            # Prüfen, ob der Bereich des Slots eine Klasse ist
            if slot.range in self._ontology_schema.all_classes():
                # Rekursive Extraktion für Unterklassen
                extracted_ontology[slot.name] = self._extract_slots_from_class(
                    slot.range
                )
            else:
                # Einfache Zuweisung, wenn es kein Unterklassenbereich ist
                extracted_ontology[slot.name] = self._generate_value(
                    slot, extracted_ontology
                )

        return (
            extracted_ontology  # Hier wird das reine Wörterbuch der Slots zurückgegeben
        )

    def _generate_value(self, slot: SlotDefinition, extracted_ontology: dict):
        regex_pattern = self._get_regex_pattern(slot)
        prompt = self._get_prompt(slot, extracted_ontology)

        if slot.multivalued:
            return self._generate_array(slot, extracted_ontology)
        elif slot.range in self._ontology_schema.all_enums():
            return self._generate_value_based_on_enum(slot, prompt)
        elif regex_pattern:
            return self._generate_value_based_on_regex(slot, prompt, regex_pattern)
        else:
            logger.warning("No regex pattern found for slot %s", slot.name)
            return self._generate_string(slot, prompt)

    def _get_regex_pattern(self, slot: SlotDefinition):
        # Slot regex pattern is preferred over type regex pattern
        if slot.pattern:
            return slot.pattern
        elif slot.range in self._ontology_schema.all_types():
            return self._ontology_schema.get_type(slot.range).pattern
        else:
            return None

    def _generate_array(self, slot: SlotDefinition, extracted_ontology: dict):
        # TODO Do not change the slot, but create a flag to say that the slot is being processed.
        slot.multivalued = False
        return [self._generate_value(slot,extracted_ontology)]

    def _generate_value_based_on_regex(
        self, slot: SlotDefinition, prompt: str, regex_pattern: str
    ):
        temp_llm = self.model
        temp_llm = temp_llm + prompt + gen(name=slot.name, regex=regex_pattern)
        value = temp_llm[slot.name]
        return value

    def _generate_string(self, slot: SlotDefinition, prompt: str):
        temp_llm = self.model
        temp_llm = temp_llm + prompt + gen(name=slot.name)
        value = temp_llm[slot.name]
        return value

    def _generate_value_based_on_enum(self, slot: SlotDefinition, prompt: str):
        enum_def = self._ontology_schema.get_enum(slot.range)
        permissible_values = [
                    str(k) for k in enum_def.permissible_values.keys()
                ]
        temp_llm = self.model
        temp_llm = temp_llm + prompt + select(name=slot.name, options=permissible_values)
        value = temp_llm[slot.name]
        return value

    def _get_prompt(self, slot: SlotDefinition, extracted_ontology: dict):
        slot_description = slot.description
        with open(
            "src/ontokit/engines/constrained_generation/prompt_templates/extract_value_from_text.jinja2",
            encoding="utf-8",
        ) as file:
            template_txt = file.read()
            template = Template(template_txt)
        prompt = template.render(
            text=self.text,
            extracted_ontology=json.dumps(extracted_ontology, indent=1),
            slot_name=slot.name,
            slot_description=slot_description,
        )
        return prompt
