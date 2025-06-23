from typing import List, Dict, Any
import ipaddress
from datetime import datetime
from google.cloud import asset_v1
from google.protobuf.field_mask_pb2 import FieldMask
from google.protobuf.json_format import MessageToDict
from app.utils.config import PlatformConfig


class CloudSecurityService:
    def __init__(self, config:PlatformConfig):
        self.project_id = config.project_id
        self.parent = f"projects/{self.project_id}"
        self.config = config
        # Initialize Asset Service client
        self.asset_client = asset_v1.AssetServiceClient()

    def scan_network_activity(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        flagged = []
        for entry in logs:
            ip = entry.get("ip")
            if ip and not self._is_private_ip(ip):
                flagged.append({
                    "ip": ip,
                    "timestamp": entry.get("timestamp", datetime.utcnow()),
                    "note": "Outbound traffic to public IP detected"
                })
        return flagged

    def list_assets(self) -> List[Dict[str, Any]]:
        """
        List all assets in the project for forensic or inventory analysis.
        """
        assets: List[Dict[str, Any]] = []
        request = asset_v1.ListAssetsRequest(
            parent=self.parent,
            content_type=asset_v1.ContentType.RESOURCE,
        )
        # Each element here is a ListAssetsResponse.AssetResponse proto
        for resp in self.asset_client.list_assets(request=request):
            # Convert the entire proto to a dict
            proto_dict = MessageToDict(resp._pb)  
            # Drill in to the bits we care about
            a = proto_dict.get("asset", {})
            r = proto_dict.get("resource", {})
            assets.append({
                "name":           a.get("name"),
                "asset_type":     proto_dict.get("assetType"),
                "resource_name":  r.get("name"),
                "location":       r.get("data", {}).get("location"),
            })
        return assets

    def get_cloud_configurations(self) -> List[Dict[str, Any]]:
        """
        Retrieve current configurations of resources in the project.
        Useful for compliance checks.
        """
        configs = []
        request = asset_v1.ListAssetsRequest(
            parent=self.parent,
            content_type=asset_v1.ContentType.RESOURCE
        )
        # Optionally, you could filter by asset types (e.g., "google.compute.Instance")
        for asset in self.asset_client.list_assets(request=request):
            configs.append({
                "asset_type": asset.asset_type,
                "resource": asset.resource.name,
                "configuration": asset.resource.data  # raw config dict
            })
        return configs

    def _is_private_ip(self, ip: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False



# from app.utils.config import PlatformConfig

# class CloudSecurityService:
#     def __init__(self, config: PlatformConfig):
#         self.config = config

#     def scan_network_activity(self, logs: list):
#         # Placeholder logic
#         return [{"finding": "suspicious traffic", "timestamp": "2025-06-17T00:00:00Z"}]
