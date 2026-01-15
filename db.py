
import json
import datetime
from dataclasses import asdict
import os
from cleanliness import Observability
from analyzer import AnalyzeResult

# Initialize logger
logger = Observability().get_logger("database")

class Database:
    """
    Handles JSON file storage for Analyze Tracker.
    """
    def __init__(self, db_path="analysis_history.json"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the JSON file if it doesn't exist."""
        try:
            if not os.path.exists(self.db_path):
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                logger.debug("json_db_initialized", path=self.db_path)
        except Exception as e:
            logger.error("db_init_failed", error=str(e))
            raise

    def save_result(self, source: str, result: AnalyzeResult):
        """
        Saves an analysis result to the JSON file.
        
        Args:
            source: description of the input source (e.g. filename or "text_input")
            result: The AnalyzeResult object to save
        
        Returns:
            int: The index of the saved item (acting as pseudo-ID)
        """
        try:
            # Load existing data
            data = []
            if os.path.exists(self.db_path):
                try:
                    with open(self.db_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            data = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("db_corrupted_resetting", path=self.db_path)
                    data = []

            # Prepare new record
            record = {
                "id": len(data) + 1,
                "timestamp": datetime.datetime.now().isoformat(),
                "source": source,
                "metrics": asdict(result)
            }
            
            data.append(record)

            # Write back
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            logger.info("result_saved_to_json", source=source, id=record['id'])
            return record['id']
            
        except Exception as e:
            logger.error("db_save_failed", error=str(e))
            raise
