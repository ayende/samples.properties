using Raven.Client.Documents;
using Raven.Client.Documents.Operations.AI;
using Raven.Client.Documents.Operations.OngoingTasks;

namespace PropertySphere.Services;

public static class PropertyDescriptionGenerator
{
    private const string TaskIdentifier = "property-description-gen";

    private static GenAiConfiguration BuildConfig()
    {
        return new GenAiConfiguration
        {
            Name = "Image Description Generator",
            Identifier = TaskIdentifier,
            Collection = "Photos",
            Prompt = """
                You are an AI Assistance looking at photos from renters in 
                rental property management, usually about some issue they have. 
                Your task is to generate a concise and accurate description of what 
                is depicted in the photo provided. So maintenance can help them.
                """,
            SampleObject = """
                {
                    "Description": "Description of the image"
                }
                """,
            UpdateScript = "this.Description = $output.Description;",
            GenAiTransformation = new GenAiTransformation
            {
                Script = """
                    ai.genContext({
                        Caption: this.Caption
                    }).withJpeg(loadAttachment("image.jpg"));
                    """
            },
            ConnectionStringName = "Property Management AI Model"
        };
    }

    public static void Create(IDocumentStore store)
    {
        var genAiConfig = BuildConfig();
        var existingTask = store.Maintenance.Send(
            new GetOngoingTaskInfoOperation(genAiConfig.Name, OngoingTaskType.GenAi)
        );

        if (existingTask is null)
        {
            store.Maintenance.Send(new AddGenAiOperation(genAiConfig));
            return;
        }

        if (!NeedsUpdate(existingTask, genAiConfig))
        {
            return;
        }

        var taskId = existingTask.TaskId;
        store.Maintenance.Send(new UpdateGenAiOperation(taskId, genAiConfig));
    }

    private static bool NeedsUpdate(OngoingTask existingTask, GenAiConfiguration desiredConfig)
    {
        if (existingTask is not GenAi genAiTask)
            return false;

        var config = genAiTask.Configuration;

        if (config.Prompt != desiredConfig.Prompt)
            return true;
        if ((config.UpdateScript ?? "").Trim() != desiredConfig.UpdateScript.Trim())
            return true;
        if (config.Collection != desiredConfig.Collection)
            return true;
        if (config.ConnectionStringName != desiredConfig.ConnectionStringName)
            return true;
        if (config.Identifier != desiredConfig.Identifier)
            return true;

        // Compare transformation script
        var transforms = config.GenAiTransformation;
        if (transforms is null)
            return true;

        var existingScript = (transforms.Script ?? "").Trim();
        var desiredScript = desiredConfig.GenAiTransformation.Script.Trim();
        return existingScript != desiredScript;
    }
}
