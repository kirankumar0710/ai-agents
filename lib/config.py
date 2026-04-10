import os
import json
import re


class Config:
    def __init__(self, path: str):
        try:
            with open(path) as f:
                raw = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {path}")
        except PermissionError:
            raise PermissionError(f"Cannot read config file: {path}")

        # ── resolve ${VAR} placeholders ───────────────────────────────────
        missing = []

        def replace_env(match):
            var = match.group(1)
            value = os.getenv(var)
            if value is None:
                missing.append(var)
                return ""  # keep parsing so we can report ALL missing
            return value

        resolved = re.sub(r"\$\{(\w+)\}", replace_env, raw)

        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        # ── parse ─────────────────────────────────────────────────────────
        try:
            self._data = json.loads(resolved)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file '{path}': {e}")

    # ── accessors ─────────────────────────────────────────────────────────

    def get(self, key: str, default=None):
        """Dot-separated key lookup; returns default if any segment missing."""
        value = self._data
        for k in key.split("."):
            if not isinstance(value, dict):
                return default
            value = value.get(k)
            if value is None:
                return default
        return value

    def require(self, key: str):
        """Like get(), but raises ValueError when the key is absent."""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required config key missing: '{key}'")
        return value


def load_config() -> Config:
    config_file = os.environ.get("CONFIG_FILE")
    if not config_file:
        raise ValueError("Environment variable CONFIG_FILE is not set")

    # Expand $HOME, ~, etc. — mirrors shell behaviour
    config_file = os.path.expandvars(os.path.expanduser(config_file))
    return Config(config_file)
