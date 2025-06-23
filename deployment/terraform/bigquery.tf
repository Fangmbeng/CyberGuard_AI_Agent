resource "google_bigquery_data_transfer_config" "cve_feed" {
  display_name            = "CVE Feed Daily"
  data_source_id          = "scheduled_query"
  project                 = var.prod_project_id
  destination_dataset_id  = var.bigquery_dataset
  schedule                = "every 24 hours"

  params = {
    query = <<-SQL
      SELECT id, description, published
      FROM `bigquery-public-data.cve.CVE`
      WHERE DATE(published) = CURRENT_DATE()
    SQL
    destination_table_name_template = "cve_feed"
    write_disposition               = "WRITE_APPEND"
    partitioning_field              = "published"
  }
}
