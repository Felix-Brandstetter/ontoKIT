verschiedene Strategien implementeiren um Ontologien abzufragen
In Engine

get_client
engine mit client aufrufen -> 3 Engines Complete prompt, rekursiv, misch



lint schema um check zu machen

Install torch with cuda (Abhängig vom Betriebssystem)

add accelerate and bitsandbytes to optional dependency

#Windows
pip uninstall bitsandbytes
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.0-py3-none-win_amd64.whl



- Grammar with llama.cpp -> Grammar File script um Json Schmema zu grammer umzuformen: https://github.com/ggerganov/llama.cpp/pull/1887
- KOR -> Object (Json, Pydantic) > prompt and hope for the best approach
- JSON Former works not with all models

- LM-Format-Enforcer JSON Schema or Pure Json !!!testen klingt vielversprechend nutz aber pydantic

- Guidance -> einfach umzusetzen mit transformers -> wie dynamisch nutzen
- Outlines

- LMQL


Fragen. Wie aus linkml jsonschema erstellen bzw refs auflösen jsonref.loads(Car.schema_json())
idee json generieren und daraus jsonschem machen (genson)


nur für default datentypen nutzen -> in rekursiver methode nutzen


Absatz über LLM constrain schreiben


guidance: select für enums
int, etc für number
boolean als select
string regex

Abhängigkeit von torch lässt sich lösen


Eventuel so:
personal_info: Array<{ // Personal information about a given person.
 first_name: string // The first name of the person
 last_name: string // The last name of the person
 age: number // The age of the person in years.




 types definieren und sagen wie man eigene anlegt

