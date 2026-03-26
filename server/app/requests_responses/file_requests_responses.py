from pydantic import BaseModel, Field

class UploadFileRequest(BaseModel):
    file_paths: list[str]    