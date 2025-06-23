"""
Google Cloud Client Manager - A pickle-safe way to handle Google Cloud clients.

This module provides a centralized way to manage Google Cloud clients that can be
safely pickled for Vertex AI Agent Engine deployment.
"""

import os
from typing import Optional, Dict, Any
from google.cloud import bigquery, storage, logging as google_cloud_logging


class PickleSafeClientManager:
    """
    A manager for Google Cloud clients that can be safely pickled.
    
    All clients are created lazily and removed during pickling to avoid
    the "Pickling client objects is explicitly not supported" error.
    """
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self._clients: Dict[str, Any] = {}
    
    def get_bigquery_client(self) -> bigquery.Client:
        """Get or create BigQuery client."""
        if 'bigquery' not in self._clients or self._clients['bigquery'] is None:
            self._clients['bigquery'] = bigquery.Client(project=self.project_id)
        return self._clients['bigquery']
    
    def get_storage_client(self) -> storage.Client:
        """Get or create Storage client."""
        if 'storage' not in self._clients or self._clients['storage'] is None:
            self._clients['storage'] = storage.Client(project=self.project_id)
        return self._clients['storage']
    
    def get_logging_client(self) -> google_cloud_logging.Client:
        """Get or create Logging client."""
        if 'logging' not in self._clients or self._clients['logging'] is None:
            self._clients['logging'] = google_cloud_logging.Client(project=self.project_id)
        return self._clients['logging']
    
    def __getstate__(self):
        """Handle pickling by removing all client objects."""
        state = self.__dict__.copy()
        # Clear all clients
        state['_clients'] = {}
        return state
    
    def __setstate__(self, state):
        """Handle unpickling by restoring state."""
        self.__dict__.update(state)
        # Clients will be recreated when accessed


# Global client manager instance
_client_manager = None

def get_client_manager() -> PickleSafeClientManager:
    """Get the global client manager instance."""
    global _client_manager
    if _client_manager is None:
        _client_manager = PickleSafeClientManager()
    return _client_manager


# Convenience functions for easy access
def get_bigquery_client() -> bigquery.Client:
    """Get BigQuery client via the global manager."""
    return get_client_manager().get_bigquery_client()

def get_storage_client() -> storage.Client:
    """Get Storage client via the global manager."""
    return get_client_manager().get_storage_client()

def get_logging_client() -> google_cloud_logging.Client:
    """Get Logging client via the global manager."""
    return get_client_manager().get_logging_client()


# Base class for services that need Google Cloud clients
class PickleSafeService:
    """
    Base class for services that use Google Cloud clients.
    
    Inheriting from this class ensures your service can be safely pickled.
    """
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id
        self._client_manager = None
    
    @property
    def client_manager(self) -> PickleSafeClientManager:
        """Get the client manager for this service."""
        if self._client_manager is None:
            self._client_manager = PickleSafeClientManager(self.project_id)
        return self._client_manager
    
    def __getstate__(self):
        """Handle pickling by removing client manager."""
        state = self.__dict__.copy()
        state['_client_manager'] = None
        return state
    
    def __setstate__(self, state):
        """Handle unpickling by restoring state."""
        self.__dict__.update(state)
        # Client manager will be recreated when accessed