from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Report(BaseModel):
    id: str
    title: str
    generated_at: str
    sections: List[str]
    output_uri: Optional[str]  # e.g., GCS path
