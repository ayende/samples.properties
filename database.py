"""Database connection and session management for RavenDB"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from ravendb import DocumentStore
from config import settings


# Global document store instance
_document_store: DocumentStore | None = None


def get_document_store() -> DocumentStore:
    """Get the singleton document store instance"""
    global _document_store
    if _document_store is None:
        raise RuntimeError("Document store not initialized. Call init_document_store() first.")
    return _document_store


def init_document_store() -> DocumentStore:
    """Initialize the RavenDB document store"""
    global _document_store
    
    if _document_store is not None:
        return _document_store
    
    _document_store = DocumentStore(
        urls=[settings.ravendb_url],
        database=settings.ravendb_database
    )
    _document_store.initialize()
    
    # Create indexes
    from indexes import DebtItemsOutstanding
    DebtItemsOutstanding().execute(_document_store)
    
    return _document_store


def close_document_store():
    """Close the document store"""
    global _document_store
    if _document_store is not None:
        _document_store.close()
        _document_store = None


@asynccontextmanager
async def get_session() -> AsyncGenerator:
    """Get a RavenDB session as an async context manager"""
    store = get_document_store()
    session = store.open_session()
    try:
        yield session
    finally:
        session.close()
