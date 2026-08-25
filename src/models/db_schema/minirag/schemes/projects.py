from .minirag_base import SQLAlchemyBase
from sqlalchemy import column,Integer,DateTime,func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

class Project(SQLAlchemyBase):
    
    __tablename__  = "projects"
    
    project_id = column(Integer, primary_key = True, autoincrement=True)
    project_uuid = column(UUID(as_uuid=True),default = uuid.uuid4,unique = True , nullable = False )
    
    created_at = column(DateTime(timezone=True),server_default = func.now(),nullabel = False)
    updated_at = column(DateTime(timezone=True),onupdate = func.now(),nullabel = True)
    
    