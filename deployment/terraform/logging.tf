resource "google_logging_project_sink" "soc_logs" {
  name        = "soc_logs_sink"
  project     = var.prod_project_id
  destination = "bigquery.googleapis.com/projects/${var.prod_project_id}/datasets/${var.bigquery_dataset}"
  filter      = "resource.type=\"gce_instance\" OR logName:\"security\""
}

resource "google_bigquery_dataset_iam_member" "sink_writer" {
  dataset_id = var.bigquery_dataset
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_logging_project_sink.soc_logs.writer_identity}"
}
