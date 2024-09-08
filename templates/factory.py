from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import List, Union
import re

import common
from common import FatalError


class Template(ABC):
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.field_validation_rules = {}
        self.doc_validation_rules = []

    @abstractmethod
    def extract_field_values(self, file_path: Path) -> dict:
        pass

    @abstractmethod
    def fields_to_save_to_db(self) -> List[str]:
        pass


class TemplateFactory:
    def __init__(self, document_types: List[dict], **kwargs):
        self._document_types: List[dict] = document_types
        self._templates: dict = {}
        self._kwargs: dict = kwargs

    def _get_template_class_name(self, file_path: Path) -> str:
        file_name = file_path.name

        if not self._document_types or not isinstance(self._document_types, dict):
            raise FatalError("Document types not configured properly")

        for _, type_params in self._document_types.items():
            if (not type_params or not isinstance(type_params, dict) or
                    not ("name_mask" in type_params) or (not "template_class" in type_params)):
                raise FatalError("Document type params not configured properly")

            if re.match(type_params["name_mask"], file_name):  # Compare against the regular expression mask
                return type_params["template_class"]

        logging.warning(f"No template found for the document: {file_path}")
        return ""

    def get_template(self, file_path: Path) -> Union[Template, None]:
        template_class_name = self._get_template_class_name(file_path)
        if not template_class_name:
            return None

        if template_class_name in self._templates:
            return self._templates[template_class_name]

        template_class = common.get_class(template_class_name)
        if not template_class:
            logging.error(f"Template class '{template_class_name}' not found.")
            return None

        new_template = template_class(template_class_name, **self._kwargs)
        self._templates[template_class_name] = new_template
        return new_template

