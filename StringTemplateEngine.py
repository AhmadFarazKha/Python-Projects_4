import re

class TemplateEngine:
    def __init__(self, delimiters=("{", "}")):
        self.open_delim, self.close_delim = delimiters
        self.pattern = re.compile(re.escape(self.open_delim) + r"(.*?)" + re.escape(self.close_delim))

    def render(self, template, context):
        """Renders the template with the given context."""
        try:
            return self._render_recursive(template, context)
        except TemplateError as e:
            return str(e)  # Return error message instead of raising exception

    def _render_recursive(self, template, context):
        """Recursively renders nested templates."""
        def replace(match):
            expression = match.group(1).strip()

            if expression.startswith("if "):
                condition = expression[3:].strip()
                try:
                    if eval(condition, {}, context): # Evaluate condition within the provided context
                        return ""
                    else:
                        return "" # Return empty string if condition is false
                except NameError as e:
                    raise TemplateError(f"NameError: {e}")
                except Exception as e:
                    raise TemplateError(f"Invalid condition: {e}")

            elif expression.startswith("elif "):
                return "" # elif is not supported

            elif expression.startswith("else"):
                return "" # else is not supported

            try:
                value = eval(expression, {}, context)
                if isinstance(value, str):
                    return value
                return str(value)  # Convert other data types to string
            except NameError:
                raise TemplateError(f"Variable '{expression}' not found in context.")
            except (TypeError, SyntaxError, AttributeError) as e:
                raise TemplateError(f"Error evaluating expression '{expression}': {e}")

        rendered = self.pattern.sub(replace, template)
        if self.pattern.search(rendered):  # Check for unresolved variables (nested templates)
            rendered = self._render_recursive(rendered, context)
        return rendered

class TemplateError(Exception):
    """Custom exception for template errors."""
    pass

# Example usage:
template_engine = TemplateEngine()

context = {
    "name": "John Doe",
    "age": 30,
    "city": "New York",
    "items": [{"name": "Laptop", "price": 1200}, {"name": "Mouse", "price": 25}],
    "user": {"address": {"street": "123 Main St"}}
}

template = """
Hello {name}, you are {age} years old and live in {city}.

Items:
{% for item in items %}
- {item['name']}: ${item['price']}
{% endfor %}

Address: {user['address']['street']}

{if age > 25}
You are over 25.
{endif}

{if city == "London"}
You live in London
{endif}
"""

rendered_template = template_engine.render(template, context)
print(rendered_template)

template_error_example = "Hello {nonexistent_variable}"
rendered_error = template_engine.render(template_error_example, context)
print("\nError example:", rendered_error)

template_invalid_expression = "Hello {1/0}"
rendered_invalid = template_engine.render(template_invalid_expression, context)
print("\nInvalid expression example:", rendered_invalid)

template_invalid_condition = "{if age > 'test'}"
rendered_invalid_condition = template_engine.render(template_invalid_condition, context)
print("\nInvalid condition example:", rendered_invalid_condition)

template_nested = "Outer { {inner} } Outer"
context_nested = {"inner": "Inner Value"}
rendered_nested = template_engine.render(template_nested, context_nested)
print("\nNested template example:", rendered_nested)

template_with_format = "Price: {item['price']:.2f}"
context_with_format = {"item": {"price": 12.345}}
rendered_with_format = template_engine.render(template_with_format, context_with_format)
print("\nTemplate with format example:", rendered_with_format)
