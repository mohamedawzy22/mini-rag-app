from fastapi import FastAPI, APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_setting,Setting
from controllers import DataController,ProjectController,ProcessController
from .schemes.data import ProcessRequest
from models import ResponseSignal
import os
import aiofiles
import logging


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1","data"]
)

@data_router.get("/upload/{project_id}")
async def upload_data(project_id : str,file : UploadFile
                      ,app_setting : Setting = Depends(get_setting)):
    
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
            "file_id" : file_id
        }
    )
        
        
@data_router.post("/process/{project_id}")
async def ProcessEndPoint(project_id : str , ProcessRequest : ProcessRequest):
    
    file_id = ProcessRequest.file_id
    chunks_size = ProcessRequest.chunks_size
    overlap = ProcessRequest.overlap
    
    process_controller = ProcessController(project_id)
    
    file_content = process_controller.get_content_file(file_id = file_id)
    
    file_chunks = process_controller.process_file_content(
        file_content = file_content,
        file_id = file_id,
        chunks = chunks_size,
        overlap = overlap,
        
    )
    
    if file_chunks is None or file_chunks == 0 :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                ResponseSignal.PROCESSING_FAILED.value,
            }
        )
    
    return file_chunks
    
