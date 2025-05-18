from django import forms
import json

class SimpleJSONTextarea(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = "[]" 
        elif isinstance(value, (list, dict)):
            value = json.dumps(value, indent=2, ensure_ascii=False)
        elif isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                value = json.dumps(parsed_value, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass 

        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        raw_value = data.get(name)
        if raw_value:
            try:
                parsed_json = json.loads(raw_value)
                if not isinstance(parsed_json, list):
                    return [parsed_json] if parsed_json else []
                return parsed_json
            except json.JSONDecodeError:
                return [] 
        return [] 