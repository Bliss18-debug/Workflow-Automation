"""
Document Metadata - Extract and manage document metadata.

Handles metadata extraction from documents, enrichment,
and search optimization through metadata indexing.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentMetadata:
    """
    Manages document metadata extraction and management.
    
    Supports:
    - Custom metadata fields
    - Automatic extraction (filename patterns, file properties)
    - Metadata search indexing
    - Metadata enrichment
    """
    
    # Standard metadata fields
    STANDARD_FIELDS = {
        "title": str,
        "author": str,
        "department": str,
        "category": str,
        "sensitivity": str,  # public, internal, confidential
        "retention_years": int,
        "created_date": datetime,
        "modified_date": datetime,
        "file_size": int,
        "page_count": int
    }
    
    def __init__(self):
        """Initialize metadata manager."""
        self.metadata_cache: Dict[str, Dict] = {}
        logger.info("DocumentMetadata initialized")
    
    def extract_metadata(
        self,
        file_path: str,
        filename: str,
        file_content: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from a document.
        
        Args:
            file_path: Path to the file
            filename: Filename
            file_content: File content (optional for advanced extraction)
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        
        # Extract from filename
        filename_metadata = self._extract_from_filename(filename)
        metadata.update(filename_metadata)
        
        # Extract from file system
        try:
            import os
            stat_info = os.stat(file_path)
            metadata["file_size"] = stat_info.st_size
            metadata["created_date"] = datetime.fromtimestamp(stat_info.st_ctime)
            metadata["modified_date"] = datetime.fromtimestamp(stat_info.st_mtime)
        except Exception as e:
            logger.warning(f"Error extracting file stats: {str(e)}")
        
        # Extract from file content if available
        if file_content:
            content_metadata = self._extract_from_content(filename, file_content)
            metadata.update(content_metadata)
        
        return metadata
    
    def _extract_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from filename."""
        metadata = {}
        
        # Example pattern: DEPT_CATEGORY_YYYY_MMDD_DESCRIPTION.pdf
        parts = filename.replace('.pdf', '').replace('.docx', '').split('_')
        
        if len(parts) >= 2:
            metadata["department"] = parts[0]
        if len(parts) >= 2:
            metadata["category"] = parts[1]
        if len(parts) >= 3:
            try:
                year = int(parts[2])
                metadata["year"] = year
            except ValueError:
                pass
        
        metadata["title"] = filename
        
        return metadata
    
    def _extract_from_content(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Extract metadata from file content (basic implementation)."""
        metadata = {}
        
        # Detect file type and extract relevant metadata
        file_type = filename.split('.')[-1].lower()
        
        if file_type == "pdf":
            # Basic PDF analysis
            try:
                page_count = content.count(b'/Page')
                if page_count > 0:
                    metadata["page_count"] = max(1, page_count // 10)  # Rough estimate
            except Exception as e:
                logger.warning(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def enrich_metadata(
        self,
        document_id: str,
        metadata: Dict[str, Any],
        additional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich document metadata with additional information.
        
        Args:
            document_id: ID of the document
            metadata: Existing metadata
            additional_data: New metadata to add
            
        Returns:
            Enriched metadata
        """
        enriched = metadata.copy()
        enriched.update(additional_data)
        
        # Cache the enriched metadata
        self.metadata_cache[document_id] = enriched
        
        logger.info(f"Metadata enriched for document: {document_id}")
        return enriched
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate metadata against standards.
        
        Args:
            metadata: Metadata to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        for field, expected_type in self.STANDARD_FIELDS.items():
            if field in metadata:
                value = metadata[field]
                # Basic type checking
                if expected_type == int and not isinstance(value, int):
                    errors.append(f"{field} must be an integer")
                elif expected_type == str and not isinstance(value, str):
                    errors.append(f"{field} must be a string")
        
        # Validate sensitivity field
        if "sensitivity" in metadata:
            valid_values = ["public", "internal", "confidential"]
            if metadata["sensitivity"] not in valid_values:
                errors.append(f"sensitivity must be one of: {', '.join(valid_values)}")
        
        return len(errors) == 0, errors
    
    def index_metadata(self, document_id: str, metadata: Dict[str, Any]) -> None:
        """
        Index document metadata for fast searching.
        
        Args:
            document_id: ID of the document
            metadata: Metadata to index
        """
        self.metadata_cache[document_id] = metadata
        logger.debug(f"Metadata indexed for document: {document_id}")
    
    def search_by_metadata(
        self,
        filters: Dict[str, Any]
    ) -> List[str]:
        """
        Search documents by metadata.
        
        Args:
            filters: Metadata filters (key -> value pairs)
            
        Returns:
            List of matching document IDs
        """
        results = []
        
        for doc_id, metadata in self.metadata_cache.items():
            match = True
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                results.append(doc_id)
        
        return results
    
    def get_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get cached metadata for a document."""
        return self.metadata_cache.get(document_id)
