"""Database connection and session management for RavenDB"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from ravendb import DocumentStore
from ravendb.documents.indexes.index_creation import IndexCreation
from ravendb.documents.operations.ai.ai_connection_string import AiConnectionString, AiModelType
from ravendb.documents.operations.ai.open_ai_settings import OpenAiSettings
from ravendb.documents.operations.connection_string.put_connection_string_operation import PutConnectionStringOperation
from indexes import DebtItems_Outstanding, ServiceRequests_ByStatusAndLocation
from config import settings
from services.property_agent import PropertyAgent
from services.property_description_generator import PropertyDescriptionGenerator
from services.photo_subscription import PhotoSubscription

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

    if settings.ai_api_key and settings.ai_api_key != "YOUR_OPENAI_API_KEY_HERE":
        openai_settings = OpenAiSettings(
            api_key=settings.ai_api_key,
            endpoint="https://api.openai.com/v1",
            model=settings.ai_model
        )
        ai_connection = AiConnectionString(
            name="Property Management AI Model",
            identifier="property-management-ai-model",
            openai_settings=openai_settings,
            model_type=AiModelType.CHAT
        )
        _document_store.maintenance.send(
            PutConnectionStringOperation(ai_connection)
        )
        PropertyAgent.create(_document_store)
        
        PropertyDescriptionGenerator.create(_document_store)
        
    PhotoSubscription.create(_document_store)

    IndexCreation.create_indexes([
        DebtItems_Outstanding(), 
        ServiceRequests_ByStatusAndLocation()
    ], _document_store)
    
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
