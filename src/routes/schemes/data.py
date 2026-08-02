from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    
    file_id: str = None
    chunks_size :Optional[int] = 100
    do_reset : Optional[int] = 0
    overlap : Optional[int] = 20
    