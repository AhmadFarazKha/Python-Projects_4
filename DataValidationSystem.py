import re
import json
import phonenumbers  # type: ignore # For international phone number validation
from jsonschema import validate, ValidationError # type: ignore # For schema validation

class DataValidator:
    def __init__(self, schema_file="validation_schema.json"):
        self.load_schema(schema_file)
        self.validation_errors = []

    def load_schema(self, schema_file):
        try:
            with open(schema_file, "r") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            print("Validation schema not found. Using default validation.")
            self.schema = {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in schema file: {e}")

    def validate_data(self, data):
        self.validation_errors = []  # Clear previous errors
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            self.validation_errors.append(str(e))
        
        for field, rules in self.schema.get("properties", {}).items():
            value = data.get(field)
            if value is None and rules.get("required", False):
                self.validation_errors.append(f"Field '{field}' is required.")
                continue # Skip further validation for missing field
            if value is not None:
                self.validate_field(field, value, rules)
        return not self.validation_errors

    def validate_field(self, field, value, rules):
        if "type" in rules and not isinstance(value, self.get_python_type(rules["type"])):
            self.validation_errors.append(f"Field '{field}' must be of type {rules['type']}. Got {type(value).__name__}")
        if "format" in rules:
            if rules["format"] == "email":
                if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    self.validation_errors.append(f"Field '{field}' is not a valid email address.")
            elif rules["format"] == "phone":
                try:
                    phone_number = phonenumbers.parse(value)
                    if not phonenumbers.is_valid_number(phone_number):
                        self.validation_errors.append(f"Field '{field}' is not a valid phone number.")
                except phonenumbers.phonenumberutil.NumberParseException:
                    self.validation_errors.append(f"Field '{field}' is not a valid phone number.")
            elif rules["format"] == "address":
                if not isinstance(value, str) or len(value) < 5: # basic check
                    self.validation_errors.append(f"Field '{field}' is not a valid address.")
        if "minimum" in rules and value < rules["minimum"]:
            self.validation_errors.append(f"Field '{field}' must be at least {rules['minimum']}.")
        if "maximum" in rules and value > rules["maximum"]:
            self.validation_errors.append(f"Field '{field}' must be at most {rules['maximum']}.")
        if "pattern" in rules and not re.match(rules["pattern"], value):
            self.validation_errors.append(f"Field '{field}' does not match the required pattern.")
        if "custom" in rules:
            try:
                if not eval(rules["custom"], {}, {"value": value}): # Execute the custom validation rule
                    self.validation_errors.append(f"Field '{field}' failed custom validation.")
            except Exception as e:
                self.validation_errors.append(f"Error in custom validation for '{field}': {e}")

    def get_python_type(self, json_type):
        type_mapping = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
        return type_mapping.get(json_type)

    def get_validation_report(self):
        if self.validation_errors:
            report = "Validation Report:\n"
            for error in self.validation_errors:
                report += f"- {error}\n"
            return report
        else:
            return "Data is valid."

    def clean_data(self, data):
        cleaned_data = {}
        for field, value in data.items():
            if isinstance(value, str):
                cleaned_data[field] = value.strip()
            else:
                cleaned_data[field] = value
        return cleaned_data

# Example Usage
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "required": True, "minLength": 3},
        "email": {"type": "string", "format": "email", "required": True},
        "phone": {"type": "string", "format": "phone"},
        "age": {"type": "integer", "minimum": 0, "maximum": 120},
        "address": {"type": "string", "format": "address"},
        "custom_value": {"type": "integer", "custom": "value % 2 == 0"} # Custom validation rule
    },
    "required": ["name", "email"]
}
with open("validation_schema.json", "w") as f:
    json.dump(schema, f, indent=4)

validator = DataValidator()

valid_data = {"name": "John Doe", "email": "john.doe@example.com", "phone": "+15551234567", "age": 30, "address": "123 Main St", "custom_value": 4}
invalid_data = {"name": "JD", "email": "invalid_email", "age": 150, "custom_value": 3}
missing_data = {"name": "Jane", "phone": "+447911123456", "age": 25, "address": "Some other address"}

print("Valid Data:")
if validator.validate_data(valid_data):
    print("Data is valid")
else:
    print(validator.get_validation_report())
cleaned_valid_data = validator.clean_data(valid_data)
print("Cleaned data:", cleaned_valid_data)

print("\nInvalid Data:")
if validator.validate_data(invalid_data):
    print("Data is valid")
else:
    print(validator.get_validation_report())

print("\nMissing Data:")
if validator.validate_data(missing_data):
    print("Data is valid")
else:
    print(validator.get_validation_report())
