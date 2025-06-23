resource "null_resource" "schedule_kfp" {
  # This runs “uvx agent‑starter‑pack run” to schedule the KFP pipeline
  provisioner "local-exec" {
    command = <<-EOT
      python data_ingestion/submit_pipeline.py \
        --project-id ${var.prod_project_id} \
        --region ${var.region} \
        --data-store-region ${var.data_store_region} \
        --data-store-id ${var.data_store_id} \
        --service-account ${var.service_account} \
        --pipeline-root ${var.pipeline_root} \
        --pipeline-name ${var.pipeline_name} \
        --cron-schedule "${var.cron_schedule}" \
        --schedule-only true
    EOT
  }
  triggers = {
    cron = var.cron_schedule
  }
}
