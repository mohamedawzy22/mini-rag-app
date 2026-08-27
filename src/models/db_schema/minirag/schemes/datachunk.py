from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,UUID,Index,func
from sqlalchemy.dialects.postgresql import UUID,JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel

class DataChunk(SQLAlchemyBase):
    
    __tablename__  = "chunks"
    
    chunk_id = Column(Integer,primary_key=True,autoincrement = True)
    chunk_uuid = Column(UUID(as_uuid=True),default = uuid.uuid4 ,unique = True, nullable = False)
    
    chunk_text = Column(String, nullable = False)
    chunk_metadata = Column(JSONB, nullable = False)
    chunk_order = Column(Integer, nullable = False)
    chunk_project_id = Column(Integer,ForeignKey("projects.project_id"), nullable = False)
    chunk_asset_id = Column(Integer,ForeignKey("assets.asset_id"), nullable = False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),  nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),  nullable=True)
    
    projects = relationship("Project",back_populates="chunks")
    assets = relationship("Asset",back_populates="chunks")
    
    __tableargs__ =(
        Index("ix_chunk_project_id",chunk_project_id),
        Index("ix_chunk_asset_id",chunk_asset_id),
    )
    
    
    
class RetrievedDocument(BaseModel):
    text: str
    score: float