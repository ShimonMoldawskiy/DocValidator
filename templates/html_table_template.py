from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re
from typing import List

from common import TemplateError, FatalError
from templates import factory
from validation.validation_rules import DocRuleBuilder, FieldRuleBuilder

class HTMLTableTemplate(factory.Template):
    def __init__(self, name: str, **kwargs):
        try:
            super().__init__(name, **kwargs)

            if not ("N" in kwargs and "D" in kwargs and "SUM" in kwargs):
                raise FatalError("Missing template parameter(s)")

            self.field_validation_rules = {
                "title":
                    FieldRuleBuilder().add_mandatory_check().add_min_length_check(kwargs["N"]).get_validation_rules(),
                "creation_date":
                    FieldRuleBuilder().add_mandatory_check().add_type_check("date%d%b%Y").add_max_check(kwargs["D"]).get_validation_rules(),
                "first_row_sum":
                    FieldRuleBuilder().add_mandatory_check().add_type_check("int").add_max_check(kwargs["SUM"]).get_validation_rules()
            }

            self.doc_validation_rules = {}
        except Exception as e:
            raise TemplateError from e

    def extract_field_values(self, file_path: Path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title from the <caption> tag
        title = soup.find('caption').get_text(strip=True) if soup.find('caption') else None

        # Extract header from the <thead> tag
        header = [th.get_text(strip=True) for th in soup.find('thead').find_all('th')] if soup.find('thead') else []

        # Extract body from the <tbody> tag (row data)
        body = []
        for row in soup.find('tbody').find_all('tr'):
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            body.append(cells)

        # Extract footer from the <tfoot> tag
        footer = soup.find('tfoot').get_text(strip=True) if soup.find('tfoot') else ""

        # Parse footer to extract creation date and country
        creation_info = re.search(r'Creation: (\d+\w+\d{4}) (.+)$', footer)
        if creation_info:
            creation_date = creation_info.group(1)  # E.g., "10Mar2010"
            creation_country = creation_info.group(2)  # E.g., "Cayman Islands"
        else:
            creation_date = None
            creation_country = None

        # Extract and sum the first row of numeric values in the body
        first_row = body[0][1:]  # Skipping the first column (it’s likely a name/label)
        first_row_sum = 0
        for value in first_row:
            try:
                # Remove formatting and convert to integer
                numeric_value = int(re.sub(r'\D', '', value))
                first_row_sum += numeric_value
            except ValueError:
                # Skip values that are not convertible to integers
                pass

        return {
            "title": title,
            "header": str(header),
            "body": str(body),
            "footer": footer,
            "creation_date": creation_date,
            "creation_country": creation_country,
            "first_row_sum": str(first_row_sum)
        }

    def fields_to_save_to_db(self) -> List[str]:
        return ["title", "header", "body", "footer", "creation_country", "creation_date"]

