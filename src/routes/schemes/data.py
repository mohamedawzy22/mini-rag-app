from pydantic import BaseModel, Field
from typing import Optional


class ProcessRequest(BaseModel):

    file_id: Optional[str] = None

    chunks_size: int = Field(
        default=500,
        gt=0
    )

    overlap: int = Field(
        default=50,
        ge=0
    )

    do_reset: bool = False