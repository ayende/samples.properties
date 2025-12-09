"""Abstract base class for AI integration configurations"""
from abc import ABC
from typing import Optional
from enum import Enum


class AiConnectorType(Enum):
    """Types of AI connectors"""
    NONE = "None"
    OPENAI = "OpenAi"
    AZURE_OPENAI = "AzureOpenAi"
    OLLAMA = "Ollama"
    EMBEDDED = "Embedded"
    GOOGLE = "Google"
    HUGGINGFACE = "HuggingFace"
    MISTRAL_AI = "MistralAi"
    VERTEX = "Vertex"


class AbstractAiIntegrationConfiguration(ABC):
    """Base class for AI integration configurations (ETL-based)"""
    
    def __init__(
        self,
        name: str = None,
        connection_string_name: str = None,
        test_mode: bool = False,
        disabled: bool = False,
        task_id: int = None
    ):
        self.name = name
        self.connection_string_name = connection_string_name
        self.test_mode = test_mode
        self.disabled = disabled
        self.task_id = task_id
        self.connection = None  # Will be set by initialization
        self.initialized = False
    
    @property
    def ai_connector_type(self) -> AiConnectorType:
        """Get the active AI connector type from connection"""
        if self.connection:
            return self.connection.get_active_provider()
        return AiConnectorType.NONE
    
    def to_json(self) -> dict:
        """Convert to JSON representation"""
        return {
            "Name": self.name,
            "ConnectionStringName": self.connection_string_name,
            "TestMode": self.test_mode,
            "Disabled": self.disabled,
            "TaskId": self.task_id
        }
