import math
import statistics

class Calculator:
    def __init__(self):
        self.history = []

    def add_to_history(self, expression, result):
        self.history.append(f"{expression} = {result}")

    def clear_history(self):
        self.history = []

    def display_history(self):
        if not self.history:
            print("No history available.")
        else:
            print("Calculation History:")
            for item in self.history:
                print(item)

    def calculate(self, expression):
        try:
            expression = expression.lower().replace(" ", "")  # Normalize input
            if expression.startswith("sin"):
                angle = float(expression[3:])
                result = math.sin(math.radians(angle))
            elif expression.startswith("cos"):
                angle = float(expression[3:])
                result = math.cos(math.radians(angle))
            elif expression.startswith("tan"):
                angle = float(expression[3:])
                result = math.tan(math.radians(angle))
            elif expression.startswith("log"):
                num = float(expression[3:])
                result = math.log10(num)
            elif expression.startswith("ln"):
                num = float(expression[2:])
                result = math.log(num)
            elif expression.startswith("sqrt"):
                num = float(expression[4:])
                result = math.sqrt(num)
            elif expression.startswith("mean"):
                nums_str = expression[4:].split(",")
                nums = [float(num) for num in nums_str]
                result = statistics.mean(nums)
            elif expression.startswith("median"):
                nums_str = expression[6:].split(",")
                nums = [float(num) for num in nums_str]
                result = statistics.median(nums)
            elif "to" in expression: # unit conversion
                parts = expression.split("to")
                value = float(parts[0])
                unit1 = parts[0].replace(str(value),"")
                unit2 = parts[1]
                if unit1 == "c" and unit2 == "f": #Celsius to fahrenheit
                    result = (value * 9/5) + 32
                elif unit1 == "f" and unit2 == "c": #Fahrenheit to celsius
                    result = (value - 32) * 5/9
                else:
                    raise ValueError("Unsupported unit conversion")
            else:
                result = eval(expression) # Basic arithmetic
            self.add_to_history(expression, result)
            return result

        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
            return f"Invalid input: {e}"

calculator = Calculator()

while True:
    print("\nScientific Calculator")
    print("Available operations: sin, cos, tan, log, ln, sqrt, mean(num1,num2,...), median(num1,num2,...), unit conversions(e.g 25ctof), basic arithmetic (+, -, *, /)")
    print("Enter 'history' to view calculation history, 'clear' to clear history, or 'exit' to quit.")

    expression = input("Enter your calculation: ")

    if expression.lower() == "exit":
        break
    elif expression.lower() == "history":
        calculator.display_history()
        continue
    elif expression.lower() == "clear":
      calculator.clear_history()
      print("History cleared.")
      continue

    result = calculator.calculate(expression)
    print("Result:", result)
