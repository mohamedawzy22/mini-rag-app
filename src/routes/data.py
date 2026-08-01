from fastapi import FastAPI, APIRouter,Depends,UploadFile,status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_setting,Setting
from controllers import DataController,ProjectController,ProcessController
from .schemes.data import ProcessRequest
from models import ResponseSignal
from models.ProjectModel import ProjectModel
import os
import aiofiles
import logging
from models.ChunkModel import ChunkModel
from models.db_schema import DataChunk


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1","data"]
)

@data_router.get("/upload/{project_id}")
async def upload_data(request: Request,project_id : str,file : UploadFile
                      ,app_setting : Setting = Depends(get_setting)):
    
    project_model =  await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    data_controlle = DataController()
    is_valid, result = data_controlle.valdation_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : result
            }
        )
    
    project_dir = ProjectController().get_project_path(project_id = project_id)
    file_dir,file_id = data_controlle.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    try:
        async with aiofiles.open(file_dir,"wb") as f :
            while chunk := await file.read(app_setting.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)    
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "signal" : ResponseSignal.FILE_UPLOAD_FAILED.value,
                
            }
        )
    return JSONResponse(
        content = {
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id,
            "project_id" : str(project.id)
        }
    )
        
        
@data_router.post("/process/{project_id}")
async def ProcessEndPoint(request: Request,project_id : str , ProcessRequest : ProcessRequest):
    
    file_id = ProcessRequest.file_id
    chunks_size = ProcessRequest.chunks_size
    overlap = ProcessRequest.overlap
    do_reset = ProcessRequest.do_reset
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    
    process_controller = ProcessController(project_id)
    
    file_content = process_controller.get_content_file(file_id = file_id)
    
    file_chunks = process_controller.process_file_content(
        file_content = file_content,
        file_id = file_id,
        chunks = chunks_size,
        overlap = overlap,
        
    )
    
    if file_chunks is None or len(file_chunks) == 0 :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                ResponseSignal.PROCESSING_FAILED.value,
            }
        )
        
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]
    
    
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
    
