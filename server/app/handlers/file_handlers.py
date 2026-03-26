from fastapi import BackgroundTasks
from typing import Dict, Any
from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest

class FileHandler:
    def __init__(self, file_service):
        self.file_service = file_service

    async def handle_submit_files(self, request: SubmitFilesRequest) -> Dict[str, Any]:
        return await self.file_service.submit_files(request)
    
    async def handle_analyze_files(self, request: AnalyzeFilesRequest, lender_id: str, background_tasks: BackgroundTasks):
        # 1. Trigger the 'Accepted' response and status update
        response = await self.file_service.analyze_files(request.borrower_id, lender_id)
        
        # 2. Queue the actual work
        background_tasks.add_task(self.file_service.run_analysis_pipeline, request.borrower_id)
        
        return response
