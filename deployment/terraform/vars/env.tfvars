# Project name used for resource naming
project_name = "cyberguardian"

# Your Production Google Cloud project id
prod_project_id = "crucial-strata-419415"

# Your Staging / Test Google Cloud project id
staging_project_id = "crucial-strata-419415"

# Your Google Cloud project ID that will be used to host the Cloud Build pipelines.
cicd_runner_project_id = "crucial-strata-419415"

# Name of the host connection you created in Cloud Build
host_connection_name = "CyberGuard_AI_Agent"

# Name of the repository you added to Cloud Build
repository_name = "Fangmbeng-CyberGuard_AI_Agent"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"
pipeline_cron_schedule = "0 * * * *"
#The value can only be one of "global", "us" and "eu".
data_store_region = "global"

# deployment/terraform/vars/env.tfvars
project_name           = "cyberguardian"
prod_project_id        = "crucial-strata-419415"
staging_project_id     = "crucial-strata-419415"
cicd_runner_project_id = "crucial-strata-419415"
region                 = "us-central1"
host_connection_name   = "CyberGuard_AI_Agent"
repository_name        = "Fangmbeng-CyberGuard_AI_Agent"
# New ingestion vars:
data_store_id          = "cyberguard-threat-ingestion_1750289908683"
data_store_region      = "global"
pipeline_root          = ""
pipeline_name          = ""
service_account        = "cyberguard-sa@crucial-strata-419415.iam.gserviceaccount.com"
cron_schedule          = "0 * * * *"      # hourly ingestion