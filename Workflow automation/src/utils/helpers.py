"""Utility modules for the workflow automation system."""

import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load configuration from JSON or environment."""
    
    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}


class Logger:
    """Configure logging for the system."""
    
    @staticmethod
    def setup(log_file: str = "app.log", level: str = "INFO"):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )


class DataExporter:
    """Export data to various formats."""
    
    @staticmethod
    def to_json(data: Dict[str, Any], indent: int = 2) -> str:
        """Export data as JSON."""
        return json.dumps(data, indent=indent, default=str)
    
    @staticmethod
    def to_csv_row(data: Dict[str, Any]) -> str:
        """Convert data to CSV row."""
        values = [str(v).replace(',', '') for v in data.values()]
        return ','.join(values)
