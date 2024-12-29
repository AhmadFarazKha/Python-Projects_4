import json
import os
import shutil
import datetime
import jsonschema  # type: ignore # For schema validation

class ConfigManager:
    def __init__(self, config_file="config.json", schema_file="config_schema.json", backup_dir="config_backups"):
        self.config_file = config_file
        self.schema_file = schema_file
        self.backup_dir = backup_dir
        self.config = {}
        self.load_config()
        self.load_schema()
        self.create_backup_dir()

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Config file not found. Creating a default configuration.")
            self.config = {}  # Create empty config
            self.save_config() # Save the empty config file
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config file: {e}")

    def load_schema(self):
        try:
            with open(self.schema_file, "r") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            print("Schema file not found. Using no validation.")
            self.schema = None
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in schema file: {e}")

    def create_backup_dir(self):
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            self.backup_config() # Create a backup after saving
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {e}")

    def backup_config(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"config_{timestamp}.json")
        try:
            shutil.copy2(self.config_file, backup_file) #copy2 preserves metadata
            print(f"Configuration backed up to: {backup_file}")
        except Exception as e:
            print(f"Failed to backup configuration: {e}")

    def get(self, path, default=None):
        """Retrieves a config value using a dot-separated path."""
        parts = path.split(".")
        value = self.config
        try:
            for part in parts:
                value = value.get(part)
                if value is None:
                    return default  # Fallback to default if path not found
            return value
        except AttributeError:  # Handle cases where value is not a dict
            return default

    def set(self, path, value):
        """Sets a config value using a dot-separated path."""
        if self.schema:
            try:
                jsonschema.validate(instance={path:value}, schema={"type":"object", "properties":{path: self.find_schema_for_path(path)}})
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError(f"Invalid config value for {path}: {e}")
        parts = path.split(".")
        target = self.config
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
        self.save_config()

    def find_schema_for_path(self, path):
        parts = path.split(".")
        schema = self.schema
        for part in parts:
            if schema and "properties" in schema and part in schema["properties"]:
                schema = schema["properties"][part]
            else:
                return {} #Return empty schema if path not found
        return schema
    
    def merge_config(self, env):
        """Merges environment-specific settings into the main config."""
        env_config_path = f"{self.config_file.replace('.json', '')}_{env}.json"
        try:
            with open(env_config_path, "r") as f:
                env_config = json.load(f)
                self.config.update(env_config)
                self.save_config()
                print(f"Merged config for environment: {env}")
        except FileNotFoundError:
            print(f"No config file found for environment: {env}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in environment config file: {e}")

# Example Usage:
config_manager = ConfigManager()

# Example schema
schema = {
    "type": "object",
    "properties": {
        "database": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["host", "port"]
        },
        "api_key": {"type": "string"}
    },
    "required": ["database"]
}
with open("config_schema.json", "w") as f:
    json.dump(schema, f, indent=4)

config_manager.set("database.host", "localhost")
config_manager.set("database.port", 5432)
config_manager.set("api_key", "your_api_key")

print("Database Host:", config_manager.get("database.host"))
print("Non-existent setting:", config_manager.get("non.existent", "default_value"))

# Example environment config
env_config = {"database": {"port": 5433}, "new_env_setting": "test"}
with open("config_dev.json", "w") as f:
    json.dump(env_config, f, indent=4)

config_manager.merge_config("dev")
print("Database Port after merge:", config_manager.get("database.port"))
print("New environment setting:", config_manager.get("new_env_setting"))

try:
    config_manager.set("database.port", "invalid") # Invalid value according to the schema
except ValueError as e:
    print(e)