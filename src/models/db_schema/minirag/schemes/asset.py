from .minirag_base import SQLAlchemyBase
from sqlalchemy import column,func,DateTime,Integer,String,ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID
import uuid,JSONB
from sqlalchemy.orm import relationship


class Asset(SQLAlchemyBase):
    
    __tablename__  = "assets"
    
    asset_id = column(Integer,primary_key = True,autoincrement = True)
    asset_uuid = column(UUID(as_uuid=True),default = uuid.uuid4 ,unique = True,nullable = False)
    
    asset_type = column(String,nullable = False)
    asset_name = column(String,nullable = False)
    asset_size = column(Integer,nullable = False)
    asset_config = column(JSONB,nullable = False)
    
    asset_project_id = column(Integer,ForeignKey("projects.project_id"),nullable = False)
    
    created_at = column(DateTime(timezone=True),server_default = func.now(),nullabel = False)
    updated_at = column(DateTime(timezone=True),onupdate = func.now(),nullabel = True)    
    
    project = relationship("Project",back_populates="assets")
    
    
    __table_args__ = (
        Index('ix_asset_project_id', asset_project_id),
        Index('ix_asset_type', asset_type),
    )