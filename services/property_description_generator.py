"""Property Description Generator using GenAI"""
from textwrap import dedent
from ravendb.documents.operations.ai import (
    GenAiConfiguration,
    GenAiTransformation,
    AddGenAiOperation,
    UpdateGenAiOperation,
)
from ravendb.documents.operations.ongoing_tasks import (
    GetOngoingTaskInfoOperation,
    OngoingTaskType,
)


class PropertyDescriptionGenerator:
    """GenAI task for generating property descriptions"""
    
    TASK_IDENTIFIER = "property-description-gen"
    
    @classmethod
    def _build_config(cls):
        """Build the desired GenAI configuration"""
        gen_ai_transformation = GenAiTransformation(
            script=dedent("""
                ai.genContext({
                    Caption: this.Caption
                })
                    .withJpeg(loadAttachment("image.jpg"));
            """).strip()
        )
        
        return GenAiConfiguration(
            name="Image Description Generator",
            identifier=cls.TASK_IDENTIFIER,
            collection="Photos",
            prompt=dedent("""
                You are an AI Assistance looking at photos from renters in 
                rental property management, usually about some issue they have. 
                Your task is to generate a concise and accurate description of what 
                is depicted in the photo provided. So maintenance can help them.
                """).strip(),
            sample_object='{"Description": "Description of the image"}',
            update_script="this.Description = $output.Description;",
            gen_ai_transformation=gen_ai_transformation,
            connection_string_name="Property Management AI Model"
        )
    
    @classmethod
    def create(cls, store):
        """Create or update the Property Description Generator GenAI task"""
        
        gen_ai_config = cls._build_config()
        
        existing_task = store.maintenance.send(
            GetOngoingTaskInfoOperation(gen_ai_config.name, OngoingTaskType.GEN_AI)
        )
        
        if not existing_task:
            store.maintenance.send(AddGenAiOperation(gen_ai_config))
            return

        if not cls._needs_update(existing_task, gen_ai_config):
            return
        
        task_id = existing_task.task_id
        store.maintenance.send(UpdateGenAiOperation(task_id, gen_ai_config))
    
    @classmethod
    def _needs_update(cls, existing_task, desired_config):
        """Check if existing task differs from desired configuration"""
        if not existing_task:
            return False
            
        config = existing_task.configuration

        # Compare key fields directly on the configuration object (snake_case properties)
        if config.prompt != desired_config.prompt:
            return True
        if (config.update_script or "").strip() != desired_config.update_script.strip():
            return True
        if config.collection != desired_config.collection:
            return True
        if config.connection_string_name != desired_config.connection_string_name:
            return True
        if config.identifier != desired_config.identifier:
            return True
            
        # Compare transformation script
        transforms = config.transforms or []
        if not transforms:
            return True
        
        first = transforms[0]
        existing_script = (first.script or "").strip()
        desired_script = desired_config.gen_ai_transformation.script.strip()
        return existing_script != desired_script
    