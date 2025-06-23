# Project name used for resource naming
project_name = "my-awesome-agent"

# Your Dev Google Cloud project id
dev_project_id = "your-dev-project-id"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"
# The value can only be one of "global", "us" and "eu".
data_store_region = "us"

# deployment/terraform/vars/env.tfvars
project_name           = "cyberguardian"
prod_project_id        = "my-prod-project"
staging_project_id     = "my-staging-project"
cicd_runner_project_id = "my-ci-cd-project"
region                 = "us-central1"
host_connection_name   = "github-conn"
repository_name        = "my-repo"
# New ingestion vars:
data_store_id          = "cyber-intel-datastore"
data_store_region      = "us"
pipeline_root          = "gs://my-pipeline-root"
pipeline_name          = "cyber_intel_ingest"
service_account        = "cyber-pipeline-sa@my-prod-project.iam.gserviceaccount.com"
cron_schedule          = "0 2 * * *"      # nightly ingestion
