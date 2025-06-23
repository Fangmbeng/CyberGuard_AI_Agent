resource "google_storage_bucket" "darkweb_code" {
  name     = "${var.project_name}-darkweb-fn"
  location = var.region
}

resource "google_storage_bucket_object" "darkweb_source" {
  name   = "ingest_darkweb.zip"
  bucket = google_storage_bucket.darkweb_code.name
  source = "../../data_ingestion/ingest_darkweb.py"
}

resource "google_cloudfunctions_function" "ingest_darkweb" {
  name        = "ingest_darkweb"
  project     = var.prod_project_id
  region      = var.region
  runtime     = "python310"
  entry_point= "ingest_darkweb"
  source_archive_bucket = google_storage_bucket.darkweb_code.name
  source_archive_object = google_storage_bucket_object.darkweb_source.name
  trigger_http = true

  environment_variables = {
    BIGQUERY_DATASET = var.bigquery_dataset
    DARK_WEB_API     = "https://api.example-darkweb.com/chatter"
  }
}

resource "google_cloud_scheduler_job" "darkweb_ingest_job" {
  name       = "darkweb-ingest-job"
  schedule   = var.cron_schedule
  time_zone  = "UTC"
  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.ingest_darkweb.https_trigger_url
  }
}
