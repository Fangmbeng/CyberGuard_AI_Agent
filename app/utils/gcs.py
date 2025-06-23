# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import google.cloud.storage as storage
from google.api_core import exceptions
from app.utils.client_manager import get_storage_client

# app/utils/gcs.py

from google.cloud import storage

def upload_to_gcs(bucket_name: str, local_file: str, gcs_blob: str):
    """Upload file to GCS using global client manager."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob)
    blob.upload_from_filename(local_file)
    print(f"Uploaded {local_file} to {gcs_blob}")

def upload_file_to_gcs(bucket_name: str, local_file: str, remote_path: str) -> str:
    """
    Uploads a local file to GCS and returns the GCS URI.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_file)
    uri = f"gs://{bucket_name}/{remote_path}"
    print(f"Uploaded {local_file} to {uri}")
    return uri

def create_bucket_if_not_exists(bucket_name: str, project: str, location: str) -> None:
    """Creates a new bucket if it doesn't already exist.

    Args:
        bucket_name: Name of the bucket to create
        project: Google Cloud project ID
        location: Location to create the bucket in (defaults to us-central1)
    """
    storage_client = storage.Client(project=project)

    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    try:
        storage_client.get_bucket(bucket_name)
        logging.info(f"Bucket {bucket_name} already exists")
    except exceptions.NotFound:
        bucket = storage_client.create_bucket(
            bucket_name,
            location=location,
            project=project,
        )
        logging.info(f"Created bucket {bucket.name} in {bucket.location}")
