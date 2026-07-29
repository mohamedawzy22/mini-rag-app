from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.scale = 1048576 
        
    def valdation_upload_file(self, file:UploadFile):
        
        if file.content_type not in self.app_setting.FILE_ALLOWED_TYPES:
            return False , ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_setting.FILE_MAX_SIZE * self.scale:
            return False ,ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True , ResponseSignal.FILE_VALIDATED_SUCCESS.value
    
    
    def cleaned_file_name(self,orig_file_name:str):
         # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
    
    
    def generate_unique_filepath(self,orig_file_name:str,project_id:str):
        
        random_key = self.generate_random_string()
        
        project_path = ProjectController().get_project_path(project_id = project_id)
        clean_files_name = self.cleaned_file_name(orig_file_name = orig_file_name)
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + clean_files_name
        )
        
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + clean_files_name
            )
        return new_file_path , random_key + "_" + clean_files_name
        