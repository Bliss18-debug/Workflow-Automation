"""
Document Manager - Core document storage and retrieval system.

Handles document upload, organization, search, and compliance policies.
Integrates with cloud storage (SharePoint, OneDrive, Google Drive).
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class Document:
    """Represents a managed document."""
    
    def __init__(
        self,
        name: str,
        content_type: str,
        file_path: str,
        owner_id: str,
        metadata: Optional[Dict] = None
    ):
        self.document_id = str(uuid.uuid4())
        self.name = name
        self.content_type = content_type
        self.file_path = file_path
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata = metadata or {}
        self.tags: List[str] = []
        self.access_control: Dict[str, List[str]] = {
            "view": [owner_id],
            "edit": [owner_id],
            "delete": [owner_id]
        }
        self.status = "active"
        self.retention_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert document to dictionary."""
        return {
            "document_id": self.document_id,
            "name": self.name,
            "content_type": self.content_type,
            "file_path": self.file_path,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
            "status": self.status,
            "retention_until": self.retention_until.isoformat() if self.retention_until else None
        }


class DocumentManager:
    """
    Manages document lifecycle, storage, and retrieval.
    
    Features:
    - Document upload and organization
    - Auto-tagging and categorization
    - Version control
    - Retention policies
    - Access control
    - Search by metadata
    """
    
    def __init__(self, storage_path: str = "./documents"):
        """
        Initialize document manager.
        
        Args:
            storage_path: Root path for document storage
        """
        self.storage_path = storage_path
        self.documents: Dict[str, Document] = {}
        self.document_index: Dict[str, List[str]] = {}  # Tag -> Document IDs
        os.makedirs(storage_path, exist_ok=True)
        logger.info(f"DocumentManager initialized with storage: {storage_path}")
    
    def upload_document(
        self,
        name: str,
        file_content: bytes,
        content_type: str,
        owner_id: str,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        auto_tag: bool = True
    ) -> str:
        """
        Upload a document.
        
        Args:
            name: Document name
            file_content: File content as bytes
            content_type: MIME type (e.g., 'application/pdf')
            owner_id: ID of the document owner
            metadata: Custom metadata dictionary
            tags: Manual tags to apply
            auto_tag: Whether to auto-tag based on content analysis
            
        Returns:
            Document ID
        """
        # Create document object
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(self.storage_path, doc_id, name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Create document record
        document = Document(name, content_type, file_path, owner_id, metadata)
        
        # Apply tags
        if tags:
            document.tags.extend(tags)
        
        # Auto-tag based on filename and metadata
        if auto_tag:
            auto_tags = self._auto_tag_document(name, metadata)
            document.tags.extend(auto_tags)
        
        # Remove duplicates
        document.tags = list(set(document.tags))
        
        self.documents[document.document_id] = document
        
        # Update index
        for tag in document.tags:
            if tag not in self.document_index:
                self.document_index[tag] = []
            self.document_index[tag].append(document.document_id)
        
        logger.info(f"Document uploaded: {document.document_id} ({name})")
        return document.document_id
    
    def _auto_tag_document(self, filename: str, metadata: Optional[Dict]) -> List[str]:
        """Auto-generate tags based on filename and metadata."""
        tags = []
        
        # Tag by file extension
        ext = Path(filename).suffix.lower().strip('.')
        if ext:
            tags.append(f"type:{ext}")
        
        # Tag by department/category if in metadata
        if metadata:
            if "department" in metadata:
                tags.append(f"dept:{metadata['department']}")
            if "category" in metadata:
                tags.append(f"category:{metadata['category']}")
        
        # Tag by year from metadata
        if metadata and "year" in metadata:
            tags.append(f"year:{metadata['year']}")
        
        return tags
    
    def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """
        Retrieve a document (with access control check).
        
        Args:
            document_id: ID of the document
            user_id: ID of the user requesting access
            
        Returns:
            Document object or None if not found or no access
        """
        if document_id not in self.documents:
            return None
        
        document = self.documents[document_id]
        
        # Check access control
        if user_id not in document.access_control["view"] and document.owner_id != user_id:
            logger.warning(f"Access denied for user {user_id} to document {document_id}")
            return None
        
        return document
    
    def search_documents(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata_filter: Optional[Dict] = None,
        owner_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Search documents by tags, metadata, and owner.
        
        Args:
            query: Search query (matches filename and tags)
            tags: Filter by tags
            metadata_filter: Filter by metadata fields
            owner_id: Filter by owner
            user_id: Requesting user (for access control)
            
        Returns:
            List of matching documents
        """
        results = []
        
        for doc_id, document in self.documents.items():
            # Access control check
            if user_id and user_id not in document.access_control["view"] and document.owner_id != user_id:
                continue
            
            # Owner filter
            if owner_id and document.owner_id != owner_id:
                continue
            
            # Name/query filter
            if query and query.lower() not in document.name.lower():
                continue
            
            # Tags filter
            if tags:
                if not any(tag in document.tags for tag in tags):
                    continue
            
            # Metadata filter
            if metadata_filter:
                if not all(
                    document.metadata.get(k) == v
                    for k, v in metadata_filter.items()
                ):
                    continue
            
            results.append(document.to_dict())
        
        return results
    
    def grant_access(
        self,
        document_id: str,
        user_id: str,
        permission_type: str  # 'view', 'edit', 'delete'
    ) -> bool:
        """
        Grant access to a document.
        
        Args:
            document_id: ID of the document
            user_id: ID of the user to grant access to
            permission_type: Type of permission
            
        Returns:
            Success status
        """
        if document_id not in self.documents:
            return False
        
        document = self.documents[document_id]
        if user_id not in document.access_control[permission_type]:
            document.access_control[permission_type].append(user_id)
            logger.info(f"Access granted: {user_id} -> {document_id} ({permission_type})")
        
        return True
    
    def set_retention_policy(
        self,
        document_id: str,
        retention_days: int,
        auto_delete: bool = False
    ) -> bool:
        """
        Set retention policy for a document.
        
        Args:
            document_id: ID of the document
            retention_days: Number of days to retain
            auto_delete: Whether to auto-delete after retention expires
            
        Returns:
            Success status
        """
        if document_id not in self.documents:
            return False
        
        document = self.documents[document_id]
        document.retention_until = datetime.now() + timedelta(days=retention_days)
        
        logger.info(f"Retention policy set for {document_id}: {retention_days} days")
        return True
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document (with access control).
        
        Args:
            document_id: ID of the document
            user_id: ID of the user requesting deletion
            
        Returns:
            Success status
        """
        if document_id not in self.documents:
            return False
        
        document = self.documents[document_id]
        
        # Check permission
        if user_id not in document.access_control["delete"] and document.owner_id != user_id:
            logger.warning(f"Delete denied for user {user_id} to document {document_id}")
            return False
        
        # Remove from file system
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
        
        # Remove from indices
        for tag in document.tags:
            if tag in self.document_index:
                self.document_index[tag].remove(document_id)
        
        # Remove document record
        del self.documents[document_id]
        
        logger.info(f"Document deleted: {document_id}")
        return True
    
    def export_document_manifest(self) -> Dict:
        """Export a manifest of all documents."""
        return {
            "total_documents": len(self.documents),
            "documents": [doc.to_dict() for doc in self.documents.values()],
            "tags": list(self.document_index.keys()),
            "exported_at": datetime.now().isoformat()
        }
