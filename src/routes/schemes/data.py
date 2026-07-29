from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    
    file_id : str
    chunks_size :Optional[int] = 100
    do_rest : Optional[int] = 0
    overlap : Optional[int] = 20
    