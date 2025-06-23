from google.cloud import aiplatform
from app.utils.config import PlatformConfig

class VertexAIService:
    def __init__(self, config: PlatformConfig):
        self.config = config
        # Initialize Vertex AI SDK
        aiplatform.init(
            project=self.config.project_id,
            location=self.config.vertex_ai_location,
        )

    def train_threat_model(
        self,
        bq_source_table: str,
        display_name: str = "cyberguardian-threat-model",
        budget_milli_node_hours: int = 1000,
    ) -> str:
        """
        Trains a text classification model on threat intelligence data stored
        in BigQuery. Returns the model resource name.
        
        Args:
            bq_source_table: BigQuery table in the format
                             "project.dataset.table" containing labeled threat data.
            display_name: Human‑readable name for the training job & model.
            budget_milli_node_hours: Compute budget for AutoML training.
        """
        # Create an AutoML Text Training job for classification
        job = aiplatform.AutoMLTextTrainingJob(
            display_name=display_name,
            prediction_type="classification",
            multi_label=True,
        )

        # Run the job using BigQuery as the input source
        model = job.run(
            dataset=bq_source_table,
            model_display_name=display_name,
            training_pipeline_args={"budgetMilliNodeHours": budget_milli_node_hours},
        )

        # Returns the full resource name of the trained model
        return model.resource_name
