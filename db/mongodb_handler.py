from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from common import FatalError
from db import db_handlers


class MongoDbHandler(db_handlers.AbstractDatabaseHandler):
    def __init__(self, config: dict):
        try:
            self._client: MongoClient = MongoClient(host=config.get("host", "localhost"), port=config.get("port", 27017))
            self._db: Database = self._client[config.get("name", "document_validation")]
            self._documents: Collection = self._db[config.get("documents_table", "documents")]
            self._discrepancies: Collection = self._db[config.get("discrepancies_table", "discrepancies")]
        except Exception as e:
            raise FatalError from e

    def insert_document(self, document_info: dict) -> ObjectId:
        return self._documents.insert_one(document_info).inserted_id

    def insert_discrepancy(self, discrepancy: dict) -> ObjectId:
        return self._discrepancies.insert_one(discrepancy).inserted_id

    def update_document(self, document_id, update_data):
        pass

    def update_discrepancy(self, document_id, update_data):
        pass

    def delete_document(self, document_id):
        pass

    def delete_discrepancy(self, discrepancy_id):
        pass
