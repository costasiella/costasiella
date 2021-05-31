def model_string(model_object):
    field_values = [type(model_object).__name__, "--------"]
    for field in model_object._meta.get_fields():
        field_values.append(": ".join([field.name, str(getattr(model_object, field.name, ''))]))
        # field_values.append(str(getattr(self, field.name, '')))
    field_values.append("--------")
    return '\n'.join(field_values)