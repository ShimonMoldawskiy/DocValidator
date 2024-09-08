from datetime import datetime
import re
from typing import Union

from common import TemplateError

class Discrepancy:
    def __init__(self, discrepancy_type: str = None, location: str = None, message: str = None):
        self.discrepancy_type = discrepancy_type
        self.location = location
        self.message = message

class FieldContext:
    def __init__(self, field_name: str, value: str):
        self.field_name = field_name
        self.value = value
        self.data_type: Union[str, None] = None
        self.typed_value = None  # Will store the value after type conversion

class ValidationRuleBuilder:
    def __init__(self):
        self.rules = []

    def get_validation_rules(self):
        return self.rules

class FieldRuleBuilder(ValidationRuleBuilder):
    def add_type_check(self, expected_type: str):
        def type_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            try:
                field_context.data_type = expected_type
                if expected_type == "int":
                    field_context.typed_value = int(field_context.value)
                elif expected_type.startswith("date"):
                    date_format = expected_type[len("date"):]
                    field_context.typed_value = datetime.strptime(field_context.value, date_format)  # Try to parse the string into a date
                else:
                    field_context.typed_value = field_context.value
            except ValueError:
                return False, Discrepancy("type_check", f"{field_context.field_name}",
                        f"Type mismatch for the value '{field_context.value}'. Expected {expected_type}.")

            return True, None

        self.rules.append(type_check)
        return self

    def add_mandatory_check(self):
        def mandatory_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None or field_context.value == '':
                return False, Discrepancy("mandatory_check", f"{field_context.field_name}",
                                          f"Missing value for the field.")
            return True, None

        self.rules.append(mandatory_check)
        return self

    def add_format_check(self, format_mask: str):
        def format_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            if not re.match(format_mask, field_context.value):
                return False, Discrepancy("format_check", f"{field_context.field_name}",
                        f"Type mismatch for the value '{field_context.value}'. Expected format '{format_mask}'.")
            return True, None

        self.rules.append(format_check)
        return self

    def add_max_length_check(self, max_length: int):
        def max_length_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            if len(field_context.value) > max_length:
                return False, Discrepancy("max_length_check", f"{field_context.field_name}",
                        f"Field value '{field_context.value}' is too long. Maximum length is {max_length}.")
            return True, None

        self.rules.append(max_length_check)
        return self

    def add_min_length_check(self, min_length: int):
        def min_length_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            if len(field_context.value) < min_length:
                return False, Discrepancy("min_length_check", f"{field_context.field_name}",
                        f"Field value '{field_context.value}' is too short. Minimum length is {min_length}.")
            return True, None

        self.rules.append(min_length_check)
        return self

    def add_max_check(self, max_val):
        def max_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            if not field_context.data_type:
                raise TemplateError(
                    f"max_check: cannot compare field value of '{field_context.field_name}' without prior type_check")
            if field_context.typed_value is None:
                return True, None
            if field_context.typed_value > max_val:
                return False, Discrepancy("max_check", f"{field_context.field_name}",
                        f"Field value '{field_context.value}' is more than the maximum value {max_val}.")
            return True, None

        self.rules.append(max_check)
        return self

    def add_min_check(self, min_val):
        def min_check(field_context: FieldContext) -> (bool, Union[Discrepancy, None]):
            if field_context.value is None:
                return True, None
            if not field_context.data_type:
                raise TemplateError(
                    f"min_check: cannot compare field value of '{field_context.field_name}' without prior type_check")
            if field_context.typed_value is None:
                return True, None
            if field_context.typed_value < min_val:
                return False, Discrepancy("min_check", f"{field_context.field_name}",
                        f"Field value '{field_context.value}' is less than the minimum value {min_val}.")
            return True, None

        self.rules.append(min_check)
        return self

class DocRuleBuilder(ValidationRuleBuilder):
    def add_custom_rule(self, rule_code: str, **kwargs):
        def custom_rule_check(field_values: dict) -> (bool, Union[Discrepancy, None]):
            return eval(rule_code, field_values.update(kwargs))

        self.rules.append(custom_rule_check)
        return self

