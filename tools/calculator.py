def calculator(expression: str) -> str:
    print(f"input expression: {expression}")
    try:
        result = eval(expression)  # Fine for learning; sanitize in prod
        return str(result)
    except Exception as e:
        return f"Error: {e}"
