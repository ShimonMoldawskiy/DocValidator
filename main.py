import argparse
import logging
from pathlib import Path
import sys

import common
from datetime import datetime
from validation.doc_validator import DocumentValidator
from templates import factory


def setup_logging(logging_config: dict):
    level = getattr(logging, logging_config.get("level", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logging_config.get("file", "app.log"))
        ]
    )

def parse_arguments(document_types: dict) -> dict:
    parser = argparse.ArgumentParser(description="Document Validator Application")

    parser.add_argument("document_folder", type=str, help="The path to the folder containing documents")

    for doc_type, doc_config in document_types.items():
        params_required = doc_config.get("params_required", [])
        for param in params_required:
            param_name = param["name"]
            param_type = eval(param["type"])  # Convert string representation of type to actual type
            param_help = param["help"]

            # Add arguments to the parser
            parser.add_argument("--" + param_name, dest=param_name, type=param_type, help=param_help)

    # Parse arguments
    args = parser.parse_args()

    # Convert parsed arguments to a dictionary
    parsed_args = vars(args)
    return parsed_args

class Parser:
    @staticmethod
    def parse(folder: str):
        folder_path = Path(folder)
        if not folder_path.is_dir():
            logging.error(f"The path {folder} is not a valid directory.")
            sys.exit(1)

        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                try:
                    logging.info(f"Start processing {file_path.name}")
                    template = template_factory.get_template(file_path)
                    validator = DocumentValidator(file_path, template, db_handler)
                    validator.process()
                except Exception as e:
                    logging.error(f"Failed to process {file_path}: {e}")


if __name__ == "__main__":
    config = common.ConfigLoader("config.json")

    setup_logging(config.get_logging_config())

    params = parse_arguments(config.get_document_types())

    document_folder = params.pop("document_folder", "")

    logging.info(f"Processing document folder {document_folder}. Template parameters - {params}")

    db_config = config.get_db_config()
    db_handler_class_name = db_config.pop("handler_class", None)
    db_handler_class = common.get_class(db_handler_class_name)
    if not db_handler_class:
        raise ValueError(f"Handler class '{db_handler_class_name}' not found.")
    db_handler = db_handler_class(db_config)

    template_factory = factory.TemplateFactory(config.get_document_types(), **params)

    Parser.parse(document_folder)

    logging.info(f"Document folder {document_folder} processed successfully.")