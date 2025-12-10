"""Property Description Generator using GenAI"""
from textwrap import dedent
from ravendb_impl.gen_ai_configuration import GenAiConfiguration
from ravendb_impl.gen_ai_transformation import GenAiTransformation
from ravendb_impl.add_gen_ai_operation import AddGenAiOperation
from ravendb_impl.update_gen_ai_operation import UpdateGenAiOperation
from ravendb_impl.get_ongoing_task_info_operation import GetOngoingTaskInfoOperation, OngoingTaskType


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
                    .withJpen(loadAttachment("image.jpg"));
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
        
        task_id = existing_task.get('TaskId')
        store.maintenance.send(UpdateGenAiOperation(task_id, gen_ai_config))
    
    @classmethod
    def _needs_update(cls, existing_task, desired_config):
        """Check if existing task differs from desired configuration"""
        if not existing_task:
            return False
            
        config = existing_task.get('Configuration', {})
        
        # Compare key fields
        if config.get('Prompt') != desired_config.prompt:
            return True
        if config.get('UpdateScript', '').strip() != desired_config.update_script.strip():
            return True
        if config.get('Collection') != desired_config.collection:
            return True
        if config.get('ConnectionStringName') != desired_config.connection_string_name:
            return True
        if config.get('Identifier') != desired_config.identifier:
            return True
            
        # Compare transformation script
        transforms = config.get('Transforms', [])
        if not transforms:
            return True
        
        existing_script = transforms[0].get('Script', '').strip()
        desired_script = desired_config.gen_ai_transformation.script.strip()
        return existing_script != desired_script
    