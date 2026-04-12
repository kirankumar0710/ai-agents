from langchain_core.tools import tool


def write_file(filename: str, content: str) -> str:
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filename}"
    except PermissionError:
        return f"Error: No permission to write to '{filename}'"
    except IsADirectoryError:
        return f"Error: '{filename}' is a directory, not a file"
    except Exception as e:
        return f"Error writing file: {e}"


def read_file(filename: str) -> str:
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found"
    except PermissionError:
        return f"Error: No permission to read '{filename}'"
    except Exception as e:
        return f"Error reading file: {e}"


def append_file(filename: str, content: str) -> str:
    try:
        with open(filename, "a") as f:
            f.write(content)
        return f"Successfully appended {len(content)} characters to {filename}"
    except PermissionError:
        return f"Error: No permission to write to '{filename}'"
    except Exception as e:
        return f"Error appending file: {e}"


@tool
def write_file_tool(filename: str, content: str) -> str:
    """Write content to a file."""
    return write_file(filename, content)
