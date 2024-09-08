import importlib
import json

class TemplateError(Exception):
    pass

class FatalError(Exception):
    pass

class ConfigLoader:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def get_db_config(self):
        return self.config.get("database", {})

    def get_document_types(self):
        return self.config.get("document_types", {})

    def get_logging_config(self):
        return self.config.get("logging", {})


def get_class(class_name: str):
    # Split the string "module_name.class_name"
    module_name, class_name = class_name.rsplit(".", 1)

    # Dynamically import the module
    module = importlib.import_module(module_name)

    # Get the class from the module
    handler_class = getattr(module, class_name)

    return handler_class


