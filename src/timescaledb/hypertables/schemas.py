from typing import List, Optional

from pydantic import BaseModel


class HyperTableSchema(BaseModel):
    """Base class for hypertables"""

    hypertable_schema: str
    hypertable_name: str
    owner: str
    num_dimensions: int
    num_chunks: int
    compression_enabled: bool
    tablespaces: Optional[List[str]] = None
