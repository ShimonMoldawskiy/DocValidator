from enum import Enum
import logging
from pathlib import Path
from typing import Tuple, List

from common import TemplateError, FatalError
from db import db_handlers
from templates import factory
from validation.validation_rules import Discrepancy, FieldContext


class ValidationStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    ERROR = "ERROR"
    NOT_PROCESSED = "NOT_PROCESSED"


class DocumentValidator:
    def __init__(self, file_path: Path, doc_template: factory.Template, db_handler: db_handlers.AbstractDatabaseHandler):
        self._file_path: Path = file_path
        self._db_handler: db_handlers.AbstractDatabaseHandler = db_handler
        self._doc_template: factory.Template = doc_template
        self._field_values = {}

    def process(self):
        try:
            if self._doc_template is None:
                self._save_to_db(ValidationStatus.ERROR, [])
                logging.info(f"End processing {self._file_path.name}, Status: {ValidationStatus.ERROR}, Template not found")
            else:
                self._field_values = self._doc_template.extract_field_values(self._file_path)
                status, result = self.validate()
                self._save_to_db(status, result["discrepancies"])
                logging.info(f"End processing {self._file_path.name}, Status: {status.value}")
        except (TemplateError, FatalError):
            raise
        except Exception as e:
            logging.error(f"Error processing {self._file_path}: {e}")

    def validate(self) -> Tuple[ValidationStatus, dict]:
        discrepancies = []
        status = ValidationStatus.NOT_PROCESSED

        for field_name, rules in self._doc_template.field_validation_rules.items():
            value = self._field_values.get(field_name, None)
            field_context = FieldContext(field_name, value)

            for rule in rules:
                valid = False
                discrepancy = Discrepancy(f"{rule.__name__} error", field_context.field_name)
                try:
                    valid, discrepancy = rule(field_context)
                except TemplateError:
                    raise
                except Exception as e:
                    status = ValidationStatus.ERROR
                    discrepancy.message = str(e)

                if not valid:
                    logging.warning(f"Discrepancy: {discrepancy.__dict__}")
                    discrepancies.append(discrepancy.__dict__) # append discrepancy object as a dictionary
                    if status == ValidationStatus.NOT_PROCESSED:
                        status = ValidationStatus.INVALID

        for rule in self._doc_template.doc_validation_rules:
            valid = False
            discrepancy = Discrepancy(f"{rule.__name__} error")
            try:
                valid, discrepancy = rule(self._field_values)
            except TemplateError:
                raise
            except Exception as e:
                status = ValidationStatus.ERROR
                discrepancy.message = str(e)
            if not valid:
                logging.warning(f"Discrepancy: {discrepancy}")
                discrepancies.append(discrepancy.__dict__) # append discrepancy object as a dictionary
                if status == ValidationStatus.NOT_PROCESSED:
                    status = ValidationStatus.INVALID

        if status == ValidationStatus.NOT_PROCESSED:
            status = ValidationStatus.VALID

        return status, {"discrepancies": discrepancies}


    def _save_to_db(self, status: ValidationStatus, discrepancies: List[dict]):
        if self._doc_template is None:
            self._db_handler.insert_document({"name": self._file_path.name, "status": status})
            return

        doc_field_values_to_be_saved = \
            {k: v for k, v in self._field_values.items() if k in self._doc_template.fields_to_save_to_db()}
        document_id = self._db_handler.insert_document({
            "name": self._file_path.name,
            "template": self._doc_template.name,
            **doc_field_values_to_be_saved, "status": str(status)})
        if discrepancies:
            for discrepancy in discrepancies:
                self._db_handler.insert_discrepancy({"document_id": document_id, **discrepancy})

