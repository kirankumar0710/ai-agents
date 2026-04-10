def load_api_key(filepath="api_key.txt"):
    try:
        with open(filepath, "r") as f:
            key = f.read().strip()

        if not key:
            raise ValueError(f"API key file '{filepath}' is empty.")

        return key

    except FileNotFoundError:
        raise FileNotFoundError(f"API key file '{filepath}' not found.")

    except PermissionError:
        raise PermissionError(f"No permission to read '{filepath}'.")
