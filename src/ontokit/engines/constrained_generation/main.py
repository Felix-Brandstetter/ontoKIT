from linkml_runtime import SchemaView
from guidance import models, gen, select, system, one_or_more, zero_or_more, instruction
import logging
import json
from linkml_runtime.linkml_model.meta import SlotDefinition

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
        json_schema = json.dumps(self._extract_slots_from_class(self.tree_root_class), indent=1)
        return json_schema

    def _extract_slots_from_class(self, class_name: str):
        class_structure = {}

        # Iteration durch alle Slots der Klasse
        for slot in self._ontology_schema.class_induced_slots(class_name):
            # Prüfen, ob der Bereich des Slots eine Klasse ist
            if slot.range in self._ontology_schema.all_classes():
                # Rekursive Extraktion für Unterklassen
                class_structure[slot.name] = self._extract_slots_from_class(slot.range)
            else:
                # Einfache Zuweisung, wenn es kein Unterklassenbereich ist
                class_structure[slot.name] = self._generate_value(slot)

        return class_structure  # Hier wird das reine Wörterbuch der Slots zurückgegeben

    def _generate_value(self, slot: SlotDefinition):
        slot_type = slot.range
        generator = None

        if slot_type in ["integer", "float", "double"]:
            return self._generate_number(slot)
        elif slot_type == "boolean":
            return self._generate_boolean(slot)
        elif slot_type == "datetime":
            return self._generate_datetime(slot)
        elif slot_type in self.ontology_schema.all_enums():
            return self._generate_enum(slot)
        else:
            return self._generate_string(slot)
