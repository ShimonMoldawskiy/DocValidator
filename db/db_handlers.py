from abc import ABC, abstractmethod

class AbstractDatabaseHandler(ABC):

    @abstractmethod
    def insert_document(self, document_info: dict):
        """Inserts a document into the database and returns the document ID."""
        pass

    @abstractmethod
    def update_document(self, document_id, update_data):
        """Updates a document by its ID."""
        pass

    @abstractmethod
    def delete_document(self, document_id):
        """Deletes a document by its ID."""
        pass

    @abstractmethod
    def insert_discrepancy(self, discrepancy: dict):
        """Inserts a discrepancy into the database and returns the discrepancy ID."""
        pass

    @abstractmethod
    def update_discrepancy(self, discrepancy_id, update_data):
        """Updates a discrepancy by its ID."""
        pass

    @abstractmethod
    def delete_discrepancy(self, discrepancy_id):
        """Deletes a discrepancy by its ID."""
        pass

