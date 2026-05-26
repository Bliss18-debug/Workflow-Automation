"""
Version Control - Document versioning and change tracking.

Maintains version history, enables rollback, and provides
change auditing for compliance and audit trails.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class DocumentVersion:
    """Represents a version of a document."""
    version_id: str
    document_id: str
    version_number: int
    file_path: str
    created_by: str
    created_at: datetime
    change_summary: str
    file_hash: Optional[str] = None  # For integrity checking
    is_current: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "version_id": self.version_id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "file_path": self.file_path,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "change_summary": self.change_summary,
            "file_hash": self.file_hash,
            "is_current": self.is_current
        }


class VersionControl:
    """
    Manages document versions and change tracking.
    
    Features:
    - Version history tracking
    - Rollback to previous versions
    - Change summaries and audit trails
    - File integrity (hashing)
    """
    
    def __init__(self):
        """Initialize version control."""
        self.versions: Dict[str, List[DocumentVersion]] = {}  # document_id -> versions
        self.change_log: List[Dict] = []
        logger.info("VersionControl initialized")
    
    def create_version(
        self,
        document_id: str,
        file_path: str,
        created_by: str,
        change_summary: str,
        file_hash: Optional[str] = None
    ) -> str:
        """
        Create a new version of a document.
        
        Args:
            document_id: ID of the document
            file_path: Path to the version file
            created_by: User ID of the person creating the version
            change_summary: Summary of changes made
            file_hash: Hash for integrity checking
            
        Returns:
            Version ID
        """
        if document_id not in self.versions:
            self.versions[document_id] = []
        
        # Mark previous version as not current
        for version in self.versions[document_id]:
            version.is_current = False
        
        # Create new version
        version_number = len(self.versions[document_id]) + 1
        version = DocumentVersion(
            version_id=str(uuid.uuid4()),
            document_id=document_id,
            version_number=version_number,
            file_path=file_path,
            created_by=created_by,
            created_at=datetime.now(),
            change_summary=change_summary,
            file_hash=file_hash,
            is_current=True
        )
        
        self.versions[document_id].append(version)
        
        # Log change
        self.change_log.append({
            "timestamp": datetime.now().isoformat(),
            "document_id": document_id,
            "version_number": version_number,
            "action": "create_version",
            "created_by": created_by,
            "change_summary": change_summary
        })
        
        logger.info(f"Version created: {version.version_id} for document {document_id}")
        return version.version_id
    
    def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        """Get a specific version."""
        for versions_list in self.versions.values():
            for version in versions_list:
                if version.version_id == version_id:
                    return version
        return None
    
    def get_document_versions(self, document_id: str) -> List[Dict]:
        """
        Get all versions of a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of version details
        """
        if document_id not in self.versions:
            return []
        
        return [v.to_dict() for v in self.versions[document_id]]
    
    def get_current_version(self, document_id: str) -> Optional[DocumentVersion]:
        """Get the current/latest version of a document."""
        if document_id not in self.versions:
            return None
        
        for version in self.versions[document_id]:
            if version.is_current:
                return version
        
        return None
    
    def rollback_to_version(
        self,
        document_id: str,
        version_id: str,
        rolled_back_by: str
    ) -> bool:
        """
        Rollback to a previous version.
        
        Args:
            document_id: ID of the document
            version_id: ID of the version to rollback to
            rolled_back_by: User ID of the person rolling back
            
        Returns:
            Success status
        """
        if document_id not in self.versions:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        target_version = None
        for version in self.versions[document_id]:
            if version.version_id == version_id:
                target_version = version
                break
        
        if not target_version:
            logger.warning(f"Version not found: {version_id}")
            return False
        
        # Create a new version based on the rollback
        new_version = self.create_version(
            document_id=document_id,
            file_path=target_version.file_path,  # Use the same file
            created_by=rolled_back_by,
            change_summary=f"Rolled back to version {target_version.version_number}",
            file_hash=target_version.file_hash
        )
        
        # Log the rollback action
        self.change_log.append({
            "timestamp": datetime.now().isoformat(),
            "document_id": document_id,
            "action": "rollback",
            "rolled_back_to_version": target_version.version_number,
            "rolled_back_by": rolled_back_by
        })
        
        logger.info(f"Document {document_id} rolled back to version {target_version.version_number}")
        return True
    
    def get_change_history(
        self,
        document_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get change history.
        
        Args:
            document_id: Optional filter by document
            limit: Maximum number of entries to return
            
        Returns:
            List of change log entries
        """
        results = self.change_log
        
        if document_id:
            results = [e for e in results if e.get("document_id") == document_id]
        
        return results[-limit:]
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions (basic comparison).
        
        Args:
            version_id1: First version ID
            version_id2: Second version ID
            
        Returns:
            Comparison details
        """
        version1 = self.get_version(version_id1)
        version2 = self.get_version(version_id2)
        
        if not version1 or not version2:
            return {}
        
        return {
            "version1": version1.to_dict(),
            "version2": version2.to_dict(),
            "created_by_diff": version1.created_by != version2.created_by,
            "timestamp_diff": (version2.created_at - version1.created_at).total_seconds(),
            "hash_match": version1.file_hash == version2.file_hash
        }
