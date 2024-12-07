import random
import json
from typing import Any, Dict

from utils.logger import logger


class ElasticLoader:
    """Class to load data to Elasticseach."""

    def __init__(self, client: object) -> None:
        self.client = client

    def _check_doc_exists(self, index: str, id: str) -> bool:
        """
        Private method to check the existence of the
        document in Elastichsearch.

        Return True if exists, otherwise False.
        """
        check = self.client.exists(index=index, id=id)
        return check

    def load_document(self, index: str, document_id: str, document: Dict[str, Any]) -> bool:
        """
        Load a single document into Elasticsearch.
        """
        try:
            if self._check_doc_exists(index, document_id):
                logger.info(f"Document {document_id} already exists in index {index}. Skipping.")
                return False

            self.client.index(index=index, id=document_id, document=document)
            logger.info(f"Document {document_id} successfully indexed in {index}.")
            return True
        except Exception as e:
            logger.error(f"Error loading document {document_id}: {e}")
            return False

    def load_documents_from_file(self, index: str, file_path: str) -> None:
        """
        Load multiple documents from a JSON file into Elasticsearch.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    logger.error("Input JSON file must contain an array of documents.")
                    return

                for document in data:
                    document_id = document.get("document_id", f"random_id_{random.randint(1000, 9999)}")
                    self.load_document(index=index, document_id=document_id, document=document)

            logger.info(f"All documents from {file_path} have been processed.")
        except Exception as e:
            logger.error(f"Error loading documents from file {file_path}: {e}")
