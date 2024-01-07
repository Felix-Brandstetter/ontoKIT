from linkml_runtime import SchemaView

a = SchemaView("data/seed_ontologies/resume copy.yaml")
for slot in a.class_induced_slots("Education"):
    print(slot.pattern)
    print(slot.range)
    if slot.range in a.all_types():
        type = a.get_type(slot.range)
        print(type.pattern)
