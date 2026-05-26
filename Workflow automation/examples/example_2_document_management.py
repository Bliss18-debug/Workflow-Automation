"""
Example 2: Document Management & Versioning

Demonstrates:
1. Document upload and tagging
2. Automatic metadata extraction
3. Version control
4. Search and retrieval
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.documents import DocumentManager, DocumentMetadata, VersionControl


def example_2_document_management():
    """Run document management example."""
    
    print("=" * 60)
    print("EXAMPLE 2: DOCUMENT MANAGEMENT & VERSIONING")
    print("=" * 60)
    
    # 1. Initialize document manager
    print("\n[Step 1] Initializing document manager...")
    doc_manager = DocumentManager(storage_path="./documents")
    print("✓ Document manager initialized")
    
    # 2. Upload documents
    print("\n[Step 2] Uploading documents...")
    
    # Simulate file content
    file_content = b"Sample PDF content for HR policies document"
    
    doc_id = doc_manager.upload_document(
        name="HR_Policies_2024.pdf",
        file_content=file_content,
        content_type="application/pdf",
        owner_id="emp_001",
        metadata={"department": "HR", "category": "Policies", "year": 2024},
        tags=["policies", "hr", "compliance"],
        auto_tag=True
    )
    
    print(f"✓ Document uploaded: {doc_id}")
    print(f"  Tags: policies, hr, compliance, type:pdf, dept:HR, category:Policies, year:2024")
    
    # 3. Search documents
    print("\n[Step 3] Searching documents...")
    
    results = doc_manager.search_documents(
        tags=["policies"],
        owner_id="emp_001"
    )
    
    print(f"✓ Found {len(results)} document(s) matching 'policies' tag")
    for doc in results:
        print(f"  - {doc['name']} (ID: {doc['document_id']})")
    
    # 4. Version control
    print("\n[Step 4] Managing document versions...")
    
    version_control = VersionControl()
    
    # Create first version
    v1_id = version_control.create_version(
        document_id=doc_id,
        file_path="./documents/HR_Policies_2024_v1.pdf",
        created_by="emp_001",
        change_summary="Initial upload"
    )
    print(f"✓ Version 1 created: {v1_id}")
    
    # Simulate an update
    updated_content = b"Updated HR policies with new regulations"
    v2_id = version_control.create_version(
        document_id=doc_id,
        file_path="./documents/HR_Policies_2024_v2.pdf",
        created_by="emp_002",
        change_summary="Updated compliance requirements"
    )
    print(f"✓ Version 2 created: {v2_id}")
    
    # List versions
    versions = version_control.get_document_versions(doc_id)
    print(f"✓ Document has {len(versions)} version(s)")
    for v in versions:
        print(f"  - Version {v['version_number']}: {v['change_summary']} (by {v['created_by']})")
    
    # 5. Access control
    print("\n[Step 5] Managing access control...")
    
    doc_manager.grant_access(doc_id, "emp_003", "view")
    doc_manager.grant_access(doc_id, "emp_004", "edit")
    
    print("✓ Access granted to emp_003 (view) and emp_004 (edit)")
    
    # Verify access
    doc = doc_manager.get_document(doc_id, "emp_003")
    if doc:
        print(f"✓ emp_003 can access: {doc['name']}")
    
    # 6. Metadata management
    print("\n[Step 6] Managing metadata...")
    
    metadata_manager = DocumentMetadata()
    
    # Extract metadata
    metadata = metadata_manager.extract_metadata(
        file_path="./documents/HR_Policies_2024.pdf",
        filename="HR_Policies_2024.pdf"
    )
    print(f"✓ Extracted metadata:")
    for key, value in metadata.items():
        print(f"  - {key}: {value}")
    
    # Enrich metadata
    enriched = metadata_manager.enrich_metadata(
        document_id=doc_id,
        metadata=metadata,
        additional_data={"reviewed_by": "emp_005", "approved": True}
    )
    print("✓ Metadata enriched with review information")
    
    # 7. Retention policy
    print("\n[Step 7] Setting retention policy...")
    
    doc_manager.set_retention_policy(doc_id, retention_days=365, auto_delete=True)
    print("✓ Retention policy set: 365 days")
    
    # 8. Export manifest
    print("\n[Step 8] Exporting document manifest...")
    
    manifest = doc_manager.export_document_manifest()
    print(f"✓ Manifest exported:")
    print(f"  Total documents: {manifest['total_documents']}")
    print(f"  Tags: {', '.join(manifest['tags'])}")
    
    print("\n✓ Document management example completed!\n")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    example_2_document_management()
