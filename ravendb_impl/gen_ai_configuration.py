"""GenAI configuration for RavenDB AI operations"""
from typing import Dict, Any, List, Optional
from ravendb.documents.operations.ai.ai_connection_string import AiModelType
from .abstract_ai_integration_configuration import AbstractAiIntegrationConfiguration
from .gen_ai_transformation import GenAiTransformation


class GenAiConfiguration(AbstractAiIntegrationConfiguration):
    """Configuration for GenAI ETL operations"""
    
    DEFAULT_MAX_CONCURRENCY = 4
    TRANSFORMATION_NAME = "GenAi-transform-script"
    
    def __init__(
        self,
        name: str = None,
        identifier: str = None,
        collection: str = None,
        prompt: str = None,
        sample_object: str = None,
        json_schema: str = None,
        update_script: str = None,
        gen_ai_transformation: GenAiTransformation = None,
        connection_string_name: str = None,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        queries: List[Any] = None,
        enable_tracing: bool = False,
        expiration_in_sec: Optional[int] = None,
        test_mode: bool = False,
        disabled: bool = False,
        task_id: int = None
    ):
        super().__init__(
            name=name,
            connection_string_name=connection_string_name,
            test_mode=test_mode,
            disabled=disabled,
            task_id=task_id
        )
        self.identifier = identifier
        self.collection = collection
        self.prompt = prompt
        self.sample_object = sample_object
        self.json_schema = json_schema
        self.update_script = update_script
        self.gen_ai_transformation = gen_ai_transformation
        self.max_concurrency = max_concurrency
        self.queries = queries or []
        self.enable_tracing = enable_tracing
        self.expiration_in_sec = expiration_in_sec
    
    def get_destination(self) -> str:
        """Get the destination identifier"""
        return self.identifier
    
    def get_default_task_name(self) -> str:
        """Get default task name"""
        return self.identifier
    
    def generate_identifier(self) -> str:
        """Generate identifier from name"""
        # Simplified version - in full implementation would match EmbeddingsGenerationConfiguration.GenerateIdentifier
        return self.name.lower().replace(" ", "-") if self.name else ""
    
    def validate(
        self,
        validate_name: bool = True,
        validate_connection: bool = True,
        validate_identifier: bool = True
    ) -> tuple[bool, list[str]]:
        """
        Validate the configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if validate_connection and not self.initialized:
            raise RuntimeError("GenAI configuration must be initialized")
        
        errors = []
        
        # Validate identifier
        if validate_identifier and not self.identifier:
            errors.append("Identifier cannot be empty")
        
        # Validate name
        if validate_name and not self.name:
            errors.append("Name of GenAI configuration cannot be empty")
        
        # Validate connection string
        if not self.test_mode and not self.connection_string_name:
            errors.append("ConnectionStringName cannot be empty")
        
        # Validate connection
        if validate_connection and not self.test_mode:
            if self.connection:
                # Assuming connection has a validate method
                conn_errors = []
                if hasattr(self.connection, 'validate'):
                    self.connection.validate(conn_errors)
                errors.extend(conn_errors)
        
        # Validate model type
        if validate_connection and self.connection:
            if self.connection.model_type != AiModelType.CHAT:
                errors.append(f"ModelType of GenAI configuration must be {AiModelType.CHAT.value}")
        
        # Validate collection
        if not self.collection:
            errors.append("Collection must be provided")
        
        # Validate transformation
        if not self.gen_ai_transformation:
            errors.append("GenAiTransformation must be specified")
        else:
            is_valid, error = self.gen_ai_transformation.validate_script()
            if not is_valid:
                errors.append(error)
        
        # Validate prompt
        if not self.prompt:
            errors.append("Prompt must be provided")
        
        # Validate schema or sample
        if not self.json_schema and not self.sample_object:
            errors.append("You must provide either a JSON schema or a sample object")
        
        # Validate update script
        if not self.test_mode and not self.update_script:
            errors.append("You must provide an update function")
        
        return len(errors) == 0, errors
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON representation"""
        json_data = super().to_json()
        
        json_data.update({
            "Identifier": self.identifier,
            "AiConnectorType": self.ai_connector_type.value if self.ai_connector_type else None,
            "Collection": self.collection,
            "Prompt": self.prompt,
            "SampleObject": self.sample_object,
            "JsonSchema": self.json_schema,
            "UpdateScript": self.update_script,
            "GenAiTransformation": self.gen_ai_transformation.to_json() if self.gen_ai_transformation else None,
            "MaxConcurrency": self.max_concurrency,
            "Queries": [q.to_json() if hasattr(q, 'to_json') else q for q in self.queries] if self.queries else None,
            "EnableTracing": self.enable_tracing,
            "ExpirationInSec": self.expiration_in_sec,
            "EtlType": "GenAi"
        })
        
        return json_data
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "GenAiConfiguration":
        """Create from JSON representation"""
        gen_ai_transformation = None
        if json_dict.get("GenAiTransformation"):
            gen_ai_transformation = GenAiTransformation.from_json(json_dict["GenAiTransformation"])
        
        return cls(
            name=json_dict.get("Name"),
            identifier=json_dict.get("Identifier"),
            collection=json_dict.get("Collection"),
            prompt=json_dict.get("Prompt"),
            sample_object=json_dict.get("SampleObject"),
            json_schema=json_dict.get("JsonSchema"),
            update_script=json_dict.get("UpdateScript"),
            gen_ai_transformation=gen_ai_transformation,
            connection_string_name=json_dict.get("ConnectionStringName"),
            max_concurrency=json_dict.get("MaxConcurrency", cls.DEFAULT_MAX_CONCURRENCY),
            queries=json_dict.get("Queries", []),
            enable_tracing=json_dict.get("EnableTracing", False),
            expiration_in_sec=json_dict.get("ExpirationInSec"),
            test_mode=json_dict.get("TestMode", False),
            disabled=json_dict.get("Disabled", False),
            task_id=json_dict.get("TaskId")
        )
